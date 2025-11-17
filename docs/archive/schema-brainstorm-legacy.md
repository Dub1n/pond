# Schema Simplification Brainstorm (Phase 4 Alignment)

## Concept Slate – Reimagining the Geometry Schema

### 1. Constraint Match Graph (CMG)

- **Idea:** Treat every component as a node in a constraint graph. Authors write edges that describe face-to-face matches using IFC axis tokens, e.g. `beam:+z -> joist:-z @ match -x,+y`.
- **Why it helps:** Matching is always explicit: a constraint must name both the axis pair and the corner/edge alias (`match -x,+y`). The solver translates the graph into exact transforms, so forgetting the perpendicular axis is impossible.
- **How it works:**  
  1. Declare components with intrinsic geometry only (`profile`, `length`, `material`).  
  2. Attach constraint edges that specify: driving component, driven component, face mapping (`+z to -z`), corner vector (`match -x,+y`), optional offsets.  
  3. The planner solves the graph, detecting contradictions early. Repeat patterns become graph templates (`template: joist_run { repeat [+x] step 400 count 12 }`).  
- **Risks:** Needs a robust solver and cycle detection, but once implemented it generalises cleanly to 3D.
- **Ergonomics:** Dramatically reduces edge-matching mistakes because every joist/header relationship must spell out both faces; when the agent rewrites the outriggers from design-B.md they can mirror the “flush face + matching corner” language instead of inventing offsets. The tradeoff is heavier bookkeeping—each run needs unique node IDs, corner vectors, and template hints—so omissions surface as solver errors that may feel opaque while iterating. Intuition sits between geometry math and BIM constraints; it rewards agents who already sketch relationship graphs but slows first-pass edits. Translation overhead is moderate: spec-authoring-worksheet-design-B.md would need an extra pass to map the worksheet bullets into graph edges before YAML exists.

### 2. Datum Stack Recipes (DSR)

- **Idea:** Define a small set of global datums (`datum.outer_ring`, `datum.water_surface`, `datum.header_line`). Components declare which datums they “stack” between: `joist.stack between [datum.outer_ring.-x, datum.header_line.+x] align corners -x,+y`.
- **Why it helps:** Authors think in structural layers (“stack the joists between these planes”) rather than raw offsets. Vertical and horizontal anchoring always reference named datums, preventing drift.
- **How it works:**  
  1. Start each spec by defining datums (planes, lines, or points with IFC tokens).  
  2. Components use a `stack` block: `stack: { from: datum.walkway.+z, to: datum.deck_surface.-z, corner: [-x,+y] }`.  
  3. Repeats reference datum spans (`repeat: { axis: +x, between: [datum.outer_ring.-x, datum.outer_ring.+x], pitch: joist_spacing }`).  
- **Risks:** Requires authors to think in datums first, but the mental model matches construction docs and 3D BIM conventions.
- **Ergonomics:** Anchoring everything to named datums removes “forgot to mirror the inset on the south edge” mistakes; the agent can lift datum names straight from the Global dimensions & datums pass of spec-authoring-worksheet-design-B.md. The downside is upfront datum bookkeeping—misnamed or missing datums stall the stack, and one-off elements (like a single fascia splice) may demand temporary datums. Once the base set is defined it feels close to the way design-B.md describes layers, so after the first pass the translation overhead nearly disappears.

### 3. Assembly Recipes & Blocks (ARB)

- **Idea:** Introduce higher-level assemblies (e.g. `assembly.joist_bay`, `assembly.corner_frame`). The author instantiates assemblies and only tweaks parameters; each assembly encapsulates all face matching internally.
- **Why it helps:** Complex alignment logic becomes an implementation detail of curated recipes. Authors can’t misalign individual members unless they dive into the assembly definition.
- **How it works:**  
  1. Assemblies live in a library with named anchor faces (`primary_origin`, `+x_span_face`).  
  2. Spec authors write `place assembly.joist_bay at datum.outer_ring corner [-x,+y]` with overrides (`joist_spacing: 400`).  
  3. The assembly expands into the low-level components, already matched and stacked correctly.  
- **Risks:** Library maintenance overhead, but ideal for recurrent deck geometry.
- **Ergonomics:** Prebuilt assemblies keep contributors from missing repeat faces or rotate operations; dropping in an `assembly.joist_bay` for Option B means the joist, blocking, and strap relationships arrive aligned. The pitfall is discoverability—authors must browse library definitions, learn parameter names, and crack open the assembly whenever the design deviates (e.g., a unique header lap), shifting debugging to a higher abstraction. Feels intuitive for recurring patterns but less so for bespoke tweaks; mapping design-B.md sentences to the right assembly still forces a selection step before touching YAML.

### 4. Spatial Sentences DSL (SSD)

- **Idea:** A natural-language-ish mini DSL captures intent: `joist_run: from beam.west face +x to header.east face -x, flush corner -x,+y, repeat every 400 along +x`. The parser translates sentences to schema objects.
- **Why it helps:** Reduces YAML ceremony and emphasises relationships. The sentence template enforces mentioning both faces and the corner, eliminating half-specified constraints.
- **How it works:**  
  1. Define a limited grammar (`component: from <ref> face <dir> to <ref> face <dir>, flush corner <corner>, repeat ...`).  
  2. Parser generates canonical schema blocks (`placement`, `repeat`, `vertical`).  
  3. Validation can highlight missing segments (“corner clause missing”).  
