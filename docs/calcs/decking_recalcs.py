#!/usr/bin/env python3
"""Produce a supported-joint cutting plan for the existing decking pieces.

All internal segment joints are placed on a joist centre.  Lengths are kept in
integer half-millimetres internally so the 47 mm joists and 170 mm clear gap
can be represented without rounding drift.
"""

from __future__ import annotations

import argparse
import ast
import heapq
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "decking-lengths.txt"

DECK_SPAN_MM = 5000
BOARD_STEP_MM = 150
JOIST_WIDTH_MM = 47
CENTRE_PAIR_CLEAR_MM = 170
CUT_INCREMENT_MM = 10
CENTRE_PAIR_OFFSET_MM = CENTRE_PAIR_CLEAR_MM / 2 + JOIST_WIDTH_MM / 2
JOIST_CENTRES_MM = (
    1273.5,
    1660.166667,
    2080.083333,
    DECK_SPAN_MM / 2 - CENTRE_PAIR_OFFSET_MM,
    DECK_SPAN_MM / 2 + CENTRE_PAIR_OFFSET_MM,
    2919.916667,
    3339.833333,
    3726.5,
)


@dataclass(frozen=True)
class Source:
    source_id: str
    label_mm: float
    available_mm: float
    end_form: str


@dataclass(frozen=True)
class Target:
    target_id: str
    outside_mm: float
    segment: int
    piece: int
    target_mm: float
    end_form: str


@dataclass(frozen=True)
class Assignment:
    source: Source
    target: Target

    @property
    def trim_mm(self) -> float:
        return self.source.available_mm - self.target.target_mm


def _half_mm(value: float) -> int:
    return round(value * 2)


def _from_half_mm(value: int) -> float:
    return value / 2


