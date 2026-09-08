# Pack C ring member and corner study

This calculation follows the cord-layout screen in `rail-support-study.md`.
It asks whether the existing 38 mm GRP sides and bolted corners can plausibly
distribute the cord forces and basket torque without separate local roll
restraint. It also screens larger corner gussets and the proposed lower-H seat
suspension concept.

This is a comparison calculation, not fabrication approval. The selected tube
and plate products, wet long-term properties, drilled-connection rules and
joint stiffness remain required.

The reproducible arithmetic is in `ring_corner_study.py`.

## Governing actions from the cord arrangement

For the proposed high pond-facing joist-end point, the outward horizontal and
vertical components have the ratio:

```text
H / V = 100 / 356.5 = 0.281
```

The heavy-side comparison load of 0.60 kN therefore pushes its 2.1 m rail side
outward by approximately 0.168 kN. The former normalized 128/316 line remains
a conservative sensitivity at 0.243 kN, not the active coordinate. Crossed cords add along-side restraint but
do not remove this radial component. All four sides tend to expand toward their
respective joists, so the ring and corners must control square-plan breathing.

For a uniformly distributed current 0.168 kN side action:

| End idealisation | End or maximum moment | End shear |
| --- | ---: | ---: |
| Pinned | 0.044 kN m maximum at midspan | 0.084 kN |
| Fully fixed | 0.030 kN m at each end | 0.084 kN |

The real bolted corners lie between these idealisations and may include a slip
dead band. These actions are preferable corner design inputs to treating the
whole 0.168 kN as an unexplained corner point load.

The torsion cases are:

- 5 N m: one 100 N basket at 50 mm eccentricity;
- 20 N m: four such baskets on one side eccentric in the same direction; and
- 30 N m: deliberately conservative application of the full 0.60 kN side
  envelope at 50 mm eccentricity.

For symmetric positions, two effective corners share the total torsion. A
one-corner-effective case conservatively sends the complete torque toward the
remaining corner. Handling uplift remains a separate, tension-only problem.

## Ring-side section

The model uses the documented longitudinal modulus `E=17 GPa` and a
conservative shear modulus `G=3 GPa`. The latter agrees with Fiberline's
published representative shear modulus. The closed-section torsion constant is
calculated using the thin-wall median-line expression.

| Property | 38 x 38 x 5 | 38 x 38 x 3.2 |
| --- | ---: | ---: |
| Area | 660 mm2 | 445 mm2 |
| Second moment `I` | 122,540 mm4 | 90,668 mm4 |
| Approximate torsion constant `J` | 179,685 mm4 | 134,861 mm4 |

### Vertical bending and support loss

| Case | 5 mm stress / movement | 3.2 mm stress / movement |
| --- | ---: | ---: |
| 100 N at 420 mm | 1.63 MPa / 0.07 mm | 2.20 MPa / 0.10 mm |
| 200 N at 840 mm | 6.51 MPa / 1.19 mm | 8.80 MPa / 1.60 mm |
| 300 N at 840 mm | 9.77 MPa / 1.78 mm | 13.20 MPa / 2.40 mm |

The gross section is in a plausible range under vertical gravity and one lost
support. Connections, local wall bearing and wet creep are not represented.

### Torsion if the corners are effective

| Total side torque | 5 mm: two / one corner rotation | 3.2 mm: two / one corner rotation |
| --- | ---: | ---: |
| 5 N m | 0.28 / 0.56 deg | 0.37 / 0.74 deg |
| 20 N m | 1.12 / 2.23 deg | 1.49 / 2.97 deg |
| 30 N m | 1.67 / 3.35 deg | 2.23 / 4.46 deg |

At 30 N m, the 5 mm tube's calculated torsional shear is approximately
1.38 MPa when two corners share it and 2.75 MPa when one carries it. These are
not high compared with the 15 MPa minimum longitudinal shear strength reported
for an EN 13706 E17 structural pultrusion, but no environmental or design
factors have been applied.

The tube is therefore more likely to be governed by service rotation than
gross torsional strength. The original isolated 5 N m case is comfortable in
this idealisation; four concurrently eccentric baskets are materially more
demanding.

### In-plane breathing

| Side-end idealisation | 5 mm stress / movement | 3.2 mm stress / movement |
| --- | ---: | ---: |
| Pinned | 6.9 MPa / 9.7 mm | 9.3 MPa / 13.2 mm |
| Fully fixed | 4.6 MPa / 1.9 mm | 6.2 MPa / 2.6 mm |

