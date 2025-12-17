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
                  start:
                    +x: { ref: start, pos: +x }
                  end:
                    +x: { ref: end, pos: +x }
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
        self.assertAlmostEqual(xs[0], -50.0)
        self.assertAlmostEqual(xs[1], 950.0)
        for comp in runners:
            self.assertAlmostEqual(comp.transform.rotation[2], 0.0)

    def test_axis_map_targets_explicit_face_when_signs_differ(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: sign-mapping
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: frame
                kind: reference
                size: [1000, 1000, 0]
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
              - id: beam
                class: IfcBeam
                size: [100, 200, 50]
                relate:
                  +x: { ref: frame, pos: -x }
                  cy: { ref: frame }
                  cz: { ref: origin }
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sign.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        beam = next(comp for comp in result.components if comp.instance_id == "beam")
        self.assertAlmostEqual(beam.transform.position[0], -550.0)
        self.assertAlmostEqual(beam.primitive.size[0], 100.0)

    def test_run_between_orients_to_span_direction(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: run-between-direction
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: start
                kind: reference
                size: [0, 0, 0]
                relate:
                  cy: { ref: origin, offset: 0 }
              - id: end
                kind: reference
                size: [0, 0, 0]
                relate:
                  cy: { ref: origin, offset: 1000 }
              - id: runner
                class: IfcBeam
                size: [100, 50, 10]
                relate:
                  cx: { ref: origin }
                  cz: { ref: origin }
                run_between:
                  start:
                    +y: { ref: start, pos: +y }
                  end:
                    +y: { ref: end, pos: +y }
                  count: 1
                  include_seed: true
                  orient: along_run
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "run_dir.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        runner = next(comp for comp in result.components if comp.component.id == "runner")
        orient_x = runner.transform.orientation[0]
        self.assertAlmostEqual(orient_x[0], 0.0, places=6)
        self.assertAlmostEqual(orient_x[1], 1.0, places=6)
        self.assertAlmostEqual(runner.transform.position[1], 475.0)

    def test_run_between_multi_axis_point_anchors_center_on_span_midpoint(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: run-between-point-anchor
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: frame
                kind: reference
                size: [200, 200, 0]
                relate:
                  cxcy: { ref: origin }
              - id: runner
                class: IfcBeam
                size: [282.842712, 10, 10]
                relate:
                  cz: { ref: origin }
                run_between:
                  start:
                    -x+y: { ref: frame, pos: -x+y }
                  end:
                    +x-y: { ref: frame, pos: +x-y }
                  count: 1
                  include_seed: true
                  orient: along_run
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "run_point.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        runner = next(comp for comp in result.components if comp.component.id == "runner")
        self.assertAlmostEqual(runner.transform.position[0], 0.0, places=6)
        self.assertAlmostEqual(runner.transform.position[1], 0.0, places=6)
        orient_x = runner.transform.orientation[0]
        self.assertAlmostEqual(orient_x[0], 0.7071067811865476, places=6)
        self.assertAlmostEqual(orient_x[1], -0.7071067811865476, places=6)

    def test_run_between_axis_maps_infer_size_and_interpolate(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: run-between-size
            components:
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
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: runner
                class: IfcBeam
                size: [null, 50, 10]
                relate:
                  cy: { ref: origin }
                  cz: { ref: origin }
                run_between:
                  start:
                    -x: { ref: start, pos: +x }
                    +x: { ref: start, pos: +x, offset: 200 }
                  end:
                    -x: { ref: end, pos: +x }
                    +x: { ref: end, pos: +x, offset: 200 }
                  count: 2
                  include_seed: true
                  orient: along_run
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "run_size.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        runners = [comp for comp in result.components if comp.component.id == "runner"]
        xs = sorted([comp.transform.position[0] for comp in runners])
        sizes = sorted([comp.primitive.size[0] for comp in runners])
        self.assertEqual(len(runners), 2)
        self.assertAlmostEqual(xs[0], 100.0)
        self.assertAlmostEqual(xs[1], 1100.0)
        self.assertAlmostEqual(sizes[0], 200.0)
        self.assertAlmostEqual(sizes[1], 200.0)

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
