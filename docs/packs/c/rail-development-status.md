# Pack C rail development — current state and next work

This is the active handoff for the Pack C submerged planting carrier as at
8 September 2026. Read it before developing another rail geometry or YAML model.

Nothing in this document is a fabrication approval.

## Current decision

- Freeze R5.1 as the selected basket-seat architecture. Its open H-shaped upper
  member, two compact lower bridges and four sleeved bolts arranged as two
  separated capture stations are retained. It is not yet a fabrication design.
- Do not freeze the rail size through the seat. Sleeve dimensions and spacing,
  transverse bolt-pair spacing and the separation of the two capture stations
  remain adjustable to the selected rail, basket bearing regions and checked
  plate geometry.
- Develop the rail and suspension next. Use a configurable seat load and
  clearance envelope while comparing carrier arrangements.
- Do not produce a detailed R5.1 YAML model yet. The basket bearing bands,
  plate product and thickness, sleeve dimensions and positions, bolt positions,
  removal path and selected rail size are unknown. Detailed geometry now would
  present assumptions as settled dimensions.
- Use R3 as the connected-ring reference rather than an accepted final rail.
- Keep R4 as a diagnostic study only. Its same-bank suspension is not a valid
  working arrangement.
- Judge R5.1 separately from shortcomings owned by the ring, suspension and
  deck. A successful seat test would still not validate the complete system.
- The comparative cord calculation in
  [rail-support-study.md](../../calcs/rail-support-study.md) now screens the
  proposed coordinates, crossed stabilisers and a split-seat bridle. It finds
  global cord equilibrium plausible at comparison loads, but confirms that
  centreline cord layouts do not directly restrain local spine roll. The later
  lower-H screen uses 220 mm-separated force lines but finds basket-route and
  slack-leg problems, so it remains a fallback hybrid rather than R5.2.
- Retain 38 x 38 x 5 mm as the ring baseline. Gross vertical and torsional
  strength is plausible at comparison loads, but in-plane breathing governs.
  Use the proposed pond-facing joist-end force line to reduce the 0.60 kN
  side's outward action from about 0.243 to 0.168 kN. Develop the 8 mm
  triangular-web corner toward at least 20 kN m/rad after bedding, with the
  radiused L as its comparison; neither is selected until connection slip and
  stiffness are established.

## Read in this order

- [R5.1.md](R5.1.md) defines the selected seat architecture and its local tests.
- [design-C.md](design-C.md) defines the as-built deck interface and the
  still-unapproved load envelope.
- [R3-review.md](R3-review.md) and [R3-rail.md](R3-rail.md) describe the
  connected single-spine reference.
- [R4-double-rail.md](R4-double-rail.md) records the invalid same-bank study.
- [R5_v1-review.md](R5_v1-review.md) and [R5-plates.md](R5-plates.md) record the
  full-plate predecessor, calculations and illustrated geometry conflict.
- [plants.md](plants.md) defines basket count and planting levels.
- [The rail diagram guide](../../../diagrams/specs/rail/README.md) covers the
  existing conceptual models. None of those models depicts R5.1.
- [The comparative support calculation](../../calcs/rail-support-study.md)
  records the proposed attachment coordinates, assumptions, cord-only layouts,
  preliminary upper-attachment reactions and limitations. Flexible-ring corner
  actions and the approved deck envelope remain outstanding.
- [The ring and corner calculation](../../calcs/ring-corner-study.md) screens
  rail bending, torsion, outward ring breathing, the existing corner and larger
  gussets. It retains the proposed lower-H suspension as a hybrid investigation
  rather than promoting it to R5.2.

## Where the rail development now stands

The selected system-level baseline is:

- a 2,100 x 2,100 mm connected square ring;
- 38 x 38 x 5 mm structural-GRP SHS, with 3.2 mm no longer an equal default;
- one gravity support at each of the eight straight joists on every side;
- two opposite-handed crossed stabiliser pairs per side for along-side and yaw
  restraint; and
