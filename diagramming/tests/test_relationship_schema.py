from __future__ import annotations

import dataclasses
from pathlib import Path
import unittest
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming.relationships import canonical_pos_token, lint_relationship_spec, load_relationship_spec


FIXTURE_DIR = Path(__file__).parent / "fixtures"


class Phase4SchemaTests(unittest.TestCase):
    def test_canonical_pos_token_orders_axes(self) -> None:
        token = canonical_pos_token(["-y", "+z", "+x"])
        self.assertEqual(token, "+x-y+z")

    def test_loads_relationship_spec_and_lints(self) -> None:
        spec_path = FIXTURE_DIR / "relationship_minimal.yaml"
        spec = load_relationship_spec(spec_path)
        self.assertEqual(len(spec.components), 1)
        self.assertIn("frame", spec.bundles)
        errors = lint_relationship_spec(spec)
        self.assertEqual(errors, [])

    def test_lint_catches_unknown_reference(self) -> None:
        spec_path = FIXTURE_DIR / "relationship_minimal.yaml"
        spec = load_relationship_spec(spec_path)
        component = spec.components[0]
        bad_repeat = dataclasses.replace(component.repeat, span_use="datums.bundles.missing.x")  # type: ignore[arg-type]
        bad_component = dataclasses.replace(component, repeat=bad_repeat)
        bad_spec = dataclasses.replace(spec, components=(bad_component,))
        errors = lint_relationship_spec(bad_spec)
        self.assertTrue(errors)
        self.assertIn("unknown target", errors[0])

    def test_checks_block_validates_references(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: lint-check
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
                size: [100, 50]
            checks:
              - align:
                  subject:
                    component: beam
                    pos: +x
                  object:
                    component: missing
                    pos: -x
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "checks.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        errors = lint_relationship_spec(spec)
        self.assertTrue(errors)
        self.assertIn("unknown target", errors[0])

    def test_run_between_orient_is_validated(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: lint-run
            datums:
              start:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
              end:
                type: point
                coordinates:
                  +x: 1000
                  +y: 0
            components:
              - id: runner
                class: IfcBeam
                size: [100, 50]
                relate:
                  - run_between:
                      start_pos: +x
                      end_pos: +x
                      from:
                        datum: datums.start
                        pos: +x
                      to:
                        datum: datums.end
                        pos: +x
                      orient: spin
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        errors = lint_relationship_spec(spec)
        self.assertTrue(errors)
        self.assertIn("orient", errors[0])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
