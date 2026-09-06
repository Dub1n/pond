## Verdict

R5 is a mechanically coherent **prototype seat**, but it is not currently a structurally validated whole-pond design. It improves R3’s local basket-to-spine connection, yet it does not solve R3’s principal unresolved issue: rotation and racking of the single-spine ring and its suspension system.

Holistically, R5 adds enough weight, submerged surface area, hardware, placement difficulty, and maintenance burden that I would not select it over a properly detailed R3 seat unless testing shows that the basket bases need continuous support or that R3’s positive keeper arrangement cannot control local movement.

My present ranking is:

1. **R3 with positive non-clamping crossbar keepers and a dedicated uplift restraint** — best prospective balance.
2. **R5 as a comparative prototype** — plausible, but disproportionately elaborate and still dependent on R3 globally.
3. **R4 as a diagnostic study only** — useful for exposing R3’s torsional and lateral cases, but invalid as the illustrated independent suspended arrangement.

## What R5 actually solves

The two plates, sleeves and four bolts in [R5-plates.md](/home/gabri/docs/pond/docs/packs/c/R5-plates.md:17) give the local seat several real advantages:

- The sleeves positively limit movement across the rail and limit yaw.
- The lower plate positively catches uplift and basket overturning.
- The main hollow spine is not drilled or squeezed.
- The large upper plate supports weak or irregular basket bases better than two narrow crossbars.
- The seat can be dismantled without opening a ring corner.

This is a meaningful improvement over R3’s present cord-bound crossbars. R3 relies on lashing friction for translation, yaw and uplift unless positive keepers are added.

R5 still uses cord collars for movement along the rail, however. It therefore replaces only part of R3’s friction-dependent restraint.

## What it does not solve

The plate pair captures the 38 mm spine, but it rotates with that spine. It provides no second reaction line to the deck or another rail. Consequently it does not solve:

- whole-spine rotation under eccentric basket or plant loading;
- ring racking and corner-joint response;
- horizontal reactions from the inclined support cords;
- loss of a support;
- accessibility and replacement of the joist terminations;
- the still-TBC deck, hanger, beam and foundation load envelope;
- the special *Butomus* and crowfoot elevations;
- the four lower basket ties and removal-clearance problem.

Indeed, R5 may transfer basket torque into the spine more reliably than R3 because its local connection is stiffer. That is useful for a representative test, but it does not make the global torque disappear.

R5 avoids R4’s fatal equilibrium problem because it retains R3’s connected ring and opposing-bank supports. That benefit comes from the inherited ring, not from the plates. R4’s 150 mm-separated rails offer better local torsional support, but its complete module still has no opposing horizontal reaction and can roll about its suspension line, exactly as [R4-double-rail.md](/home/gabri/docs/pond/docs/packs/c/R4-double-rail.md:64) states.

## Structural screen

For the documented 100 N basket moved 50 mm off the spine centre, a simple rigid-body screen gives approximately:

- **182 N upward reaction** at the loaded top edge of the rail;
- **82 N hold-down reaction** at the opposite underside.

Those forces are modest for four M6 stainless bolts. Bolt tensile strength is unlikely to govern. The uncertain parts are the 6 mm laminate, its holes, washer and sleeve bearing, bolt preload, creep, and the assumed distribution of load through the basket base.

Using a low published transverse GRP flexural modulus, a conservative cantilever-strip check gives:

| Assumed load distribution | Approx. plate stress | Approx. deflection at basket-base edge |
| --- | ---: | ---: |
| 50 N spread across 200 mm | 3.4 MPa | 0.45 mm |
| 50 N concentrated into a 25 mm strip | 27 MPa | 3.6 mm |

The first result is comfortable. The second exceeds the project’s approximate 2 mm movement target. Neither represents a proper orthotropic plate analysis, but the spread shows that actual basket bearing is decisive.

