from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
import unittest

from diagramming.relationships import (
    BooleanOperation,
    MirrorOperation,
    RotateOperation,
    SchemaError,
    TranslateOperation,
    canonical_pos_token,
    lint_relationship_spec,
    load_relationship_spec,
)


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

    def test_rotate_operation_parses_fields(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: op-rotate
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
            operations:
              - type: rotate
                targets: [origin]
                about: { ref: origin, axis: -y }
                count: 3
                include_seed: true
                id_map:
                  origin: [origin, origin_b, origin_c]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "op-rotate.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        self.assertEqual(len(spec.operations), 1)
        op = spec.operations[0]
        self.assertIsInstance(op, RotateOperation)
        assert isinstance(op, RotateOperation)
        self.assertEqual(op.about, "origin")
        self.assertEqual(op.axis, "-y")
        self.assertEqual(op.count, 3)
        self.assertTrue(op.include_seed)
        self.assertEqual(op.id_map["origin"][1], "origin_b")

    def test_mirror_operation_parses_normal_and_point(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: op-mirror-normal
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
            operations:
              - type: mirror
                targets: [origin]
                plane:
                  normal: [1, -1, 0]
                  point: [0, 0, 0]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "op-mirror-normal.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        op = spec.operations[0]
        self.assertIsInstance(op, MirrorOperation)
        assert isinstance(op, MirrorOperation)
        self.assertEqual(op.normal, (1.0, -1.0, 0.0))
        self.assertEqual(op.point, (0.0, 0.0, 0.0))

    def test_mirror_operation_axis_sugar_expands(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: op-mirror-axis
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
            operations:
              - type: mirror
                targets: [origin]
                plane:
                  axis: -x
                  coordinate: 50
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "op-mirror-axis.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        op = spec.operations[0]
        self.assertIsInstance(op, MirrorOperation)
        assert isinstance(op, MirrorOperation)
        self.assertEqual(op.normal, (-1.0, 0.0, 0.0))
        self.assertEqual(op.point, (50.0, 0.0, 0.0))

    def test_mirror_operation_rejects_mixed_plane_fields(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: op-mirror-mixed
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
            operations:
              - type: mirror
                targets: [origin]
                plane:
                  axis: x
                  coordinate: 0
                  normal: [1, 0, 0]
                  point: [0, 0, 0]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "op-mirror-mixed.yaml"
            path.write_text(spec_text, encoding="utf-8")
            with self.assertRaises(SchemaError):
                load_relationship_spec(path)

    def test_translate_operation_parses_vector(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: op-translate
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
            operations:
              - type: translate
                targets: [origin]
                vector: { x: 1, y: -2, z: 3 }
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "op-translate.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        op = spec.operations[0]
        self.assertIsInstance(op, TranslateOperation)
        assert isinstance(op, TranslateOperation)
        self.assertEqual(op.vector, (1.0, -2.0, 3.0))

    def test_boolean_operation_parses_targets(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: op-boolean
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: slab
                class: IfcSlab
                size: [100, 100, 10]
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: FLOOR
            operations:
              - type: boolean
                target: slab
                subtract: [origin]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "op-boolean.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        op = spec.operations[0]
        self.assertIsInstance(op, BooleanOperation)
        assert isinstance(op, BooleanOperation)
        self.assertEqual(op.target, "slab")
        self.assertEqual(op.subtract, ("origin",))

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
