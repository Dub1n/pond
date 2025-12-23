import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming.planner.bundle import GeometryBundle, PolygonFeature
from diagramming.relationships import ConstraintSolver, RelationshipPlanner, load_relationship_spec
from diagramming.renderers import SvgRenderer


class RendererTests(unittest.TestCase):
    def _plan_bundle(self) -> GeometryBundle:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: render
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: deck
                class: IfcSlab
                size: [400, 300, 40]
                material: decking
                label: "Deck"
                label_id: "D"
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: FLOOR
            views:
              plan:
                title: Plan
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "renderer.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        solver = ConstraintSolver(spec)
        solved = solver.solve()
        self.assertTrue(solved.diagnostics.ok)
        planner = RelationshipPlanner(spec, solved)
        planned = next(view for view in planner.plan() if view.view == "plan")
        return planned.bundle

    def test_svg_renderer_outputs_accessible_markup(self) -> None:
        bundle = self._plan_bundle()
        renderer = SvgRenderer()
        svg_text = renderer.render(bundle, aria_label="Option plan", title="Option plan")

        self.assertIn("aria-label=\"Option plan\"", svg_text)
        self.assertIn("<path", svg_text)
        self.assertRegex(svg_text, r"Legend")
        self.assertRegex(svg_text, r'width="[0-9.]+"')
        self.assertNotIn('width="100%"', svg_text)
        self.assertIn('fill="#ffffff"', svg_text)

    def test_layers_render_in_z_order(self) -> None:
        bundle = GeometryBundle(view="plan", scale=1.0, pad=0.0)
        lower = PolygonFeature(
            id="lower",
            outer=[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)],
            height=1.0,
            elevation=0.0,
        )
        upper = PolygonFeature(
            id="upper",
            outer=[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)],
            height=1.0,
            elevation=2.0,
        )
        bundle.add_polygon(lower)
        bundle.add_polygon(upper)
        bundle.build_legend()

        renderer = SvgRenderer()
        svg_text = renderer.render(bundle)

        self.assertIn('data-id="lower"', svg_text)
        self.assertIn('data-id="upper"', svg_text)
        self.assertLess(
            svg_text.index('data-id="lower"'),
            svg_text.index('data-id="upper"'),
            "Lower layer should be painted before the upper layer.",
        )

    def test_dash_scale_applies_to_svg_and_outlines(self) -> None:
        bundle = self._plan_bundle()

        renderer = SvgRenderer()
        scaled_svg = renderer.render(bundle)
        unscaled_svg = renderer.render(bundle, dash_scale=1.0)

        self.assertIn("stroke-dasharray: 1 0.75;", scaled_svg)
        self.assertIn("stroke-dasharray: 8 6;", unscaled_svg)

        def first_dash(svg: str) -> tuple[float, float]:
            match = re.search(r'stroke-dasharray="([0-9.]+) ([0-9.]+)"', svg)
            self.assertIsNotNone(match, "Expected a stroke-dasharray attribute in hidden outlines.")
            return float(match.group(1)), float(match.group(2))

        scaled_dash = first_dash(scaled_svg)
        unscaled_dash = first_dash(unscaled_svg)
        self.assertAlmostEqual(scaled_dash[0] * 8, unscaled_dash[0], places=2)
        self.assertAlmostEqual(scaled_dash[1] * 8, unscaled_dash[1], places=2)

    def test_all_polygons_emit_dashed_outline(self) -> None:
        bundle = GeometryBundle(view="plan", scale=1.0, pad=0.0)
        lower = PolygonFeature(
            id="lower",
            outer=[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)],
            height=1.0,
            elevation=0.0,
        )
        upper = PolygonFeature(
            id="upper",
            outer=[(8, 0), (18, 0), (18, 10), (8, 10), (8, 0)],
            height=1.0,
            elevation=2.0,
        )
        bundle.add_polygon(lower)
        bundle.add_polygon(upper)
        bundle.build_legend()

        renderer = SvgRenderer()
        svg_text = renderer.render(bundle)

        self.assertIn('data-id="lower::outline"', svg_text)
        self.assertIn('data-id="upper::outline"', svg_text)
        self.assertIn('fill="none"', svg_text)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
