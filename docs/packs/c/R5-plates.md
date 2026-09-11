# R5 — Plates

## Design status and scope

R5 keeps the suspended single-spine ring from [R3-rail.md](R3-rail.md) and
replaces each basket's two separate crossbars with **two square GRP plates,
one above and one below the spine**. This is the working plate-seat concept
for iteration. Start with one basket and accept the local detail by a simple
loaded trial before repeating it.

[r5-plates.yaml](../../../diagrams/specs/rail/r5-plates.yaml) and
[r5](../../../diagrams/output/r5-plates/r5/) shows the complete
ring, representative joist attachments and one B28 plate seat. The dimensions
below are a coherent starting example. Basket bases, plate grade and connection
fit still need measuring; the model is not a certified fabrication drawing.

## Arrangement and load path

The upper square plate is the basket's bearing surface. Its middle rests on
the flat top of the 38 mm square spine. The lower square plate lies beneath
the spine and prevents the seat lifting away. Four vertical bolts join the
plates **beside the spine, never through it**: two at each side, separated
along the rail. This four-bolt arrangement resists yaw better than one bolt
on each side at a single cross-section.

Fit a smooth rigid spacer sleeve around each bolt between the plates. A sleeve
is a short tube through which the bolt passes. The sleeves sit immediately
beside the rail faces and serve as the lateral stops. They also set the plate
spacing, so tightening the nuts does not bend the plates down onto the hollow
rail. These four small sleeves are the only addition to the proposed
plates/bolts/cord arrangement.

The basket load passes through the upper plate into the spine. Eccentric load
can bring the lower plate into bearing against the rail underside and load
the bolts. The four sleeves limit sideways movement and yaw. Two cord collars
around the spine, one immediately beyond each longitudinal plate edge, limit
travel along the rail. Basket ties prevent the basket leaving the upper plate.

The seat captures the square rail; it does **not** stop the entire spine or
ring rotating. Retain R3's ring, corner joints and distributed joist supports.
Cord collars remain friction-based stops and need a simple movement test.

## Plate and basket dimensions

Use **6 mm structural GRP plate with documented properties in both in-plane
directions** for the first trial. This is a starting thickness, not a plate
capacity established by the R3 tube-bending calculation.

Measure the basket's loaded base and its widening sides near the base. Size
both plates to cover that base and leave the fasteners outside it. For a square
basket, start with a plate side of the larger of the rim width or **base width

+ 80 mm**, rounded up to 10 mm. Keep the upper nuts and washers clear of the
tapered basket; enlarge the plate/bolt margin if the real basket needs it.

| Dimension                      |                               Illustrated B28 example |
| ------------------------------ | ----------------------------------------------------: |
| Basket rim / height            |                                 280 × 280 mm / 190 mm |
| Basket base                    |              200 × 200 mm, **assumed until measured** |
| Upper and lower plates         |                                 280 × 280 × 6 mm each |
| Bolt stations along the rail   |       120 mm each side of basket centre; 240 mm apart |
| Sleeve outside diameter        |                 Nominal 12 mm, smooth; bore clears M6 |
| Sleeve centres across the rail |                   26 mm either side of its centreline |
| Side clearance                 |          1 mm between sleeve and each 38 mm rail face |
| Clear distance between plates  |              39 mm: measured 38 mm rail height + 1 mm |
| Plate edge to bolt centre      |         20 mm along the rail, before rounding corners |
| Washers                        | Nominal 24 mm outside diameter, broad A4 flat washers |

These dimensions leave the fastener centres 20 mm beyond the assumed base
edge. Check the whole washer/nut/thread envelope against the real basket,
including when the basket slides pondward during removal. Keep plate corners
rounded without cutting into the washer bearing area. Use close clearance
holes according to the plate supplier; do not enlarge them to obtain the
rail clearance, which comes from the sleeve position and length.

The 1 mm clearances are fitting allowances, not a demand for 1 mm accuracy in
the basket or plate outline. Fit to a sample of the actual tube. Excessive
clearance introduces rocking; zero clearance can jam or pinch the rail.

## Fasteners and assembly

For one seat, start with **four M6 × 70 mm A4/316 through-bolts, eight broad
flat washers, four A4 all-metal locking nuts and smooth thread caps**. Confirm
length against the actual stack: two 6 mm plates + 39 mm space = 51 mm before
washers, nut and thread projection. Use four 39 mm rigid A4/316 or suitable
structural GRP sleeves; protect their fish-facing edges. Sleeve wall/bore and
plate bearing need to suit the selected fastener and tightening load.

1. Cut two equal squares; round their edges. Clamp them together to drill the
   four matching holes, then deburr and resin-seal every exposed fibre.
2. Put the upper plate over the spine and offer the lower plate underneath.
   Insert the four sleeved bolts from below, with a washer under each head.
3. Fit the upper washers and locking nuts. Tighten against the sleeves using
   the selected plate/fastener guidance. Do not keep tightening to grip the
   rail or remove its deliberate running clearance.
