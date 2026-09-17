#!/usr/bin/env python3
"""Generate and quantify the split-seat/flat-bar GRP nesting cases.

The generated SVGs are cutting-envelope inputs, not fabrication drawings.
Dimensions are millimetres.  Corner silhouettes are taken from the supplied
SVGs; round-capped seat parts are generated from their connection-centre spans.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Polygon
from svgpathtools import parse_path


ROOT = Path(__file__).resolve().parents[2]
CASES = (250, 225, 200)
COUNTS = {
    "upper-arm": 18,
    "upper-bridge": 9,
    "lower-bridge": 18,
    "corner-upper-half": 8,
    "corner-lower-web": 4,
}

# Connection-controlled widths.  The bridge covers the two +/-28 mm bolt rows
# with 17 mm transverse centre-to-edge distance.  The arm and lower bridge
# retain at least twice the M8 diameter from hole centre to a transverse edge;
# their wet coupons still decide whether these screening minima are usable.
ARM_WIDTH = 40.0
UPPER_BRIDGE_WIDTH = 90.0
LOWER_BRIDGE_WIDTH = 35.0
LOWER_BRIDGE_SPAN = 56.0


def capsule(span: float, width: float) -> Polygon:
    """Round-capped member: overall length is span + width."""
    return LineString(((width / 2, width / 2),
                       (width / 2 + span, width / 2))).buffer(
        width / 2, quad_segs=48
    )


def sampled_svg_path(path: Path, element_id: str | None = None) -> Polygon:
    root = ET.parse(path).getroot()
    candidates = [e for e in root.iter() if e.tag.endswith("path")]
    element = (next(e for e in candidates if e.get("id") == element_id)
               if element_id else candidates[0])
    parsed = parse_path(element.get("d"))
    loop = parsed.continuous_subpaths()[0]
    points = []
    for segment in loop:
        points.extend((z.real, z.imag) for z in
                      (segment.point(t) for t in np.linspace(0, 1, 25)))
    return Polygon(points)


def normalise(poly: Polygon) -> Polygon:
    min_x, min_y, _, _ = poly.bounds
    return affinity.translate(poly, -min_x, -min_y)


def corner_upper() -> Polygon:
    poly = sampled_svg_path(
        ROOT / "docs/packs/c/diagrams/corner-rework/single-upper.svg"
    )
    # The supplied drawing uses the same 0.18 px/mm convention as the existing
    # corner studies.  A 45 degree stock orientation minimises its width.
    poly = affinity.scale(poly, xfact=1 / 0.18, yfact=1 / 0.18,
                          origin=(0, 0))
    return normalise(affinity.rotate(poly, 45, origin=(0, 0)))


def corner_lower() -> Polygon:
    poly = sampled_svg_path(
        ROOT / "docs/packs/c/diagrams/corner-web_thick.svg", "Lower_plate"
    )
    poly = affinity.scale(poly, xfact=1 / 0.18, yfact=1 / 0.18,
                          origin=(0, 0))
    return normalise(affinity.rotate(poly, 45, origin=(0, 0)))


def case_parts(base: int) -> dict[str, Polygon]:
    return {
        "upper-arm": capsule(base, ARM_WIDTH),
        "upper-bridge": capsule(base, UPPER_BRIDGE_WIDTH),
        "lower-bridge": capsule(LOWER_BRIDGE_SPAN, LOWER_BRIDGE_WIDTH),
        "corner-upper-half": corner_upper(),
        "corner-lower-web": corner_lower(),
    }


def write_svg(poly: Polygon, path: Path) -> None:
    poly = normalise(poly)
    _, _, width, height = poly.bounds
    coords = " ".join(f"{x:.3f},{y:.3f}" for x, y in poly.exterior.coords)
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.3f}mm" '
        f'height="{height:.3f}mm" viewBox="0 0 {width:.3f} {height:.3f}">\n'
        f'  <polygon points="{coords}" fill="#000000"/>\n</svg>\n'
    )


def generate(base: int, output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    parts = case_parts(base)
    for name, count in COUNTS.items():
        for index in range(1, count + 1):
            write_svg(parts[name], output / f"{name}-{index:02d}.svg")


def report() -> None:
    print("base | arm WxL | upper bridge WxL | lower bridge WxL | cut-envelope area")
    for base in CASES:
        parts = case_parts(base)
        area = sum(parts[name].area * count
                   for name, count in COUNTS.items())
        print(
            f"{base:>4} | {ARM_WIDTH:.0f}x{base + ARM_WIDTH:.0f} | "
            f"{UPPER_BRIDGE_WIDTH:.0f}x{base + UPPER_BRIDGE_WIDTH:.0f} | "
            f"{LOWER_BRIDGE_WIDTH:.0f}x"
            f"{LOWER_BRIDGE_SPAN + LOWER_BRIDGE_WIDTH:.0f} | "
            f"{area / 1_000_000:.4f} m2 "
            f"({area / 600_000:.3f} bars by area)"
        )
    for name, poly in (("upper", corner_upper()), ("lower", corner_lower())):
        min_x, min_y, max_x, max_y = poly.bounds
        print(f"corner {name}: {max_x-min_x:.2f} x {max_y-min_y:.2f} mm, "
              f"{poly.area:.0f} mm2")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", type=int, choices=CASES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report()
    if args.generate:
        if not args.output:
            parser.error("--output is required with --generate")
        generate(args.generate, args.output)


if __name__ == "__main__":
    main()