This is the strongest reason not to approve either section from the former
420 mm vertical-span calculation. A nearly pinned square may breathe by a
visibly unacceptable amount even while stresses remain modest. The corner's
in-plane rotational stiffness determines whether the result is near 2 mm or
near 10--13 mm. The former 0.243 kN sensitivity retains the earlier 2.8 and
14--19 mm bounds.

For the 5 mm rail, an equal end rotational spring illustrates how demanding
“nearly fixed” actually is:

| Corner rotational stiffness | Side movement | End moment attracted |
| ---: | ---: | ---: |
| 0.1 kN m/rad | 9.4 mm | 1.4 N m |
| 0.5 kN m/rad | 8.2 mm | 5.9 N m |
| 1 kN m/rad | 7.1 mm | 9.9 N m |
| 5 kN m/rad | 4.2 mm | 21.1 N m |
| 20 kN m/rad | 2.7 mm | 26.8 N m |
| Perfectly fixed | 1.9 mm | 29.5 N m |

This linear beam-and-spring sensitivity omits joint slip. It shows that modest
gusset stiffness is not enough to make the side behave fixed; the joint must be
very stiff relative to the rail, and even the perfect bound is slightly above
the former approximate 2 mm movement target.

### Upper attachment position is an effective lever

The user-authorised attachment freedom permits a better response than merely
making the corner heavier. Moving the upper force line pondward and higher on
an accessible joist face reduces the outward component:

| Effective upper point, south side | `H/V` | Outward force at 0.60 kN | 5 mm rail movement, fixed / pinned |
| --- | ---: | ---: | ---: |
| Normalized screen: `Y=-1178, Z=+72` | 0.405 | 0.243 kN | 2.8 / 14.1 mm |
| Tip underside: `Y=-1150, Z=+72` | 0.316 | 0.190 kN | 2.2 / 11.0 mm |
| Tip side-face mid-depth: `Y=-1150, Z=+112.5` | 0.281 | 0.168 kN | 1.9 / 9.7 mm |

The side-face position is structurally preferable at system level, provided a
through-fastened A4/316 eye or cheek detail can apply the inclined reaction
without relying on screws into joist end grain, splitting the timber, or
becoming inaccessible after decking. Cord clearance around the joist tip and
deck edge must be drawn. The exact eye position should replace the current
effective coordinate in the cord model once a termination arrangement is
chosen.

## Existing corner action screen

The R3 corner has one 170 x 170 x 6 mm L plate above and below the mitred tube,
50 mm-wide arms, and two M6 bolts per leg at 60 and 120 mm from the theoretical
corner.

The current high-face geometry gives about 29.5 N m at a perfectly fixed end.
The 45 N m working screen and 60 N m bound below are deliberately retained to
cover coordinate tolerance, uneven sharing and the former steeper cord line.

For roll transfer, the top and bottom plates form a force couple about 44 mm
apart. For in-plane moment, the two bolt rows are 60 mm apart. Conservative
one-bolt bearing values are shown to establish scale; they are not connection
resistances.

| Corner action | Existing 6 mm L result |
| --- | ---: |
| 15 N m roll, shared 30 N m side case | 0.341 kN plate force; 8.7 MPa one-bolt bearing |
| 30 N m roll, one-corner case | 0.682 kN; 17.5 MPa |
| 45 N m in-plane moment | 0.750 kN bolt-row force; 19.2 MPa |
| 60 N m in-plane bound | 1.000 kN; 25.6 MPa |

For context only, EN 13706 E17 minimum pin-bearing values are 90 MPa
longitudinal and 50 MPa transverse. The comparison stresses are below those
unfactored minima, suggesting that gross plate bearing is in the right range.
They do not cover tube-wall bearing, net section, cleavage, washer indentation,
plate bending, cross-axis fibre layout, wet creep or bolt preload.

The major stiffness uncertainty is clearance and settlement. A 0.5 mm relative
slip across the approximately 44 mm top/bottom couple corresponds to about
0.65 degrees of roll dead band before elastic plate behaviour is considered.
A full millimetre corresponds to about 1.3 degrees. Similarly, bolt clearance
within the 60 mm in-plane group can materially reduce the fixed-corner benefit.

