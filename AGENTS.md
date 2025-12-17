# Repository Guidelines

## Project Structure & Module Organization

- `diagramming/` – core engine; planner logic in `planner/`, schema loaders in `schema/`, renderers in `renderers/`, material palette in `materials.py`.
- `diagramming/relationships/` – relationship-first schema loader/lint + solver (default on for `schema: pond-relationship*`; `DIAGRAM_RELATIONSHIPS` env overrides) built around axis-map `relate` entries. Components can be `kind: reference` (geometry-less frames) or solids; relations map subject axes to targets with `ref`/`pos`/`gap`/`offset`/`mode`. Center tokens (`cx`, `cy`, `cz`, `~x`, etc.) are accepted in keys/targets. Frames are parsed (`world`/`local`/`component:<id>`) but currently solved in world space. Arrays use `run_between` today (planned rename to `array`) with axis-map `start`/`end` blocks; `orient: along_run` aligns +X to the span and sizes can be inferred/interpolated. `flush` sugar expands to axis-map entries (`faces: all` by default). Per-placement `place` blocks use inline axis-maps (no nested `relate`). Aggregate selectors (`id`, `id.original`, `id.clones`) work in typed `operations` (rotate/mirror/translate/boolean). Size can be inferred from relation pairs; conflicts lint unless matched. Rotations remap numbered instances. `relate_from`/assemblies are parsed but not expanded (planned removal/reeval). Mirror op is not yet implemented.
- Relationship specs supply explicit 3D `size` vectors or rely on inference and can use `run_between`/`array` for linear arrays tied to datum/reference faces (e.g., joists/pads around openings). Checks currently assert coordinate equality only; tolerance/on_fail and richer modes are planned.
- `diagrams/specs/` – author-facing YAML specs; long-lived revisions live under `archive/`.
- `diagrams/output/` – generated artefacts (`plan.svg/png`, `section.svg/png`, `model.glb`). Git-ignored; regenerate on demand.
- `scripts/` – CLI entry points (`build_diagrams.py`).
- `diagramming/tests/` – unittest suite covering schema, planner, renderer, CLI.
- Docs (`README.md`, `architecture-spec.md`, `roadmap.md`) outline architecture and future phases.

## Build, Test, and Development Commands

- `python3 -m pip install -r requirements.txt` – installs Shapely, CadQuery (OCC), trimesh, pygltflib, mapbox-earcut, ifcopenshell, cairosvg.
- `source .venv/bin/activate` (after `python3 -m venv .venv`) – activate virtualenv before running commands.
- `python scripts/build_diagrams.py --spec archive/diagrams/specs/deck-framing.yaml --option A --outdir diagrams/output --force` – regenerate plan/section PNG/SVG plus `model.glb` for Option A.
- Flags: `--no-png`, `--no-gltf`, `--no-ifc`, `--gltf-format gltf`, `--spec` (multi-select), `--option`.
- `python -m unittest discover` – run Phase 1 test suite.
- `python scripts/lint_specs.py [--relationship-only|--legacy-only]` – lint specs; runs the relationship solver + IFC export to enforce mm/deg units, Axis/Body contexts, predefined types, material usages, RelVoids wiring, collision overlaps, and emits mesh digests. Relationship linting checks axis-map coverage, inferred-size conflicts, selector validity; `base#n` refs are accepted. Collision severity adjustable via `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore`.
- Legacy specs may include optional `ifc` blocks (`predefined_type`, `psets`); the loader carries them through feature/mesh metadata for IFC-ready exports later.
- NEVER use the view image tool to view `.svg`s, only use the view image tool for `.png`s.
- Helpful local checks: `scripts/check_water_area.py <spec> --option <key>` prints expected vs rendered water coverage; `diagramming/tests/test_layering_debug.py` exercises a minimal ring-over-water fixture for layering regressions; relationship tests cover axis-map parsing, solver inference, planner integration, and validation harness checksums. Mirror/op parity and frame-aware placement are planned, not current.
- Baseline render freshness: always pair render-count checks with `scripts/baseline_render_check.py --fresh-check`. It rasterises timestamp-sized squares and exits non-zero if the render/pixel counts look stale. Run it alongside any script/test that inspects rendered output; include a short note in logs like “baseline render check passed; rerun `.venv/bin/python scripts/baseline_render_check.py --fresh-check` for details.”
- If a script/test fails due to a missing dependency, rerun with the venv tools (`.venv/bin/python …` or `source .venv/bin/activate`) and add the missing package to `requirements.txt` so future runs succeed without manual installs.
- Collision handling for relationship builds is adjustable via `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore` (defaults to `error`).

## Coding Style & Naming Conventions

- Python 3.12+, PEP 8, 4-space indentation. Descriptive snake_case for variables/functions; PascalCase for dataclasses.
- YAML uses lowercase keys, hyphenated filenames (e.g., `deck-framing.yaml`). Keep IDs unique per option.
- Materials referenced via `material` keys (`decking`, `joist`, `timber`, `water`, `soil`); update `diagramming/materials.py` when adding new ones.

## Testing Guidelines

- Tests live in `diagramming/tests/`; rely on `unittest`.
- Use fixture specs under `diagramming/tests/fixtures/` when adding regression coverage.
- Run `python -m unittest discover` before submitting. Add view-specific assertions for new planner behaviours (e.g., slice coordinates, legend entries).

## Commit & Pull Request Guidelines

- Commit messages: short imperative (“Implement glTF exporter”, “Adjust section slice plane”).
- PRs should describe scope, reference specs/options touched, include CLI commands executed (build/tests), and attach sample outputs when visuals change (`diagrams/output/<spec>/<option>/` snapshots).
- Link roadmap items or issues where relevant; note any new dependencies or config changes.

## Security & Configuration Tips

- Engine runs offline; no external network calls. Keep secrets out of specs.
- glTF exports derive from plan geometry; confirm `height`/`material` metadata when authoring to avoid empty meshes.

## Workflow & Communication

- User prefers **collegial** communication: they would like it to be *clear, helpful, and easy to scan* without sounding clipped; reinforce user reasoning and flag risks or blockers.
- User prefers reference to **filenames only**; they say to supply the full path only when more than one file shares that name, and would rather you **omit line numbers** or git-status rundowns unless specifically requested.
- User has decided that providing full file paths and line numbers is unhelpful to them.
- Complete immediate follow-up work (tests, quality checks, documentation, related updates) without additional prompting; confirm with the user before starting sizable or risky follow-ups.
- Provide right-sized implementation context, and when the user signals confusion, explain the relevant systems and approach in an instructive, task-aligned way that builds their understanding.
- When introducing new interfaces or adapters, confirm DI seams remain substitutable and document mitigation if any SOLID rule is at risk.
- Keep canonical docs (README.md, architecture-spec.md, AGENTS.md, roadmap.md, instructions.md) up to date as work lands. If a change alters behaviour, schema shape, flags, or workflow, update the relevant doc in the same effort and suggest/perform a commit when appropriate.
