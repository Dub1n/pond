#!/usr/bin/env python3
from __future__ import annotations

"""
Baseline renderer sanity check.

Renders three non-overlapping squares whose side lengths come from the current
time (HH, MM, SS) or a supplied time. Counts pixel coverage per square to verify
that rendering + rasterisation are fresh (no stale assets) and match expected
areas. Can be used in CI with a fixed time and --fresh-check.
"""

import argparse
import dataclasses
import io
import sys
from pathlib import Path
from datetime import datetime, time
from typing import Iterable, Sequence

import cairosvg
from PIL import Image
from shapely.geometry import Polygon as ShapelyPolygon

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagramming.materials import get_material_style
from diagramming.planner.bundle import GeometryBundle, PolygonFeature
from diagramming.planner.geometry import create_rectangle
from diagramming.renderers import SvgRenderer


@dataclasses.dataclass
class SquareMetrics:
    label: str
    time_value: float
    side: float
    expected_area: float
    expected_ratio: float
    measured_ratio: float
    measured_area: float
    measured_side: float
    pixels: int


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _count_pixels(image: Image.Image, target: tuple[int, int, int], tolerance: int = 2) -> int:
    r_t, g_t, b_t = target
    count = 0
    for r, g, b in image.getdata():
        if abs(r - r_t) <= tolerance and abs(g - g_t) <= tolerance and abs(b - b_t) <= tolerance:
            count += 1
    return count


def _build_bundle(sides: Sequence[float], canvas: float, scale: float, pad: float) -> GeometryBundle:
    bundle = GeometryBundle(view="plan", pad=pad, scale=scale, background="#ffffff")

    def _square_feature(
        ident: str,
        origin: tuple[float, float],
        side: float,
        material: str,
        class_name: str,
    ) -> PolygonFeature:
        ring = create_rectangle(origin, (side, side))
        shape = ShapelyPolygon(ring[:-1])
        return PolygonFeature(
            id=ident,
            outer=ring,
            holes=(),
            class_name=class_name,
            height=1.0,
            elevation=0.0,
            material=material,
            metadata={},
            shape=shape,
        )

    margin = 24.0
    s_h, s_m, s_s = sides
    canvas_size = max(canvas, s_h + s_m + s_s + margin * 4, max(sides) + margin * 2)

    # Base canvas to keep output size stable.
    canvas_feature = _square_feature("baseline_canvas", (0.0, 0.0), canvas_size, "soil", "baseline-canvas")
    bundle.add_polygon(canvas_feature)

    positions = [
        (margin, margin),
        (margin + s_h + margin, margin),
        (margin + s_h + margin + s_m + margin, margin),
    ]
    materials = ["decking", "water", "pad"]
    ids = ["square_hh", "square_mm", "square_ss"]
    for ident, origin, side, material in zip(ids, positions, sides, materials):
        style = get_material_style(material)
        class_name = style.css_class if style else "component"
        bundle.add_polygon(_square_feature(ident, origin, side, material, class_name))

    bundle.build_legend()
    return bundle


def _timestamp_from_str(raw: str) -> time:
    try:
        parsed = datetime.strptime(raw, "%H:%M:%S").time()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("time must be HH:MM:SS") from exc
    return parsed


