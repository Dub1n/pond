## Relationship-first schema (prep)

This doc tracks the current relationship-first surface behind `DIAGRAM_RELATIONSHIPS=1` and notes the gaps against the Phase 4 prep target.

### What is available now

- Specs marked `schema: pond-relationship*` parse via `diagramming.relationships.schema`. Axis tokens use signed axes (`+x`, `-y`, `+z`) and multi-axis positions are canonicalised (`+x-y+z`).
- Datums support points, planes, and face bundles. Axis-map `relate` entries (with `flush` sugar) and optional `place` blocks drive placement; `run_between` supplies start/end axis-maps and `orient: along_run` aligns +X to the full 3D span vector, interpolating sizes when start/end faces differ.
- Frames are parsed but ignored by the solver today; all placement runs in world space. Checks reuse the axis-map shape but only assert strict coordinate equality (no tolerance/on_fail yet).
- Components use a single `size: [x, y, z]` (missing axes default to 0); box, wedge, and swept profiles are supported via `profile_params`. `relate_from` and assemblies are accepted in the schema but are not expanded.
- IFC metadata is accepted (`ifc.predefined_type`, `ifc.psets`), and linting enforces predefined-type/material on a small set of IFC entities; broader entity/type/material checks from the prep mapping table are still pending.
- Relationship solves emit CadQuery-backed box/wedge/sweep solids with deterministic GUID seeds, footprints, collision reporting, simple dimension overlays, and glTF/IFC/STEP/OBJ exports. The planner slices solids directly for plan/section bundles.

### Linting

- Run `python3 scripts/lint_specs.py` (or `.venv/bin/python scripts/lint_specs.py`) to lint both legacy and relationship-first specs. Use `--relationship-only` when iterating on the new schema.
- The linter runs the solver + IFC exporter and checks reference integrity, axis token ordering, `run_between.orient`, and minimal IFC coverage; collision overlaps are reported according to `DIAGRAM_RELATIONSHIPS_COLLISIONS`.
- `scripts/build_diagrams.py` defaults `DIAGRAM_RELATIONSHIPS` to enabled; set it to `0` to force legacy-only mode.

### Reference example

- The earlier Option C relationship example used legacy helpers and no longer parses; it has been archived at `archive/docs/examples/option-c-relationship.yaml` for historical reference.

### Limitations (prep state)

- Frames are ignored; checks lack tolerance/on_fail; assemblies/relate_from are not expanded; IFC linting is minimal compared to the prep mapping table.
