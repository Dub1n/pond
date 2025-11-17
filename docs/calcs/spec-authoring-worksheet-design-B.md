# Spec Authoring Worksheet – Option B

Use this worksheet every time you translate a design brief into a diagram spec. Treat it as a living scratch pad: overwrite the placeholders on each pass instead of adding new paragraphs, and keep it in sync with the working design. Follow the loop below strictly:

1. **Read this entire worksheet** before making any edits so the structure is fresh.  
2. **Initial fill:** complete Pass 1, then re-read the whole worksheet.  
3. **Subsequent passes:** for Pass 2 and Pass 3, always read that section before editing, overwrite the placeholders, then re-read the entire worksheet after each pass.  
4. Only once all three sections are complete should you touch `diagrams/specs/*.yaml`. If the rendered output looks wrong, come back here and correct the mismatch before editing code again.

---

## Global dimensions & datums

**Pass 1 – Design notes**  
3.0 m × 3.0 m pond; design calls for a 1.0 m walk-around plus a 0.5 m joist cantilever toward the pond. Maintain the framed opening geometry and keep the deck square so each side reads the same in plan. Headers sit 500 mm back from the cantilever edge and lap 500 mm past each pond corner so adjacent runs can share posts. Deck finish ≈100 mm above water, joist depth 150 mm, deck boards 28 mm.

**Pass 2 – Schema mapping**  
`pond_span = 3000`  
`walkway_backspan = 1000`  
`cantilever = 500`  
`walkway_total = walkway_backspan + cantilever`  
`deck_span = pond_span + 2 * walkway_backspan`  
`header_overlap = 500`  
`header_span = pond_span + 2 * header_overlap`  
`header_offset = 500`  
`beam_width = 180`  
`beam_height = 200`  
`trimmer_width = 180`  
`joist_width = 140`  
`joist_depth = 150`  
`joist_spacing = 400`  
`rim_block_width = 140`  
`rim_board_width = 145`  
`strap_band_width = 80`  
`post_size = 160`  
`pad_size = 300`  
`pad_height = 100`  
`deck_thickness = 28`  
`joist_elevation = 0`  
`deck_elevation = joist_elevation + joist_depth`  
`water_depth = 900`  
`soil_depth = water_depth`

**Pass 3 – YAML skeleton**  

```yaml
dimensions:
  pond_span: 3000
  walkway_backspan: 1000
  cantilever: 500
  walkway_total: walkway_backspan + cantilever
  deck_span: pond_span + 2 * walkway_backspan
  header_overlap: 500
  header_span: pond_span + 2 * header_overlap
  header_offset: 500
  beam_width: 180
  beam_height: 200
  trimmer_width: 180
  joist_width: 140
  joist_depth: 150
  joist_spacing: 400
  rim_block_width: 140
  rim_board_width: 145
  strap_band_width: 80
  post_size: 160
  pad_size: 300
  pad_height: 100
  deck_thickness: 28
  joist_elevation: 0
  deck_elevation: joist_elevation + joist_depth
  water_depth: 900
  soil_depth: water_depth
```

Re-read the entire worksheet before moving on.

---

## Primary structural members

### Outer/perimeter beams

- **Pass 1 – Design notes**  
  Double 47×200 outer beam runs the full perimeter, bearing on pads/ground screws at 1.5 m centres. Tops flush with joists, shimmed to sit 20–30 mm proud of posts so hangers seat fully. Walkway joists connect via face-mount hangers.
