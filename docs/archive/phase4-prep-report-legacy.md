## Phase 4 prep – IFC alignment & schema surface

### Context

- Phase 4 introduces a CadQuery-backed solid kernel, so every structural component becomes a true 3D solid.  
- Export targets (STEP today, IFC next) expect canonical semantics for both axis orientation and element typing.  
- Phase 3 specs still rely on compass-point naming and loosely-defined schema fields, which routinely causes misaligned members and manual clean-up.

### Axis-aligned naming overhaul

- **Adopt signed axis faces across the plan and section planes.** Every `align`, `anchor_point`, `attach_edge`, `placement.flush.edge`, and `vertical.flush.face` will now accept `+x`, `-x`, `+y`, `-y`, `+z`, `-z`, plus compound faces expressed as arrays (for example `[-x, -y]` for the north‑west corner).  
- **Legacy compass tokens (`north`, `south`, …) will be removed**, eliminating the translation step that currently leads to wrong offsets and floating members. This keeps the YAML vocabulary consistent with IFC’s axis conventions and with the underlying Geometry kernel.
- **Schema adopts IFC axis semantics immediately.** Authors write `+y` for “north/up” in plan and `-y` for “south/down”, matching IFC project coordinates. The planner will temporarily map these values to the legacy screen-style frame (`+y` internal = south) so existing geometry code continues to work while Phase 4 solid modelling lands. A dedicated migration will later flip the internal basis to match the schema, removing the shim.

| Legacy token | New axis face | Notes |
|--------------|---------------|-------|
| `north`      | `+y`          | IFC-style positive Y |
| `south`      | `-y`          |  |
| `east`       | `+x`          | Rightwards in plan |
| `west`       | `-x`          | Leftwards in plan |
| `north_east` | `[+y, +x]`    | Provide faces in any order; engine normalises |
| `north_west` | `[+y, -x]`    |  |
| `south_east` | `[-y, +x]`    |  |
| `south_west` | `[-y, -x]`    |  |
| `center`     | `origin`      | New keyword; resolves to centroid with no directional bias |
| `top`        | `+z`          | Vertical alignment |
| `bottom`     | `-z`          | Vertical alignment |

- **Placement helpers read axis faces directly.** Example:  

  ```yaml
  placement:
    flush:
      ref: pond_water
      face: -x
    attach_face: +x
    inset:
      +y: outrigger_margin
  ```  

  The same vocabulary applies to `vertical` blocks (`face: +z`, `attach_face: +z`) so authors never bounce between compass labels and axis labels.
- **Exporters honour IFC axes**: STEP/IFC writers pass the schema-level axes through unchanged, while the interim planner shim maps them into the legacy frame internally. This keeps external integrations consistent during the migration window.
- **Repeat spans inherit axis tokens**: `direction: +y`, `span: deck_span - post_size`, or `vector: [+x, +y]`. Mixed notation is disallowed; validation fails fast and points to the offending component.

### Schema surface decisions

1. **Single required `class` field.**  
   - If the value matches the IFC naming pattern (`Ifc*`), treat it as the canonical IFC class and resolve the primitive automatically (e.g., `IfcBeam` → rectangular footprint).  
   - Otherwise interpret the value as the geometry primitive itself (`rectangle`, `polyline`, `polygon`, …).  
   - The loader records both the resolved primitive and (when applicable) the IFC class so downstream planners/exporters have explicit data.

2. **Optional `primitive_override` for non-default footprints.**  
   - Use when an IFC class needs a different primitive (e.g., `IfcSlab` with a swept path).  
   - Validation ensures overrides are compatible with the class and supplies actionable errors.

3. **`ifc` metadata block remains, focused on semantic enrichments.**  
   - `ifc.predefined_type`, `ifc.load_bearing`, `ifc.fire_rating`, etc., stay additive; only `class` is mandatory.  
   - Validation accepts case-insensitive enum values, normalising to the STEP-style uppercase tokens (`BEAM`, `JOIST`, `DECK`, …) for storage/export.
   - Non-structural annotations (plan-only polylines without height) may omit the block entirely.

4. **Structural defaults derive from existing geometry.**  
   - `size`, `height`, and `material` feed IFC profile width/depth, extrusion thickness, and `IfcMaterial` assignments automatically.  
   - Validation prompts for missing data only when derivation fails (e.g., zero `height` on a joist).

5. **Documentation and validation move in lockstep.**  
   - Instructions will feature axis-based placement examples, repeat recipes, and IFC class lookups.  
   - Schema validation errors reference the new vocabulary (`face +x`, `class IfcBeam`) rather than the retired compass terms.

### Proposed schema shape

```yaml
class: IfcBeam                # resolves primitive = rectangle automatically
primitive_override: polygon   # optional, only when deviating from the default
ifc:
  predefined_type: BEAM
  load_bearing: true
material: timber
size: [180, 150]
height: 150
placement:
  flush:
    ref: frame_ring
    face: -x
  attach_face: +x
  inset:
    +y: joist_spacing / 2
repeat:
  interval: 400
  direction: +y
  span: deck_span - joist_width
vertical:
  flush:
    ref: datum
    face: +z
```

### Additional authoring improvements

- **Placement grammar refinement**: replace `anchor`/`offset` on rectangles with a single `placement` block so every component reads as intent (`flush`, `inset`, `translate`) rather than delta math. Provide a `translate` helper that accepts axis-keyed distances (`{+x: backspan, -y: walkway_gap}`) to remove residual vector guessing.  
- **Dimension namespaces**: allow option-level `dimensions` to expose nested groups (`structure.backspan`, `structure.cantilever`, `hardware.bolt_edge_distance`) so authors can reuse descriptive keys without collisions.  
- **Validation-first CLI**: add `scripts/lint_specs.py` that runs schema validation, IFC class checks, and axis-token audits before regeneration. This keeps contributors from generating artefacts off malformed specs.  
- **Authoring playground**: bundle a minimal Jupyter/pyodide notebook that visualises axis faces and repeat spans interactively. New agents can sanity-check placements before editing YAML.

### Implementation outline

1. **Schema layer**  
   - Implement axis-token enums and remove compass aliases.  
   - Parse the new `class` field, resolve primitives, and honour `primitive_override`.  
   - Update validation to enforce axis-token usage, IFC requirements, and structured dimensions.
2. **Planner layer**  
   - Teach placement, vertical alignment, and repeat resolvers to operate on axis faces/vectors, including the interim IFC→legacy axis mapping.  
   - Ensure rotated/mirrored clones copy resolved primitives and IFC metadata.
3. **Exporter layer**  
   - Map local `(+x, +y, +z)` orientation to IFC’s project coordinate system during STEP/IFC writes.  
   - Record derived profile data in the IFC material/property sets.
4. **Documentation & tooling**  
   - Refresh `docs/instructions.md` with axis-based examples, repeat recipes, and IFC lookup tables (enumerations noted as uppercase per IFC).  
   - Update fixtures and tests to cover axis tokens, single-field `class` handling, and validation errors.

### Next steps

1. Prototype the axis-token parser and update one option spec (e.g. Option B) to verify ergonomics.  
2. Land schema changes for the consolidated `class` field and `primitive_override`.  
3. Update planner/tests to use the new placement vocabulary and axis-aware repeat logic.  
4. Refresh authoring docs and add the spec lint CLI.  
5. Plan the migration of remaining specs once the prototype proves out, then retire compass vocabulary wholesale.
