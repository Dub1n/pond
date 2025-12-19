from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from diagramming.relationships import load_relationship_spec, validate_relationship_spec
from diagramming.relationships.lint import lint_relationship_spec


class RelationshipValidationTests(unittest.TestCase):
    def test_validate_relationship_spec_flags_missing_predefined_type(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: lint
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [400, 100, 50]
                material: timber
                relate:
                  +x+y-x-y: { ref: origin, pos: +x+y-x-y }
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "lint.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        report = validate_relationship_spec(spec)
        self.assertTrue(any("predefined type" in err for err in report.errors))

    def test_validate_relationship_spec_returns_checksum_on_success(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: checksum
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: frame
                kind: reference
                size: [200, 200, 0]
                relate:
                  cxcy: { ref: origin }
              - id: slab
                class: IfcSlab
                size: [200, 200, 20]
                material: decking
                relate:
                  +x+y-x-y: { ref: frame, pos: +x+y-x-y }
                  +z: { ref: origin, pos: +z }
                  -z: { ref: origin, pos: +z, offset: -20 }
                ifc:
                  predefined_type: FLOOR
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "valid.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        report = validate_relationship_spec(spec)
        self.assertFalse(report.errors)
        self.assertIsNotNone(report.mesh_checksum)

    def test_validate_flags_rotate_id_map_length(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: rotate-id-map
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [100, 100, 50]
                material: timber
                relate:
                  cxcy: { ref: origin }
                ifc:
                  predefined_type: BEAM
            operations:
              - type: rotate
                about: { ref: origin, axis: +z }
                count: 3
                include_seed: true
                id_map:
                  beam: [beam_a, beam_b]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "rotate-id-map.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        errors = lint_relationship_spec(spec)
        self.assertTrue(any("id_map" in err for err in errors))

    def test_lint_flags_unknown_clone_selector(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: selector-clone
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: host
                class: IfcSlab
                size: [200, 200, 20]
                material: decking
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: FLOOR
              - id: void
                class: IfcOpeningElement
                size: [50, 50, 20]
                relate:
                  cxcy: { ref: origin }
                  cz: { ref: origin }
                ifc:
                  predefined_type: OPENING
            operations:
              - type: boolean
                target: host
                subtract: [void#2]
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "selector-clone.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        errors = lint_relationship_spec(spec)
        self.assertTrue(any("matched no components" in err or "unknown selector" in err for err in errors))

    def test_ifc_mapped_items_and_types_on_repeats(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: mapped-items
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [400, 50, 150]
                material: timber
                relate:
                  cx: { ref: origin }
                  cy: { ref: origin }
                  cz: { ref: origin }
                array:
                  start:
                    +y: { ref: origin, offset: -600 }
                  end:
                    +y: { ref: origin, offset: 600 }
                  count: 3
                  include_seed: true
                ifc:
                  predefined_type: BEAM
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "mapped.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        report = validate_relationship_spec(spec)
        self.assertFalse(report.errors)
        try:
            from diagramming.planner.exporters import IfcExporter
            import ifcopenshell
        except Exception as exc:  # pragma: no cover - optional dependency guard
            self.skipTest(f"ifcopenshell not available: {exc}")
        exporter = IfcExporter()
        with TemporaryDirectory() as tmp:
            ifc_path = Path(tmp) / "model.ifc"
            exporter.export(report.result.primitives, ifc_path)
            model = ifcopenshell.open(ifc_path)
        beams = model.by_type("IfcBeam")
        mapped_items = model.by_type("IfcMappedItem")
        type_links = model.by_type("IfcRelDefinesByType")
        typed_objects = {
            obj
            for link in type_links
            for obj in getattr(link, "RelatedObjects", []) or []
        }
        self.assertGreaterEqual(len(beams), 2)
        self.assertTrue(mapped_items)
        self.assertTrue(all(beam in typed_objects for beam in beams))

    def test_relvoids_propagate_to_clones(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: relvoid-clones
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
            path = Path(tmp) / "relvoid.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        report = validate_relationship_spec(spec)
        self.assertFalse(report.errors)
        try:
            from diagramming.planner.exporters import IfcExporter
            import ifcopenshell
        except Exception as exc:  # pragma: no cover - optional dependency guard
            self.skipTest(f"ifcopenshell not available: {exc}")
        exporter = IfcExporter()
        with TemporaryDirectory() as tmp:
            ifc_path = Path(tmp) / "relvoid.ifc"
            exporter.export(report.result.primitives, ifc_path)
            model = ifcopenshell.open(ifc_path)
        slabs = model.by_type("IfcSlab")
        openings = model.by_type("IfcOpeningElement")
        rels = model.by_type("IfcRelVoidsElement")
        self.assertEqual(len(slabs), 2)
        self.assertEqual(len(openings), 2)
        self.assertEqual(len(rels), 2)
        x_coords = set()
        for opening in openings:
            placement = getattr(opening, "ObjectPlacement", None)
            relative = getattr(placement, "RelativePlacement", None) if placement else None
            coords = getattr(relative, "Location", None)
            if coords:
                xyz = getattr(coords, "Coordinates", [])
                if xyz:
                    x_coords.add(round(float(xyz[0]), 3))
        self.assertGreater(len(x_coords), 1)

    def test_metadata_maps_to_class_property_sets(self) -> None:
        spec_text = dedent(
            """
            schema: pond-relationship-test
            info:
              option: metadata-psets
            components:
              - id: origin
                kind: reference
                size: [0, 0, 0]
              - id: beam
                class: IfcBeam
                size: [400, 50, 150]
                material: timber
                relate:
                  cxcy: { ref: origin }
                metadata:
                  label: "Primary beam"
                  description: "Beam description"
                ifc:
                  predefined_type: BEAM
                  psets:
                    - name: Pset_Test
                      props:
                        Foo: "Bar"
            """
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata-pset.yaml"
            path.write_text(spec_text, encoding="utf-8")
            spec = load_relationship_spec(path)
        report = validate_relationship_spec(spec)
        self.assertFalse(report.errors)
        try:
            from diagramming.planner.exporters import IfcExporter
            import ifcopenshell
            from ifcopenshell.util import element as ifc_element_utils
        except Exception as exc:  # pragma: no cover - optional dependency guard
            self.skipTest(f"ifcopenshell not available: {exc}")
        exporter = IfcExporter()
        with TemporaryDirectory() as tmp:
            ifc_path = Path(tmp) / "metadata.ifc"
            exporter.export(report.result.primitives, ifc_path)
            model = ifcopenshell.open(ifc_path)
        beam = next(iter(model.by_type("IfcBeam")), None)
        self.assertIsNotNone(beam)
        psets = ifc_element_utils.get_psets(beam, psets_only=True)
        self.assertIn("Pset_BeamCommon", psets)
        self.assertEqual(psets["Pset_BeamCommon"].get("Reference"), "beam")
        self.assertEqual(psets["Pset_BeamCommon"].get("Name"), "Primary beam")
        self.assertIn("Pset_Test", psets)
        self.assertEqual(psets["Pset_Test"].get("Foo"), "Bar")

if __name__ == "__main__":  # pragma: no cover
    unittest.main()
