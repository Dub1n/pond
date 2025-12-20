# Roadmap (task tracker)

## Active / near-term

- [!] Enable placements to reference rotated/mirrored clones (resolve axis-map refs to op outputs so specs can anchor to clone faces). Definition of done: `dev/reports/attachments/option-c.yaml` builds successfully when C2 start references `inner_beam_south` and `inner_beam_west` clone faces.
- [x] Array rework: replace start/end run_between with axis-map `array` + `repeat`/`through` semantics (array space, per-axis repetition, through checks, overlap guards). Definition of done: schema/solver/lint/tests/docs updated; existing arrays migrated; new `docs/array.md` aligned.
- [!] Add optional `orient` field on `relate` (e.g. `span`), and consider options for explicit vectors or `component_id` frames to define orientation basis.
- [ ] Allow `frame: <component_id>` shorthand (reserve `world`/`local`; keep legacy `component:<id>` accepted during transition).
- [x] Implement frame-aware placement (subject/object frames, frame on `flush`), preserving gaps and size inference when transforming frames.
- [x] Enforce `mode: plane|edge|point`, honour `tolerance`/`on_fail`, and improve DOF reporting; add fail-on-warn paths for collisions/under/over-constraint. (Progress: lint enforces mode shapes; solver trims extra axes per mode, reports DOF, and fail-on-warn can promote under-constraint warnings; checks honour tolerance/on_fail.)
- [x] Finalise selector/clone semantics (template vs placement IDs, id_map remapping, metadata/IFC propagation to clones); lint `base#n` and selectors consistently. (Progress: id_map length lint, selector warnings, clone metadata/IFC/material propagation. Remaining: ✅ enforce `base#n` validity, deterministic template/placement remap, IFC/void propagation to clones, selector/id_map fixtures.)
- [x] Rename `run_between` to `array`, add guardrails (`count >= 2`, warn/error on single spans), and retain 3D `orient: along_run` support.
- [x] IFC discipline: enforce mapping table (entity + predefined type + material usage + mapped items) in lint/solver/export; ensure propagation to clones/voids; add fixtures. (Progress: exporter/lint/validation enforce predefined/material/mapped items/types; RelVoids follow clones; fixtures cover mapped items and openings.)
- [x] Collision and boolean robustness: resolve collision hot-spots (e.g., Option C pad/joist overlaps), stabilise boolean cutouts for rotated arrays; make collision severity configurable alongside env. (Progress: footing ignores stick even with overrides; boolean cutouts track cloned placements/rotations; collision ignore/severity covered by fixtures.)
- [x] Helper parity cleanup: `relate_from`/assemblies removed from code/docs; specs fail fast if they appear.
- [x] Implement mirror operation (plane normal + point) with right-handed frame handling; add lint/tests.
- [x] Expand metadata mapping to align with IFC classes (carry-over from Phase 3 backlog). (Progress: class-aligned property sets emitted from metadata/custom psets; validated alongside mapping table.)

## Phase 4 prep checklist (status captured here; source file archived)

- [x] Loader covers datums/helpers/assemblies and expression dimensions to prep spec expectations.
- [x] Constraint solver meets prep goals (frames, DOF/tolerance-aware checks, deterministic transforms).
- [x] CadQuery exporter builds solids; SVG/PNG derive from OCC projections.
- [x] IFC exporter enforces the prep mapping table (Axis/Body, predefined type/material usage, mapped items, openings).
- [ ] Lint/CI gating and docs/examples refreshed for the final relationship surface.
- [ ] Migration playbook executed; legacy schema archived; release notes updated.

## Backlog – relationship-first hardening

