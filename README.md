## Diagram generation

This repository now builds the pond deck diagrams procedurally from YAML specs.

**Phase 1 status:** The minimal deterministic pipeline is live. Rectangles, polylines, anchors, repeats, auto-scaled legends, per-view overrides, and optional metadata fields flow from declarative specs through a Python planner and SVG renderer. See `architecture-spec.md` for the current component breakdown.

### Quick start

```bash
python3 -m pip install -r requirements.txt  # installs Shapely, CadQuery (OCC), trimesh, pygltflib, mapbox-earcut, ifcopenshell
python3 scripts/build_diagrams.py
```

SVGs (and PNGs when `cairosvg` is available) will be written to `diagrams/output/<spec>/<option>/`.
Use `--no-png` if you only need SVG output. A glTF model (`model.glb` by default) is emitted alongside each option; disable it with `--no-gltf` or switch to `.gltf` with `--gltf-format gltf`. Relationship-first builds also emit an IFC model (`model.ifc`); skip it with `--no-ifc`.
Pass `--step` and/or `--obj` to emit `model.step` / `model.obj` for relationship-first specs when the CadQuery solver is enabled.
Pass `--orthographic` to also emit a headless 3D orthographic snapshot (`orthographic.png`); the flag requires the optional `pyrender`/`pyglet` dependencies shipped in `requirements.txt`.

### Relationship-first prep schema

- Specs marked `schema: pond-relationship*` are lintable now via `python3 scripts/lint_specs.py` and renderable when `DIAGRAM_RELATIONSHIPS=1` is set. Without the flag, the CLI skips relationship-first specs.
- The prep schema uses signed axis tokens, datums/bundles, helpers (`align`, `contact`, `flush_bundle`, `run_between`, `relate_from`), and a `checks` block; see `docs/relationship-schema-reference.md` plus the worked example in `docs/examples/option-c-relationship.yaml`.
- Relationship solving outputs neutral CadQuery-backed solids (box/wedge/sweep) with deterministic GUID seeds, OCC footprints/sections, and glTF/IFC/STEP/OBJ exports. IFC builds target IFC4X3 Reference View with Model/Axis/Body contexts, mm/deg units, swept solids where possible, material usages, openings, mapped items, and connection geometry; solver diagnostics now carry collision volumes and check results.
- Helpers now resolve frames (`world`/`local`/`component:<id>`) through align/contact/flush clauses, expand `relate_from` and `assembly.linear_bracing`, and orient `run_between orient: along_run` with 3D vectors; relationship specs expect explicit 3D `size: [x, y, z]` tuples for component solids, and section slices render upright with Z flipped internally.
- Plan/section bundles add arrowed dimension polylines derived from solved extents so annotations stay aligned with solids.
- Linting runs the solver + IFC exporter, enforcing axis tokens/frames, class/predefined-type/material expectations from the IFC mapping table, mm/deg units, Axis/Body contexts, RelVoids wiring, collision overlaps, and emits mesh digests for regression gates. Collision severity can be tuned with `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore` (defaults to `error`).
- Legacy specs can optionally include `ifc` blocks (`predefined_type`, `psets`); the loader normalises IFC class names/pset names and preserves them in feature/mesh metadata for IFC-ready exports.

### Blender export

Use the existing glTF exporter when you need geometry in Blender or any other glTF 2.0 consumer:

1. Activate the repo virtualenv (`source .venv/bin/activate`) and run `python scripts/build_diagrams.py --spec diagrams/specs/deck-framing.yaml --option A --outdir diagrams/output --force`. Add `--no-png` if you only care about the 3D asset.
2. The planner extrudes the canonical scene and writes `diagrams/output/<spec>/<option>/model.glb` (millimetres are converted to metres during export). Pass `--gltf-format gltf` when you prefer the JSON + external buffers layout instead of a `.glb`.
3. In Blender choose **File → Import → glTF 2.0**, pick the generated `model.glb`, and keep the default metre units; component IDs, labels, and materials are embedded in the mesh metadata for inspection via Blender’s Object/Data properties. Every resolved component—including repeats, rotated/mirrored clones, and boolean derivatives—exports as its own glTF node so Blender faithfully reproduces the planned symmetry.

