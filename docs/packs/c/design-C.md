# Pond deck design C — current state

## Project state

As at 11 September 2026, the deck structure is built through the framing stage.
The pads, beams, joists, blocking, bracing and corner framing are in place. **The
decking boards have not been installed.** The open framing is deliberate and
must be kept accessible while the submerged planting rail is surveyed,
prototyped and attached.

The remaining work is the selected connected ring and R5.2 planting system defined
by [rail-development-status.md](rail-development-status.md),
[corner-v2.md](corner-v2.md), [cords.md](cords.md), [R5.2.md](R5.2.md) and
[plants-v2.md](plants-v2.md). R3, R4 and R5 remain predecessor studies, not
alternative construction instructions. The old deck calculation pack, method
statement, inspection plan and construction checklists are historical records
in `docs/packs/archive/`; they are not active instructions for the remaining
work.

The active construction and test sequence is intentionally not duplicated
here; it is controlled by [install-walkthrough.md](install-walkthrough.md).

## As-built deck interface

The following is the retained interface for the work still to come. It records
the framing that the rail will load; it is not a checklist for rebuilding or
rechecking completed work.

| Item                  | As-built or intended condition                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Overall deck / pond   | 5,000 × 5,000 mm deck around a centred 3,000 × 3,000 mm pond                                                                   |
| Finished opening      | 2,300 × 2,300 mm after the 350 mm inward deck overhang                                                                         |
| Straight joists       | Eight per side, 47 × 75 mm C24 UC4 softwood                                                                                    |
| Joist geometry        | 953 mm between beam faces, plus 350 mm projection; 1,303 mm total length                                                       |
| Joist centres         | 1,273.5, 1,660.2, 2,080.1, 2,391.5, 2,608.5, 2,919.9, 3,339.8 and 3,726.5 mm from each beam end                                |
| Maximum joist pitch   | Approximately 420 mm; the centre pair has 170 mm clear between inside faces                                                    |
| Beams                 | 47 × 150 mm C24 UC4; inner and outer beam tops flush with joist tops                                                           |
| Inner connection      | Rebated top-flange saddle hanger, top strap, opposed toe-screws and tight blocking                                             |
| Outer connection      | Face-mount hanger, tight blocking and outer flat-strap bracing                                                                 |
| Supports              | 600 × 600 × 50 mm slabs on compacted gravel and geotextile, DPC before timber; intermediate supports align with joists 2 and 7 |
| Decking still to fit  | 28 × 145 mm boards, 5–6 mm gaps, 20–30 mm outside overhang and 1–2% fall away from the pond                                    |
| Shared vertical datum | Water surface and pad tops at Z = 0; beam and joist tops +150 mm, joist undersides +75 mm, nominal deck top +178 mm            |

The water volume remains 900 mm deep, so the modelled pond bottom is Z =
−900 mm. Rail studies use Z = 0 as the minimum-water design reference; verify
operational water variation during the survey. This datum is shared with
`option-c.yaml` and all three rail models.

The selected suspension uses straight joists J2--J7 on every side plus the four
existing C2 diagonal corner joists. Record every actual attachment point and
the horizontal and vertical offset to the rail; sloping supports add horizontal
reaction as well as vertical load.

## Access that must be preserved before decking

Fit and test the direct upper cord wraps and upper-face timber stops while the
joists are exposed. Do not close the deck until each wrap, knot, stop and
witness mark can be inspected and replaced. Provide documented removable
boards with smooth underside relief over every cord and stop. A cord wrap
trapped behind permanent decking is not an acceptable service detail.

Before laying boards, use the real board edge or a full-size mock-up to prove
that every basket can move inward far enough to clear the 350 mm overhang and
be lifted without disturbing the ring, liner or neighbouring baskets. Also
confirm that no board screw or edge detail can damage a support cord.

## Retained load envelope for rail development

Do not carry the old deck worksheets into the rail design and do not quote a
single member-only “joist capacity”. The useful long-term record is an approved
load envelope derived once from the complete load path. For each limit below,
use the lowest spare capacity of the joist, inner and outer connections, beam,
bracing where relevant, and supporting slab/ground after allowing for the deck
dead load and imposed deck load.

| Limit to record after the current-geometry check                                    | Approved characteristic load |
| ----------------------------------------------------------------------------------- | ---------------------------: |
| Maximum permanent downward load at any one rail support                             |                   **TBC kN** |
| Maximum permanent horizontal load at any one rail support, in either plan direction |                   **TBC kN** |
| Maximum combined permanent downward load on any two adjacent supports               |                   **TBC kN** |
| Maximum total permanent downward rail-and-plant load on one pond side               |                   **TBC kN** |
| Maximum temporary upward/handling load at one support                               |                   **TBC kN** |

