# Design-to-Diagram Worksheet (Start to Finish)

Use this end-to-end worksheet whenever a user gives a high-level design prompt. Follow every stage in order; do not skip or compress steps. Write out every decision and calculation so someone else can retrace the path from the prompt to the final diagrams. The flow mirrors common structural design practice (design brief → design basis → scheme → detailed layout → documentation → QA) and the repository’s spec/planner workflow.

> How to use this document  
>
> 1) Read the whole worksheet first. 2) Work top-to-bottom, overwriting placeholders. 3) Re-read after each section; do not advance with blanks. 4) Only edit YAML after Sections 1–6 are fully filled. 5) Keep this worksheet alongside the YAML until outputs are verified.

---

## 0) Session setup

- Date/time: 2025-11-22 16:05 UTC Engineer/author: Codex Reviewer (if any): None yet
- Prompt received (copy verbatim):  
  a simple one floor rectangular shed with a flat roof and no windows, just a cutout for the door, including the underfloor and roof structure. anything that isn't immediately available in the tool's schema can be ignored or you can simplify the design to meet the tool's abilities. All the information not given here in this description can be assumed based on standards or averages. getting the load detail and engineering-aspects is not so important in this, the final yaml *looking* like a shed with these aspects is the important part
- Project name/ID (drives file/folder names): shed-flat-roof
- Target spec path: `diagrams/specs/shed-flat-roof.yaml`
- Target output root: `diagrams/output/shed-flat-roof/`
- Repo prep (mark completion):  
  - [ ] Virtualenv active (`source .venv/bin/activate`)  
  - [ ] Dependencies installed (`python3 -m pip install -r requirements.txt`)  
  - [ ] Docs read (`README.md`, `instructions.md`, `architecture-spec.md`, `spec-authoring-worksheet.md`, relevant `docs/packs/*`) — instructions.md read; others pending

---

## 1) Design brief capture (no assumptions yet)

- Site/context notes (water level, ground, access, constraints):  
  Small garden plot, assumed level compacted ground with simple concrete pads; dry site with no standing water; access from north.
- Required uses and performance (occupancy, imposed load category, durability expectations):  
  Light domestic storage/workbench use; floor to suit Category A light-duty 1.5 kN/m²; roof non-trafficable except maintenance; expected 15–20 year life with treated timber.
- Deliverables expected (plan, section, glTF, options?):  
  Plan, section, and glTF for a single Option A.
- Open questions to resolve before sizing (ask/decide now):  
  Door swing direction and cladding type; anchorage to pads versus floating; guttering details (omit for now).
- Design life / reliability class / check level (self-check vs independent):  
  Domestic reliability; self-check only for visual correctness of the YAML-driven geometry.

---

## 2) Design basis (state codes, criteria, responsibilities)

- Codes and National Annexes to apply (e.g., EN 1990/1991/1995 UK NA):  
  Use EN 1990/1991/1995 principles as a sanity baseline; simplified for geometry only.
- Service class / durability / material grades (timber treatment, fixings class):  
  Service class 2; C24 treated softwood for floor/roof; C16/C24 for studs; galvanized or stainless fixings (class 3–4).
- Imposed load category and value (record rationale):  
  Floor: Category A 1.5 kN/m² (light storage/occupancy). Roof: snow 0.75 kN/m², maintenance allowance only.
- Dead load sources (decking, joists, beams, membranes, fixings):  
  Floor OSB ≈0.11 kN/m²; floor joists/rims ≈0.25 kN/m²; wall cladding + studs ≈0.35 kN/m²; roof deck + membrane ≈0.20 kN/m²; fasteners misc ≈0.05 kN/m².
- Stability / load path statement (how loads travel to supports; diaphragm/bracing intent):  
  Roof deck acts as flat diaphragm to top plates; walls transfer to rim/floor diaphragm; floor joists bear to perimeter rim and pads; no lateral bracing modeled beyond rectangles—visual only.
- Responsibilities (overall stability, checks, approvals):  
  Geometry/layout only; structural verification out of scope; author responsible for matching visual intent to prompt.

---

## 3) Geometry & datum decisions

