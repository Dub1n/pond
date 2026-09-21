# Split GRP plate and 200 mm flat-bar study

> **Historical GRP study with current aluminium addendum.** The active cutting
> basis is [aluminium-cut-parts.md](../packs/c/aluminium-cut-parts.md); the
> split R5.2 results below are retained for calculation lineage.

## Result

The split R5.2 seat and split upper-corner proposal is suitable for continued
prototype development.  A defensible first cutting family uses:

- **40 mm** wide upper arms;
- **90 mm** wide upper bridges; and
- **35 mm** wide lower bridges.

All are straight round-capped capsules.  Their overall length is their
connection-centre span plus their own width.  These are screening minima, not
released dimensions: actual reinforced basket bands, purchased-profile data,
wet coupons and the complete-seat proof still govern.

With nine equal dedicated seats, eight supplied split upper-corner halves and
four existing `corner-web_thick` lower webs, Deepnest produced complete
orientation-controlled layouts on **three 200 x 9.5 x 3,000 mm bars** for all
three basket-base cases.  Two bars are the theoretical area lower bound, but
the attempted two-bar Deepnest runs produced no complete layout.  This is not
a mathematical proof that every possible two-bar layout fails.

## Seat width screen

Use the comparison basis inherited from R5.1: 9.5 mm GRP, `E = 8 GPa`, 0.30 kN
screen load, 38 mm rail and 2 mm initial-movement target.  The basket dimension
below is the assumed **reinforced square base/connection-centre span**, not the
nominal rim size.

For one half of one upper arm, the existing uniformly loaded cantilever screen
uses `L = base / 2 - 19 mm`.  The widths required by the 2 mm movement limit
are only 9.8, 6.7 and 4.4 mm for 250, 225 and 200 mm bases.  Flexure therefore
does not set a usable arm width.  The selected 40 mm leaves 20 mm from the M8
axis to either transverse edge and must still cover the measured reinforced
basket band.

The upper bridge carries both M8 rows.  Their centres are 56 mm apart, so a
straight 90 mm capsule leaves 17 mm from each centre to its transverse edge,
just over `2d` for M8.  This connection geometry governs the bridge width.
A deliberately conservative full-0.30-kN point-load beam comparison would
require widths of 85.4, 62.3 and 43.7 mm over spans of 250, 225 and 200 mm;
90 mm also passes that comparison in every case.  Normal gravity is less
severe because the bridge bears on the rail along its length.

For one lower bridge, the existing full-0.30-kN central point-load comparison
over its 56 mm bolt span gives about **8.0 MPa and 0.055 mm** at 35 mm width.
Its 17.5 mm transverse centre-to-edge distance, washer seating and wet
open-hole coupon are more important than gross flexure.

| Reinforced square base / upper connection span | Upper arm, W x overall L | Upper bridge, W x overall L | Lower bridge, W x overall L |
| ---: | ---: | ---: | ---: |
| 250 mm | 40 x 290 mm | 90 x 340 mm | 35 x 91 mm |
| 225 mm | 40 x 265 mm | 90 x 315 mm | 35 x 91 mm |
| 200 mm | 40 x 240 mm | 90 x 290 mm | 35 x 91 mm |

Do not reduce the 90 mm bridge merely because the smaller baskets have lower
bending demand: the four fixed bolt axes still occupy the same transverse
width.  Do not reduce an arm below 40 mm until an actual basket shows a narrower
continuous reinforced bearing band and the wet connection coupon supports it.

## Corner screen

The supplied upper half is approximately **353.55 x 157.33 mm** in its
45-degree stock orientation.  The existing thick lower web is approximately
**353.53 x 197.48 mm** in its 45-degree stock orientation.  The latter fits a
nominal 200 mm bar geometrically, but has only about 2.5 mm total width margin;
measure the delivered bar and prove its cutting/edge-sealing method before
counting that fit as fabricable.