- R5.1 as the local basket-seat architecture, still dimensionally adaptable.

This baseline is **calculation-worthy, not fabrication-ready**. The rigid-body
cord system has feasible non-negative equilibrium in the screened load and
single-cord-loss cases. Gross rail bending, torsional shear and indicative
corner bearing stresses are also in a plausible range. The unresolved issue is
movement: inclined cords make each side bow outward, while corner clearance,
plate flexure and tube-wall bearing determine whether the square behaves closer
to a rigid frame or four nearly pinned sides.

### Loads and cord results already screened

The retained conservative inputs are a 1.80 kN complete-ring drain-down load,
0.60/0.45/0.30/0.45 kN uneven side loads, a 5 N m torque from one 100 N basket
at 50 mm eccentricity, a 20 N m four-basket same-direction torque case, a
deliberate 30 N m full-side torsion bound, 0.10 kN handling uplift, 10 N cord
seating tension and `+/-1.5 mm` effective free-length variation. The unidentified
6 mm polyester cord is represented by a conservative effective `EA=6 kN`.

With the proposed high joist-face coordinates below, the 32 gravity cords plus
16 crossed stabilisers retain rank 6 of 6. Under the stated rigid-ring cases:

- maximum intact cord tension is about 0.066 kN;
- the worst maximum after any one cord is unavailable is about 0.074 kN;
- the 95th-percentile maximum with free-length variation is about 0.088 kN;
- the preliminary intact upper-attachment envelope is about 0.086 kN downward,
  0.041 kN horizontal and 0.095 kN resultant; and
- calculated rigid-body movement is about 3.1 mm in the uneven-plus-torque
  case and 3.4 mm at the 95th percentile of the free-length study.

These low forces mean cord breaking strength is not presently governing.
Termination capacity, adjustment, chafe, creep, lower-point migration and ring
flexibility remain more important. The reaction figures are unfactored
comparison values; the deck limits in `design-C.md` remain TBC.

### Proposed gravity-support coordinates

Use pond centre `X=Y=0`, water `Z=0`, rail centrelines `X/Y=+/-1050` and the
effective lower force line `Z=-244`. On the south side, the proposed upper
point is the centre of each joist's pond-facing end face:

```text
U_i = (X_Ji, -1150, +112.5)
L_i = (clamp(X_Ji, -1050, +1050), -1050, -244)
```

The joist coordinates J1--J8 are `-1226.500, -839.833, -419.917, -108.500,
+108.500, +419.917, +839.833, +1226.500`. Thus J1/J8 attach to the straight
rail ends at `X=+/-1050`; J2--J7 retain matching along-side coordinates.

For J2--J7 the lower-to-upper vector is `(0, -100, +356.5)`, length 370.26 mm.
Cord tension is about 1.039 times its vertical contribution and outward force
is 0.281 times it. A 0.60 kN side therefore receives approximately 0.168 kN
outward instead of the former normalized screen's 0.243 kN.

This is a force-line proposal, not an eye-plate detail. The attachment must be
through-fastened to suitable joist faces without relying on screws into end
grain, retain timber edge distances, clear the joist tip/deck edge and remain
inspectable and replaceable after decking. It is on the joist end face, not
above the joist, and remains 100 mm bankward of the rail.

### Proposed crossed-stabiliser coordinates

Keep the diagonal lower points on two separated straight-side stations rather
than concentrating routine stabiliser forces at a corner. On the south side:

```text
U2 (-839.833, -1150, +112.5) -> L3 (-419.917, -1050, -244)
U3 (-419.917, -1150, +112.5) -> L2 (-839.833, -1050, -244)

U6 (+419.917, -1150, +112.5) -> L7 (+839.833, -1050, -244)
U7 (+839.833, -1150, +112.5) -> L6 (+419.917, -1050, -244)
```