- Units: `mm` (planner default). Origin: top-left; +X east/right; +Y south/down.
- Global datums (Z): water level, finished deck, beam tops, pad tops. List values or expressions:  
  Pad top and ground datum = 0; underside of floor joists = 0; top of floor joists = floor_joist_depth; finished floor (FFL) = floor_joist_depth + floor_sheet_thickness; wall top plate = FFL + wall_height; roof deck top = wall_top + roof_joist_depth + roof_deck_thickness; roof falls 20 mm north→south.
- Plan footprint targets (write numbers, not “TBD”):  
  - Overall deck width × depth: 3000 × 2400 (shed footprint)  
  - Pond/opening width × depth: Door opening 900 × 2100 in north wall; no internal opening  
  - Walkway/backspan each side: 0 (single-shell shed)  
  - Cantilever (inward/outward): Roof overhang 150 all around; no floor cantilever  
  - Clearance/gaps (liner, fall, drip edges): 25 mm roof drip beyond wall line; nominal 10 mm door clearance at jambs/sill
- Coordinate frame choice (where `origin` goes, what component is reference):  
  Origin at outer north-west corner of floor rim; all other components flush or inset from that frame.
- Sketch notes / reasoning (describe intended layout before YAML):  
  Rectangular platform floor on pads, walls centered on rim, door centered in north wall, flat roof with slight fall to south, roof joists aligned with floor joists for clean stacking.

---

## 4) Structural scheme and materials

- Primary strategy (beam lines, joist direction, diaphragm/bracing approach):  
  Platform floor with perimeter rim; floor joists running north–south spanning 2.4 m; walls platform-framed on the floor; roof joists also north–south with 20 mm fall; roof deck as diaphragm; minimal bracing modeled for visual clarity.
- Member catalogue (sizes, classes, species, hardware) with reasons:  
  Floor joists/rim: 45×145 C24 treated. Floor sheathing: 18 mm OSB3. Wall studs/plates: 45×95 C16/C24 @ 600 mm c/c. Door header: double 45×145 over opening. Roof joists: 45×145 @ 400 mm c/c. Roof deck: 18 mm OSB3 + assumed membrane. Overhang blocks at eaves in same section size.
- Support concept (pads/posts spacing, bearing assumptions, isolation):  
  9 concrete pads (300×300×100) in 3×3 grid at corners/midpoints (1500 mm in X, 1200 mm in Y); rim bears directly; DPC under rim; floating shed, no anchors modeled.
- Connections (hanger types, straps, toe-screws, clamps) and why chosen:  
  Joists face-fix or hanger to rim; double-screw plates; door header strapped to studs; roof deck screwed to joists; metal angle brackets optional at pad locations—not drawn.
- Finishes and interfaces (decking pattern, falls, liner/edge treatments):  
  Floor OSB laid with short edges on joists; roof membrane over OSB with 1:120 fall to south; simple drip edge at overhang; no gutters modeled.
- Temporary condition notes (stability during construction):  
  Ensure rim braced before joist install; shore door opening until header fixed; roof fall achieved with tapered packers if joists left level.

---

## 5) Loads, combinations, and quick calcs (write out arithmetic)

- Actions:  
  - Permanent (Gk): floor build-up ≈0.25 kN/m²; walls ≈0.35 kN/m² distributed to rim; roof ≈0.20 kN/m².  
  - Variable (Qk, category + value): Floor Cat A 1.5 kN/m²; roof snow 0.75 kN/m²; maintenance 0.25 kN/m² (not combined with snow).  
  - Additional (wind/impact if relevant): Wind uplift not modeled; ignore seismic.
- Combinations (ULS/SLS coefficients, ψ factors):  
  ULS: 1.35G + 1.5Q. SLS: G + Q (ψ0 for roof snow 0.5). Visual intent only—no detailed check.
- Tributary widths and line loads for joists/beams (show formulas):  
  Floor joist tributary width = 0.4 m; line load = (0.25 + 1.5) × 0.4 ≈ 0.7 kN/m. Roof joist tributary width = 0.4 m; line load snow combo = (0.20 + 0.75) × 0.4 ≈ 0.38 kN/m.
- Span/cantilever checks and deflection limits (cite NA/serviceability rules):  
  Floor joist span 2.4 m; 45×145 is acceptable for light storage with L/300 deflection target → allowable ≈8 mm; anticipated midspan under 1 kN/m ≈7–8 mm (within tolerance). Roof joist span 2.4 m; L/200 roof deflection target ≈12 mm, met with assumed section.
