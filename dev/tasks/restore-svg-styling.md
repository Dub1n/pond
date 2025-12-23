## Restore SVG Styling via CSS Classes

We temporarily stripped CSS class usage from rendered paths to stop `.material-water` rules from repainting deck features. As a result, `base.css` stroke widths and other class-based styles no longer apply. This task is to reintroduce class-driven styling safely.

### Goals

- Reinstate class attributes on SVG paths so `diagramming/renderers/styles/base.css` and material classes drive fill/stroke widths and other styles.
- Prevent water/material rules from overriding other materials’ fills/strokes.
- Keep hidden outlines thin and configurable (current target ~0.4px effective).
- Preserve correct layering: higher-elevation polygons must paint over lower ones, even with cutouts.

### Context / Repro

- Current renderer emits inline fills/strokes without class attributes to avoid `.material-water` bleed.
- Changing stroke widths in `base.css` has no effect because classes aren’t on paths.
- Layering regression is covered by `diagramming/tests/test_renderer.py`.

### Proposed Approach

1) Re-enable class emission on polygon paths (component + material classes).
2) Scope CSS to avoid cross-material bleed:
   - Narrow selectors (e.g., `.material-water` only matches explicit water elements).
   - Consider adding a namespace class on the scene or per-path to anchor selectors.
3) Decide precedence: prefer inline for fill/stroke? Or adjust CSS specificity to let class rules win safely.
4) Verify hidden-outline sizing still uses the code-based pixel targets; adjust if necessary.

### Acceptance Criteria

- Renderer layer-order tests pass (deck ring clips water correctly).
- Changing `stroke-width` in `base.css` visibly affects outlines again.
- Water coverage checks for options A/B/C remain within expected ratios.
- No stray debug colors (e.g., green outlines) reappear.

### Suggested Checks

- `python -m unittest diagramming.tests.test_renderer`
- `scripts/check_water_area.py diagrams/specs/option-c.yaml --view plan`
- `scripts/baseline_render_check.py --fresh-check`
