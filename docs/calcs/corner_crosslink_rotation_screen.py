#!/usr/bin/env python3
"""Relative in-plane corner-rotation screen for supplied corner-web SVGs.

This is deliberately a *comparison* model, not a laminate design or a release
calculation.  It uses the black filled material in the presentation SVGs,
registered through their dashed Arrangement-E outline, as an isotropic,
linear-elastic plane-stress plate.  The three horizontal-rail M8 lands are
given a unit rigid rotation about the rail intersection; the three vertical
rail lands are fixed.  Summed reactions give the plate-only relative rotational
stiffness.  This makes the thin/thick 55-to-55 cross-link comparison explicit,
without mistaking nearby material for link width.

The model omits bolt-hole removal, bolt/bedding compliance, tube flexibility,
orthotropy, C2 and basket actions.  Its absolute stiffness is therefore not an
installed-corner value.  It is only suitable for comparing materially identical
profiles under the same deliberately idealised rail-bolt boundary condition.
"""

from __future__ import annotations

from dataclasses import dataclass
import io
from pathlib import Path
import sys

import cairosvg
import numpy as np
from PIL import Image
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

sys.path.insert(0, str(Path(__file__).parent))
from corner_seat_web_screen import outline_transform  # noqa: E402


E_WET = 3_000.0       # N/mm2: deliberately low comparative screen modulus.
POISSON = 0.30
THICKNESS = 9.5       # mm, the lower-web comparison thickness.
PADS_A = ((55.0, 0.0), (125.0, 0.0), (195.0, 0.0))
PADS_B = ((0.0, 55.0), (0.0, 125.0), (0.0, 195.0))
PAD_RADIUS = 10.0     # mm: idealised M8 washer/bolt land, same all cases.


@dataclass(frozen=True)
class Case:
    name: str
    path: Path


CASES = (
    Case("lower-web thin", Path("docs/packs/c/diagrams/corner-web.svg")),
    Case("lower-web thick", Path("docs/packs/c/diagrams/corner-web_thick.svg")),
    Case("upper clam.14.3", Path("docs/packs/c/diagrams/corner-seat/clam.14.3.svg")),
    Case("upper clam.14.3 thick", Path("docs/packs/c/diagrams/corner-seat/clam.14.3_thick.svg")),
)


def load_mask(path: Path, pixels: int = 3000):
    """Return an Arrangement-E mm membership function from the filled SVG."""
    view_box, transform = outline_transform(path)
    rgba = np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(
        url=str(path), output_width=pixels, output_height=pixels
    ))).convert("RGBA"))
    # Paths are black. This excludes the grey dashed comparison outline.
    solid = (rgba[:, :, 3] > 127) & np.all(rgba[:, :, :3] < 20, axis=2)
    inverse = np.linalg.inv(transform)

    def contains(a: float, b: float) -> bool:
        # Source outline coordinates are Arrangement-E coordinates minus 1050.
        svg = transform @ np.array((a - 1050, b - 1050, 1.0))
        x_svg, y_svg = svg[:2]
        x = int(round((x_svg - view_box[0]) * pixels / view_box[2]))
        y = int(round((y_svg - view_box[1]) * pixels / view_box[3]))
        return 0 <= y < pixels and 0 <= x < pixels and bool(solid[y, x])

    # Derive material bounds using the transform rather than trusting viewBox crop.
    ys, xs = np.nonzero(solid)
    svg_points = np.c_[view_box[0] + xs * view_box[2] / pixels,
                        view_box[1] + ys * view_box[3] / pixels,
                        np.ones(len(xs))]
    local = (inverse @ svg_points.T).T[:, :2] + 1050
    return contains, (local[:, 0].min(), local[:, 0].max(),
                      local[:, 1].min(), local[:, 1].max()), len(xs)


def element_stiffness(points: np.ndarray) -> np.ndarray:
    """Constant-strain triangle stiffness, plane stress, N/mm."""
    (x1, y1), (x2, y2), (x3, y3) = points
    twice_area = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    area = abs(twice_area) / 2
    if area < 1e-9:
        raise ValueError("zero-area element")
    b = np.array((y2 - y3, y3 - y1, y1 - y2)) / twice_area
    c = np.array((x3 - x2, x1 - x3, x2 - x1)) / twice_area
    B = np.zeros((3, 6))
    B[0, 0::2] = b
    B[1, 1::2] = c
    B[2, 0::2] = c
    B[2, 1::2] = b
    D = E_WET / (1 - POISSON ** 2) * np.array(
        ((1, POISSON, 0), (POISSON, 1, 0), (0, 0, (1 - POISSON) / 2))
    )
    return THICKNESS * area * B.T @ D @ B


