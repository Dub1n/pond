# Pack C rail — materials, purchases and cost position

## Current result

The current complete carrier purchase is **GBP 552.29 including VAT, excluding
delivery**. It covers the GRP ring, all split R5.2/corner-v2 plates, suspension,
connections, thirteen basket attachments and cut-edge resin. Baskets,
cartridges, media, plants, guards and lifting harnesses are outside this total.

The former GBP 498.92 result depended on an assumed GBP 250 custom plate. The
custom sheet's lead time and availability are unacceptable. Three immediately
listed 200 x 9.5 x 3,000 mm GRP flat bars now cost GBP 284.76, and the split
seat stacks need a mixture of M8 x 90 and M8 x 80 bolts. Those two changes add
GBP 36.52. Replacing manually bored solid rod with factory-bored unfilled
POM-C tube for the seats and eight ready-bored nylon C2 posts adds GBP 16.85,
but removes all axial boring from these 44 parts. No goods have been ordered
and delivery remains excluded.

The cost is supported by complete purchase quantities rather than used
fractions of stock. Prices are listing evidence checked on 17 September 2026,
not reservations or delivered quotations.

## Scope and design basis

The priced prototype contains:

- two 6 m lengths of 38 x 38 x 5 mm GRP rail tube;
- four split-plate stiff corners and integrated corner basket seats;
- nine split R5.2 mid-rail seats;
- 36 direct polyester suspension loops/slings;
- thirteen four-point basket-retention sets; and
- edge sealing for all cut and drilled GRP.

The pond is ordinary freshwater with no deliberately added salt. Identified
A2/304 stainless is therefore the cost candidate; A4/316 or branded marine
hardware is not a requirement by itself. Zinc-plated steel, brass and
unidentified coatings are not accepted submerged substitutes.

Labour, ordinary cutting/drilling tools, dust extraction, abrasives, templates,
mixing equipment, PPE, temporary supports, treated timber wrap stops and their
screws are owner-provided and not priced as permanent carrier components.

## Structural GRP

