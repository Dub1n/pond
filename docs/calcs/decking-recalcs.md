# Decking recut plan

## Purpose

This plan reuses the already-cut and labelled decking wherever possible. It maps each existing label to a new cut length and a destination segment so that every internal butt joint lands on the centre of a straight joist.

Do not cut directly from this document without first measuring the physical boards and joist centres. The calculation deliberately uses the conservative instruction that every labelled existing piece is 20 mm shorter than its label; a board that is shorter than that assumption needs a rerun or a manual reassignment.

## Context

The deck is a 5 000 mm square around a 3 000 mm pond. Decking projects 350 mm over each pond edge, leaving a 2 300 mm square central opening. The surface has **nine**, not eight, concentric rows. Their outside segment lengths are 5 000, 4 700, 4 400, 4 100, 3 800, 3 500, 3 200, 2 900, and 2 600 mm.

Each row consists of four mitred side segments. A segment may be one board or two boards joined end-to-end. The outer ends of a segment retain the 45° corner mitres; any internal meeting is a square butt joint.

The eight straight-joist centres along each 5 000 mm outside beam are:

| Joist | Centre from either reference end (mm) |
| ----: | ------------------------------------: |
|    J1 |                               1 273.5 |
|    J2 |                               1 660.2 |
|    J3 |                               2 080.1 |
|    J4 |                               2 391.5 |
|    J5 |                               2 608.5 |
|    J6 |                               2 919.9 |
|    J7 |                               3 339.8 |
|    J8 |                               3 726.5 |

J4 and J5 replace the former centre joist. Each is 47 mm wide and their inside faces are 170 mm apart, so their centres are 108.5 mm either side of the 2 500 mm deck centreline. The same positions apply on all four sides by rotation.

For an inset row, the distance from its mitred outside corner to a joist is:

`new piece length = joist centre from outside corner − row inset`

where `row inset = (5 000 − segment outside length) ÷ 2`.

## Existing lengths

`decking-lengths.txt` is the source inventory. Each line is one labelled side segment; the values in brackets are its constituent labelled pieces in order. Segment numbers in the Results table are the line order, 1–4, within each outside length.

The inventory originally said `380:[85,225]`. That cannot form a 380 cm segment and breaks the otherwise clear 19 cm progression in that group, so this plan treats it as `380:[85,295]`. **Confirm that the physical board is labelled 295 cm before relying on its assignment.**

Assumptions used by the script:

- every existing labelled piece has `available length = label − 20 mm`;
- there are two uncut 3 900 mm stock boards;
- one existing piece becomes at most one new piece, avoiding kerf accumulation across multiple outputs;
- saw kerf is placed in the discarded side of each cut;
- every new cut is rounded to the nearest 10 mm (1 cm), with the complementary piece adjusted so each complete segment retains its exact outside length;
- this practical rounding moves a butt joint by no more than 3.5 mm from its calculated joist centre, leaving at least about 20 mm of bearing to either joist edge. New cut lengths refer to the long/outside edge where a piece has a 45° mitre.

## Issue

The existing cuts were planned by subtracting one intended piece from an assumed stock-board length. Actual stock lengths varied and the saw kerf was not always included. The pieces are therefore commonly up to about 20 mm shorter than their labels.

More importantly, the existing internal divisions were not derived from the final as-built joist centres. Several butt ends consequently fall between joists or too close to a joist edge rather than meeting over the joist centre. Shortening a whole segment without changing its internal division does not fix that support problem. Every segment must instead be reconstructed from pieces whose cumulative lengths, after allowing for that row's inset, equal one of the joist-centre coordinates above.

## Calculations

`decking_recalcs.py` performs the inventory calculation and validates the result. Run it from the repository root:

```bash
./.venv/bin/python docs/calcs/decking_recalcs.py --check
./.venv/bin/python docs/calcs/decking_recalcs.py
```

The first command validates silently; the second regenerates the Results mapping as Markdown. `--json` emits machine-readable output, and `--actual-shortfall-mm N` reruns the assignment with a different uniform measured shortfall.

The calculation works as follows:

1. Convert all labelled values to millimetres and subtract the assumed 20 mm shortfall from each existing piece.
2. For each of the 36 side segments, evaluate the legal one-joint divisions at the eight joist centres. A row inset is subtracted, then the cut is rounded to the nearest centimetre and its complementary piece is calculated as the segment remainder. The selected supported layout is recorded in the script so it is deterministic and reviewable.
3. Prefer whole inner segments where the inventory can provide them. An exhaustive binary-layout solve established that, under the one-source-to-one-output rule, the minimum feasible layout has 31 butt joints and 67 finished pieces: five segments remain whole and the other 31 have one joint.
4. Assign source pieces to required pieces with a minimum-cost matching. Shorter suitable sources are preferred to reduce waste; retaining an existing useful mitre breaks ties.
5. Validate that all nine rows have four complete segments, every segment adds to its exact outside length, no source is reused, and every rounded butt joint is within 5 mm of one of J1–J8. The actual maximum error in this plan is 3.5 mm.

The chosen segment layouts are:

| Outside length | Segment 1     | Segment 2     | Segment 3     | Segment 4     |
| -------------: | ------------- | ------------- | ------------- | ------------- |
|          5 000 | 3 730 + 1 270 | 2 390 + 2 610 | 1 270 + 3 730 | 2 080 + 2 920 |
|          4 700 | 2 240 + 2 460 | 1 930 + 2 770 | 1 930 + 2 770 | 2 240 + 2 460 |
|          4 400 | 970 + 3 430   | 3 430 + 970   | 3 040 + 1 360 | 3 040 + 1 360 |
|          4 100 | 3 280 + 820   | 1 940 + 2 160 | 3 280 + 820   | 1 940 + 2 160 |
|          3 800 | 2 010 + 1 790 | 3 800         | 2 010 + 1 790 | 3 800         |
|          3 500 | 3 500         | 520 + 2 980   | 2 170 + 1 330 | 520 + 2 980   |
|          3 200 | 1 490 + 1 710 | 3 200         | 370 + 2 830   | 1 180 + 2 020 |
|          2 900 | 610 + 2 290   | 1 030 + 1 870 | 610 + 2 290   | 2 900         |
|          2 600 | 1 190 + 1 410 | 880 + 1 720   | 1 720 + 880   | 1 720 + 880   |

Values in this layout table are millimetres and are ordered around each new segment from one mitred end to the other.

## Results

Find a board by its existing outside-length, segment, piece, and written label; trim it to the new cut length and allocate it to the named new segment/piece. “Available” already includes the assumed 20 mm shortfall.

