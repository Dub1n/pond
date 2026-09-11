#!/usr/bin/env python3
"""Conservative Pack C ring-member and corner-joint comparison screen.

Units are N and mm. Results locate likely governing behaviours; they do not
constitute product-specific connection design or fabrication approval.
"""

from dataclasses import dataclass
from math import pi


E_LONG = 17_000.0
G_TORSION = 3_000.0
SIDE = 2_100.0
OUTER = 38.0
PLATE_SEPARATION = 44.0  # centroids of 6 mm plates around 38 mm tube
CURRENT_SIDE_HORIZONTAL = 600.0 * 100.0 / 319.5


@dataclass(frozen=True)
class Tube:
    wall: float

    @property
    def inner(self):
        return OUTER - 2 * self.wall

    @property
    def area(self):
        return OUTER**2 - self.inner**2

    @property
    def inertia(self):
        return (OUTER**4 - self.inner**4) / 12

    @property
    def torsion_constant(self):
        # Bredt thin-wall closed-section approximation at wall midline.
        middle = OUTER - self.wall
        return 4 * middle**4 / (4 * middle / self.wall)

    def centre_torque_rotation(self, torque, active_corners=2):
        length = SIDE / 2 if active_corners == 1 else SIDE / 4
        return torque * length / (G_TORSION * self.torsion_constant)

    def torsion_shear(self, torque):
        middle = OUTER - self.wall
        return torque / (2 * middle**2 * self.wall)

    def point_load(self, load, span):
        moment = load * span / 4
        stress = moment * (OUTER / 2) / self.inertia
        movement = load * span**3 / (48 * E_LONG * self.inertia)
        return moment, stress, movement

    def transverse_side(self, total_load, fixed):
        line_load = total_load / SIDE
        if fixed:
            moment = total_load * SIDE / 12
            movement = line_load * SIDE**4 / (384 * E_LONG * self.inertia)
        else:
            moment = total_load * SIDE / 8
            movement = 5 * line_load * SIDE**4 / (384 * E_LONG * self.inertia)
        stress = moment * (OUTER / 2) / self.inertia
        return moment, stress, movement

    def semirigid_transverse(self, total_load, corner_stiffness):
        """Symmetric beam with equal end rotational springs, N mm/rad."""
        line_load = total_load / SIDE
        fixed_moment = total_load * SIDE / 12
        # Equal end springs under symmetric transverse load rotate in opposite
        # global directions; slope-deflection gives 2EI/L at each end.
        member_stiffness = 2 * E_LONG * self.inertia / SIDE
        end_moment = fixed_moment * corner_stiffness / (
            corner_stiffness + member_stiffness
        )
        movement = (
            5 * line_load * SIDE**4 / (384 * E_LONG * self.inertia)
            - end_moment * SIDE**2 / (8 * E_LONG * self.inertia)
        )
        return end_moment, movement


@dataclass(frozen=True)
class Gusset:
    name: str
    thickness: float
    bolt_pitch: float
    outline: str
    hole_diameter: float = 6.5

    def roll_couple(self, torque):
        separation = OUTER + self.thickness
        plate_force = torque / separation
        # Conservative: one bolt carries the plate force in transverse bearing.
        bearing = plate_force / (self.hole_diameter * self.thickness)
        return separation, plate_force, bearing

    def in_plane_couple(self, moment):
        force = moment / self.bolt_pitch
        bearing = force / (self.hole_diameter * self.thickness)
        return force, bearing


