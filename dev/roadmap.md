# Deck diagram pipeline roadmap

This document captures the target state for the “just works” renderer, alongside the phased milestones that will take us there. It complements the high-level overview in `README.md`.

---

## Recent progress

- Plan renderer now computes Shapely coverage for lower-elevation members and clips their fills before painting, ensuring deck surfaces mask joists and beams while dashed hidden outlines remain clear.
- Base CSS applies a more specific hidden-outline rule so material fills can no longer bleed through when debug overlays are active, and the renderer now emits stroke width/colour explicitly for hidden paths.
- `RendererTests.test_hidden_beam_overlay_visible_without_fill` gained a raster assertion on deck pixels, guarding against regressions where buried framing reappears in PNG exports.
- Partial-coverage cases are earmarked for validation in the next iteration; today’s pipeline treats fully buried members as hidden and will need refinement once partially exposed framing specs land.

---

## 1. Target repository layout (draft)

```filesystem
/
├── README.md
├── roadmap.md
├── requirements.txt
├── Makefile
│
├── diagramming/
│   ├── __init__.py
│   ├── schema/                 # Declarative model definitions & validators
│   │   ├── __init__.py
│   │   ├── base.py             # Shared dataclasses / pydantic models
│   │   ├── primitives.py       # Rectangle/polyline primitives
│   │   ├── traits.py           # Optional behaviours (repeat, anchor, align/contact)
│   │   └── decks.py            # Domain-specific enums/rules
│   │
│   ├── planner/                # Turns schema → geometry
│   │   ├── __init__.py
│   │   ├── geometry.py         # Shapely helpers (offsets, unions, slicing)
│   │   ├── layouts.py          # Legend, joist grids, callouts
│   │   ├── planner.py          # DiagramPlanner orchestrator
│   │   └── exporters/          # SVG/PNG/glTF/STEP/IFC adapters
│   │       ├── __init__.py
│   │       ├── svg.py
│   │       ├── png.py
│   │       ├── gltf.py
│   │       ├── step.py
│   │       └── ifc.py
│   │
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── svg_scene.py        # SvgScene abstraction
│   │   ├── styles/             # Shared CSS snippets (plan, section, detail)
│   │   └── annotations.py      # Dimension arrows, tags, legend drawing
│   │
│   └── tests/
│       ├── __init__.py
│       ├── fixtures/           # Sample specs / reference outputs
│       ├── test_schema.py
│       ├── test_geometry.py
│       ├── test_rendering.py
│       └── test_exports_ifc.py # IFC/STEP export regression tests
│
├── diagrams/
│   ├── specs/                  # Author-ed YAML/JSON specs
│   │   ├── deck-framing.yaml
│   │   └── edge-attachments.yaml
│   └── output/                 # Generated artefacts (gitignored)
│       └── …
│
├── docs/
│   ├── design.md
│   └── schema.md               # Auto-generated schema reference
│
├── scripts/
│   ├── build_diagrams.py       # CLI entrypoint
│   └── validate_spec.py        # Standalone schema/IFC validator
│
└── pictures/                   # Reference photos (if needed)
````

This arrangement keeps the author-facing specs in `diagrams/specs/`, while the engine (schema + planner + renderers + exporters) lives under `diagramming/`.

---

## 2. Target architecture (draft)

```diagram
Spec (YAML/JSON)
      │
      ▼
Schema loader (validation: structure + semantics)
      │ produces
      ▼
Typed model (components, views, traits, IFC hints)
      │ into
      ▼
Relationship-first constraint solver
      │
      ▼
Canonical transforms + neutral geometry
      │
      ├─► Shapely footprints (for plan/section)
      └─► CadQuery solids (OCC)
               │
               ├─► SVG/PNG (via OCC projections + SvgScene)
               ├─► glTF (tessellated)
               ├─► STEP/OBJ
               └─► IFC 4.3.2 (Reference View)
