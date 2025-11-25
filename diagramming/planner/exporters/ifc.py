from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

import ifcopenshell.api
import ifcopenshell.guid
import numpy as np

from ...relationships.solver import NeutralPrimitive


@dataclass(slots=True)
class IfcExportOptions:
    include_metadata: bool = True
    length_unit: str = "MILLIMETERS"


class IfcExporter:
    """
    Emit a minimal IFC model from neutral CadQuery-backed primitives.
    The exporter builds a default Project/Site/Building/Storey hierarchy,
    assigns Body tessellations to each product, and preserves stable GUIDs.
    """

    def __init__(self, options: Optional[IfcExportOptions] = None) -> None:
        self.options = options or IfcExportOptions()

    # ------------------------------------------------------------------ #
    def export(self, primitives: Sequence[NeutralPrimitive], out_path: Path) -> None:
        if not primitives:
            raise ValueError("No primitives to export")

        model = ifcopenshell.api.run("project.create_file")
        project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", model)
        model_context = ifcopenshell.api.run("context.add_context", model, context_type="Model")
        body_context = ifcopenshell.api.run(
            "context.add_context",
            model,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model_context,
        )

        site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
        building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding", name="Building")
        storey = ifcopenshell.api.run(
            "root.create_entity",
            model,
            ifc_class="IfcBuildingStorey",
            name="Storey",
            predefined_type="ELEMENT",
        )

        ifcopenshell.api.run("aggregate.assign_object", model, relating_object=project, products=[site])
        ifcopenshell.api.run("aggregate.assign_object", model, relating_object=site, products=[building])
        ifcopenshell.api.run("aggregate.assign_object", model, relating_object=building, products=[storey])

        for primitive in primitives:
            product = self._create_product(model, primitive)
            ifcopenshell.api.run(
                "spatial.assign_container",
                model,
                products=[product],
                relating_structure=storey,
            )
            rep = self._mesh_representation(model, body_context, primitive)
            if rep is not None:
                ifcopenshell.api.run(
                    "geometry.assign_representation",
                    model,
                    product=product,
                    representation=rep,
                )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        model.write(out_path)

    # ------------------------------------------------------------------ #
    def _create_product(self, model, primitive: NeutralPrimitive):
        class_name = primitive.class_name or "IfcBuildingElementProxy"
        predefined = None
        if primitive.ifc and isinstance(primitive.ifc, dict):
            predefined = primitive.ifc.get("predefined_type")

        product = ifcopenshell.api.run(
            "root.create_entity",
            model,
            ifc_class=class_name,
            name=primitive.metadata.get("label") if primitive.metadata else primitive.id,
            predefined_type=predefined,
        )
        if primitive.guid:
            try:
                product.GlobalId = ifcopenshell.guid.compress(str(uuid.UUID(primitive.guid)))
            except Exception:
                product.GlobalId = product.GlobalId
        product.Tag = primitive.guid
        return product

    def _mesh_representation(self, model, context, primitive: NeutralPrimitive):
        vertices, faces = self._tessellate(primitive)
        if not vertices or not faces:
            return None
        vertices_array = np.array([[v for v in vertices]], dtype=float)
        faces_array = [[[int(a) for a in face] for face in faces]]
        return ifcopenshell.api.run(
            "geometry.add_mesh_representation",
            model,
            context=context,
            vertices=vertices_array,
            faces=faces_array,
            force_faceted_brep=False,
        )

    def _tessellate(self, primitive: NeutralPrimitive) -> tuple[list[list[float]], list[Sequence[int]]]:
        if primitive.solid is not None:
            try:
                vectors, faces = primitive.solid.tessellate(0.5)
                vertex_rows = [[vec.x, vec.y, vec.z] for vec in vectors]
                return vertex_rows, list(faces)
            except Exception:
                return [], []

        # Fallback to a simple oriented box built from the primitive dimensions.
        hx, hy, hz = (primitive.size[0] / 2, primitive.size[1] / 2, primitive.size[2] / 2)
        corners = [
            (-hx, -hy, -hz),
            (hx, -hy, -hz),
            (hx, hy, -hz),
            (-hx, hy, -hz),
            (-hx, -hy, hz),
            (hx, -hy, hz),
            (hx, hy, hz),
            (-hx, hy, hz),
        ]
        angle = math.radians(primitive.transform.rotation[2])
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        tx, ty, tz = primitive.transform.position
        rotated = [
            (
                corner[0] * cos_a - corner[1] * sin_a + tx,
                corner[0] * sin_a + corner[1] * cos_a + ty,
                corner[2] + tz,
            )
            for corner in corners
        ]
        faces = [
            (0, 1, 2),
            (0, 2, 3),
            (4, 5, 6),
            (4, 6, 7),
            (0, 1, 5),
            (0, 5, 4),
            (1, 2, 6),
            (1, 6, 5),
            (2, 3, 7),
            (2, 7, 6),
            (3, 0, 4),
            (3, 4, 7),
        ]
        return rotated, faces


__all__ = ["IfcExporter", "IfcExportOptions"]
