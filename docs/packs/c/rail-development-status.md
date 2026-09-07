# Pack C rail development — current state and next work

This is the active handoff for the Pack C submerged planting carrier as at
7 September 2026. Read it before developing another rail geometry or YAML model.

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

## Active verification requirements

The full-rank ideal screen narrows the problem; it does not accept the current
system. The next work must establish:

- **Practical rigid-body stiffness.** Measure or model movement in both signs of
  horizontal translation, vertical translation, roll, pitch and yaw. Include
  cord elasticity, free-length tolerance, adjustment, lower-wrap movement and
  loss of positive tension.
- **Independent-side behaviour.** Establish how strongly each side depends on
  the corners and perpendicular sides to close its along-side movement, and how
  much corner or ring deformation occurs before that path engages.
- **Local spine rotation.** Identify a real transverse reaction couple for the
  5 N·m eccentric-seat screen. Do not treat plan-crossed cords on the same
  spine line as a torsion couple.
- **Ring and corner adequacy.** Check member bending and torsion, in-plane
  racking, corner slip, combined corner actions, laminate bearing, bolt-hole
  stress, plate bending, preload and wet creep.
- **Unequal sharing and faults.** Solve tensions for asymmetric basket loading,
  cord length and stiffness variation, a deliberately slack support, and each
  important support or stabiliser unavailable.
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

### Minimum mechanism study and physical check

The next stability study should record all upper and lower coordinates, cord
free lengths or measured load-extension curves, ring mass and centre of
gravity. For each candidate it should:

1. solve static equilibrium with every cord tension constrained to be
   non-negative and report the minimum positive-tension reserve;
2. calculate the six-degree-of-freedom constraint rank and singular values;
3. calculate material plus tension-dependent geometric stiffness and identify
   its soft modes;
4. repeat with unilateral active cords for both signs of translation, roll,
   pitch and yaw, asymmetric load and each cord unavailable; and
5. report cord, rail and deck reactions rather than stiffness alone.

Use a rigid scale square with adjustable elastic cords as an early physical
check. Measure initial tensions, apply small forces and moments in both signs of
all six degrees of freedom, and record displacement and which cords unload.
Repeat with asymmetric ballast and one deliberately slack cord. This test is a
screen for dead bands, poor sharing and support-loss mechanisms, not a strength
test of the final rail.

## Directions worth comparing

These are investigation directions rather than endorsed solutions:

- **Connected ring with torsion-stable suspension nodes.** Give selected nodes
  a defined transverse reaction pair or rigid rotational restraint.
- **Stronger connected ring and developed corners.** Compare viable rail sizes
  and wall thicknesses, and compare flat plated corners with more explicitly
  three-dimensional or triangulated joints under the same support envelope.
- **Single rail with short transverse suspension outriggers.** Widen the
  reaction line locally without adding a second continuous carrier rail.
- **Secondary stabilising rail.** Keep the selected R5.1 spine as the seat rail
  and add a continuous, side-length or local second chord to create a defined
  torsional couple.
- **Distributed gravity cords with selective crossed stabilisers.** Retain
  short near-corresponding cords for gravity, and use a few opposite-handed
  diagonals for along-side translation and yaw rather than reversing the full
  endpoint order.
- **Rigid or triangulated joist-to-rail hangers.** Provide explicit vertical,
  horizontal and rotational reactions. Check local joist torsion, concentrated
  loads, liner clearance and replacement after decking.
- **Corrected modular side carrier.** Revisit an independent side only if it
  gains an opposite-bank tie, rigid frame or another balanced horizontal
  reaction. Do not reuse R4's same-bank fork.
- **Short individual or paired-seat modules.** Put one or two R5.1 seats on a
  short rail with two separated support frames, trading global corners for more
  deck attachments.
- **Composite or shallow-truss carrier.** Retain the selected R5.1 rail as one
  chord and connect it to a deeper backbone rather than requiring the seat rail
  to perform every global function.
- **Combined suspension and seat-location fitting.** Allow selected rail
  supports to provide seat stops or restraint if reaction peaks, seat positions
  and independent removal remain acceptable.
- **Short upper extensions near the planting line.** Move hanger reactions
  closer to the 450 mm planting line to reduce inclination and horizontal pull,
  while checking cantilever and deck-edge geometry.
- **Whole-pond cross-frame reference.** A rigid `+` between opposite side
  midpoints could resist side separation and, with moment-capable perimeter
  joints, transfer mid-side roll to the opposite side. It is not diagonal
  triangulation, does not remove the need for external deck reactions and would
  obstruct the centre, so use it primarily as a benchmark for less intrusive
  restraint arrangements.

A hybrid may be best. Compare candidates under the same load cases, fault
conditions, access requirements and R5.1 envelope.

## Recommended order

1. **Screen rigid-body stability first.** Survey the upper and proposed lower
   attachment coordinates and measure cord behaviour. Treat the ring as rigid;
   solve non-negative tensions, constraint rank, soft modes and movements for
   the baseline, selective-cross and other suspension layouts. Repeat for both
   movement directions, asymmetric loading, likely slack and each unavailable
   stabilising cord. Reject a true mechanism before member sizing.
2. **Define adaptable interface envelopes.** For every viable suspension, draw
   free-body diagrams for centred and eccentric baskets, uneven side loading,
   handling and one unavailable support. Bound support locations, forces,
   moments and permitted movement; bound the ring mass, centre of gravity and
   minimum stiffness. Preserve placement ranges rather than fixing exact nodes
   prematurely.
3. **Develop ring and suspension alternatives in parallel.** Check rail sizes,
   torsion, bending, racking, corners, joints, handling and support-loss spans
   against the support envelope. Separately demonstrate six-degree-of-freedom
   stability against the bounded ring properties. Lay out four configurable
   R5.1 envelopes, supports, corners, tolerances, access and removal paths on a
   complete side.
4. **Recombine and converge.** Calculate compatible ring deformation, cord
   stretch, active and slack supports, load redistribution and deck reactions.
   Reject combinations that exceed either interface envelope. Compare structural
   clarity, peak reactions, movement, fault tolerance, fabrication, wet
   durability, inspection, replacement, liner risk and visual intrusion. Model
   only the shortlist; renders explain geometry but do not validate mechanics.
5. **Detail and disprove the preferred combination.** Select actual GRP, cord
   and connection products and complete the member, connection and deck checks.
   Adapt the R5.1 sleeves, bolt stations and bridges to the selected rail, then
   prototype a complete side under asymmetric gravity, 5 N·m seat torque,
   longitudinal handling, a loose or unavailable support, repeated removal,
   wet dwell and drain-down. Measure tension, rotation, deflection, slip and
   redistribution. Test the selected seat and side on the complete carrier
   before fabrication acceptance.

## Output expected from the next development agent

Produce a comparison document containing:

- dimensioned sketches and free-body diagrams for at least two credible rail
  or suspension alternatives;
- an explicit source for every horizontal and rotational reaction;
- symmetric, asymmetric and one-support-unavailable reactions;
- a complete-side layout using the provisional R5.1 envelopes;
- resulting deck attachment loads and access requirements;
- a ranked recommendation with clear rejection reasons;
- the measurements and product data still missing; and
- a prototype plan capable of disproving the preferred option.

The next design gate is a rail and suspension arrangement with complete static
equilibrium, explicit rotational restraint, feasible full-side geometry and
reactions that the as-built deck can safely accept. Do not move from a
convincing render directly to fabrication.