### Specs

- `diagrams/specs/deck-framing.yaml` – plan and section for each option (A/B/C).
  - You provide metric inputs (`deck_m`, `pond_m`, `overhang_m`, etc.).
  - The renderer computes dimensions, trims the viewBox to the geometry, and places standard dimension lines with extension lines.
- `diagrams/specs/edge-attachments.yaml` – edge-attachment details.
  - Each option declares a `variant` (`anchor_trench`, `timber_clamp`, or `coping`) with only the parameters that differ (offsets, depths, component sizes).

Each spec `option` can set `title`, `aria_label`, and per-variant parameters. The CLI accepts `--spec path/to/spec.yaml` to rebuild only one spec and `--outdir` to target a different output folder. PNG snapshots are emitted by default (skip them with `--no-png` when iterating quickly).
Set the top-level `scale` (pixels per unit) to produce comfortably sized SVG/PNG exports; Phase 1 defaults to millimetres.

- Helpful optional fields:
  - Components accept `height`, `material`, and `metadata.elevation` to drive 2.5D geometry and colour palettes; omit them to keep the component planar.
  - Section views can declare a slicing plane via `views.<name>.plane.axis`/`coordinate`. `axis: x` slices along the Y direction; `axis: y` slices along the X direction. Only components whose `views` include the section name are considered.
  - Per-view overrides (`pad`, `scale`, `background`) let you tighten layout or adjust palette without affecting sibling views.
  - Existing `metadata`/`traits` fields are still honoured for future behaviours.
  - `repeat` accepts `direction`, `interval`, and `span` helpers so you can drive linear arrays from counts, spacing, or run length. Use `east`/`west`/`north`/`south` (or `+x`/`-y`) for axial repeats, or supply a `vector: [dx, dy]` for diagonals; the planner normalises the vector and derives the missing spacing or count automatically.
  - Options may declare `operations` – use `type: rotate` with `targets`, `count`, `angle`, and an `about` anchor for radial layouts, or `type: mirror` with `axis: x|y` to reflect components across horizontal/vertical axes. Operations run after the base geometry resolves, so a single joist field can be duplicated around the pond without duplicating YAML; set `include_generated: true` only if you intentionally want to transform previously created clones.
  - Rectangles support `boolean.subtract` to reuse other component footprints as cutouts (the planner unions repeats/rotations automatically), which keeps soil or decking infill declarative even around pad foundations.

### Key improvements

- Responsive SVG output (`width="100%"`, trimmed viewBox, `vector-effect="non-scaling-stroke"`) with optional PNG snapshots generated alongside when `cairosvg` is installed.
- Auto legend generation from component labels across plan/section views.
- Anchoring and repeat helpers avoid manual coordinate math when laying out posts, headers, and other repeated elements.
- Rendering helpers live under `diagramming/renderers/` with shared base styles to keep new diagram types consistent.
- Legends size themselves as a percentage of diagram width so font readability stays consistent across exports.
- Shapely-backed planner metadata allows extrusion via `trimesh`, producing glTF/GLB models with component metadata embedded for downstream tooling. The same canonical scene feeds both plan/section slices and exporters so they stay in sync.
- Material palette keeps SVG fills and glTF base colours in sync via simple `material` keys in specs.
- Plan renderer clips covered structural fills against higher layers and replays hidden geometry only as dashed overlays, so deck surfaces mask joists/beams while keeping hidden edges legible for QA.
- Future validation/back-end options (pythonOCC/STEP/FreeCAD) are tracked in `roadmap.md`; legacy planner remains the canonical geometry source for non-relationship specs while CadQuery-backed solids drive the relationship path (glTF + IFC exports).

### Roadmap: “just works” architecture

