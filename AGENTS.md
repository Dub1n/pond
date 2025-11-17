# Repository Guidelines

## Project Structure & Module Organization

- `diagramming/` – core engine; planner logic in `planner/`, schema loaders in `schema/`, renderers in `renderers/`, material palette in `materials.py`.
- `diagrams/specs/` – author-facing YAML specs; long-lived revisions live under `archive/`.
- `diagrams/output/` – generated artefacts (`plan.svg/png`, `section.svg/png`, `model.glb`). Git-ignored; regenerate on demand.
- `scripts/` – CLI entry points (`build_diagrams.py`).
- `diagramming/tests/` – unittest suite covering schema, planner, renderer, CLI.
- Docs (`README.md`, `architecture-spec.md`, `roadmap.md`) outline architecture and future phases.

## Build, Test, and Development Commands

- `python3 -m pip install -r requirements.txt` – installs Shapely, trimesh, pygltflib, mapbox-earcut, cairosvg.
- `source .venv/bin/activate` (after `python3 -m venv .venv`) – activate virtualenv before running commands.
- `python scripts/build_diagrams.py --spec archive/diagrams/specs/deck-framing.yaml --option A --outdir diagrams/output --force` – regenerate plan/section PNG/SVG plus `model.glb` for Option A.
- Flags: `--no-png`, `--no-gltf`, `--gltf-format gltf`, `--spec` (multi-select), `--option`.
- `python -m unittest discover` – run Phase 1 test suite.
- NEVER use the view image tool to view `.svg`s, only use the view image tool for `.png`s.

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
