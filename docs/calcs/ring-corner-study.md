# Pack C ring member and selected corner study

This calculation supports the corner prototype in
[corner.md](../packs/c/corner.md). It screens the 38 mm GRP ring sides, corner
actions and the selected paired 9.5 mm compact triangular plan webs. It is not a deck or
batch-fabrication approval.

Run the arithmetic with:

```bash
./.venv/bin/python docs/calcs/ring_corner_study.py
```

## Actions from the cord arrangement

At a straight support, the provisional direct-wrap force line gives:

```text
horizontal / vertical = 135 / 338 = 0.399
```

The 0.60 kN heavy-side input therefore pushes one 2.1 m side outward by about
0.240 kN. This is provisional because the real upper tangent around the joist
has not been measured. Moving the wrap farther from the tip increases this
action. The crossed cords add along-side restraint but do not remove the radial
component.

For the provisional 0.240 kN uniformly distributed side action:

| End idealisation | End or maximum moment | End shear |
| --- | ---: | ---: |
| Pinned | 0.058 kN m maximum at midspan | 0.111 kN |
| Fully fixed | 0.039 kN m at each end | 0.111 kN |

Retain three side-torque inputs: 5 N m for one 100 N basket at 50 mm
eccentricity, 20 N m for four such baskets and 30 N m as the deliberate
full-side bound. A one-corner-effective case sends the complete torque toward
one remaining corner.

## Ring-side section

The model uses longitudinal modulus `E=17 GPa` and conservative shear modulus
`G=3 GPa`.

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

The 5 mm gross section is plausible under the stated vertical screens.
Connections, wall bearing and wet creep remain separate checks.

### Torsion with effective corners

| Total side torque | 5 mm: two / one corner rotation | 3.2 mm: two / one corner rotation |
| --- | ---: | ---: |
| 5 N m | 0.28 / 0.56 deg | 0.37 / 0.74 deg |
| 20 N m | 1.12 / 2.23 deg | 1.49 / 2.97 deg |
| 30 N m | 1.67 / 3.35 deg | 2.23 / 4.46 deg |

At 30 N m, the 5 mm tube's calculated torsional shear is about 1.38 MPa with
two effective corners and 2.75 MPa with one. Service rotation is more important
than gross tube stress in this screen.

### In-plane breathing

| Side-end idealisation | 5 mm stress / movement | 3.2 mm stress / movement |
| --- | ---: | ---: |
| Pinned | 9.8 MPa / 13.9 mm | 13.2 MPa / 18.7 mm |
| Fully fixed | 6.5 MPa / 2.8 mm | 8.8 MPa / 3.7 mm |

For the 5 mm rail, rotational springs at both ends illustrate why joint
stiffness governs:

| Corner rotational stiffness | Side movement | End moment attracted |
| ---: | ---: | ---: |
| 0.1 kN m/rad | 13.3 mm | 2.0 N m |
| 0.5 kN m/rad | 11.6 mm | 8.4 N m |
| 1 kN m/rad | 10.2 mm | 14.1 N m |
| 5 kN m/rad | 5.9 mm | 30.0 N m |
| 20 kN m/rad | 3.8 mm | 38.2 N m |
| Perfectly fixed | 2.8 mm | 41.9 N m |

The section stiffness scale `2EI/L` is about 1.98 kN m/rad. A corner needs
about 18 kN m/rad to attract 90% of the fixed-end moment. Use a complete-joint
minimum of **20 kN m/rad after bedding**; strength without this stiffness does
not pass.

## Why the 9.5 mm compact triangular plan web is selected

The predecessor joint used 170 x 170 x 6 mm L plates, 50 mm arms and two M6
bolts per leg only 60 mm apart. Its force scale was plausible, but about 0.5 mm
relative settlement across the top/bottom path could cause roughly 0.65 degrees
of roll dead band. Its installed stiffness was unknown.

The next 220 x 70 x 8 mm paired-strip proposal improved the outer-bolt pitch to
140 mm, but a deliberately low-modulus strip estimate was only 18.7 kN m/rad
even before bolt and bedding compliance. It was too close to the target.

The selected prototype uses two 9.5 mm compact triangular plan-web plates, a
220 mm reach, 80 mm rail-contact strips and three M8 bolts per leg at 55, 125
and 195 mm. It removes only the inside-corner triangle bounded by the new
diagonal from `(-40,40)` to `(40,-40)`: the first bolt and washer are still in
the full-width strip, while the outer diagonal web is unchanged. A low-modulus
paired-strip estimate gives **33.2 kN m/rad before connection compliance**.
To achieve the 20 kN m/rad wet-joint threshold, the combined bolt/bedding path
must demonstrate at least 50.4 kN m/rad in series. This is why the first corner
must be tested rather than batch-cut.