To reach a point where new diagrams render from minimal input with near-zero hand-tuning, we intend to layer a deterministic geometry pipeline on top of the current renderer. The proposal below favours proven OSS libraries where they add leverage and keeps our CLI entrypoint unchanged.

#### 1. Declarative schema layer

- Define a JSON/YAML schema (validated by `pydantic` or `jsonschema`) that describes decks, attachment details, and shared primitives (beams, joist fields, openings, annotations).
- Add a schema registry (`diagramming/schema/*.py`) to parse specs into typed models and provide defaulting/validation (e.g., `cantilever <= backspan / cantilever_ratio`).
- Ship a schema doc (generated via `pydantic`/`datamodel-code-generator`) so contributors know the minimal keys to supply.

#### 2. Geometry kernel

- Adopt **Shapely 2.x** (Python) as the geometry workhorse:
  - Use it to construct the plan envelopes, buffer outlines, and subtract openings.
  - Represent joist fields as `LineString` batches with offsets driven by schema definitions.
- For precise 2D fabrication-style offsets, integrate **Maker.js** (Node) via CLI bridge or port the required math. Shapely covers most polygon needs; Maker.js adds deterministic fillets/mitres if required.

#### 3. Layout utilities

- Build reusable “pattern” modules:
  - `layouts.linear_grid` – generates joist/post positions from span + spacing (with optional offsets and edge trims).
  - `layouts.legend` – automatically sizes a legend table given labelled components.
  - `layouts.callout` – handles arrow/leader placement with collision avoidance (backed by Shapely’s bounding boxes).
- For future detail diagrams that resemble node graphs, wire in **ELK.js** or **Dagre** through a small adapter (running in Node or via `py_mini_racer`) and feed coordinates back to the renderer.

#### 4. Rendering pass

- Keep `SvgScene` as the emitter but refactor it to accept higher-level instructions (polygons, lines, annotations) generated by the geometry/layout layers.
- Standardise styling via CSS modules stored in `diagramming/styles/*.css`; each diagram type references named style tokens.

#### 5. CLI workflow

1. `build_diagrams.py` loads each spec and validates against the schema.
2. A `DiagramPlanner` orchestrates:
   - **Geometry compilation** (`deck_kernel.plan()` / `deck_kernel.section()` returning Shapely objects + metadata).
   - **Layout enrichment** (automatic legend, callouts).
3. `SvgScene` serialises to SVG and (optionally) PNG.

- Add a `--explain` flag to dump intermediate geometry as GeoJSON/SVG overlays for debugging when a diagram misbehaves.

#### 6. Testing & determinism

- Unit tests at each layer: schema validation, geometry calculations (asserting numeric spans), SVG snapshots (e.g., `pytest-syrupy`), plus raster checks that verify hidden overlays stay visible while buried fills stay masked.
- Deterministic random seed for layout “nudges”.
- With Shapely and validated inputs, the same spec will always yield identical SVGs across environments.

#### 7. Optional future integrations

- Harness **Maker.js** or **OpenJSCAD** via a Node microservice if we need parametric joinery or CNC-ready exports.
- Expose a `diagramming/api.py` entrypoint for web tooling (e.g., a lightweight React front-end that edits specs live and calls the planner).

This architecture keeps our CLI UX intact (`build_diagrams.py` still takes specs, spits out SVG/PNG) but pushes more smarts into reusable, library-backed layers. Contributors only touch the declarative spec; the engine handles offsets, spacing, legends, and dimension placement automatically.

### Expected workflow at maturity

1. **Author a declarative spec**  
   - Create a YAML/JSON file describing the deck/attachment using the validated schema.  
   - Provide only semantic data (spans, spacing, member types, relationships) – no pixel math.
2. **Run the CLI** (`python scripts/build_diagrams.py --png`)  
   - Spec is validated (cantilever limits, spacing, required fields).  
   - Planner compiles geometry via Shapely/Maker.js helpers and auto-lays out annotations/legend.  
   - Renderer emits responsive SVG and optional PNG; debug overlays available with `--explain`.
