from __future__ import annotations

import dataclasses
from pathlib import Path
import unittest

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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
