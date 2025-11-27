from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
import unittest

from diagramming.relationships import ConstraintSolver, load_relationship_spec


class RelationshipSolverTests(unittest.TestCase):
    def test_size_is_inferred_from_axis_pairs(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: solve-infer
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: frame
                kind: reference
                size: [1000, 1000, 0]
                relate:
                  cxcy: { ref: origin }
              - id: top
                kind: reference
                size: [1, 1, 0]
                relate:
                  cz: { ref: origin, offset: 100 }
              - id: bottom
                kind: reference
                size: [1, 1, 0]
                relate:
                  cz: { ref: origin }
              - id: opening
                class: IfcOpeningElement
                relate:
                  +x-x:
                    ref: frame
                    pos: +x-x
                    offset:
                      +x: -50
                      -x: 50
                  +y-y:
                    ref: frame
                    pos: +y-y
                    offset:
                      +y: -50
                      -y: 50
                  +z: { ref: top, pos: +z }
                  -z: { ref: bottom, pos: +z }
                ifc:
                  predefined_type: OPENING
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "infer.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        opening = next(comp for comp in result.components if comp.instance_id == "opening")
        self.assertAlmostEqual(opening.primitive.size[0], 900.0)
        self.assertAlmostEqual(opening.primitive.size[1], 900.0)
        self.assertAlmostEqual(opening.transform.position[2], 50.0)

    def test_run_between_generates_along_run_orientation(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: run-between
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: start
                kind: reference
                size: [0, 0, 0]
                relate:
                  cx: { ref: origin, offset: 0 }
              - id: end
                kind: reference
                size: [0, 0, 0]
                relate:
                  cx: { ref: origin, offset: 1000 }
              - id: runner
                class: IfcBeam
                size: [100, 50, 10]
                relate:
                  cy: { ref: origin }
                  cz: { ref: origin }
                run_between:
                  start_pos: +x
                  end_pos: +x
                  from: { ref: start, pos: +x }
                  to: { ref: end, pos: +x }
                  count: 2
                  include_seed: true
                  orient: along_run
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        runners = [comp for comp in result.components if comp.component.id == "runner"]
        xs = sorted([comp.transform.position[0] for comp in runners])
        self.assertEqual(len(runners), 2)
        self.assertAlmostEqual(xs[0], 0.0)
        self.assertAlmostEqual(xs[1], 1000.0)
        for comp in runners:
            self.assertAlmostEqual(comp.transform.rotation[2], 0.0)

    def test_boolean_operation_aggregates_clone_selectors(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: boolean-selectors
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: slab
                class: IfcSlab
                size: [400, 400, 20]
                material: decking
                relate:
                  cxcy: { ref: origin }
                  +z: { ref: origin, pos: +z }
                  -z: { ref: origin, pos: +z, offset: -20 }
                ifc:
                  predefined_type: FLOOR
              - id: pad_a
                class: IfcFooting
                size: [100, 100, 50]
                material: pad
                relate:
                  cx: { ref: origin, offset: -100 }
                  cy: { ref: origin }
                  -z: { ref: origin, pos: +z }
                ifc:
                  predefined_type: PAD_FOOTING
            operations:
              - type: rotate
                about: { ref: origin, axis: +z }
                count: 2
                include_seed: true
                id_map:
                  pad_a: [pad_a, pad_b]
              - type: boolean
                target: slab
                subtract: [pad_a]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "boolean.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        slab = next(comp for comp in result.components if comp.instance_id == "slab")
        self.assertIn("pad_a", slab.primitive.voids)
        self.assertIn("pad_b", slab.primitive.voids)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
