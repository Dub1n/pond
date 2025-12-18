# Phase 4 implementation vs prep schema (refresh)

Scope: current relationship-first implementation in `diagramming/relationships` vs the target in `dev/phase4-prep-report.md`. The Option C relationship example is still in the tree but now archived; the notes below reflect the live code rather than that legacy spec.

## Findings against the prep schema

- Frames remain parsed only. `schema.py` accepts `frame` (including `component:<id>`) but the solver ignores it everywhere, so all relates run in world space. Checks also drop `tolerance`/`on_fail` semantics and only do strict equality comparisons.
- `run_between orient: along_run` now uses the full 3D span vector (via `_orientation_from_direction`) and applies base twist, so +X aligns to the span even when Z differs. Frame-aware orientation is still absent.
- Constraint signals are shallow. Under-constrained axes raise errors, but degrees-of-freedom counts stay zeroed and checks don’t report gaps/overlaps—only axis equality. Collision reporting works with error/warn/ignore modes.
- Helper/assembly coverage is narrower than the prep surface. Only axis-map `relate`/`flush`/`place` and `run_between` are supported; `relate_from` and any `assembly.*` entries are parsed but never expanded, and the older `touch_*` macros no longer exist.
- IFC linting is minimal. A few entity names (`IfcBeam`, `IfcMember`, `IfcSlab`, `IfcOpeningElement`) require `ifc.predefined_type`/material, but entity/type pairing, material usages, and mapped-item rules from the prep mapping table are not enforced.

## Option C example (archived)

- The example still uses the legacy helper vocabulary (`flush_bundle`, `contact`, `touch_*`, mixed `size` + `height`, non-IFC class names). It no longer parses against the current axis-map loader and its assemblies would not execute. It has been archived to avoid confusion.

## Takeaways

- Add frame-aware placement and respect `tolerance`/`on_fail` in checks to match the prep surface.
- Implement the documented helpers (`relate_from`, assemblies such as `assembly.linear_bracing`) and fail fast when unsupported helpers are declared.
- Tighten IFC linting to match the mapping table (entity + predefined type + material usage, mapped items) so author intent stays IFC-aligned.
