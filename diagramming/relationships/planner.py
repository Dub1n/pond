from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from shapely.affinity import rotate as shapely_rotate, translate as shapely_translate
from shapely.geometry import LineString, Polygon as ShapelyPolygon, box as shapely_box

from ..planner.bundle import GeometryBundle, PolygonFeature
from ..planner.planner import _iter_line_segments, _section_polygon
from .solver import NeutralPrimitive, SolveResult
from .schema import RelationshipDiagramSpec, ViewConfig


@dataclass(slots=True)
class RelationshipOption:
    key: str
    title: str | None = None


@dataclass(slots=True)
class RelationshipPlannedView:
    option: RelationshipOption
    view: str
    bundle: GeometryBundle
    view_config: ViewConfig


class RelationshipPlanner:
    def __init__(self, spec: RelationshipDiagramSpec, solved: SolveResult) -> None:
        self.spec = spec
        self.solved = solved
        self.option = RelationshipOption(key=spec.info.option or "relationship", title=spec.info.title)

    def plan(self) -> List[RelationshipPlannedView]:
        features = list(self._footprint_features(self.solved.primitives))
        views = self.spec.views or {"plan": ViewConfig(name="plan")}
        planned: List[RelationshipPlannedView] = []
        for view_name, view_config in views.items():
            bundle = GeometryBundle(
                view=view_name,
                pad=view_config.pad,
                scale=view_config.scale or view_config.scale_hint or 1.0,
                background=view_config.background,
            )
            if view_config.plane is not None:
                self._populate_section(bundle, features, view_config)
            else:
                for feature in features:
                    bundle.add_polygon(feature)
            bundle.scene = self.solved.scene
            bundle.build_legend()
            planned.append(
                RelationshipPlannedView(
                    option=self.option,
                    view=view_name,
                    bundle=bundle,
                    view_config=view_config,
                )
            )
        return planned

    # ------------------------------------------------------------------ #
    def _footprint_features(self, primitives: Sequence[NeutralPrimitive]) -> Iterable[PolygonFeature]:
        for primitive in primitives:
            shape = primitive.footprint or self._footprint_polygon(primitive)
            if shape is None or shape.is_empty:
                continue
            outer = tuple(shape.exterior.coords)
            feature = PolygonFeature(
                id=primitive.id,
                outer=outer,
                holes=(),
                height=primitive.size[2],
                elevation=primitive.transform.position[2] - (primitive.size[2] / 2),
                class_name=primitive.class_name,
                material=primitive.material,
                metadata=primitive.metadata.copy(),
                shape=shape,
                views=tuple(self.spec.views.keys()) if self.spec.views else ("plan",),
            )
            yield feature

    def _footprint_polygon(self, primitive: NeutralPrimitive) -> ShapelyPolygon:
        half_x = primitive.size[0] / 2
        half_y = primitive.size[1] / 2
        footprint = shapely_box(-half_x, -half_y, half_x, half_y)
        rotation_z = primitive.transform.rotation[2]
        if rotation_z:
            footprint = shapely_rotate(footprint, rotation_z, origin=(0.0, 0.0), use_radians=False)
        pos = primitive.transform.position
        return shapely_translate(footprint, xoff=pos[0], yoff=pos[1])

    def _populate_section(
        self,
        bundle: GeometryBundle,
        features: Sequence[PolygonFeature],
        view_config: ViewConfig,
    ) -> None:
        plane = view_config.plane
        if plane is None:
            return
        if plane.axis not in {"x", "y"}:
            return

        coord = plane.coordinate
        if plane.axis == "x":
            slice_line = LineString([(coord, -1e5), (coord, 1e5)])
            axis_index = 1
        else:
            slice_line = LineString([(-1e5, coord), (1e5, coord)])
            axis_index = 0

        segments: List[tuple[PolygonFeature, float, float]] = []
        min_coord = float("inf")

        for feature in features:
            if feature.shape is None or feature.height <= 0.0:
                continue
            intersection = feature.shape.intersection(slice_line)
            if intersection.is_empty:
                continue
            for segment in _iter_line_segments(intersection):
                coords = list(segment.coords)
                if not coords:
                    continue
                start = coords[0][axis_index]
                end = coords[-1][axis_index]
                length = abs(end - start)
                if length < 1e-3:
                    continue
                start_coord = min(start, end)
                segments.append((feature, start_coord, length))
                min_coord = min(min_coord, start_coord)

        if not segments:
            return

        per_feature_segment: Dict[str, int] = {}
        for feature, start_coord, length in segments:
            outer = _section_polygon(length, feature.elevation, feature.height, start_coord, plane.axis)
            shape = ShapelyPolygon(outer[:-1]) if len(outer) > 3 else None
            segment_index = per_feature_segment.get(feature.id, 0)
            per_feature_segment[feature.id] = segment_index + 1
            section_feature = PolygonFeature(
                id=f"{feature.id}@section#{segment_index}",
                outer=outer,
                holes=(),
                label=feature.label,
                label_id=feature.label_id,
                class_name=feature.class_name,
                height=feature.height,
                elevation=feature.elevation,
                material=feature.material,
                metadata=feature.metadata.copy(),
                shape=shape,
                views=("section",),
            )
            bundle.add_polygon(section_feature)

        if min_coord != float("inf") and min_coord != 0.0:
            shift = -min_coord
            for feature in bundle.polygons:
                shifted = [(x + shift, y) for x, y in feature.outer]
                feature.outer = tuple(shifted)
                if isinstance(feature.shape, ShapelyPolygon):
                    feature.shape = ShapelyPolygon(shifted[:-1])


__all__ = ["RelationshipPlanner", "RelationshipPlannedView", "RelationshipOption"]
