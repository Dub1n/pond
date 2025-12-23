# Relationship-First Spec Authoring Guide

Use this as a quick-reference when editing relationship-first specs (schema `pond-relationship*`). The axis-map shape keeps placement explicit, IFC-ready, and repeatable.

## Setup

- Activate the venv (`source .venv/bin/activate`) and install deps (`python3 -m pip install -r requirements.txt`).
- Run tests with `python -m unittest discover` and renders with `./.venv/bin/python scripts/build_diagrams.py …`.
- Collision severity: `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore` (default `error`); set `DIAGRAM_RELATIONSHIPS_FAIL_ON_WARN=1` to promote warnings (including validation warnings such as selector hygiene/diagnostic summaries). CLI helpers (`scripts/build_diagrams.py`, `scripts/lint_specs.py`) accept `--collision-mode`, `--collision-ignore`, and `--fail-on-warn` to set these without exporting env vars. Footings are ignored in collision checks by default (even when a custom ignore list is supplied) to avoid noisy pad overlaps.

## Components & References

- Components declare `id`, `class`, optional `material`, and `size: [x, y, z]`. Missing axes can be inferred from relations; conflicting explicit sizes lint.
- `kind: reference` components are geometry-less anchors; omitted axes default to origin.
- Use option-level `dimensions` for reusable spans/offsets; expressions are allowed.

## Axis-Map Relate (core shape)

Frames (`frame: world|local|<component_id>`, with `world`/`local` reserved) are honoured during placement; axis-map and `flush` relations follow the chosen frame while keeping gaps/offsets and size inference intact. Non-axis-aligned frames emit contextual warnings and a per-frame summary showing how local axes were projected.

Each entry maps subject axes to a target:

```yaml
relate:
  +x-y:
    ref: deck_frame         # component/reference/datum/bundle id
    pos: +x-y               # defaults to subject when omitted
    gap: 10                 # scalar or per-axis map (e.g., {+x: 5})
    offset: {cy: -50}       # scalar or per-axis map; center tokens allowed
    mode: plane             # plane|edge|point (default point)
    frame: world            # world|local|<component_id>
```

Tips:

- Each axis-map key defines a single plane/edge/point. Multi-axis keys are not shorthand for
  multiple independent plane constraints; use separate entries when you intend separate planes.
- Subject/pos accept multi-axis tokens, including centers (`cx`, `cy`, `cz`, `~x` etc.).
- Axis-map refs can target rotated/mirrored clones; target faces are resolved using the clone’s
  orientation so world-aligned axes land on the nearest matching local face.
- Coordinate shorthand is allowed in world frame: `cxcy: [0, 0]`, `cz: 150`, or `-z: joist_top`.
- Use `relate.orient` to set a component basis explicitly. `vector` aligns a local axis, `frame` inherits another component’s orientation, and `axis` + `twist` can roll around the chosen axis (defaults to `+x` when omitted).
- Use one X and one Y span when you want inference; extra face pairs can conflict with explicit sizes.
- `flush` sugar expands to axis-map entries (`faces: all` by default, inset scalar or per-face map).

## Placement & Arrays

- `place` creates named placements with inline axis-map blocks (no nested `relate`):

```yaml
place:
  - id: pad_a
    +x: { ref: frame, pos: -x, offset: -pad_size/2 }
    +y: { ref: joist_run#1, pos: +y, gap: pad_size/2 - joist_width/2 }
    +z: { ref: pad_top, pos: +z }
```

- `array` lays out arrays using an axis-map for the array space and a `repeat` block for per-axis repetition:

```yaml
array:
  -y: { ref: frame, pos: +y }
  +y: { ref: frame, pos: -y }
  repeat:
    "0,1,0": { count: 7 }
```

- The axis-map defines the array space; `repeat` defines how many instances along each direction. Without `repeat`, an array is a single instance and behaves like a placement constraint.
- `array` is the canonical placement block; do not combine `array` and `relate` on the same component.
- `array.orient` sets the orientation of each instance (same shape as `relate.orient`).
- Use `through` blocks inside `array` for direction checks; they do not infer size.
- Use `frame: <component_id>` when you need a relation to borrow another component’s orientation instead of the target’s local axes. Component ids cannot be `world` or `local`.
- For corner-to-corner spans (e.g. diagonals), multi-axis keys like `-x+y` in `array` are treated as point anchors when `mode: point` (the default), so the span is based on the actual corner point rather than drifting due to face/size assumptions.
- You can reference run instances directly (e.g. `joist_run_west#1`) anywhere a `ref` is accepted.
- Repeat keys accept direction vectors (`"x,y,z"`) and shorthand axis aliases (`"x"`, `"-x"`, etc.). Unsigned axis keys inherit the array direction on that axis.

## Operations & Selectors

- Typed operations: `rotate`, `mirror`, `translate`, `boolean`.
- Selectors: `id` (all instances), `id.original` (seeds/place entries), `id.clones` (generated copies). Work in operations, booleans, groups, checks.
- Axis-map refs can target clone ids produced by operations, letting placements and checks anchor directly to rotated/mirrored faces.
- Boolean subtract uses selectors against a target component (void references to `IfcOpeningElement` propagate to clones for IFC openings; other voids only drive plan cutouts).
- Selector hygiene: `id.clones` warns if no clones exist, and unknown clone refs/selectors fail lint after solver resolution.

## Size Inference Rules

- If you provide paired axes in `relate`, missing size axes are back-filled. If explicit size disagrees with the inferred span, lint errors. Keep inference to one X and one Y pair when you want it.
- References are lenient (missing axes → 0); regular components must name the axes they constrain or supply explicit size.

## Checks

- Same axis-map shape under `checks:`; use `mode: plane|edge` for coplanar/colinear assertions. Checks now honour `tolerance` + `on_fail: warn|error|ignore`, apply offsets/gaps/frames, and respect `fail_on_warn` escalation.
- Prefer checks for “this must never drift” geometry (like diagonal start/end conditions) and back them with a unit test when a bug is discovered (for example: `RelationshipSolverTests.test_array_multi_axis_point_anchors_center_on_span_midpoint`).
- Checks accept `tolerance` and `on_fail: warn|error|ignore`; failures respect the chosen severity, and `fail_on_warn` still promotes warnings. DOF reporting warns only when an axis can’t infer a position or size (remaining DOF) and emits per-component DOF summaries; validation also emits a diagnostics summary (collisions/under/over-constraint counts). Providing both spans and explicit sizes is allowed as long as they agree.

## IFC & Materials

- Provide `class` and `ifc.predefined_type` where applicable (beams/joists/slabs/openings). Materials map to `diagramming/materials.py`.
- Repeated beams/members/slabs emit mapped items and type definitions; missing predefined types/material usages are gated in validation, openings propagate to cloned hosts, and an IFC completeness summary reports predefined/material/clone-propagation status. Metadata flows into class-aligned property sets (e.g., `Pset_BeamCommon`, `Pset_SlabCommon`) alongside any custom `ifc.psets` you declare.
- Metadata (labels, views, psets) flows into glTF/IFC exports.

## Run & Validate

- Lint: `python scripts/lint_specs.py` (runs solver + IFC validation, size/selector checks, collision reporting, mesh digests). Use `--ci` in CI to enforce fail-on-warn gating.
- Render: `./.venv/bin/python scripts/build_diagrams.py --spec <path> --option <id> --outdir <dir> --force`.
- Baseline freshness: pair render checks with `./.venv/bin/python scripts/baseline_render_check.py --fresh-check` and note results in logs.
- When adding helpers/ops, add axis-map + IFC regression tests and update authoring docs in the same change.