Use three [F.H. Brundle green GRP flat bars](https://www.fhbrundle.co.uk/products/330320095GN__GRP_Flat_Bar_200_x_9.5mm___3M_long_Green),
each 200 x 9.5 x 3,000 mm and GBP 94.92 including VAT. Total purchased area is
1.8 m2 and total listed cost is **GBP 284.76**.

The retained orientation-controlled Deepnest layouts cover:

| Part | Quantity |
| --- | ---: |
| R5.2 upper arms | 18 |
| R5.2 upper bridges | 9 |
| R5.2 lower bridges | 18 |
| Corner-v2 upper halves | 8 |
| Thick lower corner webs | 4 |
| Low corner-basket pads | 4 nominal, cut from layout offcuts |

The three R5.2 basket-base sets have cutting-envelope totals of 1.1080 m2
(250 mm), 1.0698 m2 (225 mm) and 1.0315 m2 (200 mm). All still require three
bars in the demonstrated nests. Occupied lengths leave at least about 750 mm
per bar before ordinary kerf/edge allocation. The 197.48 mm rotated lower web
is the critical width fit and must be checked against the delivered stock.

Use the layouts in `nesting/output/split-flat-bar/` and the reproducible study
in [split-plate-stock-study.md](../../calcs/split-plate-stock-study.md). The
nest allows only 0/180-degree rotations so Deepnest cannot improve utilisation
by putting a directionally loaded part across the pultrusion direction.

### Material evidence

The following is the published E23 column from [GRP Grating Systems' grade
table](https://www.grpgrating.fullfatwebsitedesign.co.uk/grp-thickness-grades.php).
It is a dry comparator, not certification of the F.H. Brundle flat bar and not
a wet-service design resistance.

| Property | Units | Published E23 minimum |
| --- | --- | ---: |
| Full-section modulus | GPa | 23 |
| Tensile strength, axial / transverse | MPa | 240 / 50 |
| Tensile modulus, axial / transverse | GPa | 23 / 7 |
| Flexural strength, axial / transverse | MPa | 240 / 100 |
| Interlaminar shear | MPa | 25 |
| Pin bearing | MPa | 70 |

The current seat comparison uses 8 GPa and the corner comparison uses its own
lower comparative modulus; neither is a literal adoption of this table. Obtain
the selected profile's resin system, fibre directions, thickness tolerance,
wet/immersed suitability and bolted-connection guidance. Wet coupons and the
complete seat/corner tests remain mandatory.

## Complete purchase schedule

| Purchase | Buy quantity and selected specification | Price basis | Budget inc VAT |
| --- | --- | --- | ---: |
| GRP plate stock | 3 x 200 x 9.5 x 3,000 mm green structural flat bar | F.H. Brundle 330320095GN, GBP 94.92 each | GBP 284.76 |
| GRP rail tube | 2 x 6 m, 38 x 38 x 5 mm | [F.H. Brundle 3305385GY](https://www.fhbrundle.co.uk/products/3305385GY__GRP_Hollow_Section_38_x_38_x_5mm_x_6m_Grey), GBP 54.96 each; retained rounded allowance | GBP 110.00 |
| Main suspension cord | 1 x 100 m reel, white 5 mm eight-plait polyester | [RopesDirect](https://www.ropesdirect.co.uk/products/5mm-8-plait-white-polyester-100m-reel), approximate 310 kg breaking load | GBP 32.64 |
| Locating cord | 1 x 100 m reel, 3 mm polyester/PET | [Springfields](https://www.springfields.co.uk/100m-3mm-paracord-black.html); not structural suspension cord | GBP 8.49 |
| Chafe sleeve | 20 m, 25 mm polyester tubular webbing | [Profabrics](https://www.profabrics.co.uk/products/tubular-webbing-25mm), GBP 0.78/m inc | GBP 15.60 |
| Seat and shared-inner-corner bolts | 44 x M8 x 90 A2-70 DIN 931 part-thread | [Vital HH931-M8-90-A2-70](https://www.vital-parts.co.uk/hex-head-bolts-din-931/9335-hh931-m8-90-a2-70), GBP 0.33 each | GBP 14.52 |
| Outer corner bolts | 16 x M8 x 80 A2-70 DIN 931 part-thread | [Vital HH931-M8-80-A2-70](https://www.vital-parts.co.uk/hex-head-bolts-din-931/9317-hh931-m8-80-a2-70), GBP 0.29004 each, line rounded up | GBP 4.65 |
| Separate C2 post bolts | 8 x M8 x 50 A2-70 DIN 931 part-thread | [Vital HH931-M8-50-A2-70](https://www.vital-parts.co.uk/hex-head-bolts-din-931/9297-hh931-m8-50-a2-70) | GBP 1.52 |
| M8 locking nuts | 68 x DIN 985 A2 nyloc | [Vital LN985-M8-A2-70](https://www.vital-parts.co.uk/thin-nyloc-hex-nuts-din-985/14514-ln985-m8-a2-70) | GBP 4.76 |
| Broad M8 washers | 128 x 8.4 ID x 25 OD x 1.5 mm A2 | [Vital WPE-M8-25-A2](https://www.vital-parts.co.uk/stainless-steel-penny-washers/30213-wpe-m8-25-a2), 100+ tier | GBP 7.68 |
| C2 roof washers | 8 x 8.4 ID x 30 OD x 1.5 mm A2 | [Vital WPE-M8-30-A2](https://www.vital-parts.co.uk/stainless-steel-penny-washers/30215-wpe-m8-30-a2) | GBP 0.89 |
| Basket screws | 52 x M6 x 40 A2 socket-button | [The Boathouse](https://www.norfolkwatersports.co.uk/shop/m6-x-40-socket-button-a2-s-s-129), budget includes 20% tax uncertainty | GBP 6.24 |
| Internal basket washers | 52 x M6 x 40 mm OD A2 | [TC Fixings A2WP0640](https://www.tcfixings.co.uk/product/m6-x-40mm-a2-stainless-penny-repair-washers/7433), 50+ tier | GBP 10.64 |
| Basket underside washers | 52 x M6 A2 Form G | [The Boathouse](https://www.norfolkwatersports.co.uk/shop/m6-s-s-a2-washer-form-g-114), tax allowance included | GBP 1.25 |
| Basket locking nuts | 52 x M6 A2 nyloc | [The Boathouse](https://www.norfolkwatersports.co.uk/shop/m6-s-s-a2-nylock-nut-113), tax allowance included | GBP 2.50 |
| Seat-sleeve tube | 2 x 1 m, unfilled natural POM-C tube, 20 OD x 10 ID; form one 1 mm rail-facing flat | [Vision Plastics natural acetal tube](https://visionplastics.co.uk/acetal-natural-colour/natural-acetal-tubes), GBP 9.68/m ex VAT; confirm availability | GBP 23.23 |
| Separate C2 post spacers | 8 x ready-bored nylon spacer, 16 OD x 8.4 ID x 20 mm | [Vital RS-84-160-200-NY-N](https://www.vital-parts.co.uk/nylon-spacers/45551-rs-84-160-200-ny-n), GBP 0.25 each inc VAT | GBP 2.00 |
| Corner crush sleeves | 1 m, 304 tube, 12 OD x 1 mm wall / 10 ID | [S3i](https://www.s3i.co.uk/12mm-stainless-steel-tube-modular.php) | GBP 5.62 |
| Cut-edge resin | 500 g EL2 resin/hardener kit | [Easy Composites](https://www.easycomposites.co.uk/el2-epoxy-laminating-resin), GBP 15.30 inc | GBP 15.30 |
| **Non-GRP-plate and non-rail subtotal** | All rows below rail except plate | | **GBP 157.53** |
| **Complete purchase** | Plate + rail + remaining purchases | | **GBP 552.29** |

The four offcut basket pads, optional plain rubber grip pads and any qualified
structural adhesive are not separate priced purchases. Offcut pads come from
the three paid-for bars. Trial the plain seat clamp first; add an interface
material only if its measured benefit justifies its cost and removal penalty.

## Quantities and duties

| Connection | Installed quantity | Duty |
| --- | ---: | --- |
| M8 x 90 seat bolts | 36 | Join two upper plies and one lower bridge around the rail |
| M8 x 90 shared-inner-corner bolts | 8 | Join two upper plates, rail tube and lower web |
| M8 x 80 outer corner bolts | 16 | Join one upper plate, rail tube and lower web |
| Separate M8 x 50 C2 posts | 8 | Smooth ready-bored nylon cord posts; not corner bolts |
| M8 nylocs | 68 | One per installed M8 bolt |
| 25 mm M8 washers | 128 | 72 seat + 48 corner + 8 C2 underside |
| 30 mm roof washers | 8 | Retain C2 cord above the nylon post |
| Flattened POM-C seat sleeves | 36 | Set clamp gap and retain transverse location with 1 mm rail-facing flat |
| Stainless corner crush sleeves | 24 | Limit rail-wall crushing at six axes per corner |
| M6 basket sets | 52 | Four distributed retention positions per basket |

The 90 mm DIN 931 bolt has 68 mm plain shank. At nominal 9.5 mm plate and a
38 mm rail/gap, the new seat reaches approximately 68 mm to the lower nut-side
washer. The shared corner stack is similar. The measured sealed stack decides
whether the thread transition and nut engagement are acceptable; the complete
batch must use one verified grip rather than nominal arithmetic alone.

## Cord and webbing allocation

The 5 mm reel allowance remains approximately 92.34 m including production,
samples, knots, tails and contingency, leaving 7.66 m. The separate 3 mm reel
is used for rail-wrap locating collars, crossing-sleeve connectors and tags;
it is not a seat stop or load-bearing suspension.

The 20 m webbing purchase allocates approximately:

- 9.00 m to 36 upper timber contacts;
- 3.84 m to 32 straight/crossed lower rail contacts;
- 1.20 m to eight C2 posts at a 150 mm starting allowance; and
- 0.80 m to eight crossing sleeves.

Total planned use is 14.84 m, leaving 5.16 m for samples and replacement.

## Why the selected spending remains justified

- Three stocked flat bars remove the custom-sheet lead-time dependency and
  leave substantial usable offcut, while preserving one material system.
- Known A2 fasteners provide repeatable grip, smooth bearing and inspectable
  corrosion behaviour for little more than unidentified job-lot hardware.
- Four broad basket retainers prevent a few pence of saving from concentrating
  load into one plastic mesh strand.
- Five-millimetre new polyester cord has published approximate strength and a
  larger wear section. Used or unidentified rope would save little while
  making the wet extension and chafe evidence less meaningful.
- Direct cord loops, owner-made sleeves, offcut pads and existing-bolt seat
  clamping avoid commercial marine fittings, cam buckles and separate stops.

The cheaper 4 mm polyester reel would reduce the total by GBP 11.04 if it
passes the same complete-loop proof, settled-extension, knot and chafe tests.
Identifiable unused A2 hardware may replace a listed line when its full count,
grade, grip and condition are known. Adhesive-only corners remain more
expensive than the retained bolts and create additional wet-peel, creep and
repair work.

## Procurement and release conditions

The listing total does not establish fitness. Purchase/fabrication release
still depends on:

- actual flat-bar width, thickness, fibre direction and wet-service evidence;
- sample bolt grips, sleeves, washer lands and sealed cut edges;
- measured B23/B27 basket bases, ribs, cartridge fit and wet/drained masses;
- complete support-cord extension, proof, chafe and knot behaviour;
- full R5.2 seat, corner-v2 and basket-retention tests; and
- flexible-ring and deck calculations using measured geometry and reactions.

See [install-walkthrough.md](install-walkthrough.md) for every construction,
assembly, installation and test procedure. This document is the sole active
Pack C material and purchasing schedule.
