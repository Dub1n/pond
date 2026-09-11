# Pack C ring support study — selected cord layout

This is the reproducible calculation record behind [cords.md](../packs/c/cords.md).
It selects the cord force lines and screens rigid-body equilibrium; it does not
approve the flexible ring, corners, attachments or deck.

Run the arithmetic with:

```bash
./.venv/bin/python docs/calcs/rail_support_study.py
```

## Selected layout

Use 44 independent cords:

- 24 straight gravity cords at J2--J7, six per side;
- 4 inclined corner gravity cords from side-mounted eyes wholly behind the
  ends of the existing C2 diagonal joists; and
- 16 crossed stabilisers, two opposite-handed pairs in the J2--J3 and J6--J7
  bays of every side.

This replaces the former 48-cord layout. Its eight J1/J8 cords converged at the
ring corners from straight joist tips. Four C2 cords now put one direct support
at each corner without cantilevering hardware beyond a joist. Do not install
J1/J8 as additional cords.

All coordinates are millimetres. The origin is the pond centre; the minimum
water and pad datum is `Z=0`. The 2,100 mm ring centreline is at
`X/Y=+/-1050`. Straight lower eyes are centred on the top rail faces; their
nominal shackle tangent is at local `r=1050, Z=-207`.

For the south side, with positive `a` eastwards:

```text
straight upper U(a) = (a, -1150, +112.5)
straight lower L(a) = (a, -1050, -207)
a at J2--J7 = -839.833, -419.917, -108.500,
              +108.500, +419.917, +839.833

crossed pairs = U2 -> L3, U3 -> L2, U6 -> L7, U7 -> L6
```

The four corner cords use these side-eye tangents and lower corner tangents:

```text
C1 U=(-1159.546,-1218.236,+112.5) -> L=(-1050,-1050,-184)
C2 U=(+1159.546,-1218.236,+112.5) -> L=(+1050,-1050,-184)
C3 U=(+1159.546,+1218.236,+112.5) -> L=(+1050,+1050,-184)
C4 U=(-1159.546,+1218.236,+112.5) -> L=(-1050,+1050,-184)
```

Each eye-base centre is 55 mm back from the timber tip along its diagonal. Its
effective Wichard-ring tangent is 41.5 mm beyond the selected side face from
the joist centreline. Southern corners use the south-facing side and northern
corners the north-facing side; this cancels a common yaw bias. [corner.md](../packs/c/corner.md)
defines the side-mounted assembly. Rotate the straight/crossed rule using:

```text
South ( a, -r, z)   East  ( r,  a, z)
North (-a,  r, z)   West  (-r, -a, z)
```

For J2--J7, the lower-to-upper vector is `(0,-100,+319.5)`, length
334.78 mm. Each crossed cord is 537.04 mm. Crossed cords meet geometrically
near local `(a,r,z)=(+/-629.875,1100,-47.25)`; separate them physically because
the crossing is not a structural node. Each corner cord is 358.07 mm. The full
named map is in `cords.md`.

## Assumptions and method

The base screen uses:

- 6 mm low-stretch braided polyester;
- conservative effective wet/bedded axial rigidity `EA=6 kN`;
- 10 N seating tension in every cord;
- 1.80 kN complete-ring drain-down load;
- uneven side loads of 0.60, 0.45, 0.30 and 0.45 kN;
- 5 N m local torque with the uneven case;
- 0.10 kN local handling uplift;
- `+/-1.5 mm` random effective free-length error over 250 seeded trials;
- tension-only cords and small movement; and
- an ideal rigid ring for the six-degree-of-freedom equilibrium calculation.

For cord unit vector `n`, lower point `r`, translation `v` and rotation
`omega`, the compatibility row is:

```text
delta = n dot v + (r cross n) dot omega
```

An active-set solution removes a cord that demands negative tension and
resolves equilibrium. The script also finds the minimum-energy non-negative
tension distribution, removes every cord in turn and repeats the free-length
study. Moments are scaled by the 1,050 mm ring half-width for rank and
conditioning comparisons.

The model omits ring bending, corner slip, eye offsets, joist flexibility,
connection settlement, creep, chafe and hydrodynamic effects. These omissions
generally make the real assembly softer and may redistribute reactions.

## Results

| Quantity | Selected 44-cord layout |
| --- | ---: |
| Constraint rank | 6 of 6 |
| Largest/smallest singular value | 2.54 |
| Symmetric drain-down movement | 2.88 mm |
| Uneven plus 5 N m movement / rotation | 3.20 mm / 0.066 deg |
| Maximum cord in stated intact cases | 75.8 N |
| Worst maximum with any one cord unavailable | 84.6 N |
| Free-length 95th-percentile maximum cord | 99.5 N |
| Free-length 95th-percentile movement / rotation | 3.42 mm / 0.083 deg |
| Screened upper downward / horizontal / resultant | 91.7 / 45.9 / 102.5 N |
| Minimum active cords in sensitivity runs | 43 of 44 |

All 44 single-cord-unavailable cases found feasible equilibrium in this ideal
screen. That establishes a credible positioning system; it does not prove that
all failures are harmless. Cord and fitting strength are not governing at these
forces. Adjustment, termination slip, lower-eye position, ring flexibility and
the joist-to-ground reaction path remain the important gates.

At a 0.60 kN side load the straight-cord geometry produces approximately
0.188 kN outward action (`H/V=100/319.5=0.313`). The former normalized geometry
gave 0.243 kN; retain it as the coordinate/offset sensitivity. Crossed cords give
along-side and yaw restraint but no local transverse couple at a seat. R5.1
seat torque therefore passes into the 38 x 38 x 5 mm spine and the corner
system in [ring-corner-study.md](ring-corner-study.md).

The reaction figures are unfactored calculation values. Carry at least the
0.103 kN point resultant, the 0.188 kN heavy-side outward action and the
0.60 kN heavy-side gravity input into the complete deck assessment. The
0.30 kN support proof in `cords.md` tests a connection; it is not an approved
deck reaction.

## Alternatives retained only as sensitivities

The script retains two comparisons so geometry changes can be detected:

- former 32 straight gravity plus 16 crossed cords;
- an idealised C2 timber-tip centreline layout; and
- the rejected 141.4 mm projected vertical-corner layout.

The ideal tip model confirms that an inclined cord is stable, but a physical
side-mounted eye needs timber end distance and a cord-clearance offset. The
projected comparison violates the no-cantilever constraint. Neither is an
installation option. The earlier lower-H split-seat bridle remains a historical analytical
branch: it obstructed the basket route, had lightly loaded legs sensitive to
free length and did not improve on the selected direct corner support plus
stiff joint.
