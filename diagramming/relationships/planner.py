from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from shapely.affinity import rotate as shapely_rotate, translate as shapely_translate
from shapely.geometry import MultiPoint, Polygon as ShapelyPolygon, box as shapely_box

from ..materials import apply_material_class
from ..planner.bundle import GeometryBundle, PolygonFeature
from .solver import NeutralPrimitive, SolveResult, footprint_from_solid, mesh_from_primitive
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
        key = spec.info.option.lower() if spec.info.option else "relationship"
        self.option = RelationshipOption(key=key, title=spec.info.title)
        self._footprints = self._build_footprint_map(solved.primitives)

    def plan(self) -> List[RelationshipPlannedView]:
        plan_features = list(self._footprint_features(self.solved.primitives))
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
                for feature in self._section_features(self.solved.primitives, view_config):
                    if view_name in feature.views:
                        bundle.add_polygon(feature)
            else:
                for feature in plan_features:
                    if view_name in feature.views:
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
        footprints = self._footprints
        for primitive in primitives:
            shape = footprints.get(primitive.id)
            if shape is None or shape.is_empty:
                continue
            metadata = primitive.metadata or {}
            if primitive.voids:
                void_shapes = [footprints.get(vid) for vid in primitive.voids if footprints.get(vid) is not None]
                if void_shapes:
                    union = None
                    for vshape in void_shapes:
                        union = vshape if union is None else union.union(vshape)
                    if union is not None and not union.is_empty:
                        shape = shape.difference(union)
            if shape.is_empty:
                continue
            polygons = [shape] if isinstance(shape, ShapelyPolygon) else list(shape.geoms)  # type: ignore[attr-defined]
            for idx, polygon in enumerate(polygons):
                if polygon.is_empty:
                    continue
                outer = tuple(polygon.exterior.coords)
                holes = tuple(tuple(ring.coords) for ring in polygon.interiors)
                feature_id = primitive.id if idx == 0 else f"{primitive.id}#{idx}"
                feature = PolygonFeature(
                    id=feature_id,
                    outer=outer,
                    holes=holes,
                    height=primitive.size[2],
                    elevation=primitive.transform.position[2] - (primitive.size[2] / 2),
                    class_name=apply_material_class(primitive.class_name, primitive.material),
                    material=primitive.material,
                    label=metadata.get("label"),
                    label_id=metadata.get("label_id"),
                    metadata=metadata.copy(),
                    shape=polygon,
                    views=tuple(metadata.get("views"))
                    if metadata.get("views")
                    else tuple(self.spec.views.keys()) if self.spec.views else ("plan",),
                )
                yield feature

    def _footprint_from_mesh(self, primitive: NeutralPrimitive) -> ShapelyPolygon | None:
        mesh = mesh_from_primitive(primitive, to_meters=False)
        if mesh is None or not hasattr(mesh, "vertices") or len(mesh.vertices) == 0:
            return None
        hull = MultiPoint([(float(v[0]), float(v[1])) for v in mesh.vertices]).convex_hull
        if hull.is_empty or not isinstance(hull, ShapelyPolygon):
            return None
        return hull

    def _footprint_polygon(self, primitive: NeutralPrimitive) -> ShapelyPolygon:
        half_x = primitive.size[0] / 2
        half_y = primitive.size[1] / 2
        footprint = shapely_box(-half_x, -half_y, half_x, half_y)
        rotation_z = primitive.transform.rotation[2]
        if rotation_z:
            footprint = shapely_rotate(footprint, rotation_z, origin=(0.0, 0.0), use_radians=False)
        pos = primitive.transform.position
        return shapely_translate(footprint, xoff=pos[0], yoff=pos[1])

    def _build_footprint_map(self, primitives: Sequence[NeutralPrimitive]) -> Dict[str, ShapelyPolygon]:
        footprints: Dict[str, ShapelyPolygon] = {}
        for primitive in primitives:
            shape = (
                primitive.footprint
                or footprint_from_solid(primitive.solid)  # type: ignore[arg-type]
                or self._footprint_from_mesh(primitive)
                or self._footprint_polygon(primitive)
            )
            if shape is None or shape.is_empty:
                continue
            footprints[primitive.id] = shape
        return footprints

    def _section_features(
        self,
        primitives: Sequence[NeutralPrimitive],
        view_config: ViewConfig,
    ) -> List[PolygonFeature]:
        plane = view_config.plane
        if plane is None or plane.axis not in {"x", "y"}:
            return []

        origin = (plane.coordinate, 0.0, 0.0) if plane.axis == "x" else (0.0, plane.coordinate, 0.0)
        normal = (1.0, 0.0, 0.0) if plane.axis == "x" else (0.0, 1.0, 0.0)

        per_feature_segment: Dict[str, int] = {}
        section_features: List[PolygonFeature] = []

        for primitive in primitives:
            metadata = primitive.metadata or {}
            views = tuple(metadata.get("views")) if metadata.get("views") else ("section",)
            for polygon in self._slice_primitive(primitive, origin, normal, plane.axis):
                segment_index = per_feature_segment.get(primitive.id, 0)
                per_feature_segment[primitive.id] = segment_index + 1
                section_features.append(
                    PolygonFeature(
                        id=f"{primitive.id}@section#{segment_index}",
                        outer=tuple(polygon.exterior.coords),
                        holes=tuple(tuple(ring.coords) for ring in polygon.interiors),
                        label=metadata.get("label"),
                        label_id=metadata.get("label_id"),
                        class_name=apply_material_class(primitive.class_name, primitive.material),
                        height=primitive.size[2],
                        elevation=primitive.transform.position[2] - (primitive.size[2] / 2),
                        material=primitive.material,
                        metadata=metadata.copy(),
                        shape=polygon,
                        views=views,
                    )
                )

        return section_features

    def _slice_primitive(
        self,
        primitive: NeutralPrimitive,
        origin: tuple[float, float, float],
        normal: tuple[float, float, float],
        axis: str,
    ) -> List[ShapelyPolygon]:
        mesh = mesh_from_primitive(primitive, to_meters=False)
        if mesh is None:
            return []
        polygons: List[ShapelyPolygon] = []
        section = mesh.section(plane_origin=origin, plane_normal=normal)
        if section is None:
            return polygons

        for polyline in section.discrete:
            coords_3d = list(polyline)
            if len(coords_3d) < 3:
                continue
            coords_2d = [(pt[1], -pt[2]) if axis == "x" else (pt[0], -pt[2]) for pt in coords_3d]
            if coords_2d[0] != coords_2d[-1]:
                coords_2d.append(coords_2d[0])
            shape = ShapelyPolygon(coords_2d).buffer(0)
            if not shape.is_empty:
                polygons.append(shape)
        return [poly for poly in polygons if isinstance(poly, ShapelyPolygon) and not poly.is_empty]


__all__ = ["RelationshipPlanner", "RelationshipPlannedView", "RelationshipOption"]