Each diagonal is about 559.84 mm long. Its tension is about 1.570 times its
vertical contribution; its along-side and radial force components are about
1.178 and 0.281 times the vertical component. The opposite hands cancel their
load in the adjusted symmetric condition and provide deliberate along-side
and yaw stiffness.

The J2--J3 cords cross near `(-629.875, -1100, -65.75)`; mirror this in the
J6--J7 bay. Separate or protect the cords at that crossing. It is not a
structural node. Each lower point needs a positively located eye or constrained
collar; two cords sharing a nominal coordinate cannot share one migrating wrap.

Attaching the diagonals at the ring corner is not preferred. A short J2-to-
corner route gives about 43% less calculated along-side stiffness than the
J2--J3 crossed cord, while a matching J3-to-corner route has tension about
2.05 times its vertical contribution. Both concentrate new action into the
joint already responsible for breathing and torsion. Use a corner stabiliser
only as a separately calculated alternative, not the baseline.

Generate the other sides from local along coordinate `a`, bankward distance
`r` and height `z`:

```text
South ( a, -r, z)   East  ( r,  a, z)
North (-a,  r, z)   West  (-r, -a, z)
```

### What the ring and corners must do

At the former cord angle, a 0.60 kN side created about 0.243 kN outward. The
38 x 38 x 5 mm side then calculated at 2.8 mm movement with perfectly fixed
corners and 14.1 mm with pinned corners. The proposed upper coordinate reduces
the outward action to 0.168 kN and those bounds to about 1.9 and 9.7 mm.

The gross 5 mm tube remains plausible:

- one 100 N load over 420 mm gives about 1.63 MPa bending and 0.07 mm movement;
- 300 N over an 840 mm support-loss span gives about 9.77 MPa and 1.78 mm;
- 5 N m torsion gives about 0.28 degrees with two effective corners;
- 20 N m gives about 1.12 degrees; and
- the 30 N m bound gives about 1.67 degrees, with approximately 1.38 MPa
  torsional shear when two corners share it.

Service movement, rather than gross tube strength, governs this screen. If one
corner alone transfers the 30 N m torque, the tube rotation bound doubles to
about 3.35 degrees.

The existing paired 170 x 170 x 6 mm L plates have plausible indicative
bearing stresses but unknown stiffness and slip. Approximately 0.5 mm relative
movement through their top/bottom load path corresponds to roughly 0.65 degrees
of roll dead band. They have not been shown inadequate, but they have not been
shown sufficiently rigid.

For the 5 mm side, `2EI/L` is about 1.98 kN m/rad. A corner must provide about
18 kN m/rad to attract 90% of the perfectly fixed end moment. Use **20 kN m/rad
after bedding** as the minimum near-fixed development target and approximately
38 kN m/rad for 95%. At 20 kN m/rad, the proposed 0.168 kN side action gives
about 2.65 mm movement, versus the 1.94 mm perfectly fixed bound.

### Developed 8 mm corner candidates

Compare paired top-and-bottom plates in three plan outlines:

1. **Preferred triangular plan web:** 220 mm reach, 70 mm rail-contact strips,
   8 mm thick, with continuous diagonal material filling the inner elbow.
2. **Radiused L:** the same reach, strips and thickness, but without the full
   diagonal web. This is simpler but its elbow may control flexibility.
3. **Square upper bound:** 220 x 220 x 8 mm. It supplies the largest diaphragm
   but adds unnecessary material, drag and sediment area.

The triangular web is a horizontal top/bottom plan plate, not a separate
vertical fin. A low-modulus strip estimate puts the paired radiused L at about
9--19 kN m/rad, close to but not securely above the 20 kN m/rad target. The
triangular web should raise the lower bound by preventing elbow flexure, but it
cannot be credited as near-fixed until actual laminate and connection stiffness
are modelled or measured.

Use provisional bolt centrelines at **55 and 195 mm** from the theoretical
corner on each leg, centred across the 70 mm strip. Their 140 mm separation is
the main stiffness improvement. An optional third bolt at **125 mm** improves
direct-shear sharing and redundancy if the profile supplier permits the holes;
because it is near the group centroid, it adds little rotational leverage.

