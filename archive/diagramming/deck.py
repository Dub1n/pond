from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .core import SvgScene
from .dimensions import horizontal_dimension


def format_length(value_m: float) -> str:
    if value_m >= 1.0:
        return f"{value_m:.1f} m"
    mm = round(value_m * 1000)
    return f"{value_m:.2f} m ({mm:.0f} mm)"


@dataclass
class DeckOption:
    key: str
    title: str
    deck_m: float
    pond_m: float
    walkway_m: float
    overhang_m: float
    header_back_m: Optional[float] = None
    plan_aria: Optional[str] = None
    section_aria: Optional[str] = None
    walkway_label: str = "B"
    overhang_label: str = "A"
    header_label: str = "D"

    @classmethod
    def from_dict(cls, key: str, data: Dict[str, Any]) -> "DeckOption":
        deck = float(data["deck_m"])
        pond = float(data["pond_m"])
        walkway = float(data.get("walkway_m", (deck - pond) / 2.0))
        overhang = float(data["overhang_m"])
        header_back = data.get("header_back_m")
        if header_back is not None:
            header_back = float(header_back)
        return cls(
            key=key,
            title=data.get("title", f"Option {key}"),
            deck_m=deck,
            pond_m=pond,
            walkway_m=walkway,
            overhang_m=overhang,
            header_back_m=header_back,
            plan_aria=data.get("plan_aria"),
            section_aria=data.get("section_aria"),
            walkway_label=data.get("walkway_label", "B"),
            overhang_label=data.get("overhang_label", "A"),
            header_label=data.get("header_label", "D"),
        )


