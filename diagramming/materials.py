from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class MaterialStyle:
    key: str
    css_class: str
    svg_fill: str
    svg_stroke: Optional[str]
    gltf_color: Tuple[float, float, float, float]

    @property
    def rgba255(self) -> Tuple[int, int, int, int]:
        channels = [int(max(0.0, min(1.0, value)) * 255) for value in self.gltf_color]
        while len(channels) < 4:
            channels.append(255)
        return tuple(channels[:4])  # type: ignore[return-value]


_MATERIALS: Dict[str, MaterialStyle] = {
    "decking": MaterialStyle(
        key="decking",
        css_class="material-decking",
        svg_fill="#d5c1a3",
        svg_stroke="#5f4b32",
        gltf_color=(0.835, 0.757, 0.635, 1.0),
    ),
    "timber": MaterialStyle(
        key="timber",
        css_class="material-timber",
        svg_fill="#c89a5b",
        svg_stroke="#5b3b12",
        gltf_color=(0.788, 0.604, 0.357, 1.0),
    ),
    "joist": MaterialStyle(
        key="joist",
        css_class="material-joist",
        svg_fill="#a98d68",
        svg_stroke="#49341d",
        gltf_color=(0.663, 0.552, 0.408, 1.0),
    ),
    "water": MaterialStyle(
        key="water",
        css_class="material-water",
        svg_fill="#9fd5ff",
        svg_stroke="#1f2933",
        gltf_color=(0.623, 0.835, 1.0, 0.8),
    ),
    "soil": MaterialStyle(
        key="soil",
        css_class="material-soil",
        svg_fill="#cbb38a",
        svg_stroke="#4a3f2b",
        gltf_color=(0.678, 0.58, 0.396, 1.0),
    ),
    "pad": MaterialStyle(
        key="pad",
        css_class="material-pad",
        svg_fill="#b7c2c9",
        svg_stroke="#48525a",
        gltf_color=(0.72, 0.76, 0.79, 1.0),
    ),
}


def get_material_style(material: Optional[str]) -> Optional[MaterialStyle]:
    if not material:
        return None
    return _MATERIALS.get(material.lower())


def apply_material_class(base_class: Optional[str], material: Optional[str]) -> Optional[str]:
    style = get_material_style(material)
    classes = []
    if base_class:
        classes.extend(base_class.split())
    if style:
        classes.append(style.css_class)
    if not classes:
        return None
    return " ".join(dict.fromkeys(classes))