At the 60 N m in-plane bound, the long outer pair gives about 0.429 kN per
outer bolt, approximately 8.2 MPa plate bearing and 6.6 MPa across both 5 mm
tube walls. At 30 N m roll, the 46 mm top/bottom couple gives about 0.652 kN,
approximately 12.5 MPa one-bolt plate bearing and 10 MPa across both tube walls.
These are unfactored screens, not resistances.

An M6 bolt in a nominal 6.5 mm hole has about 0.25 mm radial clearance, already
about 0.10 degrees across the 140 mm outer pair before reliable bearing.
Controlled close holes with suitable smooth sleeves/bushes, or a supplier-
approved bonded-and-bolted joint, may matter more than a third bolt. Do not
credit wet long-term preload friction.

### Local lower-H suspension and R5.2 decision

Extending the R5.1 lower bridges into an H with four outer cord eyes remains a
mechanically meaningful hybrid, but it is **not promoted to R5.2**. At
provisional transverse force lines `+/-110 mm`, a 100 N load plus 5 N m gives
about 72.7 N total pond-side and 27.3 N bank-side vertical reaction. The ideal
all-taut stiffness is about 691 N m/rad and 0.41 degrees, but the lightly loaded
legs begin unloading around 0.38 degrees and `+/-1.5 mm` free-length variation
is enough to change a leg by about 28 N.

A direct pond-side-eye cord to the bankward joist line crosses the assumed
basket volume near `Z=-98 mm`. Routing around the basket adds longitudinal
force and needs a complete thirteen-seat layout. A missing-leg three-dimensional
equilibrium is also unresolved. Keep this as a fallback hybrid until routing,
fault behaviour and lower-H plate/eye capacity are demonstrated.

## Separation of responsibilities

The load path runs from the basket and planting assembly, through the R5.1
seat, into the carrier rail, through its suspension or hangers, and finally
into the deck frame and foundations.

- The basket owns sound bearing and retention features, soaked mass, plant
  depth, media retention and fish containment.
- R5.1 owns basket support and removal; local pitch, yaw, uplift and
  longitudinal restraint; and local GRP, bolt, sleeve and clearance behaviour.
- The carrier rail owns bending, torsion, side stability, racking, corners,
  joints, flooding and drainage.
- The suspension or hangers own rail position, reaction directions, load
  sharing, rotational restraint, failure tolerance, inspection and replacement.
- The deck and foundations own the capacity of joists, connections, beams,
  bracing, slabs and ground for the complete reaction envelope.

These boundaries do not prevent a later combined component. If a hanger also
acts as a seat stop, redraw the load path and assess that combined connection.

## Provisional R5.1 interface for rail studies

Reserve space and reactions for one open H-shaped upper member with two
transverse basket-bearing arms. It is captured at two stations along the rail.
Each station has one sleeved bolt on each side and a compact lower bridge. The
sleeves set a clearance fit and prevent tightening from crushing the hollow
rail. The proposal does not drill the main rail for each seat.

This is a functional interface rather than a fixed 38 mm envelope. Retain the
two separated capture stations and one sleeved bolt on each side of the rail at
each station. Adapt sleeve length and transverse spacing to the chosen rail
height and width, and adapt the along-rail station spacing to the bearing
regions and checked hole geometry. Rail-size alternatives are therefore valid
R5.1 studies; each alternative must issue its corresponding seat hole pattern,
bridge dimensions, clearances and local capacity checks.

The seat also needs a removable, reliable longitudinal stop and a mechanical
basket retainer that does not rely on planting media, weak mesh or four
permanent cord ties. Those details are unresolved.

For early clash studies, use a configurable 300 mm along-rail by 280 mm
transverse envelope. This conservative rectangle is not the plate outline.
Keep its height, bolt spacing and rail clearance adjustable. Keep support
fittings, corners and the basket removal path outside the envelope. Each seat
must remain independently removable.

