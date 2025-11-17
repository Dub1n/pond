# Deck diagram pipeline roadmap

This document captures the target state for the “just works” renderer, alongside the phased milestones that will take us there. It complements the high-level overview in `README.md`.

---

## Recent progress

- Plan renderer now computes Shapely coverage for lower-elevation members and clips their fills before painting, ensuring deck surfaces mask joists and beams while dashed hidden outlines remain clear (beams stay temporarily green for debugging).
- Base CSS applies a more specific hidden-outline rule so material fills can no longer bleed through when debug overlays are active, and the renderer now emits stroke width/colour explicitly for hidden paths.
- `RendererTests.test_hidden_beam_overlay_visible_without_fill` gained a raster assertion on deck pixels, guarding against regressions where buried framing reappears in PNG exports.
- Partial-coverage cases are earmarked for validation in the next iteration; today’s pipeline treats fully buried members as hidden and will need refinement once partially exposed framing specs land.

## 1. Target repository layout (draft)

```filesystem
/
├── README.md
├── roadmap.md
├── requirements-diagrams.txt
├── Makefile
│
├── diagramming/
│   ├── __init__.py
│   ├── schema/                 # Declarative model definitions & validators
│   │   ├── __init__.py
│   │   ├── base.py              # Shared dataclasses / pydantic models
│   │   ├── primitives.py        # Rectangle/polyline primitives
│   │   ├── traits.py            # Optional behaviours (repeat, anchor)
│   │   └── decks.py             # Domain-specific enums/rules
│   │
│   ├── planner/                 # Turns schema → geometry
│   │   ├── __init__.py
│   │   ├── geometry.py          # Shapely helpers (offsets, unions, slicing)
│   │   ├── layouts.py           # Legend, joist grids, callouts
│   │   ├── planner.py           # DiagramPlanner orchestrator
│   │   └── exporters/           # GeoJSON/DXF/glTF writers (pluggable)
│   │       ├── __init__.py
│   │       ├── svg.py
│   │       ├── png.py
│   │       ├── geojson.py
│   │       └── gltf.py
│   │
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── svg_scene.py         # Existing SvgScene abstraction
│   │   ├── styles/              # Shared CSS snippets (plan, section, detail)
│   │   └── annotations.py       # Dimension arrows, tags, legend drawing
│   │
│   └── tests/
│       ├── __init__.py
│       ├── fixtures/            # Sample specs / reference outputs
│       ├── test_schema.py
│       ├── test_geometry.py
│       └── test_rendering.py    # SVG snapshot tests
│
├── diagrams/
│   ├── specs/                   # Author-ed YAML/JSON specs
│   │   ├── deck-framing.yaml
│   │   └── edge-attachments.yaml
│   └── output/                  # Generated artefacts (gitignored)
│       └── …
│
├── docs/
│   ├── design.md
│   └── schema.md               # Auto-generated schema reference
│
├── scripts/
│   ├── build_diagrams.py       # CLI entrypoint
│   └── validate_spec.py        # (future) standalone schema validator
│
└── pictures/                   # Reference photos (if needed)
```

This arrangement keeps the author-facing specs in `diagrams/specs/`, while the engine (schema + planner + renderers) lives under `diagramming/`.

---

## 2. Target architecture (draft)

```diagram
Spec (YAML/JSON)
      │
      ▼
Schema loader (light validation)
      │ produces
      ▼
Typed model (components, views, traits)
      │ into
      ▼
DiagramPlanner
  ├── geometry kernel (Shapely)
  ├── layout utilities (legend, joist grids, callouts)
  └── domain rules (cantilever checks, spacing guarantees)
      │ yields
      ▼
Neutral geometry bundle (polygons, polylines, metadata)
      │ fan-out to exporters
      ├── SVG renderer (SvgScene + CSS styles)
      ├── PNG (cairosvg)
      ├── GeoJSON (future-ready interoperability)
      └── glTF (optional 2.5D + later 3D)
```

Key points:

- **Canonical model:** All components are defined once; plans/sections/attachment views are slices or projections of that model.
- **Geometry-first:** Shapely manages offsets/buffers; any 3D exporter extrudes the same 2D polygons via `trimesh`.
- **Pluggable exporters:** New formats just implement `export(bundle, path, options)` without touching the planner.
- **Behaviour traits:** The planner supports additive behaviours (“repeat”, “cantilever”, “align to…”) so domain logic is reusable.

---

## 3. Integration points & dependencies

