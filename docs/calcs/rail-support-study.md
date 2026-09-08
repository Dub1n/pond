# Pack C ring support study — comparative cord layouts

This is a conservative calculation screen using the existing Option C and R3
geometry. It locates likely problems and compares support principles. It is not
a fabrication approval, a deck-capacity check, or a substitute for measured
cord, basket, connection and GRP properties.

The reproducible calculation is in `rail_support_study.py` beside this note.

## Result in brief

The existing connected ring is not an ideal rigid-body mechanism. Adding two
opposite-handed crossed cord pairs per side improves its calculated global
conditioning and produces feasible non-negative equilibrium for the cases
screened. The largest calculated individual cord tension remains below 0.10 kN
in the conservative elastic and free-length sensitivity screens.

That does **not** resolve the important local problem. Crossed cords whose
lower resultants remain on the spine centreline cannot directly resist the
5 N m torque from an eccentric R5.1 seat. The torque must travel through spine
torsion and the corners until it finds restraints elsewhere.

A second cord-only layout could provide a local couple without another rail:
use two independent support legs at provisional points on the R5.1 seat concept,
with transverse force lines approximately 160 mm apart. Those points are new,
unresolved combined seat/suspension geometry; the active R5.1 design does not
yet dimension or validate them. Two cords meeting one lower point, or a freely
migrating wrap around the 38 mm spine, do not provide this couple.

## 1. Coordinate basis and proposed points

All coordinates are millimetres. The origin is the pond centre; water and pad
tops are `Z=0`. The 2,100 mm ring centreline is at `X/Y=+/-1050`; its effective
support line is taken at `Z=-244`. Joist undersides are at `Z=+75`.

For the south side, positive `X` runs along the rail and positive `Y` points
pondward. The joist stations from J1 to J8 are:

| Joist | Along-side coordinate |
| --- | ---: |
| J1 | -1226.500 |
| J2 | -839.833 |
| J3 | -419.917 |
| J4 | -108.500 |
| J5 | +108.500 |
| J6 | +419.917 |
| J7 | +839.833 |
| J8 | +1226.500 |

The proposed upper point is the centre of the joist's pond-facing end face:

```text
U_i = (X_Ji, -1150, +112.5)
```

This is 100 mm bankward of the rail and at the mid-depth of the 47 x 75 mm
joist. It is not above the joist. It replaces the YAML's internally schematic
wrap geometry for this study because it reduces unnecessary outward ring force.
A through-fastened A4 eye or cheek termination must avoid end-grain screw
withdrawal, retain timber edge distances and remain accessible after decking.

The baseline lower point is:

```text
L_i = (clamp(X_Ji, -1050, +1050), -1050, -244)
```

The J1 and J8 points are limited to the ends of the straight rail. Rotate this
south-side rule by 90, 180 and 270 degrees for the other three sides.

The proposed crossed stabilisers are additional cords in both directions over
the J2--J3 and J6--J7 bays on every side:

```text
U2 -> L3 and U3 -> L2
U6 -> L7 and U7 -> L6
```

Those bays are preferred to the narrower central bays because their roughly
420 mm along-side spacing is less likely to be consumed by a 300 mm R5.1 clash
envelope. Route the two hands separately so their apparent crossing is not a
contact node.

For the split-seat comparison, four conservative provisional seats per side
are centred at along-side coordinates `-750, -250, +250, +750`. Each receives
two provisional lower force lines within its 280 mm transverse clash envelope:

```text
L_bank = (seat centre, -1130, -244)
L_pond = (seat centre,  -970, -244)
```

Both legs run to the nearest accessible joist attachment. These centres are a
calculation grid, not the final 13-basket schedule. A full layout must move them
to suit the measured basket bearing regions, support hardware and removal path.

## 2. Assumptions and method

The screen uses 6 mm low-stretch braided polyester with a specified minimum
breaking load of at least 6 kN. In the absence of a selected product, the base
model uses an effective wet, knotted and bedded axial rigidity `EA=6 kN`. This
corresponds to 10% extension at 10% of the stated breaking load and is
deliberately more compliant than typical identified low-stretch polyester.
`EA=15 kN` is a reasonable upper comparison value; elastic movements would be
approximately 40% of the reported base values while geometry and equilibrium
would be unchanged.

