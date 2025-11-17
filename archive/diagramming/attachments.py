from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

from .core import SvgScene
from .dimensions import horizontal_dimension, vertical_dimension


def _require(key: str, data: Dict[str, Any]) -> Any:
    if key not in data:
        raise KeyError(f"Attachment specification missing required field '{key}'")
    return data[key]


@dataclass
class AttachmentOption:
    key: str
    variant: str
    title: str
    params: Dict[str, Any]
    aria_label: Optional[str] = None

    @classmethod
    def from_dict(cls, key: str, data: Dict[str, Any]) -> "AttachmentOption":
        variant = data.get("variant")
        if not variant:
            raise KeyError(f"Attachment option {key} needs a 'variant' field")
        reserved = {"variant", "title", "aria_label", "aria"}
        params = {k: v for k, v in data.items() if k not in reserved}
        return cls(
            key=key,
            variant=variant,
            title=data.get("title", f"Option {key}"),
            params=params,
            aria_label=data.get("aria_label") or data.get("aria"),
        )


def render_attachment_diagram(option: AttachmentOption) -> SvgScene:
    variant = option.variant.lower()
    if variant == "anchor_trench":
        return _render_anchor_trench(option)
    if variant == "timber_clamp":
        return _render_timber_clamp(option)
    if variant == "coping":
        return _render_coping(option)
    raise ValueError(f"Unknown attachment variant '{option.variant}'")


# ---------------------------------------------------------------------------
# Anchor trench variant


def _render_anchor_trench(option: AttachmentOption) -> SvgScene:
    params = option.params
    scale = float(params.get("scale_px_per_mm", 1.2))
    mm = lambda value: float(value) * scale

    water_width_mm = params.get("water_width_mm", 320)
    water_depth_mm = params.get("water_depth_mm", 240)
    soil_depth_mm = params.get("soil_depth_mm", 260)
    rim_above_water_mm = params.get("rim_above_water_mm", 60)
    trench_offset_mm = params.get("trench_offset_mm", 250)
    trench_width_mm = params.get("trench_width_mm", 140)
    depth_range = params.get("trench_depth_range_mm", [200, 300])
    if isinstance(depth_range, (int, float)):
        depth_range = [float(depth_range), float(depth_range)]
    trench_depth_nominal = float(params.get("trench_depth_mm", sum(depth_range) / 2.0))
    bank_extend_mm = params.get("bank_extend_mm", 380)

    scene = SvgScene(pad=42.0)
    aria = option.aria_label or f"{option.title} — pond liner anchored in trench"
    scene.root.set("aria-label", aria)
    scene.root.set("data-diagram", f"edge-attachment-{option.key.lower()}")
    scene.add_css(
        """
        .soil { fill: #d9c4a1; stroke: #b79d73; stroke-width: 1.2; }
        .water { fill: #8cccf2; opacity: 0.7; }
        .liner { fill: none; stroke: #1d1d1d; stroke-width: 4; stroke-linejoin: round; }
        .note { font-size: 14px; fill: #444; }
        """
    )

    water_left_x = 0.0
    pond_edge_x = mm(water_width_mm)
    water_top_y = 0.0
    water_bottom_y = mm(water_depth_mm)
    bank_top_y = -mm(rim_above_water_mm)
    soil_bottom_y = water_bottom_y + mm(soil_depth_mm)

    # Water
    scene.rect(
        water_left_x,
        water_top_y,
        pond_edge_x - water_left_x,
        water_bottom_y - water_top_y,
        class_="water",
    )
    scene.line(water_left_x, water_top_y, pond_edge_x, water_top_y, stroke="#4a9fe6", stroke_width="1.6")
    scene.text(water_left_x + mm(40), water_top_y - mm(12), "Water level", class_="note")

    # Soil / bank
    scene.rect(
        pond_edge_x,
        bank_top_y,
        mm(bank_extend_mm),
        soil_bottom_y - bank_top_y,
        class_="soil",
        fill_opacity="0.6",
    )
    scene.text(pond_edge_x + mm(120), bank_top_y - mm(14), "Top of bank (reference)", class_="note")

    # Anchor trench
    trench_center_x = pond_edge_x + mm(trench_offset_mm)
    trench_left = trench_center_x - mm(trench_width_mm) / 2.0
    trench_top = bank_top_y
    trench_bottom = trench_top + mm(trench_depth_nominal)
    scene.rect(trench_left, trench_top, mm(trench_width_mm), trench_bottom - trench_top, fill="none", stroke="#333", stroke_width="2.0")
    scene.rect(trench_left, trench_top, mm(trench_width_mm), trench_bottom - trench_top, class_="soil", fill_opacity="0.45")
    scene.text(trench_center_x, trench_top - mm(16), "Anchor trench", anchor="middle", class_="note")
    scene.text(trench_center_x, trench_bottom + mm(16), "Backfill & compact", anchor="middle", class_="note")

    # Liner path
    liner_points = [
        (pond_edge_x - mm(18), water_bottom_y),
        (pond_edge_x - mm(18), water_top_y - mm(30)),
        (pond_edge_x, bank_top_y - mm(24)),
        (trench_left + mm(12), bank_top_y - mm(24)),
        (trench_left + mm(12), trench_bottom),
        (trench_left + mm(trench_width_mm) - mm(12), trench_bottom),
        (trench_left + mm(trench_width_mm) - mm(12), bank_top_y - mm(24)),
    ]
    scene.polyline(liner_points, class_="liner")
    scene.text(
        pond_edge_x + mm(80),
        bank_top_y - mm(36),
        "Liner wrapped over rim and into trench",
        class_="note",
    )

    # Rim above water note
    scene.text(
        pond_edge_x + mm(12),
        bank_top_y - mm(6),
        f"Keep rim ≥ {rim_above_water_mm:.0f} mm above water",
        class_="note",
    )

    # Dimensions
    horizontal_dimension(
        scene,
        pond_edge_x,
        trench_center_x,
        bank_top_y,
        f"≈ {trench_offset_mm:.0f} mm from pond edge",
        direction="up",
        offset=44,
    )
    depth_label = (
        f"{float(depth_range[0]):.0f}–{float(depth_range[1]):.0f} mm deep"
        if float(depth_range[0]) != float(depth_range[1])
        else f"{float(depth_range[0]):.0f} mm deep"
    )
    vertical_dimension(
        scene,
        trench_top,
        trench_bottom,
        trench_left + mm(trench_width_mm),
        depth_label,
        direction="right",
        offset=44,
    )

    return scene


