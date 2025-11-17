# Spec Authoring Guide

This guide summarises the practical steps for editing deck-framing specs so that semantic design briefs translate into consistent plan and section geometry. Keep it open alongside the design notes and `diagrams/specs/*.yaml` while you work.

## Before you edit

- Activate the repository virtualenv (`source .venv/bin/activate`) and install dependencies with `python3 -m pip install -r requirements.txt`.
- Familiarise yourself with the target option in `docs/design.md`; confirm the walkway width, cantilever length, structural members, and any height metadata that the renderers expect.
- Review existing calculations in `docs/calcs/` for similar options so you can reuse anchoring patterns.

## Coordinate frame

- Units default to millimetres at the spec level.
- The origin for each rectangle is the top-left corner; positive X runs to the right, positive Y runs downward (SVG-style coordinate system).
- To keep alignment predictable, treat the deck outer frame as the canonical reference: Option B/C set `origin: [0, 0]` on a square that surrounds the pond opening.

## Anchors and offsets

- Every anchored component defines two alignment values:
  - `align` describes **which point on the reference component** you are targeting (`center`, `north_west`, `east`, etc.).
  - `anchor_point` describes **which point on the current component** should land on that reference point.
- You can use the `anchor_point` name or its alias `attach` / `attach_side` / `attach_edge` / `attach_face` if that reads better in context; edge aliases are the quickest way to keep faces flush.
- For truly declarative “snap this face to that face” placement, set `placement.flush.edge` (plus optional `attach_edge` when the faces differ). The planner converts those aliases to the exact anchor math automatically, so there is no need to juggle half-width offsets by hand.
- Offsets accept either the traditional `[dx, dy]` pair **or** a directional mapping (`offset: {west: backspan, south: walkway_gap}`) that expands to the correct signed deltas automatically.
- `offset: [dx, dy]` is applied **after** the alignment. Positive `dx` shifts east, positive `dy` shifts south (downward). When you want to move “north” or “west”, the offset values will be negative.
- Tip: when the dimensions are non-intuitive, sketch the target on paper, label the alignment points, then convert to offsets. `docs/calcs/option-c-dimensions.md` shows the working for a 1 m backspan and 0.25 m cantilever.

### Common anchor patterns

| Goal                                  | Anchor example                                                                                                              |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Centre the pond within the deck frame | Align `pond_water` to `deck_backspan` with `align: center`, `anchor_point: center`.                                         |
| Attach a joist to the pond edge       | Anchor joist’s `north_west` corner to the pond’s `north_east` corner, then offset by the backspan length.                   |
| Place a beam at the outer rim         | `placement.flush.edge: west` with `attach_edge: east` snaps the beam’s inside face to the deck rim—no manual half-width maths. |

## Repeats and rotations

- `repeat` now covers the common linear patterns: keep `count` + `spacing` when you already know the delta, switch to `count` + `span` + `direction` to distribute clones evenly across a run, or provide `interval` + `span` + `direction` when spacing and run length are known but the count is not. Use `direction: east|west|north|south|+x|-y` (or a `vector: [dx, dy]` for diagonals); the planner normalises the vector and derives whichever value you omitted. Set `span_mode: exclusive` to keep the array inside the span without touching both ends.
- For symmetric layouts, model one side and use an `operations: rotate` step. Set `include_base: true` if the original component should stay in the scene, then rotate around an anchor (often the pond centre).
- `operations: mirror` reflects matching components across a vertical (`axis: y`) or horizontal (`axis: x`) line. Provide an `about` anchor to pin the mirror axis to a component (defaults to the group centroid) and the planner will generate mirrored clones with the same views, materials, and metadata.

### Repeat quick reference

- Anchor the first instance, then let the planner drive spacing:

  ```yaml
  repeat:
    count: 8
    direction: south
    span: pond_span - joist_width - 2 * outrigger_margin
  ```

  The example above surfaces the clear-span concept (“fill this southward run”) instead of baking in `spacing: [0, 400]`.
- When the interval is fixed but the count can float, drop `count` entirely:

  ```yaml
  repeat:
    interval: 400
    direction: east
    span: deck_span - beam_width
  ```

  The engine divides the span by the interval and creates as many clones as fit.
- Use `span_mode: exclusive` to keep end components off the span boundaries (helpful for handrails that need clearance):

  ```yaml
  repeat:
    count: 4
    direction: north
    span: walkway_width
    span_mode: exclusive
  ```

- Mixed vectors are supported—swap `direction` for `vector: [dx, dy]` when the array is diagonal or stepped.

### Mirror operations

- Mirror pairs shine when the geometry already exists on one side and only needs a reflected copy:

  ```yaml
  operations:
    - type: mirror
      targets: [outriggers_west, frame_posts_west]
      axis: y
      include_base: true       # keep the originals
      about:
        ref: pond_water
        align: center
  ```

  This keeps anchors intact on the source components while the planner produces a mirrored sibling set. Use `include_base: false` when you only need the mirrored clones.

## Dimensions and placement helpers

- Declare shared spans under `dimensions` at the option level (e.g., `backspan: 1000`, `cantilever: 250`) so components can reference them by name instead of repeating raw numbers.
- Components can opt into the `placement` block to describe how they relate procedurally:

  ```yaml
  placement:
    from:
      ref: pond_water
      align: north_east
    attach: north_west
    move:
      - direction: west
        distance: backspan + cantilever
    inset:
      south: walkway_gap
  ```

  The planner turns this into the equivalent anchor/offset tuple automatically.
- To express a flush relationship directly, swap in the shorthand:

  ```yaml
  placement:
    flush:
      ref: deck_backspan
      edge: west
    attach_edge: east    # optional when the faces differ
  ```

  This expands to the same anchor math as above while guaranteeing the faces stay aligned even if dimensions change later.