Until measured soaked masses are available, retain the existing 100 N basket
and 50 mm transverse eccentricity as a comparison screen. That applies 5 N·m
to the carrier. A rigid local screen gives reactions of about 182 N at one top
rail edge and 82 N at the opposite underside. Add seat self-weight separately.
Uplift, handling, lateral and fault-case loads remain TBC.

## What R5.1 appears to improve

Against R3's independently bound crossbars, R5.1 offers repeatable bearing
geometry, positive transverse and yaw restraint, mechanical uplift capture and
fewer submerged knots. Its fasteners pass through solid plate and controlled
sleeves rather than requiring keeper-cheek connections to small hollow
crossbars.

Against R5's paired full square plates, the open form removes material outside
the necessary bearing and connection paths. It should reduce permanent weight,
sediment shelves, drag and obstruction to water exchange. The compact lower
bridges can provide underside reactions without a second basket-sized plate.

These are credible improvements, not established capacities. Removing plate
area makes fibre direction, arm bending and stress at the internal H corners
more important.

## R5.1 concerns to resolve later

- Measure the actual B23 and B28 basket bases, reinforced bearing bands,
  taper, sound retention features and removal travel.
- Select the structural-GRP product, thickness and fibre orientation. Check arm
  bending, connection regions, creep and generously radiused internal corners.
- Set hole and plate-edge distances, washers, sleeve wall and a tightening
  procedure that cannot crush or delaminate the plate.
- Fit clearances to samples of the purchased rail, including tolerance,
  resin-sealed surfaces, grit, roots and biological growth.
- Design and test the missing longitudinal stop and basket uplift retention.
- Quantify seat mass, drainage, drag and sediment behaviour.
- Prove access to every fastener and independent basket removal.

These are real seat risks. They do not currently justify a return to the full
square plates, and nominal dimensions cannot resolve them credibly.

## Superseded branches and retained lessons

- Do not revive R4's independent same-bank cord fork. All its horizontal cord
  components pull toward the same bank, so it lacks an opposing external
  reaction. A corrected independent side needs an opposed tie, rigid hanger or
  another complete reaction system.
- Do not revive R5's basket-sized paired plates. R5.1 replaces them because
  their added mass, sediment area and obstruction did not address ring or
  suspension behaviour.
- Retain the R5 layout warning: the illustrated 296 mm seat occupied almost all
  of the 311.4 mm J3-to-J4 bay and conflicted with the omitted support collars.
  Prove a complete four-seat side layout with the actual R5.1 envelope before
  fixing support positions.

## Two coupled development problems

For development, separate the carrier into two questions:

1. **Internal rail or ring adequacy.** Hold the specified suspension attachment
   coordinates against rigid-body movement, but apply only the force and moment
   reactions that the proposed suspension can actually provide. Do not invent a
   rotational clamp at a cord wrap. Check spine bending and torsion, in-plane
   racking, corners and joints, local attachment forces, support-loss spans and
   handling.
2. **Suspended-assembly stability.** Initially idealise the rail or ring as a
   rigid body. Check vertical and horizontal translation, roll, pitch and yaw;
   identify which taut support produces each reaction; and test changes of
   active support as cords stretch or go slack.

This separation is useful for finding mechanisms and allocating failure modes,
but the final designs are not independent. The suspension layout determines
the forces and moments applied to the ring. Ring and corner deformation changes
cord lengths, tensions and load sharing. A stability modification can therefore
increase rail torsion, racking or deck reactions, while a more flexible ring can
remove the restraint predicted by a rigid-body model.

Use interface envelopes to preserve design freedom: develop the ring for a
bounded set of support forces, moments, positions and permitted movements, and
develop the suspension for a bounded ring mass, centre of gravity, stiffness
and attachment movement. Iterate if either candidate exceeds the other's
envelope, then verify the selected pair as one coupled system.