The current corner is therefore **not shown insufficient**, but neither is it
shown stiff enough. Its indicative force scale is plausible; joint slip and
ring breathing are the likely decision variables.

## Gusset comparison

Four concepts were screened:

| Variant | Roll bearing at 30 N m | Plan bearing at 60 N m | Main effect |
| --- | ---: | ---: | --- |
| Existing L170 x 50 x 6, 60 mm bolt pitch | 17.5 MPa | 25.6 MPa | Baseline |
| Square 170 x 170 x 6, same bolts | 17.5 MPa | 25.6 MPa | More plan material but no better lever |
| Radiused L220 x 70 x 8, 140 mm outer-bolt pitch | 12.5 MPa | 8.2 MPa | Better plate stiffness and bolt leverage |
| Triangular-web 220 x 8, same outer pair | 12.5 MPa | 8.2 MPa | Direct plan web across elbow; preferred comparison |
| Square 220 x 220 x 8, same outer pair | 12.5 MPa | 8.2 MPa | Maximum plan diaphragm, largest shelf |

A square plate with unchanged bolt positions is not a meaningful roll upgrade:
it creates no new couple. It may improve in-plane load spreading and eliminate
the narrow L-shaped elbow, but adds weight, drag and a sediment shelf.

Increasing thickness from 6 to 8 mm raises direct section approximately 33%
and ideal plate-bending stiffness approximately 2.37 times. Extending the outer
bolt pitch from 60 to 140 mm reduces the screened in-plane outer-bolt force by
approximately 57%.
Those benefits apply only if the revised hole pattern is permitted in the tube.

The preferred next corner specimen is a **paired 8 mm triangular plan-web
gusset**, with the radiused L as the simpler comparison. Both use top and bottom
plates, a 220 mm overall reach and 70 mm rail-contact strips. The triangular
variant fills the inner elbow with continuous diagonal plan material; it is not
a separate vertical fin. It should distribute racking action better without
becoming a full square sediment shelf.

For the 38 x 38 x 5 mm side, `2EI/L` is about 1.98 kN m/rad. A corner needs
approximately 18 kN m/rad to attract 90% of the perfectly fixed end moment.
Adopt **20 kN m/rad** as the minimum near-fixed target and approximately
38 kN m/rad for 95%.

A deliberately low-modulus strip estimate for paired 220 x 70 x 8 mm plates
gives approximately 9--19 kN m/rad for the radiused L, depending on whether
one or two plate paths engage. It is close to, but does not securely exceed,
the target. The triangular web should prevent the narrow elbow controlling,
but its improvement requires actual laminate properties and a plate/connection
model before credit is taken.

Use a provisional long outer bolt pair on each leg at **55 and 195 mm** from
the theoretical corner, centred across the 70 mm strip. The 140 mm separation
is the important stiffness improvement. A third bolt at **125 mm** may add
direct-shear sharing and redundancy if supplier drilling guidance permits, but
it lies at the group centroid and adds little rotational leverage.

At the 60 N m in-plane bound, the long outer pair gives about 0.429 kN at each
outer bolt: approximately 8.2 MPa plate bearing and 6.6 MPa across the two 5 mm
tube walls. At 30 N m roll, the 46 mm top/bottom plate couple requires about
0.652 kN: approximately 12.5 MPa one-bolt plate bearing and 10 MPa across the
two tube walls. These remain unfactored comparison stresses.

Neither outline removes bolt-clearance dead band. An M6 bolt in a 6.5 mm hole
has approximately 0.25 mm radial clearance, equivalent to about 0.10 degrees
across the 140 mm outer pair before reliable bearing. Controlled close holes
with suitable smooth sleeves/bushes, or a supplier-approved bonded-and-bolted
joint, may matter more than further plate area. Do not credit wet long-term
preload friction.

The corner-only route requires a measured or product-supported secant stiffness
of at least 20 kN m/rad after bedding over 0--60 N m in-plane action, plus a
0--30 N m roll moment-rotation check. Strength alone does not satisfy this gate.

## Lower-H local suspension proposal

The proposed extension of the two lower bridges into a second H is
mechanically meaningful but does not yet justify promotion to R5.2.

A coherent version would retain R5.1's four rail-capture bolts and sleeves and
add four separate, sleeved cord-eye connections near the ends of aligned upper
and lower transverse arms. The capture sleeves beside the rail should not also
be assumed to be suitable rope eyes. Smooth replaceable A4/316 pins or eyes need
their own plate bearing, edge distance, washer and cord bend-radius checks.