| Existing labelled board                  | Assumed available (mm) | New segment / piece       | New cut length (mm) | Trim/offcut (mm) |
| ---------------------------------------- | ---------------------: | ------------------------- | ------------------: | ---------------: |
| 500 cm segment 1, piece 1 (label 399 cm) |                   3970 | 500 cm segment 3, piece 2 |                3730 |              240 |
| 500 cm segment 1, piece 2 (label 101 cm) |                    990 | 440 cm segment 2, piece 2 |                 970 |               20 |
| 500 cm segment 2, piece 1 (label 298 cm) |                   2960 | 290 cm segment 4, piece 1 |                2900 |               60 |
| 500 cm segment 2, piece 2 (label 202 cm) |                   2000 | 380 cm segment 1, piece 2 |                1790 |              210 |
| 500 cm segment 3, piece 1 (label 197 cm) |                   1950 | 410 cm segment 4, piece 1 |                1940 |               10 |
| 500 cm segment 3, piece 2 (label 303 cm) |                   3010 | 350 cm segment 2, piece 2 |                2980 |               30 |
| 500 cm segment 4, piece 2 (label 399 cm) |                   3970 | 380 cm segment 4, piece 1 |                3800 |              170 |
| 500 cm segment 4, piece 3 (label 76 cm)  |                    740 | 350 cm segment 2, piece 1 |                 520 |              220 |
| 470 cm segment 1, piece 1 (label 96 cm)  |                    940 | 260 cm segment 3, piece 2 |                 880 |               60 |
| 470 cm segment 1, piece 2 (label 374 cm) |                   3720 | 440 cm segment 1, piece 2 |                3430 |              290 |
| 470 cm segment 2, piece 1 (label 323 cm) |                   3210 | 320 cm segment 2, piece 1 |                3200 |               10 |
| 470 cm segment 2, piece 2 (label 147 cm) |                   1450 | 350 cm segment 3, piece 2 |                1330 |              120 |
| 470 cm segment 3, piece 1 (label 252 cm) |                   2500 | 470 cm segment 1, piece 2 |                2460 |               40 |
| 470 cm segment 3, piece 2 (label 218 cm) |                   2160 | 410 cm segment 4, piece 2 |                2160 |                0 |
| 470 cm segment 4, piece 1 (label 181 cm) |                   1790 | 260 cm segment 3, piece 1 |                1720 |               70 |
| 470 cm segment 4, piece 2 (label 289 cm) |                   2870 | 320 cm segment 3, piece 2 |                2830 |               40 |
| 440 cm segment 1, piece 1 (label 110 cm) |                   1080 | 290 cm segment 2, piece 1 |                1030 |               50 |
| 440 cm segment 1, piece 2 (label 330 cm) |                   3280 | 410 cm segment 3, piece 1 |                3280 |                0 |
| 440 cm segment 2, piece 1 (label 69 cm)  |                    670 | 350 cm segment 4, piece 1 |                 520 |              150 |
| 440 cm segment 2, piece 2 (label 371 cm) |                   3690 | 440 cm segment 2, piece 1 |                3430 |              260 |
| 440 cm segment 3, piece 1 (label 300 cm) |                   2980 | 350 cm segment 4, piece 2 |                2980 |                0 |
| 440 cm segment 3, piece 2 (label 140 cm) |                   1380 | 440 cm segment 3, piece 2 |                1360 |               20 |
| 440 cm segment 4, piece 1 (label 259 cm) |                   2570 | 290 cm segment 1, piece 2 |                2290 |              280 |
| 440 cm segment 4, piece 2 (label 181 cm) |                   1790 | 260 cm segment 2, piece 2 |                1720 |               70 |
| 410 cm segment 1, piece 1 (label 218 cm) |                   2160 | 410 cm segment 2, piece 2 |                2160 |                0 |
| 410 cm segment 1, piece 2 (label 192 cm) |                   1900 | 290 cm segment 2, piece 2 |                1870 |               30 |
| 410 cm segment 2, piece 1 (label 207 cm) |                   2050 | 320 cm segment 4, piece 2 |                2020 |               30 |
| 410 cm segment 2, piece 2 (label 203 cm) |                   2010 | 380 cm segment 3, piece 1 |                2010 |                0 |
| 410 cm segment 3, piece 1 (label 196 cm) |                   1940 | 470 cm segment 3, piece 1 |                1930 |               10 |
| 410 cm segment 3, piece 2 (label 214 cm) |                   2120 | 500 cm segment 4, piece 1 |                2080 |               40 |
| 410 cm segment 4, piece 1 (label 185 cm) |                   1830 | 380 cm segment 3, piece 2 |                1790 |               40 |
| 410 cm segment 4, piece 2 (label 225 cm) |                   2230 | 350 cm segment 3, piece 1 |                2170 |               60 |
| 380 cm segment 1, piece 2 (label 352 cm) |                   3500 | 350 cm segment 1, piece 1 |                3500 |                0 |
| 380 cm segment 2, piece 1 (label 47 cm)  |                    450 | 320 cm segment 3, piece 1 |                 370 |               80 |
| 380 cm segment 2, piece 2 (label 333 cm) |                   3310 | 410 cm segment 1, piece 1 |                3280 |               30 |
| 380 cm segment 3, piece 1 (label 66 cm)  |                    640 | 290 cm segment 3, piece 1 |                 610 |               30 |
| 380 cm segment 3, piece 2 (label 314 cm) |                   3120 | 440 cm segment 4, piece 1 |                3040 |               80 |
| 380 cm segment 4, piece 1 (label 85 cm)  |                    830 | 410 cm segment 3, piece 2 |                 820 |               10 |
| 380 cm segment 4, piece 2 (label 295 cm) |                   2930 | 500 cm segment 4, piece 2 |                2920 |               10 |
| 350 cm segment 1, piece 1 (label 104 cm) |                   1020 | 440 cm segment 1, piece 1 |                 970 |               50 |
| 350 cm segment 1, piece 2 (label 246 cm) |                   2440 | 500 cm segment 2, piece 1 |                2390 |               50 |
| 350 cm segment 2, piece 1 (label 153 cm) |                   1510 | 320 cm segment 1, piece 1 |                1490 |               20 |
| 350 cm segment 2, piece 2 (label 197 cm) |                   1950 | 410 cm segment 2, piece 1 |                1940 |               10 |
| 350 cm segment 3, piece 1 (label 202 cm) |                   2000 | 320 cm segment 1, piece 2 |                1710 |              290 |
| 350 cm segment 3, piece 2 (label 148 cm) |                   1460 | 500 cm segment 1, piece 2 |                1270 |              190 |
| 350 cm segment 4, piece 1 (label 251 cm) |                   2490 | 470 cm segment 4, piece 2 |                2460 |               30 |
| 350 cm segment 4, piece 2 (label 99 cm)  |                    970 | 260 cm segment 2, piece 1 |                 880 |               90 |
| 320 cm segment 1, piece 1 (label 174 cm) |                   1720 | 260 cm segment 4, piece 1 |                1720 |                0 |
| 320 cm segment 1, piece 2 (label 146 cm) |                   1440 | 260 cm segment 1, piece 2 |                1410 |               30 |
| 320 cm segment 2, piece 1 (label 253 cm) |                   2510 | 290 cm segment 3, piece 2 |                2290 |              220 |
| 320 cm segment 2, piece 2 (label 67 cm)  |                    650 | 290 cm segment 1, piece 1 |                 610 |               40 |
| 320 cm segment 3, piece 1 (label 320 cm) |                   3180 | 440 cm segment 3, piece 1 |                3040 |              140 |
| 320 cm segment 4, piece 2 (label 305 cm) |                   3030 | 470 cm segment 2, piece 2 |                2770 |              260 |
| 290 cm segment 1, piece 1 (label 94 cm)  |                    920 | 260 cm segment 4, piece 2 |                 880 |               40 |
| 290 cm segment 1, piece 2 (label 196 cm) |                   1940 | 470 cm segment 2, piece 1 |                1930 |               10 |
| 290 cm segment 2, piece 1 (label 203 cm) |                   2010 | 380 cm segment 1, piece 1 |                2010 |                0 |
| 290 cm segment 2, piece 2 (label 87 cm)  |                    850 | 410 cm segment 1, piece 2 |                 820 |               30 |
| 290 cm segment 3, piece 1 (label 290 cm) |                   2880 | 470 cm segment 3, piece 2 |                2770 |              110 |
| 290 cm segment 4, piece 2 (label 268 cm) |                   2660 | 500 cm segment 2, piece 2 |                2610 |               50 |
| 260 cm segment 1, piece 1 (label 131 cm) |                   1290 | 500 cm segment 3, piece 1 |                1270 |               20 |
| 260 cm segment 1, piece 2 (label 129 cm) |                   1270 | 260 cm segment 1, piece 1 |                1190 |               80 |
| 260 cm segment 2, piece 1 (label 260 cm) |                   2580 | 470 cm segment 4, piece 1 |                2240 |              340 |
| 260 cm segment 3, piece 1 (label 260 cm) |                   2580 | 470 cm segment 1, piece 1 |                2240 |              340 |
| 260 cm segment 4, piece 1 (label 139 cm) |                   1370 | 440 cm segment 4, piece 2 |                1360 |               10 |
| 260 cm segment 4, piece 2 (label 121 cm) |                   1190 | 320 cm segment 4, piece 1 |                1180 |               10 |
| stock board 1 (390 cm)                   |                   3900 | 500 cm segment 1, piece 1 |                3730 |              170 |
| stock board 2 (390 cm)                   |                   3900 | 380 cm segment 2, piece 1 |                3800 |              100 |

The plan uses 67 of 71 available source pieces/boards. Total trim and offcut from used sources is 5 600 mm. The four deliberately unused small pieces are:

- 500 cm segment 4, piece 1, label 25 cm;
- 380 cm segment 1, piece 1, label 28 cm;
- 320 cm segment 4, piece 1, label 15 cm;
- 290 cm segment 4, piece 1, label 22 cm.

Before cutting, verify every board assigned with zero trim allowance (for example 172 → 172 cm, 216 → 216 cm, and 201 → 201 cm). These pieces are usable without shortening only if their measured long/outside edge reaches the stated practical cut length. If one is short, rerun with a larger uniform shortfall or swap it manually with a longer assigned source and rerun `--check` after updating the inventory.
