from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

import uuid

import ifcopenshell
import ifcopenshell.guid

from diagramming.relationships import ConstraintSolver, load_relationship_spec
from diagramming.planner.exporters import IfcExporter, ObjExporter, StepExporter
from diagramming.relationships.solver import GUID_NAMESPACE


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

    def test_collision_detection_reports_overlap(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: collide
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
              bundles:
                pad:
                  origin:
                    ref: datums.origin
                  span:
                    +x: 500
                    +y: 500
            components:
              - id: host
                class: IfcSlab
                size: [500, 500, 50]
                material: decking
                relate:
                  - flush_bundle:
                      bundle: datums.bundles.pad
                      faces: [+x, -x, +y, -y]
                  - align:
                      subject:
                        component: host
                        pos: -z
                      object:
                        datum: datums.origin
                        pos: +z
              - id: intruder
                class: IfcMember
                size: [400, 400, 50]
                material: timber
                relate:
                  - flush_bundle:
                      bundle: datums.bundles.pad
                      faces: [+x, -x, +y, -y]
                  - align:
                      subject:
                        component: intruder
                        pos: -z
                      object:
                        datum: datums.origin
                        pos: +z
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "collide.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        errors = [err.message for err in result.diagnostics.errors]
        self.assertTrue(any("collision" in msg for msg in errors))
        self.assertTrue(result.diagnostics.collisions)

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

    def test_relate_from_inherits_relationships(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: relate
            datums:
              anchor:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
              clone_anchor:
                type: point
                coordinates:
                  +x: 500
                  +y: 0
                  +z: 0
            components:
              - id: template
                class: IfcBeam
                size: [200, 100, 50]
                material: timber
                ifc:
                  predefined_type: BEAM
                relate:
                  - align:
                      subject:
                        component: template
                        pos: +x
                      object:
                        datum: datums.anchor
                        pos: +x
                  - align:
                      subject:
                        component: template
                        pos: +y
                      object:
                        datum: datums.anchor
                        pos: +y
                  - align:
                      subject:
                        component: template
                        pos: -z
                      object:
                        datum: datums.anchor
                        pos: +z
              - id: clone
                class: IfcBeam
                size: [200, 100, 50]
                material: timber
                ifc:
                  predefined_type: BEAM
                relate:
                  - relate_from:
                      source: template
                      overrides:
                        datums.anchor: datums.clone_anchor
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "relate.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertTrue(result.diagnostics.ok)
        template = next(comp for comp in result.components if comp.instance_id == "template")
        clone = next(comp for comp in result.components if comp.instance_id == "clone")
        self.assertNotEqual(template.transform.position[0], clone.transform.position[0])
        self.assertAlmostEqual(template.transform.position[1], clone.transform.position[1])
        self.assertAlmostEqual(template.transform.position[2], clone.transform.position[2])
        self.assertGreater(clone.transform.position[0], template.transform.position[0])

    def test_checks_on_fail_can_warn(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: warn
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
            components:
              - id: block
                class: IfcSlab
                size: [100, 100, 50]
                material: decking
                ifc:
                  predefined_type: FLOOR
                relate:
                  - align:
                      subject:
                        component: block
                        pos: +x
                      object:
                        datum: datums.origin
                        pos: +x
                  - align:
                      subject:
                        component: block
                        pos: +y
                      object:
                        datum: datums.origin
                        pos: +y
                  - align:
                      subject:
                        component: block
                        pos: -z
                      object:
                        datum: datums.origin
                        pos: +z
            checks:
              - align:
                  subject:
                    component: block
                    pos: +x
                  object:
                    datum: datums.origin
                    pos: -x
                  gap: 10
                  tolerance: 0.1
                  on_fail: warn
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "warn.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertTrue(result.diagnostics.ok)
        self.assertTrue(result.diagnostics.warnings)
        self.assertTrue(any("check failed" in warning.message for warning in result.diagnostics.warnings))

    def test_linear_bracing_assembly_expands(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: brace
            datums:
              start:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
              end:
                type: point
                coordinates:
                  +x: 1200
                  +y: 0
                  +z: 0
              planes:
                top:
                  base:
                    ref: datums.start
                  normal: +z
                  offset: 100
            components:
              - id: placeholder
                class: IfcSlab
                size: [100, 100, 10]
                material: decking
                ifc:
                  predefined_type: FLOOR
              - use: assembly.linear_bracing
                with:
                  id: brace_span
                  path:
                    start:
                      component: datums.start
                      face: +x
                    end:
                      component: datums.end
                      face: +x
                  attach:
                    face: +z
                    plane: datums.planes.top
                  size: [1200, 30, 5]
                  material: hardware
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bracing.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        brace_ids = [comp.instance_id for comp in result.components if comp.component.id == "brace_span"]
        self.assertTrue(brace_ids)
        brace = next(comp for comp in result.components if comp.component.id == "brace_span")
        self.assertAlmostEqual(brace.transform.position[1], 0.0)
        self.assertAlmostEqual(brace.transform.position[2], 97.5, delta=1e-3)

    def test_ifc_export_from_relationship_primitives(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: ifc
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
            components:
              - id: slab
                class: IfcSlab
                size: [2000, 1000, 50]
                material: decking
                ifc:
                  predefined_type: FLOOR
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "ifc.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
            solver = ConstraintSolver(spec)
            result = solver.solve()
            exporter = IfcExporter()
            out_path = Path(tmp) / "model.ifc"
            exporter.export(result.primitives, out_path)
            self.assertTrue(out_path.exists())
            import ifcopenshell  # local import to avoid test import dependency when unused

            model = ifcopenshell.open(out_path)
            self.assertTrue(model.by_type("IfcSlab"))

    def test_neutral_primitive_carries_cadquery_footprint(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: footprint
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
            components:
              - id: block
                class: IfcMember
                size: [500, 200, 100]
                material: timber
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "footprint.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertTrue(result.primitives)
        primitive = result.primitives[0]
        self.assertIsNotNone(primitive.solid)
        self.assertIsNotNone(primitive.footprint)
        if primitive.footprint:
            self.assertGreater(primitive.footprint.area, 0.0)
            self.assertAlmostEqual(primitive.footprint.area, 500.0 * 200.0, delta=1e-3)

    def test_ifc_export_preserves_stable_guid_and_body_context(self) -> None:
        option = "guid"
        component_id = "slab"
        spec_text = dedent(
            f"""
            schema: pond-relationship-test
            info:
              option: {option}
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
            components:
              - id: {component_id}
                class: IfcSlab
                size: [1000, 500, 50]
                material: decking
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "guid.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
            solver = ConstraintSolver(spec)
            result = solver.solve()
            exporter = IfcExporter()
            out_path = Path(tmp) / "model.ifc"
            exporter.export(result.primitives, out_path)
            model = ifcopenshell.open(out_path)
        slabs = model.by_type("IfcSlab")
        self.assertEqual(len(slabs), 1)
        slab = slabs[0]
        expected_guid = ifcopenshell.guid.compress(str(uuid.UUID(result.primitives[0].guid)))
        self.assertEqual(slab.GlobalId, expected_guid)
        self.assertEqual(slab.Tag, result.primitives[0].guid)
        body_contexts = [
            ctx for ctx in model.by_type("IfcGeometricRepresentationSubContext") if ctx.ContextIdentifier == "Body"
        ]
        self.assertTrue(body_contexts)

    def test_ifc_reference_view_features(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: reference
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
            components:
              - id: slab
                class: IfcSlab
                size: [1000, 800, 40]
                material: decking
                relate:
                  - align:
                      subject:
                        component: slab
                        pos: -z
                      object:
                        datum: datums.origin
                        pos: +z
                voids:
                  - opening
              - id: opening
                class: IfcMember
                size: [200, 200, 40]
                material: timber
                relate:
                  - align:
                      subject:
                        component: opening
                        pos: +x
                      object:
                        component: slab
                        pos: +x
                  - align:
                      subject:
                        component: opening
                        pos: +y
                      object:
                        component: slab
                        pos: +y
                  - align:
                      subject:
                        component: opening
                        pos: -z
                      object:
                        component: slab
                        pos: +z
              - id: joist
                class: IfcBeam
                size: [1000, 60, 100]
                material: joist
                relate:
                  - align:
                      subject:
                        component: joist
                        pos: -z
                      object:
                        component: slab
                        pos: +z
                  - align:
                      subject:
                        component: joist
                        pos: -x
                      object:
                        datum: datums.origin
                        pos: +x
                repeat:
                  axis: +y
                  pitch: 300
                  count: 2
                  include_seed: true
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "reference.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
            solver = ConstraintSolver(spec)
            result = solver.solve()
            exporter = IfcExporter()
            out_path = Path(tmp) / "model.ifc"
            exporter.export(result.primitives, out_path)
            model = ifcopenshell.open(out_path)

        project = model.by_type("IfcProject")[0]
        units = list(project.UnitsInContext.Units)
        length_units = [u for u in units if getattr(u, "UnitType", "") == "LENGTHUNIT"]
        self.assertTrue(any(getattr(u, "Prefix", "").upper() == "MILLI" for u in length_units))
        angle_units = [u for u in units if getattr(u, "UnitType", "") == "PLANEANGLEUNIT"]
        self.assertTrue(any(getattr(u, "Name", "").lower() == "degree" for u in angle_units))

        contexts = {ctx.ContextIdentifier for ctx in model.by_type("IfcGeometricRepresentationSubContext")}
        self.assertIn("Axis", contexts)
        self.assertIn("Body", contexts)

        beams = model.by_type("IfcBeam")
        self.assertEqual(len(beams), 2)
        beam_types = model.by_type("IfcBeamType")
        self.assertTrue(beam_types)
        maps = list(beam_types[0].RepresentationMaps or [])
        self.assertTrue(maps)
        beam_type_body_reps = [
            rep for rep in (rm.MappedRepresentation for rm in maps if rm.MappedRepresentation)
            if rep and rep.ContextOfItems and rep.ContextOfItems.ContextIdentifier == "Body"
        ]
        self.assertTrue(
            any(any(item.is_a("IfcExtrudedAreaSolid") for item in rep.Items or []) for rep in beam_type_body_reps)
        )

        first_beam_reps = beams[0].Representation.Representations or []
        self.assertTrue(any(rep.ContextOfItems.ContextIdentifier == "Axis" for rep in first_beam_reps))
        self.assertTrue(any(rep.RepresentationType == "MappedRepresentation" for rep in first_beam_reps))
        self.assertTrue(
            any(
                getattr(rel.RelatingMaterial, "is_a", lambda *_: False)("IfcMaterialProfileSetUsage")
                for rel in beams[0].HasAssociations or []
            )
        )

        slab = model.by_type("IfcSlab")[0]
        self.assertTrue(
            any(
                getattr(rel.RelatingMaterial, "is_a", lambda *_: False)("IfcMaterialLayerSetUsage")
                for rel in slab.HasAssociations or []
            )
        )

        rel_voids = model.by_type("IfcRelVoidsElement")
        self.assertTrue(rel_voids)
        self.assertEqual(rel_voids[0].RelatingBuildingElement, slab)
        self.assertTrue(rel_voids[0].RelatedOpeningElement.is_a("IfcOpeningElement"))

        connections = [rel for rel in model.by_type("IfcRelConnectsElements") if rel.ConnectionGeometry]
        self.assertTrue(connections)
        self.assertTrue(
            any(
                rel.ConnectionGeometry.is_a("IfcConnectionSurfaceGeometry")
                or rel.ConnectionGeometry.is_a("IfcConnectionCurveGeometry")
                for rel in connections
            )
        )

    def test_solver_supports_wedge_and_sweep_profiles(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: profiles
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
              bundles:
                pad:
                  origin:
                    ref: datums.origin
                  span:
                    +x: 800
                    +y: 400
              planes:
                sweep_base:
                  base:
                    ref: datums.origin
                  normal: +z
                  offset: 240
            components:
              - id: wedge
                class: IfcMember
                profile: wedge
                profile_params:
                  slope: 40
                size: [800, 400, 200]
                material: timber
                relate:
                  - flush_bundle:
                      bundle: datums.bundles.pad
                      faces: [+x, -x, +y, -y]
                  - align:
                      subject:
                        component: wedge
                        pos: -z
                      object:
                        datum: datums.origin
                        pos: +z
              - id: sweep
                class: IfcMember
                profile: sweep
                profile_params:
                  points:
                    - [-100, -50]
                    - [100, -50]
                    - [100, 50]
                    - [0, 120]
                    - [-100, 50]
                size: [600, 200, 120]
                material: timber
                relate:
                  - align:
                      subject:
                        component: sweep
                        pos: +x
                      object:
                        bundle: datums.bundles.pad
                        pos: +x
                  - align:
                      subject:
                        component: sweep
                        pos: +y
                      object:
                        bundle: datums.bundles.pad
                        pos: +y
                  - align:
                      subject:
                        component: sweep
                        pos: -z
                      object:
                        datum: datums.planes.sweep_base
                        pos: +z
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "profiles.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        result = solver.solve()
        self.assertTrue(result.diagnostics.ok)
        wedge = next(prim for prim in result.primitives if prim.id == "wedge")
        sweep = next(prim for prim in result.primitives if prim.id == "sweep")
        self.assertEqual(wedge.profile, "wedge")
        self.assertEqual(sweep.profile, "sweep")
        self.assertIsNotNone(wedge.solid)
        self.assertIsNotNone(sweep.solid)
        self.assertIsNotNone(wedge.footprint)
        self.assertIsNotNone(sweep.footprint)
        self.assertIn("profile", wedge.metadata)
        self.assertIn("profile_params", sweep.metadata)

    def test_step_and_obj_exports_from_primitives(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: exports
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
            components:
              - id: block
                class: IfcMember
                size: [500, 200, 100]
                material: timber
                relate:
                  - align:
                      subject:
                        component: block
                        pos: +x
                      object:
                        datum: datums.origin
                        pos: +x
                  - align:
                      subject:
                        component: block
                        pos: +y
                      object:
                        datum: datums.origin
                        pos: +y
                  - align:
                      subject:
                        component: block
                        pos: -z
                      object:
                        datum: datums.origin
                        pos: +z
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "exports.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
            solver = ConstraintSolver(spec)
            result = solver.solve()
            step_path = Path(tmp) / "model.step"
            obj_path = Path(tmp) / "model.obj"
            StepExporter().export(result.primitives, step_path)
            ObjExporter().export(result.primitives, obj_path)
            self.assertTrue(step_path.exists())
            self.assertTrue(obj_path.exists())
            self.assertGreater(step_path.stat().st_size, 0)
            self.assertGreater(obj_path.stat().st_size, 0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