- Connection forces/assumptions (uplift, hanger shear, strap tension):  
  Joist hanger shear ≈ line load × span / 2 ≈ 0.7 × 2.4 / 2 ≈ 0.84 kN per end; header over door takes ~0.7 kN/m × 0.9 m ≈ 0.63 kN distributed to studs; uplift ignored for visuals.
- Support reactions and bearing pressure assumption:  
  Pad reaction ≈ total shed load (~5 kN dead + 10 kN live) / 9 ≈ 1.7 kN per pad; bearing stress on 0.09 m² pad ≈ 19 kPa (fine for compacted soil).

---

## 6) Dimensions and expressions to drive YAML

Use the three-pass approach to stay explicit. Do not proceed until each pass is complete and re-read.

**Pass 1 – Plain-language dimensions** (list every span, offset, height, inset):  
Overall shed footprint 3000 × 2400. Roof overhang 150 all sides. Door centered on north wall: 900 wide, 2100 high, 1050 inset from west edge to rough opening start. Floor joists 45×145 at 400 c/c running north–south. Rim same depth/width. Floor deck 18 thick. Pad grid 3×3 at 300 size, spaced 1500 in X, 1200 in Y. Wall studs 45×95 at 600 c/c; wall height 2200 to top plate. Door header double 45×145. Roof joists 45×145 at 400 c/c running north–south with 20 mm fall to south; roof deck 18 thick. Roof eave drop 25 mm drip beyond walls.

**Pass 2 – Dimension names and expressions** (one per line):  
shed_width = 3000  
shed_depth = 2400  
roof_overhang = 150  
door_width = 900  
door_height = 2100  
door_inset_from_west = (shed_width - door_width) / 2  
floor_joist_width = 45  
floor_joist_depth = 145  
floor_joist_spacing = 400  
rim_width = 45  
rim_depth = 145  
floor_sheet_thickness = 18  
pad_size = 300  
pad_height = 100  
pad_spacing_x = 1500  
pad_spacing_y = 1200  
wall_stud_width = 45  
wall_stud_depth = 95  
wall_stud_spacing = 600  
wall_height = 2200  
header_depth = 145  
header_width = 45  
roof_joist_width = 45  
roof_joist_depth = 145  
roof_joist_spacing = 400  
roof_deck_thickness = 18  
roof_fall = 20  
ffl = floor_joist_depth + floor_sheet_thickness  
wall_top = ffl + wall_height  
roof_top = wall_top + roof_joist_depth + roof_deck_thickness  
roof_low_edge_drop = roof_fall

**Pass 3 – YAML-ready `dimensions` block** (copy-ready snippet):  

```yaml
dimensions:
  shed_width: 3000
  shed_depth: 2400
  roof_overhang: 150
  door_width: 900
  door_height: 2100
  door_inset_from_west: (shed_width - door_width) / 2
  floor_joist_width: 45
  floor_joist_depth: 145
  floor_joist_spacing: 400
  rim_width: 45
  rim_depth: 145
  floor_sheet_thickness: 18
  pad_size: 300
  pad_height: 100
  pad_spacing_x: 1500
  pad_spacing_y: 1200
  wall_stud_width: 45
  wall_stud_depth: 95
  wall_stud_spacing: 600
  wall_height: 2200
  header_depth: 145
  header_width: 45
  roof_joist_width: 45
  roof_joist_depth: 145
  roof_joist_spacing: 400
  roof_deck_thickness: 18
  roof_fall: 20
  ffl: floor_joist_depth + floor_sheet_thickness
  wall_top: ffl + wall_height
  roof_top: wall_top + roof_joist_depth + roof_deck_thickness
  roof_low_edge_drop: roof_fall
```

---

## 7) Component mapping plan (write before touching YAML)

For each component group, write the intent, anchors/placement, repeats, and views. Use placement helpers (`placement.flush`, `attach_edge`, `inset`, `vertical.flush`) to avoid manual offsets.

### 7a) Perimeter / outer frame

- Intent & alignment: Floor rim rectangle framing the full footprint; walls sit flush on rim; roof overhang built from roof joist length and eaves inset.
- Placement (ref, flush edge, attach edge, inset): Set rim origin at [0, 0]; roof perimeter derives from rim with inset = -roof_overhang.
- Vertical datum: Rim flush to pad tops at z=0; walls start at FFL; roof sits on wall top with fall via vertical offset at south edge.
- Repeat/operations (if mirrored/rotated): None needed; single rectangle per layer.
- YAML skeleton to use:  