Other retained assumptions are:

- 10 N seating tension in every cord, solely to remove slack;
- 1.80 kN complete-ring drain-down load, bounding four 0.45 kN sides;
- uneven side loads of 0.60, 0.45, 0.30 and 0.45 kN;
- 5 N m local seat-torque comparison;
- 0.10 kN local handling uplift applied with the uneven gravity case;
- `+/-1.5 mm` random effective free-length error for adjustment, bedding and
  short-term settlement, over 250 reproducible trials;
- cords carry tension only; compression is prohibited;
- the ring is rigid for the six-degree-of-freedom equilibrium calculation;
- beneficial tension-dependent geometric stiffness is omitted.

For cord unit vector `n`, lower point `r`, translation `v` and rotation `omega`,
the compatibility row is:

```text
delta = n dot v + (r cross n) dot omega
```

The calculation solves the minimum-energy compatible axial-spring response
with an active set:
any cord demanding negative tension is removed and equilibrium is resolved. It
also finds the minimum-energy non-negative tension distribution and repeats the
torque case with every cord individually unavailable. Moments are scaled by the
1,050 mm ring half-width for rank and conditioning comparisons.

This is a linear, small-movement model. It does not include ring bending,
corner slip, wrap migration, R5.1 arm flexure, deck flexibility, long-term
creep or hydrodynamic loads. Those omissions generally make the physical
system softer and less evenly shared.

## 3. Results

### Layout A — gravity cords plus crossed stabilisers

Layout A has 32 baseline gravity cords and 16 crossed stabilisers.

| Quantity | Result |
| --- | ---: |
| Constraint rank | 6 of 6 |
| Largest/smallest singular value | 2.66 |
| Symmetric drain-down movement | 2.70 mm |
| Uneven-load movement / rigid-body rotation | 3.06 mm / 0.060 deg |
| Uneven plus 5 N m movement / rotation | 3.07 mm / 0.061 deg |
| Maximum cord tension in stated intact cases | 66.0 N |
| Worst maximum with any one cord unavailable | 73.8 N |
| Maximum upper-point downward / horizontal reaction | 85.1 / 40.9 N |
| 95th-percentile tension with free-length error | 87.8 N |
| 95th-percentile movement with free-length error | 3.40 mm |
| Minimum active cords in sensitivity runs | 47 of 48 |

All single-cord-unavailable equilibrium cases were feasible in the ideal rigid
model. The low forces show that cord tensile strength is not the likely issue.
Adjustment, seating, chafe, attachment capacity and how ring/corner flexibility
redistributes those forces remain more important.

The calculated whole-ring response to a 5 N m moment is not evidence of local
spine-roll control. Layout A sends that moment through the spine and corners;
it supplies no direct transverse couple at the loaded seat.

### Layout B — crossed stabilisers plus split R5.1 seat bridles

Layout B retains Layout A and adds two independent legs at each conservative
provisional seat, using provisional points within the R5.1 transverse envelope
rather than adding a second rail. Whether the selected plate geometry can
provide those points without additional material remains to be established.

| Quantity | Result |
| --- | ---: |
| Constraint rank | 6 of 6 |
| Largest/smallest singular value | 2.94 |
| Symmetric drain-down movement | 1.21 mm |
| Uneven-load movement / rigid-body rotation | 1.51 mm / 0.035 deg |
| Uneven plus 5 N m movement / rotation | 1.52 mm / 0.036 deg |
| Maximum cord tension in stated intact cases | 39.5 N |
| Worst maximum with any one cord unavailable | 42.3 N |
| Maximum upper-point downward / horizontal reaction | 110.9 / 42.4 N |
| 95th-percentile tension with free-length error | 61.8 N |
| 95th-percentile movement with free-length error | 1.83 mm |
| Minimum active cords in sensitivity runs | 77 of 80 |

