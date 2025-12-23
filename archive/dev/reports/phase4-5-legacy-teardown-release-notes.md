# Phase 4.5 legacy teardown release notes

Highlights
- Legacy schema/planner code archived under `archive/diagramming/`; legacy specs/fixtures moved under `archive/`.
- CLI build/lint are relationship-only; `DIAGRAM_RELATIONSHIPS` and legacy-only args removed.
- `run_between` and `component:<id>` frame aliases removed; `array` + `frame: <component_id>` only.
- IFC openings now emit only for `IfcOpeningElement` voids; non-opening voids no longer require RelVoids.
- Docs/onboarding refreshed for the relationship-first surface; Option C spec promoted to `diagrams/specs/option-c.yaml`.

Verification
- `./.venv/bin/python scripts/lint_specs.py --collision-mode warn` (passed; 80 collision warnings for option-c).
- `./.venv/bin/python -m unittest discover` (passed).
- `./.venv/bin/python scripts/build_diagrams.py --spec diagrams/specs/option-c.yaml --option C --outdir diagrams/output --force --collision-mode warn` (built plan/section SVG/PNG, GLB, IFC; collision warnings noted).