- [ ] IFC completeness gate: fail when IFC-classed components lack predefined type/material or RelVoids/mapped items don’t propagate to clones; emit a completeness summary.
- [x] Array guardrails: enforce `count >= 2`, deprecate legacy `run_between` name in lint/errors; keep 3D `orient: along_run`.
- [ ] Checks/diagnostics depth: formalise warning/error surfacing for collisions and under/over-constraint; add DOF reporting. (Progress: DOF reporting in solver; tolerance/on_fail on checks; warnings emitted for remaining axes.)
- [x] Frame projection diagnostics: add per-relation context (axis remap, frame, offsets), tolerance threshold for warnings, and optional per-frame summaries.
- [x] Component-frame coverage: add fixtures/tests for `frame: <component_id>` placement and size-axis remapping.
- [ ] Clone-aware linting: accept `base#n` refs, validate cloned instance IDs/selectors consistently; fail unknown clone refs.
- [ ] Selector hygiene: lint unknown selectors and id_map/count mismatches; warn when transforms run before array expansion if that risks nondeterminism.
- [ ] Docs/tests gate: new helpers/ops must ship with regression tests covering axis-map + IFC output; gate docs accordingly.
- [ ] Additional diagnostics: add fail-on-warn modes and parity checks for collisions/under/over-constraint; keep DOF reporting flagged until implemented.

## Backlog – legacy teardown (Phase 4.5)

- [ ] Remove legacy anchor/planner/rendering helpers and schema surfaces; move legacy specs/fixtures to `archive/`.
- [ ] Simplify CLI defaults (retire `DIAGRAM_RELATIONSHIPS` flag, dual-path build/lint logic, and legacy-only arguments).
- [ ] Delete unused legacy exporters/renderers/tests; collapse duplicated bundle/material logic into the relationship pipeline.
- [ ] Prune docs/examples referencing legacy helpers; refresh onboarding docs to cover relationship-first only.
- [ ] Run full lint/test/build suite to verify the single-path engine; record final teardown release notes.

## Backlog – richer modelling & integrations (Phase 5)

- [ ] Optional Maker.js or additional geometry helpers for fillets/mitres and non-rectangular details where OCC primitives are awkward.
- [ ] Template library (e.g., `linear_grid`, `cantilevered_grid`, `joist_bay`, `stair_run`) with schema-based validation.
- [ ] Extended IFC capabilities (Design Transfer View where useful; property templates/classifications for joists/beams/slabs).
- [ ] Analysis hooks: export structural views for external tools; optional QTO-focused IFC views.
- [ ] Graph/auto-layout integration (ELK.js/Dagre) for complex attachment diagrams.
- [ ] `--explain` CLI flag dumping intermediate constraint/geometry overlays (SVG/JSON) for debugging.
- [ ] Footprint offset helpers on solids to keep reveals/tolerances declarative.
- [ ] Selector groups and selector integration across operations/booleans; lint support.
- [ ] DOF reporting and richer diagnostics surfaced once implemented.
- [ ] Re-evaluate `relate_from`/assemblies once core axis-map is stable (decide whether to reintroduce with coverage).

## Backlog – authoring UX & tooling (Phase 6)

- [ ] Joist/post pattern macros and higher-level deck presets that expand spans/spacings into full component sets.
- [ ] Dedicated spec/IFC validator CLI (`scripts/validate_spec.py`) with schema, constraint, and IFC mapping reports.
- [ ] Auto-generated schema documentation (e.g., `docs/schema.md`) including IFC fields and helper patterns.
- [ ] Lightweight web UI that edits specs and previews diagrams via the planner/solver API.
- [ ] Authoring assistants that convert prose design briefs into starter YAML using the relationship-first schema.
- [ ] Quality-of-life features: template wizards, copy/paste between options, diff view of geometry between versions.

## Completed milestones

- [x] Axis-map schema landed (`relate`/`flush`/`place`, center tokens, size inference, aggregate selectors, typed operations; rotations remap clones).
- [x] Relationship-first solver with CadQuery solids, run_between spans, selector-aware operations, deterministic GUIDs, OCC collision reporting.
- [x] Planner projects plan/section from solids and emits dimension polylines; renderers share bundle pipeline with legacy path.
- [x] Exporters: glTF/GLB (tessellated solids), IFC 4.3 Reference View scaffolding, STEP/OBJ from CadQuery.
- [x] Lint CLI runs solver + IFC validation, checks axis coverage/size inference/selector validity, emits mesh digests.
- [x] Regression harness covers relationship schema parsing, solver, planner, validation; run_between multi-axis point anchors fixed with coverage.