- You can still fall back to explicit `origin` or `anchor` fields when the placement is simpler; avoid mixing `placement` with either of those on the same component.

### Converting manual anchors to placement helpers

- When you inherit an `anchor` + `offset` block that was doing face alignment by hand, swap it for `placement.flush` so future dimension tweaks remain safe:

  ```yaml
  # Legacy
  anchor:
    ref: inner_frame_west
    align: north_west
    anchor_point: center
    offset:
      west: post_size / 2
      south: post_size / 2

  # Refactored
  placement:
    flush:
      ref: inner_frame_west
      edge: west
    attach_edge: east
    inset:
      north: post_size / 2
  ```

- Treat `inset` as the declarative way to “nudge” along the orthogonal axis—you get the same result without re-deriving half widths when sizes change.
- For components that only rely on anchor points (no clean face to flush), `anchor_point` aliases such as `north_east` / `south_west` often remove the need for offsets entirely.

### Vertical placement

- Components can declare a `vertical` block to keep elevations declarative:

  ```yaml
  vertical:
    flush:
      ref: pond_water
      face: top
    attach_face: top   # defaults to the same face as flush.face
    offset: 0          # optional; positive lifts, negative drops
  ```

  The schema expands this to a numeric `metadata.elevation` so beams, pads, and soil stay tied to their datum even when heights change.
- Supported faces are `top`, `bottom`, and `center` (aliases such as `upper`, `lower`, `mid` are accepted). Components without a `height` may still anchor vertically—useful for 2D planes that act as datums for other members.
- Combine `vertical` with the usual `placement` helpers: horizontal alignment stays in the `placement` block, Z alignment lives under `vertical`, keeping specs readable when both axes need constraints.

### Boolean cutouts

- When one component should reclaim another’s footprint (e.g., soil against pad foundations), add a `boolean.subtract` list to the host rectangle. Each entry can be a plain component ID or a mapping with `target` and `include_generated` flags. The planner unions all matching geometry—including repeat instances and rotated clones—before subtracting it from the host.
- Example:

  ```yaml
  - type: rectangle
    id: soil_fill
    size: [deck_span, deck_span]
    boolean:
      subtract:
        - pads_west            # subtract base + repeat clones
        - target: pads_east
          include_generated: false   # ignore rotated copies if you only need the base instances
  ```

- You can combine `boolean.subtract` with traditional `cutouts`; the rectangular cutouts still apply first, then component subtraction removes the remaining overlap.

## Section views

- When a view declares a `plane`, the planner now slices the extruded scene directly. As long as each plan component has a `height` and either an explicit `metadata.elevation` or a `vertical` block, the section view resolves automatically from the same geometry.
- You no longer need to author duplicate section-only rectangles; reserve manual components for detail overlays or callouts that are absent from the canonical model.
- Pick the plane axis/coordinate so it intersects the members you care about (`axis: y` cuts across the X direction, `axis: x` cuts across Y). The planner flattens the slice to start at `x = 0` for readability.
- If a component should be hidden from the slice (e.g. dashed annotations), omit `height` or keep `views: [plan]` so it doesn’t extrude into the 3D scene.
- Water and soil still rely on absolute elevations to keep the datum legible; verify their `height`/`metadata.elevation` values match the physical depth.

## Heights, materials, metadata

- `height` is the component’s vertical thickness for glTF extrusion.
- `material` keys reference the palette in `diagramming/materials.py` so plan/section fills and 3D colours stay in sync.
- `metadata.elevation` is measured from datum (typically below the deck). Positive values lift the component; negative values drop it below grade.
- Metadata values accept the same dimension math as `size` / `offset` (e.g., `-pad_height`, `beam_height + pad_height`) so you can keep vertical stacks consistent even when you tweak option-level dimensions.

## Workflow checklist

1. Copy the semantic requirements into a fresh calc note if geometry is non-trivial (see `docs/calcs/` for examples).
2. Update the YAML option:
   - Adjust deck frame/cutouts for plan geometry.
   - Place joists, beams, posts with correct anchors/repeats.
   - Mirror or rotate components to fill all sides.
   - Refresh section components to match the same dimensions and heights.
3. Run `python scripts/build_diagrams.py --spec diagrams/specs/deck-framing.yaml --option <Option>` to regenerate outputs and check plan/section PNGs.
4. Execute `python3 -m unittest discover` to confirm planner and renderer tests still pass.
5. Commit the YAML, any new calc notes, and regenerated docs as needed.

## Worked example: outriggers around a pond

- **Dimensions** — declare `walkway_width`, `cantilever`, and any derived spans (`opening_span`, `outrigger_margin`) so repeats and cutouts can reference names instead of literals.
- **Frame member** — author one inner frame component with `placement.flush.edge` against the pond, confirming it sits at the correct elevation.
- **Outriggers** — attach them to that frame via `placement.flush` + `inset`, then use `repeat` with `count` + `span` in the walking direction. No spacing maths required.
- **Rotation / mirror** — rotate or mirror the single authored edge around the pond centre; keep `include_base: true` when the original edge should remain.
- **Section view** — reuse the same dimension names (`backspan`, `cantilever`) inside section rectangles so the vertical slice stays aligned with the plan automatically.

## Troubleshooting

- If a component fails to appear, confirm you added it to the correct `views` list (defaults to all views when omitted).
- When rotations misbehave, check that the `about` anchor resolves to a component with known bounds (often `pond_water`).
- For repeat spacing hiccups, log the bounding box widths in `docs/calcs/`—the context makes future adjustments faster.

Stuck on something? Check `diagramming/planner/geometry.py` to see how alignments are resolved, or add a short note in `docs/calcs/` so the next person benefits from the discovery.