3. **Reuse/export**  
   - Same geometry can be serialised as GeoJSON/DXF/glTF for other tools or archived for QA.  
   - Tests assert that a given spec always produces the same geometry/SVG snapshots.

Example minimal spec (two touching rectangles):

```yaml
diagram:
  type: plan
  units: mm
  layers:
    - name: framing
      components:
        - id: deck
          primitive: rectangle
          size: [2000, 1200]
        - id: pond
          primitive: rectangle
          size: [600, 600]
          anchor:
            ref: deck
            align: north_east
            offset: [-600, -600]
  legend:
    include: [deck, pond]
```

The planner interprets this as two adjacent rectangles sharing a corner, auto-generates Joist spacing/legend entries, and produces aligned plan/section views without manual tweaks.

#### Phase 1 authoring surface (current goal)

To reach the “just works” experience incrementally, Phase 1 focuses on the primitives we already use:

- `rectangle` with `size [width, depth]`; optional `anchor` (base component, alignment key, offset), optional `repeat` block for simple linear replication, optional `label`.
- `polyline` with `points [[x, y], …]`; optional `stroke_width` for attachment diagram clarity; optional `label`.
- `legend` generated automatically from labels (`label`, `label_id`).
- Minimal validation (e.g., ensure `size` exists on rectangles), avoiding heavy schema tooling until we need it.

Anchoring semantics:

```yaml
anchor:
  ref: deck                # component we snap to
  align: north_west        # reference point on that component
  attach_edge: east        # alias for anchor_point; keeps faces flush without manual offsets
  offset: [0, 0]
```

Rectangles can also declare `params.cutouts` (each with its own `anchor`, typically `ref: self`) so a deck slab with a pond void is a single component.

- For placement blocks, use `flush.edge` + `attach_edge` when you want faces to touch:

  ```yaml
  placement:
    flush:
      ref: deck
      edge: west
    attach_edge: east
  ```

  The planner expands this to the same anchor math, so specs stay resilient if widths change later.
- Mirror that approach in Z with the `vertical` block whenever you want faces to meet without hard-coding elevations:

  ```yaml
  vertical:
    flush:
      ref: pond_water
      face: top
    attach_face: top
    offset: 0    # optional; positive lifts, negative drops
  ```

  The schema resolves this into a numeric elevation before planning, so pads, beams, and soil stay tied to the datum even when their heights change.

These cover the plan/section/attachment diagrams already in the repo. Fields such as `height`, `metadata`, and `traits` are reserved for later phases so we can extend into 2.5D/3D or richer templates without breaking old specs.

### ADR notes: why a custom planner?

| Option | Strengths | Why it falls short for our use case |
|--------|-----------|--------------------------------------|
| **Generic CAD DSLs (OpenSCAD, CadQuery, Maker.js alone)** | Powerful parametric modelling | Still requires custom code per diagram and no domain validation (cantilever rules, joist spacing). |
| **Diagram DSLs (PlantUML, Mermaid, Graphviz)** | Dead-simple syntax, auto layout | Designed for graphs/flowcharts, cannot express metric geometry or structural rules. |
| **BIM schemas (IFC, gbXML, OpenStudio)** | Rich semantics, industry exchange | Heavyweight; we would still need a conversion layer and overkill for simple plan/section diagrams. |
| **Vector/GIS formats (SVG, DXF, GeoJSON)** | Universally consumable outputs | They encode final geometry only—no declarative spec or domain rules. Great export targets, not authoring formats. |

Therefore we keep a slim custom `DiagramPlanner` that:

- Validates domain rules via a schema,  
- Uses proven libraries (Shapely, Maker.js, ELK/Dagre) for geometry/layout,  
- Emits multiple exports (SVG/PNG/GeoJSON/glTF) from the same source.

This approach maximises determinism and future interoperability without forcing contributors into heavyweight BIM tooling. The planner becomes the “brain” that bridges declarative specs and reusable rendering/geometry engines.

