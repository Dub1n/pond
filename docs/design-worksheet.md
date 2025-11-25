# Design-to-Diagram Worksheet (Start to Finish)

Use this end-to-end worksheet whenever a user gives a high-level design prompt. Follow every stage in order; do not skip or compress steps. Write out every decision and calculation so someone else can retrace the path from the prompt to the final diagrams. The flow mirrors common structural design practice (design brief → design basis → scheme → detailed layout → documentation → QA) and the repository’s spec/planner workflow.

> How to use this document  
>
> 1) Read the whole worksheet first. 2) Work top-to-bottom, overwriting placeholders. 3) Re-read after each section; do not advance with blanks. 4) Only edit YAML after Sections 1–6 are fully filled. 5) Keep this worksheet alongside the YAML until outputs are verified.

---

## 0) Session setup

- Date/time: `<fill>` Engineer/author: `<fill>` Reviewer (if any): `<fill>`
- Prompt received (copy verbatim):  
  `<paste user prompt>`
- Project name/ID (drives file/folder names): `<project-name>`
- Target spec path: `diagrams/specs/<project-name>.yaml`
- Target output root: `diagrams/output/<project-name>/`
- Repo prep (mark completion):  
  - [ ] Virtualenv active (`source .venv/bin/activate`)  
  - [ ] Dependencies installed (`python3 -m pip install -r requirements.txt`)  
  - [ ] Docs read (`README.md`, `instructions.md`, `architecture-spec.md`, `spec-authoring-worksheet.md`, relevant `docs/packs/*`)

---

## 1) Design brief capture (no assumptions yet)

- Site/context notes (water level, ground, access, constraints):  
  `<fill>`
- Required uses and performance (occupancy, imposed load category, durability expectations):  
  `<fill>`
- Deliverables expected (plan, section, glTF, options?):  
  `<fill>`
- Open questions to resolve before sizing (ask/decide now):  
  `<fill>`
- Design life / reliability class / check level (self-check vs independent):  
  `<fill>`

---

## 2) Design basis (state codes, criteria, responsibilities)

- Codes and National Annexes to apply (e.g., EN 1990/1991/1995 UK NA):  
  `<fill>`
- Service class / durability / material grades (timber treatment, fixings class):  
  `<fill>`
- Imposed load category and value (record rationale):  
  `<fill>`
- Dead load sources (decking, joists, beams, membranes, fixings):  
  `<fill>`
- Stability / load path statement (how loads travel to supports; diaphragm/bracing intent):  
  `<fill>`
- Responsibilities (overall stability, checks, approvals):  
  `<fill>`

---

## 3) Geometry & datum decisions

- Units: `mm` (planner default). Origin: top-left; +X east/right; +Y south/down.
- Global datums (Z): water level, finished deck, beam tops, pad tops. List values or expressions:  
  `<fill>`
- Plan footprint targets (write numbers, not “TBD”):  
  - Overall deck width × depth: `<fill>`  
  - Pond/opening width × depth: `<fill>`  
  - Walkway/backspan each side: `<fill>`  
  - Cantilever (inward/outward): `<fill>`  
  - Clearance/gaps (liner, fall, drip edges): `<fill>`
- Roof fall/slope (direction and value) or confirm flat: `<fill>`
- Coordinate frame choice (where `origin` goes, what component is reference):  
  `<fill>`
- Sketch notes / reasoning (describe intended layout before YAML):  
  `<fill>`

---

## 4) Structural scheme and materials

- Primary strategy (beam lines, joist direction, diaphragm/bracing approach):  
  `<fill>`
- Member catalogue (sizes, classes, species, hardware) with reasons:  
  `<fill>`
- Support concept (pads/posts spacing, bearing assumptions, isolation):  
  `<fill>`
- Connections (hanger types, straps, toe-screws, clamps) and why chosen:  
  `<fill>`
- Finishes and interfaces (decking pattern, falls, liner/edge treatments):  
  `<fill>`
- Temporary condition notes (stability during construction):  
  `<fill>`

---

## 5) Loads, combinations, and quick calcs (write out arithmetic)

- Actions:  
  - Permanent (Gk): `<components and values>`  
  - Variable (Qk, category + value): `<fill>`  
  - Additional (wind/impact if relevant): `<fill>`
- Combinations (ULS/SLS coefficients, ψ factors):  
  `<fill>`
