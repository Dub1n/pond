# Pond Diagramming – Phase 1 Architecture Spec

## Overview

Phase 1 delivers a deterministic 2D pipeline that converts declarative YAML specs into SVG (and optional PNG) diagrams. The goal is to minimise hand-tuned geometry while keeping the stack lightweight and easy to extend in later phases. A relationship-first loader/solver now exists in `diagramming/relationships` (feature-flagged via `DIAGRAM_RELATIONSHIPS=1`) to stage the next-generation schema; behind the flag it resolves neutral CadQuery-backed box primitives, projects plan/sections, and feeds the existing renderers, while the legacy planner remains the default for non-relationship specs.

```diagram
YAML spec ──> Schema loader ──> DiagramPlanner ──> GeometryBundle ──> SVG/PNG/GLB files
```

- **Schema layer (`diagramming/schema/`)** parses and validates author input.
- **Planner (`diagramming/planner/`)** resolves anchoring/repeats with Shapely geometries and emits reusable primitives (2D + 2.5D metadata).
- **Renderer (`diagramming/renderers/`)** serialises primitives to SVG, with shared styles and legend rendering.
- **CLI (`scripts/build_diagrams.py`)** orchestrates builds across specs/options and produces artefacts under `diagrams/output/` (SVG/PNG plus glTF/GLB models).

## Schema Layer

### Responsibilities

- Parse YAML mappings into dataclasses (`RectangleComponent`, `PolylineComponent`, etc.).
- Provide validation for required fields, anchor structure (including orphan detection), repeat spacing, and duplicate IDs.
- Expose `DiagramSpec` with named options and view metadata.
- Honour optional `scale` (pixels per unit) so render outputs can be resized without changing geometry, plus per-view overrides (`pad`, `scale`, `background`).
- Views may declare a slicing plane (`plane.axis` + `plane.coordinate`) so sections are cut from the canonical 3D model instead of being hand-authored (`axis: x` slices along the Y direction, `axis: y` slices along the X direction).
- Normalise anchoring aliases (`attach`, `attach_edge`, `attach_face`) plus the `placement.flush.edge` helper in XY and the new `vertical.flush.face` shorthand in Z so face-to-face snaps stay declarative and immune to width tweaks.
- Extend repeat parsing to accept `direction` + `interval`/`span` combinations, letting authors derive spacing or counts from spans without hard-coding XY vectors.
- Accept optional `metadata`, `traits`, and future `height` fields without affecting Phase 1 output, while evaluating numeric metadata expressions against option-level dimensions (e.g., `elevation: -pad_height`).
- Accept optional `ifc` blocks (`predefined_type`, `psets`) on components and preserve them in feature/mesh metadata to prep IFC exports.
- Support component-driven boolean cutouts via `boolean.subtract`, letting rectangles reference other component IDs (and their repeats/rotations) as subtraction masks.

### Key types

- `Anchor`: Declarative alignment (ref component, alignment key, optional offset).
- `Repeat`: Linear replication metadata, including optional `rotate` (degrees) and `about` anchors for radial copies.
- `OptionSpec`: Bundles components and per-view configuration.

### Extensibility

- New primitives are introduced by implementing `from_dict` constructors and updating `_parse_component`. Heavy validation is deferred to Phase 2 when schema tooling is added.

## Planner Layer

### Planner Responsibilities

- Resolve component origins via explicit coordinates or anchor relationships.
- Expand repeats, rotations, and cut-outs while keeping bounding boxes for downstream anchoring.
- Apply rotate and mirror operations after components resolve so symmetry transforms reuse the same geometry without duplicate YAML.
- Apply boolean subtraction when components declare `boolean.subtract`, unioning the referenced components’ geometry (including repeats and rotated clones) before removing it from the host component.
- Build `GeometryBundle` with polygon/polyline features plus legend metadata and 3D traits (height, elevation, material). Each option caches a Shapely-/trimesh-backed scene reused by all views and exporters.
- Slice section views directly from the cached scene: a `plane.axis` (`x` or `y`) plus `plane.coordinate` defines the cut, and only components that list the section in their `views` set are considered. Labels are de-duplicated to avoid repeated callouts for repeated geometry.

### Important classes

- `DiagramPlanner`: Public entry point (`plan(option, view)` → `PlannedView`).
- `ViewContext`: Tracks resolved components for anchor lookups.
- `GeometryBundle`: Collects features, pad size, legend entries.

### Behaviour notes