The revised C2 axes read approximately `(-140,55)` and `(55,-140)`.  Thus the
direct C2-to-neighbouring-55 span is 140 mm rather than the former 125.1 mm.
Keeping the former 33.3 MPa isolated-strip result at 9.5 mm thickness would
require about **83.9 mm** width.  Raster measurement of the new supplied
silhouette gives about **117.7 mm** through the middle of each direct C2
bridge; its corresponding isolated-strip result is about **23.7 MPa**.  It
therefore passes that narrow comparison with useful margin.

The connection-land screen gives:

- about 38.9 mm centre-to-edge at each separate C2 post, comfortably enclosing
  the present 30 mm roof washer;
- about 19.4 mm centre-to-edge at the two shared 55 mm rail axes, enough for a
  24 mm washer and just over `2d`, but not a generous `3d` land; and
- only about 10.5 mm centre-to-edge at each single-layer outer basket axis.

The last value is too close to treat as an issued detail.  An 18 mm underside
M6 washer fits nominally with only about 1.5 mm to the profile edge, but cutting
and drilling tolerance, wet bearing and handling leave inadequate comfort.
Widen those local basket lands to at least a **16 mm axis-to-edge screening
minimum**, preferably the former R20 land, before making a template.

At a shared inner rail bolt, putting the earlier 0.763 kN corner-bolt action and
the complete 0.30 kN C2 proof action onto one 6.5 mm effective bearing diameter
in one 9.5 mm ply gives about **17.2 MPa nominal bearing**.  This remains below
the dry 70 MPa E23 comparator, but it does not establish real load sharing,
wet bearing, bedding stiffness or fatigue.  Both upper plies, the unchanged
lower web and the actual washer/sleeve stack must be present in the coupon.

The two upper plates each retain a roughly 38.8 mm local inner-link half, and
both share the two 55 mm bolts.  This is a plausible parallel path, but it is
not the former monolithic `clam.14.3_thick` plate.  The old plate-only corner
opening stiffness result therefore does **not** transfer.  A fresh two-plate
connection model or, more usefully for this prototype, the complete wet corner
proof remains required.

The layer step also needs an explicit detail.  With the rail-side plate below
the C2-side plate, one single-layer basket point is 9.5 mm low.  Use a sealed
9.5 mm GRP offcut pad at that low point, broad enough for the measured basket
bearing feature; do not pull the plastic basket across the step with its M6
fastener.

## Deepnest basis and results

`split_plate_stock_study.py` generates 57 external cutting silhouettes per
case:

- 18 upper arms;
- 9 upper bridges;
- 18 lower bridges;
- 8 supplied upper-corner halves; and
- 4 existing thick lower corner webs.

Internal holes and slots are not reusable stock and are conservatively left in
the cutting envelopes.  The reported envelope areas are therefore greater
than finished laminate areas.

| Base case | Cutting-envelope area | Area-only bar equivalent | Demonstrated Deepnest purchase | Best occupied lengths of the three bars |
| ---: | ---: | ---: | ---: | ---: |
| 250 mm | 1.1080 m2 | 1.847 bars | **3 bars** | 2,212 / 2,244 / 2,240 mm |
| 225 mm | 1.0698 m2 | 1.783 bars | **3 bars** | 2,194 / 2,088 / 2,204 mm |
| 200 mm | 1.0315 m2 | 1.719 bars | **3 bars** | 2,090 / 2,034 / 2,010 mm |

Deepnest used only 0/180-degree rotations so that it could not turn a member
across the pultrusion direction to improve utilisation.  Contact nesting was
used as a material-quantity screen; add the measured saw kerf and edge-cleanup
allowance before transferring a layout to stock.  Each demonstrated layout
has more than 750 mm longitudinal remainder per bar, so ordinary kerf spacing
does not change the three-bar purchase count.  The 197.48 mm lower-web width,
not longitudinal capacity, is the fabrication-sensitive fit.