- **Risks:** Another syntax layer to learn, but the enforced order encourages full intent capture.
- **Ergonomics:** The sentence grammar mirrors the prose in design-B.md (“from outer beam to header, repeat every 400”), letting agents almost paste the requirement while the parser enforces mandatory clauses. Pitfalls shift to syntax—typos or unsupported constructions become parser errors, and long sentences can feel unwieldy when you mix repeats, stacks, and offsets. It reads intuitively because clause order matches how spec-authoring-worksheet-design-B.md already scripts placement notes, yet there is still a translation step into the approved verb phrases.

### 5. Relationship-Only Specs (ROS)

- **Idea:** Components carry zero absolute coordinates. Everything is declared as relationships (`joist_run aligns beam via { faces: [+z -> -z], corner: [-x,+y] }`). The planner picks one component as ground truth (typically the pond water) and resolves the world from relationships.
- **Why it helps:** Impossible to forget a perpendicular align because there are no raw positions to fall back on. If a relationship is missing, the solver fails instead of guessing.
- **How it works:**  
  1. Mark a single `anchor` component with absolute placement (e.g. `pond_water` at origin).  
  2. Every other component lists one or more relationships.  
  3. Solver performs constraint propagation; under-constrained specs raise explicit errors.  
- **Risks:** Demands a solid constraint engine, but scales naturally to 3D and IFC solids.
- **Ergonomics:** Eliminates edge drift entirely—if a joist lacks a relationship to the header the solver refuses to run, so agents don’t unknowingly ship misaligned geometry. The cost is that every component must surface enough constraints to solve; while drafting Option B you have to capture perpendicular, vertical, and rotation ties that were previously implied, and under-constrained errors can feel abstract until you visualise the network. For authors already thinking in relationships the flow is coherent, but spec-authoring-worksheet-design-B.md would grow a checklist to ensure each new piece references the right anchors, adding planning time before YAML entry.

## Fitting the Concepts into Phase 4 Prep

### Constraint Match Graph ↔ Phase 4

- Integrates cleanly with the planned IFC axis tokens: each constraint already uses `±x/±y/±z`.  
- Could sit atop the proposed single-field `class` design; assemblies resolve to IFC primitives once constraints solve.  
- Aligns with the report’s call for validation-first tooling: graph solver detects missing faces immediately.

### Datum Stack Recipes ↔ Phase 4

- Complements the report’s axis-overhaul by promoting datums as first-class dimension names (`dimensions.structure.datum.outer_ring`).  
- Works with the interim axis shim because datums stay declarative; planner just translates the axis tokens.  
- Encourages the documentation update the report already earmarks (authors learn to think in axis-aligned datums).

### Assembly Recipes & Blocks ↔ Phase 4

- Slots into the “optional primitive override” idea—assemblies can declare their IFC class once and emit the rest.  
- Supports the planned lint CLI: assemblies validate their parameter sets before expanding.  
- Helps bridge the Phase 3→4 gap by keeping familiar YAML while hiding the new solid kernel complexity.

### Spatial Sentences DSL ↔ Phase 4

- Could be the “authoring playground” mentioned in the report: the DSL feeds a notebook UI that previews the parsed placements.  
- Parser emits the axis-aware schema, so it plays nicely with the `+x/-x` vocabulary.  
- Useful as a migration aid—legacy specs get translated into sentences first, then into the new canonical blocks.

### Relationship-Only Specs ↔ Phase 4

- Most radical, but matches the report’s long-term IFC ambition: IFC data is relationship-heavy, so pushing relationships into the spec aligns with downstream exports.  
- Necessitates upgrades to the planner described under “Implementation outline” (constraint solver instead of simple placement math) but those upgrades dovetail with the CadQuery solid kernel.  
- Encourages richer validation (under-constrained vs over-constrained) that the report already flags as necessary for Phase 4 robustness.

## Phase 4 Ergonomics Rewrite

With freedom to rethink the schema, Phase 4 can centre on relationship-first authoring that still aligns with IFC where it matters. The proposal below describes the new canonical shape and how it mitigates the ergonomic pitfalls identified earlier.

- **Core structure.**
  - Every component declares its `component.id`, `class`, and intrinsic geometry (`profile`, `size`, `height`, `material`, optional `metadata`). `class` prefers IFC tokens (`IfcBeam`, `IfcJoist`); when a concept falls outside IFC, we keep descriptive names but still allow optional `ifc.*` enrichments.
  - Authors describe placement solely through `relate` clauses. Each clause targets two endpoints (`subject`, `object`) and spells out axis-aligned contacts such as `faces: {subject: +z, object: -z}` and optional corner vectors (`corner: [-x, +y]`) plus `offset` dictionaries keyed by axes. Multiple clauses per component build a constraint set that the solver resolves; under- or over-constrained nets return actionable diagnostics before renders run.
  - Rotations, mirrors, and repeats become constraint templates: `repeat: {axis: +x, pitch: dimensions.structure.joist_spacing, count: 12}` appends derived components without requiring manual IDs; the solver ensures each generated element inherits the same relationship set.

