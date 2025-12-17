#!/usr/bin/env python3
"""
Helper to prototype a general mirror transform for relationship-first specs.

Given a plane (normal + point), it emits:
- A 4x4 reflection matrix (applied as M @ [x, y, z, 1]^T).
- A right-handed local frame on the mirror plane (tangent, bitangent, normal),
  with the tangent flipped as needed to restore det > 0 after reflection.

This is a standalone demo; it does not modify the solver. Use it to sanity-check
future mirror syntax/implementation.
"""
from __future__ import annotations

import argparse
from typing import Tuple

import numpy as np


def _normalise(vec: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm == 0:
        raise ValueError("normal vector cannot be zero-length")
    return vec / norm


def reflection_matrix(normal: np.ndarray, point: np.ndarray) -> np.ndarray:
    """
    Build a 4x4 homogeneous reflection matrix about a plane defined by
    (normal, point). Uses the form:
      R = I - 2 * n n^T
      t = (I - R) * p0
      M = [[R, t], [0, 0, 0, 1]]
    """
    n = _normalise(normal).reshape(3, 1)
    identity = np.eye(3)
    R = identity - 2.0 * (n @ n.T)
    t = (identity - R) @ point.reshape(3, 1)
    M = np.eye(4)
    M[:3, :3] = R
    M[:3, 3:4] = t
    return M


def right_handed_frame(normal: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Produce an orthonormal, right-handed basis on the mirror plane:
    - normal (N) is the plane normal.
    - tangent (T) is a reflected fallback axis projected into the plane.
    - bitangent (B) = N x T.
    If det < 0, flip T to restore a right-handed basis.
    """
    n = _normalise(normal)
    # Choose a fallback not parallel to n.
    fallback = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(fallback, n)) > 0.9:
        fallback = np.array([0.0, 1.0, 0.0])
    t = fallback - np.dot(fallback, n) * n
    t = _normalise(t)
    b = np.cross(n, t)
    b = _normalise(b)
    if np.dot(np.cross(t, b), n) < 0.0:
        t = -t
        b = np.cross(n, t)
    return t, b, n


def mirrored_axes_frame(normal: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Reflect the canonical world axes across the plane and then flip one in-plane
    axis (Y) if needed to restore a right-handed basis. Returns the adjusted
    X', Y', Z' axes suitable for treating the mirrored clone as right-handed.
    """
    n = _normalise(normal)
    R = reflection_matrix(n, np.zeros(3))[:3, :3]
    x_reflected = R @ np.array([1.0, 0.0, 0.0])
    y_reflected = R @ np.array([0.0, 1.0, 0.0])
    z_reflected = R @ np.array([0.0, 0.0, 1.0])
    det = np.linalg.det(np.stack([x_reflected, y_reflected, z_reflected], axis=1))
    if det < 0:
        y_reflected = -y_reflected
    return x_reflected, y_reflected, z_reflected


def parse_vector(raw: str) -> np.ndarray:
    parts = [p.strip() for p in raw.replace(",", " ").split() if p.strip()]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("vector must have 3 components")
    try:
        return np.array([float(p) for p in parts], dtype=float)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid vector '{raw}': {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prototype mirror transform helper.")
    parser.add_argument(
        "--normal",
        required=True,
        type=parse_vector,
        help="Plane normal as 'nx,ny,nz' (e.g., '1,0,0' for the YZ plane, '1,-1,0' for x=y).",
    )
    parser.add_argument(
        "--point",
        default="0,0,0",
        type=parse_vector,
        help="A point on the plane as 'x,y,z' (default origin).",
    )
    args = parser.parse_args()

    M = reflection_matrix(args.normal, args.point)
    t, b, n = right_handed_frame(args.normal)
    mx, my, mz = mirrored_axes_frame(args.normal)

    np.set_printoptions(precision=4, suppress=True)
    print("Reflection matrix (4x4 homogeneous):")
    print(M)
    print()
    print("Right-handed local frame on the plane:")
    print(f"  tangent   (T): {t}")
    print(f"  bitangent (B): {b}")
    print(f"  normal    (N): {n}")
    print()
    print("Mirrored world axes adjusted to right-handed (X', Y', Z'):")
    print(f"  X': {mx}")
    print(f"  Y': {my}")
    print(f"  Z': {mz}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
