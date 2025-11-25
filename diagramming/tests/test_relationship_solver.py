from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming.relationships import ConstraintSolver, load_relationship_spec


class RelationshipSolverTests(unittest.TestCase):
    def test_solver_resolves_flush_and_checks(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: solve
            datums:
              anchor:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
              bundles:
                frame:
                  origin:
                    ref: datums.anchor
                  span:
                    +x: 2000
                    +y: 1000
              planes:
                deck_top:
                  base:
                    ref: datums.anchor
                  normal: +z
                  offset: 50
            components:
              - id: deck_surface
                class: IfcSlab
                size: [2000, 1000, 50]
                material: decking
                relate:
                  - flush_bundle:
                      bundle: datums.bundles.frame
                      faces: [+x, -x, +y, -y]
                  - touch_planes:
                      object: datums.planes.deck_top
                      faces: [-z]
            checks:
              - align:
                  subject:
                    component: deck_surface
                    pos: +x
                  object:
                    bundle: datums.bundles.frame
                    pos: +x
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "solve.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertTrue(result.diagnostics.ok)
        deck = next(comp for comp in result.components if comp.instance_id == "deck_surface")
        self.assertAlmostEqual(deck.transform.position[0], 1000.0)
        self.assertAlmostEqual(deck.transform.position[1], 500.0)
        self.assertAlmostEqual(deck.transform.position[2], 75.0)
        self.assertTrue(any(text.startswith("PASS") for text in result.diagnostics.check_results))

    def test_run_between_generates_positions(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: run
            datums:
              start:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
              end:
                type: point
                coordinates:
                  +x: 900
                  +y: 0
            components:
              - id: runner
                class: IfcBeam
                size: [100, 50, 10]
                material: timber
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
                      count: 3
                      inset:
                        start: 50
                        end: 50
                      orient: along_run
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertTrue(result.diagnostics.ok)
        xs = [comp.transform.position[0] for comp in result.components]
        self.assertEqual(len(xs), 3)
        self.assertAlmostEqual(xs[0], 50.0)
        self.assertAlmostEqual(xs[1], 450.0)
        self.assertAlmostEqual(xs[2], 850.0)
        for comp in result.components:
            self.assertAlmostEqual(comp.transform.rotation[2], 0.0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