# ---------------------------------------------------------------------------
# Timber clamp variant


def _render_timber_clamp(option: AttachmentOption) -> SvgScene:
    params = option.params
    scale = float(params.get("scale_px_per_mm", 1.35))
    mm = lambda value: float(value) * scale

    water_width_mm = params.get("water_width_mm", 320)
    water_depth_mm = params.get("water_depth_mm", 220)
    rim_board_depth_mm = params.get("rim_board_depth_mm", 90)
    rim_board_thickness_mm = params.get("rim_board_thickness_mm", 45)
    batten_size_mm = params.get("batten_size_mm", [45, 45])
    if isinstance(batten_size_mm, (int, float)):
        batten_size_mm = [batten_size_mm, batten_size_mm]
    batten_width_mm, batten_height_mm = batten_size_mm
    screw_spacing_mm = params.get("screw_spacing_mm", 180)
    min_screw_above_water_mm = params.get("screw_above_water_mm", 75)

    scene = SvgScene(pad=44.0)
    aria = option.aria_label or f"{option.title} — liner clamped under deck rim"
    scene.root.set("aria-label", aria)
    scene.root.set("data-diagram", f"edge-attachment-{option.key.lower()}")
    scene.add_css(
        """
        .soil { fill: #d9c4a1; stroke: #b79d73; stroke-width: 1.1; }
        .water { fill: #8cccf2; opacity: 0.72; }
        .deck { fill: #d7b996; stroke: #7b5532; stroke-width: 1.4; }
        .timber { fill: #c28f5c; stroke: #7b5532; stroke-width: 1.3; }
        .foam { fill: #cfe5e5; stroke: #7aa; stroke-width: 1.0; }
        .liner { fill: none; stroke: #1d1d1d; stroke-width: 4; stroke-linejoin: round; }
        .steel { fill: #9da7b4; }
        .note { font-size: 14px; fill: #444; }
        """
    )

    pond_edge_x = mm(water_width_mm)
    water_top_y = 0.0
    water_bottom_y = mm(water_depth_mm)
    deck_top_y = -mm(70)
    deck_thickness_mm = params.get("deck_board_thickness_mm", 28)
    deck_height = mm(deck_thickness_mm)
    rim_board_depth = mm(rim_board_depth_mm)
    rim_board_thickness = mm(rim_board_thickness_mm)
    batten_width = mm(batten_width_mm)
    batten_height = mm(batten_height_mm)

    rim_board_y = deck_top_y + deck_height
    batten_y = rim_board_y + rim_board_depth - batten_height
    foam_thickness_mm = params.get("foam_thickness_mm", 10)
    foam_height = mm(foam_thickness_mm)
    foam_y = rim_board_y + mm(6)
    screw_line_y = batten_y + batten_height / 2

    # Water and soil
    scene.rect(0, water_top_y, pond_edge_x, water_bottom_y - water_top_y, class_="water")
    scene.line(0, water_top_y, pond_edge_x, water_top_y, stroke="#4a9fe6", stroke_width="1.5")
    scene.rect(pond_edge_x, -mm(40), mm(320), water_bottom_y + mm(60), class_="soil", fill_opacity="0.6")
    scene.text(pond_edge_x + mm(20), water_top_y - mm(12), "Water level", class_="note")

    # Deck boards
    deck_width = mm(260)
    scene.rect(pond_edge_x, deck_top_y, deck_width, deck_height, class_="deck")
    scene.text(pond_edge_x + deck_width - mm(6), deck_top_y - mm(10), "Deck boards", anchor="end", class_="note")

    # Rim board
    scene.rect(pond_edge_x, rim_board_y, rim_board_thickness, rim_board_depth, class_="timber")
    scene.text(pond_edge_x + rim_board_thickness + mm(8), rim_board_y + rim_board_depth / 2 + mm(4), "Rim board", class_="note")

    # Foam / underlay
    scene.rect(pond_edge_x, foam_y, rim_board_thickness, foam_height, class_="foam")
    scene.text(pond_edge_x + rim_board_thickness + mm(16), foam_y + foam_height + mm(2), "Underlay / closed-cell foam", class_="note")

    # Clamp batten
    batten_x = pond_edge_x + rim_board_thickness
    scene.rect(batten_x, batten_y, batten_width, batten_height, class_="timber")
    scene.text(batten_x + batten_width + mm(12), batten_y + batten_height / 2 + mm(4), "Clamp batten 45×45 mm", class_="note")

    # Screws (two) representing spacing
    screw_width = mm(6)
    screw_height = batten_height + mm(24)
    first_screw_x = batten_x + batten_width / 2 - screw_width * 1.5
    scene.rect(first_screw_x, batten_y - mm(6), screw_width, screw_height, class_="steel")
    scene.rect(first_screw_x + screw_width * 2, batten_y - mm(6), screw_width, screw_height, class_="steel")
    scene.text(
        batten_x + batten_width + mm(18),
        batten_y + screw_height + mm(6),
        f"A2/A4 screws @ {screw_spacing_mm:.0f} mm centres",
        class_="note",
    )

    # Liner path
    liner_points = [
        (pond_edge_x - mm(18), water_bottom_y),
        (pond_edge_x - mm(18), water_top_y - mm(20)),
        (pond_edge_x, water_top_y - mm(32)),
        (pond_edge_x, foam_y + foam_height / 2),
        (batten_x, foam_y + foam_height / 2),
        (batten_x, batten_y + batten_height / 2),
    ]
    scene.polyline(liner_points, class_="liner")
    scene.text(pond_edge_x - mm(10), water_top_y - mm(28), "Liner never punctured below waterline", class_="note", anchor="end")

    # Picture frame board / overhang note
    scene.text(
        pond_edge_x + deck_width,
        deck_top_y - mm(22),
        "Picture-frame board with drip kerf",
        anchor="end",
        class_="note",
    )

    # Dimension: screw line above water
    vertical_dimension(
        scene,
        water_top_y,
        screw_line_y,
        batten_x + batten_width,
        f"Keep fasteners ≥ {min_screw_above_water_mm:.0f} mm above water line",
        direction="right",
        offset=40,
    )

    return scene


