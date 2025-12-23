from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming.relationships import ConstraintSolver, RelationshipPlanner, load_relationship_spec


class RelationshipPlannerTests(unittest.TestCase):
    def test_plan_and_section_views_render_from_axis_map(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: planner
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: frame
                kind: reference
                size: [1200, 800, 0]
                relate:
                  cxcy: { ref: origin }
              - id: slab
                class: IfcSlab
                size: [1200, 800, 50]
                material: decking
                views: [plan, section]
                relate:
                  +x+y-x-y: { ref: frame, pos: +x+y-x-y }
                  +z: { ref: origin, pos: +z }
                  -z: { ref: origin, pos: +z, offset: -50 }
                ifc:
                  predefined_type: FLOOR
            views:
              plan:
                title: Plan
                renders: [svg]
              section:
                title: Section
                plane:
                  axis: y
                  coordinate: 0
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "planner.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        solved = solver.solve()
        self.assertTrue(solved.diagnostics.ok)

        planner = RelationshipPlanner(spec, solved)
        planned_views = planner.plan()
        plan = next(view for view in planned_views if view.view == "plan")
        section = next(view for view in planned_views if view.view == "section")

        slab = next(feature for feature in plan.bundle.polygons if feature.id == "slab")
        self.assertAlmostEqual(slab.shape.centroid.x, 0.0, delta=1e-3)
        self.assertAlmostEqual(slab.shape.centroid.y, 0.0, delta=1e-3)
        section_polygons = [feature for feature in section.bundle.polygons if feature.id.startswith("slab@section")]
        self.assertTrue(section_polygons)
        self.assertIn("section", section_polygons[0].views)

    def test_show_all_views_includes_untagged_section(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: planner-all
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: slab
                class: IfcSlab
                size: [1200, 800, 50]
                material: decking
                relate:
                  cxcy: { ref: origin }
                  -z: { ref: origin }
            views:
              plan:
                title: Plan
                renders: [svg]
              section:
                title: Section
                plane:
                  axis: y
                  coordinate: 0
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "planner-all.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        solved = solver.solve()
        self.assertTrue(solved.diagnostics.ok)

        planner = RelationshipPlanner(spec, solved, show_all_views=True)
        planned_views = planner.plan()
        section = next(view for view in planned_views if view.view == "section")
        section_polygons = [feature for feature in section.bundle.polygons if feature.id.startswith("slab@section")]
        self.assertTrue(section_polygons)

    def test_boolean_cutouts_follow_placements(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: planner-voids
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: slab
                class: IfcSlab
                size: [200, 200, 40]
                material: decking
                place:
                  - id: slab_a
                    cx: { ref: origin, offset: -300 }
                    cy: { ref: origin }
                    cz: { ref: origin }
                  - id: slab_b
                    cx: { ref: origin, offset: 300 }
                    cy: { ref: origin }
                    cz: { ref: origin }
                ifc:
                  predefined_type: FLOOR
              - id: void
                class: IfcOpeningElement
                size: [80, 80, 40]
                relate:
                  cxcy: { ref: slab, pos: cxcy }
                  cz: { ref: slab, pos: cz }
                ifc:
                  predefined_type: OPENING
            operations:
              - type: boolean
                target: slab
                subtract: [void]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "planner-voids.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        solved = solver.solve()
        self.assertTrue(solved.diagnostics.ok)

        planner = RelationshipPlanner(spec, solved)
        planned_views = planner.plan()
        plan = next(view for view in planned_views if view.view == "plan")
        slab_features = [feature for feature in plan.bundle.polygons if feature.id.startswith("slab")]
        self.assertEqual(len(slab_features), 2)
        hole_x = []
        for feature in slab_features:
            shape = feature.shape
            self.assertTrue(shape.interiors)
            hole_x.append(round(shape.interiors[0].centroid.x, 3))
        self.assertIn(-300.0, hole_x)
        self.assertIn(300.0, hole_x)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