### Initial rigid-ring screen of the R3 cord layout

The idealised 32-cord R3 arrangement is **not a first-order rigid-body
mechanism** under its ideal assumptions. For each cord, the first-order length
change used in the screen was:

```text
delta_length = n dot v + (r cross n) dot omega
```

Here `n` is the unit vector from the lower attachment to the fixed upper
attachment, `r` is the lower attachment position from the ring centre, `v` is
ring translation and `omega` is ring rotation. One row per cord forms a 32 by
6 constraint matrix. The rotation columns were divided by the 1,050 mm ring
half-width, so one unit of scaled rotation represents 1 mm movement at that
radius and the reported singular values are comparable with translations.

The screen used the documented approximate 128 mm radial offset, 316 mm
vertical drop, eight stated upper positions on each side, corresponding lower
positions limited to the 2,100 mm rail, and mirrored geometry on all four
sides:

| Cord endpoint arrangement | Matrix rank | Singular values, largest to smallest | Largest / smallest |
| --- | ---: | --- | ---: |
| Near-corresponding R3 | **6 of 6** | 5.1027, 4.5892, 4.5892, 1.0205, 0.6585, 0.6585 | 7.75 |
| Fully reversed on every side | **6 of 6** | 5.2635, 3.5899, 3.5899, 2.5072, 1.8381, 1.8381 | 2.86 |

The numerical values depend on the stated normalization and approximate
coordinates; they are not physical stiffnesses or capacities. Rank 6 is the
important initial result. The outward slopes provide opposing horizontal
reactions; vertical components acting at separated points restrain vertical
translation, roll and pitch; and the distributed positions along each side
give first-order yaw sensitivity.

An isolated straight side with near-corresponding cords still has a first-order
movement along its own length. In the ideal complete square, the perpendicular
sides and rigid corners close that mode. The full-rank result therefore depends
on the ring retaining its square geometry and is not evidence that an
individual side or flexible-corner assembly is independently stable.

That result is a kinematic screen, not proof of acceptable stability. Real
cords stretch, have unequal adjusted lengths and carry tension only. A cord
that unloads contributes no restraint. Lower wraps and their collars may move,
and a rail can rotate within a flexible wrap, so the real attachment may not
act as the fixed point used in the ideal model. The practical system may
therefore have a soft mode, a dead band or a fault-case mechanism even though
the perfect all-taut model has no infinitesimal mechanism.

Reversing every lower endpoint along a side would add strong along-side cord
components and improve the matrix conditioning, especially for yaw. It is not
a proportionate baseline. With the approximate 316 mm vertical drop and 128 mm
radial offset, near-corresponding cords have total tension about 1.08 times
their vertical contribution, or about 1.21 at the two end offsets. The fully
reversed cords range from about 217 to 2,277 mm along the side and from about
1.28 to 7.28 times their vertical contribution. The outer cords would impose
large horizontal reactions and create long crossing, chafe and adjustment
problems.

Selective opposite-handed crossed pairs are worth investigating. Retain the
near-corresponding cords for distributed gravity support and add or reassign a
small number of diagonals over one or a few joist bays to provide deliberate
along-side and yaw restraint. Use both diagonal directions, establish positive
tension reserve, prevent rubbing at crossings and repeat the check with either
member slack or unavailable. At the same radial and vertical offsets, a 311 mm
along-side diagonal has total tension about 1.46 times its vertical contribution
and a 420 mm diagonal about 1.77 times, before solving the actual distribution.
This is more proportionate than full reversal but still increases horizontal
rail and deck reactions.

Such diagonals primarily address rigid-body along-side translation and yaw.
Because their lower attachments remain on the single spine line, they do not
by themselves provide the local transverse reaction couple that resists twist
of that spine under an eccentric seat. Two geometrically crossing cords also
need deliberate separation or chafe protection; contact at their apparent
crossing is not a structural node.

## Remaining verification requirements