The retained layouts and placement data are in
`docs/packs/c/nesting/output/split-flat-bar/`.  Deepnest's continuous 6 m
attempt did not produce a complete 57-part layout for any case; partitioning
the same parts into three real 3 m bars produced 19/19 placements on every bar.

At the current listed price of GBP 94.92 including VAT per green bar, the GRP
purchase is **GBP 284.76 excluding delivery** in all three cases.  Basket size
changes useful offcut, not the rounded purchase quantity.

## Aluminium plate replacement

The GRP sheet is being screened for replacement by **10 mm EN AW-5083
aluminium plate** supplied in 670 x 460 mm sheets.  The available material's
H temper is presently unknown.  This is a material-and-layout comparison, not
a release to substitute aluminium: obtain the actual EN AW grade, H temper,
thickness and 3.1 certificate before assigning allowable strength, bearing,
fatigue or wet-service behaviour.

The selected 35-part set has a conservative rectangular-envelope total of
**1.2049 m2**: nine 190 x 190 mm uppers, eighteen 40 x 100 mm bridge drawings,
four 380 x 380 mm corner uppers and four 240 x 240 mm lower webs. Five sheets
provide 1.5410 m2. Four provide only 1.2328 m2, or 2.3% more than that envelope
sum before kerf and edge margins, so **five sheets are the minimum purchasing
allowance** unless the cutter demonstrates a valid four-sheet nest from the
exact SVGs.

Ten millimetres should not be assumed necessary merely because it is the
available stock.  Aluminium has a much higher elastic modulus than the GRP
comparison input, so there is plausible scope to thin the replacement plate
and reduce mass and cost.  The minimum thickness must instead be recalculated
from the certified temper and the actual plate layout, including the C2 direct
path, M8/M6 bearing and net section, local basket bearing, complete-joint
stiffness, corrosion detailing and wet proof.  Until that work is complete,
10 mm is the available-stock option, not an approved thickness.

The matching rail candidate is now **38 x 38 x 3.2 mm pultruded GRP hollow
section in place of the 5 mm-wall section**.  The existing gross-member script
already includes this section: it gives `I = 90,668 mm4` and approximately
`J = 134,861 mm4`, about 74% and 75% respectively of the 5 mm-wall values.  It
remains plausible in the stated member screens, including 13.2 MPa and 2.40 mm
at the deliberate 0.30 kN / 840 mm support-loss case.  This is a prototype
substitution, not a connection release.  The thinner wall increases the
calculated two-wall bearing demand at the retained 0.763 kN corner action from
about 9 MPa to about 14 MPa, and its nominal clear cavity is 31.6 mm rather
than 28 mm.  Measure the real cavity, remake the 24 corner crush sleeves to
fit, and repeat the perforated wet-corner proof before batch cutting the rail.

For permanently wet service, the material study must also define compatible
water chemistry, electrical isolation from stainless hardware, sealed and
cleanable faying surfaces, and a representative immersed coupon/complete-joint
test.  Do not credit paint, anodising or sealant alone as the corrosion control
for a damaged or wet fastener interface.

### One part versus split parts

The 670 x 460 mm stock removes the 200 mm pultruded-bar width constraint that
drove the 57-part split arrangement.  The preferred aluminium prototype is
therefore a **35-part monolithic-upper arrangement**:

- nine one-piece upper H seats and the existing eighteen separate lower
  bridges; and
- four one-piece upper corner carriers and the existing four separate lower
  corner webs.

This replaces the eighteen separate upper arms and nine separate upper
bridges with nine H profiles, and replaces eight corner upper halves with four
upper carriers.  It does not change the number of M8 or M6 fasteners, POM-C
seat sleeves, internal corner crush sleeves or separate C2 post stacks.

The selected cutting drawings are the four SVGs linked from
[aluminium-cut-parts.md](../packs/c/aluminium-cut-parts.md): one R5.3 upper,
one seat lower bridge, one corner-v3 upper and one lower corner web. Their SVG
units are millimetres and their paths and holes are the fabrication geometry.

