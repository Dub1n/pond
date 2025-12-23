# Design C placements

Positions along the outer/inner beams for option C from `diagrams/specs/option-c.yaml`.
Offsets are measured from the deck-frame +Y (north) face along the beam toward -Y.
Values are in mm; apply the same offsets on every side (rotated).

## Outer beam (O)

T (corner_tie_vertical_nw) faces are 0.0 and 500.0 along O.
T (corner_tie_horizontal_nw) faces are 476.5 and 523.5 along O.
J (joist_run_west_outer) #1 faces are 1250.0 and 1297.0 along O.
J (joist_run_west_outer) #2 faces are 3703.0 and 3750.0 along O.
J (joist_run_west_inner) #1 faces are 1636.7 and 1683.7 along O.
J (joist_run_west_inner) #2 faces are 2056.6 and 2103.6 along O.
J (joist_run_west_inner) #3 faces are 2476.5 and 2523.5 along O.
J (joist_run_west_inner) #4 faces are 2896.4 and 2943.4 along O.
J (joist_run_west_inner) #5 faces are 3316.3 and 3363.3 along O.
P (pad_outer_corner_nw) edges are -276.5 and 323.5 along O (negative means outside the deck edge).
P (pad_run2_west) edges are 1360.2 and 1960.2 along O.
P (pad_run6_west) edges are 3039.8 and 3639.8 along O.

## Inner beam (I)

P (pad_corner_nw) edges are 447.0 and 1047.0 along I.
P (pad_edge_center_west) edges are 2200.0 and 2800.0 along I.
Joist offsets along I match the O list above (same Y placements).