def render_deck_plan(option: DeckOption, scale: float = 100.0) -> SvgScene:
    scene = SvgScene(pad=48.0)
    aria = option.plan_aria or f"{option.title} — plan view of deck and pond opening"
    scene.root.set("aria-label", aria)
    scene.root.set("data-diagram", f"deck-plan-{option.key.lower()}")
    scene.add_css(
        """
        .deck-outline { fill: none; stroke: #7b5532; stroke-width: 1.8; }
        .walkway { fill: #f3d9b6; fill-opacity: 0.68; stroke: none; }
        .pond { fill: #8cccf2; stroke: #3f86c5; stroke-width: 1.4; }
        .deck-overhang { fill: rgba(194, 143, 92, 0.45); stroke: none; }
        .beam { fill: #b8874d; stroke: #6d482a; stroke-width: 1.2; }
        .header { fill: #b8874d; stroke: #6d482a; stroke-width: 1.4; fill-opacity: 0.85; }
        .joist { stroke: #6b462a; stroke-width: 5; }
        .note { font-size: 14px; fill: #444; }
        .title { font-size: 18px; font-weight: 600; }
        .tag { fill: #ffffff; stroke: #333; stroke-width: 1.1; }
        .tag text { font-size: 13px; fill: #333; }
        .legend { font-size: 13px; fill: #333; }
        """
    )

    deck_px = option.deck_m * scale
    pond_px = option.pond_m * scale
    walkway_px = option.walkway_m * scale
    overhang_px = option.overhang_m * scale
    pond_start = walkway_px
    pond_end = pond_start + pond_px

    # Walkway shading (outer ring)
    scene.rect(0, 0, pond_start, deck_px, class_="walkway")  # left
    scene.rect(pond_end, 0, max(deck_px - pond_end, 0), deck_px, class_="walkway")  # right
    scene.rect(pond_start, 0, pond_px, pond_start, class_="walkway")  # top
    scene.rect(pond_start, pond_end, pond_px, max(deck_px - pond_end, 0), class_="walkway")  # bottom

    # Outer deck boundary
    scene.rect(0, 0, deck_px, deck_px, class_="deck-outline")
    scene.text(0, -24, option.title, font_size=20, class_="title")
    scene.text(
        deck_px,
        deck_px + 36,
        f"Overall deck: {option.deck_m:.1f} m square. Pond opening {option.pond_m:.1f} m.",
        anchor="end",
        class_="note",
    )

    # Pond opening label is added after support framing
    scene.text(
        (pond_start + pond_end) / 2,
        pond_start + pond_px / 2 + 14,
        f"{option.pond_m:.1f} m pond (clear span)",
        anchor="middle",
        class_="note",
    )

    # Support beams framing the pond
    beam_thk = scale * 0.16
    scene.rect(pond_start, pond_start, pond_px, beam_thk, class_="beam")
    scene.rect(pond_start, pond_end - beam_thk, pond_px, beam_thk, class_="beam")
    scene.rect(pond_start, pond_start, beam_thk, pond_px, class_="beam")
    scene.rect(pond_end - beam_thk, pond_start, beam_thk, pond_px, class_="beam")

    support_inner = pond_start + beam_thk
    inner_extent = pond_end - beam_thk
    water_size = max(pond_px - 2 * beam_thk, 0)
    scene.rect(support_inner, support_inner, water_size, water_size, class_="pond")
    inner_span = max(inner_extent - support_inner, 0)
    if overhang_px > 0 and inner_span > 0:
        scene.rect(support_inner, support_inner, overhang_px, inner_span, class_="deck-overhang")  # left
        scene.rect(inner_extent - overhang_px, support_inner, overhang_px, inner_span, class_="deck-overhang")  # right
        scene.rect(support_inner, support_inner, inner_span, overhang_px, class_="deck-overhang")  # top
        scene.rect(support_inner, inner_extent - overhang_px, inner_span, overhang_px, class_="deck-overhang")  # bottom

    # Outer rim beams (symbolic)
    outer_beam = scale * 0.18
    scene.rect(0, 0, deck_px, outer_beam, class_="beam")
    scene.rect(0, deck_px - outer_beam, deck_px, outer_beam, class_="beam")
    scene.rect(0, 0, outer_beam, deck_px, class_="beam")
    scene.rect(deck_px - outer_beam, 0, outer_beam, deck_px, class_="beam")

    # Joist direction: render on left walkway
    joist_start_x = outer_beam
    joist_end_x = support_inner + overhang_px
    joist_step = scale * 0.4
    y = pond_start + scale * 0.25
    while y < pond_end - scale * 0.25:
        scene.line(joist_start_x, y, joist_end_x, y, class_="joist")
        y += joist_step

    # Header + outriggers for option with header
    if option.header_back_m:
        header_offset_px = option.header_back_m * scale
        header_x = pond_start - header_offset_px
        header_width = scale * 0.18
        scene.rect(header_x - header_width / 2, pond_start - beam_thk * 0.4, header_width, pond_px + beam_thk * 0.8, class_="header")
        scene.text(
            header_x,
            pond_start - 30,
            "Header (double 47×200)",
            anchor="middle",
            class_="note",
        )
        # Outriggers
        outr_step = scale * 0.4
        outr_x0 = header_x + header_width / 2
        outr_x1 = pond_start + overhang_px
        y = pond_start + outr_step / 2
        while y < pond_end:
            scene.line(outr_x0, y, outr_x1, y, class_="joist")
            y += outr_step
        # Dimension header setback
        label = f"{option.header_label}: {format_length(option.header_back_m)} header setback"
        horizontal_dimension(
            scene,
            header_x,
            pond_start,
            deck_px,
            label,
            direction="down",
            offset=82,
        )

    # Tags & legend
    legend_entries: list[tuple[str, str]] = []

    def add_tag(cx: float, cy: float, label: str, description: str) -> None:
        box_w, box_h = 26, 24
        scene.rect(cx - box_w / 2, cy - box_h / 2, box_w, box_h, rx=4, ry=4, class_="tag")
        scene.text(cx, cy + 6, label, anchor="middle", font_size=13)
        if description:
            legend_entries.append((label, description))

    add_tag((pond_start + pond_end) / 2, (pond_start + pond_end) / 2, "C", f"Pond opening ({option.pond_m:.1f} m square)")
    add_tag(pond_start - beam_thk * 0.6, pond_start + beam_thk * 0.5, "S", "Support beam at pond edge")
    add_tag(joist_start_x + max(joist_end_x - joist_start_x, 0) * 0.65, pond_start + scale * 0.45, "E", "47×150 mm joist @ 400 mm centres (typ.)")
    if option.header_back_m:
        header_x = pond_start - option.header_back_m * scale
        add_tag(header_x + scale * 0.05, pond_start - scale * 0.35, "H", f"Header {format_length(option.header_back_m)} back from edge")

    # Dimensions
    walkway_text = f"{format_length(option.walkway_m)} walkway"
    horizontal_dimension(scene, 0, pond_start, deck_px, walkway_text, direction="down", offset=48, text_offset=-16)
    overhang_text = f"{format_length(option.overhang_m)} overhang"
    horizontal_dimension(
        scene,
        support_inner,
        support_inner + overhang_px,
        -outer_beam,
        overhang_text,
        direction="up",
        offset=72,
        text_offset=-18,
    )

    if legend_entries:
        legend_width = max(len(text) for _, text in legend_entries) * 6.2 + 36
        legend_height = 22 * len(legend_entries) + 18
        legend_x = deck_px / 2 - legend_width / 2
        legend_y = deck_px + 44
        scene.rect(legend_x, legend_y, legend_width, legend_height, rx=6, ry=6, fill="#f9f4ec", stroke="#c7b091", stroke_width=1.0)
        scene.text(legend_x + 12, legend_y + 18, "Legend", font_size=14, class_="legend")
        cur_y = legend_y + 40
        for label, text in legend_entries:
            scene.rect(legend_x + 12, cur_y - 14, 18, 18, rx=3, ry=3, class_="tag")
            scene.text(legend_x + 21, cur_y, label, anchor="middle", font_size=12)
            scene.text(legend_x + 40, cur_y, text, class_="legend", anchor="start")
            cur_y += 22

    return scene


