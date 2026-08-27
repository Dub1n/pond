# Option C geometry (1 m backspan, 350 mm pond overhang)

This file records the as-built dimensions represented by `option-c.yaml`. Coordinates below are measured from the north or west outside face of the 5 m deck frame, as appropriate, and apply to every side by rotation.

## Principal dimensions

- Deck outer frame: 5 000 × 5 000 mm.
- Pond: 3 000 × 3 000 mm, centred in the deck; pond edges are 1 000 mm from the deck perimeter.
- Decking overhang: 350 mm inward from every pond edge.
- Finished central opening: 2 300 × 2 300 mm (`3 000 − 2 × 350`).
- Walkway joist backspan: 953 mm between the inside face of the 47 mm outer beam and the pond-edge beam line.
- Joist projection beyond the inner beam: 350 mm.
- Total straight walkway-joist length: 1 303 mm (`953 + 350`).
- Decking: nine concentric 150 mm rows, with outside segment lengths 5 000, 4 700, 4 400, 4 100, 3 800, 3 500, 3 200, 2 900, and 2 600 mm.

## Straight joists along each side

There are eight 47 × 75 mm straight joists per side. Their centre positions along the 5 m outer beam are:

| Joist | Centre from end (mm) | Gap to next centre (mm) |
| ----: | -------------------: | ----------------------: |
|     1 |              1 273.5 |                   386.7 |
|     2 |              1 660.2 |                   419.9 |
|     3 |              2 080.1 |                   311.4 |
|     4 |              2 391.5 |                   217.0 |
|     5 |              2 608.5 |                   311.4 |
|     6 |              2 919.9 |                   419.9 |
|     7 |              3 339.8 |                   386.7 |
|     8 |              3 726.5 |                       — |

Joists 4 and 5 replace the former single joist at 2 500 mm. Their inside faces are 170 mm apart: each centre is `170 ÷ 2 + 47 ÷ 2 = 108.5 mm` from the deck centreline. The other six joist centres have not moved. The largest straight-joist spacing is approximately 420 mm centre-to-centre.

These along-beam centres are deliberately independent of the overhang dimension in the YAML. Changing the joist projection must not move the already-built joists sideways.

## Other plan components

- Outer and inner beams are 47 × 150 mm and share the joist top elevation.
- The outer-to-inner corner diagonal remains approximately 1 281 mm long.
- Each diagonal from the inner beam corner to the 350 mm overhang corner is approximately 495 mm (`350 × √2`).
- Two 47 × 75 mm corner ties per corner meet the diagonal 500 mm from the outer corner.
- The perimeter pad positions continue to align with joists 2 and 7 at about 1 660 and 3 340 mm from the end of each outer beam.
- The deck surface is 28 mm thick in the model. Its opening is the 2 300 mm square described above.

## Section datums

- The deck underside is at the top of the 150 mm beams.
- Straight walkway joists are 75 mm deep in the current design; their tops align with the beam and decking underside.
- Pads in `option-c.yaml` are 600 × 600 × 50 mm.
- Pond water and surrounding soil are modelled to 900 mm depth.

## Calculation status

Earlier structural notes used a 250 or 340 mm projection and seven uniformly spaced joists. Those load, uplift, and deflection results are not valid for this as-built 350 mm/eight-joist arrangement unless explicitly recalculated. `joist-depth-checks.md` and `uplift-pad-check.md` are marked accordingly; an engineering issue of those documents should use the 1 303 mm total joist length and the actual irregular tributary widths above.