- **Datums as first-class references.**
  - Specs may declare a `datums:` block containing named planes, lines, or points (`outer_ring_edge`, `header_plane`, `datum.top_of_pad`). Datums expose axis faces just like components, so constraints can target `datums.header_plane.+x` when a component should stay tied to project geometry instead of another element.
  - Datums are optional: simple specs can relate components directly, while larger architectural layouts gain clarity by anchoring everything to shared frames.

- **Dimensions and expressions.**
  - Dimension namespaces (`dimensions.structure.backspan`, `dimensions.arch.finish_height`) remain the only place literal numbers appear. Both component geometry and constraint offsets reference these names or expression strings (`deck_span - 2 * dimensions.structure.walkway_backspan`), keeping specs symbolic and resilient.

- **Constraint solver & validation.**
  - The planner runs a proper constraint solve over the `relate` graph: it checks for sufficient constraints in X/Y/Z, reports conflicting faces, and highlights dangling references. Validation errors quote the exact clause (`component joist_run_north → faces {+z/-z}`) to aid debugging.
  - Because constraints already use `±x/±y/±z`, downstream exporters adopt IFC axes directly; the legacy screen-coord shim disappears.

- **Progressive ergonomics.**
  - Assembly recipes publish curated constraint bundles (`assembly.joist_bay`) that expand inline at load time. Their definitions live beside the schema and remain editable YAML, so there’s no opaque templating layer—authors can read the expanded constraints or override them when needed.
  - A companion authoring helper (CLI/notebook) accepts constrained sentences (`place joist_run from outer_beam face +x to header face -x corner [-x,+y] repeat every dimensions.structure.joist_spacing along +x`) and emits canonical `relate` clauses. Teams can ignore it or adopt it based on preference; the stored schema stays consistent either way.

- **IFC alignment without rigid coupling.**
  - Axis tokens and default classes follow IFC out of the box, enabling direct exporting of structural members. However, the schema never forces IFC values when they would obscure intent—detail annotations can stay freeform while still benefiting from constraint checking.
  - Optional `ifc:` blocks capture predefined types, payload (load-bearing, fire rating), and property sets for teams that need richer BIM outputs, but omitting them leaves the authoring flow unchanged.

This rewrite keeps the author’s mental model focused on “which faces touch, along which spans, using which named frames.” Constraints eliminate accidental edge mismatches, datums provide shared context for complex arrangements, and the combination of assemblies plus optional sentence helpers reduces boilerplate without hiding the underlying mechanics. At the same time, the schema naturally exports to IFC-aligned tooling because the axis vocabulary and class semantics match industry expectations wherever it helps.

### Keeping it DRY without Excess Abstraction

Authoring the Option C example surfaced a few practical aids that preserve clarity while trimming repetition:

- **Datum bundles.** Allow specs to declare `datums.deck_faces: true` or `datums.pond_faces: true`, which expands into the standard orthogonal planes rooted at a provided point. Authors still see the generated datums in validation output, but they no longer have to spell out every plane manually.
- **Span aliases.** Let repeats reference a named datum pair or axis bundle (`span: datums.deck_faces.y`) so they only state intent (“fill between the deck faces along Y”) instead of re-deriving from/to offsets each time.
- **Constraint presets.** Introduce small declarative helpers (`touch: {subject: +z, object: datums.joist_top_plane}`) that expand into the full `relate` clause. These work like readable macros—transparent after expansion—yet keep common cases terse.
- **Inline assemblies.** Permit compact assembly definitions directly inside a spec (`use assembly.joist_bay with {pitch: dimensions.structure.joist_spacing}`) that immediately inline into canonical constraints. Because the expansion is literal, authors can inspect or tweak it without leaving the file.
- **Authoring helpers.** Ship CLI/notebook utilities that consume simple prompts—“joist run from outer beam to inner beam, cantilever 250”—and emit the corresponding constraint block. Teams can adopt them ad hoc without changing the stored schema.
- **Validation nudges.** Provide lint rules that suggest promoting redundant ad hoc planes or spans into shared datums, helping teams converge on consistent names without strict enforcement.
- **Batch faces & inheritance.** Extend presets to accept face arrays (`touch_planes: {object: datums.planes.joist_top, faces: [+z, -z]}`) and let components inherit a prior constraint set with targeted overrides (`relate_from: outer_beam_template`). This keeps mirrored members compact while preserving explicit intent.
- **Rotation helpers.** Add assemblies such as `rotate_quadrants` that clone a seed component around a pivot, so orthogonal frames or joist belts fan out from one canonical definition without bespoke macros.

These niceties keep the schema ergonomic: authors describe intent once, rely on bundles or presets for the boilerplate, and fall back to raw constraints whenever bespoke geometry demands it. Importantly, none of them hide the underlying relationships, so debugging and IFC alignment stay transparent.
