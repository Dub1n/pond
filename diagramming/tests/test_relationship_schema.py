from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
import unittest

from diagramming.relationships import canonical_pos_token, lint_relationship_spec, load_relationship_spec


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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
