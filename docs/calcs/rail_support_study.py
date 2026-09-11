#!/usr/bin/env python3
"""Comparative rigid-ring and cord-support screen for Pack C.

This is deliberately a transparent, conservative comparison model.  It is not
a connection, timber, GRP, or fabrication design check.  Dimensions are mm and
forces are N; moments are N mm.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np


HALF_RING = 1050.0
RAIL_Z = -244.0
UPPER_Z = 112.5
UPPER_RADIAL = 1150.0
STRAIGHT_LOWER_RADIAL = 1050.0
STRAIGHT_LOWER_Z = -207.0
CORNER_LOWER_Z = -184.0
CORNER_JOIST_BACKSET = 55.0
CORNER_EYE_SIDE_OFFSET = 41.5
JOIST_STATIONS = np.array(
    [-1226.5, -839.833333, -419.916667, -108.5,
     108.5, 419.916667, 839.833333, 1226.5]
)
EA_CORD = 6000.0  # N: effective wet/knotted/bedded axial rigidity
PRETENSION = 10.0  # N: nominal seating tension, not structural prestress
MOMENT_SCALE = HALF_RING


@dataclass(frozen=True)
class Cord:
    name: str
    upper: np.ndarray
    lower: np.ndarray
    family: str

    @property
    def length(self) -> float:
        return float(np.linalg.norm(self.upper - self.lower))

    @property
    def n(self) -> np.ndarray:
        return (self.upper - self.lower) / self.length

    @property
    def row(self) -> np.ndarray:
        return np.r_[self.n, np.cross(self.lower, self.n)]

    @property
    def stiffness(self) -> float:
        return EA_CORD / self.length


def side_point(side: int, along: float, radial: float, z: float) -> np.ndarray:
    """Rotate south-side coordinates about Z in 90-degree increments."""
    point = np.array([along, -radial, z], dtype=float)
    for _ in range(side):
        point = np.array([-point[1], point[0], point[2]])
    return point


def baseline() -> list[Cord]:
    cords = []
    for side, station in product(range(4), JOIST_STATIONS):
        lower_along = float(np.clip(station, -HALF_RING, HALF_RING))
        cords.append(Cord(
            f"S{side + 1}-J{np.where(JOIST_STATIONS == station)[0][0] + 1}",
            side_point(side, station, UPPER_RADIAL, UPPER_Z),
            side_point(
                side, lower_along, STRAIGHT_LOWER_RADIAL,
                STRAIGHT_LOWER_Z
            ),
            "gravity",
        ))
    return cords


def middle_gravity() -> list[Cord]:
    """Six straight-joist gravity cords per side, omitting J1 and J8.

    The two former end cords that converged on each ring corner are replaced
    by one inclined cord from a non-projecting C2 diagonal-joist side eye.
    """
    return [
        cord for cord in baseline()
        if not (cord.name.endswith("J1") or cord.name.endswith("J8"))
    ]


def corner_gravity(mode: str = "side-face") -> list[Cord]:
    """One gravity cord at each ring corner from the diagonal C2 joist.

    The selected side-face eye is wholly behind the timber tip.  Its force
    tangent is 55 mm back along the joist and 41.5 mm outside the joist
    centreline.  South corners use the south-facing diagonal face and north
    corners the north-facing face so the four offsets do not impose a common
    yaw bias.  ``direct-tip`` retains the ideal centreline tip comparison and
    ``projected`` retains the rejected vertical-corner comparison.
    """
    cords = []
    for corner in range(4):
        lower = side_point(corner, -HALF_RING, HALF_RING, CORNER_LOWER_Z)
        if mode == "projected":
            upper = lower.copy()
            upper[2] = UPPER_Z
        elif mode == "direct-tip":
            upper = side_point(corner, -UPPER_RADIAL, UPPER_RADIAL, UPPER_Z)
        elif mode == "side-face":
            tip = side_point(
                corner, -UPPER_RADIAL, UPPER_RADIAL, UPPER_Z
            )
            radial = tip.copy()
            radial[2] = 0.0
            radial /= np.linalg.norm(radial)
            tangent = np.array([-radial[1], radial[0], 0.0])
            face_sign = (1.0, -1.0, 1.0, -1.0)[corner]
            upper = (
                tip + CORNER_JOIST_BACKSET * radial
                + face_sign * CORNER_EYE_SIDE_OFFSET * tangent
            )
        else:
            raise ValueError(f"unknown corner mode: {mode}")
        cords.append(Cord(
            f"C{corner + 1}-D",
            upper,
            lower,
            "corner-gravity",
        ))
    return cords


def crossed_stabilisers() -> list[Cord]:
    """Opposite-handed pairs over the J2-J3 and J6-J7 bays on every side."""
    cords = []
    for side in range(4):
        for a, b in ((1, 2), (5, 6)):
            for upper_i, lower_i in ((a, b), (b, a)):
                cords.append(Cord(
                    f"S{side + 1}-X{upper_i + 1}to{lower_i + 1}",
                    side_point(side, JOIST_STATIONS[upper_i], UPPER_RADIAL, UPPER_Z),
                    side_point(
                        side, JOIST_STATIONS[lower_i],
                        STRAIGHT_LOWER_RADIAL, STRAIGHT_LOWER_Z
                    ),
                    "crossed",
                ))
    return cords


def split_seat_bridles() -> list[Cord]:
    """Two independent cords to +/-80 mm points on each provisional seat.

    The points are provisional within the R5.1 transverse envelope, not fixed
    R5.1 geometry. This is a mathematical best case until the arms and
    attachments are defined and checked. A freely migrating wrap or two cords
    at one point gives no couple.
    Four seats per side deliberately bounds the actual 13-seat arrangement.
    """
    cords = []
    for side in range(4):
        for seat_no, along in enumerate((-750.0, -250.0, 250.0, 750.0), 1):
            upper_station = float(JOIST_STATIONS[np.argmin(abs(JOIST_STATIONS - along))])
            for transverse in (-80.0, 80.0):
                cords.append(Cord(
                    f"S{side + 1}-seat{seat_no}{'b' if transverse < 0 else 'p'}",
                    side_point(side, upper_station, UPPER_RADIAL, UPPER_Z),
                    side_point(side, along, HALF_RING + transverse, RAIL_Z),
                    "bridle",
                ))
    return cords


def generalized_load(points: list[tuple[np.ndarray, np.ndarray]], moment=None):
    result = np.zeros(6)
    for position, force in points:
        result[:3] += force
        result[3:] += np.cross(position, force)
    if moment is not None:
        result[3:] += moment
    return result


def cases() -> dict[str, np.ndarray]:
    centre = np.array([0.0, 0.0, RAIL_Z])
    side_centres = [side_point(side, 0.0, HALF_RING, RAIL_Z) for side in range(4)]
    return {
        "symmetric 1.80 kN drain-down": generalized_load(
            [(centre, np.array([0.0, 0.0, -1800.0]))]
        ),
        "uneven sides 0.60/0.45/0.30/0.45 kN": generalized_load([
            (side_centres[i], np.array([0.0, 0.0, -load]))
            for i, load in enumerate((600.0, 450.0, 300.0, 450.0))
        ]),
        "uneven plus south-seat 5 N m torque": generalized_load(
            [(side_centres[i], np.array([0.0, 0.0, -load]))
             for i, load in enumerate((600.0, 450.0, 300.0, 450.0))],
            moment=np.array([5000.0, 0.0, 0.0]),
        ),
        "uneven plus 0.10 kN handling uplift": generalized_load(
            [(side_centres[i], np.array([0.0, 0.0, -load]))
             for i, load in enumerate((600.0, 450.0, 300.0, 450.0))]
            + [(side_point(0, -260.0, HALF_RING, RAIL_Z),
                np.array([0.0, 0.0, 100.0]))]
        ),
    }


def scaled_matrix(cords: list[Cord]) -> np.ndarray:
    matrix = np.vstack([cord.row for cord in cords])
    matrix[:, 3:] /= MOMENT_SCALE
    return matrix


def compatible_response(cords: list[Cord], external: np.ndarray, pretension=None,
                        unavailable=()):
    """Linear axial-spring response with a tension-only active-set iteration."""
    keep = [i for i in range(len(cords)) if i not in unavailable]
    if pretension is None:
        pretension = np.full(len(cords), PRETENSION)
    demand = -external.copy()
    demand[3:] /= MOMENT_SCALE
    all_columns = np.column_stack([cord.row for cord in cords])
    all_columns[3:, :] /= MOMENT_SCALE
    active = keep.copy()
    for _ in range(len(cords) + 1):
        a = all_columns[:, active]
        k = np.array([cords[i].stiffness for i in active])
        t0 = pretension[active]
        tangent = (a * k) @ a.T
        if np.linalg.matrix_rank(tangent) < 6:
            return None
        q = np.linalg.solve(tangent, demand - a @ t0)
        tension = t0 + k * (a.T @ q)
        negative = np.where(tension < -1e-8)[0]
        if not len(negative):
            result = np.zeros(len(cords))
            result[active] = np.maximum(tension, 0.0)
            return result, q, active
        del active[int(negative[np.argmin(tension[negative])])]
    return None


def stiffness_modes(cords: list[Cord], tension: np.ndarray | None = None):
    rows = np.vstack([cord.row for cord in cords])
    scale = np.diag([1, 1, 1, 1 / MOMENT_SCALE, 1 / MOMENT_SCALE, 1 / MOMENT_SCALE])
    rows = rows @ np.linalg.inv(scale)
    axial = np.diag([cord.stiffness for cord in cords])
    matrix = rows.T @ axial @ rows
    values = np.linalg.eigvalsh(matrix)
    return np.sqrt(np.maximum(values, 0.0))


def local_roll_screen():
    # Best-case provisional split-seat pair, linearized about the rail axis.
    sample = split_seat_bridles()[:2]
    lever = 80.0
    k_theta = sum(c.stiffness * (c.n[2] * lever) ** 2 for c in sample)
    twist_one = 5000.0 / k_theta
    twist_two = 5000.0 / (2.0 * k_theta)
    unload_rotation = PRETENSION / (sample[0].stiffness * abs(sample[0].n[2]) * lever)
    return k_theta, twist_one, twist_two, unload_rotation


def attachment_envelope(cords, responses):
    records = []
    for tension in responses:
        grouped = {}
        for cord, value in zip(cords, tension):
            key = tuple(np.round(cord.upper, 3))
            grouped.setdefault(key, np.zeros(3))
            grouped[key] += value * cord.n  # equal magnitude; deck direction is opposite
        forces = list(grouped.values())
        records.extend(forces)
    return (
        max(force[2] for force in records),
        max(np.linalg.norm(force[:2]) for force in records),
        max(np.linalg.norm(force) for force in records),
    )


def main():
    layouts = {
        "A former 32 gravity plus 16 crossed cords": (
            baseline() + crossed_stabilisers()
        ),
        "C selected 24 middle gravity plus 4 C2 side-face plus 16 crossed": (
            middle_gravity() + corner_gravity() + crossed_stabilisers()
        ),
        "C idealized direct C2-tip corner cords": (
            middle_gravity() + corner_gravity("direct-tip")
            + crossed_stabilisers()
        ),
        "C rejected projected vertical corner cords": (
            middle_gravity() + corner_gravity("projected")
            + crossed_stabilisers()
        ),
        "B crossed cords plus split-seat bridles": (
            baseline() + crossed_stabilisers() + split_seat_bridles()
        ),
    }
    print("ASSUMPTIONS")
    print(f"EA_eff={EA_CORD:.0f} N; seating pretension={PRETENSION:.1f} N")
    print(f"ring centreline=+/-{HALF_RING:.0f} mm; lower Z={RAIL_Z:.0f} mm")
    print()
    for name, cords in layouts.items():
        matrix = scaled_matrix(cords)
        singular = np.linalg.svd(matrix, compute_uv=False)
        print(name)
        print(f"  cords={len(cords)} rank={np.linalg.matrix_rank(matrix)}/6 "
              f"condition={singular[0] / singular[-1]:.2f}")
        print("  singular=" + ", ".join(f"{value:.3f}" for value in singular))
        envelope_responses = []
        for case_name, load in cases().items():
            response = compatible_response(cords, load)
            if response is None:
                print(f"  {case_name}: INFEASIBLE tension-only compatible response")
                continue
            tensions, q, response_active = response
            envelope_responses.append(tensions)
            movement = (f"move={np.linalg.norm(q[:3]):.2f} mm "
                        f"rot={np.degrees(np.linalg.norm(q[3:]) / MOMENT_SCALE):.3f} deg "
                        f"active={len(response_active)}")
            print(f"  {case_name}: min={tensions.min():.1f} N "
                  f"max={tensions.max():.1f} N slack={(tensions < 0.1).sum()} "
                  f"{movement}")
        # Find the worst single unavailable cord under uneven + torque.
        load = cases()["uneven plus south-seat 5 N m torque"]
        failures = []
        for missing in range(len(cords)):
            response = compatible_response(cords, load, unavailable=(missing,))
            failures.append((response is not None,
                             np.max(response[0]) if response is not None else np.inf,
                             cords[missing].name))
        feasible = [entry for entry in failures if entry[0]]
        print(f"  one-cord-unavailable: {len(feasible)}/{len(cords)} equilibria feasible; "
              f"worst max={max(x[1] for x in feasible):.1f} N "
              f"when {max(feasible, key=lambda x: x[1])[2]} unavailable")
        vertical, horizontal, resultant = attachment_envelope(cords, envelope_responses)
        print(f"  upper-attachment envelope (listed cases): down={vertical:.1f} N, "
              f"horizontal={horizontal:.1f} N, resultant={resultant:.1f} N")
        # Conservative installation/bedding sensitivity: +/-1.5 mm effective
        # free-length error, fixed seed for reproducibility.  Positive error
        # means a longer/slacker cord.  No beneficial geometric stiffness.
        rng = np.random.default_rng(20260908)
        load = cases()["uneven plus south-seat 5 N m torque"]
        trials = []
        mechanisms = 0
        for _ in range(250):
            errors = rng.uniform(-1.5, 1.5, len(cords))
            initial = np.maximum(0.0, PRETENSION - np.array(
                [cord.stiffness for cord in cords]) * errors)
            response = compatible_response(cords, load, initial)
            if response is None:
                mechanisms += 1
                continue
            tension, q, response_active = response
            trials.append((tension.max(), np.linalg.norm(q[:3]),
                           np.degrees(np.linalg.norm(q[3:]) / MOMENT_SCALE),
                           len(response_active)))
        trial_array = np.array(trials)
        print(f"  +/-1.5 mm free-length sensitivity (250): mechanisms={mechanisms}; "
              f"max tension p95={np.percentile(trial_array[:, 0], 95):.1f} N; "
              f"movement p95={np.percentile(trial_array[:, 1], 95):.2f} mm; "
              f"rotation p95={np.percentile(trial_array[:, 2], 95):.3f} deg; "
              f"minimum active={int(trial_array[:, 3].min())}")
        print()
    k_theta, twist_one, twist_two, unload = local_roll_screen()
    print("LOCAL SPINE-ROLL SCREEN (best-case fixed split-seat contacts)")
    print(f"  rotational stiffness per paired node={k_theta / 1000:.2f} N m/rad")
    print(f"  twist under 5 N m: one node={np.degrees(twist_one):.1f} deg; "
          f"two nodes sharing={np.degrees(twist_two):.1f} deg")
    print(f"  first bridle cord unloads after about {np.degrees(unload):.1f} deg")


if __name__ == "__main__":
    main()
