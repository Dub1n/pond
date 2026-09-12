# Pack C direct-loop suspension screen

## Purpose and status

`rail_support_study.py` is a transparent rigid-body comparison for the
low-cost direct-cord prototype in `docs/packs/c/cords.md`. It asks whether the
provisional cord directions can restrain all six rigid-ring motions and find a
tension-only equilibrium under the stated comparison loads.

The upper cord-wrap coordinates have not been measured. Results below are
therefore evidence that the topology is worth prototyping, not cutting lengths,
deck capacities or fabrication approval.

## Modelled arrangement

The selected prototype contains 36 cord items:

- 24 closed gravity loops at J2-J7;
- 8 closed crossed loops, one opposite-handed J2-J3 pair per side; and
- 4 continuous C2 corner slings.

A straight or crossed closed loop has two nearby physical legs. The rigid-body
screen represents their combined action with one conservative equivalent line
and assigns the whole loop an effective wet/knotted/bedded axial rigidity of
6 kN.

Each C2 sling is represented by two separate model legs, one to each existing
55 mm corner-bolt axis. Each leg receives half the loop rigidity and half the
10 N seating tension. Removing a corner sling removes both legs together.
This does not model sliding equalisation around the joist, knot bedding or
local corner-plate response.

## Provisional geometry

The fixed ring centreline is `X/Y=+/-1050 mm`. For a provisional screen only:

- straight and crossed upper wrap tangents are placed at radial coordinate
  1,185 mm, representing a wrap 35 mm behind the 1,150 mm joist-tip plane;
- their provisional effective height is the joist underside at `Z=+75 mm`;
- their lower equivalent point is at the rail underside at `Z=-263 mm`;
- each C2 wrap is provisionally 35 mm back along the diagonal from its tip;
- the two lower C2 points are 55 mm along the two rail legs; and
- their provisional cord-post tangent is `Z=-203 mm`.

These are not construction dimensions. The actual force tangent depends on
cord diameter, chafe sleeve, member corner radii, knot position and which faces
the two legs leave. Establish it using the real joist, upper-face stop and
relieved removable deck board. Moving the wrap farther from the pond increases
the horizontal reaction.

## Loads and assumptions

- ring treated as rigid;
- tension-only axial cord response;
- 10 N seating tension per complete cord item;
- `EA_eff=6 kN` per complete direct loop or sling;
- symmetric 1.80 kN drain-down;
- uneven side loads 0.60/0.45/0.30/0.45 kN;
- the uneven case plus a 5 N m south-seat torque;
- the uneven case plus 0.10 kN local handling uplift; and
- loss of each complete cord item in turn under uneven load plus torque.

The model does not include flexible rail sides, measured corner
moment-rotation behaviour, loop contact/friction, knot slip, timber indentation,
locating collars, stops, chafe, seat flexibility or the deck load path.

## Current provisional result

Run:

```bash
./.venv/bin/python docs/calcs/rail_support_study.py
```

At the provisional coordinates the script reports:

| Result | Value |
| --- | ---: |
| Cord items / model legs | 36 / 40 |
| Rigid-body rank | 6 of 6 |
| Matrix condition measure | 3.45 |
| Maximum listed-case model-leg tension | 94.5 N |
| Worst remaining leg after one complete item is unavailable | 117.2 N |
| Complete-item-unavailable cases with feasible equilibrium | 36 of 36 |
| Maximum listed-case rigid-body translation | 5.02 mm |
| Provisional upper downward / horizontal / resultant envelope | 108.5 / 64.0 / 126.0 N |

The modest forces leave ample gross rope-strength margin even after a knot,
but that does not validate knot security, bearing surfaces or the supporting
timber. Continue to proof each complete support item to 0.30 kN over dry ground.

## Required rerun

Before cord cutting or deck approval:

1. Record the two effective upper tangents of a real gravity loop and crossed
   loop around the chosen joist position.
2. Record both C2 upper tangents and both lower cord-post tangents.
3. Update the constants and, if the two legs separate materially, replace the
   equivalent straight/crossed lines with explicit paired legs.
4. Rerun every complete-item-loss case, including simultaneous loss of both
   legs of one C2 sling.
5. Feed the resulting reactions into the flexible-ring/corner model and the
   complete deck check.

The physical full-side test remains decisive for installed movement because
cord-wrap bedding and ring flexibility are outside this model.
