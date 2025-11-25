# Shed flat-roof render pass — report (2025-11-22)

## Actions taken

- Read repository instructions and design worksheet template; authored a filled worksheet for the shed concept.
- Authored `shed-flat-roof.yaml` option A with pads, platform floor, split north wall for door opening, roof joists/deck, and door header.
- Ran `.venv/bin/python scripts/build_diagrams.py --spec diagrams/specs/shed-flat-roof.yaml --outdir diagrams/output --force` to produce plan/section PNG/SVG plus glTF.
- Ran `.venv/bin/python scripts/baseline_render_check.py --fresh-check` (fresh check passed).
- No edits made after user feedback; observations only.

## Structure overview (what the YAML describes)

- 3.0 m × 2.4 m footprint on a 3×3 concrete pad grid; pads under a 45×145 rim/joist platform with 18 mm floor deck.
- Walls modeled as flat rectangles: north split around a 900 mm centered door, full-width south wall, west/east walls inset to clear the north/south wall depths.
- Door header above the opening (double orientation implied by height/depth).
- Roof joists (45×145) running north–south with 150 mm overhang each side; roof deck sized to the overhang and sitting on the joists.
- Section plane at mid-depth to show floor, walls, roof stack.

## Semantic mapping of key placements

- Pads: base at grade origin; repeated east/south to span footprint.
- Floor rim: origin at pad grid corner; flush to pad tops.
- Floor joists: flush to rim west edge; repeated east across width; top set by rim bottom flush.
- Floor deck: flush to rim top.
- North wall: split into left/right rectangles; both sit on floor deck; door opening left empty between them.
- South wall: flush to rim south edge; west/east walls inset by wall depth so their outer faces align with north/south inner faces (keeps corners boxed).
- Roof joists: flush to roof deck west edge; repeated east across roof width; set at floor deck elevation + wall height.
- Roof deck: sized to overhang; placed at floor deck elevation + wall height + roof joist depth.
- Door header: aligned to north edge of floor rim and inset by door offset; vertical offset = wall height – header depth.

## Where the YAML fell short (diagnosed issues)

- East wall floats: placement aligns its inner face to the floor rim outer face, leaving an outward offset; needs attach_edge/flush to make outer faces flush.
- West roof joist floats: first joist sits off the west wall/rim; needs attach_edge west flush to roof deck or a rim-like member to close the gap.
- Roof deck overhang asymmetry: deck aligns flush to joist edge on one side and overhangs on the other; likely from referencing roof_base for joist placement without symmetric attach_edge.
- Roof-to-wall gap: no roof rim/top plate component bridging walls to roof deck, leaving daylight at the wall tops; roof fall not expressed, so roof is flat despite dimension.
- Section readability: walls are shallow rectangles (wall depth only), so plate/stud depth and top/bottom plates are not distinguished; roof fall dimension unused.

## What worked well with the schema

- Placement helpers (`flush` + `repeat.interval/span`) made joist and pad arrays quick without manual spacing math.
- Origin-at-rim pattern kept most components aligned without extra offsets.
- Vertical blocks with flush + offset made stacking (pads → rim → deck → walls → roof) clear and editable.
- Splitting the north wall instead of a boolean cutout avoided MultiPolygon errors while keeping the opening visible.

## Schema friction / ideas for ease and accuracy

- Face alignment clarity: distinguishing “attach outer face to outer face” versus “attach inner face” would help walls; attach_edge defaults could be more explicit.
- Openings: a native wall-with-opening pattern would avoid manual splits/booleans and reduce MultiPolygon risks.
- Roof fall: a helper for sloped planes (datum + fall direction/value) would let roof decks/joists express slope without per-edge offsets.
- Rim/plate primitives: lightweight “plate/rim” components (or templates) would close wall-to-roof gaps and reduce drift at roof edges.
- Symmetric overhangs: a concise pattern to keep overhangs symmetric around an origin would prevent one-sided over/underhangs when using placement against overhang-sized rectangles.
- Material semantics: pads used timber material due to palette limitation; a concrete/default pad material key would improve clarity.

## Worksheet review

- The worksheet captured brief, geometry, dimensions, and component mapping clearly enough to script the YAML without re-reading the prompt.
- Pass-3 dimensions dropped straight into the spec; helpful for repeat spans and heights.
- Component mapping (Section 7) guided which faces to flush and how to repeat; however, it didn’t call out face orientation (inner vs outer) explicitly—adding that prompt would help avoid floating walls.
- QA checklist reminded to consider section plane and vertical flushes; roof fall and rim closure gaps were still easy to miss.

## Additional observations / thoughts

- The schema coped with a simple shed using rectangles and repeats, but face specificity and slope support are the main gaps for accuracy.
- Boolean openings on thin walls are fragile; splitting the wall is safer but verbose.
- A roof rim/top-plate helper plus slope support would make “box with roof” authoring faster and less error-prone.
- If overhang symmetry and face-attach defaults were more declarative, the floating wall/joist issues would likely disappear on first pass.