| Purpose                                          | Dependency                  | Notes                                                                                                      |
| ------------------------------------------------ | --------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 2D geometry ops (union, offset, slice)           | **Shapely 2.x**             | Primary kernel; deterministic and battle-tested.                                                           |
| Optional precise offsetting / parametric helpers | Lightweight Python helpers  | We avoid bundling Node. If Shapely (plus small scripts) isn’t enough, we port the necessary Maker.js math. |
| Legend/callout text layout                       | internal utilities (Python) | Single-pass layout using bounding boxes; no external dep needed.                                           |
| Graph-like auto layout (future)                  | **ELK.js** or **Dagre**     | Only when needed (e.g., attachment diagrams with ports).                                                   |
| 2D → PNG conversion                              | **cairosvg**                | Optional; unchanged.                                                                                       |
| 2D → 3D extrusion / glTF export                  | **trimesh** + **pygltflib** | Plan/section geometry extruded to thin solids, metadata stored in glTF extras.                             |
| IFC export (future)                              | **IfcOpenShell**            | Optional adapter to map components to Ifc classes (joist → `IfcBeam`, deck → `IfcSlab`).                   |

glTF compatibility is a hard requirement for later phases: every planner bundle will be convertible to glTF (either natively, or via a small adapter) so that AR/3D viewers can pick it up.

---

## 4. Reference snippets (Phase 1 sketch)

**Spec fragment (Phase 1 primitives only):**

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

**Pseudo-code: DiagramPlanner (Phase 1 skeleton):**

```python
def compile_plan(spec: PlanSpec) -> GeometryBundle:
    bundle = GeometryBundle()

    for comp in spec.model.components:
        poly = resolve_rectangle(comp.params["size"])
        poly = anchor_polygon(poly, comp.anchor, spec.model)
        if comp.repeat:
            polys = replicate(poly, comp.repeat)
        else:
            polys = [poly]
        for geom in polys:
            bundle.add_polygon(geom, label=comp.label, id=comp.id)

    # Legend auto build
    bundle.legend = build_legend(bundle)
    return bundle

def render_svg(bundle: GeometryBundle, style: StyleSheet) -> str:
    scene = SvgScene()
    for item in bundle.polygons:
        scene.polygon(item.geom, class_=style.class_for(item))
    add_legend(scene, bundle.legend)
    return scene.to_string()
```

This is intentionally minimal: rectangles + anchors + repeat + labels. As later traits and templates arrive, the `replicate` helper grows and the geometry bundle gains more metadata (e.g., heights).

**Anchoring semantics (Phase 1):**

```yaml
anchor:
  ref: deck                # component we snap to
  align: north_west        # point on the reference component
  anchor_point: center     # point on this component that aligns (defaults to center)
  offset: [0, 0]
```

- `align` picks the reference point (`center`, `north`, `north_east`, `north_west`, `east`, `south`, `south_east`, `south_west`, `west`).
- `anchor_point` (optional) picks which point on the component aligns; defaults to `center` so existing specs keep working.
- `offset` is applied after both points coincide.
- Cut-outs reuse the same block with `ref: self` to position the void relative to the parent rectangle.

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

### Phase 1 – Minimal deterministic pipeline (completed)

- [x] Schema supports `rectangle` & `polyline` primitives with `anchor`, `repeat`, `label` (see `diagramming/schema`).
- [x] Planner resolves anchors + repetition + simple spacing; outputs plan & section geometry; legend auto-generated (see `diagramming/planner`).
- [x] Exporters: SVG by default with PNG snapshots when `cairosvg` is present (auto-skipped otherwise).
- [x] Light validation for required fields and anchor references keeps authoring ergonomic.
- [x] Test suite covers schema parsing, planner geometry, SVG rendering, and CLI integration via `python3 -m unittest`.
- [x] Renderer enforces white backgrounds and accepts an optional spec-level `scale` for consistent sizing; defaults remain sensible when omitted.
- [x] Per-view overrides (`pad`, `scale`, `background`) and legend typography scaling keep outputs readable across renders.

### Phase 2 – Extended geometry & exports

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

### Phase 3 – 2.5D / glTF compatibility

- [x] Adopt Shapely 2.x inside the planner so repeats/anchors/rotations operate on real geometries (laying the groundwork for richer traits).
- [x] Extend `GeometryBundle` (and schema) with 3D metadata: component `height`, optional `elevation`, material/label metadata, and per-instance transforms.
- [x] Integrate `trimesh` to extrude polygons (respecting mm→m conversion) and build reusable meshes; serialize glTF via `pygltflib` with metadata in `extras`.
- [x] Add CLI flag/output pipeline to write `model.gltf` alongside SVG/PNG for each option.
- [x] Derive plan/section views from the canonical 3D scene when a view declares a slicing plane.
- [x] Material palette maps (`material` keys → SVG classes + glTF colors) to keep 2D/3D visuals in sync.
- [x] Keep planar views in sync by deriving plan/section slices from the canonical geometry bundle.
- [x] Expose rotation transforms in the schema (`rotation`, `rotation_anchor`, `repeat.rotate`, `repeat.about`) so declarative specs can drive radial layouts.
- [x] Add optional orthographic rendering (`--orthographic`) that consumes the canonical scene via pyrender/pyglet to produce 3D snapshots.
- [x] Optional behaviours: span-aware linear replicate helper (count/interval/span + direction) and mirror symmetry operations so repetitive layouts stay declarative.
- [ ] Expand metadata mapping to align with IFC classes (prepping for Phase 4).

