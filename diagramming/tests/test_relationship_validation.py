from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming.relationships import load_relationship_spec, validate_relationship_spec


class RelationshipValidationTests(unittest.TestCase):
    def test_validate_relationship_spec_flags_missing_predefined_type(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: lint
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [400, 100, 50]
                material: timber
                relate:
                  +x+y-x-y: { ref: origin, pos: +x+y-x-y }
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "lint.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        report = validate_relationship_spec(spec)
        self.assertTrue(any("predefined type" in err for err in report.errors))

    def test_validate_relationship_spec_returns_checksum_on_success(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: checksum
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: frame
                kind: reference
                size: [200, 200, 0]
                relate:
                  cxcy: { ref: origin }
              - id: slab
                class: IfcSlab
                size: [200, 200, 20]
                material: decking
                relate:
                  +x+y-x-y: { ref: frame, pos: +x+y-x-y }
                  +z: { ref: origin, pos: +z }
                  -z: { ref: origin, pos: +z, offset: -20 }
                ifc:
                  predefined_type: FLOOR
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "valid.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        report = validate_relationship_spec(spec)
        self.assertFalse(report.errors)
        self.assertIsNotNone(report.mesh_checksum)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
