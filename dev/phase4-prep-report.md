# Phase 4 prep – relationship-first schema & solid kernel (IFC 4.3.2 aligned)

> Last updated: 2025-11-25

## Context & objective

Primary objective: turn concise, semantic descriptions (e.g., Option C / design-C) into deterministic YAML, resolve positions via a relationship-first constraint model, and generate CadQuery solids that export cleanly to IFC 4.3.2 (Reference View), STEP, and glTF.

Phase 4 formalizes the schema surface (datums, bundles, helper clauses) and locks IFC semantics so “same spec => same solids => same IFC” holds across platforms and time.

---

## Standards pin (what we target & why)

- IFC version: IFC 4.3.2.0 (aka IFC4X3_ADD2).
- Model View Definition (MVD): Reference View (RV) for general handover; Alignment-Based RV is out-of-scope unless alignments are introduced later.
- Units: project units are millimetres (IfcSIUnit: LENGTHUNIT + MILLI); plane angles in degrees.
- Contexts & subcontexts: one 3D “Model” context with subrepresentations Axis and Body per product; optional 2D “Plan” (footprint) as needed.
- Placements: every product has an IfcLocalPlacement with an IfcAxis2Placement3D (local Z = up).
- Solids: prefer IfcExtrudedAreaSolid (or Tapered) for prismatic members and slabs; fall back to tessellation only when necessary.

These settings are chosen for maximum interoperability while keeping authoring deterministic for our use case.

---

## Target outcomes

1. Relationship-first authoring: components declare intrinsic geometry and explicit `align`/`contact` clauses that attach faces/edges/points to datum bundles or other components. No free-floating origin vectors.
2. Deterministic solving: a constraint solver resolves the graph, emits transparent diagnostics for under/over-constraint, and produces canonical transforms for CadQuery/IFC.
3. IFC-aligned semantics baked into authoring: class names default to IFC entities; predefined types and property sets are explicit, not inferred.
4. Single source of truth: neutral geometry feeds renderers (SVG/PNG), glTF, STEP, and IFC with consistent IDs and material tags.
5. Reproducibility gates: identical input yields identical solids and IFC (stable GUIDs seeded from component IDs + schema version).

---

## Schema surface (Phase 4)

### Components & classes

- `component` requires: `id`, `class`, `size` (`[x, y, z]` in local axes; omitted axes default to 0), `material`, and optional `metadata`. Profiles are implicit for box solids; non-box profiles are future extensions.
- `class` must be an IFC entity where applicable. Examples:
  - Joists and beams: `IfcBeam` with `ifc.predefined_type: JOIST` (for joists) or `BEAM` (for beams).
  - Deck surface: `IfcSlab` with `ifc.predefined_type: FLOOR`.
  - Blocking/straps/hangers: use `IfcMember` (`ifc.predefined_type` as needed) or `IfcFastener` for discrete connectors when modelled.
- Each component may include an `ifc` block:

  ```yaml
  ifc:
    predefined_type: JOIST        # where supported by the entity’s TypeEnum
    psets:
      - name: Pset_BeamCommon
        props:
          LoadBearing: true
          Reference: "C24 UC4 softwood"
  ```

### Datums & bundles

- `datums.points|planes|faces` define shared frames once; components address them by name.
- Bundle names (`deck_faces.x|y|z`) are linted for reuse so repeats/mirrors remain predictable.
- IFC mapping: datums do not export to IFC; they drive object placement and face alignment which become `IfcLocalPlacement` + Axis/Body alignment in the exported representation.

### Alignment clauses (helpers expand to canonical form)

- `align` — general alignment using `pos` tokens; supports `gap`/`contact`, optional `frame`.
- `contact` — zero-gap alias of `align`.
- `flush_bundle` — macro to align multiple faces to a bundle with per-face insets.
- `relate_from` — copy another component’s alignment set with targeted overrides (mirrors/variants).
- `run_between` — place a component (or an array) between two targets; `start_pos` is required, `end_pos` defaults to `start_pos`, direction from `from→to`, optional `orient: along_run` rotates local +X to the run vector, `count`/`pitch`/`inset` control instance spacing.
All helpers expand to explicit constraints in the solver’s debug output.

### Position tokens, frames, and alignment vocabulary

- Alignment targets use `pos` tokens with 1/2/3 signed axes (`+x`, `+x+z`, `+x+y+z`), canonicalised on load. One axis = face center, two axes = edge center, three axes = corner.
- Default frame is world; optional `frame` per subject/object: `world` (default), `local`, or `component:<id>` (inherit another component’s axes). Direction comes from `from→to`; authors do not need negative lengths.
- `orient` on `run_between` controls whether the component rotates to align its local +X to the run (`along_run`) or preserves axes while translating (`preserve_axes`, default).

### Checks & alignment assertions

