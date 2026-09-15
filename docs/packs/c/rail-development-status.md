# Pack C rail development - current state and next work

This is the active handoff for the submerged planting carrier as at
12 September 2026. It records one low-cost prototype architecture. Earlier
R3, R4, R5 and lower-H alternatives are development history, not parallel
construction instructions.

Nothing in this document is approval to load the deck or batch-fabricate the
carrier.

> **Corner status — under development.** The integrated corner/basket bracket,
> its C2 attachment points and its basket retainers are being redesigned. Do
> not assume that the corner dimensions, C2 lower points or basket interface
> summarised in this status handoff are current. Use [corner.md](corner.md) for
> the live study and its prototype gates; this document deliberately retains
> the older summary pending that work.

## Current decision

Proceed to measured samples and dry-ground prototypes using:

- a 2,100 x 2,100 mm connected ring of 38 x 38 x 5 mm structural-GRP SHS;
- the paired 9.5 mm compact triangular-web joints in [corner.md](corner.md);
- 36 direct polyester cord loops and slings in [cords.md](cords.md), without
  proprietary suspension fittings;
- the open H-cradle seats in [R5.1.md](R5.1.md); and
- permanent B23/B28 rigid baskets containing independently removable planted
  cartridges, as specified in [plants-v2.md](plants-v2.md).

Retain the stiff corners. Their frame action substantially reduces outward
bending of each rail side under inclined support reactions. The principal
simplification is instead the suspension: cord bears directly around timber
and GRP, protected by replaceable chafe sleeves and located by cheap stops or
lashings. Temporary supports establish the exact ring height while permanent
knots are dressed and marked.

Only the direct-loop suspension method is active.

## Read and use in this order

For the current hands-on sequence and seat clamp, start with
[install-walkthrough.md](install-walkthrough.md), then consult these references.

1. [design-C.md](design-C.md) - as-built deck interface and five still-TBC
   allowable reaction limits.
2. [corner.md](corner.md) - stiff joint, two-point corner sling and release
   gates.
3. [cords.md](cords.md) - direct loops, upper-face stops, knots, chafe and
   installation sequence.
4. [R5.1.md](R5.1.md) - seat, clamped movement stop, reference alternatives and basket
   attachment.
5. [plants-v2.md](plants-v2.md) - cartridges, guards, depth variants, planting
   and removal sequence.
6. [rail-support-study.md](../../calcs/rail-support-study.md) and
   [ring-corner-study.md](../../calcs/ring-corner-study.md) - calculation
   method, superseded-coordinate results and required reruns.

Do not create a detailed production YAML until the measured basket templates,
actual cord-wrap tangents and prototype corner curve are available.

## Integrated arrangement

Use pond centre `X=Y=0`, minimum-water/pad datum `Z=0` and ring centrelines at
`X/Y=+/-1050`.

### Suspension

The selected low-cost prototype has 36 independent cord items:

- 24 direct gravity loops at straight joists J2-J7, six per side;
- 8 crossed loops, `U2 -> L3` and `U3 -> L2` on each side; and
- 4 continuous C2 corner slings, each dividing into two lower legs attached
  at the existing `(55,0)` and `(0,55)` corner-bolt axes.

Each straight or crossed item is a closed loop with two adjacent load-bearing
legs. It wraps around the joist and beneath the rail. Two small replaceable
lashing collars locate each lower wrap along the rail. A treated timber stop
on the accessible joist upper face keeps the upper wrap from walking toward
the free end without carrying its vertical load.

The exact upper wrap stations remain a measured design input. Put each wrap as
near the pond-facing end as practical to limit outward horizontal force, while
leaving adequate sound timber for the upper-face stop and its screws. Use the
real cord/chafe tangent and relieved removable-deck-board template, then rerun
the support calculation. Provisional model coordinates are not cord-cutting
dimensions.

At each C2 corner, the midpoint of one continuous cord wraps around the timber
and one end descends to each of Arrangement E's two separate ear posts.
These are eight additional post bolts, not eight of the 24 rail/corner bolts.
The current purchase candidate uses smooth acetal-covered posts; see
[purchase-cost-study.md](purchase-cost-study.md). Model both sling legs and
treat loss of the continuous sling as one fault.

### Corner

Each rail corner retains:

- one top and one bottom 9.5 mm structural-GRP flat-bar web;
- the six-sided compact triangular-web outline with 220 mm reach and 80 mm
  strips at the bolt zones;
- three M8 axes on each leg at 55, 125 and 195 mm;
- close 8.2-8.5 mm stack holes; and
- one measured internal compression sleeve at every bolt; 304 tube is the
  current freshwater purchase candidate.

The paired-strip estimate remains 33.2 kN m/rad before connection compliance.
The assembled wet joint must demonstrate at least 20 kN m/rad from 0 to
60 N m after bedding. The 60 N m plan and 30 N m roll combination gives the
existing conservative 0.763 kN bolt/plate force screen. Add the measured
two-legged sling actions to the prototype test rather than assuming the former
single central force line.

### Seats and baskets

R5.1 retains one upper H and two 50 x 110 lower bridges around the rail. The
active plate material/thickness route is in [materials.md](materials.md). Four
M8 sleeved bolts form two spaced capture stations. Bearing-arm
spacing and projection transfer from the sound base bands on the purchased
basket.

Longitudinal restraint now uses the existing four bolts and H/lower bridges
as a gentle clamp, with sleeves matched to the measured stack. A broad grippy
pad or suitable adhesive between H and rail is optional. Retain all mechanical
capture parts; do not cut seat-lashing slots/grooves. The same 0.10 kN wet
slide test applies, including empty and loaded states. See the fitting and
installation procedure in [install-walkthrough.md](install-walkthrough.md).

Four internal broad stainless washers and M6 button-head screws retain each empty
rigid basket at tested sound rib intersections. The planted bag, harness and
fish guard remain a removable cartridge and carry no seat load.

## Calculation status

The provisional rigid-ring screen with 24 gravity supports, four corner
supports and one opposite-handed crossed pair per side achieves rank 6, finds
feasible equilibrium with each complete cord item unavailable, and gives about
5.02 mm maximum translation in the listed cases at the current provisional
wrap coordinates. That establishes the 36-item topology as a reasonable
prototype minimum, but does **not** validate the new wraps:

- a direct closed loop has two nearby physical legs represented by one
  equivalent model line;
- each corner now has two separated lower legs rather than one central line;
- the upper force lines move to surveyed tangents around the joists; and
- a continuous corner sling loses both legs in one fault.

Update the calculation with the measured gravity, crossed and C2 wrap
coordinates before fixing cord lengths or issuing deck reactions. Continue to
use a 0.30 kN proof for each complete support item over dry ground. This is a
connection proof, not spare deck capacity.

The 5 mm SHS remains plausible in gross vertical bending and torsion. A pinned
side is provisionally estimated to breathe about 13.9 mm versus about 2.8 mm
with fixed ends, so measured corner stiffness, joint slip and flexible-ring
redistribution remain release gates.

## Simplicity and cost position

The direct-loop suspension should require only polyester cord, chafe sleeves,
small timber stops and screws, locating cord, eight simple corner-post spacers
and washers, tags and consumables. On an order-of-magnitude basis this is a
low-hundreds suspension rather than a multi-thousand-pound one.

The current purchase-led study is
[purchase-cost-study.md](purchase-cost-study.md): **GBP 498.92 including VAT,
excluding delivery**, using the owner's **GBP 250 plate assumption + GBP 110
rail allowance**. All remaining purchases total **GBP 138.92**. The plate
quote is pending; this is a complete priced prototype candidate, not an
approved build or reserved checkout price.

The owner confirms ordinary freshwater, **no added salt**. Use A2-70/A2
stainless and 304 tube as the lower-cost candidates, 5 mm polyester main cord,
stock acetal sleeves/posts and existing-bolt seat clamping. Optional pads or
adhesive are not included in the original price. Keep all 52 bought
40 mm basket washers. The study supplies selected product links, purchase
quantities, VAT rounding, full cord/stock allocations and the necessary
fit/wet/stiffness tests. The earlier 6 mm / 6 kN cord, blanket A4-80 hardware,
shared corner-post bolts and bought cam buckles are not minimum requirements.

### Superseded complete-carrier budget screen

