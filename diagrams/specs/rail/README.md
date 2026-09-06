# Rail design studies

These are standalone relationship-first YAML specifications in **Option C's
world coordinates**, with one editable shallow B28 basket and its support in
each. They are comparison drawings; basket bases and local fittings are
prototype dimensions, not issued fabrication details.

| YAML / option | Design document | Extent |
| --- | --- | --- |
| [r3-spine.yaml](r3-spine.yaml) / `R3` | [R3-rail.md](../../../docs/packs/c/R3-rail.md) | Complete single-spine ring; two crossbars beneath one basket |
| [r4-double-rail.yaml](r4-double-rail.yaml) / `R4` | [R4-double-rail.md](../../../docs/packs/c/R4-double-rail.md) | One 2,100 mm ladder side; forked same-bank suspension is unresolved |
| [r5-plates.yaml](r5-plates.yaml) / `R5` | [R5-plates.md](../../../docs/packs/c/R5-plates.md) | Complete single-spine ring; upper/lower square plates, four sleeved bolts and two cord collars |

Each file shows all eight south joists for context and **two completed support
paths, at J3 and J4**, bracketing the sample basket. R3/R5 still require all
32 supports; the other 30 are omitted. R4 illustrates two of eight proposed
forked stations. Its two lower legs both pull toward the same bank: rendering
the module in position does not show that it can stay there.

## Build and inspect

Run from the repository root. The default build/lint search is not recursive,
so pass these files explicitly:

```bash
./.venv/bin/python scripts/build_diagrams.py \
  --spec diagrams/specs/rail/r3-spine.yaml \
  --spec diagrams/specs/rail/r4-double-rail.yaml \
  --spec diagrams/specs/rail/r5-plates.yaml \
  --outdir diagrams/output --force --collision-mode ignore

./.venv/bin/python scripts/lint_specs.py \
  --spec diagrams/specs/rail/r3-spine.yaml \
  --spec diagrams/specs/rail/r4-double-rail.yaml \
  --spec diagrams/specs/rail/r5-plates.yaml --collision-mode warn

./.venv/bin/python scripts/baseline_render_check.py --fresh-check
```

SVG/PNG views, `model.glb` and `model.ifc` land in
`diagrams/output/<yaml-stem>/<lowercase-option>/`. Generated output is ignored
by Git; the YAML is the source. The views are:

- `plan`: the ring or side module, basket and south joist context.
- `seat-plan`: the basket's bearing base and local seat. Upper walls/rim and
  long rails/joists are hidden to expose the support; this is not a second
  assembly or an exploded copy.
- `section`: a transverse cut through a basket bearing band, with water and
  deck-edge datum marks. It shows the full shallow basket height.
- `connection`: a transverse detail through the left bar (R3/R4) or left bolt
  station (R5). Basket walls/rim are omitted so the connection is legible.
- `suspension`: a true section through J4, showing the joist wrap, sloping
  cord and lower rail wrap. Knots and second turns are described in the docs.

The palette uses `grp`, `polyester`, `a4-stainless` and `basket-polymer`, defined
in `diagramming/materials.py`. The basket's muted green-grey is a diagram key,
not a request to change the specified dark basket material.

## Shared coordinates and Option C integration

| Datum                                      | Coordinates, mm                                |
| ------------------------------------------ | ---------------------------------------------- |
| Pond/deck centre                           | X = 0, Y = 0                                   |
| Pond walls                                 | X/Y = ±1,500                                   |
| Finished deck opening                      | X/Y = ±1,150                                   |
| R3/R5 spine centrelines                    | X/Y = ±1,050                                   |
| R4 south rail centrelines                  | Y = −1,125 and −975                            |
| Water surface / pad tops / beam undersides | Z = 0                                          |
| Beam and joist tops / deck underside       | Z = +150                                       |
| Straight joist undersides                  | Z = +75                                        |
| Nominal deck top                           | Z = +178                                       |
| Shallow B28 base / rim                     | Z = −200 / −10                                 |
| R3/R4 main rail top                        | Z = −225                                       |
| R5 main rail top                           | Z = −206 (6 mm upper plate replaces 25 mm bar) |

South-side +X runs along the rail and +Y points into the pond. The basket
centre is X = −260, Y = −1,050. The eight joist centres match Option C's
irregular as-built placements, not an invented uniform array. The water volume
in Option C remains 900 mm deep, from Z = −900 to 0. Rail studies use water
Z = 0 as the minimum-water design reference; check actual operating variation.

To combine **one alternative** with `option-c.yaml`:

1. Keep Option C's `origin`, `deck_frame`, `pond_frame`, `opening_frame` and
   `joist_run_south` components. Remove the identically named **CONTEXT**
   components from the rail file instead of adding duplicate IDs.
2. Remove `rN_water_line` and `rN_deck_edge`. They are diagram-only strips;
   Option C already contains the water and deck geometry.
3. Reuse the shared `dimensions.interface` values already present in Option C.
   Add the revision-prefixed dimensions under `dimensions.rail`. Do not copy
   duplicate unprefixed dimension leaves into a second namespace.
4. Add all remaining rail components. Preserve their `relate` and `place`
   blocks without translation or rotation. Keep Option C's operations.
5. Use Option C's views for the combined scene. For close local views, retain
   the standalone files, whose visibility lists deliberately omit return rails
   from transverse details. A full-deck combined plan can obscure submerged
   parts beneath decking and water.

R3/R4/R5 prefixes prevent rail-part name conflicts, but the three alternatives
are not meant to occupy the pond simultaneously. No include/assembly extension
to the YAML language is required. R4 must not be blindly rotated four times:
full-length adjacent ladders clash at the corners, and their restraint is
unresolved.

## Edit or repeat a basket station

Start with `rN_basket_x`, the assumed `rN_basket_base`, `rN_basket_rim` and
`rN_basket_height`. All seat parts are positioned from the geometry-less
`rN_station` reference. The base remains at the chosen `rN_bearing_depth` when
height changes; change the bearing depth too if preserving 10 mm rim cover.

For R3/R4, bar length and spacing follow the base width, while their paired
placements use `place`. For R5, set `r5_plate_side` from the measured basket
and hardware clearance; bolt stations follow base width and rail size. The
plate thickness, sleeve length and inter-plate fit are separate named inputs.
The 280 mm example plate is not automatically a suitable B23 plate.

At the end of each YAML is a **complete commented `translate` operation**.
Uncomment that block to keep the original seat and add a copy 520 mm along X,
at X = +260. Its target list includes the basket, support and local fittings;
it excludes joist supports, main rails and R4's fixed end ties. This copies
the whole seat once without rewriting each component. Repeat/adjust operations
only after checking corner zones, support wraps, neighbouring baskets and
removal travel. It is a language example, not the final 13-basket schedule.

Cord centreline lengths are explicit numbers because this expression language
supports arithmetic but no square-root function. Their comments give the
endpoint vectors. If changing the rail, joist or water elevation, recompute
each as `sqrt(dx*dx + dy*dy + dz*dz)`; orientation vectors and midpoint Z use
the named rail-top expression. Do not accept a successful solver run as proof
that an unchanged literal length still reaches both endpoints.

## Simplifications and collision interpretation

The following are deliberate modelling choices:

- GRP square tubes are solid outer envelopes. Hollow walls, vents and drains
  are specified in the documents. R3/R5's four envelope pieces meet squarely;
  the actual members are four 2,138 mm long-point mitred cuts, with paired
  6 mm L plates and four M6 bolts at every corner. Corner plates/bolts are
  documented rather than repeated at this scale.
- The basket is an open **stepped envelope** with a 200 mm lower body and
  280 mm rim. It shows bearing and rim extents, not true tapered mesh. Media,
  planting pot and plant are omitted. Upper/lower mesh engagement must be
  checked on the real basket.
- Cord is a square prism. A wrap is an outline of touching prisms. One turn
  stands for the prescribed two; knots, chafe sleeves, joist keeper stops,
  and the two small collars beside each main support wrap are omitted.
  Upper supports need removable-board access or an accepted accessible fixing.
  Joined cord segments overlap slightly at bends; R4's fork legs meet at the
  upper wrap. The water-datum strip also intersects cords passing through it.
- R3 crossing bindings and four lower ties can intersect the solid basket-base
  envelope, representing real mesh openings and cord engagement. R4 adds
  attached keeper cheeks at the basket crossings; small cheek-fixing hardware
  and the identical end-tie connection detail are described in R4's document.
- R5 sleeves, bolts, washers and plates overlap where actual holes exist.
  They are square envelope solids; bolt/sleeve bores, plate bolt holes,
  drainage holes and tie holes are not cut. The four bolt axes lie outside
  the main tube, so no hole through the spine is implied.

Audit `--collision-mode warn` output against those contacts. `ignore` is used
for exports of the documented envelopes; it does not establish physical
clearance or structural adequacy. Keep schema, size, selector and IFC checks
enabled. All parts retain material and height metadata through the normal
planner/exporter path.
