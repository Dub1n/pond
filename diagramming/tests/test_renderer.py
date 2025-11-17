import io
import re
import unittest
from pathlib import Path

import cairosvg
from PIL import Image

from diagramming import DiagramPlanner
from diagramming.renderers import SvgRenderer
from diagramming.schema import load_spec


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

    def test_hidden_beam_overlay_visible_without_fill(self) -> None:
        spec_path = Path("diagrams/specs/deck-framing.yaml")
        spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("A", "plan")

        renderer = SvgRenderer()
        svg_text = renderer.render(planned.bundle)
        png_bytes = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"))
        image = Image.open(io.BytesIO(png_bytes)).convert("RGB")

        red_pixels = 0
        green_pixels = 0
        deck_pixels = 0
        for r, g, b in image.getdata():
            if r >= 200 and g <= 80 and b <= 80:
                red_pixels += 1
            if g - max(r, b) >= 10:
                green_pixels += 1
            if abs(r - 213) <= 15 and abs(g - 193) <= 15 and abs(b - 163) <= 15:
                deck_pixels += 1

        self.assertGreater(green_pixels, 0, "Expected hidden beam outline dashed in green.")
        self.assertEqual(red_pixels, 0, "Beam fill should be fully hidden beneath deck.")
        self.assertGreater(deck_pixels, 0, "Deck fill should override hidden framing colours.")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
