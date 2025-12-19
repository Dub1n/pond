# Axis-Maps: A Relationship-First Constraint Primitive for Deterministic Geometry

> **Abstract**  
> Axis-maps define a protocol-level vocabulary for expressing geometric relationships. They specify which relationships are asserted, which degrees of freedom are constrained, and how intent is represented, while deliberately leaving resolution strategies and numeric methods to implementations.

## Motivation

Most CAD and parametric modelling systems expose geometry through high-level operations: sketches, mates, anchors, transforms, or helpers that encode placement implicitly. While effective for interactive use, these abstractions tend to obscure *why* geometry is positioned the way it is, make partial intent difficult to express, and complicate reproducibility, automation, and validation.

The **axis-map** is proposed as a low-level, explicit alternative: a declarative constraint primitive that maps specific axes, faces, edges, or points of one object to those of another, with clear intent about degrees of freedom, orientation, and reference frames. Axis-maps are designed to be authored directly, reasoned about symbolically, and resolved deterministically.

This document outlines the axis-map concept, its implementation, how it relates to existing paradigms, and why it enables workflows that are otherwise difficult or impossible in conventional CAD systems.

---

## What Is an Axis-Map?

An **axis-map** is a directional mapping between *subject axes* and *target geometry*, optionally scoped to a specific reference frame and interpreted in a defined geometric mode.

In practical terms, an axis-map answers questions such as:

- Which side of this component is being constrained?
- To which face, edge, or point of another component or reference?
- In which coordinate frame should this relationship be interpreted?
- How many degrees of freedom are intentionally constrained?

Each axis-map entry may specify:

- **Subject axis** (e.g. `+x`, `-y`, `cx`, `-x+y`)
- **Target reference** (component, instance, datum, or bundle)
- **Target position** (axis, face, edge, point)
- **Mode** (`plane`, `edge`, `point`)
- **Frame** (`local`, `world`, or another component)
- **Gap / offset** values
- Optional size inference or validation behaviour

Crucially, axis-maps may be *partial*, *complete*, or *intentionally over-constrained*.

---

## Example (Pond relationship specs)

This project uses axis-maps as the primary placement primitive. A typical block sets faces and centers against other components and datums, with frame-aware positioning and explicit offsets:

```yaml
components:
  - id: joist
    class: IfcBeam
    size: [47, 150, null]
    relate:
      +x: { ref: rim_west, pos: +x, frame: local }
      -x: { ref: rim_east, pos: -x, frame: local, gap: 10 }
      cy: { ref: deck_frame, pos: cy }
      +z: { ref: datum_top, pos: +z }
```

Each key (`+x`, `-x`, `cy`, `+z`) names the subject axis; the value names a target (`ref`), the target position (`pos`), an optional `frame`, and per-axis `gap`/`offset`. Missing size on `z` will be inferred from opposing `+z/-z` relations elsewhere or validated if explicitly provided.

---

## Partial Constraints as a First-Class Feature

Most modelling systems implicitly assume that geometry should be fully solved to a single rigid transform. Axis-maps reject this assumption.

A single axis-map may:

- Constrain only one axis (leaving translation and rotation free elsewhere)
- Constrain two axes (fixing a plane but allowing sliding)
- Constrain all axes (fully determining placement)
- Constrain more axes than strictly necessary, for the purpose of **consistency checking**

Over-constraint is not treated as an error by default. Instead, it is used as a mechanism to assert intent and verify that implied geometry (for example, inferred sizes or spans) agrees with explicitly declared values. When disagreement occurs, it is surfaced as a lint or validation error rather than silently resolved.

This makes axis-maps suitable not only for placement, but also for *geometric assertions*.

---

## Explicit Sidedness and Orientation

Axis-maps encode sidedness directly via signed axes (`+x`, `-x`, etc.). This avoids a common source of ambiguity in CAD systems where face normals, selection order, or UI state determine orientation implicitly.

By making sidedness explicit:

- Orientation is stable and reproducible
- Flips and mirror errors become visible in diffs
- Constraint intent survives refactors and automated generation

Signed axes also allow the same component to participate in multiple relationships without ambiguity about which face or direction is being referenced.

---

## Modes and Degrees of Freedom

Each axis-map entry is interpreted under an explicit **mode**:

- **Point**: constrains a specific point (0 DOF)
- **Edge**: constrains along a line (1 DOF)
- **Plane**: constrains a face or plane (2 DOF)

This aligns the schema directly with geometric degrees of freedom rather than UI metaphors. It allows the solver to reason precisely about what remains unconstrained, and enables diagnostics that explain *which* freedoms are still available and *why*.

---

## Size Inference and Validation

Axis-maps support size inference when paired constraints imply a span (for example, opposing faces along an axis). Inferred sizes may be:

- Accepted implicitly
- Compared against explicit size declarations
- Used as validation checks

This allows authors to write specifications that act as *geometric proofs*: the model both derives geometry and verifies that independent statements about size and alignment are consistent.

---

## Comparison With Existing Paradigms

### CAD Mates and Constraints

Traditional CAD systems expose mates such as coincident, flush, distance, or angle constraints. These are high-level operations that often compile down to lower-level constraint graphs.

Axis-maps operate closer to this internal representation, but are:

- Explicit about axes and sidedness
- Frame-aware
- Composable
- Directly authorable

They replace many specialised mate types with a single, uniform primitive.

---

## Prior Art and Positioning

Axis-maps draw on established ideas that already exist across several domains. Parametric CAD systems use constraint graphs and mating operations to position geometry relationally rather than purely by coordinates. Robotics and kinematics systems express relationships between parts through coordinate frame mappings and transforms. BIM standards such as IFC encode hierarchical placements and orientation through nested local coordinate systems.

All of these demonstrate that relational geometry is well understood in principle. However, in most tools these structures are either hidden behind interactive UIs, embedded implicitly in procedural code, or exposed only as verbose, machine-oriented output formats.

What axis-maps make explicit is a stable, authorable representation of these relationships at the axis level. They combine signed axes, partial constraints, explicit degrees of freedom, frame awareness, and optional over-constraint for validation into a single declarative primitive. While similar information exists inside CAD kernels and solvers, it is rarely exposed as a first-class, text-based authoring surface.

The novelty of axis-maps does not lie in inventing new geometric concepts, but in elevating an implicit internal structure into a readable, deterministic schema that can be written by humans, generated by programs or language models, validated in CI, and compiled reliably into downstream geometry formats.

### Constraint Graphs and Parametric Solvers

Constraint graphs describe relationships abstractly, often without exposing their geometric interpretation. Axis-maps encode constraints in a form that is both solver-friendly and human-readable, making the constraint graph itself part of the authoring surface.

---

### Coordinate Frame Transforms (Robotics / Kinematics)

Robotics systems describe relationships between coordinate frames using full 6-DOF transforms. Axis-maps generalise this idea by allowing *partial* frame relationships, which better matches the realities of physical assemblies and construction geometry.

---

### IFC and BIM Placement

IFC expresses placement as nested local coordinate systems. Axis-maps operate *upstream* of this representation, providing a semantic layer that explains how those placements are derived. This makes them well suited as a pre-IFC authoring abstraction.

---

## Why Axis-Maps Enable New Workflows

Because axis-maps are:

- Declarative
- Deterministic
- Textual
- Explicit about intent and ambiguity

they enable workflows that are difficult in conventional CAD tooling:

- Authoring entirely in a text editor
- Version control and meaningful diffs
- CI-based validation and regression testing of geometry
- Programmatic mutation and parameter sweeps
- Language-model-assisted generation of accurate, adjustable diagrams
- Clear diagnostics when geometry changes unexpectedly

Rather than hiding complexity, axis-maps make it inspectable and enforceable.

---

## Design Philosophy

Axis-maps are intentionally low-level. They are not optimised for casual discovery or direct manipulation, but for correctness, traceability, and reproducibility. Higher-level authoring aids (templates, helpers, UX sugar) are expected to *compile into* axis-maps rather than replace them.

This preserves a single canonical representation of geometric intent while allowing multiple authoring experiences to coexist above it.

---

## Summary

The axis-map is a small but powerful abstraction: a declarative mapping between axes that captures placement, orientation, constraint, and validation intent in a single, uniform form. By elevating this concept to a first-class schema element, the system enables deterministic geometry generation that is explainable, automatable, and suitable for both human and machine authorship.