def main():
    tubes = [Tube(3.2), Tube(5.0)]
    torques = [5_000.0, 20_000.0, 30_000.0]
    print("RING MEMBER")
    for tube in tubes:
        print(f"38x38x{tube.wall:g}: A={tube.area:.0f} mm2 "
              f"I={tube.inertia:.0f} mm4 J~{tube.torsion_constant:.0f} mm4")
        for torque in torques:
            two = tube.centre_torque_rotation(torque, 2) * 180 / pi
            one = tube.centre_torque_rotation(torque, 1) * 180 / pi
            shear_two = tube.torsion_shear(torque / 2)
            shear_one = tube.torsion_shear(torque)
            print(f"  M={torque / 1000:.0f} Nm: rotation two corners={two:.2f} deg, "
                  f"one corner={one:.2f} deg; shear={shear_two:.2f}/{shear_one:.2f} MPa")
        for load, span in ((100.0, 420.0), (200.0, 840.0), (300.0, 840.0)):
            _, stress, movement = tube.point_load(load, span)
            print(f"  P={load:.0f} N L={span:.0f}: bend={stress:.2f} MPa, "
                  f"deflection={movement:.2f} mm")
        for fixed in (False, True):
            moment, stress, movement = tube.transverse_side(CURRENT_SIDE_HORIZONTAL, fixed)
            print(f"  0.188 kN current outward side, {'fixed' if fixed else 'pinned'} ends: "
                  f"M={moment / 1000:.1f} Nm, bend={stress:.1f} MPa, "
                  f"deflection={movement:.1f} mm")
        if tube.wall == 5.0:
            for stiffness_nm in (100, 500, 1_000, 5_000, 20_000):
                moment, movement = tube.semirigid_transverse(
                    CURRENT_SIDE_HORIZONTAL, stiffness_nm * 1000
                )
                print(f"    corner K={stiffness_nm:>5} Nm/rad: "
                      f"end M={moment / 1000:.1f} Nm, deflection={movement:.1f} mm")

    stop_tube = Tube(5.0)
    stop_hole = 8.0
    removed_area = 2 * stop_tube.wall * stop_hole
    removed_vertical_i = 2 * stop_tube.wall * stop_hole**3 / 12
    wall_centre = (OUTER - stop_tube.wall) / 2
    removed_horizontal_i = 2 * (
        stop_tube.wall * stop_hole * wall_centre**2
        + stop_hole * stop_tube.wall**3 / 12
    )
    print("\nFALLBACK ONE TRANSVERSE 8 MM STOP-BUSH STATION")
    print(f"  gross area loss={removed_area:.0f} mm2 "
          f"({100 * removed_area / stop_tube.area:.1f}%)")
    print(f"  local gross-I loss: vertical bending="
          f"{100 * removed_vertical_i / stop_tube.inertia:.2f}%; "
          f"horizontal bending={100 * removed_horizontal_i / stop_tube.inertia:.1f}%")
    print("  closed-wall torsional shear path is interrupted; bush not credited as closure")

    gussets = [
        Gusset("existing L170 arm50 t6, bolts 60/120", 6.0, 60.0, "L"),
        Gusset("square170 t6, same bolts", 6.0, 60.0, "square"),
        Gusset("extended radiused L220 arm70 t8, bolts 55/195", 8.0, 140.0, "L"),
        Gusset("triangular-web220 t8, bolts 55/125/195", 8.0, 140.0, "triangle"),
        Gusset("selected triangular-web220 arm80 t12, M8 bolts 55/125/195",
               12.0, 140.0, "triangle", 8.5),
        Gusset("square220 t8, bolts 55/125/195", 8.0, 140.0, "square"),
    ]
    print("\nCORNER FORCE SCREENS")
    for gusset in gussets:
        print(gusset.name)
        for torque in (15_000.0, 30_000.0):
            sep, force, bearing = gusset.roll_couple(torque)
            print(f"  roll {torque / 1000:.0f} Nm: plate separation={sep:.0f} mm, "
                  f"couple force={force:.0f} N, one-bolt bearing={bearing:.1f} MPa")
        for moment in (45_000.0, 60_000.0):
            force, bearing = gusset.in_plane_couple(moment)
            print(f"  plan moment {moment / 1000:.0f} Nm: bolt-row force={force:.0f} N, "
                  f"one-bolt bearing={bearing:.1f} MPa")

    side_k = 2 * E_LONG * Tube(5.0).inertia / SIDE
    print("\nCORNER STIFFNESS TARGET")
    print(f"  side rotational scale 2EI/L={side_k / 1e6:.2f} kNm/rad")
    for fraction in (0.90, 0.95):
        required = fraction / (1 - fraction) * side_k
        print(f"  K for {fraction:.0%} fixed-end moment={required / 1e6:.1f} kNm/rad")
    strip_i = 8.0 * 70.0**3 / 12
    strip_k = 3 * 3_000.0 * strip_i / 220.0
    print(f"  low-modulus 220x70x8 strip={strip_k / 1e6:.1f} kNm/rad; "
          f"paired paths={2 * strip_k / 1e6:.1f} kNm/rad")
    selected_i = 12.0 * 80.0**3 / 12
    selected_k = 3 * 3_000.0 * selected_i / 220.0
    print(f"  selected low-modulus 220x80x12 strip="
          f"{selected_k / 1e6:.1f} kNm/rad; paired paths="
          f"{2 * selected_k / 1e6:.1f} kNm/rad before connection compliance")

    selected = gussets[-2]
    _, roll_force, _ = selected.roll_couple(30_000.0)
    plan_force, _ = selected.in_plane_couple(60_000.0)
    combined = (roll_force**2 + plan_force**2) ** 0.5
    print(f"  selected conservative vector force={combined:.0f} N; "
          f"plate bearing={combined / (selected.hole_diameter * selected.thickness):.1f} MPa; "
          f"two-wall tube bearing={combined / (selected.hole_diameter * 10):.1f} MPa")

    print("\nNON-PROJECTING DIAGONAL-JOIST SIDE EYE")
    backset = 55.0
    side_offset = 41.5
    # C2 runs from the outer inner-beam corner to the opening tip. The lower
    # rail corner lies 141.4 mm pondward of that tip; the eye base is 55 mm
    # behind the tip in the opposite, outward direction.
    plan_diagonal = (2 * 100.0**2) ** 0.5 + backset
    plan_offset = (plan_diagonal**2 + side_offset**2) ** 0.5
    vertical_drop = 296.5
    length = (plan_offset**2 + vertical_drop**2) ** 0.5
    proof = 300.0
    proof_vertical = proof * vertical_drop / length
    proof_horizontal = proof * plan_offset / length
    print(f"  backset={backset:.1f} mm; side tangent offset={side_offset:.1f} mm; "
          f"cord length={length:.1f} mm")
    print(f"  0.30 kN line proof: V={proof_vertical:.0f} N; "
          f"plan resultant={proof_horizontal:.0f} N")

    print("\nCORD-DERIVED SIDE ENVELOPE")
    attachment_options = {
        "normalized 128 mm line": (128.0, 316.0),
        "tip underside": (100.0, 316.0),
        "tip side-face to rail-centreline": (100.0, 356.5),
        "selected top-centred rail eye": (100.0, 319.5),
    }
    for label, (radial, vertical_drop) in attachment_options.items():
        horizontal = 600.0 * radial / vertical_drop
        fixed_end_moment = horizontal * SIDE / 12
        _, _, pinned = tubes[1].transverse_side(horizontal, False)
        _, _, fixed = tubes[1].transverse_side(horizontal, True)
        print(f"  {label}: H={horizontal:.0f} N; fixed-end M="
              f"{fixed_end_moment / 1000:.1f} Nm; 5 mm movement="
              f"{fixed:.1f}/{pinned:.1f} mm fixed/pinned")

    print("\nLOWER-H LOCAL SCREEN")
    half_spacing = 110.0
    upper_y = -128.0
    upper_z = 316.0
    weight = 100.0
    torque = 5_000.0
    pond_v = weight / 2 + torque / (2 * half_spacing)
    bank_v = weight - pond_v
    values = []
    stiffness = 0.0
    for label, lower_y, total_v in (
        ("bank", -half_spacing, bank_v),
        ("pond", half_spacing, pond_v),
    ):
        delta_y = upper_y - lower_y
        length = (delta_y**2 + upper_z**2) ** 0.5
        nz = upper_z / length
        cord_k = 6_000.0 / length
        leg_tension = total_v / (2 * nz)
        stiffness += 2 * cord_k * (nz * half_spacing) ** 2
        values.append((label, total_v, leg_tension,
                       abs(total_v * delta_y / upper_z)))
    print(f"  reactions: pond={pond_v:.1f} N, bank={bank_v:.1f} N")
    for label, vertical, tension, horizontal in values:
        print(f"  {label}: pair V={vertical:.1f} N, leg T={tension:.1f} N, "
              f"pair horizontal={horizontal:.1f} N")
    rotation = torque / stiffness
    bank = values[0]
    bank_length = ((upper_y + half_spacing)**2 + upper_z**2) ** 0.5
    bank_nz = upper_z / bank_length
    bank_k = 6_000.0 / bank_length
    unload = bank[2] / (bank_k * bank_nz * half_spacing)
    print(f"  ideal stiffness={stiffness / 1000:.0f} Nm/rad; "
          f"rotation={rotation * 180 / pi:.2f} deg; "
          f"bank leg unload={unload * 180 / pi:.2f} deg")
    print(f"  +/-1.5 mm free-length effect at bank leg="
          f"+/-{bank_k * 1.5:.1f} N")


if __name__ == "__main__":
    main()
