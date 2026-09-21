#!/usr/bin/env python3
"""Generate prototype SVGs for the monolithic aluminium upper plates.

The drawings expose the current screening geometry and hole centres.  They are
not cutter-ready profiles: basket M6 positions remain survey targets, and the
corner requires the complete wet proof described in the material study.
"""

from __future__ import annotations

from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/packs/c/diagrams/aluminium-uppers"

M8_DIAMETER = 8.5
M6_DIAMETER = 6.5


def capsule(start: tuple[float, float], end: tuple[float, float], width: float):
    return LineString((start, end)).buffer(width / 2, quad_segs=24)


def rounded_union(parts) -> Polygon:
    """Join paths and remove re-entrant features below the 5 mm screen."""
    return unary_union(parts).buffer(5, quad_segs=24).buffer(-5, quad_segs=24)


def path_data(poly: Polygon) -> str:
    points = list(poly.exterior.coords)
    return "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in points) + " Z"


def drawing(
    filename: str,
    title: str,
    profile: Polygon,
    m8_axes: list[tuple[float, float]],
    m6_targets: list[tuple[float, float]],
    c2_axes: list[tuple[float, float]] | None = None,
    guide_lines: list[tuple[tuple[float, float], tuple[float, float]]] | None = None,
    notes: list[str] | None = None,
) -> None:
    c2_axes = c2_axes or []
    guide_lines = guide_lines or []
    notes = notes or []
    min_x, min_y, max_x, max_y = profile.bounds
    margin = 35
    note_height = 18 * (len(notes) + 2)
    view_x = min_x - margin
    view_y = min_y - margin
    width = max(max_x - min_x + 2 * margin, 760)
    height = max_y - min_y + 2 * margin + note_height

    guides = "\n".join(
        f'  <line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
        'class="guide"/>' for a, b in guide_lines
    )
    m8 = "\n".join(
        f'  <circle cx="{x}" cy="{y}" r="{M8_DIAMETER / 2}" class="m8"/>'
        for x, y in m8_axes
    )
    m6 = "\n".join(
        f'  <circle cx="{x}" cy="{y}" r="{M6_DIAMETER / 2}" class="m6"/>'
        for x, y in m6_targets
    )
    c2 = "\n".join(
        f'  <circle cx="{x}" cy="{y}" r="{M8_DIAMETER / 2}" class="c2"/>'
        for x, y in c2_axes
    )
    labels = [title, "Black: 10 mm aluminium candidate profile; red: M8; blue: C2 M8; dashed green: provisional M6 survey targets"]
    labels.extend(notes)
    text_y = max_y + margin + 16
    text = "\n".join(
        f'  <text x="{min_x}" y="{text_y + 18 * index}" class="note">{label}</text>'
        for index, label in enumerate(labels)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
  width="{width:.1f}mm" height="{height:.1f}mm"
  viewBox="{view_x:.1f} {view_y:.1f} {width:.1f} {height:.1f}">
  <title>{title}</title>
  <desc>Prototype coordination drawing only; not a released cutting template.</desc>
  <style>
    .profile {{ fill: #20252b; stroke: #000; stroke-width: 1; }}
    .guide {{ stroke: #8b949e; stroke-width: 0.8; stroke-dasharray: 6 4; }}
    .m8 {{ fill: #fff; stroke: #d1242f; stroke-width: 2; }}
    .c2 {{ fill: #fff; stroke: #0969da; stroke-width: 2.5; }}
    .m6 {{ fill: none; stroke: #1a7f37; stroke-width: 1.5; stroke-dasharray: 4 3; }}
    .note {{ font: 12px sans-serif; fill: #24292f; }}
  </style>
  <path id="profile" d="{path_data(profile)}" class="profile"/>
{guides}
{m8}
{c2}
{m6}
{text}
</svg>
'''
    (OUT / filename).write_text(svg)


def seat_upper(base: int) -> None:
    half = base / 2
    arms = [
        capsule((-half, -half), (-half, half), 40),
        capsule((half, -half), (half, half), 40),
    ]
    bridge = capsule((-half, 0), (half, 0), 90)
    profile = rounded_union([*arms, bridge])
    m8_axes = [(-half, -28), (-half, 28), (half, -28), (half, 28)]
    # These expose a plausible four-point layout only.  Move each point onto a
    # measured sound basket rib before adding it to a cutting/drilling file.
    basket_offset = half - 45
    m6_targets = [
        (-half, -basket_offset), (-half, basket_offset),
        (half, -basket_offset), (half, basket_offset),
    ]
    drawing(
        f"r5.1.2-upper-{base}.svg",
        f"R5.1.2 monolithic upper — {base} mm reinforced-base screen",
        profile,
        m8_axes,
        m6_targets,
        guide_lines=[((-half - 45, 0), (half + 45, 0)),
                     ((0, -half - 20), (0, half + 20))],
        notes=[
            f"Envelope {base + 90:.0f} x {base + 40:.0f} mm; 40 mm arms; 90 mm central rail region.",
            "Four M8 axes use two capture stations and the retained +/-28 mm transverse rows.",
            "M6 circles are survey targets, not drilling coordinates; locate on the real basket ribs.",
        ],
    )


def corner_upper() -> None:
    m55_a = (55, 0)
    m55_b = (0, 55)
    m125_a = (125, 0)
    m125_b = (0, 125)
    m195_a = (195, 0)
    m195_b = (0, 195)
    c2_a = (55, -140)
    c2_b = (-140, 55)
    basket = [(-60, -60), (120, -60), (-60, 120), (120, 120)]

    parts = [
        capsule(c2_a, m55_a, 75),
        capsule(c2_b, m55_b, 75),
        capsule(m55_a, m195_a, 80),
        capsule(m55_b, m195_b, 80),
        capsule(m55_a, m55_b, 80),
        capsule(m195_a, basket[3], 50),
        capsule(basket[3], m195_b, 50),
        capsule(c2_a, basket[1], 50),
        capsule(basket[1], m195_a, 50),
        capsule(c2_b, basket[2], 50),
        capsule(basket[2], m195_b, 50),
        capsule(basket[0], (27.5, 27.5), 50),
    ]
    for point, radius in [
        (m55_a, 15), (m125_a, 15), (m195_a, 15),
        (m55_b, 15), (m125_b, 15), (m195_b, 15),
        (c2_a, 20), (c2_b, 20),
        *((point, 20) for point in basket),
    ]:
        parts.append(Point(point).buffer(radius, quad_segs=24))
    profile = rounded_union(parts)
    drawing(
        "corner-seat-upper-monolithic.svg",
        "Monolithic aluminium corner-seat upper — current interface candidate",
        profile,
        [m55_a, m125_a, m195_a, m55_b, m125_b, m195_b],
        basket,
        c2_axes=[c2_a, c2_b],
        guide_lines=[((-175, 0), (235, 0)), ((0, -175), (0, 235))],
        notes=[
            "Six M8 rail axes: 55, 125 and 195 mm on each rail leg.",
            "Separate C2 axes: (55,-140) and (-140,55); 75 mm direct paths to the neighbouring 55 mm axes.",
            "Four provisional M6 basket targets retain R20 lands; move only after the real basket survey.",
            "Retain the separate lower corner web and prove the complete perforated wet joint.",
        ],
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for base in (200, 225, 250):
        seat_upper(base)
    corner_upper()
    for path in sorted(OUT.glob("*.svg")):
        print(path)


if __name__ == "__main__":
    main()
