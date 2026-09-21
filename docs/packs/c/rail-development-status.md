# Pack C rail development — current state

## Decision

Proceed with a measured freshwater prototype using:

- a 2,100 x 2,100 mm-centreline ring of 38 x 38 x 3.2 mm GRP hollow section;
- four one-piece 10 mm aluminium corner seats in
  [corner v3](corner-v3.md);
- nine one-piece 10 mm aluminium mid-rail seats in [R5.3](R5.3.md);
- 36 direct 5 mm polyester loops/slings in [cords.md](cords.md); and
- ten B23 and three B27 rigid baskets with independently removable cartridges
  in [plants-v2.md](plants-v2.md).

Five 670 x 460 x 10 mm EN AW-5083 sheets are the current plate allowance; the
H temper must be confirmed. All hardware, cord and webbing has been purchased.
Only plate and rail remain to buy. This is a prototype decision, not batch-
fabrication or deck-loading approval.

## Active documents

1. [design-C.md](design-C.md) — as-built deck interface and reaction envelope.
2. [purchase-cost-study.md](purchase-cost-study.md) — materials, purchases and
   remaining procurement gates.
3. [aluminium-cut-parts.md](aluminium-cut-parts.md) — exact SVG cutting pack and
   quantities.
4. [corner-v3.md](corner-v3.md) — corner geometry, load paths and proof.
5. [R5.3.md](R5.3.md) — mid-rail seat geometry, load paths and proof.
6. [cords.md](cords.md) and [plants-v2.md](plants-v2.md) — suspension and
   planting interfaces.
7. [install-walkthrough.md](install-walkthrough.md) — the active fabrication,
   assembly, installation and test sequence.

R5.2 and corner v2 are retained as development history, not parallel cutting
instructions.

## Integrated arrangement

Use pond centre `X=Y=0`, minimum-water/pad datum `Z=0` and ring centrelines at
`X/Y=+/-1050`. The 36 complete cord items remain 24 direct gravity loops at
straight joists J2–J7, eight crossed loops and four continuous C2 corner
slings. Three-millimetre cord locates wraps and tags only; it does not suspend
the ring or stop seats.

Each corner has one upper, one lower web, six sleeved rail axes at 55, 125 and
195 mm on each rail and two separate C2 posts. Each mid-rail seat has one
upper, two lower bridges and four sleeve-controlled M8 capture bolts. Four M6
sets retain each empty basket; planted service load remains direct bearing.

## Calculation position

- The 3.2 mm rail gross-member screen gives `I = 90,668 mm4` and approximately
  `J = 134,861 mm4`; the deliberate 0.30 kN / 840 mm support-loss case gives
  13.2 MPa and 2.40 mm. Perforated wet connections remain unproved.
- The nominal rail cavity is 31.6 mm. All 24 corner sleeves must be remade to
  measured delivered cavities; calculated two-wall bearing at the retained
  0.763 kN corner action is about 14 MPa.
- Ten-millimetre aluminium has ample gross elastic stiffness in the seat
  comparisons, but unknown temper, open-hole bearing, local basket bearing,
  corrosion isolation and complete-joint behaviour prevent a thinner release.
- Corner v3 must demonstrate at least 20 kN m/rad from 0 to 60 N m after
  bedding, plus the retained 30 N m roll and unequal/lost-C2 cases.
- Each R5.3 seat retains the 0.30 kN centred/eccentric/uplift cases and 100 N
  bidirectional migration check, dry and after wet dwell.
- Deck reactions remain open until cord tangents, drained basket masses and
  measured corner behaviour are available.

## Release gates

The design remains open pending:

- certified aluminium grade, H temper and thickness, water chemistry and
  stainless-isolation detail;
- delivered rail dimensions and wet-service evidence;
- demonstrated five-sheet cutter nest from the exact four SVGs;
- B23/B27 base ribs, retention zones, cartridge clearance and drained masses;
- one complete R5.3 seat and one complete corner-v3 dry/wet proof;
- cord knot, chafe, locating, extension and complete-item proof results;
- flexible-ring results using measured coordinates and stiffnesses; and
- accepted deck reaction limits plus inspection, unloading and replacement
  access.

All procedures for closing these gates are in
[install-walkthrough.md](install-walkthrough.md).