- **Pass 2 – Schema mapping**  
  `<placement.flush ref=deck_backspan edge=north attach_edge=north>`  
  `<size = [deck_span, beam_width]>`  
  `<vertical.flush ref=pond_water face=top attach_face=bottom offset=joist_elevation - beam_height>`  
  `<repeat via rotate operation>`
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: beam_north
    size: [deck_span, beam_width]
    placement:
      flush:
        ref: deck_walkway
        edge: north
      attach_edge: north
    class: component-structure
    label: "Perimeter beam (double 47×200)"
    label_id: "B1"
    height: beam_height
    material: timber
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: bottom
      offset: joist_elevation - beam_height
  ```

Re-read the entire worksheet.

### Inner beams / headers / trimmers

- **Pass 1 – Design notes**  
  Side trimmers are double 47×200s tight to the pond edge on all four sides. Headers (also double 47×200) sit 500 mm back from the cantilever edge (i.e., 1.0 m in from the outer rim) and run 4.0 m so each end laps 500 mm past pond corners, sharing the corner posts. Hangers or bolted bearing tie headers to trimmers; overlapping runs keep the top arrises flush.
- **Pass 2 – Schema mapping**  
  `<trimmer placement.flush ref=pond_water edge=north attach_edge=south>`  
  `<trimmer repeat via rotate>`  
  `<header placement.flush ref=deck_walkway edge=north attach_edge=south inset.east=header_overlap inset.west=header_overlap>`  
  `<header translate.south = header_offset - beam_width>`  
  `<header vertical.flush ref=pond_water face=top attach_face=bottom offset=joist_elevation - beam_height>`
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: trimmer_north
    size: [header_span, trimmer_width]
    placement:
      flush:
        ref: deck_walkway
        edge: north
      attach_edge: south
      inset:
        east: header_overlap
        west: header_overlap
      translate:
        south: walkway_backspan
    class: component-structure
    label: "Side trimmer (double 47×200)"
    label_id: "B2"
    height: beam_height
    material: timber
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: bottom

  - type: rectangle
    id: header_north
    size: [header_span, trimmer_width]
    placement:
      flush:
        ref: deck_walkway
        edge: north
      attach_edge: south
      inset:
        east: header_overlap
        west: header_overlap
      translate:
        south: header_offset
    class: component-structure
    label: "Header (double 47×200 with 0.5 m lap)"
    label_id: "B3"
    height: beam_height
    material: timber
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: bottom
  ```

Re-read the entire worksheet.

---

## Joist and slab layout

### Joist zones (describe each run separately)

For each zone (cantilever band, shoulders, walkway core):

- **Pass 1 – Design notes**  
  Continuous 47×150 joists at 400 mm centres run perpendicular to each pond face. Joists bear on face-mount hangers at the perimeter beam, cross the walkway span, seat on the header through the core, and cantilever 500 mm to the picture-frame rim. Shoulder bays at the corners instead terminate on the trimmers; the same joist run covers all zones without breaks.
- **Pass 2 – Schema mapping**  
  `<placement.flush ref=trimmer_north edge=north attach_edge=south>`  
  `<translate.south = cantilever>`  
  `<repeat direction=east span=pond_span + 2 * walkway_backspan interval=joist_spacing include_base=true>`  
  `<vertical.flush ref=pond_water face=top attach_face=bottom offset=joist_elevation>`
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: joist_run_north
    size: [joist_width, walkway_total]
    placement:
      flush:
        ref: trimmer_north
        edge: north
      attach_edge: south
      translate:
        south: cantilever
    repeat:
      interval: joist_spacing
      direction: east
      span: pond_span + 2 * walkway_backspan
      include_base: true
    class: component-structure
    label: "47×150 joist @ 400 centres (1 m backspan + 0.5 m cantilever)"
    label_id: "J1"
    height: joist_depth
    material: joist
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: bottom
  ```

Re-read the entire worksheet.

### Blocking / straps / accessories

- **Pass 1 – Design notes**  
  Install solid blocking at the cantilever edge and inside shoulder bays to prevent roll; add picture-frame rim blocking tied into joists. LSTA-type straps wrap over each cantilevered joist at the rim and bolt/seat hardware secures the header line.
- **Pass 2 – Schema mapping**  
  `<rim_block placement.flush ref=trimmer_north edge=north attach_edge=north translate.south=cantilever - rim_block_width>`  
  `<strap placement.flush ref=joist_run_north edge=north attach_edge=north views=[plan]>`  
  `<blocking repeat matches joist repeat>`  
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: rim_block_north
    size: [pond_span + 2 * header_overlap, rim_block_width]
    placement:
      flush:
        ref: header_north
        edge: north
      attach_edge: south
      translate:
        south: cantilever - rim_block_width
    class: component-structure
    label: "Rim blocking at cantilever edge"
    label_id: "RB1"
    height: joist_depth
    material: joist
    views: [plan]

  - type: rectangle
    id: cantilever_strap_north
    size: [joist_width, strap_band_width]
    placement:
      flush:
        ref: joist_run_north
        edge: north
      attach_edge: north
    repeat:
      interval: joist_spacing
      direction: east
      span: pond_span + 2 * walkway_backspan
      include_base: true
    class: component-detail
    label: "LSTA strap over cantilever"
    label_id: "ST1"
    views: [plan]
  ```