The rigid-ring model has now covered cord elasticity, free-length variation,
asymmetric loading and every individual cord unavailable. It narrows the
problem but does not accept the physical system. The remaining work is:

- **Semi-rigid ring behaviour.** Calculate movement with the developed corner
  moment-rotation curves, including clearance dead band. Establish how the
  sides and perpendicular members share breathing, roll and yaw actions.
- **Corner adequacy.** Check combined in-plane moment, roll, shear and bolt
  actions for the triangular-web and radiused-L variants. Resolve laminate
  direction, plate flexure, tube-wall bearing, hole stress, preload and wet
  creep.
- **Fault coupling.** Repeat the cord cases with one ineffective corner and
  with the ring flexible. The existing cord-loss result assumes a rigid ring.
- **Deck reaction envelope.** Issue vertical, both horizontal and moment
  reactions at every attachment, including adjacent-support and side totals,
  for checking the complete as-built deck-to-ground path.
- **Geometry and service.** Fit four adjustable R5.1 envelopes, all supports,
  corners and removal routes on a complete side. Keep every permanent upper
  termination inspectable and replaceable after decking.
- **Products and wet details.** Select actual GRP and cord properties, connection
  guidance and permanent-immersion basis; provide intentional venting, drainage,
  sealed cut faces and fish-safe details.

The ring and suspension can be developed in separate workstreams only through
explicit interface envelopes. They must then be recombined because a stability
change can invalidate the ring design:

- crossed cords add along-side force, ring compression or tension and corner
  demand;
- pretension adds permanent ring and deck actions;
- rigid hangers and torsion-stable nodes attract concentrated forces and
  moments;
- moving supports can increase spans or conflict with seats;
- a stiffer ring changes cord load sharing and may increase a peak reaction;
- a flexible rail or slipping corner invalidates rigid-ring attachment
  coordinates.

Conversely, some candidates deliberately solve both problems. Moment-capable
corners allow the square to share reactions globally; a secondary rail or
outrigger can stiffen the carrier and create a suspension reaction couple; a
rigid triangulated hanger locates the ring while changing its internal loads;
and a whole-pond cross-frame would brace the ring while transferring reactions
to opposite sides. Do not exclude these hybrids merely because the analysis is
split into two parts.

Increasing the main rail size or wall thickness belongs principally to the
internal-ring work. It may improve torsional stiffness, handling strength and
support-loss spans, but it cannot create a missing external reaction. Increasing
corner-plate thickness or area may improve plate bending, edge distances and
bolt-group leverage only when the revised geometry changes the actual load
path; bolt slip, tube-wall bearing or the lack of a three-dimensional torsion
connection may govern instead. Size members and corners after defining the
reactions they must transmit.

### Completed mechanism screen and later physical check

The calculation study now records proposed upper/lower force lines, a
conservative cord axial stiffness, non-negative compatible tensions, six-
degree-of-freedom rank, small-movement stiffness, uneven loading, free-length
variation and each cord individually unavailable. It also reports preliminary
upper reactions. This completes the rigid-ring screening stage.

It does not complete the coupled flexible-ring problem. The next model must
replace perfect corners with the semi-rigid properties described below and
then report ring deformation, corner actions and the complete deck reaction
envelope. Actual ring mass, basket centres of gravity and selected cord
load-extension curves remain later substitutions for the conservative inputs.

Use a rigid scale square with adjustable elastic cords as an early physical
check. Measure initial tensions, apply small forces and moments in both signs of
all six degrees of freedom, and record displacement and which cords unload.
Repeat with asymmetric ballast and one deliberately slack cord. This test is a
screen for dead bands, poor sharing and support-loss mechanisms, not a strength
test of the final rail.

## Directions worth comparing

The active comparison is now deliberately narrow:

- **Baseline:** 38 x 38 x 5 mm connected ring, high pond-facing joist
  attachments, distributed gravity cords, J2--J3/J6--J7 crossed stabilisers,
  to-be-developed semi-rigid corners and R5.1 seats.