- New `checks` block uses the same `align`/`contact` vocabulary. Defaults: `gap: 0.0`, `tolerance: 0.5` (mm), `on_fail: error`.
- Subject/object use `pos` tokens (1/2/3 axes) with optional `frame` (`world` default; `local`; `component:<id>` to inherit another component’s axes). Axis tokens are canonicalised on load.
- Optional `contact` expresses required overlap/length; mutually exclusive with `gap`. Expressions are allowed (e.g., `contact: component_width/2`).

### Repeats & inline assemblies

- Linear repeats use `axis` and a span reference (`span.use`) with `pitch` or `count` and optional `inset.start/end`.
- Inline assemblies (`rotate_quadrants`, `linear_bracing`, future `joist_bay`) expand into explicit components at load-time.
- IFC mapping: repeated geometry shall be authored as occurrences of a type using `IfcMappedItem` (or `Ifc*Type` with `RepresentationMap`) when profiles are uniform; use raw occurrence geometry if profiles vary.

---

## IFC mapping rules (authoring <-> IFC)

The table below constrains how common pond-deck parts export to IFC so that receiving tools classify and display them consistently.

| Authoring intent             | IFC entity (occurrence)      | PredefinedType                          | Shape reps                                | Material use                                | Psets (examples)                           |
| ---------------------------- | ---------------------------- | --------------------------------------- | ----------------------------------------- | ------------------------------------------- | ------------------------------------------ |
| Joist                        | `IfcBeam`                    | `JOIST`                                 | `Axis` (line), `Body` (ExtrudedAreaSolid) | `IfcMaterialProfileSetUsage` (rect profile) | `Pset_BeamCommon.LoadBearing`, `Reference` |
| Inner/outer beam             | `IfcBeam`                    | `BEAM` (or `EDGEBEAM` where applicable) | Axis + Body                               | `IfcMaterialProfileSetUsage`                | `Pset_BeamCommon`                          |
| Blocking/bridging            | `IfcMember`                  | as needed                               | Axis + Body                               | `IfcMaterialProfileSetUsage`                | `Pset_MemberCommon.LoadBearing`            |
| Straps/hangers (if modelled) | `IfcFastener` or `IfcMember` | —                                       | Body only (tessellated if needed)         | simple `IfcMaterial`                        | relevant Psets                             |
| Decking (planks or surface)  | `IfcSlab`                    | `FLOOR`                                 | Body (extrusion), optional FootPrint      | `IfcMaterialLayerSetUsage` (if layered)     | `Pset_SlabCommon`                          |
| Pond void (opening)          | `IfcOpeningElement`          | `OPENING`                               | Reference + Body                          | —                                           | — (linked via `IfcRelVoidsElement`)        |

Voids: Any pond cut-out is authored as an `IfcOpeningElement` and related to the host element via `IfcRelVoidsElement`. The opening’s Body is not a second subtraction in RV; it documents the void while the host Body carries the real hole.

Instances: For repeated joists, define a single `IfcBeamType` with a `RepresentationMap` and place occurrences via `IfcMappedItem`, or generate mapped occurrences directly when using IfcOpenShell helpers.

Profiles & layers: Linear members use `IfcMaterialProfileSet(Usage)`. Deck slabs use `IfcMaterialLayerSet(Usage)` with AXIS3 layer direction so layers build upwards (+Z).

---

## Geometry & orientation conventions

- Axis tokens in authoring are world-space by default; tokens are canonicalised (`+x+z`, not `+z+x`) and may opt into `local` or `component:<id>` frames per subject/object when needed.
- Local placement: each product’s `IfcLocalPlacement.RelativePlacement` is an `IfcAxis2Placement3D`; Axis = +Z is up; RefDirection = +X; Y is derived.
- Axis rep: when present, the joist/beam axis runs along local +X.
- Solids: CadQuery output now covers box, wedge, and swept profiles; additional solid types can be added later. When profiles are needed (e.g., IFC Axis reps), derive them from the canonical primitive unless a non-rectangular profile is specified.
- Extrusion: `IfcExtrudedAreaSolid.ExtrudedDirection` points along +Z unless a non-vertical sweep is intended; profile rectangles sit in the XY plane of the swept area position.
- Contexts: establish a 3D “Model” context (precision, TrueNorth as needed) with subcontexts for Axis and Body identifiers.

---

## Validation & tooling

