from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import trimesh
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry.polygon import orient

from ..bundle import GeometryBundle, PolygonFeature
from ...materials import get_material_style

MM_TO_METERS = 0.001


@dataclass(slots=True)
class GltfExportOptions:
    include_metadata: bool = True
    file_format: str = "glb"  # "glb" or "gltf"


class GltfExporter:
    """
    Convert a GeometryBundle into a glTF/GLB asset by extruding polygons.

    Each polygon with a positive `height` is extruded along the +Z axis.
    Heights and elevations are provided in millimetres and converted to metres
    for the glTF scene. Component metadata is written to the mesh metadata so
    downstream consumers can recover labels/IDs.
    """

    def __init__(self, options: Optional[GltfExportOptions] = None) -> None:
        self.options = options or GltfExportOptions()

    # ------------------------------------------------------------------ #
    def export(self, bundle: GeometryBundle, out_path: Path) -> None:
        out_path = self._resolve_output_path(out_path)

        if bundle.scene is not None and bundle.scene.geometry:
            scene = bundle.scene
        else:
            scene = self._build_scene_from_bundle(bundle)
            if not scene.geometry:
                raise ValueError("No extrudable features found (missing heights?)")

        export_type = "glb" if out_path.suffix.lower() == ".glb" else "gltf"
        export_data = scene.export(file_type=export_type)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(export_data, bytes):
            out_path.write_bytes(export_data)
        else:
            out_path.write_text(export_data)

    # ------------------------------------------------------------------ #
    def _mesh_for_feature(self, feature: PolygonFeature) -> Optional[trimesh.Trimesh]:
        if feature.height <= 0.0:
            return None
        if feature.shape is None or feature.shape.is_empty:
            return None

        polygon = orient(feature.shape, sign=1.0)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty:
            return None

        try:
            mesh = trimesh.creation.extrude_polygon(polygon, height=feature.height)
        except ValueError:
            return None

        mesh.apply_scale(MM_TO_METERS)
        elevation = feature.elevation * MM_TO_METERS
        if elevation:
            mesh.apply_translation((0.0, 0.0, elevation))

        style = get_material_style(feature.material)
        if style:
            color = np.tile(np.array(style.rgba255, dtype=np.uint8), (len(mesh.vertices), 1))
            mesh.visual.vertex_colors = color
        mesh.metadata = self._build_metadata(feature)
        return mesh

    def _build_scene_from_bundle(self, bundle: GeometryBundle) -> trimesh.Scene:
        scene = trimesh.Scene()
        for feature in bundle.polygons:
            mesh = self._mesh_for_feature(feature)
            if mesh is None:
                continue
            node_name = feature.label_id or feature.id
            index = 1
            unique_name = node_name
            while unique_name in scene.geometry:
                unique_name = f"{node_name}#{index}"
                index += 1
            scene.add_geometry(mesh, node_name=unique_name)
        return scene

    @staticmethod
    def _build_metadata(feature: PolygonFeature) -> Dict[str, object]:
        meta: Dict[str, object] = {}
        if feature.id:
            meta["id"] = feature.id
        if feature.label:
            meta["label"] = feature.label
        if feature.label_id:
            meta["label_id"] = feature.label_id
        if feature.class_name:
            meta["class"] = feature.class_name
        if feature.material:
            meta["material"] = feature.material
        if feature.metadata:
            for key, value in feature.metadata.items():
                meta.setdefault(key, value)
        return meta

    def _resolve_output_path(self, out_path: Path) -> Path:
        suffix = out_path.suffix.lower()
        if suffix in {".glb", ".gltf"}:
            if self.options.file_format == "gltf" and suffix != ".gltf":
                return out_path.with_suffix(".gltf")
            if self.options.file_format == "glb" and suffix != ".glb":
                return out_path.with_suffix(".glb")
            return out_path
        preferred = ".glb" if self.options.file_format == "glb" else ".gltf"
        return out_path.with_suffix(preferred)