def read_sources(
    path: Path,
    *,
    assumed_shortfall_mm: float = 20,
    stock_count: int = 2,
    stock_length_mm: float = 3900,
) -> list[Source]:
    """Read the labelled segment pieces and append the uncut stock boards."""
    sources: list[Source] = []
    segment_number: dict[int, int] = {}
    for line_number, raw_line in enumerate(path.read_text().splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            outside_text, pieces_text = line.split(":", 1)
            outside_cm = int(outside_text)
            pieces_cm = ast.literal_eval(pieces_text)
        except (ValueError, SyntaxError) as exc:
            raise ValueError(f"{path}:{line_number}: invalid row") from exc
        if not isinstance(pieces_cm, list) or not pieces_cm:
            raise ValueError(f"{path}:{line_number}: pieces must be a list")
        if sum(pieces_cm) != outside_cm:
            raise ValueError(
                f"{path}:{line_number}: pieces total {sum(pieces_cm)} cm, "
                f"not {outside_cm} cm"
            )
        segment_number[outside_cm] = segment_number.get(outside_cm, 0) + 1
        segment = segment_number[outside_cm]
        for piece_index, label_cm in enumerate(pieces_cm, 1):
            if len(pieces_cm) == 1:
                end_form = "two mitres"
            elif 1 < piece_index < len(pieces_cm):
                end_form = "square ends"
            else:
                end_form = "one mitre"
            label_mm = float(label_cm * 10)
            sources.append(
                Source(
                    source_id=(
                        f"{outside_cm} cm segment {segment}, "
                        f"piece {piece_index} (label {label_cm} cm)"
                    ),
                    label_mm=label_mm,
                    available_mm=label_mm - assumed_shortfall_mm,
                    end_form=end_form,
                )
            )
    expected_outside_cm = set(range(500, 259, -30))
    if set(segment_number) != expected_outside_cm or set(segment_number.values()) != {4}:
        raise ValueError(
            "inventory must contain the nine outside lengths from 500 to 260 cm, "
            "with exactly four segments at each length"
        )
    for stock_number in range(1, stock_count + 1):
        sources.append(
            Source(
                source_id=f"stock board {stock_number} (390 cm)",
                label_mm=stock_length_mm,
                available_mm=stock_length_mm,
                end_form="uncut",
            )
        )
    return sources


def _split_at_joist(
    outside_mm: float, joist_index: int, *, practical: bool
) -> tuple[float, float]:
    inset_mm = (DECK_SPAN_MM - outside_mm) / 2
    exact_joint_mm = JOIST_CENTRES_MM[joist_index] - inset_mm
    joint_mm = (
        round(exact_joint_mm / CUT_INCREMENT_MM) * CUT_INCREMENT_MM
        if practical
        else exact_joint_mm
    )
    return joint_mm, outside_mm - joint_mm


def target_layouts(*, practical: bool = True) -> dict[tuple[int, int], tuple[float, ...]]:
    """Return the optimised cutting layout for all 36 segments.

    Layout selection minimises the number of butt joints first, then selects
    supported joint positions that permit a one-to-one reuse of the existing
    labelled pieces plus the two stock boards.  The resulting minimum is 31
    joints (67 pieces): five segments can remain whole and every other segment
    needs one supported butt joint.
    """
    # Value is None for an unjointed segment, otherwise the zero-based joist
    # index on which the one butt joint is centred.
    selected_joist: dict[int, tuple[int | None, ...]] = {
        5000: (7, 3, 0, 2),
        4700: (3, 2, 2, 3),
        4400: (0, 7, 6, 6),
        4100: (7, 3, 7, 3),
        3800: (4, None, 4, None),
        3500: (None, 0, 5, 0),
        3200: (3, None, 0, 2),
        2900: (1, 2, 1, None),
        2600: (3, 2, 5, 5),
    }
    layouts: dict[tuple[int, int], tuple[float, ...]] = {}
    for outside_mm, choices in selected_joist.items():
        for segment, joist_index in enumerate(choices, 1):
            layouts[(outside_mm, segment)] = (
                (outside_mm,)
                if joist_index is None
                else _split_at_joist(
                    outside_mm, joist_index, practical=practical
                )
            )
    return layouts


def make_targets(*, practical: bool = True) -> list[Target]:
    targets: list[Target] = []
    for (outside_mm, segment), pieces in sorted(
        target_layouts(practical=practical).items(), reverse=True
    ):
        for piece_index, target_mm in enumerate(pieces, 1):
            end_form = "two mitres" if len(pieces) == 1 else "one mitre"
            targets.append(
                Target(
                    target_id=(
                        f"{outside_mm / 10:g} cm segment {segment}, "
                        f"piece {piece_index}"
                    ),
                    outside_mm=outside_mm,
                    segment=segment,
                    piece=piece_index,
                    target_mm=target_mm,
                    end_form=end_form,
                )
            )
    return targets


def make_assignments(sources: list[Source]) -> list[Assignment]:
    """Keep the reviewed source mapping while rounding cuts for site use."""
    exact_assignments = assign_sources(sources, make_targets(practical=False))
    practical_targets = {
        target.target_id: target for target in make_targets(practical=True)
    }
    assignments = [
        Assignment(assignment.source, practical_targets[assignment.target.target_id])
        for assignment in exact_assignments
    ]
    if any(assignment.trim_mm < 0 for assignment in assignments):
        # A changed inventory may make the reviewed assignment too short after
        # rounding up. In that case, compute a fresh feasible practical match.
        return assign_sources(sources, list(practical_targets.values()))
    return assignments


def _end_work(source: Source, target: Target) -> int:
    if source.end_form == target.end_form:
        return 0
    if source.end_form == "one mitre" and target.end_form == "two mitres":
        return 1
    if source.end_form == "two mitres" and target.end_form == "one mitre":
        return 1
    if source.end_form == "uncut":
        return 2 if target.end_form == "two mitres" else 1
    return 2


def assign_sources(sources: list[Source], targets: list[Target]) -> list[Assignment]:
    """Find a minimum-waste one-source-to-one-target assignment.

    Material waste is the primary cost.  For equal waste, retaining a useful
    existing mitre is preferred.  Stock boards are treated as single pieces;
    in the selected layout each becomes one 3800 mm segment with a 100 mm
    offcut, so kerf cannot affect any second piece.
    """
    source_count = len(sources)
    target_count = len(targets)
    start = 0
    source_base = 1
    target_base = source_base + source_count
    sink = target_base + target_count
    graph: list[list[list[int]]] = [[] for _ in range(sink + 1)]

    def add_edge(node_a: int, node_b: int, capacity: int, cost: int) -> None:
        graph[node_a].append([node_b, len(graph[node_b]), capacity, cost])
        graph[node_b].append([node_a, len(graph[node_a]) - 1, 0, -cost])

    for source_index in range(source_count):
        add_edge(start, source_base + source_index, 1, 0)
    for target_index in range(target_count):
        add_edge(target_base + target_index, sink, 1, 0)
    for source_index, source in enumerate(sources):
        for target_index, target in enumerate(targets):
            if _half_mm(source.available_mm) < _half_mm(target.target_mm):
                continue
            waste_half_mm = _half_mm(source.available_mm - target.target_mm)
            cost = waste_half_mm * 10 + _end_work(source, target)
            add_edge(
                source_base + source_index,
                target_base + target_index,
                1,
                cost,
            )

    potential = [0] * len(graph)
    flow = 0
    while flow < target_count:
        distance = [10**18] * len(graph)
        previous: list[tuple[int, int] | None] = [None] * len(graph)
        distance[start] = 0
        queue = [(0, start)]
        while queue:
            current_distance, node = heapq.heappop(queue)
            if current_distance != distance[node]:
                continue
            for edge_index, edge in enumerate(graph[node]):
                other, _, capacity, cost = edge
                if not capacity:
                    continue
                candidate = current_distance + cost + potential[node] - potential[other]
                if candidate < distance[other]:
                    distance[other] = candidate
                    previous[other] = (node, edge_index)
                    heapq.heappush(queue, (candidate, other))
        if previous[sink] is None:
            raise ValueError("the available pieces cannot satisfy the target layout")
        for node, value in enumerate(distance):
            if value < 10**18:
                potential[node] += value
        node = sink
        while node != start:
            previous_node, edge_index = previous[node]  # type: ignore[misc]
            edge = graph[previous_node][edge_index]
            edge[2] -= 1
            reverse_index = edge[1]
            graph[node][reverse_index][2] += 1
            node = previous_node
        flow += 1

    assignments: list[Assignment] = []
    for source_index, source in enumerate(sources):
        node = source_base + source_index
        for edge in graph[node]:
            other, _, capacity, _ = edge
            if target_base <= other < sink and capacity == 0:
                assignments.append(Assignment(source, targets[other - target_base]))
    if len(assignments) != target_count:
        raise AssertionError("assignment flow did not cover every target")
    return assignments


def validate_plan(assignments: Iterable[Assignment]) -> None:
    assignments = list(assignments)
    by_segment: dict[tuple[float, int], list[Target]] = {}
    seen_sources: set[str] = set()
    for assignment in assignments:
        if assignment.source.source_id in seen_sources:
            raise AssertionError(f"source reused: {assignment.source.source_id}")
        seen_sources.add(assignment.source.source_id)
        if _half_mm(assignment.trim_mm) < 0:
            raise AssertionError(f"source too short: {assignment.source.source_id}")
        key = (assignment.target.outside_mm, assignment.target.segment)
        by_segment.setdefault(key, []).append(assignment.target)
    if len(by_segment) != 36:
        raise AssertionError("plan must contain nine rows of four segments")
    maximum_centre_error_mm = CUT_INCREMENT_MM / 2
    for (outside_mm, _), pieces in by_segment.items():
        pieces.sort(key=lambda item: item.piece)
        if _half_mm(sum(item.target_mm for item in pieces)) != _half_mm(outside_mm):
            raise AssertionError("target pieces do not reconstruct their segment")
        inset_mm = (DECK_SPAN_MM - outside_mm) / 2
        cumulative_mm = 0.0
        for piece in pieces[:-1]:
            cumulative_mm += piece.target_mm
            global_joint_mm = inset_mm + cumulative_mm
            nearest_joist_mm = min(
                JOIST_CENTRES_MM, key=lambda value: abs(value - global_joint_mm)
            )
            if abs(global_joint_mm - nearest_joist_mm) > maximum_centre_error_mm:
                raise AssertionError(
                    f"joint at {global_joint_mm} mm is too far from a joist centre"
                )


def _fmt_mm(value: float) -> str:
    rounded = round(value, 1)
    return f"{rounded:.1f}" if rounded % 1 else f"{rounded:.0f}"


def markdown_report(assignments: list[Assignment], sources: list[Source]) -> str:
    source_order = {source.source_id: index for index, source in enumerate(sources)}
    ordered = sorted(
        assignments,
        key=lambda item: source_order[item.source.source_id],
    )
    lines = [
        "| Existing labelled board | Assumed available (mm) | "
        "New segment / piece | New cut length (mm) | Trim/offcut (mm) |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for assignment in ordered:
        lines.append(
            "| "
            f"{assignment.source.source_id} | "
            f"{_fmt_mm(assignment.source.available_mm)} | "
            f"{assignment.target.target_id} | "
            f"{_fmt_mm(assignment.target.target_mm)} | "
            f"{_fmt_mm(assignment.trim_mm)} |"
        )
    used = {assignment.source.source_id for assignment in assignments}
    unused = [source for source in sources if source.source_id not in used]
    lines.extend(
        [
            "",
            f"Used {len(assignments)} of {len(sources)} source pieces/boards; "
            f"total trim and offcut is "
            f"{_fmt_mm(sum(item.trim_mm for item in assignments))} mm.",
            "",
            "Unused existing pieces:",
            "",
        ]
    )
    lines.extend(f"- {source.source_id}" for source in unused)
    return "\n".join(lines)


def json_report(assignments: list[Assignment], sources: list[Source]) -> str:
    used = {assignment.source.source_id for assignment in assignments}
    payload = {
        "joist_centres_mm": JOIST_CENTRES_MM,
        "assignments": [
            {
                "source": asdict(item.source),
                "target": asdict(item.target),
                "trim_mm": item.trim_mm,
            }
            for item in assignments
        ],
        "unused_sources": [
            asdict(source) for source in sources if source.source_id not in used
        ],
    }
    return json.dumps(payload, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--actual-shortfall-mm", type=float, default=20)
    parser.add_argument("--stock-count", type=int, default=2)
    parser.add_argument("--stock-length-mm", type=float, default=3900)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--check", action="store_true", help="validate silently instead of reporting"
    )
    args = parser.parse_args()
    sources = read_sources(
        args.input,
        assumed_shortfall_mm=args.actual_shortfall_mm,
        stock_count=args.stock_count,
        stock_length_mm=args.stock_length_mm,
    )
    assignments = make_assignments(sources)
    validate_plan(assignments)
    if not args.check:
        print(
            json_report(assignments, sources)
            if args.json
            else markdown_report(assignments, sources)
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
