# Phase 4 prep – relationship-first schema & solid kernel (IFC 4.3.2 aligned)

> _Last updated: 2025-11-17_

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

1. Relationship-first authoring: components declare intrinsic geometry and explicit `relate` clauses that attach faces/edges to datum bundles or other components. No free-floating origin vectors.
2. Deterministic solving: a constraint solver resolves the graph, emits transparent diagnostics for under/over-constraint, and produces canonical transforms for CadQuery/IFC.
3. IFC-aligned semantics baked into authoring: class names default to IFC entities; predefined types and property sets are explicit, not inferred.
4. Single source of truth: neutral geometry feeds renderers (SVG/PNG), glTF, STEP, and IFC with consistent IDs and material tags.
5. Reproducibility gates: identical input yields identical solids and IFC (stable GUIDs seeded from component IDs + schema version).

---

## Schema surface (Phase 4)

### Components & classes

- `component` requires: `id`, `class`, `profile` (rectangle unless otherwise stated), cross-section `size` and `height` (extrusion depth), `material`, and optional `metadata`.
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

### Constraint clauses (helpers expand to canonical form)

- `flush_bundle` — snap multiple subject faces to a named face bundle, with per-face insets (usable for rebates/clearances).
- `touch_planes` — declare face-to-plane contacts.
- `touch_components` — pairwise face contacts with optional offsets.
- `relate_from` — copy another component’s relationships with targeted overrides (mirrors/variants).
All helpers expand to explicit constraints in the solver’s debug output.

### Repeats & inline assemblies

- Linear repeats use `axis` and a span reference (`span.use`) with `pitch` or `count` and optional `inset.start/end`.
- Inline assemblies (`rotate_quadrants`, `linear_bracing`, future `joist_bay`) expand into explicit components at load-time.
- IFC mapping: repeated geometry shall be authored as occurrences of a type using `IfcMappedItem` (or `Ifc*Type` with `RepresentationMap`) when profiles are uniform; use raw occurrence geometry if profiles vary.

---

## IFC mapping rules (authoring <-> IFC)

The table below constrains how common pond-deck parts export to IFC so that receiving tools classify and display them consistently.

| Authoring intent | IFC entity (occurrence) | PredefinedType | Shape reps | Material use | Psets (examples) |
|---|---|---|---|---|---|
| Joist | `IfcBeam` | `JOIST` | `Axis` (line), `Body` (ExtrudedAreaSolid) | `IfcMaterialProfileSetUsage` (rect profile) | `Pset_BeamCommon.LoadBearing`, `Reference` |
| Inner/outer beam | `IfcBeam` | `BEAM` (or `EDGEBEAM` where applicable) | Axis + Body | `IfcMaterialProfileSetUsage` | `Pset_BeamCommon` |
| Blocking/bridging | `IfcMember` | as needed | Axis + Body | `IfcMaterialProfileSetUsage` | `Pset_MemberCommon.LoadBearing` |
| Straps/hangers (if modelled) | `IfcFastener` or `IfcMember` | — | Body only (tessellated if needed) | simple `IfcMaterial` | relevant Psets |
| Decking (planks or surface) | `IfcSlab` | `FLOOR` | Body (extrusion), optional FootPrint | `IfcMaterialLayerSetUsage` (if layered) | `Pset_SlabCommon` |
| Pond void (opening) | `IfcOpeningElement` | `OPENING` | Reference + Body | — | — (linked via `IfcRelVoidsElement`) |

Voids: Any pond cut-out is authored as an `IfcOpeningElement` and related to the host element via `IfcRelVoidsElement`. The opening’s Body is not a second subtraction in RV; it documents the void while the host Body carries the real hole.

Instances: For repeated joists, define a single `IfcBeamType` with a `RepresentationMap` and place occurrences via `IfcMappedItem`, or generate mapped occurrences directly when using IfcOpenShell helpers.

Profiles & layers: Linear members use `IfcMaterialProfileSet(Usage)`. Deck slabs use `IfcMaterialLayerSet(Usage)` with AXIS3 layer direction so layers build upwards (+Z).

---

## Geometry & orientation conventions

- Local placement: each product’s `IfcLocalPlacement.RelativePlacement` is an `IfcAxis2Placement3D`; Axis = +Z is up; RefDirection = +X; Y is derived.
- Axis rep: when present, the joist/beam axis runs along local +X.
- Extrusion: `IfcExtrudedAreaSolid.ExtrudedDirection` points along +Z unless a non-vertical sweep is intended; profile rectangles sit in the XY plane of the swept area position.
- Contexts: establish a 3D “Model” context (precision, TrueNorth as needed) with subcontexts for Axis and Body identifiers.

---

## Validation & tooling

- Constraint solver: resolves face/edge relationships and reports degrees of freedom; blocks builds on under/over-constraint.
- IFC export adapter: validates per-entity rules (Axis+Body presence, material usage alignment, opening relationships).
- Lint CLI (`scripts/lint_specs.py`) checks: missing datums, clashing spans, duplicate IDs, non-IFC `class` values, missing `predefined_type`, misuse of LayerSet/ProfileSet usages, and absence of Axis/Body where required.
- Determinism: stable GUIDs derived from `(component_id, schema_version, option_id)`; exporter emits a build manifest containing unit settings, context IDs, and hash of canonical geometry.
- Tests:
  - Schema: helper expansions are canonical.
  - Solver: DOF counts, mirror/repeat parity, collision checks.
  - Exporter: unit assignment is mm, contexts include Axis/Body, JOIST mapping is correct, openings are rel-voided, material usages match entity type.
  - Round-trip: import -> check entity counts & types -> re-emit -> compare manifests.

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
  size: [ backspan + cantilever + beam_width, joist_width ]
  height: joist_depth
  material: timber
  ifc:
    predefined_type: JOIST
    psets:
      - name: Pset_BeamCommon
        props:
          LoadBearing: true
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
                +x: cantilever
    - touch_planes:
        object: datums.planes.joist_top
        faces: [+z]
  repeat:
    axis: +y
    span:
      use: datums.bundles.deck_faces.y
      inset: { start: walkway_gap, end: walkway_gap }
    pitch: joist_spacing
    include_seed: true
```

Deck slab (single surface or layered)

```yaml
- id: deck_surface
  class: IfcSlab
  profile: rectangle
  size: [ deck_x, deck_y ]
  height: deck_thickness
  material: decking
  ifc:
    predefined_type: FLOOR
    psets:
      - name: Pset_SlabCommon
        props:
          LoadBearing: false
  relate:
    - flush_bundle:
        faces: [+z]
        object: datums.bundles.deck_faces.z
```

Pond opening

```yaml
- id: pond_opening
  class: IfcOpeningElement
  profile: rectangle
  size: [ pond_x, pond_y ]
  height: deck_thickness
  relate:
    - touch_components:
        pairs:
          - subject_face: all
            object_component: deck_surface
            object_face: cut
  metadata:
    host: deck_surface          # exporter turns this into IfcRelVoidsElement
```

Notes

- Keep IFC defaults conservative. When in doubt, prefer IfcBeam/IfcSlab with clear predefined types and simple swept solids.
- Do not over-model fixings; use IfcFastener only when they affect coordination.
- Use types + mapped items for repeated members to keep IFC light and precise.
