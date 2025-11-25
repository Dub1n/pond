## Relationship-first schema (prep)

This document captures the prep surface for the relationship-first schema described in `dev/phase4-prep-report.md`. The loader and lint are live so contributors can draft specs ahead of the solver/CadQuery integration.

### What is available now

- Specs marked with `schema: pond-relationship*` parse via `diagramming.relationships.schema`.
- Axis tokens use signed axes (`+x`, `-y`, `+z`); multi-axis positions are canonicalised (`+x-y+z`).
- Datums support points, planes, and face bundles; helpers consume references such as `datums.planes.deck_top` and `datums.bundles.frame.x`.
- Relationship helpers parsed today: `align` / `contact`, `flush_bundle`, `run_between`, `relate_from`, `touch_planes`, `touch_components`, plus `repeat` spans and `voids`.
- IFC metadata is accepted (`ifc.predefined_type`, `ifc.psets`) and uppercased for consistency.

### Linting

- Run `python3 scripts/lint_specs.py` (or `.venv/bin/python scripts/lint_specs.py`) to lint both legacy and relationship-first specs. Use `--relationship-only` when iterating on the new schema.
- The linter checks reference integrity (component IDs, datums, bundles, planes) and warns when IFC classes are missing an `ifc` block.
- The CLI short-circuits if a Phase 4 spec is passed to `scripts/build_diagrams.py`; renderers remain legacy-only until the solver lands.

### Feature flag

- The relationship-first path is gated by `DIAGRAM_RELATIONSHIPS=1` for future solver/CadQuery hookups. For now it only influences diagnostics; rendering still refuses relationship-first specs.

### Reference example

- `docs/examples/option-c-relationship.yaml` mirrors Option C using the relationship-first schema: datums/bundles drive placement, helpers define face-to-face intent, and repeats use axis spans instead of raw spacing.

### Limitations (prep state)

- Constraint solving and solids are stubbed; `diagramming.relationships.solver.ConstraintSolver` returns placeholders with warnings.
- Renderers still rely on the legacy planner; plan/section projections from CadQuery will arrive with the solver work.
