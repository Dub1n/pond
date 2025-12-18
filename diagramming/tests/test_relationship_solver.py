from __future__ import annotations

import os
from pathlib import Path
from unittest import mock
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

    def test_frame_local_axes_follow_orientation(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: frame-local
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: frame
                kind: reference
                size: [100, 80, 40]
                metadata:
                  _rotation_z: 180
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
              - id: block
                class: IfcMember
                size: [20, 20, 20]
                relate:
                  +x: { ref: frame, pos: +x, frame: local }
                  cy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: MEMBER
              - id: flush_block
                class: IfcMember
                size: [null, null, null]
                relate:
                  flush:
                    ref: frame
                    frame: local
                ifc:
                  predefined_type: MEMBER
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "frame-local.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        block = next(comp for comp in result.components if comp.instance_id == "block")
        flush_block = next(comp for comp in result.components if comp.instance_id == "flush_block")

        self.assertAlmostEqual(block.transform.position[0], -60.0)
        self.assertAlmostEqual(block.transform.position[1], 0.0)
        self.assertAlmostEqual(block.transform.position[2], 0.0)

        self.assertAlmostEqual(flush_block.transform.position[0], 0.0)
        self.assertAlmostEqual(flush_block.transform.position[1], 0.0)
        self.assertAlmostEqual(flush_block.transform.position[2], 0.0)
        self.assertAlmostEqual(flush_block.primitive.size[0], 100.0)
        self.assertAlmostEqual(flush_block.primitive.size[1], 80.0)
        self.assertAlmostEqual(flush_block.primitive.size[2], 40.0)

    def test_array_generates_along_run_orientation(self) -> None:
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
                array:
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

    def test_array_orients_to_span_direction(self) -> None:
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
                array:
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

    def test_array_multi_axis_point_anchors_center_on_span_midpoint(self) -> None:
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
                array:
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

    def test_array_axis_maps_infer_size_and_interpolate(self) -> None:
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
                array:
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

    def test_run_between_alias_is_preserved(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: run-between-alias
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: start
                kind: reference
                size: [0, 0, 0]
                relate:
                  cx: { ref: origin, offset: -200 }
              - id: end
                kind: reference
                size: [0, 0, 0]
                relate:
                  cx: { ref: origin, offset: 200 }
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
            path = Path(tmp) / "run-between-alias.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        runners = [comp for comp in result.components if comp.component.id == "runner"]
        self.assertEqual(len(runners), 2)

    def test_array_count_guardrail_warns_on_single_span(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: array-guardrail
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: start
                kind: reference
                size: [0, 0, 0]
                relate:
                  cx: { ref: origin, offset: -100 }
              - id: end
                kind: reference
                size: [0, 0, 0]
                relate:
                  cx: { ref: origin, offset: 100 }
              - id: runner
                class: IfcBeam
                size: [50, 20, 10]
                relate:
                  cy: { ref: origin }
                  cz: { ref: origin }
                array:
                  start:
                    +x: { ref: start, pos: +x }
                  end:
                    +x: { ref: end, pos: +x }
                  count: 1
                  include_seed: true
                  orient: along_run
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "array-guardrail.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        runners = [comp for comp in result.components if comp.component.id == "runner"]
        warning_texts = [warning.message for warning in result.diagnostics.warnings]
        self.assertEqual(len(runners), 1)
        self.assertTrue(any("count should be >= 2" in msg for msg in warning_texts))

    def test_rotate_clones_preserve_ifc_metadata(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: rotate-metadata
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [100, 50, 20]
                material: timber
                relate:
                  cxcy: { ref: origin }
                ifc:
                  predefined_type: BEAM
            operations:
              - type: rotate
                about: { ref: origin, axis: +z }
                count: 2
                include_seed: true
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "rotate-meta.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        clone = next(comp for comp in result.components if comp.instance_id == "beam_rot1")
        self.assertEqual(clone.primitive.material, "timber")
        self.assertEqual(clone.primitive.metadata.get("material"), "timber")
        self.assertEqual(clone.primitive.ifc.get("predefined_type"), "BEAM")

    def test_footing_collisions_are_ignored(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: footing-collision
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: footing
                class: IfcFooting
                size: [100, 100, 50]
                material: pad
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: PAD_FOOTING
              - id: beam_a
                class: IfcBeam
                size: [100, 100, 50]
                material: timber
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: BEAM
              - id: beam_b
                class: IfcBeam
                size: [100, 100, 50]
                material: timber
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "collision.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        collision_pairs = {(a, b) for a, b, _ in result.diagnostics.collisions}
        self.assertIn(("beam_a", "beam_b"), collision_pairs)
        self.assertFalse(any("footing" in " ".join(pair) for pair in collision_pairs))

    def test_fail_on_warn_upgrades_collision_warning(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: collision-warn
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam_a
                class: IfcBeam
                size: [100, 100, 50]
                material: timber
                relate:
                  cxcy: { ref: origin }
                ifc:
                  predefined_type: BEAM
              - id: beam_b
                class: IfcBeam
                size: [100, 100, 50]
                material: timber
                relate:
                  cxcy: { ref: origin }
                ifc:
                  predefined_type: BEAM
            """
        )
        env = os.environ.copy()
        env["DIAGRAM_RELATIONSHIPS_COLLISIONS"] = "warn"
        env["DIAGRAM_RELATIONSHIPS_FAIL_ON_WARN"] = "1"
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "collision-warn.yaml"
            path.write_text(spec_text, encoding="utf-8")
            with mock.patch.dict(os.environ, env, clear=True):
                spec = load_relationship_spec(path)
                solver = ConstraintSolver(spec)
                result = solver.solve()
        self.assertTrue(any("collision" in err.message for err in result.diagnostics.errors))

    def test_mirror_operation_reflects_position_and_orientation(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: mirror-basic
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [100, 50, 10]
                metadata:
                  _rotation_z: 90
                relate:
                  cx: { ref: origin, offset: 200 }
                  cy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: BEAM
            operations:
              - type: mirror
                targets: [beam]
                plane:
                  axis: x
                  coordinate: 0
                include_seed: true
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "mirror.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        beams = {comp.instance_id: comp for comp in result.components if comp.component.id == "beam"}
        mirrored = beams.get("beam_mirrored")
        self.assertIsNotNone(mirrored)
        assert mirrored is not None
        self.assertAlmostEqual(mirrored.transform.position[0], -200.0)
        self.assertAlmostEqual(mirrored.transform.position[1], 0.0)
        x_axis = mirrored.transform.orientation[0]
        y_axis = mirrored.transform.orientation[1]
        z_axis = mirrored.transform.orientation[2]
        cross = (
            x_axis[1] * y_axis[2] - x_axis[2] * y_axis[1],
            x_axis[2] * y_axis[0] - x_axis[0] * y_axis[2],
            x_axis[0] * y_axis[1] - x_axis[1] * y_axis[0],
        )
        handedness = cross[0] * z_axis[0] + cross[1] * z_axis[1] + cross[2] * z_axis[2]
        self.assertGreater(handedness, 0.9)

    def test_mirror_operation_skips_seeds_when_requested(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: mirror-seed
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [100, 50, 10]
                relate:
                  cx: { ref: origin, offset: 150 }
                  cy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: BEAM
            operations:
              - type: mirror
                targets: [beam]
                plane:
                  axis: x
                  coordinate: 0
                include_seed: false
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "mirror-seed.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        beams = [comp for comp in result.components if comp.component.id == "beam"]
        mirrored = [comp for comp in beams if comp.instance_id.endswith("_mirrored")]
        self.assertEqual(len(mirrored), 0)

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

    def test_under_constrained_axes_warn_and_report_dof(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: dof-warn
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: block
                class: IfcBeam
                size: [100, 50, 25]
                relate:
                  cz: { ref: origin }
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "dof-warn.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        warning_texts = [warning.message for warning in result.diagnostics.warnings]
        self.assertTrue(any("under-constrained on axis x" in msg for msg in warning_texts))
        self.assertTrue(any("under-constrained on axis y" in msg for msg in warning_texts))
        dof = result.diagnostics.degrees_of_freedom.get("block", 0)
        self.assertGreaterEqual(dof, 2)

    def test_checks_honor_tolerance_and_on_fail(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: check-tolerance
            datums:
              offset_ref:
                type: point
                coordinates: { x: 10, y: 10 }
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
            checks:
              +x:
                ref: offset_ref
                tolerance: 5
                on_fail: warn
              +y:
                ref: offset_ref
                pos: +y
                tolerance: 1
                on_fail: error
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "check-tolerance.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        warning_texts = [warning.message for warning in result.diagnostics.warnings]
        error_texts = [error.message for error in result.diagnostics.errors]
        self.assertTrue(any("tolerance" in msg and "delta" in msg for msg in warning_texts))
        self.assertTrue(any("axis y" in msg for msg in error_texts))

    def test_rotate_id_map_prefers_seed_and_carries_boolean_voids(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: rotate-seed-voids
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: host
                class: IfcSlab
                size: [200, 200, 20]
                material: decking
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: FLOOR
              - id: cutter
                class: IfcOpeningElement
                size: [50, 50, 20]
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                place:
                  - id: cut_seed
                    cxcy: { ref: origin }
                ifc:
                  predefined_type: OPENING
            operations:
              - type: rotate
                about: { ref: origin, axis: +z }
                count: 2
                include_seed: true
                targets: [cutter]
                id_map:
                  cut_seed: [cut_seed, cut_seed_rot]
                  cutter: [cutter_a, cutter_b]
              - type: boolean
                target: host
                subtract: [cutter]
              - type: rotate
                about: { ref: origin, axis: +z }
                count: 2
                include_seed: true
                targets: [host]
                id_map:
                  host: [host_seed, host_clone]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "rotate-seed-voids.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        ids = {comp.instance_id for comp in result.components}
        self.assertIn("cut_seed_rot", ids)
        host_clone = next(comp for comp in result.components if comp.instance_id == "host_clone")
        self.assertIn("cut_seed", host_clone.primitive.voids)
        self.assertIn("cut_seed_rot", host_clone.primitive.voids)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
