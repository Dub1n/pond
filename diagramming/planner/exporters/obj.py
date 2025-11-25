from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from ...relationships.solver import NeutralPrimitive, build_scene_from_primitives


@dataclass(slots=True)
class ObjExportOptions:
    include_metadata: bool = True
    to_meters: bool = False


class ObjExporter:
    """
    Export resolved primitives to an OBJ mesh. Uses the CadQuery-derived meshes
    already built for glTF/IFC to keep IDs and metadata consistent.
    """

    def __init__(self, options: Optional[ObjExportOptions] = None) -> None:
        self.options = options or ObjExportOptions()

    def export(self, primitives: Sequence[NeutralPrimitive], out_path: Path) -> None:
        scene = build_scene_from_primitives(primitives, to_meters=self.options.to_meters)
        if not scene.geometry:
            raise ValueError("No geometry available for OBJ export")
        export_data = scene.export(file_type="obj")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(export_data, (bytes, bytearray)):
            out_path.write_bytes(export_data)
        else:
            out_path.write_text(export_data)


__all__ = ["ObjExporter", "ObjExportOptions"]
