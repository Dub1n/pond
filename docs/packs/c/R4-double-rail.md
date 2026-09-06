# R4 — Double Rail

## Design status and scope

R4 develops the twin-rail side carrier suggested in [R3-review.md](R3-review.md).
It is a comparison concept with an unresolved suspension detail. **Two rails
can give a basket a better seat, but the independent module cannot maintain
the illustrated position using only cords to that bank's joists.** Do not
build four suspended modules on the assumption that the second rail fixes this.

The drawing in [r4-double-rail.yaml](../../../diagrams/specs/rail/r4-double-rail.yaml)
therefore shows one full south-side module and one B28 basket. It shows the
proposed forked cords, so the missing restraint is visible. It is a geometry
study, not a claim of force equilibrium or an accepted installation.
Two of the eight proposed upper stations (J3 and J4) are drawn in detail;
the other six use the same proposed connection and remain subject to the
same unresolved restraint.

## Arrangement and datum

- Two parallel **38 × 38 × 5 mm structural GRP square tubes**, each 2,100 mm
  long, with **150 mm between centrelines**. Equal sections keep their bearing
  faces level without packing a smaller secondary rail.
- Basket centreline 450 mm from the pond wall, as in R3. The rail centrelines
  are 375 and 525 mm from the wall, with the basket centred between them.
- Two **25 × 25 × 3 mm GRP transverse bars** beneath the measured reinforced
  basket-base bands. Each bears on both rails and fixes their separation.
- Two additional transverse ties near the module ends keep the empty module
  together. The illustrated ties are 150 mm in from the ends. These and the
  basket bars form a ladder; the basket is not its structural bracing.
- Nominal crossbar top is 200 mm below minimum water; rail top is 225 mm
  below it. This matches R3's shallow B28 seat.

The 25 mm secondary rail in the review remains a possible comparative test
attachment. It is not the baseline here: putting a 25 mm tube alongside a
38 mm tube requires deliberate top alignment and different support details.

For the example 200 mm basket base, use 230 mm crossbars. The rails occupy
188 mm across their outer faces, so the crossbar overhang is 21 mm at each
end. Set the bars under the actual base bands; the drawing's 160 mm bar-centre
spacing is an editable example, not a basket manufacturer's measurement.

## Basket-to-rail connections

At each bar/rail crossing, retain direct GRP bearing. Fit a pair of rounded
keeper cheeks to the underside of the bar, one beside each rail face, with
slight clearance. A keeper cheek is a small fence that prevents the bar
moving across the rail. Its fixing to the bar must carry that side load.
Use a short replaceable cord binding around the crossing to prevent uplift
and migration along the rail. Do not treat a loose block as an attached keeper.

The YAML shows representative cheeks and bindings; their small fixing bolts,
washers and any internal crush spacers are described here rather than drawn.
Use broad-bearing A4/316 through-fastening to the crossbar, with hollow-wall
compression controlled by the selected GRP supplier's detail. Do not drill
the main rails for these local keepers. The end ties need the same positive
location and uplift restraint as the basket bars.

Four replaceable ties hold the basket at sound reinforced lower-mesh zones.
Undo them, move the basket pondward until its rim clears the deck, then lift.
The rails and ladder ties remain in place. Measure the actual removal travel:
the nominal 280 mm rim overlaps the deck by 40 mm, before handling clearance.

## Why the proposed joist suspension is incomplete

An obvious interpretation of the review is one upper attachment at each joist,
forking into two lower cord legs, one to each rail. This holds the rails
together vertically only if the rest of the force system holds the ladder in
place. Both rails are pondward of the joist tip. Consequently **every loaded
leg pulls the module toward the same bank**. There is no opposing horizontal
reaction. Changing cord lengths or adding more cords to the same bank cannot
hold the illustrated free module there.

At the drawing's joist underside Z = +75 mm and rail top Z = −225 mm,
the vertical drop is 300 mm. The water surface is Z = 0, level with pad tops
and beam undersides. An upper wrap 50 mm behind the joist tip is **300 mm
pondward of the wall**, compared with the tip at 350 mm. The two lower lines are
therefore 75 and 225 mm pondward of the wrap. The horizontal/vertical force
ratios are approximately 0.25 and 0.75. Both have the same horizontal sign.
With an illustrative equal split of a 100 N load, they total about **50 N
toward the bank**. Actual lower wraps add depth and alter the values slightly,
but cannot change that conclusion.

A fork from a common upper point also permits the rigid ladder to roll as a
unit about the upper suspension line. Two local bearing lines improve the
basket/crossbar interface; they do not establish global roll or lateral
restraint. Longitudinal end cords do not supply the missing pondward reaction.

R3 and R5 instead retain a connected ring with cords to opposing banks; their
ring joints and complete suspension still need the existing prototype checks.
For an independent R4 module, a designed rigid bracket/strut or a connection to
an opposing structure would be necessary. Neither is quietly assumed here.
If such a connection makes R4 too elaborate, keep the single-spine ring and
compare its R3 and R5 seats.

## Corners and extent

Do not simply rotate this 2,100 mm ladder four times. The inner rails of
adjacent modules would cross near the corners. Four independent sides require
shorter/staggered ends and a revised corner basket layout; concentric connected
rings require eight designed corners. This study leaves that decision open
alongside the suspension question. There is no whole-pond R4 cut list.

## Plant depths, materials and service

Shallow B23 baskets need measured risers above the common seat. *Butomus*
requires its lower internal-pot arrangement and crowfoot its dedicated deeper
cradle, as set out in [plants.md](plants.md). The one shallow B28 model does
not represent those depth variants or a final layout of all 13 baskets.

Use the cut-face resin sealing, deliberate hollow-member vent/drain paths,
protected A4 fasteners and replaceable polyester cord detailed in
[R3-rail.md](R3-rail.md). An open ladder has no closed mitred ring, but protected
ends must still admit water and release air. Preserve access to every upper
termination through removable decking or an accessible designed fixing.

## One-side prototype allowance and decision

| Item | One illustrated module |
| --- | --- |
| Main rails | 2 × 2,100 mm, 38 × 38 × 5 mm GRP |
| Crossbars | 2 basket bars + 2 end ties, nominal 230 mm, 25 × 25 × 3 mm GRP |
| Crossings | 8, each with paired attached keepers and an uplift binding |
| Suspension study | 8 upper joist stations, each with two lower legs; incomplete force system |
| Basket | 1 B28 with four removable ties |

First decide whether there is a simple acceptable source of the missing
horizontal and roll restraint. If there is none, stop R4 development here.
If one is proposed, test that complete detail on dry ground, including full
drained load, an eccentric basket, handling uplift and one lost support. Only
then resolve the corners, full planting layout and reactions against the load
envelope in [design-C.md](design-C.md).

Renders are in [r4](../../../diagrams/output/r3-double-rail/r4/)