This inclusive-VAT screen assumes self-cut/drilled GRP and user-bored acetal
seat sleeves; it includes normal retail delivery and waste but no paid
fabrication labour. Upper wrap-stop timber and screws, abrasives, drills and
templates are user-provided and therefore costed at zero.
It includes the rail, all four stiff corners, nine dedicated R5.1 seats and
four integrated corner pods, the 36-item
suspension, seat movement stops and the 52-point basket-to-seat retention set.
It excludes the rigid baskets, cartridges, planting bags, media, plants, guards
and harnesses.

| Cost group | Included basis | Working allowance |
| --- | --- | ---: |
| Main rail tube | two 6 m lengths of 38 x 38 x 5 mm GRP at [GBP 54.96 each](https://www.fhbrundle.co.uk/products/3305385GY__GRP_Hollow_Section_38_x_38_x_5mm_x_6m_Grey) | GBP 110 |
| Plate stock | four lower compact corner webs, plus quoted 5 mm 5083 plate for 9 H members, 18 lower bridges and 4 corner pods | TBC; see [materials.md](materials.md) |
| Main suspension cord | measured direct loops/slings and spares; provisional allowance up to one reel | GBP 120-160 |
| Suspension small parts | 76 chafe locations, locating cord, crossing sleeves, separators and tags | GBP 50-90 |
| Four-corner hardware | 24 sleeved M8 corner bolts, broad washers, locknuts, caps and eight cord posts | GBP 120-180 |
| Nine-seat capture hardware | 36 M8 bolts, 72 broad washers, locknuts, caps and 36 bored POM-C sleeves; two [1.5 m lengths of 16 mm acetal rod](https://www.directplastics.co.uk/acetal-black-rod-16mm-dia-x-1500mm) cost GBP 12.10 inc VAT | GBP 70-100 |
| Basket-to-seat retention | 52 M6 x 40 A4 button screws, 52 internal 40 mm A4 penny washers, underside washers, locknuts and caps; screws are [GBP 0.25 each](https://www.vital-parts.co.uk/hex-socket-button-screws-iso-7380-1/7129-hbs73801-m6-40-a4) and penny washers [GBP 0.25 each](https://www.gsproducts.co.uk/6mm-stainless-steel-penny-washer/) | GBP 50-70 |
| Seat movement stops | 18 endless polyester cam straps plus webbing chafe; quantity price is [GBP 2.69 each ex VAT](https://www.ukratchetstraps.com/products/25mm-wide-cambuckle-strap-ls25-4-5m) | GBP 70-90 |
| Cut-edge resin | one [500 g EL2 epoxy kit](https://www.easycomposites.co.uk/el2-epoxy-laminating-resin) at GBP 12.75 ex VAT / GBP 15.30 inc VAT; use only if compatible with the purchased GRP supplier's sealing guidance | GBP 15.30 |
| Delivery, order rounding and waste | several ordinary UK retail orders | GBP 150-250 |
| **Current self-fabricated cash total** | requires 5083 plate and revised hardware quotes | **TBC** |

Do not carry the former GBP 1,600 working target forward: the submerged 5083
plate quotation, revised plate stacks and corner-pod hardware have not yet
been priced. The current stock and quote basis is [materials.md](materials.md).

### Superseded structural-GRP stock take-off

This is retained as history only. The active plate take-off is in
[materials.md](materials.md); it replaces the former thirteen-H GRP sheet with
5 mm 5083 for nine Hs, eighteen bridges and four corner pods.

This historical allowance is not a supplier sheet-size recommendation.
It uses at least 5 mm clear material between separately cut parts and assumes
the 8 mm upper H is a 250 x 250 mm square with two 50 mm-wide arms and a
90 mm central strip. Confirm the final H outline against the measured B23/B28
bearing bands before ordering material.

| GRP stock and parts | Net finished laminate | Compact rectangular cutting envelope | Practical layout |
| --- | ---: | ---: | --- |
| 9.5 mm: four lower compact triangular corner webs | 0.1928 m2 | TBC | The former eight-web flat-bar take-off included the now-integrated upper webs. Use the current SVG nest in [materials.md](materials.md) for the common-sheet option. |
| 8 mm: thirteen 250 mm square upper Hs and 26 lower bridges | 0.6435 m2 | 0.9652 m2 | Superseded by the nine-H / four-pod 5083 take-off in [materials.md](materials.md). |

One compact corner web has polygon area 48,200 mm2. One assumed H has 38,500 mm2 of
finished laminate; the 26 bridges add 143,000 mm2. A rotated 110 x 50 mm bridge
fits inside each 150 x 80 mm H cut-out with at least 15 mm clearance to the
surrounding H material, exceeding the 5 mm cutting allowance. Add the selected
supplier's outer-edge trim, saw/router kerf and any minimum-order offcut before
placing an order.

If the GRP shapes, acetal seat sleeves and stainless corner sleeves/posts are
outsourced rather than made by the user, carry roughly **GBP 2,500-3,400**
until written machining quotes replace that allowance. The basket-retention
row is the sole cost taken from `plants-v2.md` and is counted once, within the
9-seat plus 4-corner-pod system.

The present costed candidate retains the 5 mm tube wall, stiff corners, two
seat capture stations, two seat-stop locations and four basket-retention
points. These are the evaluated route, not a ban on alternatives: any further
change should demonstrate the required function and a lower complete purchase
cost, including the rework it introduces.

## Purchase sequence

### First purchase - samples only

- one B23, one B28, one PB18 and one PB25;
- a sample of the quoted common structural-GRP sheet and the
  38 x 38 x 5 mm tube, with available wet-service information;
- enough selected A2 hardware and sleeves for one corner and one R5.1 seat;
- one useful sample length of the 5 mm polyester purchase candidate;
- sample chafe sleeve, 3 mm locating/stop cord, owner-provided timber and screws;
- two smooth corner cord-post spacers and retaining washers; and
- the sample basket-retention washers and fitted seat clamp, with any selected
  pad or adhesive and its separate cost allowance.

### Prototype purchase

Only after the sample fits, buy material for one full side, one complete
corner sling, representative seats and a real relieved deck-edge mock-up. Make
the gravity, crossed and corner cutting samples before ordering the batch cord
length.

### Batch purchase

Only after all release gates, use the reconciled purchase table in
`purchase-cost-study.md` with the functional details in `corner.md`,
`cords.md` and `R5.1.md`. It covers four stiff corners, 36 cord items,
9 dedicated seats, 4 corner pods and 13 permanent basket attachments. Transfer measured sample
dimensions instead of reconstructing the order from nominal sizes.

## Build and test sequence

1. Survey all joist tips and upper faces, C2 connections, liner, water levels,
   deck edge and post-deck access.
2. Measure the B23/B28 bearing bands, base ribs, taper and wet removal envelope.
   Make the full-size basket-position sheet.
3. Prototype one gravity loop, one crossed pair and one two-legged C2 sling.
   Establish knot, tail, chafe, collar, stop and cord-post details.
4. Update the suspension calculation with their actual tangent coordinates and
   issue the resulting deck reactions.
5. Build and wet-test one complete stiff corner, including clearance dead band,
   plan stiffness, roll, sling load and combined cycles.
6. Build the representative full side with all selected loops, one corner,
   representative seats and the real relieved deck-board mock-up.
7. Hold the ring at its exact height on temporary supports, dress and mark all
   knots, then remove the temporary support gradually while checking level and
   sharing.
8. Proof each complete cord item at 0.30 kN dry, then repeat system cases after
   soaking, with the calculated worst support absent and one corner ineffective.
9. Test the seats, basket attachments, movement stops and all removal paths.
10. Accept the deck reaction limits and post-deck access before batch work.

Use temporary control lines when lowering. Cut or drill GRP over dry ground
with dust extraction; round and resin-seal every cut. The freshwater purchase
candidate uses identified A2/304 stainless, with A4/316 retained as an
alternative if actual water conditions require it. All hollow members have
deliberate drainage/vent routes, and
fish or liner may touch no exposed fibre, burr or projecting thread.

## Release gates and residual risk

Batch fabrication requires:

- purchased-material information and measured seat/basket dimensions;
- passed direct-loop knot, chafe, collar, upper-stop and wet-dwell tests;
- passed two-legged corner-sling test, including unequal sharing and whole-
  sling loss;
- passed corner stiffness, dead-band, combined and proof tests;
- passed seat, basket-retention, movement-stop and maintenance trials;
- flexible-ring results using measured wrap coordinates and joint behaviour;
- accepted deck reaction limits; and
- an inspection/replacement plan keeping every upper knot and stop accessible.

If the corner does not retain 20 kN m/rad after bedding, locate whether the
compliance is bolt clearance, tube-wall bearing, plate bending, mitre bedding
or rail torsion before changing the corner geometry.
