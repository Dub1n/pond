from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming.relationships import ConstraintSolver, RelationshipPlanner, load_relationship_spec


class RelationshipPlannerTests(unittest.TestCase):
    def test_plan_and_section_views_from_solver_output(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: P
            datums:
              origin:
                type: point
                coordinates:
                  +x: 0
                  +y: 0
                  +z: 0
              bundles:
                frame:
                  origin:
                    ref: datums.origin
                  span:
                    +x: 1200
                    +y: 800
              planes:
                top:
                  base:
                    ref: datums.origin
                  normal: +z
                  offset: 50
            components:
              - id: slab
                class: IfcSlab
                size: [1200, 800, 50]
                material: decking
                relate:
                  - flush_bundle:
                      bundle: datums.bundles.frame
                      faces: [+x, -x, +y, -y]
                  - touch_planes:
                      object: datums.planes.top
                      faces: [-z]
            views:
              plan:
                title: Plan
                renders: [svg]
              section:
                title: Section
                plane:
                  axis: y
                  coordinate: 400
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
        self.assertAlmostEqual(slab.shape.centroid.x, 600.0)
        self.assertAlmostEqual(slab.shape.centroid.y, 400.0)
        section_polygons = [feature for feature in section.bundle.polygons if feature.id.startswith("slab@section")]
        self.assertEqual(len(section_polygons), 1)
        self.assertGreater(section_polygons[0].height, 0.0)
        self.assertEqual(section_polygons[0].views, ("section",))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