```yaml
- type: rectangle
  id: floor_rim
  size: [shed_width, shed_depth]
  origin: [0, 0]
  material: timber
  height: rim_depth
  vertical:
    flush:
      ref: grade
      face: top
    attach_face: bottom
```

### 7b) Inner beams / headers / trimmers

- Intent & alignment: Door header above opening; optional mid-plate blocking at roof edge if needed; rim doubler along door wall.
- Placement/inset/translate: Door header flush to wall inner face with inset to door jambs; translate vertically to door height.
- Repeat (count/span/direction) or operations: None beyond single header and rim doubler; could mirror blocking if added.
- Vertical: Header top flush with wall_top.
- YAML skeleton:  

```yaml
- type: rectangle
  id: door_header
  size: [door_width, header_depth]
  placement:
    flush:
      ref: wall_north
      edge: west
    inset:
      east: door_inset_from_west
  vertical:
    flush:
      ref: floor_plane
      face: top
    attach_face: bottom
    offset: door_height
  material: timber
  height: header_width
```

### 7c) Joist zones (each run separately)

- Zone name/intended span: Floor joists spanning north–south across shed_depth; roof joists same orientation with overhang.
- Placement and inset relative to datum/frame: First floor joist flush to west rim; repeat eastward across shed_width minus joist width; roof joists start at west overhang edge with inset = roof_overhang.
- Repeat (count/span/direction/interval): `repeat: { interval: floor_joist_spacing, direction: east, span: shed_width - floor_joist_width }` for floor; similar for roof.
- Vertical alignment: Floor joists top at floor_joist_depth; roof joists top at roof_top minus roof_deck_thickness, south edge dropped by roof_fall via vertical offset or wedge plane.
- YAML skeleton:  

```yaml
- type: rectangle
  id: floor_joist_run
  size: [shed_depth, floor_joist_width]
  placement:
    flush:
      ref: floor_rim
      edge: west
  repeat:
    interval: floor_joist_spacing
    direction: east
    span: shed_width - floor_joist_width
  material: joist
  height: floor_joist_depth
  vertical:
    flush:
      ref: floor_rim
      face: top
    attach_face: bottom
```

### 7d) Blocking / straps / accessories

- Purpose and placement: Rim doubler at door; blocking at roof eaves for overhang support; optional floor blocking at midspan for diaphragm look.
- Views (plan/section): Plan and section for rim/roof blocking; omit small hardware.
- Operations (mirror/rotate) if needed: Mirror roof blocking east/west; reuse repeat for eave blocks along north/south edges.
- YAML cue:  

```yaml
- type: rectangle
  id: roof_eave_block
  placement:
    flush:
      ref: roof_edge_south
      edge: south
    inset:
      west: roof_overhang
  views: [plan, section]
```

### 7e) Supports (pads/posts) and foundations

- Layout logic and spacing: 3×3 pad grid; first at origin corner; repeats span pad_spacing_x and pad_spacing_y.
- Placement and inset relative to beams/joists: Pads flush to rim corners; mid pads inset by pad_spacing_x/pad_spacing_y.
- Vertical datum / embedment: Pads sit at grade datum; rim flushes to pad top.
- Repeat details: `repeat` east with span shed_width; `repeat` south with span shed_depth.
- YAML cue:  

```yaml
- type: rectangle
  id: pad_base
  size: [pad_size, pad_size]
  origin: [0, 0]
  repeat:
    count: 3
    direction: east
    span: shed_width - pad_size
  operations:
    - type: repeat
      count: 3
      direction: south
      span: shed_depth - pad_size
  material: timber
  height: pad_height
  vertical:
    flush:
      ref: grade
      face: top
    attach_face: top
```

### 7f) Finishes & interfaces

- Decking direction/fall/gaps: Floor OSB laid east–west with joints on joists; no gaps modeled. Roof membrane over OSB; fall to south; drip edge at overhang.
- Liner/edge treatment and clamp heights: Not applicable; treat drip as visual offset only.
- Additional detail polylines or cutouts: Door cutout in wall plane; no windows.

### 7g) Operations & views