The lower individual cord forces arise from adding many parallel load paths;
they should not be used to downsize connections. Several legs share a joist
attachment, so the attachment envelope is higher than Layout A.

The whole-ring 5 N m result applies a global moment at the south-side centre;
it does not prove that a particular seat bridle attracts a local seat torque.
The following separate two-leg calculation is the controlling local screen.

For a local load `W` and torque `M` shared by force lines separated by `d`:

```text
V_plus  = W / 2 + M / d
V_minus = W / 2 - M / d
```

With `W=100 N`, `M=5,000 N mm` and `d=160 mm`, the two vertical reactions are
81.25 N and 18.75 N. Both remain positive. A separation below 100 mm requires
a negative reaction and therefore cannot work with tension-only cords; at least
125 mm is preferable to retain a 10 N reserve in the lightly loaded leg.

Using the conservative `EA=6 kN`, a fixed `+/-80 mm` split pair has an ideal
local rotational stiffness of about 169 N m/rad. The 5 N m screen corresponds
to about 1.7 degrees if one node acts, or 0.8 degrees if two nodes genuinely
share it. With only 10 N initial seating tension, one leg begins to unload at
about 0.6 degrees. At that point the response becomes one-sided and nonlinear.
The result is in the right ballpark for further development, but it is not yet
a robust two-way torsional restraint.

One split leg unavailable leaves no local couple at that seat. The global ring
may still find equilibrium, but only by transferring torque through the spine
and corners as Layout A does.

## 4. Reaction envelope and decision

The calculation-level upper attachment envelopes are:

| Layout | Downward | Horizontal resultant | Total resultant |
| --- | ---: | ---: | ---: |
| A: crossed stabilisers | 0.086 kN | 0.041 kN | 0.095 kN |
| B: split-seat bridles | 0.111 kN | 0.043 kN | 0.119 kN |

These are characteristic comparison reactions from the listed intact assumed
loads,
not approved limits. They exclude load factors, long-term effects, eye-plate
eccentricity, attachment-group interaction and the deck's ordinary loads. The
five deck limits in `design-C.md` must remain TBC until the joist-to-ground and
connection checks are completed.

For a conservative preliminary adjacent-attachment screen, twice the maximum
listed point reaction gives 0.171 kN downward for Layout A and 0.222 kN for
Layout B. The assumed maximum side gravity input is 0.600 kN. These are useful
loads to carry into the deck calculation, not approved capacities.

The rigid-body model cannot uniquely divide force and moment between the two
corners of a flexible side. It therefore does not issue a corner-action
envelope. That is a positive finding about the remaining problem: corner
forces require a beam/torsion model of the chosen rail and corner stiffness,
using the cord forces produced here. Treating the square as perfectly rigid
would conceal rather than calculate those actions.

The study locates two different issues:

1. **Global positioning is plausible.** Layout A gives full rank, tolerable
   comparison movements and non-negative equilibrium even after any single
   cord is removed. Crossed stabilisers are therefore worth retaining as the
   low-material baseline for translation and yaw.
2. **Local roll remains the decision point.** A stabilising cord returning to
   the spine centreline cannot solve it. Layout B can create the required
   couple without another rail only through new attachment points on the
   eventual R5.1 arms at least 125 mm apart, preferably about 160 mm for this
   screen. Its low-tension leg and seat-arm load path then govern.

Layout B should proceed only as a combined seat/suspension candidate. Before
detailing it, check whether the R5.1 arms can accept the two cord attachment
forces without obstructing basket bearing, removal, bolt stations or the
longitudinal stop. If they cannot, the present single-spine architecture has no
credible cord-only local torsion solution; it would then need a structural
lever arm such as an outrigger, torsion-capable hanger or secondary rail.

Neither layout provides net downward restraint against an uplift exceeding the
assembly's concurrent gravity load. Hanging cords pull upward only. Basket
retention and temporary handling therefore remain separate load paths.

## Reproduction

Run:

```bash
./.venv/bin/python docs/calcs/rail_support_study.py
```

The script uses only NumPy and SciPy already present in `requirements.txt`.
