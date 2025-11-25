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

    def test_under_constrained_axes_reported(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: under
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
            components:
              - id: floating
                class: IfcBeam
                size: [100, 50, 25]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "under.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertFalse(result.diagnostics.ok)
        self.assertIn("floating", result.diagnostics.degrees_of_freedom)
        errors = [err.message for err in result.diagnostics.errors]
        self.assertTrue(any("under-constrained" in msg for msg in errors))

    def test_over_constrained_axis_reports_error(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: over
            datums:
              left:
                type: point
                coordinates:
                  +x: 0
              right:
                type: point
                coordinates:
                  +x: 1000
            components:
              - id: beam
                class: IfcBeam
                size: [200, 100, 50]
                relate:
                  - align:
                      subject:
                        component: beam
                        pos: +x
                      object:
                        datum: datums.left
                        pos: +x
                      tolerance: 0.1
                  - align:
                      subject:
                        component: beam
                        pos: +x
                      object:
                        datum: datums.right
                        pos: +x
                      tolerance: 0.1
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "over.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertFalse(result.diagnostics.ok)
        errors = [err.message for err in result.diagnostics.errors]
        self.assertTrue(any("over-constrained" in msg for msg in errors))

    def test_run_between_missing_axis_reports_error_and_graph(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: graph
            datums:
              start:
                type: point
                coordinates:
                  +x: 0
              end:
                type: point
                coordinates:
                  +x: 500
            components:
              - id: runner
                class: IfcBeam
                size: [100, 50, 10]
                relate:
                  - run_between:
                      start_pos: +z
                      end_pos: +z
                      from:
                        datum: datums.start
                        pos: +z
                      to:
                        datum: datums.end
                        pos: +z
                      count: 2
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "graph.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertFalse(result.diagnostics.ok)
        errors = [err.message for err in result.diagnostics.errors]
        self.assertTrue(any("run_between references unknown target" in msg for msg in errors))
        self.assertIn("runner", result.diagnostics.constraint_graph)
        graph_targets = result.diagnostics.constraint_graph["runner"]
        self.assertTrue(any("datums.start" in target for target in graph_targets))
        self.assertTrue(any("datums.end" in target for target in graph_targets))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