# ---------------------------------------------------------------------------
# Coping stones variant


def _render_coping(option: AttachmentOption) -> SvgScene:
    params = option.params
    scale = float(params.get("scale_px_per_mm", 1.2))
    mm = lambda value: float(value) * scale

    water_width_mm = params.get("water_width_mm", 320)
    water_depth_mm = params.get("water_depth_mm", 220)
    collar_width_mm = params.get("collar_width_mm", 180)
    collar_depth_mm = params.get("collar_depth_mm", 60)
    stone_thickness_mm = params.get("stone_thickness_mm", 45)
    gap_mm = params.get("shadow_gap_mm", 12)
    rim_above_water_mm = params.get("rim_above_water_mm", 60)

    scene = SvgScene(pad=44.0)
    aria = option.aria_label or f"{option.title} — coping stones over concrete collar"
    scene.root.set("aria-label", aria)
    scene.root.set("data-diagram", f"edge-attachment-{option.key.lower()}")
    scene.add_css(
        """
        .soil { fill: #d9c4a1; stroke: #b79d73; stroke-width: 1.1; }
        .water { fill: #8cccf2; opacity: 0.7; }
        .concrete { fill: #bfbfbf; stroke: #9d9d9d; stroke-width: 1.3; }
        .stone { fill: #e4e2da; stroke: #b3b0a8; stroke-width: 1.2; }
        .deck { fill: #d7b996; stroke: #7b5532; stroke-width: 1.3; }
        .liner { fill: none; stroke: #1d1d1d; stroke-width: 4; stroke-linejoin: round; }
        .note { font-size: 14px; fill: #444; }
        """
    )

    pond_edge_x = mm(water_width_mm)
    water_top_y = 0.0
    water_bottom_y = mm(water_depth_mm)
    bank_top_y = -mm(rim_above_water_mm)
    soil_bottom_y = water_bottom_y + mm(260)

    # Water and soil
    scene.rect(0, water_top_y, pond_edge_x, water_bottom_y - water_top_y, class_="water")
    scene.line(0, water_top_y, pond_edge_x, water_top_y, stroke="#4a9fe6", stroke_width="1.5")
    scene.rect(pond_edge_x, bank_top_y, mm(360), soil_bottom_y - bank_top_y, class_="soil", fill_opacity="0.6")

    # Concrete collar
    collar_x = pond_edge_x
    collar_y = water_top_y + mm(20)
    scene.rect(collar_x, collar_y, mm(collar_width_mm), mm(collar_depth_mm), class_="concrete")
    scene.text(
        collar_x + mm(collar_width_mm) / 2,
        collar_y - mm(12),
        f"Concrete collar {collar_width_mm:.0f} mm wide",
        anchor="middle",
        class_="note",
    )

    # Liner over collar
    liner_points = [
        (pond_edge_x - mm(18), water_bottom_y),
        (pond_edge_x - mm(18), water_top_y - mm(24)),
        (pond_edge_x, water_top_y - mm(36)),
        (collar_x + mm(collar_width_mm) / 2, collar_y - mm(18)),
        (collar_x + mm(collar_width_mm) / 2, collar_y + mm(collar_depth_mm)),
        (collar_x + mm(collar_width_mm), collar_y + mm(collar_depth_mm)),
    ]
    scene.polyline(liner_points, class_="liner")

    # Coping stone
    stone_width = mm(collar_width_mm) + mm(40)
    stone_x = collar_x - mm(20)
    stone_y = collar_y - mm(stone_thickness_mm)
    scene.rect(stone_x, stone_y, stone_width, mm(stone_thickness_mm), class_="stone")
    scene.text(stone_x + stone_width / 2, stone_y - mm(12), f"Coping stone {stone_thickness_mm:.0f} mm", anchor="middle", class_="note")

    # Deck boards with shadow gap
    deck_x = stone_x + stone_width + mm(gap_mm)
    deck_y = stone_y
    deck_width = mm(260)
    deck_height = mm(28)
    scene.rect(deck_x, deck_y, deck_width, deck_height, class_="deck")
    scene.text(deck_x + deck_width, deck_y - mm(10), "Decking with drip kerf", anchor="end", class_="note")
    scene.text(
        deck_x - mm(gap_mm / 2),
        deck_y + deck_height + mm(6),
        f"{gap_mm:.0f} mm drainage gap",
        anchor="middle",
        class_="note",
    )

    # Rim note
    scene.text(
        pond_edge_x + mm(24),
        bank_top_y - mm(8),
        f"Rim ≥ {rim_above_water_mm:.0f} mm above water level",
        class_="note",
    )

    return scene