Four legs, one at each H end, are preferable to two because they distribute
load between the two along-rail bearing stations and restrain pitch as well as
roll. Using provisional stations `x=+/-90...110 mm` and transverse eye lines
`y=+/-110 mm` gives a 220 mm roll lever within the current 280 mm clash
envelope.

For the 100 N, 5 N m expected pondward-eccentric case, the preliminary
four-leg equilibrium is approximately:

| Reaction | Result |
| --- | ---: |
| Pond-side pair | 72.7 N vertical total |
| Bank-side pair | 27.3 N vertical total |
| Largest individual leg | About 45.5 N tension |
| Combined bankward horizontal reaction | About 56 N |

The transparent two-line screen gives 72.7 N total vertical reaction on the
pond side and 27.3 N on the bank side. After resolving the inclined cords, the
largest leg tension is about 45.5 N and the combined bankward horizontal
reaction is about 56 N.

The ideal all-taut roll stiffness is about 691 N m/rad, implying 0.41 degrees
at 5 N m. That apparently good result is not robust: the bank-side legs carry
only about 13.7 N each and are predicted to unload after roughly 0.38 degrees.
The previous `+/-1.5 mm` free-length variation is enough to change a leg force
by approximately 28 N.

There is also a geometry conflict. A direct line from a pond-side eye at
`y=+110 mm` to the bankward joist line crosses the rail centreline around
`Z=-98 mm`, inside the assumed basket volume. Routing it around a basket end
requires longitudinal splay, creates additional along-side reactions and needs
a complete thirteen-seat clash drawing.

The executable screen does not yet solve the three-dimensional missing-leg
case. With one highly loaded pond-side leg unavailable, do not credit the
remaining three tension-only legs with maintaining both pitch and roll: their
feasibility depends on final along-rail eye coordinates, active cord set and
seat/ring contact. Treat the fault action as returning to the spine and corners
unless a later nonlinear model demonstrates otherwise. Handling uplift likewise
remains owned by basket retention and lower-plate bearing against the rail, not
the suspension cords.

Accordingly, do **not** create R5.2 yet. Retain the lower-H arrangement as a
hybrid candidate only. Promote it when a complete routing study shows that all
four cords clear the basket and removal path, and a nonlinear model shows how
the ring receives slack-leg and missing-leg actions. If the corner study later
shows acceptable movement, the simpler centreline/crossed-cord arrangement is
preferable.

## Decision and next analytical gate

The present evidence supports this order:

1. Retain 38 x 38 x 5 mm as the ring-study baseline; do not adopt 3.2 mm merely
   because its strength appears adequate.
2. Prefer an upper force line near the inner joist face at approximately
   `Y=-1150, Z=+112.5` in the south-side convention, subject to a valid
   through-fastened termination and clearance detail. This reduces breathing
   demand before adding GRP.
3. Model the square's in-plane breathing with the selected attachment point and
   measured or supplier-derived corner slip/stiffness. Use 0.168 kN as the
   current side action and retain 0.243 kN as a sensitivity.
4. Model 5, 20 and 30 N m torsion, including one ineffective corner. Use both
   rotation and stress criteria.
5. Compare the present corner against the paired 8 mm triangular plan web and
   radiused L, both with the long outer bolt pair. A 170 mm square with
   unchanged bolts is not a useful primary alternative.
6. Keep the lower-H suspension as a fallback hybrid, not a selected R5.2.

The next design decision is therefore still “adequate semi-rigid corners or
supplementary local roll restraint.” The calculations have not rejected the
corner-only route, but they show that its in-plane stiffness must be established
before relying on it.

## Property basis

- [Fiberline's EN 13706 summary](https://fiberline.com/european-standard-en-13706)
  gives the E17 minima used for context: 17 GPa
  longitudinal modulus, 90/50 MPa longitudinal/transverse pin bearing, and
  15 MPa longitudinal shear.
- [Fiberline's published material comparison](https://fiberline.com/media/asmaipxx/fiberline_product_comparison.pdf)
  gives a representative 3 GPa GRP shear modulus.
- Manufacturer values are comparison inputs only; the purchased profile and
  plate still need their own product data and permanent-immersion basis.

## Reproduction

```bash
./.venv/bin/python docs/calcs/ring_corner_study.py
```