- Coordinates are kept in millimetres; origin defaults to `(0, 0)` when no anchor is provided.
- Components may declare `rotation` plus an optional `rotation_anchor`; the planner resolves the pivot via `Anchor` semantics and applies the transform with Shapely.
- Option-level `operations` (currently `rotate`) run after base geometry resolves, cloning groups of components around an anchor so mirrored layouts do not require duplicated YAML.
- `PolygonFeature` tracks Shapely polygons (with optional holes) and stores `height`/`elevation` so downstream exporters can extrude directly.
- Vertical placement data (`component.vertical`) is resolved against recorded elevations so pads, beams, and even zero-height datums can align in Z without hard-coded offsets.
- Legends are auto-built from unique `(label, label_id)` pairs.
- STEP/IFC/OBJ exporters and wedge/sweep profiles now extend the CadQuery solids produced by the relationship path; see `roadmap.md` for the current implementation checkpoints before embedding heavier kernels elsewhere.

## Rendering Layer

### Rendering Responsibilities

- Convert `GeometryBundle` into SVG paths and polylines.
- Apply shared CSS (`diagramming/renderers/styles/base.css`).
- Apply per-material styling (`diagramming/materials.py`) so SVG fills and glTF colours stay in sync.
- Add accessible metadata (`aria-label`, optional `<title>`), enforce a configurable background fill, and size legend typography proportionally to diagram width for consistent readability.
- Labels render for every resolved component (including repeats and rotated clones) so mirrored geometry carries its own tag; the legend still deduplicates entries.
- Optional orthographic renderer (`render_orthographic_png`) reuses the canonical `trimesh.Scene`, pushing it through pyrender's off-screen pipeline to produce `orthographic.png` snapshots without touching the SVG stack.
- Plan views execute a two-pass layering routine: first pass clips each polygon against the union of higher-elevation coverage so buried members drop their fill, then a dedicated hidden pass replays the full footprint with dashed strokes (beams are temporarily forced to green for debug sessions).

### PNG Support

- PNG snapshots are produced via `cairosvg` when installed. The renderer itself is agnostic; the CLI handles conversion.

## CLI Workflow

1. Discover specs (default: every `*.yaml` in `diagrams/specs/`).
2. For each option + view, call `DiagramPlanner.plan` and render SVG.
3. Write SVG to `diagrams/output/<spec>/<option>/<view>.svg`.
4. Unless `--no-png` is passed (or `cairosvg` is missing), emit matching PNG using the rendered SVG string.
5. Unless `--no-gltf` is passed, extrude plan geometry via `trimesh` and write `model.glb` (or `.gltf`) alongside the option.
6. When `DIAGRAM_RELATIONSHIPS=1` is set and a spec declares `schema: pond-relationship*`, load via `diagramming.relationships`, solve to neutral CadQuery-backed solids (box/wedge/sweep) with deterministic GUID seeds, project plan/section footprints via `RelationshipPlanner`, and reuse the same SVG/PNG/glTF/IFC pipeline. IFC exports now target IFC4X3 Reference View with Model/Axis/Body contexts, mm/deg units, swept solids where possible, material usages, openings, mapped items, and connection geometry. Assembly helpers such as `assembly.rotate_quadrants` are expanded in-solver; broader assembly support remains future work.

### Command-Line Flags

- `--spec`: repeatable, target specific specs.
- `--option`: repeatable, limit to certain options (case-sensitive).
- `--outdir`: override output root; defaults to `diagrams/output`.
- `--no-png`: skip PNG generation.
- `--no-gltf`: skip glTF/GLB export (produced by default).
- `--gltf-format`: choose `glb` (default) or `gltf` container.

## Testing

`python3 -m unittest` exercises:

- Schema loading (`diagramming/tests/test_schema.py`).
- Planner geometry and anchoring (`diagramming/tests/test_planner.py`).
- SVG renderer output (`diagramming/tests/test_renderer.py`).
- Raster regression (`RendererTests.test_hidden_beam_overlay_visible_without_fill`) converts plan SVG to PNG to assert hidden overlays remain visible while structural fills are fully masked by decking.
- CLI integration (`diagramming/tests/test_cli.py`).

Fixtures currently rely on the `deck-framing` spec; future phases can add dedicated fixtures under `diagramming/tests/fixtures/`.

## Phase 2 Hooks

The following seams were left to simplify upgrades:

- `GeometryBundle` already separates polygons and polylines for additional exporters (GeoJSON, glTF).
- CLI wiring anticipates more exporters; guard rails for missing dependencies are in place.
- Schema/primitives stored as dataclasses to support future `pydantic`/`jsonschema` validation upgrades.
- `GeometryBundle.scene` exposes the canonical `trimesh.Scene` so new exporters (GeoJSON, IFC) can reuse the same geometry without re-running the planner.
