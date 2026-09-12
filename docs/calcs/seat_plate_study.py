#!/usr/bin/env python3
"""R5.1 plate-thickness comparison screen (N, mm, MPa).

This is a deliberately simple local screen, not an orthotropic plate or
connection approval. It makes the conservative geometry and load basis visible
while the actual basket and wet laminate data are still unknown.
"""

E_LOW = 8_000.0
ARM_WIDTH = 50.0
RAIL_HALF_WIDTH = 19.0
MAX_BASKET_WIDTH = 280.0
SCREEN_LOAD = 300.0
BRIDGE_SPAN = 56.0
TARGET_MOVEMENT = 2.0


def cantilever_uniform(load, length, breadth, thickness):
    """One half of one bearing arm, uniformly loaded outboard of the rail."""
    half_load = load / 4.0
    line_load = half_load / length
    inertia = breadth * thickness**3 / 12.0
    moment = half_load * length / 2.0
    stress = moment * (thickness / 2.0) / inertia
    movement = line_load * length**4 / (8.0 * E_LOW * inertia)
    return stress, movement


def bridge_point(load, span, breadth, thickness):
    """One lower bridge, conservatively a central point load between M8 axes."""
    inertia = breadth * thickness**3 / 12.0
    moment = load * span / 4.0
    stress = moment * (thickness / 2.0) / inertia
    movement = load * span**3 / (48.0 * E_LOW * inertia)
    return stress, movement


def main():
    overhang = MAX_BASKET_WIDTH / 2.0 - RAIL_HALF_WIDTH
    print("R5.1 PLATE THICKNESS SCREEN")
    print("Assumptions: 0.30 kN drained/localized basket screen, 280 mm basket "
          "width, two 50 mm arms, E=8 GPa low-direction screening modulus.")
    print(f"Arm outboard cantilever={overhang:.0f} mm; target initial movement "
          f"<={TARGET_MOVEMENT:.0f} mm")
    print("t (mm) | upper-arm stress / movement | lower bridge stress / movement")
    for thickness in (5.0, 6.0, 8.0, 10.0, 12.0):
        arm_stress, arm_move = cantilever_uniform(
            SCREEN_LOAD, overhang, ARM_WIDTH, thickness
        )
        bridge_stress, bridge_move = bridge_point(
            SCREEN_LOAD, BRIDGE_SPAN, ARM_WIDTH, thickness
        )
        print(f"{thickness:>6.0f} | {arm_stress:>6.1f} MPa / {arm_move:>5.2f} mm"
              f" | {bridge_stress:>6.1f} MPa / {bridge_move:>5.2f} mm")
    print("The bridge screen puts the full 0.30 kN on one bridge; normal gravity "
          "does not load it. Actual wet properties, basket band width, holes, "
          "slots, washer/sleeve bearing and creep remain release checks.")


if __name__ == "__main__":
    main()