- Constraint solver: resolves face/edge relationships, reports degrees of freedom, blocks builds on under/over-constraint, and records OCC collision volumes between solids (void pairs excluded).
- IFC export adapter: validates per-entity rules (Axis+Body presence, material usage alignment, opening relationships) and now feeds the lint harness used by CI.
- Lint CLI (`scripts/lint_specs.py`) checks: missing datums, clashing spans, duplicate IDs, non-IFC `class` values, missing `predefined_type`, misuse of LayerSet/ProfileSet usages, absence of Axis/Body where required, and invalid frame/axis tokens; it executes the solver + IFC exporter and surfaces check results plus mesh digests.
- Determinism: stable GUIDs derived from `(component_id, schema_version, option_id)`; exporter emits a build manifest containing unit settings, context IDs, and hash of canonical geometry.
- Dual-render harness: compares OCC-driven SVG hashes against legacy planner output and records mesh checksums (glTF parity guard) for relationship-first fixtures.
- Dimension helpers: plan/section bundles now add arrowed dimension polylines from solved extents so annotations track solids rather than ad-hoc offsets.
- Tests:
  - Schema: helper expansions are canonical.
  - Solver: DOF counts, mirror/repeat parity, collision checks with OCC overlap volumes.
- Exporter: unit assignment is mm, contexts include Axis/Body, JOIST mapping is correct, openings are rel-voided, material usages match entity type.
- Round-trip: import -> check entity counts & types -> re-emit -> compare manifests.
- Checks: axis token linting (order, sign, frame validity); align checks evaluate post-solve with defaults applied and report pass/fail counts in solver diagnostics.

Progress note: the relationship-first solver now resolves box primitives with deterministic GUID seeds, DOF/check diagnostics, and Shapely-derived plan/section projections behind `DIAGRAM_RELATIONSHIPS=1`. Legacy specs lint IFC classes for missing `ifc` blocks, and `run_between`/axis tokens carry stricter validation plus regression tests.

---

## Migration plan

### Before migration

1. Land datum/helper parsing behind a feature flag; keep legacy anchors available.
2. Implement solver core -> CadQuery adapter scaffold; maintain Shapely footprints for plan/section.
3. Draft schema reference and a full Option C example in the new format.
4. Add lint + CI running both legacy and relationship-first validators.

### Execution

1. Convert Option C end-to-end, exercising repeats, voids, and IFC metadata.
2. Port planner tests to relationship-first; deprecate compass/offset placement.
3. Update renderers/exporters to consume solver output; plan/section slices come from CadQuery projections.
4. Migrate remaining specs in batches, using `relate_from` and assemblies to reduce duplication; record lessons in the worksheet.
5. Flip default validation to relationship-first and gate diagram generation on solver success.

### After migration

1. Retire legacy placement code paths and vocabulary; document removal.
2. Finalize CadQuery -> tessellated glTF and STEP/IFC exporters.
3. Monitor authoring ergonomics and capture ADRs for new assemblies or constraint types.
4. Expand example library and mapping coverage.

---

## Implementation checklist (Phase 4)

- [ ] Loader parses datums, helpers, assemblies, expression dimensions.
- [ ] Constraint solver resolves constraints and emits neutral geometry + transforms.
- [ ] CadQuery exporter builds solids; SVG/PNG derive from OCC projections.
- [ ] IFC exporter enforces mapping table, Axis/Body, units, contexts, and openings.
- [ ] Lint CLI & CI wire-up; schema/docs/examples updated.
- [ ] Migration playbook executed; legacy schema archived; release notes updated.

---

## Appendix – sample components

Joist (occurrence authored once, repeated via `repeat`)

```yaml
- id: joist_run_west
  class: IfcBeam
  profile: rectangle
  size: [ backspan + cantilever + beam_width, joist_width, joist_depth ]
  material: timber
  ifc:
    predefined_type: JOIST
    psets:
      - name: Pset_BeamCommon
        props:
          LoadBearing: true
  run_between:
    start_pos: +x+z
    end_pos: -x+z
    from: { component: outer_beam_west, pos: +x+z }
    to:   { component: inner_beam_west, pos: -x+z }
    orient: along_run
    count: joist_count
    pitch: joist_spacing
    inset: { start: walkway_gap, end: walkway_gap }
    include_seed: true
```

Deck slab (single surface or layered)

```yaml
- id: deck_surface
  class: IfcSlab
  profile: rectangle
  size: [ deck_x, deck_y, deck_thickness ]
  material: decking
  ifc:
    predefined_type: FLOOR
    psets:
      - name: Pset_SlabCommon
        props:
          LoadBearing: false
  align:
    subject: { component: deck_surface, pos: +z }
    object:  { component: datums.bundles.deck_faces.z, pos: +z }
```

Pond opening

```yaml
- id: pond_opening
  class: IfcOpeningElement
  profile: rectangle
  size: [ pond_x, pond_y, deck_thickness ]
  align:
    subject: { component: pond_opening, pos: +z }
    object:  { component: deck_surface, pos: +z }
  metadata:
    host: deck_surface          # exporter turns this into IfcRelVoidsElement
```

Notes

- Keep IFC defaults conservative. When in doubt, prefer IfcBeam/IfcSlab with clear predefined types and simple swept solids.
- Do not over-model fixings; use IfcFastener only when they affect coordination.
- Use types + mapped items for repeated members to keep IFC light and precise.
