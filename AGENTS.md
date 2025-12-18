# Repository guidelines

## Project structure & docs

- `diagramming/` – engine; `planner/` for plan/section bundles, `relationships/` for relationship-first loader/solver/lint, `renderers/` for SVG, palette in `materials.py`.
- Relationship specs (`schema: pond-relationship*`) are default (`DIAGRAM_RELATIONSHIPS=1`). Axis-map `relate` entries map subject axes to targets with `ref`/`pos`/`gap`/`offset`/`mode`; `flush` expands to axis-map entries; `place` embeds per-placement axis-maps. Frames (`world`/`local`/`component:<id>`) are honoured in placement. Arrays use `array` (legacy `run_between`) with axis-map `start`/`end`; `orient: along_run` aligns +X to the span and can infer/interpolate size. `kind: reference` components are geometry-less anchors; size inference fills missing axes and lints conflicts. Selectors (`id`, `id.original`, `id.clones`) work in typed `operations` (rotate/mirror/translate/boolean); mirror reflects across axis-aligned planes while keeping frames right-handed. Collisions respect `DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore` and skip footings by default; set `DIAGRAM_RELATIONSHIPS_FAIL_ON_WARN=1` to promote warnings. Checks assert coordinate equality only; tolerance/on_fail pending.
- Specs live in `diagrams/specs/`; generated artefacts in `diagrams/output/` (git-ignored). Long-lived revisions and superseded docs live under `archive/` (relationship references/reporting now archived there).
- Canonical docs: `README.md` (front page), `DEVELOPMENT.md` (maintainer + architecture guide), `dev/roadmap.md` (task tracker only), `docs/instructions.md` (spec authoring quick reference). Historical architecture notes live in `archive/architecture-spec.md`. Update these when behaviour changes.

## Build, test, and development commands

- `python3 -m pip install -r requirements.txt` (activate venv first: `python3 -m venv .venv && source .venv/bin/activate`).
- Build: `python scripts/build_diagrams.py --spec diagrams/specs/deck-framing.yaml --option A --outdir diagrams/output --force` with flags `--no-png`, `--no-gltf`, `--no-ifc`, `--gltf-format gltf`, `--orthographic`. Relationship builds emit IFC unless skipped.
- Lint: `python scripts/lint_specs.py --relationship-only` (or `--legacy-only`), runs solver + IFC validation, collision reporting (`DIAGRAM_RELATIONSHIPS_COLLISIONS=error|warn|ignore`), selector/coverage checks, mesh digests.
- Tests: `python -m unittest discover`.
- Baseline freshness: pair render checks with `./.venv/bin/python scripts/baseline_render_check.py --fresh-check` and note results (e.g., “baseline render check passed; rerun … for details”).
- Helpful spot checks: `scripts/check_water_area.py <spec> --option <key>`; `diagramming/tests/test_layering_debug.py` for layering regressions. If a command fails due to a missing dependency, rerun via the venv (`./.venv/bin/python …`) and add the package to `requirements.txt`.

## Coding style & naming

- Python 3.12+, PEP 8, 4-space indent. snake_case for variables/functions; PascalCase for dataclasses. YAML uses lowercase keys and hyphenated filenames; keep IDs unique per option. Material keys (`decking`, `joist`, `timber`, `water`, `soil`) map via `diagramming/materials.py`.

## Testing guidelines

- Tests live in `diagramming/tests/`; rely on `unittest`. Use fixtures under `diagramming/tests/fixtures/` for regression coverage. Add view-specific assertions for new planner behaviours (e.g., slice coordinates, legend entries). Run `python -m unittest discover` before submitting.

## Workflow & communication

- NEVER use the view image tool to view `.svg`s; only use it for `.png`s.
- User prefers collegial, clear communication. Reference filenames only (omit paths/line numbers unless needed to disambiguate); avoid git-status rundowns unless requested.
- Complete immediate follow-up work (tests, quality checks, documentation updates) without extra prompting; confirm before starting sizable or risky follow-ups.
- Keep DI seams substitutable when adding interfaces/adapters; document mitigations if any SOLID principle is at risk.
- Keep canonical docs current as work lands; note any new dependencies or config changes. glTF exports derive from plan geometry; ensure `height`/`material` metadata is present when authoring to avoid empty meshes.
