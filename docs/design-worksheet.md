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

For each component group, write the intent, axis-map relates, arrays (`array`, legacy `run_between`), operations, and views. State which faces/points must coincide (e.g., “-x+y to deck corner”) to avoid floating geometry. Frames are honoured during placement.

### 7a) Reference frames/planes

- Intent & alignment: `<fill>`
- Which datums they tie to: `<fill>`
- YAML skeleton:  

```yaml
- id: <ref_id>
  kind: reference
  size: [<x>, <y>, <z>]   # axes you care about; missing defaults to 0
  relate:
    cxcy: { ref: origin } # example center tie; use axis-map keys as needed
```

### 7b) Solids (beams/joists/slabs/pads)

- Intent & alignment: `<fill>`
- Face/edge/point alignment (subject/target pairs): `<fill>`
- Vertical datum (z faces): `<fill>`
- Arrays (if any): `<fill>`
- Operations (rotate/mirror/translate/boolean): `<fill>`
- YAML skeleton:  

```yaml
- id: <component_id>
  class: <IfcEntity>
  size: [<x>, <y>, <z>]
  material: <material_key>
  relate:
    +x-y: { ref: <target>, pos: +x-y, gap: <expr_optional>, offset: <expr_optional> }
    +z:   { ref: <target>, pos: +z }
    -z:   { ref: <target>, pos: +z }
  array:   # rename from run_between; optional
    start:
      +y: { ref: <target>, pos: +y }
    end:
      -y: { ref: <target>, pos: -y }
    count: <n>           # enforce >=2; otherwise use relate only
    include_seed: true
    orient: along_run
  place:   # optional named placements (inline axis-map)
    - id: <placement_id>
      +x: { ref: <target>, pos: -x }
      +y: { ref: <target>, pos: +y }
  voids: [<ids>]        # openings/void refs
  ifc:
    predefined_type: <TYPE>
```

### 7c) Operations

- Targets/selector plan: `<fill>`
- Rotations/mirrors/translates/booleans: `<fill>`
- YAML skeleton:  

```yaml
operations:
  - type: rotate
    targets: [<ids or selectors>]
    about: { ref: <target>, axis: +z }
    count: 4
    include_seed: true
    id_map:
      <seed_id>: [<rot0>, <rot1>, <rot2>, <rot3>]
  - type: boolean
    target: <host_id>
    subtract: [<void_ids>]
  # mirror planned but not implemented yet
```

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
