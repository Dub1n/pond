from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import trimesh
from shapely.affinity import rotate as shapely_rotate, scale as shapely_scale
from shapely.geometry import (
    GeometryCollection,
    LineString,
    MultiLineString,
    Polygon as ShapelyPolygon,
)
from shapely.ops import unary_union

from ..materials import apply_material_class, get_material_style
from ..schema.components import (
    Anchor,
    BooleanConfig,
    Component,
    ComponentBase,
    PolylineComponent,
    RectangleComponent,
)
from ..schema.spec import (
    DiagramSpec,
    MirrorOperation,
    OptionSpec,
    PlaneSpec,
    ViewSpec,
    Operation,
    RotateOperation,
)
from .bundle import GeometryBundle, PolygonFeature, PolylineFeature
from .geometry import (
    Bounds,
    alignment_offset,
    bounds_from_origin,
    create_rectangle,
)


class ViewContext:
    def __init__(self) -> None:
        self._polygon_bounds: Dict[str, List[Bounds]] = {}
        self._polyline_bounds: Dict[str, List[Bounds]] = {}
        self._vertical: Dict[str, List[Tuple[float, float]]] = {}

    def add_polygon(self, component_id: str, bounds: Bounds) -> None:
        self._polygon_bounds.setdefault(component_id, []).append(bounds)

    def add_polyline(self, component_id: str, bounds: Bounds) -> None:
        self._polyline_bounds.setdefault(component_id, []).append(bounds)

    def bounds_for(self, component_id: str) -> Bounds:
        if component_id in self._polygon_bounds and self._polygon_bounds[component_id]:
            return self._polygon_bounds[component_id][0]
        if component_id in self._polyline_bounds and self._polyline_bounds[component_id]:
            return self._polyline_bounds[component_id][0]
        raise KeyError(f"component '{component_id}' has not been resolved yet")

    def set_vertical(self, component_id: str, elevation: float, height: float) -> None:
        self._vertical.setdefault(component_id, []).append((elevation, height))

    def vertical_for(self, component_id: str) -> Tuple[float, float]:
        if component_id in self._vertical and self._vertical[component_id]:
            return self._vertical[component_id][0]
        raise KeyError(f"component '{component_id}' has no vertical data recorded")

    def update_polygon_bounds(self, component_id: str, bounds: Bounds) -> None:
        if component_id in self._polygon_bounds and self._polygon_bounds[component_id]:
            self._polygon_bounds[component_id][0] = bounds
        else:
            self._polygon_bounds[component_id] = [bounds]


@dataclass(slots=True)
class PlannedView:
    option: OptionSpec
    view: str
    bundle: GeometryBundle
    view_config: Optional[ViewSpec]


@dataclass(slots=True)
class OptionGeometry:
    polygons: List[PolygonFeature]
    polylines: List[PolylineFeature]
    scene: trimesh.Scene


