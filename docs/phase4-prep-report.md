# Phase 4 prep – relationship-first schema & solid kernel

## Context

- Roadmap Phase 4 introduces a CadQuery-backed solid kernel plus STEP/IFC exporters. To keep authoring productive we are replacing the Phase 3 placement schema with a relationship-first model that still aligns with IFC axes and classes.
- Phase 3 specs rely on compass aliases, per-component offsets, and plan-first reasoning. Migrating to a constraint-led schema reduces edge-matching mistakes, unlocks 3D solids, and keeps the schema intuitive for agents translating design briefs.
- Deliverables for this prep cycle cover schema design, tooling, documentation, and migration scaffolding so the Phase 4 implementation team can focus on building the solver and exporters.

## Target outcomes

- **Relationship-first authoring:** Components define intrinsic geometry plus constraint clauses (`relate`) that explicitly bind faces and corners using IFC-style axis tokens.
- **Datum bundles as shared frames:** Specs can declare datum points, planes, and face bundles once; components reference them for horizontal/vertical alignment without re-stating coordinates.
- **Constraint solver & validation:** Planner resolves the constraint graph, reports under/over-constrained components, and feeds neutral geometry to both 2D renderers and the CadQuery solid pipeline.
- **IFC-aligned semantics with opt-in metadata:** `class` prefers IFC identifiers; optional `ifc.*` blocks enrich solids without burdening authoring when semantics are non-structural.
- **Progressive ergonomics:** Helpers (`touch_planes`, `flush_bundle`, span aliases), inline assemblies (`rotate_quadrants`, `linear_bracing`), and authoring adapters keep specs concise while retaining explicit intent.
- **Tooling & documentation:** Updated authoring guide, lint CLI, and worked examples (including Option C) walk contributors through the new schema with end-to-end workflows.

## Schema surface decisions

### Components & classes

- `component` blocks require `id`, `class`, `profile`, geometry (`size`, `height`, material), and optional `metadata`.
- `class` values default to IFC names (`IfcBeam`, `IfcJoist`); non-IFC elements keep descriptive strings yet still accept `ifc.predefined_type`, `ifc.load_bearing`, etc.
- Components reference datums or other components exclusively through `relate` helper clauses—no raw `origin`/`offset` vectors remain.

### Datums & bundles

- `datums:` defines anchor points, planes, and `faces` bundles. Bundles can cover full orthogonal frames (deck faces) or localised frames (pond faces) and accept per-face insets.
- Lint rules encourage reusing bundle names across specs so rotations and repeats remain predictable.

### Constraint clauses

- Presets expand into the canonical solver input while keeping YAML succinct:
  - `flush_bundle` snaps multiple subject faces to a datum bundle; optional per-face insets handle beam rebates or clearances.
  - `touch_planes` batches face-to-plane contacts (`faces: [+z, -z]`).
  - `touch_components` records component-to-component contacts with optional per-pair offsets.
  - `relate_from` copies an existing component’s constraint set and applies targeted overrides (useful for mirrored members).
- All helpers expand to explicit clauses in diagnostic output so debugging remains transparent.

### Repeats & assemblies

- `repeat` uses `axis` + `span.use` to reference datum bundles, with optional `inset.start/end` and symbolic `pitch`.
- Inline assemblies (`rotate_quadrants`, `linear_bracing`, future `joist_bay`) expand at load-time into canonical components, enabling reuse without hiding complexity.
- Authoring helpers (CLI or notebook) can translate concise prompts into full constraint blocks, but the stored schema always contains explicit helper usage.

## Validation & tooling

- **Constraint solver:** new planner module ingests component geometry, resolves the constraint graph, and flags unmet degrees of freedom. Integrates with CadQuery to derive solids once positions resolve.
- **Lint CLI (`scripts/lint_specs.py`):** checks for missing datums, conflicting spans, duplicate IDs, and prompts authors to promote repeated planes into bundles.
- **Schema reference (`docs/schema.md`):** regenerated to cover helper syntax, datums, relationship clauses, and IFC metadata.
- **Tests:** extend `diagramming/tests/` with solver unit tests, repeat/rotation fixtures, and regression coverage for exported IFC/STEP orientation.
- **Authoring guide:** updates to `docs/instructions.md`, worksheet templates, and new `docs/examples/option-c-phase4.yaml`.

## Migration plan

### Before migration

1. Implement datum + helper parsing in the loader with feature flags, keeping legacy specs functional during prototyping.
2. Build constraint solver core plus CadQuery integration scaffold (neutral geometry extrusion pipeline).
3. Publish schema reference draft and Option C example so authors can review the new format early.
4. Add lint CLI and CI job that runs validation in both legacy and relationship-first modes.

### Migration execution

1. Convert one production spec (Option C) to the new schema end-to-end, exercising repeat helpers and IFC metadata.
2. Port planner tests to rely on relationship clauses; mark legacy anchor logic as deprecated.
3. Update renderers/exporters to consume solver output; ensure SVG/PNG/glTF parity remains.
4. Migrate remaining specs in batches, using `relate_from` and assembly helpers to reduce duplication; capture findings in the worksheet playbook.
5. Switch default CLI validation to relationship-first mode and gate diagram generation on successful constraint solving.

### After migration

1. Retire compass vocabulary and legacy placement code paths; document removal in release notes.
2. Finalise CadQuery solids → STEP/IFC exporters with axis-aligned semantics coming straight from the schema.
3. Monitor authoring feedback, iterate on helper ergonomics, and track follow-up ADRs for additional assemblies or constraint types.
4. Expand the example library (additional deck options, attachment details) to reinforce new patterns.

## Implementation checklist

- [ ] Schema loader parses datums, helpers, assemblies, and expression-based dimensions.
- [ ] Constraint solver resolves faces/planes, surfaces actionable diagnostics, and emits neutral geometry + extrusion metadata.
- [ ] Planner integrates solver output with existing renderers and new CadQuery exporter.
- [ ] Lint CLI + CI wiring enforce schema hygiene pre-generation.
- [ ] Docs updated: instructions, worksheet template, schema reference, example specs.
- [ ] Migration playbook executed, legacy schema archived, and release notes published.

## Appendix – sample component

```yaml
- id: joist_run_west
  class: IfcJoist
  profile: rectangle
  size:
    - dimensions.structure.backspan + dimensions.structure.cantilever + dimensions.structure.beam_width
    - dimensions.structure.joist_width
  height: dimensions.structure.joist_depth
  material: timber
  relate:
    - touch_components:
        pairs:
          - subject_face: -x
            object_component: outer_beam_west
            object_face: +x
          - subject_face: +x
            object_component: inner_beam_west
            object_face: +x
            offsets:
              subject:
                +x: dimensions.structure.cantilever
    - touch_planes:
        object: datums.planes.joist_top
        faces: [+z]
  repeat:
    axis: +y
    span:
      use: datums.bundles.deck_faces.y
      inset:
        start: dimensions.structure.walkway_gap
        end: dimensions.structure.walkway_gap
    pitch: dimensions.structure.joist_spacing
    include_seed: true
```

This snippet shows how helpers keep relationships explicit while delegating boilerplate to reusable datum bundles, face batches, and symbolic dimensions.