Re-read the entire worksheet.

---

## Supports

### Perimeter posts / pads

- **Pass 1 – Design notes**  
  Pads or ground screws at 1.5 m centres under the perimeter beam; share corner posts between adjacent sides. Pads 300×300×100 mm with DPC/EPDM isolation; posts sized 160×160 bearing to grade.
- **Pass 2 – Schema mapping**  
  `<pad placement.flush ref=beam_north edge=south attach_edge=center inset.west=post_size/2>`  
  `<repeat interval=1500 direction=east span=deck_span - 2 * post_edge_clearance>`  
  `<vertical.flush ref=pond_water face=top attach_face=top offset=-pad_height>`  
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: pad_run_north
    size: [pad_size, pad_size]
    placement:
      flush:
        ref: beam_north
        edge: south
      attach_edge: center
      inset:
        west: post_size / 2
    repeat:
      interval: 1500
      direction: east
      span: deck_span - 2 * post_size
    class: component-structure
    label: "300×300 pads @ 1.5 m centres"
    label_id: "PD1"
    height: pad_height
    material: pad
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: top
      offset: -pad_height
  ```

Re-read the entire worksheet.

### Header posts / hangers / seats

- **Pass 1:** Corner posts pick up both the header lap and the adjacent trimmer; mid-bay posts align beneath the header to keep spans under 2.0 m. Use joist hangers or bolted bearing plates at the header–joist interface and angle seats beneath the joists where they transition to cantilever.  
- **Pass 2:** `<post placement.flush ref=header_north edge=south attach_edge=center inset.west=header_overlap>` `<repeat count=3 direction=east span=header_span - 2 * header_overlap include_base=true>` `<vertical.flush ref=pond_water face=top attach_face=bottom offset=-pad_height>`  
- **Pass 3 YAML:**  

  ```yaml
  - type: rectangle
    id: header_post_north
    size: [post_size, post_size]
    placement:
      flush:
        ref: header_north
        edge: south
      attach_edge: center
      inset:
        west: header_overlap
    repeat:
      count: 3
      direction: east
      span: header_span - 2 * header_overlap
      include_base: true
    class: component-structure
    label: "Header support post"
    label_id: "HP1"
    height: deck_elevation + pad_height
    material: timber
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: bottom
      offset: -pad_height
  ```

Re-read the entire worksheet.

---

## Finishes & interfaces

- **Pass 1:** Deck boards run perpendicular to joists with 20–30 mm overhang and 1–2% fall away from the pond. Picture-frame rim and fascia conceal the liner clamp; liner batten (45×45) fixed ≥75 mm above water with stainless screws at 150–200 mm centres, liner backed by foam/underlay.  
- **Pass 2:** Map `deck_walkway`, `deck_cantilever`, and `liner_clamp` polylines; ensure fascia appears in plan only.  
- **Pass 3 YAML:**  

  ```yaml
  - type: rectangle
    id: deck_walkway
    size: [deck_span, deck_span]
    origin: [0, 0]
    class: component-structure
    label: "Deck walkway (1.0 m backspan)"
    label_id: "DK1"
    height: deck_thickness
    material: decking
    metadata:
      elevation: deck_elevation
    cutouts:
      - size: [pond_span, pond_span]
        anchor:
          ref: self
          align: center

  - type: rectangle
    id: deck_cantilever
    size: [pond_span, pond_span]
    anchor:
      ref: pond_water
      align: center
      anchor_point: center
    class: component-structure
    label: "Cantilevered deck (0.5 m overhang)"
    label_id: "DK2"
    height: deck_thickness
    material: decking
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: bottom
      offset: joist_depth
    cutouts:
      - size: [pond_span - 2 * cantilever, pond_span - 2 * cantilever]
        anchor:
          ref: self
          align: center

  - type: rectangle
    id: rim_board
    size: [pond_span - 2 * cantilever + 2 * rim_board_width, pond_span - 2 * cantilever + 2 * rim_board_width]
    anchor:
      ref: pond_water
      align: center
      anchor_point: center
    class: component-detail
    label: "Picture-frame rim board"
    label_id: "RB2"
    height: deck_thickness
    material: decking
    views: [plan]
    cutouts:
      - size: [pond_span - 2 * cantilever, pond_span - 2 * cantilever]
        anchor:
          ref: self
          align: center

  - type: polyline
    id: liner_clamp
    points:
      - [0, 0]
      - [pond_span, 0]
      - [pond_span, pond_span]
      - [0, pond_span]
      - [0, 0]
    anchor:
      ref: pond_water
      align: north_west
      anchor_point: north_west
    class: component-detail
    label: "Liner clamp batten"
    label_id: "LC1"
    views: [plan]
  ```

Re-read the entire worksheet.

---

## Operations & views

- **Pass 1:** Author one quadrant (north side) then rotate three copies about the pond centre; keep base included so original geometry remains. No mirrors required because rotation covers all sides. Section plane slices through the walkway mid-span to show joist, header, trimmer, and cantilever stack.  
- **Pass 2:** `operations.rotate targets=[...] angle=90 count=4 include_base=true about.ref=pond_water about.align=center`; section plane `axis: y`, `coordinate: deck_span / 2`.  
- **Pass 3 YAML:**  

  ```yaml
  views:
    plan:
      title: "Option B plan — 1 m walk with 0.5 m overhang"
      aria_label: "Plan view of Option B showing the 1 m walk-around, 0.5 m cantilever, and header laps."
      scale: 0.18
      background: "#ffffff"
    section:
      title: "Option B section — continuous joists with header backspan and 0.5 m cantilever"
      aria_label: "Section view of Option B highlighting joist continuity from perimeter beam to header and cantilever strap."
      scale: 0.18
      background: "#ffffff"
      plane:
        axis: y
        coordinate: deck_span / 2

  operations:
    - type: rotate
      targets:
        - beam_north
        - trimmer_north
        - header_north
        - joist_run_north
        - rim_block_north
        - cantilever_strap_north
        - pad_run_north
        - header_post_north
      count: 4
      angle: 90
      include_base: true
      about:
        ref: pond_water
        align: center
  ```

Re-read the entire worksheet.

---

## Section components

- **Pass 1:** Section should cut across a joist mid-bay showing outer beam, joist backspan, header, cantilever rim, strap, decking, pad/post stack, and pond water depth. Soil fill trimmed around pads.  
- **Pass 2:** Use `deck_span / 2` for plane location, reference `joist_depth`, `deck_thickness`, `pad_height`, and `water_depth` for vertical extents.  
- **Pass 3 YAML:**  

  ```yaml
  - type: rectangle
    id: soil_fill
    size: [deck_span, deck_span]
    origin: [0, 0]
    class: component-structure
    label: "Soil infill beneath deck"
    label_id: "SO1"
    views: [section]
    height: soil_depth
    material: soil
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: top
    boolean:
      subtract:
        - target: pad_run_north
          include_generated: true
    cutouts:
      - size: [pond_span, pond_span]
        anchor:
          ref: self
          align: center

  - type: rectangle
    id: water_plane_section
    size: [pond_span, deck_span]
    anchor:
      ref: pond_water
      align: center
      anchor_point: center
    class: component-water
    label: "Pond water (section slice)"
    label_id: "WS1"
    views: [section]
    height: water_depth
    material: water
    vertical:
      flush:
        ref: pond_water
        face: top
      attach_face: top
      offset: -water_depth
  ```

Re-read the entire worksheet once more, confirm every placeholder is overwritten, then proceed to implement the YAML edits. After generating outputs and tests, compare the visuals back to the design doc; if discrepancies appear, return to the relevant section above to correct the logic before touching the spec again.