class DiagramPlanner:
    def __init__(self, spec: DiagramSpec) -> None:
        self.spec = spec
        self._option_cache: Dict[str, OptionGeometry] = {}

    def plan(self, option_key: str, view: str) -> PlannedView:
        option = self.spec.get_option(option_key)
        geometry = self._get_option_geometry(option_key, option)
        view_config = option.views.get(view)
        pad = view_config.pad if view_config else 48.0
        spec_scale = self.spec.scale or 1.0
        scale = view_config.scale if view_config and view_config.scale is not None else spec_scale
        background = view_config.background if view_config else None
        bundle = GeometryBundle(view=view, pad=pad, scale=scale, background=background)

        if view_config and view_config.plane is not None:
            self._populate_section_from_plane(bundle, geometry, view_config.plane)
        else:
            for feature in geometry.polygons:
                if view in feature.views:
                    bundle.add_polygon(feature)
            for feature in geometry.polylines:
                if view in feature.views:
                    bundle.add_polyline(feature)

        bundle.scene = geometry.scene
        bundle.build_legend()
        return PlannedView(option=option, view=view, bundle=bundle, view_config=view_config)

    # ------------------------------------------------------------------ #
    def _get_option_geometry(self, option_key: str, option: OptionSpec) -> OptionGeometry:
        if option_key not in self._option_cache:
            self._option_cache[option_key] = self._compute_option_geometry(option)
        return self._option_cache[option_key]

    def _compute_option_geometry(self, option: OptionSpec) -> OptionGeometry:
        context = ViewContext()
        polygons: List[PolygonFeature] = []
        polylines: List[PolylineFeature] = []
        scene = trimesh.Scene()

        for component in option.components:
            if isinstance(component, RectangleComponent):
                for feature in self._plan_rectangle(component, context):
                    feature.views = component.views
                    feature.class_name = apply_material_class(feature.class_name, feature.material)
                    polygons.append(feature)
            elif isinstance(component, PolylineComponent):
                for feature in self._plan_polyline(component, context):
                    feature.views = component.views
                    feature.class_name = apply_material_class(feature.class_name, feature.material)
                    polylines.append(feature)
            else:  # pragma: no cover
                raise TypeError(f"unhandled component type: {type(component)}")

        boolean_map: Dict[str, BooleanConfig] = {
            component.id: component.boolean
            for component in option.components
            if isinstance(component, RectangleComponent) and component.boolean
        }
        geometry = OptionGeometry(polygons=polygons, polylines=polylines, scene=scene)
        if boolean_map:
            self._apply_boolean_operations(boolean_map, geometry, context)
        if option.operations:
            self._apply_operations(option.operations, geometry, context)
            if boolean_map:
                self._apply_boolean_operations(boolean_map, geometry, context)

        self._rebuild_scene(geometry)

        return geometry

    def _apply_operations(
        self,
        operations: Sequence[Operation],
        geometry: OptionGeometry,
        context: ViewContext,
    ) -> None:
        for operation in operations:
            if isinstance(operation, RotateOperation):
                self._apply_rotate_operation(operation, geometry, context)
            elif isinstance(operation, MirrorOperation):
                self._apply_mirror_operation(operation, geometry, context)
            else:  # pragma: no cover - defensive until more operations exist
                raise TypeError(f"unhandled operation type: {operation.type!r}")

    def _apply_boolean_operations(
        self,
        boolean_map: Dict[str, BooleanConfig],
        geometry: OptionGeometry,
        context: ViewContext,
    ) -> None:
        if not boolean_map:
            return

        for feature in geometry.polygons:
            base_id = _base_component_id(feature.id)
            config = boolean_map.get(base_id)
            if not config or not config.subtract:
                continue

            subject = feature.shape
            if subject is None or subject.is_empty:
                continue

            masks: List[ShapelyPolygon] = []
            for target in config.subtract:
                for candidate in geometry.polygons:
                    if candidate.id == feature.id:
                        continue
                    candidate_shape = candidate.shape
                    if candidate_shape is None or candidate_shape.is_empty:
                        continue
                    if _id_matches(
                        candidate.id,
                        target.target,
                        include_generated=target.include_generated,
                    ):
                        masks.append(candidate_shape)

            if not masks:
                continue

            mask_union = unary_union(masks)
            if mask_union.is_empty:
                continue
            mask = mask_union.buffer(0)
            if mask.is_empty:
                continue

            result = subject.difference(mask)
            if result.is_empty:
                feature.outer = ()
                feature.holes = ()
                feature.shape = ShapelyPolygon()
                continue

            if isinstance(result, ShapelyPolygon):
                updated_shape = result
            elif result.geom_type == "MultiPolygon":
                polygons = [
                    geom for geom in result.geoms if isinstance(geom, ShapelyPolygon) and not geom.is_empty
                ]
                if not polygons:
                    feature.outer = ()
                    feature.holes = ()
                    feature.shape = ShapelyPolygon()
                    continue
                if len(polygons) > 1:
                    raise ValueError(
                        f"boolean subtraction on '{feature.id}' produced multiple disjoint polygons; "
                        "split the component or adjust the boolean targets"
                    )
                updated_shape = polygons[0]
            elif isinstance(result, GeometryCollection):
                polygons = [
                    geom for geom in result.geoms if isinstance(geom, ShapelyPolygon) and not geom.is_empty
                ]
                if not polygons:
                    feature.outer = ()
                    feature.holes = ()
                    feature.shape = ShapelyPolygon()
                    continue
                if len(polygons) > 1:
                    raise ValueError(
                        f"boolean subtraction on '{feature.id}' produced multiple disjoint polygons; "
                        "split the component or adjust the boolean targets"
                    )
                updated_shape = polygons[0]
            else:
                raise ValueError(
                    f"boolean subtraction on '{feature.id}' produced unsupported geometry '{result.geom_type}'"
                )

            updated_shape = updated_shape.buffer(0) if not updated_shape.is_empty else updated_shape
            if updated_shape.is_empty:
                feature.outer = ()
                feature.holes = ()
                feature.shape = ShapelyPolygon()
                continue

            feature.shape = updated_shape
            feature.outer = tuple(updated_shape.exterior.coords)
            feature.holes = tuple(tuple(ring.coords) for ring in updated_shape.interiors)

            bounds = _bounds_from_shape(updated_shape)
            context.update_polygon_bounds(feature.id, bounds)
            if feature.id == base_id:
                context.update_polygon_bounds(base_id, bounds)

    def _rebuild_scene(self, geometry: OptionGeometry) -> None:
        scene = trimesh.Scene()
        for feature in geometry.polygons:
            mesh = self._mesh_from_feature(feature)
            if mesh is None:
                continue
            node_name = self._unique_scene_name(scene, feature)
            scene.add_geometry(mesh, node_name=node_name, geom_name=node_name)
        geometry.scene = scene

    def _apply_rotate_operation(
        self,
        operation: RotateOperation,
        geometry: OptionGeometry,
        context: ViewContext,
    ) -> None:
        grouped_polygons: List[List[PolygonFeature]] = []
        grouped_polylines: List[List[PolylineFeature]] = []

        for target in operation.targets:
            polygons = [
                feature
                for feature in geometry.polygons
                if _id_matches(feature.id, target, include_generated=operation.include_generated)
            ]
            polylines = [
                feature
                for feature in geometry.polylines
                if _id_matches(feature.id, target, include_generated=operation.include_generated)
            ]
            if not polygons and not polylines:
                raise ValueError(f"rotate operation target '{target}' did not match any components")
            grouped_polygons.append(polygons)
            grouped_polylines.append(polylines)

        group_bounds = _group_bounds(grouped_polygons, grouped_polylines)
        pivot = self._operation_pivot(operation.about, group_bounds, context)

        start_index = 0 if operation.include_base else 1
        for index in range(start_index, operation.count):
            if operation.include_base and index == 0:
                continue
            rotation_angle = operation.angle * index
            suffix = f"@rot{index}"

            for polygons in grouped_polygons:
                for feature in polygons:
                    new_id = _append_suffix(feature.id, suffix)
                    if _feature_exists(geometry, new_id):
                        continue
                    rotated = self._rotate_polygon_feature(feature, rotation_angle, pivot, new_id)
                    geometry.polygons.append(rotated)
                    if rotated.shape is not None:
                        bounds = _bounds_from_shape(rotated.shape)
                        context.add_polygon(rotated.id, bounds)
                    context.set_vertical(rotated.id, rotated.elevation, rotated.height)

            for polylines in grouped_polylines:
                for feature in polylines:
                    new_id = _append_suffix(feature.id, suffix)
                    if _feature_exists(geometry, new_id):
                        continue
                    rotated = self._rotate_polyline_feature(feature, rotation_angle, pivot, new_id)
                    geometry.polylines.append(rotated)
                    bounds = _points_bounds(rotated.points)
                    context.add_polyline(rotated.id, bounds)
                    context.set_vertical(rotated.id, rotated.elevation, 0.0)

    def _apply_mirror_operation(
        self,
        operation: MirrorOperation,
        geometry: OptionGeometry,
        context: ViewContext,
    ) -> None:
        grouped_polygons: List[List[PolygonFeature]] = []
        grouped_polylines: List[List[PolylineFeature]] = []

        for target in operation.targets:
            polygons = [
                feature
                for feature in geometry.polygons
                if _id_matches(feature.id, target, include_generated=operation.include_generated)
            ]
            polylines = [
                feature
                for feature in geometry.polylines
                if _id_matches(feature.id, target, include_generated=operation.include_generated)
            ]
            if not polygons and not polylines:
                raise ValueError(f"mirror operation target '{target}' did not match any components")
            grouped_polygons.append(polygons)
            grouped_polylines.append(polylines)

        if not grouped_polygons and not grouped_polylines:
            return

        group_bounds = _group_bounds(grouped_polygons, grouped_polylines)
        if operation.axis == "y":
            axis_value = (group_bounds.min_x + group_bounds.max_x) / 2
        else:
            axis_value = (group_bounds.min_y + group_bounds.max_y) / 2

        if operation.about is not None:
            pivot = self._operation_pivot(operation.about, group_bounds, context)
            axis_value = pivot[0] if operation.axis == "y" else pivot[1]

        suffix = "@mirrorY" if operation.axis == "y" else "@mirrorX"

        for polygons in grouped_polygons:
            for feature in polygons:
                new_id = _append_suffix(feature.id, suffix)
                if _feature_exists(geometry, new_id):
                    continue
                mirrored = self._mirror_polygon_feature(feature, operation.axis, axis_value, new_id)
                geometry.polygons.append(mirrored)
                if mirrored.shape is not None and not mirrored.shape.is_empty:
                    bounds = _bounds_from_shape(mirrored.shape)
                    context.add_polygon(mirrored.id, bounds)
                context.set_vertical(mirrored.id, mirrored.elevation, mirrored.height)

        for polylines in grouped_polylines:
            for feature in polylines:
                new_id = _append_suffix(feature.id, suffix)
                if _feature_exists(geometry, new_id):
                    continue
                mirrored = self._mirror_polyline_feature(feature, operation.axis, axis_value, new_id)
                geometry.polylines.append(mirrored)
                bounds = _points_bounds(mirrored.points)
                context.add_polyline(mirrored.id, bounds)
                context.set_vertical(mirrored.id, mirrored.elevation, 0.0)

    def _rotate_polygon_feature(
        self,
        feature: PolygonFeature,
        angle: float,
        pivot: Tuple[float, float],
        new_id: str,
    ) -> PolygonFeature:
        shape = feature.shape
        if shape is None or shape.is_empty:
            shape = ShapelyPolygon(feature.outer[:-1]) if feature.outer else None
        if shape is None:
            raise ValueError(f"polygon feature '{feature.id}' cannot be rotated without geometry")
        rotated = shapely_rotate(shape, angle, origin=pivot, use_radians=False)
        outer = tuple(rotated.exterior.coords)
        holes = tuple(tuple(ring.coords) for ring in rotated.interiors)
        return PolygonFeature(
            id=new_id,
            outer=outer,
            holes=holes,
            label=feature.label,
            label_id=feature.label_id,
            class_name=feature.class_name,
            height=feature.height,
            elevation=feature.elevation,
            material=feature.material,
            metadata=feature.metadata.copy(),
            shape=rotated,
            views=feature.views,
        )

    def _rotate_polyline_feature(
        self,
        feature: PolylineFeature,
        angle: float,
        pivot: Tuple[float, float],
        new_id: str,
    ) -> PolylineFeature:
        shape = feature.shape
        if shape is None or shape.is_empty:
            shape = LineString(feature.points)
        rotated = shapely_rotate(shape, angle, origin=pivot, use_radians=False)
        points = tuple(rotated.coords)
        return PolylineFeature(
            id=new_id,
            points=points,
            stroke_width=feature.stroke_width,
            label=feature.label,
            label_id=feature.label_id,
            class_name=feature.class_name,
            elevation=feature.elevation,
            thickness=feature.thickness,
            material=feature.material,
            metadata=feature.metadata.copy(),
            shape=rotated,
            views=feature.views,
        )

    def _mirror_polygon_feature(
        self,
        feature: PolygonFeature,
        axis: str,
        axis_value: float,
        new_id: str,
    ) -> PolygonFeature:
        shape = feature.shape
        if shape is None or shape.is_empty:
            shape = ShapelyPolygon(feature.outer[:-1]) if feature.outer else None
        if shape is None:
            raise ValueError(f"polygon feature '{feature.id}' cannot be mirrored without geometry")
        mirrored = _mirror_shape(shape, axis, axis_value)
        if mirrored.is_empty:
            raise ValueError(f"mirror operation produced empty geometry for '{feature.id}'")
        outer = tuple(mirrored.exterior.coords)
        holes = tuple(tuple(ring.coords) for ring in mirrored.interiors)
        return PolygonFeature(
            id=new_id,
            outer=outer,
            holes=holes,
            label=feature.label,
            label_id=feature.label_id,
            class_name=feature.class_name,
            height=feature.height,
            elevation=feature.elevation,
            material=feature.material,
            metadata=feature.metadata.copy(),
            shape=mirrored,
            views=feature.views,
        )

    def _mirror_polyline_feature(
        self,
        feature: PolylineFeature,
        axis: str,
        axis_value: float,
        new_id: str,
    ) -> PolylineFeature:
        shape = feature.shape
        if shape is None or shape.is_empty:
            shape = LineString(feature.points)
        mirrored = _mirror_shape(shape, axis, axis_value)
        if mirrored.is_empty:
            raise ValueError(f"mirror operation produced empty geometry for '{feature.id}'")
        if isinstance(mirrored, (MultiLineString, GeometryCollection)):
            raise ValueError(f"mirror operation produced unsupported geometry for '{feature.id}'")
        points = tuple(mirrored.coords)
        return PolylineFeature(
            id=new_id,
            points=points,
            stroke_width=feature.stroke_width,
            label=feature.label,
            label_id=feature.label_id,
            class_name=feature.class_name,
            elevation=feature.elevation,
            thickness=feature.thickness,
            material=feature.material,
            metadata=feature.metadata.copy(),
            shape=mirrored,
            views=feature.views,
        )

    def _operation_pivot(
        self,
        anchor: Optional[Anchor],
        group_bounds: Bounds,
        context: ViewContext,
    ) -> Tuple[float, float]:
        if anchor is None:
            return ((group_bounds.min_x + group_bounds.max_x) / 2, (group_bounds.min_y + group_bounds.max_y) / 2)
        if anchor.ref == "group":
            ref_bounds = group_bounds
        else:
            ref_bounds = context.bounds_for(anchor.ref)
        point = ref_bounds.point(anchor.align)
        return (point[0] + anchor.offset[0], point[1] + anchor.offset[1])

    def _unique_scene_name(self, scene: trimesh.Scene, feature: PolygonFeature) -> str:
        base_name = feature.label_id or feature.id or "feature"
        node_name = base_name
        existing_nodes = set(scene.graph.nodes)
        index = 1
        while node_name in existing_nodes:
            node_name = f"{base_name}#{index}"
            index += 1
        return node_name

    def _mesh_from_feature(self, feature: PolygonFeature) -> Optional[trimesh.Trimesh]:
        if feature.height <= 0.0:
            return None
        if feature.shape is None or feature.shape.is_empty:
            return None

        polygon = feature.shape
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty:
            return None

        try:
            mesh = trimesh.creation.extrude_polygon(polygon, height=feature.height)
        except ValueError:
            return None

        mesh.apply_scale(0.001)
        elevation_m = feature.elevation * 0.001
        if elevation_m:
            mesh.apply_translation((0.0, 0.0, elevation_m))

        style = get_material_style(feature.material)
        if style:
            color = np.tile(np.array(style.rgba255, dtype=np.uint8), (len(mesh.vertices), 1))
            mesh.visual.vertex_colors = color

        mesh.metadata = feature.metadata.copy()
        mesh.metadata.setdefault("id", feature.id)
        mesh.metadata.setdefault("label", feature.label)
        mesh.metadata.setdefault("label_id", feature.label_id)
        mesh.metadata.setdefault("class", feature.class_name)
        if feature.material:
            mesh.metadata.setdefault("material", feature.material)
        return mesh

    def _populate_section_from_plane(
        self,
        bundle: GeometryBundle,
        geometry: OptionGeometry,
        plane: PlaneSpec,
    ) -> None:
        if plane.axis not in {"x", "y"}:
            raise ValueError("Section plane axis must be 'x' or 'y'")

        coord = plane.coordinate
        if plane.axis == "x":
            slice_line = LineString([(coord, -1e5), (coord, 1e5)])
            axis_index = 1  # use y coordinate
            label_axis = "y"
        else:
            slice_line = LineString([(-1e5, coord), (1e5, coord)])
            axis_index = 0  # use x coordinate
            label_axis = "x"

        segments: List[Tuple[PolygonFeature, float, float]] = []
        min_coord = float("inf")
        max_coord = float("-inf")

        for feature in geometry.polygons:
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
                max_coord = max(max_coord, start_coord + length)

        if not segments:
            return

        segments.sort(key=lambda item: item[1])

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

        shift = -min_coord if min_coord != float("inf") else 0.0
        if shift:
            for feature in bundle.polygons:
                shifted = [(x + shift, y) for x, y in feature.outer]
                feature.outer = tuple(shifted)
                if isinstance(feature.shape, ShapelyPolygon):
                    feature.shape = ShapelyPolygon(shifted[:-1])

    # ------------------------------------------------------------------ #
    def _plan_rectangle(
        self, component: RectangleComponent, context: ViewContext
    ) -> Iterable[PolygonFeature]:
        origin = self._resolve_origin(component, context)
        features: List[PolygonFeature] = []
        repeat = component.repeat
        total = repeat.count if repeat else 1
        instance_index = 0
        resolved_elevation = self._resolve_component_vertical(component, context)
        component_height = component.height or 0.0

        for repeat_index in range(total):
            if repeat and not repeat.include_base and repeat_index == 0:
                continue

            if repeat:
                dx = repeat.spacing[0] * repeat_index
                dy = repeat.spacing[1] * repeat_index
            else:
                dx = dy = 0.0

            position = (origin[0] + dx, origin[1] + dy)
            feature_id = component.id if instance_index == 0 else f"{component.id}#{instance_index}"
            outer = create_rectangle(position, component.size)
            parent_bounds = bounds_from_origin(position, component.size)
            holes: List[Tuple[Tuple[float, float], ...]] = []
            shapely_holes: List[Sequence[Tuple[float, float]]] = []
            material_key = component.material or _metadata_str(component.metadata, "material")

            for cutout in component.cutouts:
                cutout_origin = self._resolve_cutout_origin(
                    cutout_anchor=cutout.anchor,
                    cutout_size=cutout.size,
                    context=context,
                    parent_bounds=parent_bounds,
                )
                cutout_polygon = create_rectangle(cutout_origin, cutout.size)
                holes.append(cutout_polygon)
                shapely_holes.append(cutout_polygon[:-1])

            polygon = ShapelyPolygon(outer[:-1], shapely_holes if shapely_holes else None)

            rotation_angle = component.rotation
            if repeat:
                rotation_angle += repeat.rotate * repeat_index

            if rotation_angle:
                rotation_anchor = (repeat.about if repeat else None) or component.rotation_anchor
                pivot = self._resolve_rotation_point(rotation_anchor, context, parent_bounds)
                polygon = shapely_rotate(polygon, rotation_angle, origin=pivot, use_radians=False)
                outer = tuple(polygon.exterior.coords)
                holes = tuple(tuple(ring.coords) for ring in polygon.interiors)
            else:
                holes = tuple(holes)
                polygon = polygon

            features.append(
                PolygonFeature(
                    id=feature_id,
                    outer=outer,
                    holes=holes,
                    label=component.label,
                    label_id=component.label_id,
                    class_name=component.class_name,
                    height=component_height,
                    elevation=resolved_elevation,
                    material=material_key,
                    metadata=component.metadata.copy(),
                    shape=polygon,
                )
            )
            bounds_tuple = polygon.bounds
            bounds = Bounds(min_x=bounds_tuple[0], min_y=bounds_tuple[1], max_x=bounds_tuple[2], max_y=bounds_tuple[3])
            context.add_polygon(component.id, bounds)
            context.add_polygon(feature_id, bounds)
            context.set_vertical(component.id, resolved_elevation, component_height)
            context.set_vertical(feature_id, resolved_elevation, component_height)
            instance_index += 1
        return features

    def _plan_polyline(
        self, component: PolylineComponent, context: ViewContext
    ) -> Iterable[PolylineFeature]:
        points = list(component.points)
        if component.origin:
            points = [(x + component.origin[0], y + component.origin[1]) for x, y in points]

        if component.anchor:
            bounds = _points_bounds(points)
            ref_bounds = context.bounds_for(component.anchor.ref)
            ref_point = ref_bounds.point(component.anchor.align)
            offset_self = alignment_offset(
                (bounds.width, bounds.height), component.anchor.anchor_point
            )
            self_point = (bounds.min_x + offset_self[0], bounds.min_y + offset_self[1])
            dx = ref_point[0] - self_point[0] + component.anchor.offset[0]
            dy = ref_point[1] - self_point[1] + component.anchor.offset[1]
            points = [(x + dx, y + dy) for x, y in points]
            bounds = _points_bounds(points)
        else:
            bounds = _points_bounds(points)

        rotation_angle = component.rotation
        if rotation_angle:
            rotation_anchor = component.rotation_anchor
            pivot = self._resolve_rotation_point(rotation_anchor, context, bounds)
            line = shapely_rotate(LineString(points), rotation_angle, origin=pivot, use_radians=False)
            points = list(line.coords)
            bounds = _points_bounds(points)
            shape = line
        else:
            shape = LineString(points)

        context.add_polyline(component.id, bounds)
        resolved_elevation = self._resolve_component_vertical(component, context)
        component_height = component.height or 0.0
        context.set_vertical(component.id, resolved_elevation, component_height)
        material_key = component.material or _metadata_str(component.metadata, "material")
        return [
            PolylineFeature(
                id=component.id,
                points=tuple(points),
                stroke_width=component.stroke_width,
                label=component.label,
                label_id=component.label_id,
                class_name=component.class_name,
                elevation=resolved_elevation,
                thickness=_metadata_float(component.metadata, "thickness"),
                material=material_key,
                metadata=component.metadata.copy(),
                shape=shape,
            )
        ]

    # ------------------------------------------------------------------ #
    def _resolve_origin(
        self, component: RectangleComponent, context: ViewContext
    ) -> Tuple[float, float]:
        if component.origin is not None:
            return component.origin
        if component.anchor is None:
            return (0.0, 0.0)
        if component.anchor.ref == "self":
            raise ValueError(f"component '{component.id}' cannot anchor to itself")

        ref_bounds = context.bounds_for(component.anchor.ref)
        ref_point = ref_bounds.point(component.anchor.align)
        offset_self = alignment_offset(component.size, component.anchor.anchor_point)
        x = ref_point[0] - offset_self[0] + component.anchor.offset[0]
        y = ref_point[1] - offset_self[1] + component.anchor.offset[1]
        return (x, y)

    def _resolve_cutout_origin(
        self,
        cutout_anchor: Anchor,
        cutout_size: Tuple[float, float],
        context: ViewContext,
        parent_bounds: Bounds,
    ) -> Tuple[float, float]:
        ref_bounds = parent_bounds if cutout_anchor.ref == "self" else context.bounds_for(cutout_anchor.ref)
        ref_point = ref_bounds.point(cutout_anchor.align)
        offset_self = alignment_offset(cutout_size, cutout_anchor.anchor_point)
        x = ref_point[0] - offset_self[0] + cutout_anchor.offset[0]
        y = ref_point[1] - offset_self[1] + cutout_anchor.offset[1]
        return (x, y)

    def _resolve_component_vertical(
        self,
        component: ComponentBase,
        context: ViewContext,
    ) -> float:
        base_elevation = _metadata_float(component.metadata, "elevation")
        placement = component.vertical
        if placement is None:
            return base_elevation
        try:
            ref_elevation, ref_height = context.vertical_for(placement.ref)
        except KeyError as exc:
            raise ValueError(
                f"component '{component.id}' vertical placement reference '{placement.ref}' has not been resolved yet"
            ) from exc
        component_height = component.height or 0.0
        elevation = placement.resolve(ref_elevation, ref_height, component_height)
        component.metadata["elevation"] = elevation
        return elevation

    def _resolve_rotation_point(
        self,
        anchor: Optional[Anchor],
        context: ViewContext,
        bounds: Bounds,
    ) -> Tuple[float, float]:
        if anchor is None:
            return ((bounds.min_x + bounds.max_x) / 2, (bounds.min_y + bounds.max_y) / 2)
        if anchor.ref == "self":
            ref_bounds = bounds
        else:
            ref_bounds = context.bounds_for(anchor.ref)
        point = ref_bounds.point(anchor.align)
        return (point[0] + anchor.offset[0], point[1] + anchor.offset[1])


