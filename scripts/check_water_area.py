#!/usr/bin/env python3
"""
Quick check for water coverage in rendered plan views.

Example:
  scripts/check_water_area.py diagrams/specs/option-c.yaml --view plan
"""
from __future__ import annotations

import argparse
import io
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import cairosvg
from PIL import Image
from shapely.geometry import Polygon
from shapely.ops import unary_union
from xml.etree import ElementTree as ET
from datetime import datetime
import contextlib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagramming.relationships import ConstraintSolver, RelationshipPlanner, load_relationship_spec
from diagramming.renderers import SvgRenderer
from scripts.baseline_render_check import run_check as baseline_run_check


@dataclass
class WaterMetrics:
    spec: Path
    option: str
    view: str
    bundle_area: float
    water_area: float
    expected_visible_area: float
    view_area: float
    expected_ratio: float
    measured_ratio: float
    water_pixels: int
    total_pixels: int


def _visible_water_area(bundle, water_feature, higher_shapes: Sequence[Polygon]) -> float:
    if water_feature.shape is None:
        return 0.0
    if not higher_shapes:
        return water_feature.shape.area
    cover = unary_union(higher_shapes)
    if cover.is_empty:
        return water_feature.shape.area
    remainder = water_feature.shape.difference(cover)
    return remainder.area


def _count_water_pixels(svg_text: str) -> tuple[int, int]:
    png_bytes = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"))
    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    water_pixels = 0
    total = image.width * image.height
    for r, g, b in image.getdata():
        if b >= max(r, g) + 20:
            water_pixels += 1
    return water_pixels, total


def _pad_extent(bundle) -> tuple[float, float]:
    extent = bundle.extent()
    if extent is None:
        return (0.0, 0.0)
    width = extent[2] - extent[0]
    height = extent[3] - extent[1]
    pad = getattr(bundle, "pad", 0.0) or 0.0
    return (width + 2 * pad, height + 2 * pad)


def measure_water(spec_path: Path, option_key: str | None, view: str = "plan") -> WaterMetrics:
    spec = load_relationship_spec(spec_path)
    option = option_key or (spec.info.option or "relationship")
    solver = ConstraintSolver(spec)
    solved = solver.solve()
    if not solved.diagnostics.ok:
        detail = "; ".join(diag.message for diag in solved.diagnostics.errors)
        raise SystemExit(f"Spec failed to solve: {detail}")
    planner = RelationshipPlanner(spec, solved)
    planned_views = planner.plan()
    try:
        planned = next(p for p in planned_views if p.view == view)
    except StopIteration as exc:
        available = ", ".join(p.view for p in planned_views)
        raise SystemExit(f"View '{view}' not found. Available views: {available}") from exc
    bundle = planned.bundle

    def _is_water(p) -> bool:
        return (
            (p.class_name or "").startswith("component-water")
            or (p.material == "water")
            or ("water" in p.id)
        )

    try:
        water_feature = next(p for p in bundle.polygons if _is_water(p))
    except StopIteration as exc:
        raise SystemExit("No water polygon found in bundle.") from exc
    higher_shapes: list[Polygon] = []
    for poly in bundle.polygons:
        if poly is water_feature:
            continue
        top = poly.elevation + poly.height
        if top <= water_feature.elevation + water_feature.height:
            continue
        if poly.shape is not None:
            higher_shapes.append(poly.shape)

    expected_area = _visible_water_area(bundle, water_feature, higher_shapes)
    width, height = _pad_extent(bundle)
    view_area = width * height
    renderer = SvgRenderer()
    svg_text = renderer.render(bundle)
    parsed_width = 0.0
    parsed_height = 0.0
    try:
        root = ET.fromstring(svg_text)
        path = root.find(".//{http://www.w3.org/2000/svg}path[@data-id='pond_water']")
        if path is None:
            path = root.find(".//{http://www.w3.org/2000/svg}path[@data-id='water']")
        if path is not None:
            tokens = (
                path.attrib["d"]
                .replace(",", " ")
                .replace("M", " ")
                .replace("L", " ")
                .replace("Z", " ")
                .split()
            )
            nums = [float(tok) for tok in tokens if tok.strip()]
            coords = list(zip(nums[0::2], nums[1::2]))
            xs = [x for x, _ in coords]
            ys = [y for _, y in coords]
            parsed_width = max(xs) - min(xs)
            parsed_height = max(ys) - min(ys)
    except Exception:
        pass
    water_pixels, total_pixels = _count_water_pixels(svg_text)
    expected_ratio = expected_area / view_area if view_area else 0.0
    measured_ratio = water_pixels / total_pixels if total_pixels else 0.0
    return WaterMetrics(
        spec=spec_path,
        option=option,
        view=view,
        bundle_area=sum(p.shape.area for p in bundle.polygons if p.shape is not None),
        water_area=water_feature.shape.area if water_feature.shape is not None else 0.0,
        expected_visible_area=expected_area,
        view_area=view_area,
        expected_ratio=expected_ratio,
        measured_ratio=measured_ratio,
        water_pixels=water_pixels,
        total_pixels=total_pixels,
    )


def format_metrics(metrics: WaterMetrics) -> str:
    return (
        f"{metrics.spec.name} option {metrics.option} ({metrics.view}):\n"
        f"  expected visible water area: {metrics.expected_visible_area:.2f}\n"
        f"  view area: {metrics.view_area:.2f}\n"
        f"  expected ratio: {metrics.expected_ratio:.4f}\n"
        f"  measured ratio: {metrics.measured_ratio:.4f} "
        f"(pixels {metrics.water_pixels}/{metrics.total_pixels})"
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check water visibility in rendered plans.")
    parser.add_argument("spec", type=Path, help="Path to spec YAML.")
    parser.add_argument("--option", help="Option key to render (defaults to info.option).")
    parser.add_argument("--view", default="plan", help="View name (default: plan)")
    parser.add_argument(
        "--skip-baseline",
        action="store_true",
        help="Skip baseline render freshness check (default: run it).",
    )
    args = parser.parse_args(argv)

    metrics = measure_water(args.spec, args.option, args.view)
    print(format_metrics(metrics))

    if not args.skip_baseline:
        buf = io.StringIO()
        ts = datetime.now().time()
        with contextlib.redirect_stdout(buf):
            baseline_code = baseline_run_check(
                ts=ts,
                canvas=256.0,
                scale=4.0,
                pad=24.0,
                tolerance=0.05,
                fresh_check=True,
                multiplier=8.0,
                abs_tolerance=0.0005,
            )
        baseline_out = buf.getvalue().strip()
        fresh = baseline_code == 0
        status_line = (
            "Baseline render sanity check passed; renders appear fresh. "
            "Run `.venv/bin/python scripts/baseline_render_check.py --fresh-check` for details."
            if fresh
            else "Baseline render sanity check failed; rerun `.venv/bin/python scripts/baseline_render_check.py --fresh-check` "
            "to inspect freshness before trusting measurements."
        )
        print(status_line)
        if not fresh and baseline_out:
            print(baseline_out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
