# Pack C rail development — current state and next work

This is the active handoff for the submerged planting carrier as at
11 September 2026. It records one integrated prototype architecture. Earlier
R3, R4, R5 and lower-H alternatives are development history, not parallel
construction instructions.

Nothing in this document is approval to load the deck or batch-fabricate the
carrier.

## Current decision

Proceed to measured samples and dry-ground prototypes using:

- a 2,100 x 2,100 mm connected ring of 38 x 38 x 5 mm structural-GRP SHS;
- the paired 12 mm triangular-web joints in [corner.md](corner.md);
- 44 independently adjustable polyester cords and the fittings in
  [cords.md](cords.md);
- the open H-cradle seats in [R5.1.md](R5.1.md); and
- permanent B23/B28 rigid baskets containing independently removable planted
  cartridges, as specified in [plants-v2.md](plants-v2.md).

The design now fixes the geometry that can responsibly be fixed before the
products arrive. It deliberately retains measured transfer dimensions for the
basket bearing bands, final cord cutting jig, sleeve lengths and depth
adaptors. Those are manufacturing hold points, not invitations to redesign the
load paths.

## Read and use in this order

1. [design-C.md](design-C.md) — as-built deck interface and five still-TBC
   allowable reaction limits.
2. [corner.md](corner.md) — cut pattern, bolt stack, non-projecting diagonal-joist
   eye, test specimen and four-corner release gates.
3. [cords.md](cords.md) — selected rope/terminations, all 44 upper and lower
   force lines, cutting and one-person installation sequence.
4. [R5.1.md](R5.1.md) — seat, no-hole strap movement stop, fallback stop pin and
   broad-washer basket attachment.
5. [plants-v2.md](plants-v2.md) — cartridges, guards, depth variants, planting
   and removal sequence.
6. [rail-support-study.md](../../calcs/rail-support-study.md) and
   [ring-corner-study.md](../../calcs/ring-corner-study.md) — reproducible
   assumptions and calculation screens.

The old rail diagram YAML illustrates predecessor geometry only. Do not create
a detailed R5.1 production YAML until the measured basket templates, actual eye
offsets and prototype corner curve are available.

## Integrated geometry

Use pond centre `X=Y=0`, minimum-water/pad datum `Z=0` and ring centrelines at
`X/Y=+/-1050`. Straight pad eyes are centred on the rail top; their nominal
eye/shackle tangents are at local `r=1050, Z=-207`.

### Suspension

The 44-cord set is:

- 24 gravity cords at straight joists J2--J7, six per side;
- 4 inclined corner cords supported from side eyes wholly behind the existing C2
  diagonal joists; and
- 16 crossed stabilisers: `U2 -> L3`, `U3 -> L2`, `U6 -> L7` and `U7 -> L6`
  on every side.

The straight upper force line is on the pond-facing joist-end plane at
`r=1150, Z=+112.5`; its matching lower force line is on the rail centreline at
`r=1050, Z=-207`. The straight vector is 100 mm inward and 319.5 mm down,
length 334.78 mm. The crossed cords are 537.04 mm between force lines.

The former J1/J8 cords are deleted. Each C2 upper corner eye is side-mounted
55 mm behind its diagonal timber tip, with no fitting beyond the timber end
plane. The four new corner cords are inclined and nominally 358.07 mm between
force lines. The resulting horizontal and eccentric actions are included in
the suspension/deck envelope; they are the cost of respecting the no-projection
constraint without adding another structure.

`cords.md` is the controlling 44-row map. Coordinates are eye/pin force lines,
not raw rope cut lengths.

### Corner

Each rail corner has:

- one top and one bottom 12 mm balanced structural-GRP plate;
- a five-sided triangular-web outline with 220 mm reach and 80 mm strips;
- three M8 axes on each leg, 55, 125 and 195 mm from the theoretical corner;
- close 8.2–8.5 mm stack holes;
- one measured internal A4 sleeve at every bolt; and
- an articulated lower cord eye on the theoretical corner force line.