Do not restore the superseded R5.1 and corner-v1 details literally.  Carry the
following current features into the new one-piece cutting profiles:

- the R5.2-derived two capture stations, four M8 axes, 56 mm transverse
  bolt-row span and **40 mm-wide upper and lower paths**;
- four independent M6 basket-retention positions on measured sound basket
  ribs, with at least 16 mm axis-to-edge and preferably the former R20 local
  lands;
- all six corner rail axes at 55, 125 and 195 mm, the complete lower-web load
  path and full rail-contact strips;
- separate C2 posts using the purchased M8 x 50 bolts and nylon spacers, the
  direct C2-to-neighbouring-55 mm paths, and full-size B23/B27 post, washer,
  chafe, knot and removal-clearance templates; and
- accessible drainage, electrical isolation from stainless hardware, sealed
  cleanable interfaces and independent removal.

The one-piece seat is the geometric union of the current two arms and upper
bridge, with generous internal radii.  On the largest 250 mm reinforced-base
screen, changing from three upper parts to this union removes about **3,430
mm2 per seat**, or about **30,900 mm2 across nine seats**, without narrowing a
bearing or bolt land.  The corresponding 10 mm aluminium arm screen at 40 mm
width is only about **6.0 MPa and 0.05 mm** at the deliberately conservative
0.30 kN load.  A 35 mm lower bridge is about **7.2 MPa and 0.006 mm**.  These
elastic results show that plate flexure no longer governs, but they are not a
reason to reduce the 40, 90 or 35 mm widths: real basket bearing, washer
footprints, edge distance, corrosion isolation and handling now set them.

Use a redrawn monolithic upper corner based on the selected thick connected
web, not a full square and not a simple union of the split halves.  The
monolithic plate removes the split pair's plate-to-plate slip path and
one-ply/two-ply basket step.  Retain the named rail, basket and C2 load paths,
then clip only material outside them.  The old 75 mm-wide C2 strip comparison
falls from about 83 MPa at 6 mm 5083 to about **30 MPa at 10 mm** by the same
isolated-strip calculation; nevertheless, do not narrow that path before the
temper is certified and the current C2-post and basket lands have been drawn
and proof tested.

The exact profiles simplify the assembly to 35 parts and remove wet interfaces.
Their conservative 1.2049 m2 rectangular-envelope total, rather than the
earlier conceptual-area estimate, now controls the five-sheet allowance. The
actual non-rectangular profiles may nest more efficiently, but that saving is
not credited until a cutter includes kerf, edge margin and hold-down needs.

The purchased longer M8 bolts may be used at the thinner one-upper-plate
stacks only after measuring an assembled sample.  Shorten threaded excess
after proving that the actual bolt has enough thread within and beyond the
nyloc, that the plain-shank/thread transition does not sit incorrectly in the
nut or a bearing plane, and that the accepted thread cap still fits.  Cutting
the tip of a nominal DIN 931 part-thread bolt does not move its thread
transition toward the head, so the physical purchased bolts and completed
stack--not nominal overall length--decide whether trimming is sufficient.

## Remaining physical gates

Before batch cutting:

1. obtain the aluminium grade, temper, thickness and traceable certificate,
   then confirm the water chemistry and stainless-isolation detail;
2. measure the 3.2 mm-wall rail, its cavity and the completed bolt stacks;
3. overlay the real M8/M6 holes and washers on the new monolithic profiles,
   retaining the stated local lands and current C2/basket clearances;
4. dry-build one monolithic H seat with the actual bolts, POM-C sleeves, lower
   bridges and rail, then repeat the 0.30 kN eccentric/uplift and wet-dwell
   checks;
5. prove one complete monolithic-upper corner with its separate lower web,
   perforated 3.2 mm rail, measured crush sleeves and deliberately unequal C2
   loading; and
6. confirm the assumed square dimension is a continuous reinforced basket-base
   feature rather than a nominal outside or rim dimension, then complete the
   final five-sheet nest before ordering or cutting plate.
