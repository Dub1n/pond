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
        self.assertEqual(section_polygons[0].views, ("section",))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
