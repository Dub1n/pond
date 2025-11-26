from __future__ import annotations

from typing import List, Tuple

from ..planner.bundle import GeometryBundle, PolylineFeature


def dimension_features_for_bundle(bundle: GeometryBundle) -> List[PolylineFeature]:
    extent = bundle.extent()
    if extent is None:
        return []

    min_x, min_y, max_x, max_y = extent
    width = max(max_x - min_x, 0.0)
    height = max(max_y - min_y, 0.0)
    offset = max(width, height) * 0.05 + bundle.pad * 0.25

    dims: List[PolylineFeature] = []
    dims.extend(_horizontal_dimension(min_x, max_x, min_y, offset))
    dims.extend(_vertical_dimension(min_y, max_y, max_x, offset))
    return dims


def _horizontal_dimension(min_x: float, max_x: float, anchor_y: float, offset: float) -> List[PolylineFeature]:
    y = anchor_y - offset
    label = f"{max_x - min_x:.0f} mm"
    return [
        PolylineFeature(
            id="dim-x",
            points=((min_x, y), (max_x, y)),
            stroke_width=1.6,
            label_id=label,
            class_name="dimension",
            metadata={"kind": "dimension", "arrows": True},
        ),
        PolylineFeature(
            id="dim-x-ext-start",
            points=((min_x, anchor_y), (min_x, y)),
            stroke_width=1.0,
            class_name="dimension-extension",
            metadata={"kind": "dimension-extension"},
        ),
        PolylineFeature(
            id="dim-x-ext-end",
            points=((max_x, anchor_y), (max_x, y)),
            stroke_width=1.0,
            class_name="dimension-extension",
            metadata={"kind": "dimension-extension"},
        ),
    ]


def _vertical_dimension(min_y: float, max_y: float, anchor_x: float, offset: float) -> List[PolylineFeature]:
    x = anchor_x + offset
    label = f"{max_y - min_y:.0f} mm"
    return [
        PolylineFeature(
            id="dim-y",
            points=((x, min_y), (x, max_y)),
            stroke_width=1.6,
            label_id=label,
            class_name="dimension",
            metadata={"kind": "dimension", "arrows": True},
        ),
        PolylineFeature(
            id="dim-y-ext-start",
            points=((anchor_x, min_y), (x, min_y)),
            stroke_width=1.0,
            class_name="dimension-extension",
            metadata={"kind": "dimension-extension"},
        ),
        PolylineFeature(
            id="dim-y-ext-end",
            points=((anchor_x, max_y), (x, max_y)),
            stroke_width=1.0,
            class_name="dimension-extension",
            metadata={"kind": "dimension-extension"},
        ),
    ]


__all__ = ["dimension_features_for_bundle"]
