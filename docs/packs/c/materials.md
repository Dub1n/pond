# Pack C rail, corner and seat material schedule

## Status and scope

This is the live procurement and cutting schedule for nine dedicated R5.1 seats
and four `t=30 mm` integrated corner-seat pods. Together they support the
thirteen permanent rail baskets. It supersedes the former thirteen-R5.1-seat
plate take-off in [R5.1.md](R5.1.md) and the corresponding plate rows in
[rail-development-status.md](rail-development-status.md).

It is a purchasing and proof-planning schedule, **not fabrication approval**.
The plate material, bolt grips, C2 post stack, basket bearing, wet corrosion
behaviour and full rail/deck reactions remain release gates.

## Current arrangement

| Position | Quantity | Component | Material route now being priced |
| --- | ---: | --- | --- |
| Straight rail stations | 9 | R5.1 open H cradle: one upper H and two lower bridges | 5 mm EN AW-5083/H111 plate, or common-thickness structural GRP if the one-sheet route is quoted |
| Each rail corner | 4 | Selected `clam.14.3_thick` upper web, two C2 post axes and four basket-retention axes | 9.5 mm certified structural-GRP, or 6 mm EN AW-5083/H111 after the revised proof; 5 mm 5083 is not screened |
| Each rail corner | 4 | Selected `corner-web_thick` lower web and six M8 rail/corner bolts | Same certified 9.5 mm structural-GRP sheet as the upper part; the former 200 mm flat-bar route is superseded by this larger profile |

The four corner pods replace four ordinary R5.1 seats; they are not extra
seats. Do not fit an R5.1 H at a corner. See [corner.md](corner.md) for the
corner geometry and proof gates.

## Component cut sizes

All plan dimensions are millimetres. The stock layouts retain at least 5 mm to
a sheet edge and between separately cut outlines. Round, deburr and seal all
exposed plate edges and holes before service.

| Component | Quantity | Finished / template geometry | Plate route |
| --- | ---: | --- | --- |
| Dedicated R5.1 upper H | 9 | 250 x 250 maximum blank; two 50 mm bearing arms, 90 mm central strip, 25 mm internal radii and two 30 x 7 strap slots | 5 mm 5083, pending revised local checks |
| Dedicated R5.1 lower bridge | 18 | 50 x 110 | Same 5 mm 5083 as its upper H; one bridge in each H cut-out |
| `t=30 mm` upper corner pod | 4 | **Selected:** `clam.14.3_thick`, 71,304 mm2, 407.8 x 407.8 mm cutter-profile bounding box. | 9.5 mm certified structural-GRP, or 6 mm 5083 pending pod/post proof |
| Selected lower corner web | 4 | `corner-web_thick`, 43,506 mm2, 282.8 x 282.8 mm cutter-profile bounding box. | 9.5 mm structural GRP only |

Each H contains two 150 x 80 openings. A 110 x 50 bridge fits in each opening
with at least 15 mm clearance, so the 18 bridges need no separate plate area.
The 250 mm H envelope is still a measured-basket template allowance, not a
released production outline.

## Plate layouts and quote sizes

### Lowest material-area split purchase

This is the lowest guaranteed rectangular take-off, excluding the GRP lower
corner webs:

| Blank | Contents | Minimum cut blank | Area |
| --- | --- | ---: | ---: |
| A | Nine upper Hs plus 18 bridges nested in their openings | 770 x 770 | 0.5929 m2 |
| B | Four pods, each aligned to its diagonal minimum rectangle in a 2 x 2 layout | 573.7 x 750.4 | 0.4304 m2 |
| **Total** | 9 Hs, 18 bridges and 4 pods | two-piece purchase | **1.0233 m2** |

For a quote, request **770 x 770 mm** and **575 x 755 mm** 5 mm 5083 blanks,
or ask the cutter to nest the supplied profiles directly. The rounded purchase
sizes total 1.026 m2.

### One-piece square purchase

A square with a 3 x 3 H grid in one corner, two pod envelopes in the
right-hand strip and two rotated pod envelopes in the bottom strip needs a
minimum side of **1054.4 mm**. Request **1055 x 1055 mm** as the mathematical
minimum, or **1060 x 1060 mm** to carry a small supplier/cutting tolerance.

| One-piece stock | Contents | Area |
| --- | --- | ---: |
| 1055 x 1055 mm | 9 Hs, 18 nested bridges and 4 pods | 1.1130 m2 |
| 1060 x 1060 mm | Same, with 5.6 mm additional overall margin | 1.1236 m2 |

The square layout is a guaranteed rectangular-envelope layout, not proof that
a laser-cut polygon nesting cannot save a little more. It is the correct
single-piece quote basis.

### Custom structural-GRP one-sheet purchase

If a supplier can provide a custom structural-GRP sheet at variable length and
width, include the four lower compact webs with the nine upper Hs and four
upper corner pods. This only makes sense if the whole sheet is specified to the
governing structural-GRP requirement for the lower corner webs, currently the
9.5 mm compact-web screen or a supplier-approved equivalent; do not infer that
a thinner generic GRP sheet is acceptable from the 5 mm 5083 plate screen.

The renewed Deepnest CLI contact-nest uses all 35 selected profiles: nine Hs,
18 bridges, four `clam.14.3_thick` upper webs and four
`corner-web_thick` lower webs.  With the sheet height constrained to 1,000 mm,
the best successful horizontal-minimisation screen occupies approximately
**1,491 x 1,000 mm** (about **1.491 m2**).  It is a conservative outer-contour
contact nest: internal water-flow cut-outs are not used as nesting voids, and
it is not a cutting layout.  Allow 5 mm at every sheet edge and between
separately cut outlines, plus kerf and cutter allowance; request approximately
**1,505 x 1,015 mm** (1.528 m2) for a first structural-GRP quote.  The cutter
must independently apply those clearances, laminate-direction constraints and
final hole/radius rules to the supplied profiles.

