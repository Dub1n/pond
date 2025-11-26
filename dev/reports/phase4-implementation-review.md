# Phase 4 implementation vs prep schema

Scope: compared the relationship-first implementation in `diagramming/relationships` against the target described in `dev/phase4-prep-report.md`, and walked through the authored example in `docs/examples/option-c-relationship.yaml`.

## Findings against the prep schema

- Align/contact is parsed and used, but frames are ignored end-to-end. `schema.py` accepts `frame` and `component:<id>` targets, yet `solver.py` resolves every alignment in world space and never transforms by subject/object frames; `flush_bundle.frame` is also dropped. `on_fail` is stored but not acted on, so checks always error rather than warn.
- `run_between` resolves spans and rotation only in the XY plane. `orient: along_run` just sets a Z-rotation from atan2(x, y) and skips Z-bearing vectors and frame-aware orientation, so local +X is not actually aligned to the 3D run vector the prep doc calls for.
- Constraint robustness is partial. `run_between` seeds untouched axes as “soft” but `_finalise_transform` treats them as solved, so unconstrained X/Y/Z from a single-axis span won’t trip the DOF error the prep report expects. Collision checks run, but contact/overlap assertions from the `checks` block are limited to simple gap tolerances.
- Helper coverage lags the target. `relate_from` is parsed but treated as an unsupported helper at solve time, and only `assembly.rotate_quadrants` is expanded—assemblies like `assembly.linear_bracing` in the example never materialise. `touch_planes`/`touch_components` exist as convenience macros even though the prep schema only documents `align`/`contact`/`flush_bundle`/`run_between`.
- IFC discipline is looser than the mapping table in the prep doc. Linting enforces an `ifc` block only when the class already starts with `Ifc`, but it doesn’t check the entity/predefined type pairing or material usage expectations from the table. The solver and exporter fall back to `IfcBuildingElementProxy` when classes are non-standard, so author intent can silently drift from the IFC-aligned surface.

## Option C example observations

- The example barely exercises `align`: it is only used for pad Y placement, while the main members lean on `touch_planes`/`touch_components` and `flush_bundle`. That bypasses the general `align` vocabulary outlined in the prep report, and frames are never specified.
- Several classes aren’t IFC entities (`PondWater`, `DeckSurface`, `Pad`, `IfcJoist`) and none of the IFC classes carry `ifc.predefined_type`, so the schema’s IFC alignment guarantees aren’t demonstrated.
- Components mix two-value `size` with a separate `height` field even though the prep surface standardises on a single `[x, y, z]` vector. Assemblies such as `assembly.linear_bracing` are declared but won’t expand under the current solver, so authored intent is partly dropped.

## Takeaways

- Implement frame-aware alignment/flush handling in the solver and honour `on_fail` so the checks block can downgrade to warnings when requested.
- Expand helper coverage to match the prep schema (`relate_from`, `assembly.linear_bracing`, full `run_between` orientation), and fail fast on helpers that are declared but unsupported.
- Tighten linting to enforce the IFC mapping table (entity + predefined type + material usage) and detect unconstrained “soft” axes so authors catch drift early.
- Refresh `docs/examples/option-c-relationship.yaml` to use the core `align`/`contact` vocabulary, IFC classes with predefined types, and the unified `size` vector, then rerun the relationship lint/IFC validation with `DIAGRAM_RELATIONSHIPS=1`.
