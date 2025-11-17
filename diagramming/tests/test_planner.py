import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from shapely.geometry import Polygon as ShapelyPolygon

from diagramming import DiagramPlanner
from diagramming.schema import load_spec


def _load_planner() -> DiagramPlanner:
    spec_path = Path(__file__).resolve().parent / "fixtures" / "deck-framing.yaml"
    spec = load_spec(spec_path)
    return DiagramPlanner(spec)


class PlannerGeometryTests(unittest.TestCase):
    def test_option_a_plan_geometry(self) -> None:
        planner = _load_planner()
        planned = planner.plan("A", "plan")

        deck = next(feature for feature in planned.bundle.polygons if feature.id == "deck_outer")
        self.assertEqual(len(deck.holes), 1)

        posts = [feature for feature in planned.bundle.polygons if feature.label_id == "P"]
        self.assertEqual(len(posts), 24)
        centers = {(round(f.shape.centroid.x), round(f.shape.centroid.y)) for f in posts}
        expected_centers = {
            (80, 2500),
            (80, 2900),
            (80, 3300),
            (80, 3700),
            (80, 4100),
            (80, 4500),
            (6920, 2500),
            (6920, 2900),
            (6920, 3300),
            (6920, 3700),
            (6920, 4100),
            (6920, 4500),
            (2500, 80),
            (2900, 80),
            (3300, 80),
            (3700, 80),
            (4100, 80),
            (4500, 80),
            (2500, 6920),
            (2900, 6920),
            (3300, 6920),
            (3700, 6920),
            (4100, 6920),
            (4500, 6920),
        }
        self.assertEqual(centers, expected_centers)
        for feature in posts:
            xs = [point[0] for point in feature.outer]
            ys = [point[1] for point in feature.outer]
            self.assertGreaterEqual(min(xs), -200.0)
            self.assertLessEqual(max(xs), 7200.0)
            self.assertGreaterEqual(min(ys), -200.0)
            self.assertLessEqual(max(ys), 7200.0)

        joist_ids = [feature.id for feature in planned.bundle.polygons if feature.id.startswith("joists_west")]
        self.assertTrue(any("@rot" in feature_id for feature_id in joist_ids))

        overhang = next(line for line in planned.bundle.polylines if line.id == "overhang_line")
        self.assertEqual(overhang.points[0], (2000.0, 1500.0))
        self.assertEqual(overhang.points[1], (5000.0, 1500.0))
        self.assertAlmostEqual(planned.bundle.scale, 0.18)
        self.assertEqual(planned.bundle.background, "#ffffff")

    def test_option_b_section_contains_header_and_outrigger(self) -> None:
        planner = _load_planner()
        planned = planner.plan("B", "section")

        header_slices = [
            feature
            for feature in planned.bundle.polygons
            if feature.id.startswith("header_north") and "@section" in feature.id
        ]
        self.assertTrue(header_slices, "Expected section slices for header_north")
        header = header_slices[0]
        header_xs = [point[0] for point in header.outer]
        header_ys = [point[1] for point in header.outer]
        self.assertAlmostEqual(max(header_xs) - min(header_xs), 180.0)
        self.assertAlmostEqual(max(header_ys), 0.0)
        self.assertAlmostEqual(min(header_ys), -220.0)

        outrigger_slices = [
            feature
            for feature in planned.bundle.polygons
            if feature.id.startswith("outriggers_north") and "@section" in feature.id
        ]
        self.assertTrue(outrigger_slices, "Expected section slices for outriggers_north")
        outrigger = outrigger_slices[0]
        outrigger_xs = [point[0] for point in outrigger.outer]
        outrigger_ys = [point[1] for point in outrigger.outer]
        self.assertAlmostEqual(max(outrigger_xs) - min(outrigger_xs), 600.0)
        self.assertAlmostEqual(max(outrigger_ys), -220.0)
        self.assertAlmostEqual(min(outrigger_ys), -370.0)
        self.assertAlmostEqual(planned.bundle.scale, 0.18)

    def test_option_c_section_generated_from_scene(self) -> None:
        planner = _load_planner()
        planned = planner.plan("C", "section")

        section_ids = {feature.id for feature in planned.bundle.polygons}
        self.assertTrue(any("@section" in feature_id for feature_id in section_ids))
        self.assertFalse(any(feature_id.startswith("section_") for feature_id in section_ids))

        joist_slices = [
            feature
            for feature in planned.bundle.polygons
            if feature.id.startswith("joists_west") and "@section" in feature.id
        ]
        self.assertTrue(joist_slices)
        for joist in joist_slices:
            self.assertAlmostEqual(joist.height, 150.0)
            ys = [point[1] for point in joist.outer]
            self.assertAlmostEqual(max(ys), 0.0)
            self.assertAlmostEqual(min(ys), -150.0)

        inner_beam_slices = [
            feature
            for feature in planned.bundle.polygons
            if feature.id.startswith("inner_beam_west") and "@section" in feature.id
        ]
        self.assertTrue(inner_beam_slices)
        for beam in inner_beam_slices:
            self.assertAlmostEqual(beam.height, 150.0)
            ys = [point[1] for point in beam.outer]
            self.assertAlmostEqual(max(ys), 0.0)
            self.assertAlmostEqual(min(ys), -150.0)

        pad_slices = [
            feature
            for feature in planned.bundle.polygons
            if feature.id.startswith("pads_west") and "@section" in feature.id
        ]
        self.assertTrue(pad_slices)
        for pad in pad_slices:
            self.assertAlmostEqual(pad.height, 100.0)
            ys = [point[1] for point in pad.outer]
            self.assertAlmostEqual(min(ys), 0.0)
            self.assertAlmostEqual(max(ys), 100.0)

        outer_beam_slices = [
            feature
            for feature in planned.bundle.polygons
            if feature.id.startswith("beam_west") and "@section" in feature.id
        ]
        self.assertTrue(outer_beam_slices)
        for beam in outer_beam_slices:
            ys = [point[1] for point in beam.outer]
            self.assertAlmostEqual(max(ys), 0.0)
            self.assertAlmostEqual(min(ys), -150.0)

        soil_slices = [
            feature
            for feature in planned.bundle.polygons
            if feature.id.startswith("soil_fill") and "@section" in feature.id
        ]
        self.assertTrue(soil_slices)
        for soil in soil_slices:
            ys = [point[1] for point in soil.outer]
            self.assertAlmostEqual(min(ys), 0.0)
            self.assertAlmostEqual(max(ys), 900.0)

    def test_operation_rotate_group(self) -> None:
        spec_text = dedent(
            """
            name: rotate-test
            units: mm
            options:
              A:
                title: Rotation Test
                components:
                  - type: rectangle
                    id: pivot
                    size: [100, 100]
                    origin: [200, 200]
                  - type: rectangle
                    id: spoke
                    size: [200, 40]
                    anchor:
                      ref: pivot
                      align: east
                      anchor_point: west
                operations:
                  - type: rotate
                    targets: [spoke]
                    count: 4
                    angle: 90
                    include_base: true
                    about:
                      ref: pivot
                      align: center
            """
        )
        with TemporaryDirectory() as tmp_dir:
            spec_path = Path(tmp_dir) / "rotate.yaml"
            spec_path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("A", "plan")
        spokes = {feature.id: feature for feature in planned.bundle.polygons if feature.id.startswith("spoke")}
        self.assertEqual(len(spokes), 4)
        centroids = {
            feature.id: (round(feature.shape.centroid.x, 1), round(feature.shape.centroid.y, 1))
            for feature in spokes.values()
        }
        expected = {
            "spoke": (400.0, 250.0),
            "spoke@rot1": (250.0, 400.0),
            "spoke@rot2": (100.0, 250.0),
            "spoke@rot3": (250.0, 100.0),
        }
        self.assertEqual(centroids, expected)

    def test_repeat_span_distribution(self) -> None:
        spec_text = dedent(
            """
            name: repeat-span
            units: mm
            options:
              A:
                title: Repeat span
                components:
                  - type: rectangle
                    id: post
                    size: [100, 100]
                    origin: [0, 0]
                    repeat:
                      count: 5
                      direction: east
                      span: 2000
            """
        )
        with TemporaryDirectory() as tmp_dir:
            spec_path = Path(tmp_dir) / "repeat-span.yaml"
            spec_path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("A", "plan")
        posts = [
            feature for feature in planned.bundle.polygons if feature.id.startswith("post")
        ]
        self.assertEqual(len(posts), 5)
        centers = sorted(round(feature.shape.centroid.x) for feature in posts)
        self.assertEqual(centers, [50, 550, 1050, 1550, 2050])

    def test_repeat_interval_and_span_compute_count(self) -> None:
        spec_text = dedent(
            """
            name: repeat-interval-span
            units: mm
            options:
              A:
                title: Repeat derived count
                components:
                  - type: rectangle
                    id: support
                    size: [50, 50]
                    origin: [0, 0]
                    repeat:
                      interval: 300
                      span: 900
                      direction: east
            """
        )
        with TemporaryDirectory() as tmp_dir:
            spec_path = Path(tmp_dir) / "repeat-derived.yaml"
            spec_path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("A", "plan")
        supports = [
            feature for feature in planned.bundle.polygons if feature.id.startswith("support")
        ]
        self.assertEqual(len(supports), 4)
        centers = sorted(round(feature.shape.centroid.x) for feature in supports)
        self.assertEqual(centers, [25, 325, 625, 925])

    def test_mirror_operation_vertical_axis(self) -> None:
        spec_text = dedent(
            """
            name: mirror-test
            units: mm
            options:
              A:
                title: Mirror Test
                components:
                  - type: rectangle
                    id: beam
                    size: [200, 40]
                    origin: [0, 0]
                operations:
                  - type: mirror
                    targets: [beam]
                    axis: y
                    about:
                      ref: beam
                      align: west
            """
        )
        with TemporaryDirectory() as tmp_dir:
            spec_path = Path(tmp_dir) / "mirror.yaml"
            spec_path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("A", "plan")
        beam = next(feature for feature in planned.bundle.polygons if feature.id == "beam")
        mirrored = next(
            feature for feature in planned.bundle.polygons if feature.id == "beam@mirrorY"
        )
        self.assertAlmostEqual(round(beam.shape.centroid.x, 1), 100.0)
        self.assertAlmostEqual(round(mirrored.shape.centroid.x, 1), -100.0)
        self.assertEqual(beam.height, mirrored.height)
        self.assertEqual(beam.views, mirrored.views)

    def test_boolean_cutouts_from_components(self) -> None:
        spec_text = dedent(
            """
            name: boolean-test
            units: mm
            options:
              A:
                title: Boolean subtraction sample
                components:
                  - type: rectangle
                    id: soil
                    size: [1000, 1000]
                    origin: [0, 0]
                    boolean:
                      subtract:
                        - pads
                  - type: rectangle
                    id: pads
                    size: [200, 200]
                    anchor:
                      ref: soil
                      align: north_west
                      anchor_point: north_west
                      offset: [200, 200]
                    repeat:
                      count: 2
                      spacing: [300, 0]
            """
        )
        with TemporaryDirectory() as tmp_dir:
            spec_path = Path(tmp_dir) / "boolean.yaml"
            spec_path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(spec_path)
        planner = DiagramPlanner(spec)
        planned = planner.plan("A", "plan")

        soil = next(feature for feature in planned.bundle.polygons if feature.id == "soil")
        self.assertEqual(len(soil.holes), 2)
        interiors = soil.shape.interiors if soil.shape is not None else ()
        centers = sorted(
            (
                round(ShapelyPolygon(ring.coords).centroid.x),
                round(ShapelyPolygon(ring.coords).centroid.y),
            )
            for ring in interiors
        )
        self.assertEqual(centers, [(300, 300), (600, 300)])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