### Phase 4 – CadQuery-powered 3D kernel

#### Schema & solver groundwork

- [ ] Finish the outstanding Phase 3 IFC metadata alignment so every component already advertises IFC-ready class IDs before solids land.
- [ ] Land the relationship-first schema outlined in `docs/phase4-prep-report.md` (datums, bundles, helper clauses, assemblies) behind a feature flag; keep current anchor specs readable until migration completes.
- [ ] Implement the constraint solver + diagnostics layer that resolves face/edge relationships, surfaces under/over-constrained components, exports constraint graphs for debugging, and blocks CLI builds when solving fails.
- [ ] Ship the lint CLI (`scripts/lint_specs.py`), CI wiring, updated authoring docs/worksheet, and publish an Option C example spec so contributors can rehearse the new schema before the kernel swap.

#### CadQuery integration & exports

- [ ] Adopt CadQuery (OCC-backed) as the primary solid modeller; represent every component as a solid with canonical transforms, metadata, and material tags.
- [ ] Build schema → CadQuery adapters (rectangles, polyline-derived extrusions, repeat/mirror helpers) so constraint-solver output generates solids directly.
- [ ] Maintain Shapely footprints as derived projections from the solid scene for legacy compatibility/quick unions.
- [ ] Replace vertical anchor math with solver-driven face/edge constraints resolved against CadQuery solids; record bounding boxes and collision checks from the kernel.
- [ ] Rework plan/section renderers to consume CadQuery projections/sections: generate wires from OCC, convert to SVG primitives, and apply existing styling/legend routines.
- [ ] Rebuild glTF export to tessellate CadQuery solids (via OCC exporters or conversion to trimesh); add STEP/OBJ export path for interoperability.
- [ ] Dimension annotation helpers: generate extension lines, arrows, and callouts from canonical geometry (plan/section aware).

#### Tooling, migration & regression safety

- [ ] Introduce collision/overlap detection tests at the solid level plus fixtures that parallel the current 2D assertions.
- [ ] Provide migration path and documentation for existing specs (convert Option C first, run dual-kernel validation, retire the anchor schema once all specs pass lint + solver).
- [ ] Evaluate performance/CI impacts; cache solids per option to keep builds deterministic and efficient.
- [ ] Add a dual-render validation harness (SVG diff + mesh checksum) so CadQuery projections and glTF output stay in lockstep with the legacy pipeline during rollout.

### Phase 5 – Rich modelling & external integrations

- [ ] Optional Maker.js integration for fillets/mitres on rectangles (if needed).
- [ ] Expand metadata mapping to align with IFC classes (prepping for IfcOpenShell export).
- [ ] Introduce template library (e.g., `linear_grid`, `cantilevered_grid`) with schema-based validation via `pydantic`.
- [ ] Add optional IFC export (IfcOpenShell) mapping components to `Ifc*` entities.
- [ ] Incorporate ELK/Dagre for graph-like layouts (complex attachment diagrams).
- [ ] Provide `--explain` CLI flag dumping intermediate geometry overlays for debugging.
- [ ] Footprint offset helpers (buffer solids once the CadQuery kernel lands) so reveals/tolerances stay declarative without manual size tweaks.

### Phase 6 – Authoring UX & tooling

- [ ] Joist/post pattern macros: declarative helpers that expand named spans into repeated components automatically.
- [ ] Dedicated spec validator CLI (`scripts/validate_spec.py`).
- [ ] Auto-generated schema documentation (`docs/schema.md`).
- [ ] Optional lightweight web UI (React/Next) that edits specs and previews diagrams by calling the planner API.

---

## 7. Open questions / decisions (tracked)

- **glTF metadata schema:** define consistent `extras` for joists, posts, beams (maybe align with IFC namespace).
- **Legend layout**: keep CSS-based legend vs. upgrade to richer table layout helper.
- **Section coverage:** extend the schema to describe joist framing on multiple axes (e.g. return legs around corners) so canonical slices include all support members without manual duplication.
- **Validation/back-end selection:** CadQuery vs. pythonOCC vs. FreeCAD vs. Blender vs. external engineering APIs – re-evaluate only if CadQuery proves insufficient for the solid kernel.