These values are deliberately still TBC. The archived calculations used seven
joists and a 250 mm projection, while the installed frame has eight joists and
a 350 mm projection. They also did not contain verified capacities for the
selected hangers, straps, toe-screws or ground support, so they cannot establish
a safe residual capacity.

Retain this compact calculation basis when the envelope is set. These are
inputs, not proof that the installed load path passes:

| Design input                                             |     Retained value |
| -------------------------------------------------------- | -----------------: |
| C24 characteristic bending strength, `fm,k`              |           24 N/mm² |
| C24 characteristic shear strength, `fv,k`                |          2.5 N/mm² |
| C24 mean modulus parallel to grain, `E0,mean`            |       11,000 N/mm² |
| 47 × 75 mm joist second moment of area, strong axis      |    1.652 × 10⁶ mm⁴ |
| 47 × 75 mm joist section modulus, strong axis            |         44,063 mm³ |
| Timber service class                                     |                  3 |
| Permanent-action `kmod` / `kdef` / timber `γM`           | 0.50 / 2.00 / 1.30 |
| Permanent / leading variable action factors, `γG` / `γQ` |        1.35 / 1.50 |
| Characteristic deck imposed load, `Qk`                   |          3.0 kN/m² |
| Adopted walking-surface deflection limit                 |              L/250 |

Rebuild the deck dead load from the actual 47 × 75 framing, selected boards
and installed details. Do not reuse the archived 0.457 kN/m² total unchanged:
its framing allowance was based on 47 × 150 joists.

Set the envelope once using these inputs:

- actual 47 × 75 mm joists, 953 mm backspan, 350 mm projection, irregular
  tributary widths and measured rail attachment positions;
- actual beam support positions, slab arrangement, ground condition and all
  rail reactions on an edge at the same time;
- actual hanger, strap, screw and fastener products and their installation;
- the final decking dead load and the retained 3.0 kN/m² characteristic deck
  imposed load;
- Service Class 3 timber design, treating the installed rail, wet media and
  plants as a permanent action with the appropriate permanent-load strength
  modification, rather than reusing the medium-term factor from the former
  deck imposed-load check;
- vertical and horizontal reactions from the measured support angles; and
- the fully soaked, out-of-water mass of every completed basket plus its share
  of rail, seats and cords. This drain-down case governs the gravity input;
  submerged apparent weight does not.

Check ULS member and connection resistance, SLS movement/creep, inner-beam
reaction, outer uplift, combined beam loading and support bearing/uplift. Once
accepted, replace the five TBC entries above with the governing values and a
short identification of the governing component. Later rail changes then only
need to demonstrate that their reactions remain inside this envelope.

For the current comparison screen, four nominal 10 kg drained baskets plus
about 5–6 kg of rail and seats on one side produce roughly 0.45 kN total
downward load. Upper reactions remain provisional until the direct-wrap
tangents are measured. The
specified **0.3 kN proof test for one completed cord support is a connection
test, not evidence that the deck has 0.3 kN spare capacity at every joist.**
Use measured masses and the approved envelope for the final decision.

## Rail and plant coordination gates

The R5.2/corner-v2 ring is selected for survey and prototype, not batch
fabrication. The remaining deck decision depends on these recorded inputs:

- the completed framing, liner, intended board edge, water levels and available
  post-deck inspection/removal opening;
- final 2,100 mm ring position and all thirteen basket positions;
- real B23 and B27 tops, reinforced bases, taper, retention zones, cartridges,
  apparent underwater weights and fully soaked drained masses;
- the 45-degree corner-basket template including C2 posts, washers, sleeved
  cord turns and removal travel;
- the selected GRP profile's directional and permanent-immersion information;
- measured suspension tangents, settled axial stiffness, complete-item loss
  cases and corner-v2 stiffness; and
- final vertical/horizontal rail reactions compared with the five TBC deck
  limits above.

The rail carries ten B23 and three B27 baskets. The lily basket, hornwort cage
and two moss slates remain independent. Crown depths, media, ballast, guards,
plant allocation and maintenance are controlled by
[plants-v2.md](plants-v2.md).

Continuing acceptance requires submerged rims/GRP at minimum normal water,
scheduled crown depths, no progressive seat or corner movement, retained
basket/cartridge recovery, complete rail flooding/drainage, smooth fish-safe
surfaces and reactions within the approved deck envelope. Keep a connected
central swimming/cleaning route and roughly 70–80% open water.

All construction, test, lowering, adjustment and inspection procedure is in
[install-walkthrough.md](install-walkthrough.md).