```

Key points:

- **Canonical model:** All components are defined once; plans/sections/attachment views are slices or projections of the same canonical scene.
- **Geometry-first:** Shapely manages 2D footprints; CadQuery models 3D solids. All exporters read from the canonical transforms.
- **Pluggable exporters:** New formats just implement `export(bundle, solids, path, options)` without touching solver logic.
- **Behaviour traits:** The planner/solver supports additive behaviours (`repeat`, `cantilever`, `align/contact`, `relate_from`) so domain logic is reusable.

---

## 3. Integration points & dependencies

| Purpose                                   | Dependency                     | Notes                                                                                 |
| ----------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------- |
| 2D geometry ops (union, offset, slice)    | **Shapely 2.x**                | Primary 2D kernel; deterministic and battle-tested.                                   |
| 3D solids & projections                   | **CadQuery (OCC)**             | Primary solid modeller for Phase 4+ (IFC/STEP/glTF driven from here).                 |
| Tessellation & glTF export                | **trimesh + pygltflib**        | Tessellate CadQuery solids and write glTF 2.0 with metadata in `extras`.              |
| 2D → PNG conversion                       | **cairosvg**                   | Optional; unchanged.                                                                  |
| IFC export                                | **IfcOpenShell**               | Build IFC 4.3.2 Reference View: contexts, Axis/Body reps, materials, openings, psets. |
| Optional precise offsets/fillets (future) | Lightweight helpers / Maker.js | Only if we need fillets/mitres beyond what OCC/CadQuery provides.                     |
| Graph-like auto layout (future)           | **ELK.js** / **Dagre**         | For complex attachment diagrams where auto-layout is beneficial.                      |

glTF + IFC compatibility are hard requirements from Phase 4 onwards: every solved model can be exported to glTF and IFC without re-solving geometry.

---

## 4. Reference snippets (Phase 1 sketch)

> Historical reference: how the minimal deterministic pipeline looked before CadQuery/IFC. Still useful context for understanding the evolution of the planner, but not prescriptive for Phase 4+.

**Spec fragment (Phase 1 primitives only):**

```yaml
model:
  components:
    - id: deck
      type: rectangle
      params:
        size: [5000, 5000]
      label: Deck

    - id: joists
      type: rectangle
      params:
        size: [3000, 150]          # single joist footprint
      anchor:
        ref: deck
        align: west
        anchor_point: center
        offset: [0, 500]
      repeat:
        axis: x+
        spacing: 400
        count: 6
      label: Joist

    - id: pond
      type: rectangle
      params:
        size: [3000, 3000]
      anchor:
        ref: deck
        align: center
      label: Pond opening

    - id: deck_with_cutout
      type: rectangle
      params:
        size: [5000, 5000]
        cutouts:
          - size: [3000, 3000]
            anchor:
              ref: self
              align: center
              anchor_point: center
      label: Deck (hollow)

views:
  - id: plan
    type: plan
    include: [deck, joists, pond]
  - id: section_AA
    type: section
    plane:
      point: [2500, 0]
      normal: x+
    include: [deck, joists, pond]
