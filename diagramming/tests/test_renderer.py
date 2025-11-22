import re
import unittest
from pathlib import Path

from diagramming import DiagramPlanner
from diagramming.renderers import SvgRenderer
from diagramming.schema import load_spec
from diagramming.planner.bundle import GeometryBundle, PolygonFeature


class RendererTests(unittest.TestCase):
    def test_svg_renderer_outputs_accessible_markup(self) -> None:
        spec_path = Path(__file__).resolve().parent / "fixtures" / "deck-framing.yaml"
        spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("C", "plan")

        renderer = SvgRenderer()
        svg_text = renderer.render(planned.bundle, aria_label="Option C plan", title="Option C plan")

        self.assertIn("aria-label=\"Option C plan\"", svg_text)
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
        spec_path = Path("diagrams/specs/deck-framing.yaml")
        spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("A", "plan")

        renderer = SvgRenderer()
        scaled_svg = renderer.render(planned.bundle)
        unscaled_svg = renderer.render(planned.bundle, dash_scale=1.0)

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
