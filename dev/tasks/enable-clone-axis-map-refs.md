## Enable Axis-Map References to Rotated/Mirrored Clones

Relationship specs need to anchor axis-map relations to the rotated/mirrored clones produced by
`operations` (rotate/mirror/translate). Today, axis-map references resolve only to the base component
ids, which blocks placement that depends on clone faces.

### Use Case (Option C diagonals)

The corner diagonals (C1 and C2) should be defined directly against the rotated inner/outer beams,
using multi-reference axis-maps to establish the diagonal direction. This removes the current
"constructed point" workaround and makes the intent explicit.

**Desired component blocks (exact YAML):**

```yaml
- id: corner_diagonal_deck_to_inner_nw
  class: IfcBeam
  size: [corner_diagonal_length_outer, joist_width, joist_depth]
  material: joist
  label: "47x75mm Joist from deck corner to inner beam corner | 1414mm"
  label_id: "C1"
  relate:
    -xcy:
      - { ref: outer_beam_west, pos: +x }
      - { ref: outer_beam_north, pos: +y }
    +xcy:
      - { ref: inner_beam_west, pos: -x }
      - { ref: inner_beam_north, pos: -y }
    +z: { ref: joist_top, pos: +z }
  ifc:
    predefined_type: JOIST

- id: corner_diagonal_inner_to_opening_nw
  class: IfcBeam
  size: [corner_diagonal_length_inner, joist_width, joist_depth]
  material: joist
  label: "47x75mm Joist from inner beam corner to pond opening corner | 481mm"
  label_id: "C2"
  relate:
    -xcy:
      - { ref: inner_beam_west, pos: +x }
      - { ref: inner_beam_north, pos: +y }
    +xcy:
      - { ref: opening_frame, pos: -x }
      - { ref: opening_frame, pos: -y }
    +z: { ref: joist_top, pos: +z }
  ifc:
    predefined_type: JOIST
```

These blocks require `outer_beam_north`, `inner_beam_north`, etc. to resolve to the rotated clones
created by the `operations` block. Without that, the solver can only access the seed component and
cannot anchor to the correct face orientation.

### Acceptance Criteria

- Axis-map `ref` can target rotated/mirrored clones (e.g., `outer_beam_north`) and resolve faces.
- The above C1/C2 blocks in `dev/option-c.yaml` solve without surrogate reference components.
- No regression for non-clone references; selector behavior remains unchanged.

### Suggested Tests

- Add a fixture that rotates a beam and uses a placement to reference the rotated clone’s faces.
- Update Option C build to use the exact blocks above once clone refs resolve.