Strongwell explicitly treats pultruded plate as direction-dependent and requires the appropriate lengthwise or crosswise properties for the direction being checked. Its plate tables also use a 2.5 safety factor; its general guidance recommends 4.0 for connections and higher provision for long-term creep or dynamic loading. [Strongwell plate guidance](https://www.strongwell.com/wp-content/uploads/2020/03/Section10m-0320.pdf), [Strongwell safety factors](https://www.strongwell.com/wp-content/uploads/2013/05/Section07.pdf).

The potentially more severe fabrication load is bolt tightening. A normal M6 preload can greatly exceed the service reaction. The 12 mm sleeve end presents a small annular bearing area against the plate, so uncontrolled torque could cause local indentation, punching, splitting or delamination. The document recognizes this in general terms, but it needs an actual sleeve wall, washer, plate grade and tightening value. Strongwell warns about local bolt stress and calls for washers on both sides, but does not validate this particular detail. [Strongwell fabrication manual](https://www.strongwell.com/wp-content/uploads/2024/10/Strongwell-Fabrication-and-Repair-Manual.pdf).

## Clear problem in the illustrated geometry

The sample B28 seat does not properly fit between its illustrated J3 and J4 main supports once all required cordwork is included.

From [r5-plates.yaml](/home/gabri/docs/pond/diagrams/specs/rail/r5-plates.yaml:367):

- Plate plus collars occupies approximately X = −408 to −112 mm.
- The J4 lower support is centred at X = −108.5 mm.
- That leaves only **3.5 mm** between the seat envelope and the support centre.

The model omits the two collars required beside every 6 mm main-support wrap. Once those are included, the seat and J4 support conflict. Even centring the 296 mm seat in the 311.4 mm J3–J4 interval leaves only about 7.7 mm at each end, essentially no fabrication, cord-bulge or servicing clearance.

This does not invalidate every possible R5 layout. It means the illustrated B28 station is not buildable as detailed. B28 seats must use wider support bays, support locations must change, or the seat length must shrink. A complete four-baskets-per-side position drawing is therefore a prerequisite, not later drafting work.

## New failure and maintenance risks

The main R5-specific concerns are:

- **Local plate flexure and creep.** Drainage and tie holes will weaken an already thin plate; their pattern is still undefined.
- **Bolt-preload damage.** Sleeve-end bearing or overtightening can damage the laminate before the basket is loaded.
- **Clearance degradation.** The nominal 1 mm sleeve and underside gaps can jam with tube tolerance, grit, roots or biofilm; enlarging them permits more rocking and impact.
- **Cord-collar slip.** Longitudinal restraint remains friction-dependent.
- **Water and debris obstruction.** The upper plate covers nearly the whole basket base, reducing bottom exchange and creating a sediment surface. The lower plate adds a second large horizontal shelf. This works against the basket specification’s aim of preserving water exchange around the internal pot.
- **Added permanent load.** A pair of 280 × 280 × 6 mm plates weighs approximately 1.7 kg at a representative GRP density of 1,800 kg/m³. Depending on B23 plate size, all 13 seats would contain roughly **17.5–22 kg of plate**, versus about 3 kg for R3’s hollow crossbars. The likely net increase is around 15–19 kg before bolts and sleeves. That must enter the still-unapproved load envelope in [design-C.md](/home/gabri/docs/pond/docs/packs/c/design-C.md:83).
- **More inspection points.** Thirteen seats mean 52 bolts, 52 sleeves, 104 washers, 26 plates, 26 collars and 52 basket ties, plus drainage holes and caps.
- **Handling drag.** Twenty-six broad horizontal plates make lowering, lifting and rapid water movement less benign than the open R3 arrangement.

## Recommendation

Keep R5 as a one-seat and then one-side test variant. Do not adopt or batch-fabricate it yet.

The prototype should use the actual chosen plate and orientation, actual basket, drilled drainage/tie pattern, actual sleeves and a specified tightening procedure. Test distributed and deliberately localized base loading, 50 mm eccentricity, handling uplift, one loose fastener, collar slip, sustained wet loading, sediment fouling, and repeated basket removal.

Before the full-side test, lay out all four seats together with all eight support wraps, their omitted collars, the corner plates and removal routes. The present J3–J4 arrangement will need revision.

For the working design, I would first prototype R3’s two crossbars with positive rounded keeper cheeks and a separate light uplift lashing. That retains the open water path and low mass while eliminating most of R3’s local connection uncertainty. If the complete side still rolls or racks, R5 will not cure that failure; the design then needs a genuine second reaction line, rigid bracket, or otherwise valid redesigned twin-rail system.

The YAML models lint successfully, their documented envelope collisions are intentional, and the baseline render freshness check passed after rebuilding the three rail studies. I made no tracked file changes.

---

Yes—you’ve identified the right distinction. The cheek connection can suffer the same kinds of GRP connection failure as R5: local crushing, hole elongation, delamination and damage from excessive bolt preload. It is not inherently safer merely because it is smaller.

The difference is the load it must carry. With R3:

- Gravity passes directly from the crossbar into the spine.
- Cheeks principally resist sideways movement and yaw.
- A separate lower strap or lashing resists uplift.

Consequently, a lightly loaded cheek fixing can be less demanding than R5’s plate bolts. But if we eliminate the uplift cord and make the cheeks part of a fully mechanical saddle, their attachment must also carry uplift and overturning. The difference then becomes much smaller. Attaching cheeks reliably to a hollow 25 mm crossbar could actually be harder than bolting through a solid 6 mm plate unless the crossbar has internal compression sleeves or another broad-bearing connection.

Your proposed development of R5 makes sense. The full lower square is particularly inefficient: under normal gravity it does almost nothing. It is only needed to catch uplift and overturning. It could be replaced by two short lower bridge pieces, one at each bolt station, spanning beneath the rail between a pair of sleeved bolts.

The upper member only needs to:

1. support the basket’s reinforced bearing areas;
2. transfer their loads to the spine;
3. connect the two bolt stations;
4. provide basket-retention points.

That suggests an open, broadly H-shaped upper member:

```text
       basket bearing strip
    ─────────────────────────
              │
              │ central strip over spine
              │
    ─────────────────────────
       basket bearing strip
```

The two wide arms would sit beneath the basket’s reinforced base bands. The central strip would run along the spine and carry the bolt stations. Most of the basket underside would remain open to water.

Below the rail, two small bridges would complete two mechanical yokes:

```text
          upper member
    ────────●──────●────────
            │      │
          ┌──────────┐
          │  spine   │
          └──────────┘
            │      │
            ●──────●
          lower bridge
```

There would be another bridge and bolt pair farther along the rail. The spacer sleeves would remain valuable: they establish the clearance around the rail and prevent tightening from crushing or pinching it.

This revised arrangement could retain R5’s strongest features while removing much of its excess:

- positive transverse restraint;
- positive yaw restraint from two separated bolt stations;
- mechanical uplift capture;
- no hole through the main spine;
- much less plate weight;
- substantially more water exchange;
- fewer sediment-catching surfaces;
- lower hydrodynamic resistance;
- potentially enough free rail length to coexist with the support wraps.

The bolt positions should probably align closely with the basket bearing strips. That shortens the path between basket load, plate, bolts and lower bridges. The current ±120 mm positions were chosen mainly to put the hardware outside the assumed basket base; the real basket may allow a tighter and more efficient arrangement. Edge distances and washer footprints should follow the selected plate supplier’s connection guidance rather than retaining the current 20 mm edge distance automatically.

I would keep four bolts arranged as two pairs along the rail. Reducing it to one pair would restore an easy yaw mechanism. Putting low-profile bolt heads and broad washers above, with capped locking nuts beneath the lower bridges, may also give better basket clearance than the current tall upper nuts and caps.

There are two remaining design problems.

First, cutting an H shape introduces narrow ligaments and internal corners. Those transitions need generous radii, and the upper member may need to be thicker than 6 mm once most of the square has been removed. Alternatively, retain the 25 mm hollow crossbars as the two bearing arms and connect them to a compact central plate saddle. That hybrid may be stiffer and lighter than a flat H-shaped plate.

Second, the resulting saddle can still slide along the smooth spine. The sleeves solve transverse movement and yaw, but they provide no positive longitudinal stop. If cord collars are to be eliminated, it needs one of:

- broad, deliberately designed split collars beside the saddle;
- small supplier-approved bonded GRP stops on the spine;
- a mechanical stop integrated with nearby support hardware;
- a carefully designed rail pin or through-fastened stop, accepting the disadvantages of drilling the spine.

A broad split collar or attached GRP stop seems preferable to drilling the main rail repeatedly. It would still depend on either clamping friction or an adhesive connection, so that detail needs testing; there is no completely free way to locate a removable object along an otherwise smooth tube.

Basket retention could also move away from four cord ties. The upper bearing arms might have shallow rounded upstands outside the measured basket base, with one or two removable broad straps or mechanical retainers for uplift. The critical caution is that these must capture a structurally sound basket feature rather than place concentrated load into arbitrary plastic mesh.

And you are right about the shared system problems. They should not count against R5 when comparing the local seats because R3 and R5 use the same ring and suspension. The fair comparison is:

- Hold the ring, corners, supports, basket loads and deck interface constant.
- Compare only the R3 crossbar saddle with the revised R5 open cradle.
- Then test the selected seat on the complete side and ring for the shared global behaviour.

Once R3 gains a fully mechanical saddle and R5 loses most of its plates, the two concepts begin to converge. The real choice becomes:

- **R3-derived:** two stiff tubular bearing arms, each with a compact mechanical saddle around the spine.
- **R5-derived:** one open plate cradle joining both bearing areas and capturing the spine at two separated locations.

I have a slight preference for the revised R5-derived open cradle if eliminating cord is a strong objective. A single integrated component makes the geometry between the two bearing zones and two rail yokes deliberate, and the solid plate is easier to through-bolt safely than attaching separate cheeks to small hollow crossbars. The R3-derived version will probably be lighter and stiffer, but its four cheek-to-crossbar attachments per basket need careful detailing.

Neither needs to solve the shared global ring issues to win the local comparison. It needs to avoid adding new problems while giving a predictable, inspectable and mostly mechanical basket seat.
