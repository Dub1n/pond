# Pack C ring member and selected corner study

This calculation supports the corner prototype in
[corner.md](../packs/c/corner.md). It screens the 38 mm GRP ring sides, corner
actions and the selected paired 12 mm triangular plan webs. It is not a deck or
batch-fabrication approval.

Run the arithmetic with:

```bash
./.venv/bin/python docs/calcs/ring_corner_study.py
```

## Actions from the cord arrangement

At a straight support, the top-centred lower eye and selected upper force line
give:

```text
horizontal / vertical = 100 / 319.5 = 0.313
```

The 0.60 kN heavy-side input therefore pushes one 2.1 m side outward by about
0.188 kN. The former normalized geometry gave 0.243 kN; retain that as the
conservative coordinate/assembly sensitivity. The crossed cords add along-side
restraint but do not remove this radial component.

For the current 0.188 kN uniformly distributed side action:

| End idealisation | End or maximum moment | End shear |
| --- | ---: | ---: |
| Pinned | 0.049 kN m maximum at midspan | 0.094 kN |
| Fully fixed | 0.033 kN m at each end | 0.094 kN |

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
| Pinned | 7.6 MPa / 10.9 mm | 10.3 MPa / 14.7 mm |
| Fully fixed | 5.1 MPa / 2.2 mm | 6.9 MPa / 2.9 mm |

For the 5 mm rail, rotational springs at both ends illustrate why joint
stiffness governs:

| Corner rotational stiffness | Side movement | End moment attracted |
| ---: | ---: | ---: |
| 0.1 kN m/rad | 10.5 mm | 1.6 N m |
| 0.5 kN m/rad | 9.1 mm | 6.6 N m |
| 1 kN m/rad | 8.0 mm | 11.0 N m |
| 5 kN m/rad | 4.6 mm | 23.5 N m |
| 20 kN m/rad | 3.0 mm | 29.9 N m |
| Perfectly fixed | 2.2 mm | 32.9 N m |

The section stiffness scale `2EI/L` is about 1.98 kN m/rad. A corner needs
about 18 kN m/rad to attract 90% of the fixed-end moment. Use a complete-joint
minimum of **20 kN m/rad after bedding**; strength without this stiffness does
not pass.

## Why the 12 mm triangular plan web is selected

The predecessor joint used 170 x 170 x 6 mm L plates, 50 mm arms and two M6
bolts per leg only 60 mm apart. Its force scale was plausible, but about 0.5 mm
relative settlement across the top/bottom path could cause roughly 0.65 degrees
of roll dead band. Its installed stiffness was unknown.

The next 220 x 70 x 8 mm paired-strip proposal improved the outer-bolt pitch to
140 mm, but a deliberately low-modulus strip estimate was only 18.7 kN m/rad
even before bolt and bedding compliance. It was too close to the target.

The selected prototype uses two 12 mm triangular plan-web plates, 220 mm reach,
80 mm rail-contact strips and three M8 bolts per leg at 55, 125 and 195 mm.
The continuous diagonal part is a horizontal web between the two strips, not a
vertical fin. A low-modulus paired-strip estimate gives **41.9 kN m/rad before
connection compliance**, leaving roughly a factor of two for the real joint to
meet the 20 kN m/rad test threshold.

With 8.5 mm maximum holes and 140 mm outer pitch:

| Screen | Selected result |
| --- | ---: |
| 60 N m plan action: outer-bolt force | 0.429 kN |
| 30 N m roll action: plate force | 0.600 kN |
| Conservative vector combination | 0.737 kN |
| Plate bearing at vector force | 7.2 MPa |
| Two-wall tube bearing at vector force | 8.7 MPa |

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

## Direct corner support

The selected upper corner eye is mounted on a C2 side face with its complete
base behind the timber tip. Its base centre is 55 mm behind the tip and the
nominal articulated-eye tangent is 41.5 mm outside the joist centreline. The
358.07 mm cord therefore has 200.75 mm plan offset and 296.5 mm vertical drop.
A 0.30 kN line proof resolves to approximately **0.248 kN vertical and
0.168 kN horizontal**. The larger horizontal component must be included in the
corner and deck tests; it is accepted to remove the impossible 141.4 mm
cantilever beyond the timber.

The four direct corner cords replace the former eight J1/J8 cords. Together
with 24 middle gravity cords and 16 crossed stabilisers, the 44-cord rigid-ring
screen remains rank 6, finds feasible equilibrium after any one cord is removed
and has a worst screened individual cord of 0.100 kN in the free-length
sensitivity. See
[rail-support-study.md](rail-support-study.md).

## What the calculation cannot close

The following remain physical or system gates:

- bolt-hole clearance, bedding, laminate through-thickness response and wet
  creep;
- the complete plan and roll moment-rotation curve, including one loosened
  fastener and one ineffective corner;
- rail breathing and cord redistribution using that measured curve;
- the side-mounted C2 eye connection, existing diagonal-joist connections and
  their complete route into the deck and foundations;
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

Manufacturer values are comparison inputs only. The purchased tube and plate
need their own certificates and permanent-immersion basis.