def _square_metrics(
    bundle: GeometryBundle,
    squares: Iterable[PolygonFeature],
    source_sizes: Sequence[float],
) -> tuple[list[SquareMetrics], int]:
    extent = bundle.extent()
    if extent is None:
        raise SystemExit("Bundle has no extent to measure.")
    width = extent[2] - extent[0] + 2 * bundle.pad
    height = extent[3] - extent[1] + 2 * bundle.pad
    view_area = width * height

    renderer = SvgRenderer(extra_css=".baseline_canvas { fill: #ffffff; stroke: none; }")
    svg_text = renderer.render(bundle)
    png_bytes = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"))
    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    total_pixels = image.width * image.height

    metrics: list[SquareMetrics] = []
    for square, source_size in zip(squares, source_sizes):
        style = get_material_style(square.material)
        if style is None or not style.svg_fill:
            raise SystemExit(f"No material style for square '{square.id}'")
        target_rgb = _hex_to_rgb(style.svg_fill)
        pixel_count = _count_pixels(image, target_rgb)
        expected_area = square.shape.area if square.shape is not None else square.outer[0][0] ** 2
        expected_ratio = expected_area / view_area
        measured_ratio = pixel_count / total_pixels if total_pixels else 0.0
        measured_area = measured_ratio * view_area
        metrics.append(
            SquareMetrics(
                label=square.id,
                time_value=source_size,
                side=square.outer[1][0] - square.outer[0][0],
                expected_area=expected_area,
                expected_ratio=expected_ratio,
                measured_ratio=measured_ratio,
                measured_area=measured_area,
                measured_side=measured_area ** 0.5,
                pixels=pixel_count,
            )
        )
    return metrics, total_pixels


def run_check(
    ts: time,
    canvas: float,
    scale: float,
    pad: float,
    tolerance: float,
    fresh_check: bool,
    multiplier: float,
    abs_tolerance: float,
) -> int:
    base_sides = [max(1.0, float(ts.hour)), max(1.0, float(ts.minute)), max(1.0, float(ts.second))]
    sides = [value * multiplier for value in base_sides]
    bundle = _build_bundle(sides, canvas=canvas, scale=scale, pad=pad)
    squares = [p for p in bundle.polygons if p.id.startswith("square_")]
    metrics, total_pixels = _square_metrics(bundle, squares, base_sides)

    print(f"timestamp: {ts.isoformat()}")
    for entry in metrics:
        print(
            f"{entry.label}: time_value={entry.time_value:.0f}, expected_side={entry.side:.2f}, "
            f"sqrt_expected_area={entry.expected_area ** 0.5:.2f}, "
            f"measured_side≈{entry.measured_side:.2f}, "
            f"expected_ratio={entry.expected_ratio:.4f}, "
            f"measured_ratio={entry.measured_ratio:.4f} "
            f"(pixels {entry.pixels}/{total_pixels})"
        )

    if fresh_check:
        fresh = True
        for entry in metrics:
            if entry.expected_ratio == 0:
                continue
            diff = abs(entry.measured_ratio - entry.expected_ratio)
            allowed = max(entry.expected_ratio * tolerance, abs_tolerance)
            if diff > allowed:
                fresh = False
                break
        print(
            f"fresh: {'true' if fresh else 'false'} "
            f"(tolerance {tolerance * 100:.1f}% or abs {abs_tolerance:.5f} on ratios)"
        )
        return 0 if fresh else 1
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Baseline render + raster sanity check.")
    parser.add_argument(
        "--time",
        type=_timestamp_from_str,
        help="Optional HH:MM:SS to use instead of now (for deterministic CI runs).",
    )
    parser.add_argument("--canvas", type=float, default=256.0, help="Canvas square size (default: 256).")
    parser.add_argument("--scale", type=float, default=4.0, help="Bundle scale (default: 4).")
    parser.add_argument(
        "--multiplier",
        type=float,
        default=8.0,
        help="Multiply HH/MM/SS values by this factor to size the squares (default: 8).",
    )
    parser.add_argument("--pad", type=float, default=24.0, help="Bundle pad (default: 24).")
    parser.add_argument(
        "--fresh-check",
        action="store_true",
        help="Compare measured ratios to expected and exit non-zero on mismatch.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.05,
        help="Relative tolerance for fresh check (default: 0.05 == 5%%).",
    )
    parser.add_argument(
        "--abs-tolerance",
        type=float,
        default=0.0005,
        help="Absolute tolerance floor for fresh check (default: 0.0005).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    ts = args.time or datetime.now().time()
    return run_check(
        ts,
        canvas=args.canvas,
        scale=args.scale,
        pad=args.pad,
        tolerance=args.tolerance,
        fresh_check=args.fresh_check,
        multiplier=args.multiplier,
        abs_tolerance=args.abs_tolerance,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