The selected paired-strip estimate is 41.9 kN m/rad before connection
compliance. The assembled wet joint must demonstrate at least 20 kN m/rad from
0 to 60 N m after bedding. The 60 N m plan and 30 N m roll combination gives a
conservative 0.737 kN bolt/plate force screen, 7.2 MPa plate bearing and
8.7 MPa two-wall tube bearing. These are demands, not product resistances.

### Seats and baskets

R5.1 uses one 12 mm upper H and two 50 x 110 x 12 mm lower bridges around the
38 mm rail. Four M8 sleeved bolts form two spaced capture stations. The upper H
has 50 mm-wide basket-bearing arms, a 90 mm central strip and internal radii
of at least 25 mm. Bearing-arm spacing and projection transfer directly from
the sound base bands on the purchased basket.

The prototype movement stop uses two independent 25 mm polyester endless
cam-buckle straps per seat, routed through rounded slots in the upper H and
around the rail. This is the simplest one-person installation and adds no rail
hole. It is accepted only after wet cyclic slip and seven-day creep tests with
witness marks. A zinc or otherwise unverified buckle is trial hardware only.
If the straps slip, use one through-bushed M6 rail pin and one elongated 3 mm
316L stop plate on the accessible face; that fallback requires the open-hole,
horizontal-bending and torsion coupon noted in `R5.1.md`.

Four internal 40 mm A4 penny washers and M6 button-head screws retain the empty
rigid basket at tested sound rib intersections. A washer against one unsupported
plastic strand is prohibited. The PB18/PB25 bag, harness and fish guard remain
one removable planted cartridge and carry no seat load.

## Calculation status

The selected 44-cord rigid-ring study gives:

| Result                                           |                 Value |
| ------------------------------------------------ | --------------------: |
| Rigid-body constraint rank                       |                6 of 6 |
| Uneven 1.80 kN case plus 5 N m: maximum cord     |                75.8 N |
| Worst maximum with any one cord unavailable      |                84.6 N |
| Free-length 95th-percentile maximum cord         |                99.5 N |
| Upper downward / horizontal / resultant envelope | 91.7 / 45.9 / 102.5 N |
| Free-length 95th-percentile rigid-body movement  |               3.42 mm |

All single-cord-unavailable cases found feasible equilibrium in the ideal
screen. The cord geometry therefore provides a plausible global positioning
system, but the result assumes a rigid ring and cannot establish installed
movement or deck adequacy.

At the selected straight force line a 0.60 kN heavy side pushes the rail
outward by about 0.188 kN. The 5 mm SHS screens plausibly for gross vertical
bending and torsion, but a pinned side could breathe about 10.9 mm versus about
2.2 mm with fixed ends. That is why measured corner stiffness, slip and flexible
ring redistribution are release gates.

The upper reactions are unfactored comparison values. The individual 0.30 kN
support proof checks a cord connection and cannot be treated as spare deck
capacity. `design-C.md` must replace all five TBC limits using the actual
joists, hangers, straps, screws, beams, slabs, ground and decking loads.

## Purchase sequence

Do not order all custom parts at once.

### First purchase — measurement and coupons

- one B23, one B28, one PB18 and one PB25;
- one quoted sample of the specified 12 mm balanced structural-GRP plate and
  the 38 x 38 x 5 mm tube, with wet-service certificates;
- enough M8/A4 hardware and sleeves for one corner coupon and one R5.1 seat;
- one Wichard 6684 or equivalent articulated lower eye with its two spreader/
  backing plates;
- one Marlow Excel Pro 6 mm sample with a supplier-spliced thimble eye;
- one Clamcleat CL253AN, PT230SSE hanger and one load-rated M6 shackle; and
- four 40 mm A4 penny washers for each sample basket and one cheap 25 mm
  polyester endless cam strap plus one marine 316 endless cam strap for the
  movement-stop comparison.

