My honest summary: the underlying idea is strong, and I could work productively with it, but the language is easier to understand conceptually than it is to write confidently. The core relationship model felt coherent; arrays, generated identities, operations, and collision handling were the bumpy parts.

I’d describe it as a promising semantic geometry language that already works, rather than a polished authoring language that disappears beneath the task.

## Overall impression

Once I understood the basic rule—

> define a component’s size, then constrain its faces or centre axes relative to other components

—the ordinary placement expressions became quite natural. This is substantially easier to reason about than a file full of absolute XYZ coordinates.

For example:

```yaml
+x: { ref: pond_frame, pos: -x }
+z: { ref: deck_surface, pos: -z }
```

is compact and meaningful. It says why the component is where it is, rather than merely where it is. That is the language’s biggest success.

My rough ratings would be:

| Area                                   | Impression                     |
| -------------------------------------- | ------------------------------ |
| Conceptual model                       | Very good                      |
| Reading ordinary components            | Good                           |
| Writing ordinary orthogonal components | Good after learning the tokens |
| Arrays and irregular repetition        | Moderate                       |
| Rotations, clones, and generated IDs   | Difficult                      |
| Diagnosing unexpected geometry         | Moderate to difficult          |
| Determinism and generated outputs      | Very good                      |
| Fabrication-level modelling            | Limited                        |

## What worked particularly well

### Relationship-first placement is genuinely useful

The spec usually preserves design intent rather than just coordinates. When the overhang changed from 340 to 350 mm, expressions such as:

```yaml
opening_width: pond_span - 2 * cantilever
```

propagated naturally into the opening and inner diagonal geometry.

Similarly, references such as `deck_frame`, `pond_frame`, and `opening_frame` made the model much easier to understand. Geometry-less reference components are a good abstraction: they give relationships something stable and semantically named to attach to without introducing fake solids.

This is the part I engaged with most smoothly.

### Dimensions and expressions are readable

The `dimensions` section is effective. Named values and basic arithmetic make the specification much more reviewable than repeated literals.

This was especially useful for the centre pair:

```yaml
joist_pair_offset: joist_pair_clear_gap / 2 + joist_width / 2
joist_pair_low_center: deck_span / 2 - joist_pair_offset
joist_pair_high_center: deck_span / 2 + joist_pair_offset
```

That expresses the actual construction rule clearly. A reviewer can verify the relationship without reverse-engineering coordinates.

### `place` was a good fit for the as-built joists

The existing evenly distributed joists were represented with arrays. Once the centre joist became an irregular pair, explicit named placements were the most honest representation.

That transition was straightforward:

```yaml
- id: joist_run_south_4
  cx: { ref: deck_frame, pos: -x, offset: joist_pair_low_center }
```

The language did not force me to pretend the joists were still uniformly spaced. This is important: `array` and `place` cover meaningfully different cases.

### Rotation provided substantial leverage

Authoring one side and rotating it around the origin is exactly the right model for this deck. It avoided four copies of the physical geometry and ensured the update propagated symmetrically.

The solver handled the eight placed joists, their rotations, the renamed instances, and downstream pad references correctly. When I inspected the resolved primitives, the centres and 1,303 mm lengths were exactly what the spec requested.

So although the operation syntax is cumbersome, the underlying capability behaved reliably.

### Validation is real rather than decorative

The schema rejects removed or incompatible constructs, checks unknown references, reports remaining degrees of freedom, validates array spans, and produces deterministic mesh checksums. That gave me more confidence than a permissive YAML format that silently accepts nonsense.

The ability to generate SVG, PNG, glTF, and IFC from the same resolved scene is also a major strength. The specification is genuinely authoritative rather than merely input to one drawing renderer.

## What was difficult

### Axis tokens are compact but cognitively dense

Simple tokens such as `+x`, `-y`, and `cx` became easy quickly. Expressions such as these did not:

```yaml
+x+y-x-y
-xcy
-x+y
```

They require the reader to mentally tokenize a small symbolic language embedded inside YAML keys.