def _mirror_shape(geometry: GeometryCollection | ShapelyPolygon | LineString, axis: str, axis_value: float):
    if axis == "y":
        return shapely_scale(geometry, xfact=-1.0, yfact=1.0, origin=(axis_value, 0.0))
    return shapely_scale(geometry, xfact=1.0, yfact=-1.0, origin=(0.0, axis_value))


def _points_bounds(points: Sequence[Tuple[float, float]]) -> Bounds:
    xs = [pt[0] for pt in points]
    ys = [pt[1] for pt in points]
    return Bounds(min(xs), min(ys), max(xs), max(ys))


def _id_matches(feature_id: str, target: str, include_generated: bool = False) -> bool:
    if feature_id == target:
        return True
    if feature_id.startswith(f"{target}#"):
        return True
    if include_generated and feature_id.startswith(f"{target}@"):
        return True
    return False


def _base_component_id(feature_id: str) -> str:
    index_hash = feature_id.find("#")
    index_at = feature_id.find("@")
    indices = [idx for idx in (index_hash, index_at) if idx != -1]
    if not indices:
        return feature_id
    return feature_id[: min(indices)]


def _append_suffix(base_id: str, suffix: str) -> str:
    if not suffix:
        return base_id
    return f"{base_id}{suffix}"


def _bounds_from_shape(shape: ShapelyPolygon) -> Bounds:
    min_x, min_y, max_x, max_y = shape.bounds
    return Bounds(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)