### Prototype purchase — only after sample fit

- one complete corner set and one non-projecting C2 side-eye assembly;
- one 100 m reel of the accepted same-batch rope;
- fittings for the representative side described in `R5.1.md`;
- one complete B23 and B28 seat/basket attachment; and
- test loads, a small spring scale, witness paint and replaceable chafe sleeves.

### Batch purchase — only after all release gates

Use the quantity tables in `corner.md`, `cords.md` and `R5.1.md`. Together they
cover four corners, 44 installed cords plus four spare cleats/cord allowance,
13 seats and 13 permanent basket attachments. Transfer the accepted sample
dimensions and supplier batches; do not rebuild the order from nominal sizes.

## Build and test sequence

1. Survey all joist tips/faces, C2 connections, liner, water levels, intended
   deck edge and service access before fitting boards.
2. Measure the B23/B28 bearing bands, base ribs, taper and wet removal envelope.
   Make one full-size basket-position sheet for all 13 seats.
3. Test one sleeved GRP connection coupon and one lower-eye saddle. Establish
   the tightening procedure; reject whitening, indentation, splitting or
   permanent set.
4. Build and wet-test one complete corner to `corner.md`, including clearance
   dead band, plan stiffness, roll, combined cycles and proof loads.
5. Build the representative full side with all selected cords, one corner,
   shallow B23/B28, *Butomus* and crowfoot stations, and a real deck-edge
   mock-up.
6. Prove each cord termination at 0.30 kN over dry ground, then repeat the
   system cases after soaking, with the calculated worst cord removed and one
   corner ineffective.
7. Test R5.1 eccentric gravity, handling uplift, wet strap-stop slip, one
   loosened fastener, washer/mesh creep and all cartridge/basket/seat removal
   sequences. If strap slip exceeds the limit, test the fallback stop pin/plate
   before batch work.
8. Insert the measured corner moment-rotation curve and actual eye offsets into
   the flexible-ring analysis. Issue every upper reaction to the deck check.
9. Accept the five deck reaction limits and post-deck access before making the
   four-corner/13-seat/44-cord batch.
10. Lower and proof the empty ring, seats and rigid baskets. Add the prepared
    planted cartridges only after the carrier remains level and accepted.

Use temporary control lines when lowering. Cut/drill GRP over dry ground with
dust extraction; round and resin-seal every cut. All immersed metal is A4/316
or 316L, all hollow members have deliberate sealed drainage/vent routes, and
fish or liner may touch no exposed fibre, burr or projecting thread.

## Release gates and residual risk

The design aims to make each single cord replaceable and to prevent one loose
corner bolt, one movement-stop strap slipping or one cartridge component from
causing immediate loss of the carrier. “Near certainty that any possible
failure will not occur” cannot be established from calculations alone,
especially for wet GRP joints, unknown timber connections and biological
growth. Batch fabrication therefore requires all of these records:

- purchased-material certificates and machining/immersion guidance;
- measured R5.1/basket dimensions, full-side clash and removal sheet;
- passed corner stiffness, dead-band, wet dwell, combined and proof tests;
- passed rope/cleat/splice/shackle/eye dry and wet proof tests;
- passed seat, basket-washer, movement-stop and maintenance trials;
- flexible-ring results using the measured joint curve, one ineffective corner
  and each important cord unavailable;
- accepted characteristic per-support, horizontal, adjacent-support, side-total
  and temporary-uplift deck limits; and
- an inspection/replacement plan keeping every upper termination accessible.

If the corner does not retain 20 kN m/rad after bedding, do not simply thicken
the plate again. First locate the compliance: bolt clearance, tube-wall bearing,
plate bending, mitre bedding or rail torsion. Correct that element, or reopen a
supplementary roll-restraint architecture with a complete basket-clearance and
fault analysis.
