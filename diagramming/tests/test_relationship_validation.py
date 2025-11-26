from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming import DiagramPlanner
from diagramming.relationships import (
    dual_render_compare,
    load_relationship_spec,
    relationship_bundle,
    validate_relationship_spec,
)
from diagramming.schema import load_spec


FIXTURE_DIR = Path(__file__).parent / "fixtures"


class RelationshipValidationTests(unittest.TestCase):
    def test_validate_relationship_spec_flags_missing_predefined_type(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: lint
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
            components:
              - id: beam
                class: IfcBeam
                size: [400, 100, 50]
                material: timber
                ifc: {}
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "lint.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        report = validate_relationship_spec(spec)
        self.assertTrue(any("predefined type" in err for err in report.errors))

    def test_dual_render_harness_matches_legacy_plan(self) -> None:
        relationship_spec = load_relationship_spec(FIXTURE_DIR / "relationship_dual.yaml")
        legacy_spec = load_spec(FIXTURE_DIR / "legacy_dual.yaml")

        relationship_report = validate_relationship_spec(relationship_spec)
        self.assertFalse(relationship_report.errors)

        rel_bundle = relationship_bundle(relationship_spec)
        legacy_bundle = DiagramPlanner(legacy_spec).plan("A", "plan").bundle
        diff = dual_render_compare(rel_bundle, legacy_bundle)

        self.assertTrue(diff.match)
        self.assertLess(diff.area_delta, 1e-6)
        second_report = validate_relationship_spec(relationship_spec)
        self.assertEqual(relationship_report.mesh_checksum, second_report.mesh_checksum)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
