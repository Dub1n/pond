# Pack C rail corner — construction specification

## Decision and limit of approval

Use the corner described here with the 38 x 38 x 5 mm structural-GRP ring,
the R5.1 seats and the suspension in [cords.md](cords.md). The joint has two
12 mm triangular plan-web plates, six close-fit M8 through-bolts and one
inclined gravity cord attached directly to the side of the existing C2
diagonal corner joist, wholly behind its end plane.

This is the issued **prototype construction detail**, not permission to load
the completed deck. It removes the previous 8 mm plate sizing uncertainty and
defines all joint dimensions. Fabrication of the four installed corners still
depends on the material certificate, one wet corner test and the deck checks
listed under [release gates](#release-gates). Those gates test connection slip
and wet behaviour which cannot be made certain by bolt-strength arithmetic.

## Why this arrangement is selected

- The former 220 x 70 x 8 mm paired-strip estimate was only about
  18.7 kN m/rad before bolt and bedding flexibility. It could not securely
  deliver the required 20 kN m/rad installed stiffness.
- Increasing the load-path strips to 80 mm and the plates to 12 mm gives a
  conservative paired-strip estimate of about **41.9 kN m/rad before
  connection compliance**. The complete tested joint must still achieve at
  least 20 kN m/rad after bedding.
- Three bolts per leg retain the useful 140 mm outer-bolt lever and add a
  middle load path if a fastener loosens. M8 is selected in place of the
  earlier M6 prototype so close holes, shanks, bushes and broad washers can be
  made more repeatably.
- One inclined cord at each corner replaces the two former end cords
  converging there. A side-mounted eye 55 mm behind the joist tip avoids any
  cantilever beyond the timber while leaving the cord clear of the joist end.
  Its horizontal action is included explicitly in the suspension and deck
  envelopes rather than hidden by a projected fitting.
- The full triangular web braces the two rail legs without the complete
  220 x 220 sediment shelf of a square plate.

## Joint geometry

### Coordinate convention and plate outline

Set local `x=0, y=0` at the intersection of the two 38 mm rail centrelines.
The two rail legs extend along local `+x` and `+y`. Dimensions below are
millimetres and apply to both top and bottom plates.

Cut each 12 mm plate to this five-sided outline:

```text
(-40,-40) -> (220,-40) -> (220,40) -> (40,220)
             -> (-40,220) -> close
```

This produces 80 mm-wide contact strips centred on both rails and a continuous
diagonal web between `(220,40)` and `(40,220)`. Round every external corner to
at least 12 mm radius. Do not cut drainage holes in the first test joint. If
the test shows a sediment trap, add only the hole pattern accepted in the wet
corner test; do not drill through the 80 mm rail strips, the diagonal load path
or any washer zone.

Cut four 45-degree mitred rail members to retain the 2,100 x 2,100 mm
centreline square. The nominal long-point length remains 2,138 mm, but set the
final saw stop from the surveyed square and one clamped trial corner.

### Bolt pattern

Drill six vertical bolt axes at:

```text
x leg: (55,0), (125,0), (195,0)
y leg: (0,55), (0,125), (0,195)
```

Use **8.2 mm jig-reamed holes** only if a measured sample of the selected M8
bolt shank passes freely without hammering. Otherwise use the smallest
repeatable free hole accepted by the plate/profile supplier, up to 8.5 mm,
and re-test clearance dead band. Do not open individual holes with a hand file
to make a misaligned stack fit.

Each M8 bolt passes, in order, through:

1. a 24 mm outside-diameter A4 broad washer;
2. the 12 mm top plate;
3. the 5 mm top wall of the rail;
4. a 28 mm nominal internal compression sleeve;
5. the 5 mm bottom rail wall;
6. the 12 mm bottom plate;
7. another 24 mm A4 broad washer; and
8. an A4 all-metal prevailing-torque nut.

The **sleeve length is the measured clear cavity**, not an assumed 28 mm.
Use an A4/316 sleeve at least 12 mm outside diameter with an 8.2–8.5 mm bore,
square ends and no burr. Insert and retain the sleeves while the mitred tube
ends remain open. They prevent tightening from crushing the hollow section;
they do not replace bolt bearing in the close holes.

Use M8 x 90 mm A4-80 partially threaded hex bolts at the 125 and 195 mm axes.
The two 55 mm axes use M8 x 100 after the eye bridge is fitted above. Check that
the smooth shank crosses every bearing plate and both tube walls and that the
nut obtains full thread engagement. If either purchased stack needs another
length, change that position on all four corners and fit smooth caps; do not
leave thread bearing against GRP.

The joint is bearing-type. Do not credit wet friction from bolt preload. Bring
the plates into full contact, tighten the nuts in a crossing sequence only to
the torque established by the connection coupon, mark nut-to-bolt witness
lines, and recheck after the wet dwell. Adhesive is not required. A
supplier-approved immersed structural epoxy may be tested as secondary
bedding, but the joint must pass with the six bolts as the fail-safe load path.

## Diagonal-joist corner support

### Upper non-projecting side eye

The C2 timber diagonal finishes at the nominal opening corner
`(+/-1150,+/-1150)`. Nothing may cross the vertical plane through that timber
tip. Fit one Wichard 6684 folding pad eye to a vertical side face of the joist,
with the centre of its base **55 mm back from the surveyed tip** and at the
joist mid-depth `Z=+112.5 mm`. Orient the pad-eye fixing axes along the joist;
the nominal axes are 43.3 and 66.7 mm back from the tip. This keeps the nearer
M6 axis about 7.2 bolt diameters from the end. Here “back” means toward the
inner-beam corner and away from the pond centre, following the actual C2 member.

Use the south-facing joist face at both southern corners and the north-facing
face at both northern corners. This makes the transverse offsets oppose in
pairs instead of imposing a common yaw on the ring. Put a **50 mm along-joist
x 60 mm vertical x 3 mm 316L spreader plate** between pad eye and timber and a
matching 3 mm 316L backing plate on the opposite face. Round plate corners to
at least 8 mm. Use two M6 x 80 mm A4-80 countersunk through-bolts per eye,
with A4 broad washers and all-metal prevailing-torque nuts at the backing
plate. Check the purchased pad-eye recess, shank grip and finished thread
before ordering the batch; cap every exposed thread. Do not use end-grain
screws or a fitting that projects past the joist tip. Check the complete folded
and loaded pad-eye sweep against that end plane on the sample, not just its base.
If any part crosses it, move the complete eye farther toward the inner beam and
rerun the mapped coordinate before drilling; do not add a projecting stop.

The nominal cord force-line points are:

| Corner    | Upper eye tangent `(X,Y,Z)` mm | Lower eye tangent `(X,Y,Z)` mm |
| --------- | ------------------------------ | ------------------------------ |
| southwest | `(-1159.546,-1218.236,+112.5)` | `(-1050,-1050,-184)`           |
| southeast | `(+1159.546,-1218.236,+112.5)` | `(+1050,-1050,-184)`           |
| northeast | `(+1159.546,+1218.236,+112.5)` | `(+1050,+1050,-184)`           |
| northwest | `(-1159.546,+1218.236,+112.5)` | `(-1050,+1050,-184)`           |

These points use the catalogue 15 mm ring-tangent offset outside a 47 mm joist
face and give a nominal line length of **358.07 mm**. Measure the actual ring,
shackle and thimble tangent. Accept only if it is within 3 mm of the scheduled
point and the taut cord clears timber and the finished deck by at least 5 mm
through its full working movement; otherwise update the surveyed coordinate
and rerun the suspension model before drilling.

At the 0.30 kN **line** proof load, the nominal cord gives about 0.248 kN
vertical and 0.168 kN horizontal resultant. The side offset also loads the
spreader, timber and existing diagonal-joist connections eccentrically. Proof
the whole eye stack and include those actions in the deck check; catalogue eye
capacity alone does not validate the timber or its load path.

### Lower corner eye

Put the lower corner eye in plan at the theoretical rail-corner axis
`(+/-1050,+/-1050)`. Make one removable **6 mm 316L top bridge** for it, using
the same local axes as the GRP plate:

```text
outline: (-35,-35) -> (125,-35) -> (-35,125) -> close
corner-bolt holes: (55,0) and (0,55), 8.5 mm diameter
pad-eye centre: (0,0)
pad-eye holes: +/-11.7 mm along the local x=-y diagonal, 7 mm diameter
external corner radii: at least 12 mm
```

Fit a [Wichard 6684 universal folding pad eye](https://industrie.wichard.com/en/stainless-steel/fastenings/folding-pad-eyes/single/part-6684)
to the bridge with two M6 x 20 mm A4 countersunk screws, broad washers and
all-metal nuts. The maker publishes 316L construction, a 750 kg nautical
working load and load capability regardless of direction. Its nuts sit in the
gap below the bridge. Create that gap with two 8 mm-long, 20 mm-OD A4 spacers
at the bridge's M8 holes. Replace only the two 55 mm corner bolts with
M8 x 100 mm A4-80 bolts so they pass through bridge, spacers, top GRP plate,
rail, sleeves and bottom plate; retain M8 x 90 at the other four positions.
Fit broad washers under the bridge bolt heads. Do not drill another hole
through the mitre or rely on one GRP plate alone as the eye connection.

With nominal rail and catalogue dimensions, the effective lower eye/shackle
tangent is `Z=-184 mm`; the nominal cord length to the upper side eye is
358.07 mm. Measure both tangents on the purchased eye, shackle and thimble.
Proof the complete bridge as part of the corner and record the inclined cord's
horizontal action.

## Calculation envelope

The retained unfactored joint actions are 60 N m in-plane racking and 30 N m
one-corner roll. The 0.30 kN side-eye line proof is separate. With 12 mm
plates, 8.5 mm maximum holes and the 140 mm outer-bolt pitch:

| Screen | Result |
| --- | ---: |
| In-plane outer-bolt force at 60 N m | 0.429 kN |
| Roll plate force at 30 N m and 50 mm plate-centre separation | 0.600 kN |
| Conservative vector combination | 0.737 kN |
| Plate bearing at the vector force | 7.2 MPa |
| Two-wall tube bearing at the vector force | 8.7 MPa |
| Low-modulus plate-path stiffness before connection compliance | 41.9 kN m/rad |
| Required complete-joint secant stiffness after bedding | at least 20 kN m/rad |

These values establish size and test loads, not product resistance. The plate
certificate must cover both in-plane directions, diagonal/shear reinforcement,
pin bearing, open-hole/net-section behaviour and long-term immersed service.

## Material and purchase schedule

Buy for **one corner first**. Buy the remaining three sets only after the wet
test passes.

| Item                                                       | One corner | Four corners after release |
| ---------------------------------------------------------- | ---------: | -------------------------: |
| 12 mm balanced structural-GRP triangular plates            |          2 |                          8 |
| M8 x 90 A4-80 partially threaded hex bolts                 |          4 |                         16 |
| M8 x 100 A4-80 partially threaded hex bolts                |          2 |                          8 |
| M8 A4 broad washers, 24 mm OD                              |         12 |                         48 |
| M8 A4 all-metal prevailing-torque nuts                     |          6 |                         24 |
| Measured-length A4/316 internal sleeves, OD at least 12 mm |          6 |                         24 |
| Smooth M8 thread caps                                      |          6 |                         24 |
| Wichard 6684 upper joist pad eye                           |          1 |                          4 |
| 50 x 60 x 3 mm 316L upper spreader plate                   |          1 |                          4 |
| 50 x 60 x 3 mm 316L upper backing plate                    |          1 |                          4 |
| M6 x 80 A4-80 countersunk upper-eye through-bolts          |          2 |                          8 |
| M6 A4 broad washers for upper-eye bolts                    |          2 |                          8 |
| M6 A4 all-metal nuts for upper-eye bolts                   |          2 |                          8 |
| M6 smooth thread caps for upper-eye bolts                  |          2 |                          8 |
| 6 mm 316L lower corner-eye bridge                          |          1 |                          4 |
| 8 mm x 20 mm OD A4 bridge spacers                          |          2 |                          8 |
| Wichard 6684 lower bridge pad eye                          |          1 |                          4 |
| M6 x 20 A4 countersunk lower-eye screws                    |          2 |                          8 |
| M6 A4 broad washers for lower-eye screws                   |          2 |                          8 |
| M6 A4 all-metal nuts for lower-eye screws                  |          2 |                          8 |
| M6 smooth thread caps for lower-eye screws                 |          2 |                          8 |

Reference stock for the longer bridge positions is this
[M8 x 100 A4-80 DIN 931 bolt](https://www.accu.co.uk/metric-hexagon-bolts/616585-SEB-M8-100-A4-80).
Its nominal 78 mm unthreaded length should cross the 76 mm bearing stack before
the lower washer; verify the actual sample for smooth-shank bearing and full
nut engagement before ordering the eight.

Machine the 24 internal corner sleeves from one 1 m length of certified 12 mm
316 round bar, boring the same 8.2--8.5 mm close hole as the accepted bolts and
facing each to the measured tube cavity. Machine the eight 20 mm bridge spacers
from certified 20 mm 316 round bar with the M8 close bore shown above. These
stock allowances are not permission to omit the first coupon or to replace
A4/316 with ungraded stainless. The smaller R5.1 stop spacers are scheduled
separately in [R5.1.md](R5.1.md).

An acceptable plate enquiry is: “12 mm smooth structural GRP plate, isophthalic
or vinyl-ester resin, balanced 0/90 and +/-45 reinforcement, permanent fresh-
water immersion, with wet modulus, pin-bearing, open-hole and machining data.”
[RBJ Plastics](https://rbjplastics.com/standard-profiles/glass-fibre-angles.html)
describes multi-layer cross-ply structural pultrusions and offers custom
production; [Anglia Composites](https://www.angliacomposites.co.uk/app/download/2719884/Data%20Brochure.pdf)
lists solid GRP plate up to 20 mm. Neither listing by itself proves that the
quoted sheet meets this joint enquiry. Reject a sheet with only a generic
strength or thickness claim.

## Fabrication and assembly

1. Make a full-size drilling/template plate from plywood. Mark the five-sided
   outline, rail centrelines, six bolt centres and fibre directions.
2. Cut one top and one bottom plate. Keep their certified strong directions at
   90 degrees unless the supplied laminate is certified balanced in both
   axes. Round, deburr, clean and seal every cut with the supplier's compatible
   resin.
3. Clamp the mitred rails square between the plates in a flat jig. Confirm the
   2,100 mm centreline dimensions and both diagonals before drilling.
4. Drill and ream the complete stack with backing support. Vacuum GRP dust at
   source. Never drill over the pond.
5. Fit the measured internal sleeves, bolts and washers. Tighten in three
   crossing passes to the coupon torque; mark every nut.
6. Fit the lower articulated corner eye and the non-projecting C2 side-eye
   assembly. Check its recorded force line and 5 mm minimum clearance; it is
   intentionally inclined, not plumb.
7. Resin-seal the mitred tube ends but keep the specified vent/drain route.
   Fit smooth caps and confirm that fish and liner can touch no fibre, burr or
   thread.
8. Test the corner before making the remaining three. After release, use the
   same template, drill sequence, bolt batch and torque record for all four.

## Release gates

Release the four-corner batch only when all of these are recorded:

- exact plate and rail certificates, including permanent-immersion basis;
- connection-coupon torque with no indentation, whitening or permanent set;
- no more than 0.05 degrees clearance-led dead band after ten bedding cycles;
- secant plan stiffness at least 20 kN m/rad from 0 to 60 N m;
- separate 0–30 N m roll and combined plan/roll cycles, followed by 90 N m
  plan and 45 N m roll proofs;
- the same tests after at least seven days' immersion, with no cracking,
  delamination, hole ovalisation, loosened witness marks or material stiffness
  loss;
- 0.30 kN line proof of the complete C2 side-eye connection over dry ground;
- a flexible-ring rerun using the measured corner curve, one ineffective
  corner and one missing cord; and
- accepted per-support, adjacent-support, side-total and temporary-uplift deck
  envelopes in [design-C.md](design-C.md).

Inspect the installed corners, eye bridges, witness marks, cords and sealed
edges after the first month, after the first drain-down, and at least annually.