The compact outline rotates and nests in a 200 x 9.5 x 3,000 mm flat bar. Eight
alternating 45/225-degree webs require about 2,506.4 mm including 5 mm end trim
at both ends and 5 mm clear between adjacent outlines. It is a stock-saving
geometry change, not a stiffness credit: the wet corner test must detect any
compliance introduced by the tapered first 40 mm of each rail-contact strip.

At the same 220 x 80 mm outline, 8 mm gives only 27.9 kN m/rad before
connection compliance and would require 70.5 kN m/rad from the connection path
to reach the target. Do not use it. Twelve millimetres gives 41.9 kN m/rad and
needs 38.3 kN m/rad from the connection path, but no demonstrated corner action
requires that extra plate once the 10 mm prototype passes its wet test.

With 8.5 mm maximum holes and 140 mm outer pitch:

| Screen | Selected result |
| --- | ---: |
| 60 N m plan action: outer-bolt force | 0.429 kN |
| 30 N m roll action: plate force | 0.632 kN |
| Conservative vector combination | 0.763 kN |
| Plate bearing at vector force | 9.5 MPa |
| Two-wall tube bearing at vector force | 9.0 MPa |

These are demand calculations, not design resistances. The accepted plate
certificate must support in-plane properties in both directions, diagonal
reinforcement, pin bearing, open-hole behaviour and permanent fresh-water
immersion. The complete connection also needs its wet coupon and moment-
rotation tests. `corner.md` gives the plate polygon, sleeves, bolt stack and
release criteria.

## Fallback R5.1 movement-stop hole

The selected R5.1 prototype uses a no-hole strap stop, so this drilled detail
is now a fallback only. If the strap test fails, one transverse stop may use an
8 mm outside-diameter full-width bush through the two vertical walls of the
38 x 38 x 5 mm tube. At the section through its axis, a simple gross-section
subtraction gives:

| Local section screen | Result |
| --- | ---: |
| Gross area removed | 80 mm² of 660 mm² = 12.1% |
| Vertical-bending second-moment loss | 0.35% |
| Horizontal in-plane second-moment loss | 17.9% |

The vertical loss is small because the hole is at rail mid-height; the
horizontal loss is larger because it perforates both side walls near the
extreme fibres for that bending axis. More importantly, the holes interrupt
the closed-wall torsional shear path. The bush can prevent wall crushing and
provide a controlled bearing surface, but this screen does **not** credit it
with restoring closed-section torsion.

The fallback detail therefore uses one stop-bush station per seat, not two.
It remains subject to the actual profile maker's hole/ligament rules and wet
open-hole, horizontal-bending and torsion coupon tests. It is a quantified
fallback compromise, not a claim that drilling has no effect.

## Direct corner sling

Each C2 support is now one continuous cord wrapped around the diagonal joist
and terminated at the existing 55 mm bolt axis on each adjacent rail leg. This
introduces the support into both sides of the stiff corner without a separate
fitting or new plate hole. Unequal leg tension can add a local corner moment,
so the joint test must include biased sharing as well as the symmetric case.

The provisional rigid-ring model uses a 35 mm C2 wrap backset and two smooth
cord-post tangents at `Z=-203 mm`. With the 24 gravity loops and one crossed
pair per side, it remains rank 6 and finds feasible equilibrium with every
complete cord item removed in turn. Replace the provisional tangents with the
measured wrap geometry before using its force envelope. See
[rail-support-study.md](rail-support-study.md).

## What the calculation cannot close

The following remain physical or system gates:

- bolt-hole clearance, bedding, laminate through-thickness response and wet
  creep;
- the complete plan and roll moment-rotation curve, including one loosened
  fastener and one ineffective corner;
- rail breathing and cord redistribution using that measured curve;
- the direct C2 wrap, upper-face stop, two lower posts, existing diagonal-joist
  connections and their complete route into the deck and foundations;
- the R5.1 seat reaction envelope and measured drain-down masses; and
- the five still-TBC deck limits in [design-C.md](../packs/c/design-C.md).

This is why the dimensions in `corner.md` are issued for one prototype corner
first, followed by the four-corner batch only after its release gates pass.

## Property basis

- [Fiberline's EN 13706 summary](https://fiberline.com/european-standard-en-13706)
  gives the contextual E17 minima: 17 GPa longitudinal modulus, 90/50 MPa
  longitudinal/transverse pin bearing and 15 MPa longitudinal shear.
- [Fiberline's material comparison](https://fiberline.com/media/asmaipxx/fiberline_product_comparison.pdf)
  gives the representative 3 GPa shear modulus used in the tube sensitivity.

Manufacturer values are comparison inputs only. The purchased tube and flat bar
need their own certificates and permanent-immersion basis. Do not substitute
[RG1000/recycled UHMWPE](https://www.directplastics.co.uk/pdf/datasheets/RG1000-black-green-data-sheet.pdf):
its approximately 0.9 GPa modulus and high creep make it suitable for wear
parts, not these stiffness-critical structural webs.
