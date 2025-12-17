# Pond Diagramming – Relationship-First Architecture

## Overview

The stack now centres on a relationship-first schema and constraint solver that emit neutral CadQuery-backed primitives. Axis-map `relate` entries replace legacy anchor DSLs, making placement explicit and IFC-ready. Legacy specs still load, but relationship specs (schema prefix `pond-relationship*`, flag `DIAGRAM_RELATIONSHIPS=1`) are the canonical path forward.

```text
YAML (relationship schema)
    │
    ▼
Schema loader (axis-map parsing, size inference)
    │
    ▼
Constraint solver (CadQuery solids + diagnostics)
    │
    ├─► Plan/section footprints (Shapely)
    ├─► CadQuery solids (OCC)
    └─► Metadata (IFC/glTF-ready)
            │
            ├─► Renderers (SVG/PNG)
            ├─► glTF/GLB
            ├─► IFC 4.3 Reference View
            └─► STEP/OBJ (via OCC)
```

Core traits:

- Axis-map `relate` entries keyed by subject tokens with explicit `ref`/`pos`/`gap`/`offset`/`mode` (plane|edge|point); frame tokens are parsed (`world`/`local`/`component:<id>`) but the current solver still treats all relations in world space.
- Center tokens (`cx`, `cy`, `cz`, `~x`, etc.) in keys and targets.
- Reference components (`kind: reference`) are geometry-less anchors with lenient defaults; components infer missing size axes from relation pairs, linting conflicts when explicit sizes disagree.
- `run_between` spans accept components or references and use axis-map `start`/`end` blocks (same shape as `relate`) to seed faces/centers; `orient: along_run` aligns local +X to the span and sizes can be inferred/interpolated from start/end faces. Multi-axis point anchors like `-x+y` are treated as a true corner point in `mode: point` (default), preventing diagonal spans from drifting along an edge.
- `flush` sugar expands to axis-map entries (`faces: all` default, scalar or per-face inset).
- `place` blocks embed per-placement axis-maps; no nested `relate`.
- Aggregate selectors (`id`, `id.original`, `id.clones`) apply everywhere component lists are accepted, including typed `operations` (`rotate`, `mirror`, `translate`, `boolean`).
- Deterministic GUIDs seeded from template/instance IDs; rotation id-maps remap numbered instances.

## Schema Loader

- Resolves dimensions/expressions (`dimensions.*`) and registers unique leaf aliases.
- Parses axis-map blocks for components, placements, and checks; supports `mode`, `gap`/`offset` as scalars or axis maps, center tokens, and frames.
- Instance refs with a numeric suffix (e.g. `joist_run_west#1`) are valid `ref` targets (useful for pads/checks keyed off run elements).
- Size inference: paired axes in relates fill missing `size`; conflicts lint unless equal.
- Operations: typed blocks with selector support and id maps for rotations.
- Validation hooks for missing axes (components only), bad selectors, frame targets, and inferred-size conflicts.

## Constraint Solver

- Expands placements and selectors into explicit instances.
- Applies axis-map relations with size inference, honoring center placements and per-axis gaps/offsets.
- `run_between` generates spaced instances along spans using `start`/`end` axis-maps (single-axis OK; missing axes fall back to shared relates). When `mode: point` and the subject key has multiple axes (e.g. `-x+y`), the solver anchors the true point rather than treating the entry as independent faces; sizes interpolate when start/end supply face pairs, and `orient: along_run` produces aligned orientations.
- Typed operations clone transforms with deterministic IDs; boolean ops attach void references.
- Emits neutral primitives: CadQuery solids (box/wedge/sweep) + metadata, deterministic GUIDs, stored footprints/meshes.
- Collision detection via OCC intersections; severity set by `DIAGRAM_RELATIONSHIPS_COLLISIONS`.
- Diagnostics: errors/warnings, DOF records, check results, constraint graph.

## Planner & Renderers

- RelationshipPlanner projects plan footprints/section slices from solver primitives, deriving dimension polylines from solved extents.
- GeometryBundle carries polygons/polylines, legend data, and the canonical `trimesh.Scene`.
- SVG renderer consumes bundles; PNG snapshots via cairosvg when available. Styling stays shared across legacy/relationship paths.

## Exporters

- glTF/GLB via tessellated solids with metadata in `extras`.
- IFC 4.3 Reference View: mm/deg units, Model/Axis/Body contexts, predefined types/material usages mapped from schema, openings via `IfcRelVoidsElement`, axis curves for linear members, deterministic GUIDs.
- STEP/OBJ reuse CadQuery solids; OBJ remains a tessellated fallback.

## CLI & Tooling

- `scripts/build_diagrams.py` orchestrates renders/exports; `--no-png`, `--no-gltf`, `--no-ifc`, `--gltf-format` flags apply to both pipelines.
- `scripts/lint_specs.py` runs schema + solver + IFC validation (units, contexts, predefined types/material usages, RelVoids wiring, collisions) and emits mesh digests.
- Baseline freshness: pair render scripts with `scripts/baseline_render_check.py --fresh-check`.

## Testing

- Relationship tests cover axis-map parsing (center tokens, size inference), solver placements/operations/booleans, planner integration, and validation harness checksums, including regression coverage for multi-axis `run_between` point anchors.
- Legacy tests remain for anchor DSL regressions. Run `python -m unittest discover` from an activated venv.

Current gaps vs the prep surface: frames are ignored at solve time; checks only assert equality (no tolerance/on_fail); `relate_from` and assembly expansion are not implemented; IFC linting/enforcement is limited to a small set of entities.

## Migration Notes

- Relationship schema supersedes legacy anchors/flush_bundle/align/contact; keep legacy path only for archived specs.
- Specs adopting relationship mode should use axis-map relates, references, `place`, `run_between`, and typed `operations` for booleans/rotations instead of legacy helpers.
