#!/usr/bin/env python3
"""Emit clean millimetre SVG profiles for the Pack C Deepnest job.

The generated files are intentionally cutter-profile geometry only: no labels,
holes, kerf compensation or drilling.  Hole/washer detail remains controlled
by the Pack C fabrication documents.
"""

from pathlib import Path
from shutil import copyfile
import sys
import xml.etree.ElementTree as element_tree

import numpy as np
from svgpathtools import parse_path


ROOT = Path(__file__).parent
PROFILES = ROOT / "profiles"
JOB = ROOT / "jobs" / "full-grp"
PACK = ROOT.parent
sys.path.insert(0, str(PACK.parent.parent / "calcs"))
from corner_seat_web_screen import matrix, outline_transform  # noqa: E402


def svg(name, points, width, height):
    """Write one closed profile with a 5 mm display margin."""
    min_x = min(x for x, _ in points)
    min_y = min(y for _, y in points)
    shifted = [(x - min_x + 5, y - min_y + 5) for x, y in points]
    path = "M " + " L ".join(f"{x:g},{y:g}" for x, y in shifted) + " Z"
    text = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width + 10:g}mm" '
        f'height="{height + 10:g}mm" viewBox="0 0 {width + 10:g} {height + 10:g}">\n'
        f'  <path d="{path}" fill="#000000"/>\n'
        "</svg>\n"
    )
    (PROFILES / name).write_text(text)


def transformed_design_profile(name, source, path_id):
    """Emit one supplied design silhouette in Arrangement-E millimetres.

    The corner-design SVGs are presentation drawings.  Their dashed `Outline`
    is the authoritative transform between design coordinates and Arrangement
    E millimetres; the viewBox is not.  Retain the exact Bézier *outer* outline
    while stripping the dashed outline, internal water-flow cut-outs and all
    presentation transforms.  The latter cannot be used as nesting voids:
    they need their own 5 mm cutter clearance and remain structural details.
    """
    root = element_tree.parse(source).getroot()
    target = None

    def walk(node, accumulated):
        nonlocal target
        if "transform" in node.attrib:
            accumulated = accumulated @ matrix(node.attrib["transform"])
        if node.tag.endswith("path") and node.attrib.get("id") == path_id:
            target = (node.attrib["d"], accumulated)
        for child in node:
            walk(child, accumulated)

    walk(root, np.eye(3))
    if target is None:
        raise ValueError(f"could not find {path_id!r} in {source}")
    _, outline = outline_transform(source)
    path, primary = target
    path = path[:path.upper().index("Z") + 1]
    # raw design path -> displayed SVG -> Arrangement-E local mm.
    local = np.array(((1.0, 0.0, 1050.0), (0.0, 1.0, 1050.0), (0.0, 0.0, 1.0))) @ np.linalg.inv(outline) @ primary
    a, b, c, d, e, f = (local[0, 0], local[1, 0], local[0, 1],
                         local[1, 1], local[0, 2], local[1, 2])
    # Deepnest's SVG importer is unreliable for this supplied cubic-path plus
    # matrix combination.  Flatten only the outer curve to <=5 mm chords,
    # preserving a far more faithful cutter/nesting contour than a convex or
    # polygonal-envelope substitute.
    points = []
    for segment in parse_path(path):
        count = max(1, int(np.ceil(segment.length(error=1e-5) * abs(a) / 5)))
        for fraction in np.linspace(0, 1, count, endpoint=False):
            value = segment.point(fraction)
            points.append((a * value.real + c * value.imag + e,
                           b * value.real + d * value.imag + f))
    min_x = min(x for x, _ in points)
    min_y = min(y for _, y in points)
    max_x = max(x for x, _ in points)
    max_y = max(y for _, y in points)
    points = [(x - min_x + 5, y - min_y + 5) for x, y in points]
    path = "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in points) + " Z"
    width, height = max_x - min_x + 10, max_y - min_y + 10
    text = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.3f}mm" '
        f'height="{height:.3f}mm" viewBox="0 0 {width:.3f} {height:.3f}">\n'
        f'  <path d="{path}" fill="#000000"/>\n'
        '</svg>\n'
    )
    (PROFILES / name).write_text(text)


def main():
    PROFILES.mkdir(parents=True, exist_ok=True)
    JOB.mkdir(parents=True, exist_ok=True)

    # Outer contour only; radii and strap slots are fabrication-detail gates.
    h = [(-125, -125), (-75, -125), (-75, -45), (75, -45),
         (75, -125), (125, -125), (125, 125), (75, 125),
         (75, 45), (-75, 45), (-75, 125), (-125, 125)]
    bridge = [(0, 0), (110, 0), (110, 50), (0, 50)]
    svg("r51-upper-h.svg", h, 250, 250)
    svg("r51-lower-bridge.svg", bridge, 110, 50)
    transformed_design_profile(
        "corner-upper-pod-t30.svg",
        PACK / "diagrams/corner-seat/clam.14.3_thick.svg",
        "clam.14.3_thick",
    )
    transformed_design_profile(
        "corner-lower-web.svg", PACK / "diagrams/corner-web_thick.svg",
        "Lower_plate",
    )

    # The CLI treats each SVG as one item; make explicit numbered copies.
    quantities = {
        "r51-upper-h.svg": 9,
        "r51-lower-bridge.svg": 18,
        "corner-upper-pod-t30.svg": 4,
        "corner-lower-web.svg": 4,
    }
    for source, quantity in quantities.items():
        for index in range(1, quantity + 1):
            copyfile(PROFILES / source, JOB / f"{Path(source).stem}-{index:02d}.svg")

    # Deepnest CLI defaults to inches/72 units: this makes the job millimetres.
    (JOB / "deepnest-mm.json").write_text(
        '{\n  "units": "mm",\n  "scale": 1\n}\n'
    )


if __name__ == "__main__":
    main()