The most important surprise is that a multi-axis key represents one plane, edge, or point constraint; it is not shorthand for several independent constraints. The authoring guide explicitly warns about this, which is good, but the fact that the warning is necessary shows that the syntax does not communicate its meaning naturally.

This was readable after learning it, but not self-explanatory.

An optional expanded syntax would help:

```yaml
align:
  subject: { x: max, y: center }
  target:
    ref: inner_beam_west
    x: min
```

The compact tokens could remain available for experienced authors.

### `pos`, signs, offsets, gaps, modes, and frames interact subtly

There are several concepts packed into one relation:

```yaml
+x:
  ref: something
  pos: -x
  offset: ...
  gap: ...
  mode: point
  frame: ...
```

Each individual field makes sense, but their combined directionality is not always obvious:

- Does a positive gap move in the subject-face direction or the target-face direction?
- Is an offset applied in world axes, target-local axes, or the specified frame?
- Does a multi-axis relation resolve as a point, edge, or several planes?
- When `pos` is omitted, is copying the subject token actually what the author intended?

The solver is internally consistent, but I sometimes had to consult the documentation or implementation rather than being able to predict the answer directly from the YAML.

### Arrays are powerful, but their mental model is not simple

The distinction is:

- the array’s axis map defines its available spatial extent;
- `repeat` defines how instances occupy that extent;
- the member size is subtracted before pitch is calculated;
- direction vectors influence which world axis is used;
- `through` checks direction but does not infer size;
- `array` cannot coexist with `relate`.

That is coherent once understood, but it is a lot of implicit behaviour behind a short block.

For a regular run, it is elegant:

```yaml
repeat:
  x: { count: 7 }
```

For an irregular run, it becomes awkward. The centre-pair change is a good example. There was no natural expression for “use these eight derived centre offsets” within one array, so explicit `place` entries were clearer.

I think the language needs an irregular-array form:

```yaml
array:
  centers:
    x:
      - joist_outer_low_center
      - joist_inner_low_center
      - joist_inner_mid_low_center
      - joist_pair_low_center
      - joist_pair_high_center
      - joist_inner_mid_high_center
      - joist_inner_high_center
      - joist_outer_high_center
```

That would preserve the fact that these are one repeated joist family without pretending the spacing is uniform.

### Generated IDs and `id_map` were the roughest authoring experience

This was the least pleasant part:

```yaml
joist_run_south_4:
  [joist_run_south_4, joist_run_east_4,
   joist_run_north_4, joist_run_west_4]
```

Repeated eight times, it adds a large block of mechanical bookkeeping. It also exposes execution details that feel lower-level than the geometric intent.

To work confidently, I had to understand:

- component IDs;
- placement IDs;
- template IDs;
- seed IDs;
- array `#` instance IDs;
- clone IDs;
- selector behaviour;
- how a rotation searches `instance_id`, `seed_id`, and `template_id`;
- which names later references and operations will see.

It worked, but this is where the language stopped feeling declarative.

Automatic naming would be much better:

```yaml
rotate:
  target: joist_run_south
  copies:
    south: 0
    east: 90
    north: 180
    west: 270
  rename: "joist_run_{copy}_{placement_index}"
```

The author should normally describe the naming pattern, not list every generated name.

### Operation ordering is non-local

The lint warning about mirroring a component before later clone generation illustrates another difficulty. Operations are sequential transformations over a generated identity graph, but the YAML reads more like a declarative description.

That mismatch means the author has to know when order matters. Earlier transformations not affecting later clones is defensible, but it was not what I would automatically expect from a “relationship-first” model.

Either operations should be made explicitly pipeline-like, or clone inheritance should be expressed declaratively.

### Collision reporting was the biggest workflow bump

The default build produced a very long list of collision errors for beam corners, beam-to-joist intersections, diagonals, and other intended construction contacts. I had to rebuild with collision handling set to ignore.

That was the point where the workflow behaved least like I expected. The geometry was solving correctly, but the normal documented build command failed because the collision system could not distinguish:

