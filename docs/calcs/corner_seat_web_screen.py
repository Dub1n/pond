#!/usr/bin/env python3
"""Repeatable first-pass screen for Arrangement E upper-web silhouettes.

This is deliberately not a plate FEA or a fabrication drawing.  It converts
the named bolt-to-bolt force paths into continuously radiused minimum-width
capsules, then reports the remaining plan area and writes an SVG concept.  The
separate strip calculation uses the same deliberately conservative 0.30 kN
complete-sling proof action already used in ``corner-v1.md``.

It is a guard against a visually convincing cut-out deleting a continuous
path.  Actual plate bending, washer bearing, wet laminate properties and the
complete upper/lower corner stack remain physical proof gates.
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import re
import xml.etree.ElementTree as element_tree

import cairosvg
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt, map_coordinates
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union


# Bolt/post/pad axes in Arrangement E local (a, b) millimetres.
P1 = (-125, 50)
P2 = (50, -125)
M55_B = (0, 55)
M55_A = (55, 0)
M195_A = (195, 0)
M195_B = (0, 195)
BASKET_INNER = (120, 120)
BASKET_SIDE_A = (120, -60)
BASKET_SIDE_B = (-60, 120)
BASKET_OUTER = (-60, -60)

SAMPLES = (
    "octagon.7.2.svg", "octagon.9.4.svg", "octagon.11.8.svg",
    "hand.7.svg", "hand.9.svg", "hand.12.svg",
    "clam.10.3.svg", "clam.14.3.svg", "clam.16.2.svg",
)


def capsule(p0: tuple[float, float], p1: tuple[float, float], width: float):
    """Return a round-capped, mm-coordinate bridge."""
    return LineString([p0, p1]).buffer(width / 2, quad_segs=12)


def complete_hybrid() -> Polygon:
    """The complete Octagon/Hand hybrid specified by the user.

    It contains the base C2-to-55 routes as well as the two additional
    C2-to-side-basket-to-195 routes.  The two rail strips remain 80 mm; C2
    routes remain 75 mm; basket routes remain 50 mm as a screening choice.
    The latter are not a released basket-bearing dimension.
    """
    parts = [
        capsule(P1, M55_B, 75),
        capsule(P2, M55_A, 75),
        capsule(M55_B, M195_B, 80),
        capsule(M55_A, M195_A, 80),
        capsule(M55_B, M55_A, 80),
        capsule(M195_A, BASKET_INNER, 50),
        capsule(BASKET_INNER, M195_B, 50),
        capsule(M195_A, BASKET_SIDE_A, 50),
        capsule(BASKET_SIDE_A, P2, 50),
        capsule(M195_B, BASKET_SIDE_B, 50),
        capsule(BASKET_SIDE_B, P1, 50),
        capsule(BASKET_OUTER, (27.5, 27.5), 50),
    ]
    # Explicit washer/post lands, rather than relying on a line end-cap.
    for p, radius in [
        (P1, 15), (P2, 15), (M55_A, 15), (M55_B, 15),
        (M195_A, 15), (M195_B, 15), (BASKET_INNER, 20),
        (BASKET_SIDE_A, 20), (BASKET_SIDE_B, 20), (BASKET_OUTER, 20),
    ]:
        parts.append(Point(p).buffer(radius, quad_segs=12))
    # The dashed octagon in the variant drawings is a comparison envelope, not
    # a hard material boundary. Clipping to it would pinch a 75 mm C2 bridge.
    # The controlling physical boundary is the C2-tip plane (a+b >= -200).
    web = unary_union(parts)
    # Five-mm offset pair removes unmanufacturable re-entrant points while
    # preserving a 5 mm minimum inside radius as a geometric rule.
    return web.buffer(5, quad_segs=12).buffer(-5, quad_segs=12)


def strip_stress(width: float, thickness: float, load_n: float = 300.0,
                 length: float = 125.1) -> float:
    """Simple supported strip comparison: sigma = 6 P L / (b t^2)."""
    return 6 * load_n * length / (width * thickness ** 2)


def svg_path(poly: Polygon) -> str:
    def ring(coords) -> str:
        first, *rest = coords
        return "M " + " L ".join(
            [f"{first[0]:.3f} {first[1]:.3f}"] +
            [f"{x:.3f} {y:.3f}" for x, y in rest]
        ) + " Z"

    path = ring(list(poly.exterior.coords))
    for interior in poly.interiors:
        path += " " + ring(list(interior.coords))
    return path


def matrix(text: str) -> np.ndarray:
    """Read the Serif-export matrix form used by the supplied SVGs."""
    a, b, c, d, e, f = map(
        float, re.search(r"matrix\(([^)]+)\)", text).group(1).split(",")
    )
    return np.array(((a, c, e), (b, d, f), (0.0, 0.0, 1.0)))


def outline_transform(path: Path) -> tuple[list[float], np.ndarray]:
    """Return viewport and local-mm-to-export transform for a variant SVG."""
    root = element_tree.parse(path).getroot()
    view_box = list(map(float, root.attrib["viewBox"].split()))
    found: list[np.ndarray] = []

    def walk(node, accumulated: np.ndarray) -> None:
        if "transform" in node.attrib:
            accumulated = accumulated @ matrix(node.attrib["transform"])
        if node.attrib.get("id") == "Outline":
            found.append(accumulated)
        for child in node:
            walk(child, accumulated)

    walk(root, np.eye(3))
    if len(found) != 1:
        raise ValueError(f"expected one reference outline in {path}")
    return view_box, found[0]


def supplied_variant_metrics(path: Path, pixels: int = 3000) -> tuple[float, dict[str, float]]:
    """Measure the rendered supplied silhouette in Arrangement-E millimetres.

    The drawings are presentation SVGs, not direct mm profiles.  Their dashed
    reference outline provides the transform from the present local coordinates
    to pixels, avoiding any dependence on each file's cropped viewBox.
    """
    view_box, transform = outline_transform(path)
    png = cairosvg.svg2png(url=str(path), output_width=pixels,
                           output_height=pixels)
    rgba = np.asarray(Image.open(io.BytesIO(png)).convert("RGBA"))
    solid = (rgba[:, :, 3] > 127) & np.all(rgba[:, :, :3] < 20, axis=2)
    px_per_mm_x = abs(transform[0, 0]) * pixels / view_box[2]
    px_per_mm_y = abs(transform[1, 1]) * pixels / view_box[3]
    pixel_area = 1 / (px_per_mm_x * px_per_mm_y)
    distance = distance_transform_edt(solid) * np.sqrt(pixel_area)

    def pixel(a: float, b: float) -> tuple[float, float]:
        # The dashed source outline is expressed at (a-1050, b-1050).
        point = transform @ np.array((a - 1050, b - 1050, 1.0))
        return ((point[0] - view_box[0]) * pixels / view_box[2],
                (point[1] - view_box[1]) * pixels / view_box[3])

    paths = {
        "c2": ((P1, M55_B), (P2, M55_A)),
        "side": ((BASKET_SIDE_A, M55_A), (BASKET_SIDE_B, M55_B)),
        "inner": ((M195_A, BASKET_INNER), (BASKET_INNER, M195_B)),
    }
    widths = {}
    for name, lines in paths.items():
        measured = []
        for start, end in lines:
            start_array, end_array = np.array(start), np.array(end)
            for fraction in np.linspace(0.03, 0.97, 95):
                x, y = pixel(*(start_array + fraction * (end_array - start_array)))
                measured.append(2 * map_coordinates(
                    distance, ((y,), (x,)), order=1, mode="constant"
                )[0])
        widths[name] = min(measured)
    return solid.sum() * pixel_area, widths


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--measure-supplied", action="store_true")
    args = parser.parse_args()
    if args.measure_supplied:
        directory = Path(__file__).parents[1] / "packs/c/diagrams/corner-seat"
        for filename in SAMPLES:
            area, widths = supplied_variant_metrics(directory / filename)
            print(f"{filename[:-4]:16} {area:7.0f} mm2  "
                  f"C2 {widths['c2']:4.1f}  side {widths['side']:4.1f}  "
                  f"inner {widths['inner']:4.1f}")
        return
    web = complete_hybrid()
    out = Path(__file__).parents[1] / "packs/c/diagrams/corner-seat/"
    out.mkdir(parents=True, exist_ok=True)
    svg = out / "octagon-hand-complete.svg"
    svg.write_text(
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"380mm\" "
        "height=\"380mm\" viewBox=\"-160 -160 390 390\">\n"
        f"  <path d=\"{svg_path(web)}\" fill=\"#000\" "
        "fill-rule=\"evenodd\"/>\n</svg>\n"
    )
    print(f"octagon-hand-complete area: {web.area:.0f} mm2")
    print(f"minimum a+b boundary coordinate: "
          f"{min(x + y for x, y in web.exterior.coords):.1f} mm")
    for material, thickness in [("GRP", 9.5), ("5083", 6.0)]:
        print(f"C2 75 mm strip, {material} {thickness:g} mm: "
              f"{strip_stress(75, thickness):.1f} MPa")
    print(svg)


if __name__ == "__main__":
    main()
