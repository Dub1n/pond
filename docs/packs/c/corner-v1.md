# Pack C rail corner — construction specification

> **Superseded design record.** The current split-plate corner is
> [corner-v2.md](corner-v2.md). Retain this document only for design and
> calculation lineage; do not use its purchase or fabrication detail for the
> prototype.

## Decision and limit of approval

**Purchase update, 15 September 2026:**
[purchase-cost-study.md](purchase-cost-study.md) supplies the current
freshwater cost candidate: 24 M8 x 80 A2-70 corner bolts with 304 tubular
crush spacers, plus **eight separate** M8 x 50 acetal-covered C2 ear posts,
and 5 mm polyester slings. It overrides the original A4-80/solid-spacer and
shared-post purchase details below, with explicit grip/bearing and wet-test
gates. The original hardware paragraphs and schedule remain reference only,
not an instruction to order both systems. Geometry is still under development.

Use the corner described here with the 38 x 38 x 5 mm structural-GRP ring and
the suspension in [cords.md](cords.md). **Do not fit an ordinary R5.1 seat at a
rail intersection.** The former three R5.1 corner-seat solids have been
removed from the coordination model. It now shows the four `t=30 mm`
Arrangement E pods as a simplified continuous upper plate with distinct
basket-retention bolt and C2-post axes; the basket itself is deliberately
omitted. That is a coordination representation, not a buildable basket arrangement. A
separately gated diagonal basket carrier is described in
[corner-basket locations](#corner-basket-locations).
The joint has a selected thick lower web and an integrated thick upper pod,
nominally 9.5–10 mm structural GRP, with six close-fit M8 through-bolts.
One continuous corner sling wraps around the existing C2 diagonal joist and
ends at two separate smooth ear posts at local `(-125,+50)` and
`(+50,-125)`, reflected at the other corners. The original 55 mm shared-post
axes are superseded for Arrangement E.

This is the issued **prototype construction detail**, not permission to load
the completed deck. The selected thick upper and lower profiles are cut from
certified 9.5 mm structural-GRP sheet and define all joint dimensions. Fabrication of the four
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

## Corner-basket locations

### Result and status

The current corner-centred R5.1 seats fail. A nominal 270 x 270 mm B27 centred
on the rail intersection covers both rails, the six M8 axes, both 55 mm cord
posts and the C2 sling departures; it also projects 35 mm beyond the 2,300 mm
opening. It is not a repairable version of R5.1 and must not be made by simply
shortening its arms or moving its bolts.

There are now two useful *spatial* arrangements at every corner: an
axis-aligned B27 moved inboard along the C2 diagonal on an upper-only diagonal
carrier (Arrangement A), or a centred B27 on a new integrated **corner pod**
(Arrangement E). SW and NE use the global `x=y` family; SE and NW use the
global `x=-y` family. They are the same local details after reflection. Both
retain the C2 sling. Neither is an issued fabrication detail: each introduces
an unanalysed plate-bending and basket-load path.

The alternative of putting the basket between the lower sling ends and C2 is
rejected. The rail centreline is 100 mm inside the opening/C2-tip plane
(`1050` versus `1150` mm); a 270 mm B27 cannot fit in that strip, even before
the 38 mm rail, cord sleeve, chafe, deck-board relief and removal clearance are
allowed. Moving the C2 lower points cannot create the missing width. Removing
the C2 sling gives a possible coordination space but is a separate suspension
redesign, not a basket-clearance modification.

### Local coordinate rule

Use the corner coordinate system already used for the plate: the rail
centrelines meet at local `(a,b)=(0,0)` and the two rail legs run in local
`+a` and `+b` directions into the pond. The C2 joist and its upper wrap are in
the opposite diagonal direction. For reference, the four local-to-global
origins/directions are:

| Corner | Local `(a,b)` direction into pond | Global diagonal family |
| ------ | --------------------------------- | ---------------------- |
| SW     | `(+x,+y)`                         | `x=y`                  |
| SE     | `(-x,+y)`                         | `x=-y`                 |
| NE     | `(-x,-y)`                         | `x=y`                  |
| NW     | `(+x,-y)`                         | `x=-y`                 |

For a square basket with measured maximum lower-envelope side `B`, put its
centre at `(t,t)`. Its envelope is `a,b = t-B/2 .. t+B/2`. Use the catalogue
nominal **`B=270 mm`** for this first spatial screen, with no arbitrary extra
plan padding. Repeat it with the measured loaded B27 lower envelope before any
cutting: the nominal 270 x 270 x 190 mm does not establish base taper,
deformation or mesh-rib positions. A 280 mm envelope remains a sensitivity
check, not the present governing placement assumption.

The current structural exclusion features are the 80 mm rail-contact strips,
the six bolt axes `(55,0)`, `(125,0)`, `(195,0)`, `(0,55)`, `(0,125)` and
`(0,195)`, the two lower cord posts at `(55,0)` and `(0,55)`, and the compact
web outer diagonal `a+b=260`. The latter is not merely a plate edge: retain a
measured no-fixing/no-cut band around it for the diagonal shear/load path. No
basket-retention washer axis is allowed in a rail strip, a bolt/washer zone, a
cord-post/chafe zone or that diagonal band. A basket may cover an existing
corner bolt in plan only when it is proved that the basket base remains clear
of the bolt head/cord-post stack and that the bolt stays wholly independent of
the basket retention load path.

### Available positions

| Arrangement | Nominal B27 centre and footprint | C2 condition | Component change | Finding |
| --- | --- | --- | --- | --- |
| **A — compact inboard diagonal carrier** | Start template at `t=170 mm`; the nominal 270 mm envelope is `a,b=35..305 mm`. The no-contact rail tangent is only `t=154 mm`, so `t=170 mm` retains 16 mm nominal clearance to the 38 mm rail's pond-side face. | Retain the present C2 wrap and lower posts. The closest basket edge is 35 mm from the `a=0`/`b=0` post lines, so actual post, washer, knot, chafe and basket clearances must be surveyed together. | Keep the complete lower 9.5 mm web unchanged. Replace only the top plate with an extended carrier that retains the exact original web and adds a rounded inboard basket wing. | **Only compact candidate.** Spatially credible, mechanically unproven. |
| **B — fully clear diagonal basket** | `t >= 370 mm` for a 280 mm envelope plus 10 mm clearance; nominal global centres are SW `(-680,-680)`, SE `(680,-680)`, NE `(680,680)`, NW `(-680,680)`. | Existing C2 sling is clear in plan. | A new diagonal cradle/cross-support is required; it is no longer a corner-plate change. | Spatially clean but rejects the low-part-count corner objective and consumes open water. Do not develop before Arrangement A is disproved. |
| **C — between rail and C2 / behind lower ends** | No B27 envelope fits. The available nominal centreline depth is only 100 mm. | Would need a new suspension route as well as a new basket carrier. | Not a permitted use of the current corner. | **Rejected.** |
| **D — remove C2 sling** | Arrangement A or B becomes easier to coordinate. | Remove the whole continuous C2 item, not one leg. | Full suspension, flexible-ring, corner and deck-reaction redesign. | **Not selected for clearance alone.** |
| **E — offset integrated corner pod** | Basket centre `t=30 mm`; nominal B27 envelope `a,b=-105..165 mm`. Its actual convex plate has a 279.3 x 367.7 mm diagonal enclosing blank, materially smaller than the `t=0` 440 mm reference. | Replace the two 55 mm posts with two new C2-side ear posts at `(-125,+50)` and `(+50,-125)`; the reflected corners use the reflected pair. | Retain the lower compact web. Make a new raised upper bracket that carries basket bearing/retention and the two cord ears as one tested assembly. | **Selected coordination/proof-template position.** This remains the hard template limit: the post fitting margin is only about 20 mm. |

The original corner-centred case (`t=0`, nominal footprint `-135..135 mm`) is
rejected **on the issued compact plate or an ordinary R5.1 seat**. It crosses
both rail lines, the 55 mm posts, all six joint fasteners and both C2 legs. It
must not appear as an available station unless it is explicitly implemented as
and passes the separate Arrangement E corner-pod prototype.

### Why moving the lower C2 posts along the rail does not rescue `t=0`

This was checked using the relaxed nominal 270 mm square and no added plan
padding. It still fails for two independent reasons.

First, a `t=0` B27 occupies `a,b=-135..135 mm`; each rail tube runs through
that plan area. Moving a cord endpoint does not remove that interface. A normal
R5.1 seat cannot resolve it; it needs a raised plate that deliberately bears
on the rail tops while the basket bears above the plate. That raised-plate load
path is exactly the new Arrangement E branch, not a consequence of changing a
cord bolt. Without it, the minimum theoretical centre for a 270 mm basket not
to touch the pond-side rail faces is `t=135+19=154 mm`.

Second, moving a lower post from `(55,0)` to the existing `(195,0)` bolt axis
does not route its sling outside the square. In the provisional local geometry,
the C2 upper tangent is approximately `(-124.7,-124.7,+75)` and the proposed
lower tangent is `(195,0,-203)`. The straight cord reaches the basket's
`a=135` boundary at approximately `(135,-23,-151)` mm: that point is within
the `t=0` basket plan and its 190 mm height above a directly-supported base.
It is a real cord-through-basket collision, not a conservative clearance
warning. Any lower point on either rail centreline with an offset up to 135 mm
is itself inside the basket plan; offsets above 135 mm merely move the endpoint
outside while the inclined leg still cuts through the basket.

An intermediate new bolt between 125 and 195 mm cannot change either result.
It remains on a rail load path and provides no perpendicular escape from the
square. A point far enough outboard of both basket sides could make the cord
leave the plan while still above the basket, but it would be beyond the
available 100 mm rail-to-C2 opening strip, would create a new projecting/deck
attachment, and would abandon the present corner load path. It is not an
acceptable intermediate-bolt solution.

For comparison, changing only the two equal lower offsets raises the
provisional C2 horizontal-to-vertical resultant from 0.775 at 55 mm to 0.953
at 125 mm, 1.042 at 160 mm and 1.131 at 195 mm. Thus the 195 mm proposal gives
no `t=0` clearance benefit while increasing the horizontal action by about
46 percent. Retain the `(55,0)` and `(0,55)` posts for Arrangement A unless a
fully redesigned support route is selected.

### Arrangement E — offset integrated corner pod

This is the proposed new bracket architecture. Its reference geometry was a
**440 x 440 mm coordinate envelope** with `t=0`, not a 440 mm solid square.
The selected geometry moves the basket to `(t,t)=(30,30)` mm. Its reference
eight-sided outer blank has a **279.3 x 367.7 mm** diagonal enclosing blank (a
370 x 370 mm axis-aligned bounding box), before cutting allowance. It has three
jobs that the issued compact web intentionally separates: retain the basket
above the rail lines, carry two C2 lower attachment posts outside the basket,
and retain the rail-to-rail corner stiffness. It is consequently a replacement
*upper* corner component, not an R5.1 seat and not a minor alteration to the
existing 55 mm posts.

In local `a,b` coordinates its convex vertices are `(-150,15)`, `(15,-150)`,
`(75,-150)`, `(220,-40)`, `(220,40)`, `(40,220)`, `(-40,220)` and
`(-150,85)`. Resolving those onto the diagonal axes gives a 395 mm span in
`a+b` (279.3 mm along `x=y`) and a 520 mm span in `a-b` (367.7 mm along
`x=-y`). Those are the enclosing dimensions of the reference octagon, not the
non-convex web and not fabrication blank dimensions; add the cutter/process
allowance separately.

#### Minimum-outline screen

The first convex-octagon conclusion is superseded.  A convex perimeter is a
useful *blank* and comparison datum, but it is not a structural requirement:
the required component is a single connected, radiused web with explicit paths
between the named attachments.  A non-convex outline is valid if every path is
continuous, locally wide enough for its actual action, has no inside radius or
cut feature below 5 mm, leaves the washer/post lands intact, and does not
project through the C2-tip plane `a+b=-200`.

The lower compact 9.5 mm web, six M8 corner bolts and its full rail-contact
strips remain unchanged.  Its 33.2 kN m/rad value is not transferred to the
new upper web.  The upper web is instead a separately proofed basket/C2/post
component: it must transfer the basket pads to the rail-top regions and the C2
ears to the existing 55 mm bolt core.  A pleasingly broad plate is not a
substitute for either path, and neither is a thin decorative ligament.

The nominal near basket-retention axis is `(-60,-60)`.  It needs an R20 mm
washer/bearing land; no outline may use the former octagon edge as proof that
this land fits.  Four measured B27 pad/retention locations remain the baseline:
three retainers, a continuous backing strip or a changed mesh interface needs
its own support-polygon, one-corner uplift and rotation proof.

#### Connected-web comparison and lower-bound screen

The upper pod is a web, not a sediment shelf.  The correct first discriminator
is therefore not a generic plate FEA or a density/topology optimiser: with no
measured B27 pad reaction, post stack, laminate data or loaded C2 tangent,
those would return an attractive but arbitrary shape.  The repeatable first
screen measures the *actual solid* normal width around the named force-line
centrelines, then applies the existing conservative isolated-strip comparison
to the C2 paths.  A later mesh/FEA may refine a measured, selected shape; it
cannot replace those inputs or the wet combined proof.

The C2 bridge centrelines are:

```text
(-125,50) -> (0,55)       and       (50,-125) -> (55,0)
```

Each is 125.1 mm long and needs a **75 mm clear gauge width between its post
and 55 mm bolt lands**.  This is the existing 9.5 mm GRP / 6 mm 5083 C2 proof
screen, not an arbitrary graphic stroke.  The six M8 axes keep R15 mm lands;
the two C2 axes keep R15 mm lands; the four nominal basket axes keep R20 mm
lands.  The two rail paths keep their 80 mm nominal width.  No resulting
inside corner or drainage opening may have a radius/ligament below 5 mm.

The supplied SVGs were rendered to PNG and raster-measured against their common
370 mm dashed reference outline.  Their source coordinates map to the present
Arrangement-E local millimetres; their view-box scale does not.  The table is
therefore a geometry screen, accurate to about 1 mm, not a cutter take-off.
`C2` is the smaller of the two direct C2-to-55 paths.  `Basket` is the smaller
of the supplied side/inner basket branches where that family contains it.

| Family; spaced sample | Area (mm2) | C2 gauge (mm) | Basket gauge (mm) | Screen result |
| --- | ---: | ---: | ---: | --- |
| Octagon `7.2` | 53,444 | 37.7 | — | Fails the 75 mm C2 screen; it has no direct side-to-55 basket branch. |
| Octagon `9.4` | 59,908 | 49.3 | — | Fails. |
| Octagon `11.8` | 67,820 | 61.0 | — | Fails; adding corner radius did not thicken the required C2 route. |
| Hand `7` | 54,534 | 37.0 | 38.6 | Fails. |
| Hand `9` | 62,987 | 48.3 | 49.9 | Fails. |
| Hand `12` | 72,700 | 64.9 | 66.4 | Fails at current thicknesses, despite good basket branches. |
| Clam `10.3` | 54,904 | 54.7 | 33.1 | Fails. |
| **Clam `14.3`** | **66,996** | **77.0** | **33.1** | First supplied C2 survivor; basket branches remain a separately unproved thin feature. |
| Clam `16.2` | 73,096 | 87.2 | 33.0 | C2 survivor but strictly more material than `14.3`. |
| DF20 ten R20 holes | 79,121 | 75 by construction | not separately defined | Superseded: a heavier, weakly legible load-path web with a 5.3 mm ligament; keep only as history. |

The correct new topology is the user-described **complete Octagon/Hand
hybrid**, not the earlier incomplete spider screen.  Its paths are exactly:

```text
195a -> 125a -> 55a -> 55b -> 125b -> 195b
195a -> inner basket corner -> 195b
P2 -> side basket corner a -> 195a
P1 -> side basket corner b -> 195b
outer basket corner -> (27.5,27.5)
```

Thus it retains the two base direct `P1 -> 55b` and `P2 -> 55a` C2 paths while
also adding the two C2-to-side-basket-to-195 routes.  The continuously radiused
`octagon-hand-complete` concept is **73,618 mm2**: 75 mm on each direct C2
bridge, 80 mm on the rail chain/cross-link, and 50 mm on each basket route.
Its smallest `a+b` boundary coordinate is `-155.3 mm`, safely inboard of the
`-200 mm` C2-tip plane.  The generated SVG in
`diagrams/corner-seat/octagon-hand-complete.svg` is an analysis silhouette, not
a fabrication profile: it deliberately contains no final holes, B27 pad shape,
post stack or cutter allowance.

It passes the present C2 width/strip screen, but it is **not** better than the
now-selected `clam.14.3_thick` on the stated area objective.  Its only
potential advantage is explicit 50 mm basket branches rather than the thick
Clam's approximately 55 mm inner branch.  The selected proof-template upper
profile is therefore `clam.14.3_thick`: it retains the 77 mm direct C2 routes,
materially improves the central transfer region, and remains smaller than this
complete-hybrid alternative.

`docs/calcs/corner_seat_web_screen.py` generates that silhouette from the named
axes and reports its area and proof-strip values, so the widths are not hidden
in a drawing stroke.  It applies a 5 mm offset pair to round re-entrant
geometry.  The remaining external perimeter is intentionally non-convex.

For a 75 mm x 125.1 mm C2 gauge, the isolated-strip comparison at the 0.30 kN
complete-sling proof action is **33.3 MPa** in 9.5 mm GRP and **83.4 MPa** in
6 mm 5083.  Five-millimetre 5083 is about 120 MPa and remains too close to its
125 MPa minimum proof level to select.  Applying that full C2 action to the
33 mm Clam basket branches would give about 75.7 MPa in 9.5 mm GRP and 189 MPa
in 6 mm 5083; that is not the intended load case, but it shows why they cannot
be casually credited as C2 load paths.

This is a conservative local discriminator, not a plate approval: it does not
credit surrounding web, lower plate or bolt preload.  Before cutting
`clam.14.3_thick`, prove one complete upper/lower corner stack
at 0.30 kN with deliberately unequal C2 legs, 50 mm basket eccentricity and a
wet dwell.  The same test must measure B27 pad reactions, test one-corner
basket uplift/rotation and inspect every 5 mm-radius/ligament region for
whitening, delamination, permanent set and sediment/fish-guard behaviour.

### Central cross-link / ring-breathing comparison

The thin `55a -> 55b` cross-link must not be judged by a distance-to-nearest-
edge reading.  At that location such a reading can include the adjoining rail
legs and materially overstate the narrow connection which is actually being
tested.  Instead, `docs/calcs/corner_crosslink_rotation_screen.py` renders the
black material silhouette of each supplied SVG at high resolution, registers
it through the dashed Arrangement-E outline, and solves a small, repeatable
plane-stress comparison mesh.  The three `a`-rail M8 lands are given a unit
rigid in-plane rotation about the rail intersection; the three `b`-rail M8
lands are fixed.  The reaction couple is the **idealised plate-only relative
rotation stiffness** below.

| Profile, 9.5 mm plate | Area (mm2) | 4 mm mesh | 3 mm mesh | 2 mm mesh (kN m/rad) | Change at 2 mm |
| --- | ---: | ---: | ---: | ---: | ---: |
| Lower `corner-web` | 39,002 | 113.33 | 114.18 | 113.48 | baseline |
| Lower `corner-web_thick` | 43,506 | 166.38 | 167.90 | 166.82 | +47.0% |
| Upper `clam.14.3` | 66,996 | 123.39 | 124.40 | 123.24 | baseline |
| Upper `clam.14.3_thick` | 71,304 | 172.61 | 174.07 | 173.21 | +40.5% |

The 2–4 mm mesh change is below 1.5% in all four cases, so this comparison is
not a raster/mesh artefact.  The new `clam.14.3_thick` is consequently a real
improvement for the corner-opening/ring-breathing mechanism: filling the
central/inner branch raises the idealised relative rotational restraint by
about 40%, even though it does **not** make the already 77 mm direct C2 bridge
wider.  It increases Clam area by 4,308 mm2 (6.4%).  Its inner branch is about
55.3 mm versus 33.1 mm for ordinary `clam.14.3`.

These values are deliberately **not** the 33.2 kN m/rad compact-corner value
and cannot be added to it.  This model fixes ideal bolt lands, omits holes,
bolt and bedding compliance, tube flexibility, laminate orthotropy, C2/basket
load split and any unproven shear transfer between upper and lower plates.  It
answers the narrow question—whether the extra central material resists
relative rail rotation in the same plate—and supports keeping the thick
cross-link as the candidate where that extra 6.4% material is acceptable.  A
complete wet upper/lower corner moment-rotation test remains the release gate;
run thin and thick specimens with the same bolt stack if the area decision is
to be made experimentally.

Keep the issued lower 9.5 mm compact web, its six M8 rail bolts and its full
rail-contact strips unchanged in function, but use `corner-web_thick.svg` as
the selected lower proof-template profile.  It may not delete, narrow, drill
through or use the six M8 corner bolts as basket retainers.  `clam.14.3_thick`
is the selected upper proof-template profile.  This preserves the compact
corner load path while making the upper plate a separate component requiring
its own combined proof.

#### C2 lower attachments

Use a symmetric two-post sling, not a central single post. At the selected
`t=30 mm`, 35 mm C2 upper-backset screen, the nominal pair is:

```text
P1 = (-125, +50, z_post)
P2 = (+50, -125, z_post)
```

where `z_post` is set by a full-height rope/post template. It must place the
rope tangent above the pod surface with no rope-on-laminate rubbing; do not
reuse `-203 mm` as a fabrication elevation without measuring the new stack.
The points are inboard of the C2-tip boundary `a+b=-200` and preserve two
independent lower legs. Their negative coordinate is about 20 mm outside the
near B27 face in plan, leaving a real post/washer/chafe fitting region rather
than only a drawn line clearance. A smooth replaceable A4/316 post, spacer and
broad retaining washer are required at each point; the metal post stack carries
the local clamp and rope bearing, while the cord/chafe sleeve remains outside
the preload stack.

The key clearance is at basket-rim elevation, not merely in plan. Using the
provisional upper tangent `(-125,-125,+75)`, a lower tangent at `z=-203` and a
190 mm-tall nominal basket with rim near `z=-13`, each cord reaches the
negative basket face at about 20 mm clear of it. The measured post height,
cord diameter, chafe sleeve, knot departure, basket rim and loaded height must
be substituted before choosing the ear coordinate.

A single lower post directly beneath C2 is not selected. The point far enough
outboard to clear the basket would cross the C2-tip plane, concentrate both
legs/chafe on one post and lose the useful two-leg fault/load path. Likewise,
the positive/pond-side perimeter cannot work: from the current upper tangent a
cord would need an implausible lower coordinate of about `+697 mm` to leave the
positive basket face while still above its rim.

For this pair, each leg is inclined in plan but the pair's horizontal
components remain moderated. The prior rigid-ring figures (rank 6/6, 85.2 N
maximum listed-case leg tension, 4.24 mm movement, all 36 one-complete-item
loss cases feasible and 98.3 N worst remaining leg) apply to the superseded
`t=20 mm` pair only. Re-run that model for the selected `t=30 mm` points before
crediting any structural capacity; neither result establishes the new post,
pod, C2 timber or deck capacities.

#### Offset and upper-wrap optimization

The following is a geometry-and-rigid-ring screen, with nominal 270 mm B27,
20 mm rim-height cord clearance, lower tangent provisionally `z=-203 mm`,
upper tangent `z=75 mm` and the current 35 mm C2 upper backset. The required
ear coordinates move inward by about **63 mm for each additional 20 mm of
`t`**. That quickly removes the physical space for a post, washer, chafe sleeve
and a broad ligament into the pod.

| Basket `t` | B27 plan envelope | First ear pair            | Approx. square blank envelope | Result                                                      |
| ---------: | ----------------- | ------------------------- | ----------------------------: | ----------------------------------------------------------- |
|       0 mm | `-135..135`       | `(-220,20)` / `(20,-220)` |                        440 mm | Reference only; needlessly large.                           |
|      20 mm | `-115..155`       | `(-157,40)` / `(40,-157)` |                    **377 mm** | Superseded coordination position; about 42 mm plan room.    |
|  **30 mm** | `-105..165`       | `(-125,50)` / `(50,-125)` | **279.3 x 367.7 mm** diagonal | **Selected proof template.** About 20 mm plan room remains. |
|      40 mm | `-95..175`        | `(-94,60)` / `(60,-94)`   |                        314 mm | Reject: the post is effectively on/in the basket envelope.  |

Do not pursue the attractive-looking 314 mm arithmetic envelope. It assumes a
line cord and zero-size post, washer, chafe sleeve, knot and ligament. The
selected plate removes unneeded square corners rather than treating the 345 mm
square estimate as a cut blank. Its remaining 20 mm post-fitting margin is
only a proof-template condition: do not move farther than `t=30 mm` unless a
full-size template proves the post, washer, chafe sleeve, knot and ligament
stack.

Moving the upper C2 wrap farther back along the joist moves its projected upper
tangent outward and lets a line-cord calculation pull the ears inward, but this
is not a free reduction. At 70 mm backset, `t=0` already brings the required
negative ear coordinate to about `-167 mm`; combining 70 mm backset with
`t=20 mm` brings it to about `-104 mm`, inside the B27/post fitting region. At
100 mm backset the `t=0` coordinate is already about `-121 mm`, likewise too
close to the nominal basket. Keep the existing **35 mm** screen backset for
the first pod prototype. Treat about **70 mm** as a soft upper limit only for
a zero-offset fit-up, then rerun the C2 timber, deck reaction and full-height
clearance checks. Joist capacity may improve with a further-back wrap, but it
does not improve this pod's usable cut envelope.

#### Basket support and minimum material topology

Do not make the full square. The minimum topology to calculate and test is:

1. the intact original compact-web core and all six corner-bolt/washer zones;
2. four measured basket bearing pads in the central zone, initially trialled
   near `(t-90,t-90)`, `(t-90,t+90)`, `(t+90,t-90)` and `(t+90,t+90)`;
3. two C2-side ears ending at `P1` and `P2`, with broad continuously radiused
   ligaments back into the compact-web core; and
4. only the local bridges needed to transfer the four basket pad reactions to
   the rail-top bearing regions and the C2 ear actions to both rail legs.

The four nominal pad centres are 45 mm inside the nominal basket faces, clear
of the rail centrelines and clear of the compact web's outer diagonal load
band. They are layout targets only. Move them to measured sound B27 base-rib
intersections while retaining the complete 40 mm penny-washer footprint over
at least four continuous ribs/strands. If that cannot be done, use a tested
continuous HDPE/structural backing strip; do not shrink the washers.

Three isolated M6 basket retainers are **not** an accepted material-saving
substitution. Three corner-like points put the square basket centre on, or very
near, the triangle's open edge: a 50 mm eccentric load, handling uplift, one
loosened fastener or wet mesh creep can then tip it about the two-retainer line.
The broad pod beneath the basket supplies compression bearing but not a positive
uplift keeper at the omitted corner. A three-feature system can be considered
only if the features are a tested continuous backing/bearing strip that gives a
real support polygon and anti-rotation restraint. Until that test exists,
retain four independent measured mesh-rib washer positions; removing a fourth
washer does not reduce the governing C2-ear or compact-web material.

Clip the pond-side `(+a,+b)` corner and all material that does not form one of
those four paths first. **Never retain material with `a+b<-200`:** that would
project past the C2 joist-tip plane. The two ears necessarily extend below the
deck overhang in one coordinate (`120 mm` beyond the 2,300 mm opening line),
so the full-height prototype must also prove water volume, C2/joist/deck-board
clearance, plant removal and no contact with deck structure. This is a physical
boundary check, not something the plan model can waive.

Normal basket gravity bears through defined B27 base bands onto the pod pads,
then into the rail tops and retained corner core. The four M6 basket bolts only
retain the empty rigid basket. In the opposite direction the C2 pair applies
uplift plus two opposed local horizontal reactions at the ears. The pod must
therefore be checked for central plate bending, ear prying, local torsion,
rail-top bearing, bolt/washer bearing, one-corner basket uplift, 50 mm
eccentric basket load, one loosened basket fastener and C2 unequal sharing.
The 33.2 kN m/rad compact-web value cannot be credited to any of these new
upper-pod actions.

#### Promotion gates specific to Arrangement E

Before cutting a pod blank, provide a full-size transparent plan/elevation
template with the real B27, the two real cord tangents, chafe sleeves, post
stacks, C2 timber, joist underside and removable deck board. Before promoting
it from one-corner prototype, additionally pass:

- a certified-wet-laminate calculation for the pod's bearing pads, ligaments,
  ears and transfer into the retained web;
- the existing wet corner stiffness/dead-band and plan/roll proofs unchanged;
- a complete C2-sling proof with deliberately unequal leg sharing, one damaged
  chafe/post inspection and loss of the whole continuous sling;
- B27 basket retention, wet creep, cartridge removal and empty-basket removal
  without disturbing either lower C2 leg; and
- a measured-coordinate rigid/flexible-ring and deck reaction rerun, including
  the full C2-sling-loss case and all new upper-post forces.

Until those gates pass, Arrangement E is a useful prototype branch, not a
replacement for Arrangement A or an approved centred corner basket.

### Arrangement A — controlled spatial template

This is a geometry template for one dry prototype, not a cut drawing. Make a
full-size transparent or plywood template of the measured B27 lower envelope,
four 40 mm washer footprints, the two cord-post/washer/chafe stacks and both
actual C2 cord tangents. Put the basket centre at local `(170,170)` first.
Move it only farther inboard; never toward the rail intersection. The template
passes only when all of the following are true:

1. the whole empty and filled B27 envelope, including its removal sweep, is
   inside the rail square and clear of the two C2 legs, posts, knots, chafe
   sleeves, rail, corner bolts and removable deck-board underside;
2. all four chosen retention points are on sound B27 base-rib intersections and
   each complete 40 mm washer footprint bears on at least four continuous
   ribs/strands, as required for R5.1;
3. no retention axis, washer footprint, carrier cut or carrier hole lies in an
   80 mm rail-contact strip or in the measured protected width about
   `a+b=260`; and
4. the basket can be lifted inward through its complete removal path after its
   planted cartridge has been removed, without releasing or rubbing a C2 cord.

For the nominal 270 mm basket, a symmetric four-point trial grid is
`(85,85)`, `(85,255)`, `(255,85)` and `(255,255)` mm. For the 280 mm check
envelope, begin instead with `(90,90)`, `(90,250)`, `(250,90)` and
`(250,250)` mm, then move each point only to a measured qualifying mesh-rib
intersection. These are *candidate support centres*, not drilling coordinates.
The near point remains clear of the rail strips; the two cross points sit
outside the outer-diagonal load band; and the far point requires the inboard
wing. If a real basket cannot supply four qualifying points in these regions,
reject washer-only retention for the corner carrier and design a measured
continuous backing strip/plate instead. Do not reduce the 40 mm washer or use
a single mesh cell to make the grid fit.

The top component must be one radiused structural-GRP **corner basket carrier**
with two defined regions:

- the original six-sided 9.5 mm compact-web geometry, uncut and with all six
  M8 axes unchanged, so its tested corner stiffness/load path is retained; and
- an inboard wing reaching past the far two retention points, with a separate
  bending/load-spreading calculation from the four B27 points back to the
  retained web/rail bearing paths.

The lower plate remains the issued compact web. Do not add a basket-sized
lower plate, drill the rail for a corner seat, use a normal R5.1 lower bridge,
or make the basket retention bolts part of the corner-joint clamp stack. The
upper extension is not automatically acceptable because it looks like a broad
plate: its wet laminate properties, fibre direction, cantilever bending,
local bearing, re-entrant radii, bolt-hole effects, torsional effect on the
corner and one-corner basket uplift all need checking. The existing
33.2 kN m/rad plate-path figure applies to the compact corner web only and
does not certify the wing.

Use the same prototype basket-retention stack as R5.1 only after the B27
sample passes: four M6 x 40 A4 button-head screws and four internal 40 mm A4
penny washers, with lower washer, locknut and cap. The internal washers retain
the empty rigid basket; they do not carry normal basket gravity through mesh.
Normal gravity must bear through the measured B27 base bands onto dedicated
carrier bearing pads/strips. Keep the planted cartridge, harness and fish guard
structurally independent and removable.

### C2 sling options and structural effect

Keep the C2 wrap as near its tip as the timber stop, screw edge distance and
deck-board relief permit. The current numerical screen uses a 35 mm diagonal
backset, upper tangent `z=75 mm`, lower-post tangent `z=-203 mm`, and 55 mm
lower offsets. Its 36-item layout is rank 6/6; the listed uneven-plus-seat-
torque case gives 94.5 N maximum leg tension, 5.02 mm rigid-body movement and
all 36 one-complete-item-loss cases feasible (worst remaining leg 117.2 N).
Those are provisional force-line results, not connection capacities.

Moving the upper C2 wrap back changes this screen only moderately, but makes
the horizontal action worse: with the existing lower posts, the listed-case
maximum leg is 92.8 N at 0 mm backset, 94.5 N at 35 mm, 96.4 N at 100 mm and
97.7 N at 200 mm. It is therefore a fit-up variable, not a clearance tool.
Record the real tangents and rerun before cord cutting.

Do **not** spread the lower endpoints along the rails to make basket room unless
Arrangement A fails its measured clearance test. It moves the force into a
different part of the rail/corner and increases C2 horizontal reaction sharply.
For equal C2 leg sharing in the provisional geometry, resultant horizontal to
vertical force ratio is about 0.775 at the 55 mm baseline offset, 0.914 at
110 mm, 1.194 at 220 mm and 1.449 at 320 mm. A 140 mm upper backset worsens
the same ratios to about 1.152, 1.572 and 1.826 at 55, 220 and 320 mm
respectively. Any new lower-post position needs a new structural load path,
post/chafe detail, corner moment check, C2 timber-stop check, deck horizontal
envelope and wet proof; it cannot borrow the acceptance of the `(55,0)` and
`(0,55)` posts.

Removing all four continuous C2 slings remains a last-resort redesign branch.
In the current rigid-ring screen it remains rank 6/6, but the maximum listed-
case leg rises to 102.4 N, the worst one-item-loss leg to 127.6 N, the
uneven-plus-torque movement to 5.25 mm, and upper resultant envelope to
133.9 N (from 126.0 N). That does not validate loss of the dedicated corner
support, flexible-ring racking, corner connection actions, deck reactions or
the physical failure progression. Do not remove C2 merely to gain a basket
location.

### Required proof before promotion

Do not amend the production position sheet, buy batch carrier material or add
corner baskets to the YAML until one complete Arrangement A prototype has:

1. a surveyed B27 base/rim/taper/loaded envelope and four accepted mesh-rib
   retention positions;
2. a full-size plan-and-height template proving at least the agreed clearance
   to both real C2 legs, all chafe, posts, washer stacks and deck-board relief;
3. a carrier calculation using certified immersed properties for the new upper
   wing, including gravity, 50 mm eccentricity, one-corner handling uplift,
   basket-retention uplift, local bearing and transfer into the retained web;
4. the issued corner tests unchanged: no more than 0.05 degree bedding dead
   band, at least 20 kN m/rad wet secant stiffness, combined plan/roll tests
   and the complete 0.30 kN unequal-sharing C2-sling proof;
5. a rerun of the suspension with measured C2 upper and lower tangents, the
   real completed basket mass and the complete-C2-sling-loss case, followed by
   the flexible-ring/corner/deck reaction check; and
6. wet repeated cartridge removal, empty-basket removal/reinstallation, seven-
   day immersion, creep/whitening checks at all four mesh washers, and no cord
   chafe, snag, loss of clearance or basket migration.

Until then, place the two hard-rush B28s and the *Butomus* B27 at accepted
straight-side stations. They can still read as corner planting, but the
corner itself is not an available batch basket station.

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

**Historical hardware schedule:** the current common-sheet/A2 prototype
purchases and corrected eight-separate-post count are in
[purchase-cost-study.md](purchase-cost-study.md). Do not order the following
long A4 bolts or solid stainless spacers for that candidate.

Buy for **one corner first**. Buy the remaining three sets only after the wet
test passes.

| Item                                                                   |      One corner |   Four corners after release |
| ---------------------------------------------------------------------- | --------------: | ---------------------------: |
| 9.5 mm certified structural-GRP sheet, selected thick upper/lower webs |               / | included in GRP common-sheet |
| M8 x 90 A4-80 partially threaded hex bolts                             |               4 |                           16 |
| M8 x 100 A4-80 partially threaded hex bolts                            |               2 |                            8 |
| M8 A4 broad washers, 24 mm OD                                          |              12 |                           48 |
| M8 A4 all-metal prevailing-torque nuts                                 |               6 |                           24 |
| Measured-length A4/316 internal sleeves, OD at least 12 mm             |               6 |                           24 |
| Smooth M8 thread caps                                                  |               6 |                           24 |
| Smooth A4/316 upper cord-post spacers, 20-25 mm OD                     |               2 |                            8 |
| Broad smooth A4 cord-retaining washers                                 |               2 |                            8 |
| 6 mm polyester corner sling and chafe sleeves                          | measured sample |    measured cutting schedule |
| Treated upper-face C2 cord stop                                        |               1 |                            4 |
| Stainless stop screws                                                  |               2 |                 8 plus spare |

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

The selected `corner-web_thick` lower web and `clam.14.3_thick` upper web are
not a 200 mm flat-bar take-off.  For the first proof corner, obtain at least a
**420 x 705 mm** 9.5 mm certified structural-GRP blank: it carries one 407.8
mm upper bounding profile above one 282.8 mm lower bounding profile, with the
5 mm nominal cutting clearances retained.  For the released four-corner set,
the common-sheet screen is approximately **1,505 x 1,015 mm**, as listed in
[purchase-cost-study.md](purchase-cost-study.md).  Cut only the first upper/lower pair until its
wet proof passes.

Before cutting, obtain the bar maker's written permanent-fresh-water,
wet-modulus, pin-bearing, open-hole and machining data. The section need not be
called balanced sheet, but its documented directional properties must support
both rail legs and the outer diagonal load path. Reject generic recycled
[RG1000/UHMWPE](https://www.directplastics.co.uk/pdf/datasheets/RG1000-black-green-data-sheet.pdf):
its approximately 0.9 GPa modulus and high creep make it a wear plastic, not a
suitable structural corner web at any practical thickness.

The [published E23 grade comparator](purchase-cost-study.md#published-e23-grade-comparator)
is included in the material schedule for quote comparison.  It is not a
substitute for those delivered-sheet and immersed-service data, nor for the
wet corner proof.

## Fabrication and assembly

Use [install-walkthrough.md](install-walkthrough.md) for the current full-ring
sequence, revised seat clamp and C2 chafe allocations. In particular, reopen
the drilled corner stacks for cleaning, sealing and internal sleeve insertion
before loosely assembling and squaring all four corners. Do not close the last
mitre with sleeves still to insert. Historical post/material instructions above
do not override the current purchase and installation guides.

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