### ADR notes: schema selection

For what we’re doing—“semantic” descriptions that turn into deterministic 2D/section geometry—there isn’t a perfect drop‑in schema, but there are a few standards worth leaning on as targets or inspirations so we stay portable:

| Standard | What it gives | How it could fit |
|----------|---------------|------------------|
| OGC Simple Features / GeoJSON | Lightweight, JSON, perfect for 2D plans | We can emit every component as a Feature with geometry (polygon/line) and properties (type, section, spacing). Many CAD/GIS tools read this straight away. |
| glTF 2.0 + metadata | Common, engine-friendly 3D format | Use when we want a quick 3D view or AR; we just extrude our 2D shapes a few millimetres and stash attributes in extras. |
| IFC (IfcJSON via buildingSMART) | The BIM lingua franca | Heavy, but we can define a small mapping (e.g. joists → IfcBeam, deck surface → IfcSlab) so an IFC file is just a call to IfcOpenShell after we do our geometry. |
| TopoJSON / CityJSON | Compact variants for sharing topology | Nice when we care about shared edges (deck vs. pond opening). Could be a future option if we do more snapping analysis. |
| DXF / SVG | Ubiquitous CAD vector formats | Already easy to export from the shapes we generate; just a matter of adding the exporter. |

Because IFC and the BIM stack are high‑overhead, my recommendation is:

1. Keep our declarative schema as-is for authoring—it’s the ergonomic layer.
2. Choose GeoJSON as the first “canonical export” (everyone consumes it, and the schema maps cleanly).
3. Add optional glTF and IFC exporters once we need them; they can read the same intermediate geometry we’re already producing.
4. Align our vocabulary with IFC where it makes sense (e.g. joist ⇢ IfcMember, support_beam ⇢ IfcBeam) so future conversion is mostly mechanical.

That way we aren’t forced into a heavyweight BIM DSL for authoring, but the data stays future-proof: if someone wants to round-trip into Revit, QGIS, or a web viewer later, the translators are already waiting.

### Maintenance cheatsheet

- Install tooling with `python3 -m pip install -r requirements.txt` (includes Shapely, trimesh, pygltflib, mapbox-earcut). Activate the repo’s `.venv` before running commands.
- Regenerate diagrams: `python scripts/build_diagrams.py --spec archive/diagrams/specs/deck-framing.yaml --option A --outdir diagrams/output --force`. Add `--no-gltf` or `--gltf-format gltf` as needed.
- Render an orthographic snapshot of the canonical 3D scene: append `--orthographic` (optionally `--orthographic-size 1536`) to emit `orthographic.png`.
- Run tests before shipping changes: `python -m unittest discover`.
- Authoring tips:
  - Use `height`/`material`/`metadata.elevation` on rectangles to feed both plan/section views and glTF extrusion.
  - Limit a component to explicit views via `views: [plan]` etc.; only components listed in a section view are sliced.
  - Metadata values accept dimension math (`elevation: -pad_height`, `embed: beam_height + pad_height`) so vertical stacks stay parametric.
  - Section planes: `axis: x` gives a north–south cut (values in the Y dimension), `axis: y` gives an east–west cut (values in the X dimension). Pick a coordinate that intersects the geometry you want to show.
  - Apply `rotation` (with an optional `rotation_anchor`) to spin a component around a pivot; combine it with `repeat.rotate` and `repeat.about` for radial layouts such as joist spokes or mirrored runs.
  - Material keys currently recognised: `decking`, `timber`, `joist`, `water`, `soil`. Extend `diagramming/materials.py` to add more.
- glTF validation: open `diagrams/output/<spec>/<option>/model.glb` in any viewer (e.g. https://gltf.report/). Mesh metadata includes `id`, `label`, `label_id`, and `material` extras.
- When adding new exporters or traits, prefer wiring them through the canonical `GeometryBundle` so SVG, glTF, and future outputs stay in sync.
