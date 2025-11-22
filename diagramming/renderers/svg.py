from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from shapely.geometry import GeometryCollection, MultiPolygon, Polygon as ShapelyPolygon
from shapely.geometry.base import BaseGeometry

from ..planner.bundle import GeometryBundle, LegendEntry, PolygonFeature
from ..materials import get_material_style
from .svg_scene import SvgScene


@dataclass
class LabelInstruction:
    x: float
    y: float
    text: str
    font_size: float
    anchor: str = "middle"
    class_name: str = "feature-label"


@dataclass
class PolygonRenderData:
    feature: PolygonFeature
    path_data: str
    class_name: str
    shape: Optional[BaseGeometry]
    top: float


class SvgRenderer:
    DEFAULT_DASH_SCALE = 0.125

    def __init__(self, extra_css: Optional[str] = None) -> None:
        base_css_path = Path(__file__).with_name("styles") / "base.css"
        self.base_css = base_css_path.read_text(encoding="utf-8")
        self.extra_css = extra_css

    def render(
        self,
        bundle: GeometryBundle,
        aria_label: Optional[str] = None,
        title: Optional[str] = None,
        dash_scale: float = DEFAULT_DASH_SCALE,
    ) -> str:
        dash_scale = max(dash_scale, 0.01)
        scene = SvgScene(pad=bundle.pad, scale=bundle.scale, background=bundle.background)
        if aria_label:
            scene.root.set("aria-label", aria_label)
        if title:
            scene.set_title(title)

        scene.add_css(self.base_css)
        if self.extra_css:
            scene.add_css(self.extra_css)
        if dash_scale != 1.0:
            scene.add_css(self._dash_override_css(dash_scale))

        title_size, body_size, line_height = self._compute_font_metrics(bundle, scene.scale)

        polygons = self._ordered_polygons(bundle)
        # Polylines are intentionally skipped for this layering pass.

        labels: List[LabelInstruction] = []
        seen_labels: set[str] = set()
        polygon_draws: List[PolygonRenderData] = []
        for feature in polygons:
            instruction, draw_data = self._prepare_polygon(scene, feature, body_size, seen_labels)
            if instruction:
                labels.append(instruction)
            if draw_data:
                polygon_draws.append(draw_data)

        if bundle.view == "plan":
            hidden_style = self._hidden_outline_style(bundle, dash_scale)
            self._draw_plan_polygons(scene, polygon_draws, hidden_style)
        else:
            for draw_data in polygon_draws:
                self._draw_standard_polygon(scene, draw_data)

        if labels:
            self._render_labels(scene, labels)

        if bundle.legend:
            self._render_legend(scene, bundle.legend, title_size, body_size, line_height)

        return scene.to_string()

    # ------------------------------------------------------------------ #
    def _prepare_polygon(
        self,
        scene: SvgScene,
        feature: PolygonFeature,
        label_size: float,
        seen_labels: set[str],
    ) -> Tuple[Optional["LabelInstruction"], Optional[PolygonRenderData]]:
        class_name = feature.class_name or "component"
        all_points = list(feature.outer)
        for hole in feature.holes:
            all_points.extend(hole)
        xs = [pt[0] for pt in all_points]
        ys = [pt[1] for pt in all_points]
        if xs and ys:
            scene.bounds.include(xs, ys)
        path_data = _polygon_to_path(feature.outer, feature.holes)
        shape = self._feature_shape(feature)
        render_data = PolygonRenderData(
            feature=feature,
            path_data=path_data,
            class_name=class_name,
            shape=shape,
            top=self._plan_top(feature),
        )
        label_text, base_key = self._label_text(feature.label_id, feature.label)
        label_key = self._label_key(feature.id, base_key)
        if label_text and label_key not in seen_labels:
            label_pos = self._polygon_label_position(feature, label_size)
            if label_pos is not None:
                lx, ly = label_pos
                seen_labels.add(label_key)
                return (
                    LabelInstruction(
                        x=lx,
                        y=ly,
                        text=label_text,
                        font_size=label_size,
                        anchor="middle",
                        class_name="feature-label",
                    ),
                    render_data,
                )
        return (None, render_data)

    def _render_legend(
        self,
        scene: SvgScene,
        legend: List[LegendEntry],
        title_size: float,
        body_size: float,
        line_height: float,
    ) -> None:
        bounds = scene.bounds
        if bounds.min_x == float("inf"):  # No geometry drawn yet
            origin_x = 0.0
            base_y = 0.0
        else:
            origin_x = bounds.min_x + 32.0
            base_y = bounds.max_y + 48.0

        title_y = base_y + title_size

        scene.text(
            origin_x,
            title_y,
            "Legend",
            anchor="start",
            font_size=title_size,
            class_="legend legend-title",
        )
        for idx, entry in enumerate(legend, start=1):
            y = title_y + idx * line_height
            label_parts: List[str] = []
            if entry.label_id:
                label_parts.append(entry.label_id)
            label_parts.append(entry.label)
            text = " – ".join(label_parts)
            scene.text(
                origin_x,
                y,
                text,
                anchor="start",
                font_size=body_size,
                class_="legend",
            )

    def _render_labels(self, scene: SvgScene, labels: List["LabelInstruction"]) -> None:
        label_group = scene.group(class_="feature-labels")
        for label in labels:
            y = self._baseline_adjust(label.y, label.font_size)
            attrs = {
                "font_size": label.font_size,
                "anchor": label.anchor,
                "class_": label.class_name,
            }
            scene.text(label.x, y, label.text, **attrs)
            # The text call already appends to scene; move the node into label_group.
            label_node = scene.scene[-1]
            scene.scene.remove(label_node)
            label_group.append(label_node)

    def _compute_font_metrics(
        self, bundle: GeometryBundle, scale: float
    ) -> Tuple[float, float, float]:
        extent = bundle.extent()
        width_units = 1000.0
        if extent is not None:
            width_units = max(extent[2] - extent[0], 1.0)
        scale = scale or 1.0
        diagram_width_px = width_units * scale
        target_title_px = max(min(diagram_width_px * 0.025, 40.0), 10.0)
        target_body_px = max(min(diagram_width_px * 0.02, 32.0), 8.0)
        title_size = target_title_px / scale
        body_size = target_body_px / scale
        line_height = (target_body_px * 1.4) / scale
        return title_size, body_size, line_height

    @staticmethod
    def _label_key(feature_id: str, base_key: Optional[str]) -> str:
        if base_key is None:
            return feature_id
        return f"{feature_id}:{base_key}"

    def _label_text(
        self, label_id: Optional[str], label: Optional[str]
    ) -> Tuple[Optional[str], Optional[str]]:
        if label_id:
            return label_id, label_id
        return None, None

    def _polygon_label_position(
        self, feature: PolygonFeature, label_size: float
    ) -> Optional[Tuple[float, float]]:
        if not feature.outer:
            return None
        outer_bounds = _ring_bounds(feature.outer)
        cx = (outer_bounds[0] + outer_bounds[2]) / 2
        cy = (outer_bounds[1] + outer_bounds[3]) / 2
        if feature.holes:
            hole_bounds = [_ring_bounds(hole) for hole in feature.holes if hole]
            if hole_bounds:
                min_hole_top = min(b[1] for b in hole_bounds)
                gap_top = max(min_hole_top - outer_bounds[1], 0.0)
                if gap_top > label_size * 1.5:
                    cy = outer_bounds[1] + gap_top / 2
                else:
                    max_hole_bottom = max(b[3] for b in hole_bounds)
                    gap_bottom = max(outer_bounds[3] - max_hole_bottom, 0.0)
                    if gap_bottom > label_size * 1.5:
                        cy = max_hole_bottom + gap_bottom / 2
        return (cx, cy)

    @staticmethod
    def _baseline_adjust(y: float, font_size: float) -> float:
        return y + font_size * 0.35

    def _draw_standard_polygon(self, scene: SvgScene, draw: PolygonRenderData) -> None:
        scene.path(
            draw.path_data,
            class_=draw.class_name,
            fill_rule="evenodd",
            data_id=draw.feature.id,
        )

    def _draw_plan_polygons(
        self,
        scene: SvgScene,
        draws: Sequence[PolygonRenderData],
        outline_style: dict[str, float],
    ) -> None:
        for draw in draws:
            base_kwargs = {
                "fill_rule": "evenodd",
            }
            material_attrs = self._material_attributes(draw.feature)
            base_kwargs.update(material_attrs)
            scene.path(draw.path_data, data_id=draw.feature.id, **base_kwargs)

        for draw in draws:
            attrs = {
                "fill": "none",
                "fill_rule": "evenodd",
                "data_id": f"{draw.feature.id}::outline",
                "stroke": outline_style["stroke"],
                "stroke_width": f"{outline_style['width']:.4f}",
                "stroke_dasharray": f"{outline_style['dash_on']:.4f} {outline_style['dash_off']:.4f}",
                "stroke_linecap": "butt",
                "stroke_linejoin": "round",
            }
            scene.path(draw.path_data, **attrs)

    def _geometry_to_paths(self, geometry: Optional[BaseGeometry]) -> List[str]:
        if geometry is None or geometry.is_empty:
            return []
        if isinstance(geometry, ShapelyPolygon):
            outer = list(geometry.exterior.coords)
            holes = [list(ring.coords) for ring in geometry.interiors]
            return [_polygon_to_path(outer, holes)]
        if isinstance(geometry, MultiPolygon):
            paths: List[str] = []
            for geom in geometry.geoms:
                paths.extend(self._geometry_to_paths(geom))
            return paths
        if isinstance(geometry, GeometryCollection):
            paths = []
            for geom in geometry.geoms:
                paths.extend(self._geometry_to_paths(geom))
            return paths
        return []

    def _hidden_outline_style(self, bundle: GeometryBundle, dash_scale: float) -> dict[str, float]:
        scale = bundle.scale or 1.0
        width_px = 0.4
        base_dash_on_px = 0.6
        base_dash_off_px = 0.4
        scale_factor = dash_scale / self.DEFAULT_DASH_SCALE if self.DEFAULT_DASH_SCALE else 1.0
        width_units = width_px / scale
        dash_on_units = (base_dash_on_px * scale_factor) / scale
        dash_off_units = (base_dash_off_px * scale_factor) / scale
        return {
            "stroke": "#46505a",
            "width": width_units,
            "dash_on": dash_on_units,
            "dash_off": dash_off_units,
        }

    @staticmethod
    def _plan_top(feature: PolygonFeature) -> float:
        return float(feature.elevation + feature.height)

    @staticmethod
    def _feature_shape(feature: PolygonFeature) -> Optional[ShapelyPolygon]:
        if feature.shape is not None:
            if isinstance(feature.shape, ShapelyPolygon):
                return feature.shape
            try:
                return ShapelyPolygon(feature.shape)
            except Exception:
                return None
        if feature.outer:
            try:
                return ShapelyPolygon(feature.outer)
            except Exception:
                return None
        return None

    def _ordered_polygons(self, bundle: GeometryBundle) -> List[PolygonFeature]:
        indexed = list(enumerate(bundle.polygons))
        if bundle.view != "plan":
            return [feature for _, feature in indexed]
        indexed.sort(key=lambda item: (self._plan_polygon_layer_key(item[1]), item[0]))
        return [feature for _, feature in indexed]

    @staticmethod
    def _plan_polygon_layer_key(feature: PolygonFeature) -> float:
        return float(feature.elevation + feature.height)

    @staticmethod
    def _material_attributes(feature: PolygonFeature) -> dict[str, str]:
        attrs: dict[str, str] = {}
        style = get_material_style(feature.material)
        if style is not None:
            if style.svg_fill:
                attrs["fill"] = style.svg_fill
            if style.svg_stroke:
                attrs["stroke"] = style.svg_stroke
        return attrs

    @staticmethod
    def _format_dash_value(value: float) -> str:
        value = max(value, 0.0)
        formatted = f"{value:.4f}".rstrip("0").rstrip(".")
        return formatted or "0"

    def _dash_override_css(self, dash_scale: float) -> str:
        detail_on = 8.0 * dash_scale
        detail_off = 6.0 * dash_scale
        dim_on = 4.0 * dash_scale
        dim_off = 4.0 * dash_scale
        detail = (
            f".component-detail {{ stroke-dasharray: "
            f"{self._format_dash_value(detail_on)} {self._format_dash_value(detail_off)}; }}"
        )
        dims = (
            f".dim-extension {{ stroke-dasharray: "
            f"{self._format_dash_value(dim_on)} {self._format_dash_value(dim_off)}; }}"
        )
        return f"{detail}\n{dims}"


def _polygon_to_path(
    outer: Sequence[Tuple[float, float]],
    holes: Sequence[Sequence[Tuple[float, float]]],
) -> str:
    segments: List[str] = []
    segments.extend(_ring_to_segments(outer))
    for hole in holes:
        segments.extend(_ring_to_segments(hole))
    return " ".join(segments)


def _ring_to_segments(points: Sequence[Tuple[float, float]]) -> List[str]:
    if not points:
        return []
    segments: List[str] = [f"M {points[0][0]},{points[0][1]}"]
    for x, y in points[1:]:
        segments.append(f"L {x},{y}")
    if points[0] != points[-1]:
        segments.append(f"L {points[0][0]},{points[0][1]}")
    segments.append("Z")
    return segments


def _ring_bounds(points: Sequence[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    return (min(xs), min(ys), max(xs), max(ys))
