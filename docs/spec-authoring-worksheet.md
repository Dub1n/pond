# Spec Authoring Worksheet

Use this worksheet every time you translate a design brief into a diagram spec. Treat it as a living scratch pad: overwrite the placeholders on each pass instead of adding new paragraphs, and keep it in sync with the working design. Follow the loop below strictly:

1. **Read this entire worksheet** before making any edits so the structure is fresh.  
2. **Initial fill:** complete Pass 1, then re-read the whole worksheet.  
3. **Subsequent passes:** for Pass 2 and Pass 3, always read that section before editing, overwrite the placeholders, then re-read the entire worksheet after each pass.  
4. Only once all three sections are complete should you touch `diagrams/specs/*.yaml`. If the rendered output looks wrong, come back here and correct the mismatch before editing code again.

---

## Global dimensions & datums

**Pass 1 – Design notes**  
Overall spans, offsets, heights in plain language.  
`<fill here>`

**Pass 2 – Schema mapping**  
List the dimension keys/expressions you will create.  
`dimension_name = expression`  
`dimension_name = expression`

**Pass 3 – YAML skeleton**  
Copy-ready fragment for the `dimensions` block.  

```yaml
dimensions:
  dimension_name: <value or expression>
  dimension_name: <value or expression>
  # …
```

Re-read the entire worksheet before moving on.

---

## Primary structural members

### Outer/perimeter beams

- **Pass 1 – Design notes**  
  `<fill here>`
- **Pass 2 – Schema mapping**  
  `<placement.flush …>`  
  `<vertical.flush …>`  
  `<repeat …>`
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: <component_id>
    class: <component_class>
    size: [<width>, <length>]
    placement:
      flush:
        ref: <reference_component>
        face: <face_token>
      attach_face: <face_token>
      inset:
        <axis_token>: <expression>
    vertical:
      flush:
        ref: <reference_component>
        face: <face_token>
      attach_face: <face_token>
      offset: <expression>
    material: <palette_key>
    height: <value>
  ```

Re-read the entire worksheet.

### Inner beams / headers / trimmers

- **Pass 1 – Design notes**  
  `<fill here>`
- **Pass 2 – Schema mapping**  
  `<placement.flush …>`  
  `<inset / translate …>`  
  `<vertical.flush …>`
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: <component_id>
    size: [<width>, <length>]
    placement:
      flush:
        ref: <reference_component>
        face: <face_token>
      attach_face: <face_token>
      inset:
        <axis_token>: <expression>
      translate:
        <axis_token>: <expression>
    repeat:
      count: <number>           # or interval/span
      direction: <axis_token>
      span: <expression>
    vertical:
      flush:
        ref: <reference_component>
        face: <face_token>
      attach_face: <face_token>
    material: <palette_key>
    height: <value>
  ```

Re-read the entire worksheet.

---

## Joist and slab layout

### Joist zones (describe each run separately)

For each zone (cantilever band, shoulders, walkway core):

- **Pass 1 – Design notes**  
  `<fill here>`
- **Pass 2 – Schema mapping**  
  `<placement.flush …>`  
  `<inset …>`  
  `<repeat: count / direction / span>`  
  `<vertical.flush …>`
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: <joist_id>
    size: [<span_expression>, <joist_width>]
    placement:
      flush:
        ref: <reference_component>
        face: <face_token>
      attach_face: <face_token>
      inset:
        <axis_token>: <expression>
    repeat:
      count: <number>           # or interval/span
      direction: <axis_token>
      span: <expression>
    material: joist
    height: <value>
    vertical:
      flush:
        ref: <datum_component>
        face: <face_token>
      attach_face: <face_token>
  ```

Re-read the entire worksheet.

### Blocking / straps / accessories

- **Pass 1 – Design notes**  
  `<fill here>`
- **Pass 2 – Schema mapping**  
  `<component refs + placement>`  
  `<operations if required>`
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: polyline         # or rectangle
    id: <component_id>
    placement:
      # …
    views: [plan]
  ```

Re-read the entire worksheet.

---

## Supports

### Perimeter posts / pads

- **Pass 1 – Design notes**  
  `<fill here>`
- **Pass 2 – Schema mapping**  
  `<anchor/placement>`  
  `<repeat direction/span>`  
  `<vertical.flush …>`
- **Pass 3 – YAML skeleton**  

  ```yaml
  - type: rectangle
    id: <post_id>
    size: [<post_size>, <post_size>]
    placement:
      flush:
        ref: <reference_component>
        face: <face_token>
      attach_face: <face_token>
      inset:
        <axis_token>: <expression>
    repeat:
      count: <number>
      direction: <axis_token>
      span: <expression>
    vertical:
      flush:
        ref: <reference_component>
        face: <face_token>
      attach_face: -z
    height: <value>
    material: timber
  ```

Re-read the entire worksheet.

### Header posts / hangers / seats

- **Pass 1:** `<fill here>`  
- **Pass 2:** `<schema mapping>`  
- **Pass 3 YAML:** similar skeleton with adjusted references.

Re-read the entire worksheet.

---

## Finishes & interfaces

- **Pass 1:** Describe decking, rim boards, liner clamps.  
- **Pass 2:** Map to components (`deck_overhang`, detail polylines) and their views.  
- **Pass 3 YAML:** Provide component snippets, ensuring `views` align with requirements.

Re-read the entire worksheet.

---

## Operations & views

- **Pass 1:** Identify rotations, mirrors, section planes.  
- **Pass 2:** Record exact targets, axes, about references, view constraints.  
- **Pass 3 YAML:** Draft `operations` and view-specific component entries.

Re-read the entire worksheet.

---

## Section components

- **Pass 1:** Note which section rectangles/planes reflect the plan geometry.  
- **Pass 2:** Map sizes/origins to the dimensions defined earlier.  
- **Pass 3 YAML:** Provide rectangle snippets for section components with updated dimensions and elevations.

Re-read the entire worksheet once more, confirm every placeholder is overwritten, then proceed to implement the YAML edits. After generating outputs and tests, compare the visuals back to the design doc; if discrepancies appear, return to the relevant section above to correct the logic before touching the spec again.
