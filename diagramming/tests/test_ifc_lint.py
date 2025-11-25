from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming.schema import load_spec
from diagramming.schema.ifc_lint import lint_ifc_metadata


class IfcLintTests(unittest.TestCase):
    def test_ifc_class_without_block_fails(self) -> None:
        spec_text = dedent(
            """
            name: lint-missing-ifc
            units: mm
            options:
              A:
                title: IFC lint
                components:
                  - type: rectangle
                    id: beam
                    size: [100, 200]
                    class: IfcBeam
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        errors = lint_ifc_metadata(spec)
        self.assertTrue(errors)
        self.assertIn("IfcBeam", errors[0])

    def test_ifc_block_passes_lint(self) -> None:
        spec_text = dedent(
            """
            name: lint-with-ifc
            units: mm
            options:
              A:
                title: IFC lint pass
                components:
                  - type: rectangle
                    id: slab
                    size: [1000, 500]
                    height: 30
                    class: ifcslab
                    ifc:
                      predefined_type: floor
                      psets:
                        - name: pset_slabcommon
                          props:
                            Reference: "Lint sample"
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "pass.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        errors = lint_ifc_metadata(spec)
        self.assertEqual(errors, [])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
