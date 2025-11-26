## Relationship-first schema (prep)

This document captures the prep surface for the relationship-first schema described in `dev/phase4-prep-report.md`. The loader, lints, and a box-only solver/renderer bridge are live behind `DIAGRAM_RELATIONSHIPS=1`.

### What is available now

- Specs marked with `schema: pond-relationship*` parse via `diagramming.relationships.schema`.
- Axis tokens use signed axes (`+x`, `-y`, `+z`); multi-axis positions are canonicalised (`+x-y+z`).
- Datums support points, planes, and face bundles; helpers consume references such as `datums.planes.deck_top` and `datums.bundles.frame.x`.
- Relationship helpers parsed today: `align` / `contact`, `flush_bundle`, `run_between`, `relate_from`, `touch_planes`, `touch_components`, plus `repeat` spans and `voids`. Checks reuse the same alignment vocabulary and default to `gap: 0`, `tolerance: 0.5`, `on_fail: error`.
- IFC metadata is accepted (`ifc.predefined_type`, `ifc.psets`) and uppercased for consistency; IFC-classed components lint if they omit an `ifc` block.
- Components use a single 3-axis `size: [x, y, z]` (missing axes default to 0); box, wedge, and swept profiles are supported with optional `profile_params` to drive slopes or custom sections.
- Constraint solver resolves faces/planes/bundles into deterministic transforms and neutral CadQuery primitives (box, wedge, sweep) with stable GUID seeds; checks report pass/fail, diagnostics carry DOF/graph information, and component-to-component alignments provide connection hints for IFC `RelConnects` geometry.
- Relationship planner slices CadQuery solids directly for plan and section geometry before handing off to the existing SVG/PNG/glTF/IFC/STEP/OBJ pipeline when the feature flag is set.
- CLI exports glTF by default and can also emit `model.step` / `model.obj` for relationship-first specs via `--step` and `--obj`.
- IFC export now targets IFC4X3 Reference View with Model/Axis/Body contexts, mm/deg units, swept solids for rectangular members, profile/layer material usages, openings linked via `RelVoids`, mapped items for repeats, and connection geometry derived from face/edge/point contacts.

### Linting

- Run `python3 scripts/lint_specs.py` (or `.venv/bin/python scripts/lint_specs.py`) to lint both legacy and relationship-first specs. Use `--relationship-only` when iterating on the new schema.
- The linter checks reference integrity (component IDs, datums, bundles, planes), axis token ordering, `run_between.orient` values, IFC coverage, and checks block references.
- `scripts/build_diagrams.py` now builds relationship-first specs when `DIAGRAM_RELATIONSHIPS=1` is set; solver failures block rendering.

### Feature flag

- The relationship-first path is gated by `DIAGRAM_RELATIONSHIPS=1`; with the flag set, solver outputs feed the renderer/gltf exporter. Without it, the CLI will refuse relationship-first specs.

### Reference example

- `docs/examples/option-c-relationship.yaml` mirrors Option C using the relationship-first schema: datums/bundles drive placement, helpers define face-to-face intent, and repeats use axis spans instead of raw spacing.

### Limitations (prep state)

- Assemblies are parsed but not yet expanded by the solver.