def screen(case: Case, spacing: float) -> tuple[float, int, int]:
    contains, bounds, _ = load_mask(case.path)
    amin, amax, bmin, bmax = bounds
    a = np.arange(np.floor(amin / spacing) * spacing,
                  np.ceil(amax / spacing) * spacing + spacing / 2, spacing)
    b = np.arange(np.floor(bmin / spacing) * spacing,
                  np.ceil(bmax / spacing) * spacing + spacing / 2, spacing)
    points = np.array([(x, y) for y in b for x in a])
    nx = len(a)
    triangles = []
    # Centroid test creates a regular, reproducible approximate boundary.
    for j in range(len(b) - 1):
        for i in range(len(a) - 1):
            n = j * nx + i
            for tri in ((n, n + 1, n + nx + 1), (n, n + nx + 1, n + nx)):
                centroid = points[list(tri)].mean(axis=0)
                if contains(*centroid):
                    triangles.append(tri)
    used = np.unique(np.asarray(triangles).ravel())
    remap = -np.ones(len(points), dtype=int)
    remap[used] = np.arange(len(used))
    points = points[used]
    triangles = [tuple(remap[list(t)]) for t in triangles]
    dof = 2 * len(points)
    rows, cols, vals = [], [], []
    for tri in triangles:
        ke = element_stiffness(points[list(tri)])
        ids = np.array([[2 * n, 2 * n + 1] for n in tri]).ravel()
        rr, cc = np.meshgrid(ids, ids, indexing="ij")
        rows.extend(rr.ravel()); cols.extend(cc.ravel()); vals.extend(ke.ravel())
    K = coo_matrix((vals, (rows, cols)), shape=(dof, dof)).tocsr()

    fixed: dict[int, float] = {}
    driven: set[int] = set()
    for x, y in PADS_B:
        for n, (px, py) in enumerate(points):
            if (px - x) ** 2 + (py - y) ** 2 <= PAD_RADIUS ** 2:
                fixed[2 * n] = 0.0; fixed[2 * n + 1] = 0.0
    # Unit positive rigid rotation about the rail intersection on rail A.
    for x, y in PADS_A:
        for n, (px, py) in enumerate(points):
            if (px - x) ** 2 + (py - y) ** 2 <= PAD_RADIUS ** 2:
                fixed[2 * n] = -py
                fixed[2 * n + 1] = px
                driven.add(2 * n); driven.add(2 * n + 1)
    if len(fixed) < 20:
        raise RuntimeError(f"{case.name}: bolt land not represented in mesh")
    fixed_ids = np.array(sorted(fixed))
    free = np.setdiff1d(np.arange(dof), fixed_ids)
    prescribed = np.array([fixed[i] for i in fixed_ids])
    rhs = -K[free][:, fixed_ids] @ prescribed
    displacement = np.zeros(dof)
    displacement[fixed_ids] = prescribed
    displacement[free] = spsolve(K[free][:, free], rhs)
    reactions = K @ displacement
    # Moment of reactions at rail-A prescribed lands, about (0,0), per radian.
    moment = 0.0
    for dof_id in driven:
        n, direction = divmod(dof_id, 2)
        x, y = points[n]
        moment += (-y if direction == 0 else x) * reactions[dof_id]
    # Energy check: all fixed reaction moment agrees with 2U for theta=1.
    energy_moment = float(displacement @ (K @ displacement))
    return abs(moment), len(points), len(triangles), energy_moment


def main() -> None:
    print("Idealised plate-only relative rotation stiffness, kN m/rad")
    print("case                         4 mm       3 mm       2 mm   elements")
    results = {}
    for case in CASES:
        values = []
        for spacing in (4.0, 3.0, 2.0):
            stiffness, nodes, elements, energy = screen(case, spacing)
            # For prescribed unit rotation, reaction moment and energy agree.
            if abs(stiffness - energy) / max(stiffness, 1) > 0.02:
                raise RuntimeError(f"energy mismatch in {case.name}")
            values.append((stiffness / 1e6, elements))
        results[case.name] = values[-1][0]
        print(f"{case.name:27} {values[0][0]:8.2f}  {values[1][0]:8.2f}  "
              f"{values[2][0]:8.2f}  {values[2][1]:7}")
    print("ratios at 2 mm:")
    print(f"  lower thick/thin = {results['lower-web thick'] / results['lower-web thin']:.3f}")
    print(f"  clam thick/thin  = {results['upper clam.14.3 thick'] / results['upper clam.14.3']:.3f}")


if __name__ == "__main__":
    main()