- Mirror/rotate targets and anchors: Could mirror wall panels east/west if authored once; roof blocking mirrored about center.
- Section plane (axis, coordinate, about what): Section along X at mid-depth (axis: y, coordinate: shed_depth / 2) to show door wall and roof build-up.
- Components restricted to specific views: Hardware hidden; pads in section; membrane shown in plan/section.

### 7h) Section components

- Which plan components appear in section via slicing: Pads, rim, joists, floor deck, walls, roof joists/deck all sliced automatically via heights.
- Extra section-only rectangles/annotations needed: Door opening polygon in wall for clarity; optional grade line.
- Elevation references reused from dimensions: Use ffl, wall_top, roof_top, roof_low_edge_drop for vertical anchoring.

---

## 8) YAML editing steps (perform in order)

1. Create `diagrams/specs/shed-flat-roof.yaml` by copying a minimal deck option and renaming IDs to shed_* equivalents.
2. Insert the Pass 3 `dimensions` block from Section 6.
3. Add floor rim, pads, floor joists, floor deck, wall planes, door opening cutout, roof joists, roof deck/overhang using placement helpers; avoid mixing placement with raw anchors.
4. Declare views and section plane (`views.section.plane.axis: y`, `coordinate: shed_depth / 2`) to slice through the door and show roof build-up.
5. Add materials/heights/metadata for plan/section/glTF alignment; ensure roof fall via vertical offsets on south edge components.
6. Re-read worksheet and YAML to confirm every placeholder resolved and IDs remain unique.

---

## 9) Pre-build QA checklist

- [ ] Dimensions expressions are valid and referenced consistently.
- [ ] Every component has intended `views` coverage (plan/section).
- [ ] Repeats/mirrors/rotations documented and implemented.
- [ ] Vertical datums set via `vertical.flush` where faces must touch.
- [ ] Boolean cutouts or subtract lists recorded (door opening and pad subtraction if used).
- [ ] Legend labels present where needed.

---

## 10) Generate outputs (record exact commands)

- Build command(s):  
  `python scripts/build_diagrams.py --spec diagrams/specs/shed-flat-roof.yaml --outdir diagrams/output --force`  
  `python scripts/build_diagrams.py --spec diagrams/specs/shed-flat-roof.yaml --outdir diagrams/output --option A --force --no-gltf` *(if focusing on 2D only)*
- Baseline freshness check (pair with render):  
  `python scripts/baseline_render_check.py --fresh-check` *(note result: baseline render check pending; rerun with spec once authored)*
- Tests (run after renders):  
  `python -m unittest discover`
- Notes from command output (copy key lines, errors, warnings):  
  Not run yet.

---

## 11) Inspect artefacts (plan and section)

- Output folders to review: `diagrams/output/shed-flat-roof/OptionA/`
- Files to inspect: `plan.svg`, `plan.png`, `section.svg`, `section.png`, `model.glb` (if generated).
- Visual checks (write findings; use `viewimage` only on PNGs, read SVG text directly):  
  - Geometry matches brief and worksheet decisions: Pending build.  
  - Anchors/flush faces correct (no unintended gaps/overlaps): Pending build.  
  - Legend entries correct and deduplicated: Pending build.  
  - Section slice hits intended members; heights/elevations look right: Pending build.  
  - Materials/colours consistent with palette: Pending build.  
  - Rasterisation sanity (PNG clarity, no missing fills): Pending build.
- If visuals differ from intent, go back to the relevant worksheet section, correct it, then update YAML and rerun builds.

---

## 12) Final QA and handoff

- Summary of changes vs prompt (one paragraph):  
  Captured a simple rectangular, single-storey, flat-roof shed with centered door cutout, underfloor pad support, platform floor, wall planes, and roof joists/deck with slight fall; established dimensions, load assumptions, and component mapping ready for YAML authoring under a new shed-flat-roof spec.
- Outstanding questions/risks to flag:  
  Door swing/cladding not set; roof drainage/gutter omitted; no uplift/bracing modeled beyond visual rectangles.
- Files touched (list):  
  docs/designs/design-shed.md
- Next steps for reviewers/engineers (e.g., run CLI with options, review glTF in Blender):  
  Populate diagrams/specs/shed-flat-roof.yaml per plan, run build command with baseline render check, review plan/section PNGs, and iterate if geometry deviates from intent.

---

Keep this worksheet with the project until all placeholders are filled, renders are verified, and tests pass. This ensures the design trail remains auditable and every decision—from codes to anchors to visual QA—is recorded.