def _group_bounds(
    grouped_polygons: Sequence[Sequence[PolygonFeature]],
    grouped_polylines: Sequence[Sequence[PolylineFeature]],
) -> Bounds:
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    for polygons in grouped_polygons:
        for feature in polygons:
            shape = feature.shape
            if shape is None or shape.is_empty:
                shape = ShapelyPolygon(feature.outer[:-1]) if feature.outer else None
            if shape is None or shape.is_empty:
                continue
            bounds = shape.bounds
            min_x = min(min_x, bounds[0])
            min_y = min(min_y, bounds[1])
            max_x = max(max_x, bounds[2])
            max_y = max(max_y, bounds[3])

    for polylines in grouped_polylines:
        for feature in polylines:
            shape = feature.shape
            if shape is None or shape.is_empty:
                shape = LineString(feature.points)
            bounds = shape.bounds
            min_x = min(min_x, bounds[0])
            min_y = min(min_y, bounds[1])
            max_x = max(max_x, bounds[2])
            max_y = max(max_y, bounds[3])

    if min_x == float("inf") or min_y == float("inf"):
        raise ValueError("rotate operation group has no geometry to transform")

    return Bounds(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)


def _feature_exists(geometry: OptionGeometry, feature_id: str) -> bool:
    return any(feature.id == feature_id for feature in geometry.polygons) or any(
        feature.id == feature_id for feature in geometry.polylines
    )


def _metadata_float(metadata: Dict[str, object], key: str) -> float:
    value = metadata.get(key)
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _metadata_str(metadata: Dict[str, object], key: str) -> Optional[str]:
    value = metadata.get(key)
    if value is None:
        return None
    return str(value)


def _iter_line_segments(geometry: object) -> Iterable[LineString]:
    if isinstance(geometry, LineString):
        yield geometry
    elif isinstance(geometry, MultiLineString):
        for item in geometry.geoms:
            yield from _iter_line_segments(item)
    elif isinstance(geometry, GeometryCollection):
        for item in geometry.geoms:
            yield from _iter_line_segments(item)


def _section_polygon(
    length: float,
    elevation: float,
    height: float,
    offset_x: float,
    axis: str,
) -> Tuple[Tuple[float, float], ...]:
    z_base = -elevation
    z_top = -(elevation + height)
    if z_top < z_base:
        z_base, z_top = z_top, z_base
    return (
        (offset_x, z_base),
        (offset_x + length, z_base),
        (offset_x + length, z_top),
        (offset_x, z_top),
        (offset_x, z_base),
    )
