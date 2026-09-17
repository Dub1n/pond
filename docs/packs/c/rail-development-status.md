# Pack C rail development — current state

## Decision

Proceed with a measured freshwater prototype using:

- a 2,100 x 2,100 mm centreline ring of 38 x 38 x 5 mm GRP SHS;
- four split-plate stiff corners and integrated basket seats in
  [corner-v2.md](corner-v2.md);
- nine split-plate mid-rail seats in [R5.2.md](R5.2.md);
- 36 direct 5 mm polyester loops/slings in [cords.md](cords.md); and
- ten B23 and three **B27** permanent rigid baskets containing independently
  removable planting cartridges in [plants-v2.md](plants-v2.md).

The plates come from three stocked 200 x 9.5 x 3,000 mm pultruded GRP flat
bars. The custom-sheet route is no longer active because of lead time and lack
of alternative supply. R3, R4, R5, R5.1 and corner v1 are retained development
history, not parallel fabrication instructions.

This remains a prototype candidate. It is not approval to batch-fabricate the
carrier or load the deck.

## Active documents

1. [design-C.md](design-C.md) — as-built deck interface and reaction envelope.
2. [purchase-cost-study.md](purchase-cost-study.md) — sole material schedule,
   complete purchase list, cost and cost-reduction reasoning.
3. [corner-v2.md](corner-v2.md) — current corner geometry and proof envelope.
4. [R5.2.md](R5.2.md) — current mid-rail and corner-seat architecture.
5. [cords.md](cords.md) — suspension topology, cord interfaces and proof duties.
6. [plants-v2.md](plants-v2.md) — permanent baskets, removable cartridges and
   plant allocation.
7. [install-walkthrough.md](install-walkthrough.md) — the only active source of
   fabrication, assembly, installation and test procedure.

Supporting calculations are in `docs/calcs/`. Do not reconstruct current
dimensions from R5.1 or corner v1.

## Integrated arrangement

Use pond centre `X=Y=0`, minimum-water/pad datum `Z=0` and ring centrelines at
`X/Y=+/-1050`.

### Suspension

The 36 complete cord items are:

- 24 direct gravity loops at straight joists J2-J7, six per side;
- 8 crossed loops, one opposed pair per side; and
- 4 continuous C2 corner slings, each with two lower legs on separate corner
  posts.

Each straight or crossed item is a closed loop with two adjacent load-bearing
legs. The C2 sling is one complete item: loss of that cord removes both lower
legs in the fault model. Tubular polyester webbing protects timber, rail and
C2-post contacts. Three-millimetre cord only locates lower wraps, connects
crossing sleeves and carries tags; it does not suspend the ring or stop seats.

Upper wrap coordinates and cord tangents remain measured inputs. The current
topology achieved rank 6 in the provisional constraint screen and feasible
equilibrium under each complete-item-loss case, but the listed movements are
not predictions for the purchased cord or final geometry.

### Corners

Each corner has two mirrored 9.5 mm upper plates, one 9.5 mm thick lower web,
six sleeved rail/corner bolts and two separate ready-bored nylon C2 posts. Rail
axes remain at 55, 125 and 195 mm on each leg. Both upper plates share the two
55 mm axes; the C2 post axes are approximately `(-140,55)` and `(55,-140)`.

The new 140 mm C2 bridge measures about 117.7 mm wide through its middle and
screens at about 23.7 MPa under the retained isolated 0.30 kN comparison. Two
outer M6 basket lands must be widened from the supplied approximately 10.5 mm
axis-to-edge value to at least 16 mm, preferably R20.

The corner basket is centred at the rail intersection and rotated 45 degrees.
The combined upper plates provide an effective minimum support envelope of
about 275 x 293 mm. B23 is the preferred corner basket. A real 270 mm B27 may
be considered only after a full post/cord/basket template; any plastic-corner
trim or sleeved basket opening remains a tested contingency, not nominal
geometry. One sealed 9.5 mm GRP offcut pad levels the one-ply bearing point.

### R5.2 seats

Each of the nine mid-rail seats has two upper arms, one upper bridge, two lower
bridges and four sleeved M8 x 90 bolts. Available reinforced-base sets are:

| Base span | Upper arms | Upper bridge | Lower bridges |
| ---: | ---: | ---: | ---: |
| 250 mm | 40 x 290 mm | 90 x 340 mm | 35 x 91 mm |
| 225 mm | 40 x 265 mm | 90 x 315 mm | 35 x 91 mm |
| 200 mm | 40 x 240 mm | 90 x 290 mm | 35 x 91 mm |

The first dimension is width and the second overall length. Actual reinforced
basket geometry selects the set. Gravity bears through the arms and upper
bridge into the rail. The bolts and lower bridges provide uplift/overturning
capture. Broad clamp contact provides longitudinal restraint, optionally
assisted by a proven thin pad or qualified adhesive without deleting the
mechanical capture. Each bolt uses factory-bored 20 OD x 10 ID unfilled POM-C
tube with a controlled 1 mm rail-facing flat, retaining the 56 mm bolt spacing
while giving broad transverse contact against the rail.

### Baskets

The carrier has ten nominal 230 mm B23 baskets and three nominal 270 mm B27
baskets. Four broad internal M6 washers retain each empty basket at sound rib
positions; normal planted load remains bearing load. PB18 and PB25 cartridges
remain separately removable. Basket product names do not establish reinforced
base size, retention locations or wet mass.

## Calculation position

- The 38 x 38 x 5 mm rail remains plausible in the existing gross-member
  screens; flexible-ring behaviour still depends strongly on real corner and
  suspension stiffness.
- The unchanged thick lower corner web retains its 9.5 mm comparative plate
  screen. The former monolithic upper-corner stiffness result does not transfer
  to the split pair.
- Corner v2 must demonstrate at least 20 kN m/rad from 0 to 60 N m after
  bedding, together with the 30 N m roll case and unequal C2 loading.
- R5.2 arm flexure is below the 2 mm comparison limit; connection/bearing width
  governs. The 90 mm bridge also passes the conservative complete 0.30 kN
  point-load comparison for the 250 mm span.
- Every completed support item retains the 0.30 kN dry/wet proof duty. Cord
  breaking load is not its axial stiffness; settled extension must be measured
  and returned to the flexible-ring model.
- Deck reactions remain open until cord tangents, drained basket masses and
  corner behaviour are measured.

## Simplicity and cost position

The sole live purchase schedule is [purchase-cost-study.md](purchase-cost-study.md).
Its current total is **GBP 552.29 including VAT, excluding delivery**:

| Cost group | Current amount |
| --- | ---: |
| Three stocked structural-GRP flat bars | GBP 284.76 |
| Two GRP rail tubes | GBP 110.00 |
| Cord, webbing, all fasteners, sleeves and edge resin | GBP 157.53 |

The previous GBP 498.92 total used a GBP 250 assumed custom sheet and M8 x 80
seat bolts. The stocked-bar route adds GBP 34.76 for plate and GBP 1.76 for the
revised bolt mix, but removes the custom lead-time dependency. The design still
avoids proprietary suspension fittings, blanket A4 hardware, commercial seat
stops and separate corner-basket plates. Factory-bored POM-C seat tube and
ready-bored C2 posts add GBP 16.85 relative to the former solid-rod allowance
while eliminating 44 axial bores.

Three bars are required in all 250/225/200 mm R5.2 cases. Smaller seats create
more useful offcut rather than reducing the demonstrated purchase count. The
offcut supplies the four corner levelling pads at no extra material cost.

## Purchase boundary

The prototype purchase comprises only the items in the complete table in
`purchase-cost-study.md`. Baskets and planting contents remain in the planting
schedule. Final batch release depends on sample material and connection
evidence; the listing total is not fabrication approval.

## Release gates

The design remains open until all of these are closed:

- actual flat-bar and rail dimensions, material data and freshwater evidence;
- B23/B27 reinforced bases, retention ribs, cartridge clearances and fully
  soaked drained masses;
- R5.2 grip, sleeve, basket-bearing and longitudinal-slip tests;
- corner-v2 washer lands, stepped support, complete wet stiffness and C2 fault
  tests;
- cord knot, chafe, locating, extension and complete-item proof results;
- flexible-ring results using measured coordinates and stiffnesses;
- accepted vertical/horizontal deck reaction limits and post-deck access; and
- demonstrated inspection, unloading and replacement access.

All procedural detail for satisfying these gates is in
[install-walkthrough.md](install-walkthrough.md).
