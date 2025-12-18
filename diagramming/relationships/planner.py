from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

import math
import numpy as np
from shapely.affinity import affine_transform, rotate as shapely_rotate, translate as shapely_translate
from shapely.geometry import MultiPoint, Polygon as ShapelyPolygon, box as shapely_box

from ..materials import apply_material_class
from ..planner.bundle import GeometryBundle, PolygonFeature
from .solver import NeutralPrimitive, SolveResult, footprint_from_solid, mesh_from_primitive
from .schema import RelationshipDiagramSpec, ViewConfig
from .dimensions import dimension_features_for_bundle


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
        self._primitive_index = {prim.id: prim for prim in solved.primitives}
        self._template_refs = self._build_template_reference_map(solved.primitives)

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
            for dimension in dimension_features_for_bundle(bundle):
                bundle.add_polyline(dimension)
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
        prim_index = self._primitive_index
        for primitive in primitives:
            shape = footprints.get(primitive.id)
            if shape is None or shape.is_empty:
                continue
            metadata = primitive.metadata or {}
            if primitive.voids:
                void_shapes = []
                for vid in primitive.voids:
                    base_shape = footprints.get(vid)
                    if base_shape is None:
                        continue
                    mapped = self._mapped_void_shape(primitive, prim_index.get(vid), base_shape)
                    void_shapes.append(mapped)
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

    def _mapped_void_shape(
        self,
        host: NeutralPrimitive,
        void_prim: NeutralPrimitive | None,
        shape: ShapelyPolygon,
    ) -> ShapelyPolygon:
        if void_prim is None:
            return shape
        host_template = (
            host.template_id
            or (host.metadata.get("template_id") if host.metadata else None)
            or host.id
        )
        void_template = (
            void_prim.template_id
            or (void_prim.metadata.get("template_id") if void_prim.metadata else None)
            or void_prim.id
        )
        base_host = self._template_refs.get(host_template)
        base_void = self._template_refs.get(void_template)
        if base_host is None or base_void is None:
            return shape
        try:
            host_matrix = self._transform_matrix(base_host.transform)
            void_matrix = self._transform_matrix(base_void.transform)
            relative = np.linalg.inv(host_matrix) @ void_matrix
            target_matrix = self._transform_matrix(host.transform) @ relative
            current_matrix = self._transform_matrix(void_prim.transform)
            delta = target_matrix @ np.linalg.inv(current_matrix)
            return affine_transform(shape, self._affine_from_matrix(delta))
        except Exception:
            return shape

    def _build_template_reference_map(self, primitives: Sequence[NeutralPrimitive]) -> Dict[str, NeutralPrimitive]:
        refs: Dict[str, NeutralPrimitive] = {}
        for prim in primitives:
            template = prim.template_id or (prim.metadata.get("template_id") if prim.metadata else None) or prim.id
            existing = refs.get(template)
            if existing is None or (getattr(existing, "origin", "clone") != "original" and getattr(prim, "origin", "clone") == "original"):
                refs[template] = prim
            refs.setdefault(template, prim)
        return refs

    def _transform_matrix(self, transform) -> np.ndarray:
        orientation = getattr(transform, "orientation", None)
        if orientation is None:
            angle = math.radians(transform.rotation[2] if transform.rotation else 0.0)
            orientation = (
                (math.cos(angle), math.sin(angle), 0.0),
                (-math.sin(angle), math.cos(angle), 0.0),
                (0.0, 0.0, 1.0),
            )
        matrix = np.eye(4, dtype=float)
        matrix[0:3, 0] = np.array(orientation[0])
        matrix[0:3, 1] = np.array(orientation[1])
        matrix[0:3, 2] = np.array(orientation[2])
        matrix[0:3, 3] = np.array(transform.position)
        return matrix

    def _affine_from_matrix(self, matrix: np.ndarray) -> tuple[float, float, float, float, float, float]:
        return (
            float(matrix[0, 0]),
            float(matrix[0, 1]),
            float(matrix[1, 0]),
            float(matrix[1, 1]),
            float(matrix[0, 3]),
            float(matrix[1, 3]),
        )

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