- Tributary widths and line loads for joists/beams (show formulas):  
  `<fill>`
- Span/cantilever checks and deflection limits (cite NA/serviceability rules):  
  `<fill>`
- Connection forces/assumptions (uplift, hanger shear, strap tension):  
  `<fill>`
- Support reactions and bearing pressure assumption:  
  `<fill>`

---

## 6) Dimensions and expressions to drive YAML

Use the three-pass approach to stay explicit. Do not proceed until each pass is complete and re-read.

**Pass 1 – Plain-language dimensions** (list every span, offset, height, inset):  
`<fill>` (include overhang symmetry, falls/slopes, and any edges that must stay flush)

**Pass 2 – Dimension names and expressions** (one per line):  
`dimension_name = expression or value`  
`<continue list>`

**Pass 3 – YAML-ready `dimensions` block** (copy-ready snippet):  

```yaml
dimensions:
  <name>: <value or expression>
  <name>: <value or expression>
  # add all from Pass 2
```

---

## 7) Component mapping plan (write before touching YAML)

For each component group, write the intent, anchors/placement, repeats, and views. Use placement helpers (`placement.flush`, `attach_edge`, `inset`, `vertical.flush`) to avoid manual offsets.
Always state which faces should meet (e.g., “outer west face to outer east face”) to avoid floating geometry.

### 7a) Perimeter / outer frame

- Intent & alignment: `<fill>`
- Face alignment (which faces must be flush): `<fill>`
- Placement (ref, flush edge, attach edge, inset): `<fill>`
- Vertical datum: `<fill>`
- Repeat/operations (if mirrored/rotated): `<fill>`
- YAML skeleton to use:  

```yaml
- type: rectangle
  id: <frame_id>
  size: [<width>, <depth>]
  placement:
    flush:
      ref: <ref_component>
      edge: <edge>
    attach_edge: <edge>
    inset:
      <axis>: <expression>
  vertical:
    flush:
      ref: <ref_component>
      face: <face>
    attach_face: <face>
    offset: <expression>
  material: <material_key>
  height: <value>
```

### 7b) Inner beams / headers / trimmers

- Intent & alignment: `<fill>`
- Face alignment: `<fill>`
- Placement/inset/translate: `<fill>`
- Repeat (count/span/direction) or operations: `<fill>`
- Vertical: `<fill>`
- YAML skeleton:  

```yaml
- type: rectangle
  id: <beam_id>
  size: [<width>, <depth>]
  placement:
    flush:
      ref: <ref_component>
      edge: <edge>
    attach_edge: <edge>
    inset:
      <axis>: <expression>
    translate:
      <axis>: <expression>
  repeat:
    count: <number or omit>
    direction: <axis_token>
    span: <expression or omit>
  vertical:
    flush:
      ref: <ref_component>
      face: <face>
    attach_face: <face>
  material: <material_key>
  height: <value>
```

### 7c) Joist zones (each run separately)

- Zone name/intended span: `<fill>`
- Face alignment: `<fill>`
- Placement and inset relative to datum/frame: `<fill>`
- Repeat (count/span/direction/interval): `<fill>`
- Vertical alignment: `<fill>`
- YAML skeleton:  

```yaml
- type: rectangle
  id: <joist_id>
  size: [<span_expression>, <joist_width>]
  placement:
    flush:
      ref: <ref_component>
      edge: <edge>
    attach_edge: <edge>
    inset:
      <axis>: <expression>
  repeat:
    count: <number or omit>
    direction: <axis_token>
    span: <expression>
  material: joist
  height: <value>
  vertical:
    flush:
      ref: <datum_component>
      face: <face>
    attach_face: <face>
```

### 7d) Blocking / straps / accessories

- Purpose and placement: `<fill>`
- Face alignment: `<fill>`
- Views (plan/section): `<fill>`
- Operations (mirror/rotate) if needed: `<fill>`
- YAML cue:  

```yaml
- type: rectangle    # or polyline
  id: <component_id>
  placement:
    # describe flush/offset choices
  views: [plan]      # adjust if also in section
```

### 7e) Supports (pads/posts) and foundations

- Layout logic and spacing: `<fill>`
- Face alignment to supported members: `<fill>`
- Placement and inset relative to beams/joists: `<fill>`
- Vertical datum / embedment: `<fill>`
- Repeat details: `<fill>`
- YAML cue:  