This is a best successful fixed-height contact screen, not a global optimum:
the fork is heuristic and can fail during later optimisation.  The preserved
result is [`nesting/output/thick-grp-1000-high.svg`](nesting/output/thick-grp-1000-high.svg),
with placements in the adjacent JSON file.

The reproducible profile and job files are in [`nesting/`](nesting/). Regenerate
them with `./.venv/bin/python docs/packs/c/nesting/generate_profiles.py`.

## Material options and current listings

| Route | Use / decision | Current source and price evidence | Limits |
| --- | --- | --- | --- |
| **5 mm EN AW-5083/H111 aluminium** | Current low-cost route for the nine dedicated R5.1 seat plates; it is not screened for the connected corner upper web. | [Hawkshead 5 mm 5083 laser-cut plate](https://hawksheadmetal.co.uk/metal-sheet-steel-sheet/aluminium/aluminium-sheet-and-plate/5mm-aluminium-5083-sheet-plate-profiles-blanks-custom-cut-to-size-free-of-charge-enter-exact-dimension-for-pricing/) lists BS EN 573-3:2019 5083, profile cutting and a displayed price from GBP 22.17. That is not the price of these blanks; obtain a nested-cut quotation. | Fully submerged salty/fertilised water still requires rounded edges, no water traps, compatible finish and a coupon/assembly test. Keep A4 stainless isolated at wet fasteners with shoulder bushes and insulating washers. |
| 6 mm EN AW-5083/H111 aluminium | Minimum metal candidate for the connected corner upper web; the 5 mm proof-strip comparison is at its minimum-proof limit. | [Aluminium Warehouse 6 mm 5083](https://www.aluminiumwarehouse.co.uk/products/6-mm-5083-aluminium-plate) is cut to size and lists 72 GPa modulus, 270--345 MPa tensile strength and 125 MPa minimum proof stress; its displayed GBP 2.36 is a starting price, not the finished sheet price. | More weight/cost and every bolt grip, sleeve and bearing datum must change; still require the pod/C2 coupon and full corner proof. |
| Common-thickness structural-GRP sheet | Quote as the one-sheet alternative for nine Hs, eighteen nested bridges, four selected thick upper pods and four selected thick lower webs. | No current listing. Use the renewed SVG job and **1180 x 1575 mm** provisional envelope, including the stated 5 mm nominal clearances. | The sheet must satisfy the lower-web duty as well as the H/pod bearing duty. If pultruded or directionally stronger, pair orientations deliberately and obtain supplier approval for both rail-leg and diagonal load paths. |
| 9.5 mm structural-GRP flat bar | **Not suitable for the selected thick lower profile**: the 200 mm stock width is below its 282.8 mm bounding profile. | [F.H. Brundle 200 x 9.5 x 3,000 mm GRP flat bar](https://www.fhbrundle.co.uk/products/330320095GY__GRP_Flat_Bar_200_x_9.5mm___3M_long_Grey): GBP 95.04 inc VAT, retained as historical comparison only. | Do not substitute it unless a separately verified recut/profile is approved. |
| 6082-T6 aluminium | **Rejected for the permanently submerged saline/fertilised location.** | Earlier cut-to-size listing retained only as historical comparison. | Good general corrosion resistance is not the required seawater/chemical-service basis; do not order it for these parts. |
| Marine plywood / generic GRP flooring / UHMWPE | **Not selected.** | No procurement basis in this schedule. | Plywood needs a separate encapsulated-composite design; generic flooring may lack directional joint data; UHMWPE creeps and is not structural plate stock. |

Compare actual delivered quotes on a like-for-like basis: one 1055/1060 mm
square, two small rectangular blanks, the provisional 1180 x 1575 mm structural-GRP
one-sheet route, and a direct laser-cut nest.

## Hardware quantities affected by the nine-seat change

| Item | Nine dedicated R5.1 seats | Four corner pods | Total rail baskets |
| --- | ---: | ---: | ---: |
| Basket retention: M6 x 40 A4 screws, internal penny washers, underside washers, nuts and caps | 36 each | 16 each | 52 each |
| R5.1 M8 capture bolts, locknuts, caps and bored sleeves | 36 each | — | 36 each |
| R5.1 broad M8 washers | 72 | — | 72 |
| R5.1 cam-buckle strap stops and chafe sleeves | 18 each | — | 18 each |
| Corner rail/corner M8 bolts | — | 24 | 24 |
| C2 lower post stacks | — | 8 | 8 |

The corner-pod M6 retention axes are separate from the six M8 rail/corner
bolts. C2 post elevations and their final stack are explicitly provisional;
do not buy final post spacers from nominal YAML elevations.

## Required quote and proof sequence

1. Ask for a 5 mm 5083/H111 quote for the two split blanks and for a 1055 x
   1055 mm square, and ask for a common-thickness structural-GRP quote for the
   1180 x 1575 mm one-sheet layout including the selected lower webs.
2. Obtain the plate certificate, temper, thickness tolerance and explicit
   immersed saline/fertiliser service statement.
3. Cut one complete R5.1 H/bridge stack and one full corner pod first.
4. Prove wet corrosion, washer bearing, bolt preload, strap-slot and pod/C2
   post behaviour before cutting the remaining stock.
5. Re-run the t=30 C2/ring/deck load model and update bolt lengths, sleeves,
   isolators and the rail drawing from measured stacks.

Until those steps pass, this schedule is an economical procurement screen, not
permission for batch fabrication.