- an accidental clash;
- an intentional structural connection;
- simplified solid overlap standing in for unmodelled joinery;
- components that merely meet at a shared bearing region.

For structural models, intentional contact is fundamental. I would add a first-class connection/contact declaration:

```yaml
connections:
  - between: [joist_run_south, inner_beam_south]
    type: hanger
    collision: expected
```

or component-level permitted intersections. Globally ignoring collisions throws away too much useful checking, while reporting every beam connection produces too much noise.

### Debugging lacks an “explain” surface

I eventually queried the solved primitives directly to verify that the joists resolved to:

- the expected eight centres;
- the expected 1,303 mm length;
- the expected rotated copies.

That information should be available through a supported command, for example:

```text
pond explain option-c.yaml joist_run_south_4
```

with output such as:

```text
size: 47 × 1303 × 75
centre: (-108.5, -1801.5, 112.5)
x derived from:
  deck_frame.-x + joist_pair_low_center
y derived from:
  outer_beam_south.+y
z derived from:
  deck_surface.-z
copies:
  joist_run_east_4
  joist_run_north_4
  joist_run_west_4
```

That would improve the language more than adding further syntax. Most declarative languages become approachable when users can ask why a value resolved as it did.

## Readability of the complete file

Individual component blocks are generally readable. The whole file is harder.

`option-c.yaml` combines several layers:

- design dimensions;
- physical components;
- geometric constraints;
- repetition and transformation;
- IFC classification;
- rendering labels;
- view configuration;
- boolean operations;
- generated-ID management.

Keeping everything together gives a valuable single source of truth, but it also makes the supposed “compact sketch” fairly long and visually busy.

The IFC and rendering metadata are not especially difficult, but they interrupt the structural story. Defaults, profiles, or reusable component types could reduce that noise.

There is also some risk of duplicated truth. For example, a dimension may correctly change while a human-written label still says the old length—the 481 mm diagonal label was one such case. Derived labels or interpolation would help:

```yaml
label: "47x75mm inner corner joist | {corner_diagonal_length_inner:.0f}mm"
```

Functions such as `sqrt()` or a vector-length expression would also reduce hard-coded derived dimensions.

## Was it smooth in this task?

The honest answer is: mostly smooth in the core, bumpy at the edges.

The smooth part was:

1. identify the design relationships;
2. express the new dimensions;
3. replace the uniform centre joist with explicit paired placements;
4. rotate the placements;
5. resolve and render the geometry.

The bumpy part was:

1. determining the cleanest relationship between arrays and irregular placements;
2. managing all rotated placement IDs;
3. updating references to generated copies;
4. understanding the operation-order warning;
5. dealing with a flood of expected collisions;
6. querying internals to verify resolved positions.

I never felt that the solver was randomly interpreting the YAML. Once a relationship was expressed correctly, it behaved deterministically and generally as documented. The friction was primarily in expressing and inspecting intent, not unreliable execution.

## My overall judgment

I would keep the architecture and evolve the authoring surface.

The relationship-first model is the right foundation for this repository. It is much more suitable for reviewable, model-assisted structural diagrams than raw coordinates, handwritten SVG, or a general-purpose scripting API. Axis maps, references, dimensions, and deterministic compilation are all sound ideas.

The highest-priority improvements I would make are:

1. Add `explain`, resolved-scene, and placement-table commands.
2. Automate clone naming and remove most manual `id_map` bookkeeping.
3. Add irregular arrays based on explicit derived centre positions.
4. Model expected contacts/connections separately from accidental collisions.
5. Offer an expanded, descriptive alternative to dense axis tokens.
6. Support derived label interpolation and richer dimension expressions.
7. Provide editor/schema completion with examples for every axis-map form.

With those improvements, I think it could become genuinely pleasant to author. As it stands, I could engage with it successfully and confidently, but I had to understand a meaningful amount of the compiler’s internal model to do so. That is acceptable for an experimental language maintained by its author; it would be the main barrier for a new contributor.
