# Pack C rail corner — construction specification

## Decision and limit of approval

Use the corner described here with the 38 x 38 x 5 mm structural-GRP ring,
the R5.1 seats and the suspension in [cords.md](cords.md). The joint has two
9.5 mm compact triangular plan-web plates and six close-fit M8 through-bolts. One
continuous corner sling wraps around the existing C2 diagonal joist and ends
at two smooth posts on the corner's existing 55 mm bolt axes.

This is the issued **prototype construction detail**, not permission to load
the completed deck. It uses one 200 x 9.5 x 3,000 mm structural-GRP flat bar
for all eight webs and defines all joint dimensions. Fabrication of the four
installed corners still depends on the material certificate, one wet corner test
and the deck checks
listed under [release gates](#release-gates). Those gates test connection slip
and wet behaviour which cannot be made certain by bolt-strength arithmetic.

## Why this arrangement is selected

- The former 220 x 70 x 8 mm paired-strip estimate was only about
  18.7 kN m/rad before bolt and bedding flexibility. It could not securely
  deliver the required 20 kN m/rad installed stiffness.
- Retaining the 80 mm load-path strips in 9.5 mm plate gives a conservative
  paired-strip estimate of about **33.2 kN m/rad before connection compliance**.
  The complete tested joint must still achieve at least 20 kN m/rad after
  bedding. Eight millimetres leaves too little connection-compliance allowance
  to select.
- Three bolts per leg retain the useful 140 mm outer-bolt lever and add a
  middle load path if a fastener loosens. M8 is selected in place of the
  earlier M6 prototype so close holes, shanks, bushes and broad washers can be
  made more repeatably.
- One two-legged sling at each corner replaces the former end supports. Its
  midpoint bears around C2 without a fitting beyond the timber, while its two
  ends introduce support into both rail legs through existing corner bolts.
  The surveyed sling geometry and horizontal action must be included
  explicitly in the suspension and deck envelopes.
- The full triangular web braces the two rail legs without the complete
  220 x 220 sediment shelf of a square plate.

## Joint geometry

### Coordinate convention and plate outline

Set local `x=0, y=0` at the intersection of the two 38 mm rail centrelines.
The two rail legs extend along local `+x` and `+y`. Dimensions below are
millimetres and apply to both top and bottom plates.

Cut each 9.5 mm plate to this six-sided compact outline:

```text
(-40,40) -> (40,-40) -> (220,-40) -> (220,40)
            -> (40,220) -> (-40,220) -> close
```

The new inner diagonal from `(-40,40)` to `(40,-40)` removes only the unbolted
inside-corner triangle. Each rail contact tapers from 40 mm at the theoretical
mitre to the full 80 mm width by `x=40` or `y=40`; all six bolt and washer zones
remain in full-width strip. The 24 mm washer at either 55 mm axis has about
27 mm clearance to the new diagonal. The outer diagonal web between `(220,40)`
and `(40,220)` is unchanged. Round every corner, including both ends of the
new inner diagonal, to at least 12 mm radius. Do not cut drainage holes in the
first test joint. If the test shows a sediment trap, add only the hole pattern
accepted in the wet corner test; do not drill through the 80 mm rail strips,
the outer diagonal load path or any washer zone.

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
2. the 9.5 mm top plate;
3. the 5 mm top wall of the rail;
4. a 28 mm nominal internal compression sleeve;
5. the 5 mm bottom rail wall;
6. the 9.5 mm bottom plate;
7. another 24 mm A4 broad washer; and
8. an A4 all-metal prevailing-torque nut.

The **sleeve length is the measured clear cavity**, not an assumed 28 mm.
Use an A4/316 sleeve at least 12 mm outside diameter with an 8.2–8.5 mm bore,
square ends and no burr. Insert and retain the sleeves while the mitred tube
ends remain open. They prevent tightening from crushing the hollow section;
they do not replace bolt bearing in the close holes.

Use M8 x 90 mm A4-80 partially threaded hex bolts at the 125 and 195 mm axes.
The two 55 mm axes use the length established with the smooth cord-post stack
above the top plate, provisionally M8 x 100. Check that
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

## C2 corner sling

The C2 timber diagonal finishes at the nominal opening corner
`(+/-1150,+/-1150)`. Nothing may cross the vertical plane through its tip.
Wrap the middle of one continuous 6 mm polyester sling around the joist, over
smooth replaceable chafe protection. A small rounded treated-timber stop on
the accessible upper face prevents movement toward the free end but carries no
vertical load. Set its exact backset using the real sling, screw edge distances
and a relieved removable-deck-board template.

Record the actual tangents where the two sling legs leave the wrapped joist.
Prefer the closest practical position to the tip because moving the wrap back
increases horizontal action,
but leave enough sound upper face for the stop and its two stainless screws.
Rerun the suspension and deck reactions using the measured position before
cutting the four slings.

Use the existing corner bolt axes `(55,0)` and `(0,55)` as the two lower points.
Above each top plate fit a short smooth A4/316 compression spacer, provisionally
20-25 mm outside diameter, over the M8 bolt shank. Retain the cord beneath a
broad smooth washer and bolt head. The metal spacer completes the corner-bolt
clamp path; the rope and its chafe sleeve remain outside that preload stack.
No thread may contact the rope.

Bring one sling end to each post and use the accepted knot and tail detail in
[cords.md](cords.md). The points lie on separate rail legs and are about
77.8 mm apart. This is preferable to a single corner point for the direct-cord
prototype, but unequal leg tension can apply a local moment. Proof both legs
together, deliberately bias the sharing, and include loss of the whole
continuous sling.

Do not drill cord holes through the GRP corner plate for the first prototype.
The existing bolt axes provide replaceable rounded bearing without cutting
more laminate. A radiused, sleeved two-hole detail is only a fallback if the
post test reveals a real clearance or chafe problem.

## Calculation envelope

The retained unfactored joint actions are 60 N m in-plane racking and 30 N m
one-corner roll. The 0.30 kN complete-sling proof is separate. With 9.5 mm
plates, 8.5 mm maximum holes and the 140 mm outer-bolt pitch:

| Screen | Result |
| --- | ---: |
| In-plane outer-bolt force at 60 N m | 0.429 kN |
| Roll plate force at 30 N m and 47.5 mm plate-centre separation | 0.632 kN |
| Conservative vector combination | 0.763 kN |
| Plate bearing at the vector force | 9.5 MPa |
| Two-wall tube bearing at the vector force | 9.0 MPa |
| Low-modulus plate-path stiffness before connection compliance | 33.2 kN m/rad |
| Required complete-joint secant stiffness after bedding | at least 20 kN m/rad |

These values establish size and test loads, not product resistance. The plate
certificate must cover both in-plane directions, diagonal/shear reinforcement,
pin bearing, open-hole/net-section behaviour and long-term immersed service.

## Material and purchase schedule

Buy for **one corner first**. Buy the remaining three sets only after the wet
test passes.

| Item                                                       | One corner | Four corners after release |
| ---------------------------------------------------------- | ---------: | -------------------------: |
| 200 x 9.5 x 3,000 mm structural-GRP flat bar               | one stock bar, cut two |       one stock bar, cut eight |
| M8 x 90 A4-80 partially threaded hex bolts                 |          4 |                         16 |
| M8 x 100 A4-80 partially threaded hex bolts                |          2 |                          8 |
| M8 A4 broad washers, 24 mm OD                              |         12 |                         48 |
| M8 A4 all-metal prevailing-torque nuts                     |          6 |                         24 |
| Measured-length A4/316 internal sleeves, OD at least 12 mm |          6 |                         24 |
| Smooth M8 thread caps                                      |          6 |                         24 |
| Smooth A4/316 upper cord-post spacers, 20-25 mm OD         |          2 |                          8 |
| Broad smooth A4 cord-retaining washers                     |          2 |                          8 |
| 6 mm polyester corner sling and chafe sleeves              | measured sample | measured cutting schedule |
| Treated upper-face C2 cord stop                            |          1 |                          4 |
| Stainless stop screws                                     |          2 |               8 plus spare |

Reference stock for the longer cord-post positions is this
[M8 x 100 A4-80 DIN 931 bolt](https://www.accu.co.uk/metric-hexagon-bolts/616585-SEB-M8-100-A4-80).
Its nominal 78 mm unthreaded length should cross the original bearing stack,
but the revised post changes the required grip. Verify the actual sample for
smooth-shank bearing and full nut engagement before ordering the eight.

Machine the 24 internal corner sleeves from one 1 m length of certified 12 mm
316 round bar, boring the same 8.2--8.5 mm close hole as the accepted bolts and
facing each to the measured tube cavity. Make the eight short cord-post spacers
from certified A4/316 tube or bar with a close M8 bore and a fully rounded cord
bearing surface. These stock allowances are not permission to omit the first
coupon or to replace A4/316 with ungraded stainless.

The selected stock is one **200 x 9.5 x 3,000 mm structural-GRP flat bar**.
Rotate the compact webs alternately 45 and 225 degrees: each needs a 183.85 mm
stock width and the alternating nesting pitch is 304.1 mm with at least 5 mm
between outlines. Eight require about 2,506.4 mm including 5 mm end trim at
each end, leaving about 494 mm of bar. Cut only the first top/bottom pair for
the prototype corner; retain the remaining material uncut until release.

Before cutting, obtain the bar maker's written permanent-fresh-water,
wet-modulus, pin-bearing, open-hole and machining data. The section need not be
called balanced sheet, but its documented directional properties must support
both rail legs and the outer diagonal load path. Reject generic recycled
[RG1000/UHMWPE](https://www.directplastics.co.uk/pdf/datasheets/RG1000-black-green-data-sheet.pdf):
its approximately 0.9 GPa modulus and high creep make it a wear plastic, not a
suitable structural corner web at any practical thickness.

## Fabrication and assembly

1. Make a full-size drilling/template plate from plywood. Mark the six-sided
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
6. Fit the two smooth lower cord posts and the protected C2 wrap. Check both
   recorded sling force lines, knot access and 5 mm minimum deck clearance;
   the legs are intentionally inclined, not plumb.
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
- 0.30 kN proof of the complete two-legged C2 sling over dry ground, including
  deliberately unequal leg sharing and no continuous bearing on the top stop;
- a flexible-ring rerun using the measured corner curve, one ineffective
  corner and one missing cord; and
- accepted per-support, adjacent-support, side-total and temporary-uplift deck
  envelopes in [design-C.md](design-C.md).

Inspect the installed corners, cord posts, knots, chafe sleeves, witness marks
and sealed edges after the first month, after the first drain-down, and at
least annually.