```yaml
- type: rectangle
  id: <support_id>
  size: [<size>, <size>]
  placement:
    flush:
      ref: <ref_component>
      edge: <edge>
    attach_edge: <edge>
    inset:
      <axis>: <expression>
  repeat:
    count: <number>
    direction: <axis_token>
    span: <expression>
  vertical:
    flush:
      ref: <ref_component>
      face: <face>
    attach_face: <face>
  material: timber
  height: <value>
```

### 7f) Finishes & interfaces

- Decking direction/fall/gaps: `<fill>`
- Liner/edge treatment and clamp heights: `<fill>`
- Additional detail polylines or cutouts: `<fill>`

### 7g) Operations & views

- Mirror/rotate targets and anchors: `<fill>`
- Section plane (axis, coordinate, about what): `<fill>`
- Components restricted to specific views: `<fill>`
- Overhang/fall symmetry notes (how edges should finish): `<fill>`

### 7h) Section components

- Which plan components appear in section via slicing: `<fill>`
- Extra section-only rectangles/annotations needed: `<fill>`
- Elevation references reused from dimensions: `<fill>`

---

## 8) YAML editing steps (perform in order)

1. Create or open `diagrams/specs/<project-name>.yaml`. If new, copy a similar spec as a starting point and replace IDs/names.
2. Insert the Pass 3 `dimensions` block from Section 6.
3. Add/revise components per Section 7 plans, keeping anchors/placement helpers consistent. Avoid mixing `placement` with raw `anchor` on the same component.
4. Declare views and section plane (`views.<name>.plane.axis`/`coordinate`) as decided in Section 7g.
5. Add materials/heights/metadata where needed for plan, section, and glTF alignment.
6. Re-read the whole worksheet and YAML to confirm every placeholder is resolved and IDs are unique.

---

## 9) Pre-build QA checklist

- [ ] Dimensions expressions are valid and referenced consistently.
- [ ] Every component has intended `views` coverage (plan/section).
- [ ] Repeats/mirrors/rotations documented and implemented.
- [ ] Vertical datums set via `vertical.flush` where faces must touch.
- [ ] Horizontal face alignment called out (which faces meet which edges).
- [ ] Overhangs/falls expressed and symmetric where intended.
- [ ] Boolean cutouts or subtract lists recorded (if soil/water needs reclaiming).
- [ ] Legend labels present where needed.

---

## 10) Generate outputs (record exact commands)

- Build command(s):  
  `python scripts/build_diagrams.py --spec diagrams/specs/<project-name>.yaml --outdir diagrams/output --force`  
  `python scripts/build_diagrams.py --spec diagrams/specs/<project-name>.yaml --outdir diagrams/output --option <OptionKey> --force --no-gltf`  *(when focusing on 2D only)*
- Baseline freshness check (pair with render):  
  `python scripts/baseline_render_check.py --fresh-check`  *(note result: “baseline render check passed” or record failure)*
- Tests (run after renders):  
  `python -m unittest discover`
- Notes from command output (copy key lines, errors, warnings):  
  `<fill>`

---

## 11) Inspect artefacts (plan and section)

- Output folders to review: `diagrams/output/<project-name>/<Option>/`
- Files to inspect: `plan.svg`, `plan.png`, `section.svg`, `section.png`, `model.glb` (if generated).
- Visual checks (write findings; use `viewimage` only on PNGs, read SVG text directly):  
  - Geometry matches brief and worksheet decisions: `<notes>`  
  - Anchors/flush faces correct (no unintended gaps/overlaps): `<notes>`  
  - Legend entries correct and deduplicated: `<notes>`  
  - Section slice hits intended members; heights/elevations look right: `<notes>`  
  - Materials/colours consistent with palette: `<notes>`  
  - Rasterisation sanity (PNG clarity, no missing fills): `<notes>`
- If visuals differ from intent, go back to the relevant worksheet section, correct it, then update YAML and rerun builds.

---

## 12) Final QA and handoff

- Summary of changes vs prompt (one paragraph):  
  `<fill>`
- Outstanding questions/risks to flag:  
  `<fill>`
- Files touched (list):  
  `<fill>`
- Next steps for reviewers/engineers (e.g., run CLI with options, review glTF in Blender):  
  `<fill>`

---

Keep this worksheet with the project until all placeholders are filled, renders are verified, and tests pass. This ensures the design trail remains auditable and every decision—from codes to anchors to visual QA—is recorded.*** End Patch
