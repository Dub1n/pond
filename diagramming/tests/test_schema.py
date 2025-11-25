import tempfile
import unittest
from pathlib import Path

from textwrap import dedent

from diagramming.schema import load_spec


class SpecLoadTests(unittest.TestCase):
    def test_load_spec_and_views(self) -> None:
        spec_path = Path("diagrams/specs/deck-framing.yaml")
        spec = load_spec(spec_path)

        self.assertEqual(spec.name, "deck-framing")
        self.assertEqual(spec.units, "mm")
        self.assertAlmostEqual(spec.scale, 0.18)

        option = spec.get_option("A")
        view_names = option.view_names()
        self.assertIn("plan", view_names)
        self.assertIn("section", view_names)
        self.assertTrue(option.components, "Expected Option A to declare components")
        self.assertGreaterEqual(len(option.operations), 1)
        self.assertEqual(option.operations[0].type, "rotate")

    def test_metadata_traits_and_view_overrides(self) -> None:
        spec_text = dedent(
            """
            name: sample
            units: mm
            options:
              A:
                title: Sample option
                components:
                  - type: rectangle
                    id: deck
                    size: [1000, 500]
                    metadata:
                      role: deck
                    traits: [primary, framing]
                  - type: polyline
                    id: axis
                    points:
                      - [0, 0]
                      - [1000, 0]
                    height: 20
                    metadata:
                      note: centerline
                    traits: [alignment]
                views:
                  plan:
                    title: Plan
                    pad: 32
                    scale: 0.5
                    background: "#efefef"
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        option = spec.get_option("A")
        deck = option.components[0]
        self.assertEqual(deck.metadata.get("role"), "deck")
        self.assertEqual(deck.traits, ("primary", "framing"))
        axis = option.components[1]
        self.assertEqual(axis.height, 20.0)
        self.assertEqual(axis.metadata.get("note"), "centerline")

        plan_view = option.views["plan"]
        self.assertEqual(plan_view.pad, 32)
        self.assertEqual(plan_view.scale, 0.5)
        self.assertEqual(plan_view.background, "#efefef")

    def test_ifc_block_parses_and_uppercases(self) -> None:
        spec_text = dedent(
            """
            name: ifc-sample
            units: mm
            options:
              A:
                title: IFC option
                components:
                  - type: rectangle
                    id: beam
                    size: [100, 200]
                    height: 300
                    ifc:
                      predefined_type: beam
                      psets:
                        - name: Pset_BeamCommon
                          props:
                            LoadBearing: true
                views:
                  plan:
                    title: Plan
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ifc.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        component = spec.get_option("A").components[0]
        self.assertIsNotNone(component.ifc)
        assert component.ifc  # type narrowing
        self.assertEqual(component.ifc.predefined_type, "BEAM")
        self.assertEqual(len(component.ifc.psets), 1)
        self.assertEqual(component.ifc.psets[0].name, "Pset_BeamCommon")
        self.assertTrue(component.ifc.psets[0].props.get("LoadBearing"))

    def test_anchor_validation_raises(self) -> None:
        spec_text = dedent(
            """
            name: invalid
            units: mm
            options:
              A:
                title: Invalid option
                components:
                  - type: rectangle
                    id: deck
                    size: [100, 100]
                    anchor:
                      ref: missing
                      align: center
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.yaml"
            path.write_text(spec_text, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_spec(path)

    def test_repeat_spacing_requires_offset(self) -> None:
        spec_text = dedent(
            """
            name: invalid-repeat
            units: mm
            options:
              A:
                title: Invalid repeat
                components:
                  - type: rectangle
                    id: deck
                    size: [100, 100]
                    repeat:
                      count: 2
                      spacing: [0, 0]
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "repeat.yaml"
            path.write_text(spec_text, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_spec(path)

    def test_anchor_alias_and_directional_offset(self) -> None:
        spec_text = dedent(
            """
            name: anchor-alias
            units: mm
            options:
              A:
                title: Anchor alias option
                dimensions:
                  gap: 200
                components:
                  - type: rectangle
                    id: ref
                    size: [1000, 1000]
                    origin: [0, 0]
                  - type: rectangle
                    id: child
                    size: [100, 100]
                    anchor:
                      ref: ref
                      align: north_east
                      attach: north_west
                      offset:
                        west: gap
                        south: 150
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "alias.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        option = spec.get_option("A")
        self.assertIn("gap", option.dimensions)
        child = next(component for component in option.components if component.id == "child")
        self.assertIsNotNone(child.anchor)
        assert child.anchor is not None  # for type checkers
        self.assertEqual(child.anchor.anchor_point, "north_west")
        self.assertAlmostEqual(child.anchor.offset[0], -200.0)
        self.assertAlmostEqual(child.anchor.offset[1], 150.0)

    def test_metadata_expression_uses_dimensions(self) -> None:
        spec_text = dedent(
            """
            name: metadata-expression
            units: mm
            options:
              A:
                title: Metadata expression option
                dimensions:
                  beam_height: 220
                  pad_height: 100
                components:
                  - type: rectangle
                    id: pad
                    size: [300, 300]
                    origin: [0, 0]
                    height: pad_height
                    metadata:
                      elevation: -pad_height
                      embed: beam_height + pad_height
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        option = spec.get_option("A")
        pad = next(component for component in option.components if component.id == "pad")
        self.assertAlmostEqual(pad.height, 100.0)
        self.assertAlmostEqual(pad.metadata.get("elevation"), -100.0)
        self.assertAlmostEqual(pad.metadata.get("embed"), 320.0)

    def test_anchor_attach_face_alias(self) -> None:
        spec_text = dedent(
            """
            name: anchor-face
            units: mm
            options:
              A:
                title: Anchor face option
                components:
                  - type: rectangle
                    id: ref
                    size: [1000, 1000]
                    origin: [0, 0]
                  - type: rectangle
                    id: beam
                    size: [200, 1000]
                    anchor:
                      ref: ref
                      align: west
                      attach_face: east
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "anchor-face.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        option = spec.get_option("A")
        beam = next(component for component in option.components if component.id == "beam")
        assert beam.anchor is not None
        self.assertEqual(beam.anchor.align, "west")
        self.assertEqual(beam.anchor.anchor_point, "east")
        self.assertEqual(beam.anchor.offset, (0.0, 0.0))

    def test_placement_with_named_dimensions(self) -> None:
        spec_text = dedent(
            """
            name: placement
            units: mm
            options:
              A:
                title: Placement option
                dimensions:
                  backspan: 1000
                  cantilever: 250
                  walkway_gap: 430
                components:
                  - type: rectangle
                    id: pond
                    size: [3000, 3000]
                    origin: [0, 0]
                  - type: rectangle
                    id: joist
                    size: [backspan + cantilever, 140]
                    placement:
                      from:
                        ref: pond
                        align: north_east
                      attach: north_west
                      move:
                        - direction: west
                          distance: backspan + cantilever
                      inset:
                        south: walkway_gap
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "placement.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        option = spec.get_option("A")
        self.assertAlmostEqual(option.dimensions["backspan"], 1000.0)
        joist = next(component for component in option.components if component.id == "joist")
        self.assertEqual(joist.size, (1250.0, 140.0))
        self.assertIsNotNone(joist.anchor)
        assert joist.anchor is not None
        self.assertEqual(joist.anchor.ref, "pond")
        self.assertEqual(joist.anchor.align, "north_east")
        self.assertEqual(joist.anchor.anchor_point, "north_west")
        self.assertAlmostEqual(joist.anchor.offset[0], -1250.0)
        self.assertAlmostEqual(joist.anchor.offset[1], 430.0)

    def test_placement_flush_shorthand(self) -> None:
        spec_text = dedent(
            """
            name: placement-flush
            units: mm
            options:
              A:
                title: Placement flush option
                components:
                  - type: rectangle
                    id: deck
                    size: [5000, 5000]
                    origin: [0, 0]
                  - type: rectangle
                    id: beam
                    size: [180, 3360]
                    placement:
                      flush:
                        ref: deck
                        edge: west
                      attach_edge: east
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "placement-flush.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        option = spec.get_option("A")
        beam = next(component for component in option.components if component.id == "beam")
        assert beam.anchor is not None
        self.assertEqual(beam.anchor.ref, "deck")
        self.assertEqual(beam.anchor.align, "west")
        self.assertEqual(beam.anchor.anchor_point, "east")
        self.assertEqual(beam.anchor.offset, (0.0, 0.0))

    def test_vertical_placement_flush_parses(self) -> None:
        spec_text = dedent(
            """
            name: vertical-flush
            units: mm
            options:
              A:
                title: Vertical flush option
                dimensions:
                  pad_height: 100
                components:
                  - type: rectangle
                    id: water
                    size: [1000, 1000]
                    origin: [0, 0]
                    height: 900
                    metadata:
                      elevation: -900
                  - type: rectangle
                    id: pad
                    size: [300, 300]
                    origin: [100, 100]
                    height: pad_height
                    vertical:
                      flush:
                        ref: water
                        face: top
                      attach_face: top
                      offset: 0
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "vertical-flush.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path)

        option = spec.get_option("A")
        pad = next(component for component in option.components if component.id == "pad")
        assert pad.vertical is not None
        self.assertEqual(pad.vertical.ref, "water")
        self.assertEqual(pad.vertical.ref_face, "top")
        self.assertEqual(pad.vertical.attach_face, "top")
        self.assertEqual(pad.vertical.offset, 0.0)

    def test_load_spec_skips_unrequested_options(self) -> None:
        spec_text = dedent(
            """
            name: filtered
            units: mm
            options:
              A:
                title: Option A
                components: []
              B:
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "filtered.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_spec(path, include_options=["A"])

        self.assertEqual(list(spec.option_keys()), ["A"])

    def test_requested_option_missing_raises(self) -> None:
        spec_text = dedent(
            """
            name: filtered
            units: mm
            options:
              A:
                title: Option A
                components: []
            """
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "filtered.yaml"
            path.write_text(spec_text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing requested option"):
                load_spec(path, include_options=["C"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
