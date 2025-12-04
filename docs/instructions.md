# Relationship-First Spec Authoring Guide

Use this as a quick-reference when editing relationship-first specs (schema `pond-relationship*`). The axis-map shape keeps placement explicit, IFC-ready, and repeatable.

## Setup

- Activate the venv (`source .venv/bin/activate`) and install deps (`python3 -m pip install -r requirements.txt`).
- Run tests with `python -m unittest discover` and renders with `DIAGRAM_RELATIONSHIPS=1 ./.venv/bin/python scripts/build_diagrams.py …`.
- Collision severity: `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore` (default `error`).

## Components & References

- Components declare `id`, `class`, optional `material`, and `size: [x, y, z]`. Missing axes can be inferred from relations; conflicting explicit sizes lint.
- `kind: reference` components are geometry-less anchors; omitted axes default to origin.
- Use option-level `dimensions` for reusable spans/offsets; expressions are allowed.

## Axis-Map Relate (core shape)

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

- `run_between` lays out arrays along a span using axis-map `start`/`end` (same shape as `relate`; single axis is fine):

```yaml
run_between:
  start:
    +y: { ref: frame, pos: +y }
  end:
    -y: { ref: frame, pos: -y }
  count: 7
  include_seed: true
  orient: along_run
```

- Axes only present on one side apply to all clones; missing axes fall back to the component’s `relate`. When start/end provide face pairs, sizes are inferred and interpolated along the span, so no manual insets are needed to land faces on references.

## Operations & Selectors

- Typed operations: `rotate`, `mirror`, `translate`, `boolean`.
- Selectors: `id` (all instances), `id.original` (seeds/place entries), `id.clones` (generated copies). Work in operations, booleans, groups, checks.
- Boolean subtract uses selectors against a target component (void references are stored on the host).

## Size Inference Rules

- If you provide paired axes in `relate`, missing size axes are back-filled. If explicit size disagrees with the inferred span, lint errors. Keep inference to one X and one Y pair when you want it.
- References are lenient (missing axes → 0); regular components must name the axes they constrain or supply explicit size.

## Checks

- Same axis-map shape under `checks:`; use `mode: plane|edge` for coplanar/colinear assertions. `on_fail: warn` downgrades failures; missing targets error by default.

## IFC & Materials

- Provide `class` and `ifc.predefined_type` where applicable (beams/joists/slabs/openings). Materials map to `diagramming/materials.py`.
- Metadata (labels, views, psets) flows into glTF/IFC exports.

## Run & Validate

- Lint: `python scripts/lint_specs.py --relationship-only` (runs solver + IFC validation, size/selector checks, collision reporting, mesh digests).
- Render: `DIAGRAM_RELATIONSHIPS=1 ./.venv/bin/python scripts/build_diagrams.py --spec <path> --option <id> --outdir <dir> --force`.
- Baseline freshness: pair render checks with `./.venv/bin/python scripts/baseline_render_check.py --fresh-check` and note results in logs.