4. Cap the exposed upper threads. Check that the basket base sits on GRP,
   clear of the hardware, and that the lower plate catches uplift without
   unacceptable rocking.
5. Wrap and secure a tight replaceable 3–4 mm polyester collar around the
   spine immediately outside each longitudinal plate edge. Build up enough
   cord that the plate cannot ride over it during the movement test. The YAML
   represents each multi-turn collar as an 8 mm square-edged band; that is an
   envelope, not an instruction to buy 8 mm cord.
6. Tie the basket down at four sound lower reinforced mesh positions through
   smooth, resin-sealed perimeter tie holes in the upper plate. The diagram
   shows the four tie locations; knots, hole bores and mesh cells are omitted.

No structural adhesive or sealant is needed for this seat. Gold Label remains
an optional external protective fillet as described in R3, with no structural
credit. Do not glue the removable sleeve/rail interface shut.

The [Strongwell fabrication manual, bolted connections](https://www.strongwell.com/wp-content/uploads/2024/10/Strongwell-Fabrication-and-Repair-Manual.pdf)
supports using flat washers on both sides and controlling local stress around
bolts. It does not validate this particular plate thickness or sleeve detail.

## Water movement and finish

Do not turn the upper plate into a watertight tray. Provide smooth drainage
holes in the areas outside the rail-bearing strip and away from the bolt,
washer and basket-bearing bands. Choose their positions after marking the
real basket base; the YAML leaves them uncut so it does not invent a drill
pattern through a structural bearing zone. Clean beneath the basket during
lifting and confirm free drainage with the plate level in the test tub.

Both plates are flat with open edges. The gap between them remains open beside
the spine. Keep the main ring's deliberate upper vents and lower drains;
closed mitres must not be relied upon to leak. Round and resin-seal all GRP,
cap threads and leave no sharp sleeve edges or loose fibres accessible to fish.

## Vertical arrangement and planting

Set the **upper plate top** from the required basket bearing level:

```text
B28 bearing depth = measured basket height + 10 mm rim cover
spine top depth = B28 bearing depth + upper plate thickness
```

For the example this gives bearing depth **200 mm** and spine-top depth
**206 mm**, compared with R3's 225 mm. Thus R5 raises the main rail 19 mm while
preserving the basket elevation. With the Option C water surface at Z = 0,
level with pad tops and beam undersides, plate top is −200, rail top −206,
rail bottom −244, lower plate top −245 and lower plate bottom −251 mm.

If reusing a ring already fixed at the R3 elevation, the same plate seat puts
the basket 19 mm deeper. Either adjust the cord supports or explicitly accept
that different bearing level in the plant schedule; do not hide it in packing.

Shallow B23 baskets need measured local risers on the upper plate (nominally
40 mm for a 150 mm basket). A *Butomus* internal pot and crowfoot downstand
remain separate depth details controlled by [plants.md](plants.md). Only a
shallow B28 is modelled in this iteration.

## Joist supports, ring and removal

Retain the 2,100 mm centreline square, 450 mm from every pond wall, in
38 × 38 × 5 mm GRP. Use R3's 32 adjustable polyester supports, mitred and
bolted GRP-plated corners, chafe protection and accessible upper terminations.
Keep plate seats outside corner-plate zones and clear of support wraps.

To service a basket, undo its four ties, slide it pondward clear of the
finished deck, then lift. The plate pair stays on the rail. To service the
plate pair, remove the basket, undo the four bolts and separate the plates
above and below the rail; no ring corner needs dismantling. Renew the cord
collars at the same time if worn. Prove the slide with the actual upper nuts
and caps fitted: the nominal rim needs more than 40 mm travel including
handling clearance.

## Component allowance and simple trial

| Item                           | One seat |     Thirteen seats, if adopted |
| ------------------------------ | -------: | -----------------------------: |
| Basket-sized GRP squares       |        2 | 26, sizes from basket schedule |
| M6 bolts / locking nuts / caps |   4 each |                        52 each |
| Broad washers                  |        8 |                            104 |
| Rigid spacer sleeves           |        4 |                             52 |
| Rail collars                   |        2 |          26 multi-turn collars |
| Removable basket ties          |        4 |                             52 |

The ring, its corner hardware and 32 supports are additional and remain the
R3 allowance. Plate stock area, risers and deeper seats depend on the measured
baskets; do not turn thirteen example B28 seats into a buying list.

Trial one complete seat with the soaked, out-of-water basket mass. Move the
load off centre, slide the basket through its removal travel and apply handling
uplift. Check plate flexure, rocking, sleeve contact, fastener loosening,
collar slip, drainage and basket/bolt clearance. Then include it on the full
ring-side prototype to check spine roll and support response. Use the existing
load envelope and acceptance sequence in [design-C.md](design-C.md); passing
the local plate trial does not establish spare capacity in the deck.
