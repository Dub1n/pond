from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import cadquery as cq

from ...relationships.solver import ComponentTransform, NeutralPrimitive


@dataclass(slots=True)
class StepExportOptions:
    include_metadata: bool = True


class StepExporter:
    """
    Export CadQuery-backed solids to a STEP file for downstream QA/engineering
    workflows. Falls back to oriented boxes when a primitive lacks a solid.
    """

    def __init__(self, options: Optional[StepExportOptions] = None) -> None:
        self.options = options or StepExportOptions()

    def export(self, primitives: Sequence[NeutralPrimitive], out_path: Path) -> None:
        solids = []
        for primitive in primitives:
            solid = primitive.solid or self._fallback_box(primitive)
            if solid is not None:
                solids.append(solid)
        if not solids:
            raise ValueError("No solids available for STEP export")

        compound = cq.Compound.makeCompound(solids) if len(solids) > 1 else solids[0]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(compound, str(out_path))

    # ------------------------------------------------------------------ #
    def _fallback_box(self, primitive: NeutralPrimitive):
        hx, hy, hz = (primitive.size[0] / 2, primitive.size[1] / 2, primitive.size[2] / 2)
        if hx <= 0 or hy <= 0 or hz <= 0:
            return None
        wp = cq.Workplane("XY").box(primitive.size[0], primitive.size[1], primitive.size[2], centered=True)
        return self._apply_transform(wp, primitive.transform)

    def _apply_transform(self, wp: cq.Workplane, transform: ComponentTransform):
        rotation_z = transform.rotation[2]
        if rotation_z:
            wp = wp.rotate((0, 0, 0), (0, 0, 1), rotation_z)
        pos = transform.position
        wp = wp.translate((pos[0], pos[1], pos[2]))
        return wp.val()


__all__ = ["StepExporter", "StepExportOptions"]
