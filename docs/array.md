# Arrays (relationship-first)

This document defines the array semantics for relationship-first specs (schema `pond-relationship*`).

Arrays are a placement primitive that map a component into an array space. The component `size` always
refers to the instance size. The array axis-map defines the array space (the span or bounds that
instances are placed within), and the optional `repeat` block defines repetition within that space.

This design replaces legacy `run_between` behavior and clarifies the separation between:

- Component placement and size (`size`, `relate`)
- Array space and repetition (`array`)

Legacy `start`/`end` blocks are no longer supported; use axis-map entries directly in `array`.

Arrays can be used for a single instance (no repetition) or for multi-axis repetition.

---

## Quick reference

Minimal single-instance array:

```yaml
array:
  -x: { ref: beam_a, pos: +x }
  +x: { ref: beam_b, pos: -x }
```

1D repeat along X (10 instances, 400mm pitch):

```yaml
array:
  -x: { ref: beam_a, pos: +x }
  +x: { ref: beam_b, pos: -x }
  repeat:
    x: { count: 10, pitch: 400 }
```

2D grid along X/Y with a through check:

```yaml
array:
  -x: { ref: frame, pos: -x }
  +x: { ref: frame, pos: +x }
  -y: { ref: frame, pos: -y }
  +y: { ref: frame, pos: +y }
  through:
    - cxcy: { ref: origin, pos: cxcy, mode: point }
  repeat:
    x: { count: 6 }
    y: { count: 4 }
```

---

## Array axis-map (array space)

The `array` block is an axis-map: it uses the same shape as `relate` or `place` entries.
These relations define the array space (the bounding faces / anchors for the array).

- Paired faces (e.g., `-x` and `+x`) define an array span on that axis.
- A single face (e.g., `-x`) defines the array origin on that axis and implies direction; the array extends away from that face.
- Center tokens (`cx`, `cy`, `cz`) can be used in the axis-map the same way as `relate`.
- The `frame` field is accepted (world/local/component frame, with the same rules as `relate`).

Direction rules for single-axis anchors:

- `-x` anchor means the array extends in the positive X direction.
- `+x` anchor means the array extends in the negative X direction.
- The same rule applies to Y and Z.

When both faces are provided, the direction for that axis is taken from `start` to `end`:

- `-x` to `+x` is positive X.
- `+x` to `-x` is negative X.

---

## Repeat block

The `repeat` block defines repetition along one or more axes. If `repeat` is omitted, the
array produces a single instance and the array axis-map behaves like a placement constraint.

Structure:

```yaml
repeat:
  x: { count: 10, pitch: 400 }
  y: { count: 4 }
  z: { count: 2, pitch: 300 }
```

Rules:

- `count` is the number of instances along that axis.
- `pitch` is the center-to-center spacing along that axis.
- If both `count` and `pitch` are provided, the array uses both and warns if the total
  span implied by count/pitch does not match the array span.
- If only `count` is provided, instances are evenly distributed across the axis span,
  inclusive of both ends.
- If only `pitch` is provided, instances repeat as many times as fit; leftover space
  triggers a warning.

Overlap rules:

- Error if `pitch < size[axis]` (instances overlap on that axis).
- Error if `count * size[axis]` exceeds the available array span on that axis.

---

## Through blocks

`through` blocks are optional axis-maps used only as checks:

```yaml
through:
  - +x+y: { ref: datum, pos: +x+y, mode: point }
  - +x: { ref: datum, pos: +x, mode: plane }
```

Behavior:

- `through` does not infer sizes.
- `through` participates in directionality when an axis lacks a paired face, even if the axis has no repeat.
- Each `through` entry is checked independently; if the array direction line does not
  intersect the defined plane/edge/point, the solver emits an error.

Direction line definition:

- When axes repeat, the direction is derived from the array axis-map spans on those axes.
- If an axis has only one face anchor, through constraints can supply the missing direction
  for that axis.

---

## Size inference and over-constraints

Size inference is only applied to axes that are NOT in the `repeat` block. The array axis-map
is treated as the authoritative span for those axes.

- If paired faces define a span and `size[axis]` is provided, the size must match.
- If `size[axis]` is null and a span is defined, the size is inferred from the span.
- If only one face is present and `size[axis]` is provided, the span is taken from size.

If an axis is in `repeat`, it is excluded from size-vs-span checks.

---

## Single-instance arrays

Arrays without a `repeat` block produce a single instance. In this case:

- The array axis-map behaves like a placement constraint.
- Paired faces can infer size (as `relate` does).
- A single face + explicit size determines the missing face.

This lets `array` replace `relate` for single-instance placement while still keeping the
array semantics consistent.

---

## Edge cases and diagnostics

- Missing anchors: if an axis has neither a face anchor nor sufficient repeat/through data to
  establish direction and span, the solver emits an error.
- Overlap: if pitch or count implies overlaps, the solver emits an error.
- Mismatch: if count/pitch implies a span that differs from the array span, the solver emits a warning.
- Over-constraint: conflicting span and size definitions are errors on non-repeating axes.

---

## Examples

Array that spans a frame and repeats along X only:

```yaml
- id: joist
  size: [47, 50, 150]
  array:
    -x: { ref: frame, pos: -x }
    +x: { ref: frame, pos: +x }
    cy: { ref: frame, pos: cy }
    +z: { ref: slab_top, pos: +z }
    repeat:
      x: { count: 7 }
```

Array with a single anchor and explicit pitch:

```yaml
- id: post
  size: [100, 100, 900]
  array:
    -x: { ref: frame, pos: -x }
    -y: { ref: frame, pos: -y }
    repeat:
      x: { pitch: 1200 }
      y: { pitch: 1200 }
```

Array with through checks enforcing directionality:

```yaml
- id: diagonal
  size: [800, 50, 50]
  array:
    -x: { ref: beam_west, pos: +x }
    cy: { ref: beam_south, pos: +y }
    +x: { ref: beam_east, pos: -x }
    cy: { ref: beam_north, pos: -y }
    through:
      - +x+y: { ref: origin, pos: +x+y, mode: point }
```