def render_deck_section(option: DeckOption, scale: float = 100.0) -> SvgScene:
    scene = SvgScene(pad=42.0)
    aria = option.section_aria or f"{option.title} — section through joists"
    scene.root.set("aria-label", aria)
    scene.root.set("data-diagram", f"deck-section-{option.key.lower()}")
    scene.add_css(
        """
        .decking { fill: #d7b996; stroke: #7b5532; stroke-width: 1.3; }
        .joist-backspan { fill: #b8874d; stroke: #6d482a; stroke-width: 1.2; }
        .joist-cantilever { fill: #d3a060; stroke: #6d482a; stroke-width: 1.2; }
        .post { fill: #b8874d; stroke: #6d482a; stroke-width: 1.2; }
        .water { fill: #8cccf2; opacity: 0.65; }
        .reference { stroke: #8a8a8a; stroke-width: 1.4; stroke-dasharray: 8 4; }
        .soil { fill: #d8c5a4; stroke: #b99f72; stroke-width: 1.1; }
        """
    )

    walkway_px = option.walkway_m * scale
    overhang_px = option.overhang_m * scale
    total_span = walkway_px + overhang_px

    deck_thickness = scale * 0.12
    joist_depth = scale * 0.45
    deck_top_y = 0
    decking_y = deck_top_y
    joist_top = decking_y
    joist_bottom = joist_top + joist_depth
    water_depth = scale * 0.9

    # Decking
    scene.rect(-scale * 0.2, decking_y - deck_thickness, total_span + scale * 0.4, deck_thickness, class_="decking")
    scene.text(
        -scale * 0.2,
        decking_y - deck_thickness - 36,
        "28×145 mm decking (fall to outer edge)",
        class_="note",
    )

    # Joist bodies
    backspan_end = walkway_px
    cantilever_start = walkway_px
    cantilever_end = walkway_px + overhang_px

    if option.header_back_m:
        header_back_px = option.header_back_m * scale
        header_x = walkway_px - header_back_px
        backspan_end = header_x
        cantilever_start = header_x
        cantilever_end = header_x + (walkway_px - header_x) + overhang_px

    if backspan_end > 0:
        scene.rect(0, joist_top, backspan_end, joist_depth, class_="joist-backspan")
    scene.rect(cantilever_start, joist_top, max(cantilever_end - cantilever_start, 0), joist_depth, class_="joist-cantilever")
    scene.text(
        total_span / 2,
        joist_top + joist_depth / 2 + 6,
        "47×150 mm joist",
        anchor="middle",
        class_="note",
    )

    # Outer support post
    post_width = scale * 0.24
    post_height = scale * 0.95
    scene.rect(-post_width, joist_bottom - post_height, post_width, post_height, class_="post")
    scene.text(-post_width * 0.2, joist_bottom + 30, "Outer support post", class_="note")

    # Pond edge reference
    pond_edge_x = walkway_px
    scene.line(pond_edge_x, joist_top - deck_thickness * 0.6, pond_edge_x, joist_bottom + water_depth * 0.7, class_="reference")
    scene.text(pond_edge_x + 12, joist_top - deck_thickness - 18, "Pond edge / support", class_="note")
    pond_support_width = post_width * 0.6
    pond_support_height = scale * 0.6
    scene.rect(
        pond_edge_x - pond_support_width / 2,
        joist_bottom - pond_support_height,
        pond_support_width,
        pond_support_height,
        class_="post",
    )

    # Overhang portion highlight
    if option.header_back_m:
        header_back_px = option.header_back_m * scale
        header_x = pond_edge_x - header_back_px
        header_depth = scale * 0.32
        scene.rect(header_x - header_depth / 2, joist_bottom - header_depth, header_depth, header_depth, class_="post")
        scene.text(header_x + header_depth / 2 + 14, joist_bottom - header_depth / 2, "Header", anchor="start", class_="note")
        scene.line(header_x, joist_top + joist_depth * 0.25, pond_edge_x + overhang_px, joist_top + joist_depth * 0.25, class_="joist-cantilever")
        horizontal_dimension(
            scene,
            header_x,
            pond_edge_x,
            joist_bottom,
            f"{option.header_label}: {format_length(option.header_back_m)} header setback",
            direction="down",
            offset=58,
            text_offset=-18,
        )

    # Water body
    water_start_y = joist_bottom + scale * 0.12
    scene.rect(pond_edge_x + scale * 0.18, water_start_y, overhang_px + scale * 0.8, water_depth, class_="water")

    # Dimension lines
    horizontal_dimension(
        scene,
        0,
        walkway_px,
        deck_top_y,
        f"{option.walkway_label}: {format_length(option.walkway_m)} backspan",
        direction="down",
        offset=78,
        text_offset=18,
    )
    horizontal_dimension(
        scene,
        walkway_px,
        walkway_px + overhang_px,
        deck_top_y,
        f"{option.overhang_label}: {format_length(option.overhang_m)} cantilever",
        direction="up",
        offset=96,
        text_offset=22,
    )

    scene.text(
        pond_edge_x + overhang_px + scale * 0.9,
        joist_bottom + water_depth * 0.4,
        "Water depth not to scale",
        class_="note",
        anchor="end",
    )

    return scene