- **Corner A:** paired 220 x 8 mm triangular plan-web gussets with 70 mm contact
  strips and long outer bolt pairs; preferred geometry candidate, not yet
  demonstrated to meet the stiffness target.
- **Corner B:** paired radiused L gussets with the same reach, thickness and
  bolts; simpler comparison whose inner elbow may govern.
- **Corner C:** paired 220 mm square plates only as the diaphragm upper bound.
- **Fallback hybrid:** lower-H seat suspension, considered only if corner/ring
  movement remains unacceptable and its cord-routing problem can be solved.

Do not reopen R4 same-bank suspension, full R5 plates, a second continuous rail
or intrusive pond cross-frame unless this narrowed programme disproves the
connected-ring route.

## Recommended order

The rigid-body mechanism and initial reaction screens are complete. Continue
from the semi-rigid ring/corner gate:

1. **Resolve the upper termination.** Draw a through-fastened A4/316 eye or
   cheek fitting whose force line is near the pond-facing joist end-face centre
   `Z=+112.5`. Check timber edge distances, inclined force components, cord
   bend/chafe, deck-board clearance and replacement access. If the point moves,
   rerun both calculation scripts.
2. **Develop two corner specimens analytically.** Use paired 220 x 8 mm top and
   bottom plates with 70 mm rail-contact strips: the triangular plan web and
   radiused L. Use outer bolt stations 55/195 mm and compare the optional centre
   bolt at 125 mm. Obtain selected plate/profile properties and connection
   guidance; model laminate direction, plate flexure, tube-wall bearing, bolt
   clearance and any sleeve/bush or structural adhesive contribution.
3. **Demonstrate near-fixed behaviour.** Produce moment-rotation curves over
   0--60 N m in-plane and 0--30 N m roll. Require at least 20 kN m/rad in-plane
   secant stiffness after bedding, record clearance dead band separately, and
   reject any option whose movement, permanent set or wet-creep allowance makes
   the side response unacceptable. Strength without stiffness is insufficient.
4. **Recombine the ring and cords.** Replace rigid corners with the calculated
   semi-rigid properties and use the proposed gravity/diagonal coordinates.
   Repeat uneven load, four same-direction eccentric baskets, one ineffective
   corner, each important cord unavailable and free-length variation. Report
   ring breathing, spine roll, corner actions and every deck reaction.
5. **Complete the layout gate.** Place all thirteen R5.1 envelopes, 32 gravity
   supports, 16 crossed stabilisers, corner plates and access/removal routes.
   Prove the crossed-cord intersections and lower locators do not conflict with
   seats or servicing.
6. **Retain the lower-H hybrid only as fallback.** Do not issue R5.2 unless a
   complete cord route clears the basket and a nonlinear missing-leg analysis
   defines how its fault action returns to the ring.
7. **Prototype only after those calculations.** The eventual physical programme
   must measure corner bedding, stiffness, permanent set, cord redistribution,
   wet dwell and removal, but no build is authorized by this handoff.

## Output expected from the next development agent

The next calculation/design package must contain:

- dimensioned triangular-web and radiused-L corner drawings;
- a dimensioned joist termination and complete gravity/diagonal coordinate
  schedule;
- an explicit source for every horizontal and rotational reaction;
- semi-rigid corner moment-rotation curves and combined ring movements;
- symmetric, asymmetric, one-corner and one-support-unavailable reactions;
- a complete-side layout using the provisional R5.1 envelopes;
- resulting deck attachment loads and access requirements;
- a selected corner or a clear decision that supplementary roll restraint is
  required;
- the measurements and product data still missing; and
- a prototype plan capable of disproving the preferred option.

The next design gate is a ring that remains acceptably square and level using
demonstrated semi-rigid corner properties, with complete static equilibrium,
feasible full-side geometry and reactions that the as-built deck can safely
accept. Do not move from a convincing render or gross-strength screen directly
to fabrication.
