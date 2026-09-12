#!/usr/bin/env python3
"""Provisional rigid-ring screen for the Pack C direct-loop suspension.

The wrap coordinates are deliberately provisional until measured on the real
joists, cord, chafe sleeves and deck-board template. Dimensions are mm, forces
are N and moments are N mm. This is not a connection or fabrication check.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


HALF_RING = 1050.0
RAIL_Z = -244.0
RAIL_WRAP_Z = -263.0
CORNER_POST_Z = -203.0
UPPER_WRAP_Z = 75.0  # descending legs leave near the joist underside
STRAIGHT_WRAP_RADIAL = 1185.0  # provisional 35 mm back from the joist tip
C2_WRAP_BACKSET = 35.0  # provisional distance along the diagonal from its tip
CORNER_POST_OFFSET = 55.0
JOIST_STATIONS = np.array(
    [-1226.5, -839.833333, -419.916667, -108.5,
     108.5, 419.916667, 839.833333, 1226.5]
)
EA_LOOP = 6000.0  # conservative effective rigidity assigned to one cord item
PRETENSION_ITEM = 10.0
MOMENT_SCALE = HALF_RING


@dataclass(frozen=True)
class CordLeg:
    name: str
    item: str
    upper: np.ndarray
    lower: np.ndarray
    family: str
    ea: float = EA_LOOP
    pretension: float = PRETENSION_ITEM

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
        return self.ea / self.length


def side_point(side: int, along: float, radial: float, z: float) -> np.ndarray:
    """Rotate south-side coordinates about Z in 90-degree increments."""
    point = np.array([along, -radial, z], dtype=float)
    for _ in range(side):
        point = np.array([-point[1], point[0], point[2]])
    return point


def gravity_loops() -> list[CordLeg]:
    """Equivalent centreline legs for the 24 two-legged direct loops."""
    legs = []
    for side in range(4):
        for joist_index in range(1, 7):
            station = float(JOIST_STATIONS[joist_index])
            item = f"S{side + 1}-J{joist_index + 1}"
            legs.append(CordLeg(
                item, item,
                side_point(side, station, STRAIGHT_WRAP_RADIAL, UPPER_WRAP_Z),
                side_point(side, station, HALF_RING, RAIL_WRAP_Z),
                "gravity-loop",
            ))
    return legs


def crossed_loops() -> list[CordLeg]:
    """One equivalent opposite-handed pair over J2-J3 on each side."""
    legs = []
    for side in range(4):
        for upper_i, lower_i in ((1, 2), (2, 1)):
            item = f"S{side + 1}-X{upper_i + 1}to{lower_i + 1}"
            legs.append(CordLeg(
                item, item,
                side_point(
                    side, float(JOIST_STATIONS[upper_i]),
                    STRAIGHT_WRAP_RADIAL, UPPER_WRAP_Z,
                ),
                side_point(
                    side, float(JOIST_STATIONS[lower_i]),
                    HALF_RING, RAIL_WRAP_Z,
                ),
                "crossed-loop",
            ))
    return legs


def corner_sling_legs() -> list[CordLeg]:
    """Two lower legs belonging to each of four continuous C2 slings."""
    legs = []
    extra = C2_WRAP_BACKSET / np.sqrt(2.0)
    for index, (sx, sy) in enumerate(
        ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)), 1
    ):
        item = f"C{index}-C2-sling"
        upper = np.array([
            sx * (1150.0 + extra),
            sy * (1150.0 + extra),
            UPPER_WRAP_Z,
        ])
        lowers = (
            np.array([
                sx * (HALF_RING - CORNER_POST_OFFSET),
                sy * HALF_RING,
                CORNER_POST_Z,
            ]),
            np.array([
                sx * HALF_RING,
                sy * (HALF_RING - CORNER_POST_OFFSET),
                CORNER_POST_Z,
            ]),
        )
        for leg_index, lower in enumerate(lowers, 1):
            legs.append(CordLeg(
                f"{item}-L{leg_index}", item, upper, lower, "corner-sling",
                ea=EA_LOOP / 2.0,
                pretension=PRETENSION_ITEM / 2.0,
            ))
    return legs


def selected_layout() -> list[CordLeg]:
    return gravity_loops() + crossed_loops() + corner_sling_legs()


def generalized_load(points, moment=None):
    result = np.zeros(6)
    for position, force in points:
        result[:3] += force
        result[3:] += np.cross(position, force)
    if moment is not None:
        result[3:] += moment
    return result


def cases() -> dict[str, np.ndarray]:
    centre = np.array([0.0, 0.0, RAIL_Z])
    side_centres = [side_point(side, 0.0, HALF_RING, RAIL_Z)
                    for side in range(4)]
    uneven = (600.0, 450.0, 300.0, 450.0)
    return {
        "symmetric 1.80 kN drain-down": generalized_load(
            [(centre, np.array([0.0, 0.0, -1800.0]))]
        ),
        "uneven sides 0.60/0.45/0.30/0.45 kN": generalized_load([
            (side_centres[i], np.array([0.0, 0.0, -load]))
            for i, load in enumerate(uneven)
        ]),
        "uneven plus south-seat 5 N m torque": generalized_load(
            [(side_centres[i], np.array([0.0, 0.0, -load]))
             for i, load in enumerate(uneven)],
            moment=np.array([5000.0, 0.0, 0.0]),
        ),
        "uneven plus 0.10 kN handling uplift": generalized_load(
            [(side_centres[i], np.array([0.0, 0.0, -load]))
             for i, load in enumerate(uneven)]
            + [(side_point(0, -260.0, HALF_RING, RAIL_Z),
                np.array([0.0, 0.0, 100.0]))]
        ),
    }


def scaled_matrix(legs: list[CordLeg]) -> np.ndarray:
    matrix = np.vstack([leg.row for leg in legs])
    matrix[:, 3:] /= MOMENT_SCALE
    return matrix


def compatible_response(legs, external, unavailable_items=()):
    """Linear axial response with tension-only active-set iteration."""
    keep = [i for i, leg in enumerate(legs) if leg.item not in unavailable_items]
    demand = -external.copy()
    demand[3:] /= MOMENT_SCALE
    columns = np.column_stack([leg.row for leg in legs])
    columns[3:, :] /= MOMENT_SCALE
    active = keep.copy()
    for _ in range(len(legs) + 1):
        a = columns[:, active]
        stiffness = np.array([legs[i].stiffness for i in active])
        initial = np.array([legs[i].pretension for i in active])
        tangent = (a * stiffness) @ a.T
        if np.linalg.matrix_rank(tangent) < 6:
            return None
        movement = np.linalg.solve(tangent, demand - a @ initial)
        tension = initial + stiffness * (a.T @ movement)
        negative = np.where(tension < -1e-8)[0]
        if not len(negative):
            result = np.zeros(len(legs))
            result[active] = np.maximum(tension, 0.0)
            return result, movement, active
        del active[int(negative[np.argmin(tension[negative])])]
    return None


def attachment_envelope(legs, responses):
    records = []
    for tension in responses:
        grouped = {}
        for leg, value in zip(legs, tension):
            key = tuple(np.round(leg.upper, 3))
            grouped.setdefault(key, np.zeros(3))
            grouped[key] += value * leg.n
        records.extend(grouped.values())
    return (
        max(force[2] for force in records),
        max(np.linalg.norm(force[:2]) for force in records),
        max(np.linalg.norm(force) for force in records),
    )


def main():
    legs = selected_layout()
    items = sorted({leg.item for leg in legs})
    matrix = scaled_matrix(legs)
    singular = np.linalg.svd(matrix, compute_uv=False)

    print("PROVISIONAL DIRECT-LOOP SCREEN")
    print("Replace wrap coordinates with measured cord tangents before use.")
    print(f"cord items={len(items)} model legs={len(legs)} "
          f"rank={np.linalg.matrix_rank(matrix)}/6 "
          f"condition={singular[0] / singular[-1]:.2f}")
    print(f"straight upper radial={STRAIGHT_WRAP_RADIAL:.1f} mm; "
          f"C2 backset={C2_WRAP_BACKSET:.1f} mm")

    responses = []
    for name, load in cases().items():
        response = compatible_response(legs, load)
        if response is None:
            print(f"{name}: INFEASIBLE")
            continue
        tension, movement, active = response
        responses.append(tension)
        print(f"{name}: max leg={tension.max():.1f} N "
              f"move={np.linalg.norm(movement[:3]):.2f} mm "
              f"active legs={len(active)}")

    load = cases()["uneven plus south-seat 5 N m torque"]
    failures = []
    for item in items:
        response = compatible_response(legs, load, unavailable_items=(item,))
        failures.append((response is not None, item, response))
    feasible = [entry for entry in failures if entry[0]]
    print(f"one-item-unavailable: {len(feasible)}/{len(items)} feasible")
    if feasible:
        worst = max(feasible, key=lambda entry: np.max(entry[2][0]))
        print(f"worst remaining leg={np.max(worst[2][0]):.1f} N "
              f"when {worst[1]} is unavailable")

    down, horizontal, resultant = attachment_envelope(legs, responses)
    print(f"provisional upper envelope: down={down:.1f} N "
          f"horizontal={horizontal:.1f} N resultant={resultant:.1f} N")


if __name__ == "__main__":
    main()
