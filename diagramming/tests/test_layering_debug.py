import unittest
from pathlib import Path

import io

import cairosvg
from PIL import Image
from shapely.ops import unary_union

from diagramming import DiagramPlanner
from diagramming.renderers import SvgRenderer
from diagramming.schema import load_spec


class LayeringDebugTests(unittest.TestCase):
    def test_water_is_clipped_by_upper_layer(self) -> None:
        spec_path = Path(__file__).resolve().parent / "fixtures" / "layering-debug.yaml"
        spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("D", "plan")
        bundle = planned.bundle
        water = next(p for p in bundle.polygons if p.id == "water")
        higher = [
            p.shape
            for p in bundle.polygons
            if p.id != "water" and (p.elevation + p.height) > (water.elevation + water.height)
        ]
        renderer = SvgRenderer()
        svg_text = renderer.render(bundle)
        png_bytes = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"))
        image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
        water_pixels = 0
        for r, g, b in image.getdata():
            if b >= max(r, g) + 20:
                water_pixels += 1

        view_extent = bundle.extent()
        self.assertIsNotNone(view_extent, "Bundle extent missing")
        pad = bundle.pad
        view_area = (view_extent[2] - view_extent[0] + 2 * pad) * (view_extent[3] - view_extent[1] + 2 * pad)

        measured_ratio = water_pixels / (image.width * image.height)

        # Expected visible water = water area minus any overlap with higher features.
        expected_shape = water.shape
        if expected_shape is None:
            expected_area = 0.0
        else:
            if higher:
                cover = unary_union([shape for shape in higher if shape is not None])
                expected_shape = expected_shape.difference(cover)
            expected_area = expected_shape.area if not expected_shape.is_empty else 0.0
        expected_ratio = expected_area / view_area if view_area else 0.0

        # Assert clipping is within 2% relative error to catch missing overlays.
        if expected_ratio == 0:
            self.assertEqual(water_pixels, 0)
        else:
            diff = abs(measured_ratio - expected_ratio) / expected_ratio
            self.assertLess(
                diff,
                0.02,
                f"Water should be clipped by upper layer; expected ratio {expected_ratio:.4f}, measured {measured_ratio:.4f}",
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
