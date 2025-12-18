# Pond deck diagramming

Relationship-first Python engine that turns declarative YAML specs into plan/section SVGs, PNG snapshots, and interoperable 3D exports (glTF/IFC/STEP/OBJ). Relationship builds are on by default (`schema: pond-relationship*`, `DIAGRAM_RELATIONSHIPS=1`) and fall back to the legacy planner only when explicitly disabled.

```mermaid
flowchart LR
  Spec[Deck/attachment spec (YAML)] --> Loader[Schema loader \n + relationship solver]
  Loader --> Planner[Planner & renderers]
  Planner --> SVG[Plan/section SVG \n + optional PNG]
  Loader --> Solids[CadQuery solids]
  Solids --> Exports[glTF/GLB, IFC, STEP/OBJ \n + orthographic snapshot]
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python scripts/build_diagrams.py --spec diagrams/specs/deck-framing.yaml --option A --outdir diagrams/output --force
```

- SVGs (and PNGs when `cairosvg` is available) land in `diagrams/output/<spec>/<option>/` alongside `model.glb` (or `.gltf` with `--gltf-format gltf`). IFC exports arrive for relationship builds; skip with `--no-ifc`. Add `--no-png` or `--no-gltf` when iterating. `--orthographic` writes a headless 3D snapshot (requires `pyrender`/`pyglet`); `--step`/`--obj` emit additional 3D exports when the CadQuery solver is active.
- Lint specs before committing: `python scripts/lint_specs.py --relationship-only`. Pair render checks with `./.venv/bin/python scripts/baseline_render_check.py --fresh-check` and note the result.

## Relationship schema highlights

- Axis-map `relate` entries map subject axes (`+x`, `-x+y`, `cxcy`, `~x`, etc.) to targets with explicit `ref`/`pos`/`gap`/`offset`/`mode`. `flush` sugar expands to these entries; `place` embeds per-placement axis-maps. Frames are parsed (`world`/`local`/`component:<id>`) but solving is currently world-space only.
- Arrays use `array` (legacy alias: `run_between`) with axis-map `start`/`end` blocks; `orient: along_run` aligns +X to the span and interpolates sizes from start/end faces. Instances accept selectors (`id`, `id.original`, `id.clones`) in typed `operations` (rotate/mirror/translate/boolean); rotations remap numbered clones.
- Components can be solids or geometry-less references (`kind: reference`). Missing sizes infer from relation pairs; conflicts lint. Checks reuse the same axis-map vocabulary and currently assert coordinate equality only.

## What you can build

- Deck framing plans/sections (see `diagrams/specs/deck-framing.yaml`) with responsive SVG output, legends, and synchronized plan/section slices derived from the canonical 3D scene.
- Attachment details (`diagrams/specs/edge-attachments.yaml`) with variant-specific parameters.
- 3D deliverables for downstream tools: glTF/GLB with component metadata, IFC 4.3 Reference View (mm/deg units, Model/Axis/Body contexts, void relationships), optional STEP/OBJ, and orthographic snapshots for quick QA.

## Usage tips and gotchas

- Activate the venv before running scripts; if a dependency is missing, rerun the command via `./.venv/bin/python …` and add the package to `requirements.txt`.
- Keep specs declarative: prefer axis-map relates and `array` spans over manual coordinates. Use center tokens when anchoring symmetric geometry to avoid conflicting size inference.
- Collision handling: set `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore` (default `error`) or pass `--collision-mode/--collision-ignore/--fail-on-warn` to `scripts/build_diagrams.py` and `scripts/lint_specs.py`.
- Do not hand-edit `diagrams/output/` artefacts; regenerate instead. Keep `docs/instructions.md` handy when authoring specs and see `DEVELOPMENT.md` for maintainers.

## Exports to Blender and friends

1. Run `python scripts/build_diagrams.py --spec diagrams/specs/deck-framing.yaml --option A --outdir diagrams/output --force` (add `--no-png` if you only need 3D output).
2. Import `model.glb` into Blender (`File → Import → glTF 2.0`). Units are metres; IDs, labels, and materials are embedded in node metadata. Each resolved component (including repeats/clones/booleans) is its own glTF node.

For implementation details, architecture notes, and development workflows, see `DEVELOPMENT.md` and `architecture-spec.md`. Tasks live in `dev/roadmap.md`.