```

this remains a useful low-level example but is effectively “Phase 1 era”.

---

## 5. Requirements

### User-facing (“what the tool must do”)

1. Accept simple declarative descriptions (rectangles/polylines with optional repetition and anchoring).
2. Produce synced plan and section views from the same source model.
3. Auto-generate legends and callout labels from component metadata.
4. Export responsive SVG by default; support optional PNG output.
5. Provide at least one interoperable vector/geometry export (Phase 2: GeoJSON; Phase 3: glTF; Phase 4: STEP/OBJ via CadQuery).
6. Fail fast on invalid specs with actionable error messages (unused anchors, missing `size`, etc.).

### Software-facing

1. Geometry generation must be deterministic (same inputs ⇒ identical outputs).
2. All geometry passes through a canonical “bundle” structure for reuse across exporters.
3. Rendering layer remains stateless — no hidden global state, pure functions where possible.
4. Unit/integ tests cover schema parsing, geometry transforms, and rendered output (snapshot tests).
5. Architecture allows plugging in new exporters without modifying Planner logic.
6. Maintain a clear separation between authoring spec, planning logic, and rendering/exporting modules.

---

## 6. Phased roadmap

### Phase 1 – Minimal deterministic pipeline (completed)

- [x] Schema supports `rectangle` & `polyline` primitives with `anchor`, `repeat`, `label` (see `diagramming/schema`).
- [x] Planner resolves anchors + repetition + simple spacing; outputs plan & section geometry; legend auto-generated (see `diagramming/planner`).
- [x] Exporters: SVG by default with PNG snapshots when `cairosvg` is present (auto-skipped otherwise).
- [x] Light validation for required fields and anchor references keeps authoring ergonomic.
- [x] Test suite covers schema parsing, planner geometry, SVG rendering, and CLI integration via `python3 -m unittest`.
- [x] Renderer enforces white backgrounds and accepts an optional spec-level `scale` for consistent sizing; defaults remain sensible when omitted.
- [x] Per-view overrides (`pad`, `scale`, `background`) and legend typography scaling keep outputs readable across renders.

### Phase 2 – Extended geometry & exports

- [x] Add stored fields (`height`, `metadata`, `traits`) with default values (ignored unless provided).
- [x] Introduce per-view overrides (`views.<name>.pad`, `views.<name>.scale`, `views.<name>.background`) while maintaining backward-compatible defaults.
- [x] Strengthen schema validation: detect orphan anchors, duplicate IDs, invalid repeat spacing, and report actionable warnings.
- [x] Legend sizing responds to rendered width: compute a bounding box proportional to view width and scale type accordingly so fonts stay readable across options.
- [x] Anchoring ergonomics: accept `attach` / `attach_side` aliases for `anchor_point` so specs read closer to structural language.
- [x] Face alignment helpers: support `attach_edge` / `attach_face` aliases and `placement.flush.edge` so beams snap flush without manual offsets.
- [x] Directional offsets: allow mapping syntax (`offset: {west: backspan, south: walkway_gap}`) that expands into X/Y deltas automatically.
- [x] Vertical placement helper: parse `vertical` blocks (`flush.face` / `from.face`) so elevations stay declarative and zero-height datums can act as references.
- [x] Evaluate metadata expressions against option dimensions to keep vertical stacks parametric (`elevation: -pad_height`, `embed: beam_height + pad_height`).
- [x] Placement DSL: support option-level `dimensions` plus component `placement` blocks (with `from`, `move`, `offset`) so spans translate into anchors without manual math.
- [x] Component-driven boolean cutouts: allow rectangles to subtract other components (e.g. soil vs. pad foundations) so overlapping geometry stays declarative.
- [x] Introduce `GeometryBundle` abstraction.

### Phase 3 – 2.5D / glTF compatibility

- [x] Adopt Shapely 2.x inside the planner so repeats/anchors/rotations operate on real geometries (laying the groundwork for richer traits).
- [x] Extend `GeometryBundle` (and schema) with 3D metadata: component `height`, optional `elevation`, material/label metadata, and per-instance transforms.
- [x] Integrate `trimesh` to extrude polygons (respecting mm→m conversion) and build reusable meshes; serialize glTF via `pygltflib` with metadata in `extras`.
- [x] Add CLI flag/output pipeline to write `model.gltf` alongside SVG/PNG for each option.
- [x] Derive plan/section views from the canonical 3D scene when a view declares a slicing plane.
- [x] Material palette maps (`material` keys → SVG classes + glTF colors) to keep 2D/3D visuals in sync.
- [x] Keep planar views in sync by deriving plan/section slices from the canonical geometry bundle.
- [x] Expose rotation transforms in the schema (`rotation`, `rotation_anchor`, `repeat.rotate`, `repeat.about`).
- [x] Add optional orthographic rendering (`--orthographic`) via pyrender/pyglet.
- [x] Optional behaviours: span-aware linear replicate helper and mirror symmetry operations.
- [ ] Expand metadata mapping to align with IFC classes (prepping for Phase 4) – see `phase4-prep-report.md`.

### Phase 4 – CadQuery-powered solids, relationship-first solver, and IFC 4.3.2 export

Phase 4 replaces the Phase 3 anchor-based planner with a *relationship-first constraint solver*, introduces a *CadQuery (OCC) solid kernel*, and formalises a *deterministic, IFC 4.3.2-aligned export path*.
All work in this phase must preserve the overarching goal: *semantic description → deterministic YAML → canonical transforms → solids → interoperable IFC*.

**Current prep state**

- [x] Relationship-first schema loader + linter scaffolded under `diagramming/relationships` with signed-axis tokens, datums/bundles, helper clauses, IFC metadata, and a CLI guard. Specs opt in via `schema: pond-relationship*`; rendering is still legacy-only pending solver/solids. Feature flag: `DIAGRAM_RELATIONSHIPS=1`.
- [x] Relationship-first example spec and fixtures in `docs/examples/option-c-relationship.yaml` and `diagramming/tests/fixtures/relationship_minimal.yaml`; tests cover token canonicalisation and linting.
- [x] CLI lint entrypoint (`scripts/lint_specs.py`) handles both legacy and relationship-first specs.

#### Schema & solver groundwork

- [x] **Finish outstanding Phase 3 IFC metadata alignment**
  - Ensure every component already advertises IFC-ready metadata (`class`, `ifc.predefined_type`, `ifc.psets`) before solids land.
  - Adopt correct IFC entities (e.g., joists → `IfcBeam` with `PredefinedType=JOIST`, not `IfcJoist`).
  - Standardise `ifc.psets` schema for `Pset_BeamCommon`, `Pset_MemberCommon`, `Pset_SlabCommon`, etc.

- [x] **Checks + axis grammar**
  - Add `checks` block using `align`/`contact`; defaults: `gap=0.0`, `tolerance=0.5mm`, `on_fail=error`; optional `contact` (mutually exclusive with `gap`).
  - Axis tokens are signed, canonicalised (`+x+z` ordering), world-frame by default; per subject/object `frame` override: `world` (default), `local`, `component:<id>`.
  - Share the same subject/object shape across alignment helpers and checks using `pos` tokens (1/2/3 axes) with optional frames; allow components, datums, or bundles as targets where applicable.
  - Land `run_between` helper: start/end anchors via `start_pos`/`end_pos`, direction from `from→to`, optional `orient: along_run`, `count`/`pitch`/`inset`/`include_seed` for instance spacing.

- [x] **Land the full relationship-first schema**
  - Build on the existing relationship-first loader: connect helper parsing to the solver and exporter paths.
  - Ship behind the `DIAGRAM_RELATIONSHIPS` feature flag; legacy anchor specs should remain loadable until migration completes.
- [x] **Standardise 3-axis sizes in schema**
  - Collapse component `size`/`height` into a single `[x, y, z]` vector (missing axes default to 0).
  - Positional tokens default to edge/face centres when a dimension is zero.
  - Wire this through the relationship loader as the first solver implementation step.

- [x] **Implement the constraint solver + diagnostics layer**
  - Resolve face/edge/plane relationships deterministically. **Progress:** box-only solver emits CadQuery-backed neutral primitives with DOF/check diagnostics, constraint graph export, and deterministic GUID seeds; assemblies and non-box solids remain.
  - Produce canonical transforms for each component (local placement, rotation, flip, inset).
  - Detect and surface **under-constrained**, **over-constrained**, and **inconsistent** relationships.
  - Export the constraint graph + DOF report for debugging.
  - Block CLI builds automatically when solving fails.

- [x] **Enforce deterministic identifiers**
  - Stable component UUIDs seeded from `(component_id, schema_version, option_id)`.
  - Deterministic ordering of constraints, relationships, and transforms.
  - All geometry must be reproducible byte-for-byte given the same YAML.

- [x] **Schema → CadQuery neutral bridge definition (3D-first)**
  - Finalise the canonical “neutral geometry block” emitted by the solver:
    - 3D solid primitive (box for now, leaving room for wedge/sweep/tessellated to be added later) with canonicalised placement (origin + orientation + scale) and material tag.
    - Optional stored profile/axis curve only when required for slices/IFC Axis reps.
    - Component metadata (psets, labels, material, type) with deterministic IDs/GUID seeds.
  - CadQuery is the default hub: solver → CadQuery solids → glTF/STEP/IFC/exported slices; direct solver → exporter is only a temporary bypass if needed. **Progress:** solver now returns CadQuery solids plus OCC-derived footprints; wedges/sweeps remain TODO.

#### CadQuery integration & exports

- [ ] **Adopt CadQuery (OCC-backed) as the primary solid modeller**
  - Every component becomes a solid: joists, beams, blocking, straps, deck slabs, openings. **Progress:** box primitives are CadQuery solids; non-box profiles and assemblies remain.
  - Attach canonical transforms and intrinsic metadata to each solid; downstream exporters/renderers consume CadQuery output.

- [ ] **Schema → CadQuery adapters**
  - Components map directly to 3D solids (sweeps/boxes/tessellations) without intermediate 2D footprints.
  - Profiles are generated only when slices/IFC Axis reps need them.
  - Repeat/mirror helpers expanded into explicit component transforms before baking into solids.

- [ ] **Replace vertical anchor math with solver-driven face/edge constraints**
  - The solver decides vertical and horizontal alignment; CadQuery solids are generated only *after* relationships are resolved.

- [ ] **Maintain Shapely footprints as projections derived from CadQuery solids**
  - Plan/section renderers become OCC-backed:
    - Use OCC to generate section wires.
    - Convert wires to SVG primitives.
    - Apply existing styling routines.
  - Footprints are projections of solids, not primary geometry inputs.

- [ ] **glTF export overhaul**
  - Tessellate solids using OCC or convert CadQuery → trimesh.
  - Emit `model.glb` with full component metadata under `extras`.

- [ ] **STEP/OBJ export path**
  - Provide deterministic export for downstream engineering/QA workflows.

#### IFC 4.3.2 (Reference View) export

- [ ] **Build IFC contexts**
  - 3D model context.
  - Axis + Body subcontexts.
  - UnitAssignment: **millimetres**, **degrees**.

- [ ] **Correct class + predefined type mapping**
  - Joists → `IfcBeam` (`PredefinedType=JOIST`)
  - Beams → `IfcBeam` (`BEAM` or `EDGEBEAM`)
  - Blocking/bridging → `IfcMember`
  - Deck surface → `IfcSlab` (`FLOOR`)
  - Openings → `IfcOpeningElement` + `IfcRelVoidsElement`
  - Hangers/straps (if modelled) → `IfcFastener` or `IfcMember`.

- [ ] **Axis + Body representations**
  - Axis representation: local +X curve for linear elements.
  - Body representation: swept solid (`IfcExtrudedAreaSolid`) unless geometry requires tessellation.

- [ ] **Material assignments**
  - Linear members: `IfcMaterialProfileSetUsage` (rect profile).
  - Slabs: `IfcMaterialLayerSetUsage` (layer direction = +Z).
  - Deck planks or monolithic slab selectable per spec.

- [ ] **Openings**
  - Pond voids are modelled as true `IfcOpeningElement` bodies.
  - Host slab receives `IfcRelVoidsElement`.

- [ ] **Repeated geometry via types / representation maps**
  - For repeated joists/beams: create `IfcBeamType` or `IfcMemberType`.
  - Use `IfcMappedItem` for each instance.
  - Ensures identical geometry is not duplicated.

- [ ] **Face/plane relationships → IFC connection geometry**
  - `touch_planes` → `IfcRelConnectsElements` + `IfcConnectionSurfaceGeometry`.
  - `touch_components` face contacts → `IfcConnectionSurfaceGeometry`.
  - Edge contacts → `IfcConnectionCurveGeometry`.
  - Point contacts → `IfcConnectionPointGeometry`.

- [ ] **GUID determinism**
  - IFC GUIDs seeded deterministically using canonicalised component IDs.

#### Tooling, migration & regression safety

- [ ] **Lint + CI integration**
  Add IFC-aware checks:
  - Axis/Body reps present.
  - Opening semantics correct.
  - Units = mm/deg.
  - `IfcMaterialProfileSetUsage`/`LayerSetUsage` correctness.
  - No invalid entity types or undefined predefined types.
  - Axis token grammar and frame references valid; align checks executed post-solve and reported in diagnostics.

- [ ] **Collision/overlap detection at the solid level**
  - Integrate OCC collision checks.
  - Fixtures mirroring current 2D overlap tests.

- [ ] **Dimension annotation helpers**
  - Generate extension lines, arrows, callouts from canonical geometry.
  - Ensure plan/section dimensioning is coherent with the solid model.

- [ ] **Dual-render validation harness**
  - SVG diff (OCC wires → SVG) compared to legacy planner.
  - Mesh checksum for glTF to catch regressions.

- [ ] **Migration playbook**
  - Convert *Option C* first using full relationship-first schema.
  - Run both kernels (legacy + new) to confirm identical plan/section geometry.
  - Batch-migrate remaining specs.
  - Retire anchor schema once all specs pass lint + solver.

- [ ] **Performance profile & caching**
  - Cache solids per option.
  - Enable incremental builds.
  - Optimise OCC tessellation paths.

**Deliverable at end of Phase 4:**

A deterministic, IFC-aligned 3D modelling pipeline where *semantic YAML specs* produce *canonical solids*, *interoperable IFC files*, *STEP/OBJ*, *tessellated glTF*, and *2D SVG/PNG* — all driven by one constraint-resolved source of truth.

### Phase 5 – Rich modelling, analysis, and extended integrations

With CadQuery + IFC export in place, Phase 5 focuses on **richer modelling patterns** and **deeper integrations**, not on standing up the core pipeline.

- [ ] Optional Maker.js or additional geometry helpers for fillets/mitres and non-rectangular details where OCC primitives are awkward.
- [ ] Template library (e.g., `linear_grid`, `cantilevered_grid`, `joist_bay`, `stair_run`) with schema-based validation via `pydantic`.
- [ ] Extended IFC capabilities:
  - Optional Design Transfer View exports where editable parametrics are beneficial.
  - IFC property templates and bSDD / Uniclass / other classification mappings for joists, beams, slabs.
- [ ] Analysis hooks (future):
  - Export structural “analysis views” (e.g., member centrelines with loads) for external tools.
  - Optional QTO-focused IFC views (quantities, areas, volumes).
- [ ] Incorporate ELK/Dagre (or similar) for graph-like layout in complex attachment/connection diagrams.
- [ ] Provide a `--explain` CLI flag dumping intermediate constraint/geometry overlays (SVG/JSON) for debugging.
- [ ] Footprint offset helpers (on solids, not just 2D) to keep reveals/tolerances declarative without manual size tweaks.

### Phase 6 – Authoring UX & tooling

Phase 6 focuses on **author ergonomics**, **validation UX**, and **lightweight front-ends** over the now-stable engine.

- [ ] Joist/post pattern macros and higher-level “deck presets” that expand spans + spacings into full component sets.
- [ ] Dedicated spec/IFC validator CLI (`scripts/validate_spec.py`) that reports schema, constraint, and IFC mapping issues.
- [ ] Auto-generated schema documentation (`docs/schema.md`) including IFC-related fields and helper patterns.
- [ ] Optional lightweight web UI (React/Next) that edits specs and previews diagrams by calling the planner/solver API.
- [ ] Authoring assistants that convert prose design briefs (like `design-C.md`) into starter YAML using the relationship-first schema.
- [ ] Quality-of-life features: template wizards, copy/paste between options, quick “diff view” of geometry between versions.

---

## 7. Open questions / decisions (tracked)

- **glTF metadata schema:** define consistent `extras` for joists, posts, beams (and ensure it lines up sensibly with IFC psets where possible).
- **Legend layout:** keep CSS-based legend vs. upgrade to richer table layout helper.
- **Section coverage:** extend the schema to describe joist framing on multiple axes (e.g. return legs around corners) so canonical slices include all support members without manual duplication.
- **Validation/back-end selection:** CadQuery is the default solid kernel; only re-evaluate (pythonOCC, FreeCAD, Blender, external APIs) if we hit clear limitations or licensing issues.
