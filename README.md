# Pond deck diagramming

a compiler that takes a semantic, relationship-first spec and produces a deterministic 3D scene + derived views

---

this project is a **text-first, deterministic geometry compiler** for small to medium structural systems.

designs are authored as compact, semantic YAML specifications that describe *what components exist* and *how they relate to one another*. those specifications are resolved into a single authoritative 3D scene, from which all downstream artefacts are derived: plan and section SVGs, PNG snapshots, and interoperable 3D formats including glTF, IFC, and STEP/OBJ. given the same spec, the build output is reproducible and deterministic.

the system is intentionally **not interactive CAD**. it is designed for contexts where intent, traceability, and repeatability matter more than direct manipulation. instead of positioning geometry by absolute coordinates, authors declare explicit spatial relationships: faces flush to planes, members spanning between references, arrays distributed across a defined run. sizes may be inferred where appropriate, conflicts are linted, and under- or over-constrained geometry is reported explicitly. changes propagate through the constraint graph in a predictable way, making it possible to understand *why* geometry moved, not just that it did.

because the source format is small, declarative, and human-readable, it supports workflows that are difficult or impractical in traditional CAD and BIM tools. specifications can be read directly in a text editor, reviewed and diffed in version control, and regenerated without relying on hidden state or binary project files. the verbose outputs (IFC, glTF, STEP) are treated as compiled artefacts rather than authoring surfaces.

the project is also well suited to **language-model-assisted geometry generation**. large language models are unreliable at producing pixel graphics or ad-hoc SVG, but perform well when constrained to a strict, symbolic grammar. the relationship-first schema provides such a grammar: it limits ambiguity, enforces consistency through linting and validation, and makes incorrect outputs fail loudly rather than degrade silently. this enables reliable generation of accurate, adjustable diagrams and scenes from semantic descriptions, and supports rapid exploration of design variants where visualisation helps surface issues that are not obvious from prose alone.

in addition, the tool is designed to integrate cleanly into **automated and CI-driven workflows**. specifications are deterministic, parameterisable, and inexpensive to rebuild, making them suitable for batch generation, regression testing of geometry, validation gates, and programmatic mutation (for example, sweeping dimensions or options via the CLI). unlike most CAD tooling, no interactive session is required, and results can be validated and exported entirely from the command line.

outputs are intended to be consumed by other tools for inspection, analysis, or refinement. this project focuses on occupying the narrow but important layer between **semantic design intent** and **concrete, portable geometry**, and on making that layer explicit, reproducible, and resistant to accidental drift.

if you need rapid freeform sketching, interactive CAD is a better fit. if you need a small, auditable specification that can be generated, reviewed, validated, and rebuilt into trustworthy geometry, this tool is designed for that purpose.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python scripts/build_diagrams.py --spec diagrams/specs/option-c.yaml --option C --outdir diagrams/output --force
```

- SVGs (and PNGs when `cairosvg` is available) land in `diagrams/output/<spec>/<option>/` alongside `model.glb` (or `.gltf` with `--gltf-format gltf`). IFC exports arrive for relationship builds; skip with `--no-ifc`. Add `--no-png` or `--no-gltf` when iterating. `--orthographic` writes a headless 3D snapshot (requires `pyrender`/`pyglet`); `--step`/`--obj` emit additional 3D exports when the CadQuery solver is active.
- Lint specs before committing: `python scripts/lint_specs.py` (use `--ci` in CI to enforce fail-on-warn gating). Pair render checks with `./.venv/bin/python scripts/baseline_render_check.py --fresh-check` and note the result.

## Relationship schema highlights

- Axis-map - an explicit axis-level constraint between components: `relate` entries map subject axes (`+x`, `-x+y`, `cxcy`, `~x`, etc.) to targets with explicit `ref`/`pos`/`gap`/`offset`/`mode`. Each axis-map key defines a single plane/edge/point (multi-axis keys are not shorthand for multiple independent plane constraints). `flush` sugar expands to these entries; `place` embeds per-placement axis-maps. Frames (`world`/`local`/`<component_id>`) are honoured during solving with size-axis remapping and contextual warnings + per-frame summaries when frames are not axis-aligned (component ids cannot be `world` or `local`); helper/assembly blocks are rejected in favour of explicit axis-maps. Axis-map refs can target operation clone ids, resolving faces using clone orientation.
- Datums (points/planes/bundles) resolve dimension expressions and can be referenced anywhere a `ref` is accepted.
- Arrays use `array` with axis-map entries plus directional `repeat` vectors (`"x,y,z"`); `through` blocks provide direction checks. `array` is the canonical placement block (single-instance arrays replace `relate`). Instances accept selectors (`id`, `id.original`, `id.clones`) in typed `operations` (rotate/mirror/translate/boolean); rotations remap numbered clones.
- Components can be solids or geometry-less references (`kind: reference`). Missing sizes infer from relation pairs; conflicts lint. Axis-maps support multi-reference entries for rotated placement. Checks reuse the same axis-map vocabulary, honour `tolerance` + `on_fail: warn|error|ignore`, and DOF reporting only warns when an axis remains unconstrained.

## What you can build

- Relationship-first Option C sketch (see `diagrams/specs/option-c.yaml`) with responsive SVG output, legends, and synchronized plan/section slices derived from the canonical 3D scene.
- 3D deliverables for downstream tools: glTF/GLB with component metadata, IFC 4.3 Reference View (mm/deg units, Model/Axis/Body contexts, mapped items/types, class-aligned property sets from metadata, material usages, and cloned RelVoids), optional STEP/OBJ, and orthographic snapshots for quick QA.

## Usage tips and gotchas

- Activate the venv before running scripts; if a dependency is missing, rerun the command via `./.venv/bin/python …` and add the package to `requirements.txt`.
- Keep specs declarative: prefer axis-map relates and `array` spans over manual coordinates. Use center tokens when anchoring symmetric geometry to avoid conflicting size inference.
- Collision handling: set `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore` (default `error`) or pass `--collision-mode/--collision-ignore/--fail-on-warn` to `scripts/build_diagrams.py` and `scripts/lint_specs.py`.
- Do not hand-edit `diagrams/output/` artefacts; regenerate instead. Keep `docs/instructions.md` handy when authoring specs and see `DEVELOPMENT.md` for maintainers.

## Exports to Blender and friends

1. Run `python scripts/build_diagrams.py --spec diagrams/specs/option-c.yaml --option C --outdir diagrams/output --force` (add `--no-png` if you only need 3D output).
2. Import `model.glb` into Blender (`File → Import → glTF 2.0`). Units are metres; IDs, labels, and materials are embedded in node metadata. Each resolved component (including repeats/clones/booleans) is its own glTF node.

For implementation details, architecture notes, and development workflows, see `DEVELOPMENT.md` and `architecture-spec.md`. Tasks live in `dev/roadmap.md`.
