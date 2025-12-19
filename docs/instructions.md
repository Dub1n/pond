# Relationship-First Spec Authoring Guide

Use this as a quick-reference when editing relationship-first specs (schema `pond-relationship*`). The axis-map shape keeps placement explicit, IFC-ready, and repeatable.

## Setup

- Activate the venv (`source .venv/bin/activate`) and install deps (`python3 -m pip install -r requirements.txt`).
- Run tests with `python -m unittest discover` and renders with `./.venv/bin/python scripts/build_diagrams.py …` (set `DIAGRAM_RELATIONSHIPS=0` to force legacy-only mode).
- Collision severity: `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore` (default `error`); set `DIAGRAM_RELATIONSHIPS_FAIL_ON_WARN=1` to promote warnings. CLI helpers (`scripts/build_diagrams.py`, `scripts/lint_specs.py`) accept `--collision-mode`, `--collision-ignore`, and `--fail-on-warn` to set these without exporting env vars. Footings are ignored in collision checks by default (even when a custom ignore list is supplied) to avoid noisy pad overlaps.

## Components & References

- Components declare `id`, `class`, optional `material`, and `size: [x, y, z]`. Missing axes can be inferred from relations; conflicting explicit sizes lint.
- `kind: reference` components are geometry-less anchors; omitted axes default to origin.
- Use option-level `dimensions` for reusable spans/offsets; expressions are allowed.

## Axis-Map Relate (core shape)

Frames (`frame: world|local|component:<id>`) are honoured during placement; axis-map and `flush` relations follow the chosen frame while keeping gaps/offsets and size inference intact.

Each entry maps subject axes to a target:

```yaml
relate:
  +x-y:
    ref: deck_frame         # component/reference/datum/bundle id
    pos: +x-y               # defaults to subject when omitted
    gap: 10                 # scalar or per-axis map (e.g., {+x: 5})
    offset: {cy: -50}       # scalar or per-axis map; center tokens allowed
    mode: plane             # plane|edge|point (default point)
    frame: world            # world|local|component:<id>
```

Tips:

- Subject/pos accept multi-axis tokens, including centers (`cx`, `cy`, `cz`, `~x` etc.).
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

- `array` (alias `run_between`) lays out arrays along a span using axis-map `start`/`end` (same shape as `relate`; single axis is fine):

```yaml
array:
  start:
    +y: { ref: frame, pos: +y }
  end:
    -y: { ref: frame, pos: -y }
  count: 7
  include_seed: true
  orient: along_run
```

- Axes only present on one side apply to all clones; missing axes fall back to the component’s `relate`. When start/end provide face pairs, sizes are inferred and interpolated along the span, so no manual insets are needed to land faces on references.
- Arrays expect `count >= 2`; count=1 yields a lint error and solver warning—use a plain placement when you only need a single instance.
- For corner-to-corner spans (e.g. diagonals), multi-axis keys like `-x+y` in `array.start/end` are treated as point anchors when `mode: point` (the default), so the span is based on the actual corner point rather than drifting due to face/size assumptions.
- You can reference run instances directly (e.g. `joist_run_west#1`) anywhere a `ref` is accepted.

## Operations & Selectors

- Typed operations: `rotate`, `mirror`, `translate`, `boolean`.
- Selectors: `id` (all instances), `id.original` (seeds/place entries), `id.clones` (generated copies). Work in operations, booleans, groups, checks.
- Boolean subtract uses selectors against a target component (void references are stored on the host and propagate to clones for IFC openings and plan cutouts).

## Size Inference Rules

- If you provide paired axes in `relate`, missing size axes are back-filled. If explicit size disagrees with the inferred span, lint errors. Keep inference to one X and one Y pair when you want it.
- References are lenient (missing axes → 0); regular components must name the axes they constrain or supply explicit size.

## Checks

- Same axis-map shape under `checks:`; use `mode: plane|edge` for coplanar/colinear assertions. `on_fail`/tolerance are not yet honoured by the solver (checks currently assert strict coordinate equality).
- Prefer checks for “this must never drift” geometry (like diagonal start/end conditions) and back them with a unit test when a bug is discovered (for example: `RelationshipSolverTests.test_array_multi_axis_point_anchors_center_on_span_midpoint`).
- Checks accept `tolerance` and `on_fail: warn|error|ignore`; failures respect the chosen severity, and `fail_on_warn` still promotes warnings. DOF reporting warns only when an axis can’t infer a position or size (remaining DOF); providing both spans and explicit sizes is allowed as long as they agree.

## IFC & Materials

- Provide `class` and `ifc.predefined_type` where applicable (beams/joists/slabs/openings). Materials map to `diagramming/materials.py`.
- Repeated beams/members/slabs emit mapped items and type definitions; missing predefined types/material usages are linted and validated at export time, and openings propagate to cloned hosts. Metadata flows into class-aligned property sets (e.g., `Pset_BeamCommon`, `Pset_SlabCommon`) alongside any custom `ifc.psets` you declare.
- Metadata (labels, views, psets) flows into glTF/IFC exports.

## Run & Validate

- Lint: `python scripts/lint_specs.py --relationship-only` (runs solver + IFC validation, size/selector checks, collision reporting, mesh digests).
- Render: `DIAGRAM_RELATIONSHIPS=1 ./.venv/bin/python scripts/build_diagrams.py --spec <path> --option <id> --outdir <dir> --force`.
- Baseline freshness: pair render checks with `./.venv/bin/python scripts/baseline_render_check.py --fresh-check` and note results in logs.
