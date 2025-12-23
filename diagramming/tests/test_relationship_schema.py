from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
import unittest

from diagramming.relationships import SchemaError, canonical_pos_token, lint_relationship_spec, load_relationship_spec


class RelationshipSchemaTests(unittest.TestCase):
    def test_canonical_pos_token_orders_and_accepts_centers(self) -> None:
        token = canonical_pos_token("cy+z-cx")
        self.assertEqual(token, "cxcy+z")

    def test_lint_flags_missing_axis_on_component(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: lint-missing
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [100, 50, 20]
                relate:
                  +x: { ref: origin, pos: +x }
                  +y: { ref: origin, pos: +y }
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        errors = lint_relationship_spec(spec)
        self.assertTrue(any("missing placement on axis z" in err for err in errors))

    def test_reference_allows_missing_axes(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: lint-reference
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "reference.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        errors = lint_relationship_spec(spec)
        self.assertFalse(errors)

    def test_axis_map_accepts_multiple_targets(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: multi-ref
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: datum
                kind: reference
                size: [0, 0, 0]
                relate:
                  cx: { ref: origin }
                  cy: { ref: origin }
              - id: beam
                class: IfcBeam
                size: [100, 50, 20]
                relate:
                  +x:
                    - { ref: origin, pos: +x }
                    - { ref: datum, pos: +x }
                  +y: { ref: origin, pos: +y }
                  +z: { ref: origin, pos: +z }
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "multi-ref.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        beam = next(comp for comp in spec.components if comp.id == "beam")
        self.assertEqual(len(beam.relations), 4)

    def test_frame_shorthand_accepts_component_id(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: frame-shorthand
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: host
                kind: reference
                size: [100, 50, 20]
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
              - id: child
                class: IfcBeam
                size: [40, 20, 10]
                material: timber
                relate:
                  +x: { ref: host, pos: +x, frame: host }
                  cy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "frame-shorthand.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        child = next(comp for comp in spec.components if comp.id == "child")
        self.assertEqual(child.relations[0].target.frame, "host")

    def test_lint_catches_unknown_operation_selector(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: lint-op
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: slab
                class: IfcSlab
                size: [100, 100, 10]
                relate:
                  +x-y+z: { ref: origin, pos: +x-y+z }
            operations:
              - type: boolean
                target: missing_component
                subtract: [slab]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "op.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        errors = lint_relationship_spec(spec)
        self.assertTrue(any("unknown selector" in err for err in errors))

    def test_loader_resolves_datums_and_dimension_expressions(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: datums
            dimensions:
              base: 100
              offsets:
                dx: base / 2
                dz: base + 20
            datums:
              anchor:
                type: point
                coordinates: { x: base, y: offsets.dx, z: offsets.dz - 10 }
              planes:
                top:
                  base: { ref: anchor }
                  normal: +z
                  offset: offsets.dx
              bundles:
                grid:
                  origin: { ref: anchor }
                  span:
                    +x: base * 2
                    +y: offsets.dx * 3
                  translate:
                    +z: offsets.dx
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "datums.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)

        dims = spec.dimensions
        self.assertAlmostEqual(dims.lookup("offsets.dx"), 50.0)
        self.assertAlmostEqual(dims.lookup("offsets.dz"), 120.0)
        anchor = spec.datums["anchor"]
        self.assertAlmostEqual(anchor.coordinates["+x"], 100.0)
        self.assertAlmostEqual(anchor.coordinates["+y"], 50.0)
        self.assertAlmostEqual(anchor.coordinates["+z"], 110.0)
        plane = spec.planes["top"]
        self.assertEqual(plane.base, "anchor")
        self.assertEqual(plane.normal, "+z")
        self.assertAlmostEqual(plane.offset, 50.0)
        bundle = spec.bundles["grid"]
        self.assertEqual(bundle.origin, "anchor")
        self.assertAlmostEqual(bundle.span["+x"], 200.0)
        self.assertAlmostEqual(bundle.span["+y"], 150.0)
        self.assertAlmostEqual(bundle.translate["+z"], 50.0)

    def test_loader_rejects_removed_helpers_and_relate_from(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            assemblies: {}
            components:
              - id: base
                kind: reference
                size: [0, 0, 0]
                relate_from: seed
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "removed-helpers.yaml"
            path.write_text(spec_text, encoding="utf-8")
            with self.assertRaises(SchemaError):
                load_relationship_spec(path)

    def test_loader_rejects_relate_with_array(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: relate-array
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [100, 50, 20]
                relate:
                  cx: { ref: origin }
                array:
                  -x: { ref: origin, pos: -x }
                  +x: { ref: origin, pos: +x }
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "relate-array.yaml"
            path.write_text(spec_text, encoding="utf-8")
            with self.assertRaises(SchemaError):
                load_relationship_spec(path)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
