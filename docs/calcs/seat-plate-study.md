# Pack C R5.1 seat plate-thickness study

Run the local screen with:

```bash
./.venv/bin/python docs/calcs/seat_plate_study.py
```

This is a sizing comparison for the open H and its two lower bridges, not a
plate-design approval. It deliberately uses a 0.30 kN drained/localized basket
screen: more than twice the approximately 0.138 kN mean drain-down share in the
current 1.80 kN thirteen-seat ring screen, while the actual fully soaked
out-of-water basket mass is still unknown.

The model gives the largest nominal 280 mm basket a 121 mm outboard projection
from the edge of the 38 mm rail. It divides the load between two 50 mm-wide
arms, then checks one half arm as a uniformly loaded cantilever. It uses an
8 GPa low-direction modulus solely as a conservative screening input. A second
screen puts the complete 0.30 kN into one 56 mm M8-to-M8 lower bridge, although
the bridge is normally unloaded under gravity.

| Thickness | Upper-arm stress / movement | One lower bridge stress / movement | Sizing conclusion |
| ---: | ---: | ---: | --- |
| 5 mm | 21.8 MPa / 3.99 mm | 20.2 MPa / 0.26 mm | Fails the 2 mm movement screen. |
| 6 mm | 15.1 MPa / 2.31 mm | 14.0 MPa / 0.15 mm | Still exceeds the movement screen and is too thin to select before wet connection testing. |
| **8 mm** | **8.5 MPa / 0.97 mm** | **7.9 MPa / 0.06 mm** | **Selected prototype minimum for both H and bridges.** |
| 10 mm | 5.4 MPa / 0.50 mm | 5.0 MPa / 0.03 mm | Extra margin, not justified by this local screen. |
| 12 mm | 3.8 MPa / 0.29 mm | 3.5 MPa / 0.02 mm | No local need demonstrated. |

The 8 mm choice is not based on the flexure numbers alone. It also preserves a
reasonable thickness at four M8 capture holes, two 30 x 7 mm strap slots,
four M6 basket-retention holes, washer footprints, cut edges and wet-service
creep. It is the thinnest practical selected thickness, conditional on the
same wet coupon and complete-seat tests already required by [R5.1.md](../packs/c/R5.1.md).

The upper H and lower bridges must be cut from the same **8 mm** balanced,
permanent-fresh-water-rated structural-GRP sheet. Do not mix thicknesses to
save offcuts: it changes the sleeve stack and rail-bearing datum.
