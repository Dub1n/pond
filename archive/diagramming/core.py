from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


def _fmt(value: float) -> str:
    """Format floats without trailing zeros."""
    if abs(value) < 1e-9:
        value = 0.0
    if float(int(value)) == value:
        return str(int(value))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _approx_text_width(text: str, font_size: float) -> float:
    """Rough monospace-free width approximation."""
    return max(len(text), 1) * font_size * 0.55


@dataclass
class Bounds:
    min_x: float = math.inf
    min_y: float = math.inf
    max_x: float = -math.inf
    max_y: float = -math.inf

    def include(self, xs: Iterable[float], ys: Iterable[float]) -> None:
        xs_list = list(xs)
        ys_list = list(ys)
        if not xs_list or not ys_list:
            return
        self.min_x = min(self.min_x, min(xs_list))
        self.max_x = max(self.max_x, max(xs_list))
        self.min_y = min(self.min_y, min(ys_list))
        self.max_y = max(self.max_y, max(ys_list))

    def padded(self, pad: float) -> Tuple[float, float, float, float]:
        if self.max_x < self.min_x or self.max_y < self.min_y:
            # No geometry, return a tiny box around origin
            return (-pad, -pad, pad * 2, pad * 2)
        width = self.max_x - self.min_x
        height = self.max_y - self.min_y
        return (
            self.min_x - pad,
            self.min_y - pad,
            width + 2 * pad,
            height + 2 * pad,
        )


def _normalize_attr(key: str) -> str:
    return "class" if key == "class_" else key.replace("_", "-")


class SvgScene:
    """
    Minimal scene graph helper that tracks a bounding box while creating SVG elements.
    """

    def __init__(self, pad: float = 32.0) -> None:
        self.pad = pad
        self.root = ET.Element(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "role": "img",
                "width": "100%",
                "height": "auto",
                "style": "overflow:visible",
                "preserveAspectRatio": "xMidYMid meet",
            },
        )
        self.defs = ET.SubElement(self.root, "defs")
        self._css_blocks: List[str] = []
        self._markers: set[str] = set()
        self.scene = ET.SubElement(self.root, "g", {"id": "scene"})
        self.bounds = Bounds()
        self._finalized = False
        self.add_css(
            """
            :root { color-scheme: light; }
            text { font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif; letter-spacing: 0.01em; fill: #1c1c1c; }
            .label { font-size: 16px; }
            .note { font-size: 14px; fill: #505050; }
            .dim-line { stroke: #222; stroke-width: 1.6; fill: none; vector-effect: non-scaling-stroke; }
            .dim-extension { stroke: #888; stroke-width: 1.2; fill: none; stroke-dasharray: 4 4; vector-effect: non-scaling-stroke; }
            .dim-text { font-size: 14px; fill: #222; }
            line, polyline, polygon, rect, path { vector-effect: non-scaling-stroke; }
            """
        )

    # Basic utilities -----------------------------------------------------
    def add_css(self, css: str) -> None:
        css = css.strip()
        if css:
            self._css_blocks.append(css)

    def ensure_arrow_marker(self, marker_id: str = "dimArrow", color: str = "#333") -> str:
        if marker_id in self._markers:
            return f"url(#{marker_id})"
        marker = ET.SubElement(
            self.defs,
            "marker",
            {
                "id": marker_id,
                "markerWidth": "10",
                "markerHeight": "8",
                "refX": "9",
                "refY": "4",
                "orient": "auto",
            },
        )
        ET.SubElement(marker, "path", {"d": "M0,0 10,4 0,8 Z", "fill": color})
        self._markers.add(marker_id)
        return f"url(#{marker_id})"

    def group(self, **attrs: str) -> ET.Element:
        return ET.SubElement(self.scene, "g", {_normalize_attr(k): str(v) for k, v in attrs.items()})

    # Geometry -------------------------------------------------------------
    def rect(self, x: float, y: float, width: float, height: float, **attrs: str) -> ET.Element:
        self.bounds.include([x, x + width], [y, y + height])
        attr_map = {"x": _fmt(x), "y": _fmt(y), "width": _fmt(width), "height": _fmt(height)}
        attr_map.update({_normalize_attr(k): str(v) for k, v in attrs.items()})
        return ET.SubElement(self.scene, "rect", attr_map)

    def line(self, x1: float, y1: float, x2: float, y2: float, **attrs: str) -> ET.Element:
        self.bounds.include([x1, x2], [y1, y2])
        attr_map = {
            "x1": _fmt(x1),
            "y1": _fmt(y1),
            "x2": _fmt(x2),
            "y2": _fmt(y2),
        }
        attr_map.update({_normalize_attr(k): str(v) for k, v in attrs.items()})
        return ET.SubElement(self.scene, "line", attr_map)

    def polyline(self, points: Sequence[Tuple[float, float]], **attrs: str) -> ET.Element:
        xs = [pt[0] for pt in points]
        ys = [pt[1] for pt in points]
        self.bounds.include(xs, ys)
        attr_map = {"points": " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points)}
        attr_map.update({_normalize_attr(k): str(v) for k, v in attrs.items()})
        return ET.SubElement(self.scene, "polyline", attr_map)

    def polygon(self, points: Sequence[Tuple[float, float]], **attrs: str) -> ET.Element:
        xs = [pt[0] for pt in points]
        ys = [pt[1] for pt in points]
        self.bounds.include(xs, ys)
        attr_map = {"points": " ".join(f"{_fmt(x)},{_fmt(y)}" for x, y in points)}
        attr_map.update({_normalize_attr(k): str(v) for k, v in attrs.items()})
        return ET.SubElement(self.scene, "polygon", attr_map)

    def text(
        self,
        x: float,
        y: float,
        text: str,
        anchor: str = "start",
        font_size: float = 14.0,
        **attrs: str,
    ) -> ET.Element:
        approx_width = _approx_text_width(text, font_size)
        approx_height = font_size * 1.2
        if anchor == "middle":
            xs = [x - approx_width / 2, x + approx_width / 2]
        elif anchor == "end":
            xs = [x - approx_width, x]
        else:
            xs = [x, x + approx_width]
        ys = [y - approx_height, y]
        self.bounds.include(xs, ys)
        attr_map = {
            "x": _fmt(x),
            "y": _fmt(y),
            "font-size": _fmt(font_size),
            "text-anchor": anchor,
        }
        attr_map.update({_normalize_attr(k): str(v) for k, v in attrs.items()})
        element = ET.SubElement(self.scene, "text", attr_map)
        element.text = text
        return element

    # Export ---------------------------------------------------------------
    def _finalize(self) -> None:
        if self._finalized:
            return
        if self._css_blocks:
            style = ET.SubElement(self.defs, "style")
            style.text = "\n".join(self._css_blocks)
        view_x, view_y, view_w, view_h = self.bounds.padded(self.pad)
        self.root.set("viewBox", f"{_fmt(view_x)} {_fmt(view_y)} {_fmt(view_w)} {_fmt(view_h)}")
        self._finalized = True

    def to_string(self, pretty: bool = True) -> str:
        self._finalize()
        if pretty:
            try:
                ET.indent(self.root, space="  ")  # type: ignore[attr-defined]
            except AttributeError:
                pass
        return ET.tostring(self.root, encoding="unicode")

    def write(self, path: Path, pretty: bool = True) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_string(pretty=pretty), encoding="utf-8")
