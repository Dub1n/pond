from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import cadquery as cq
import numpy as np
from shapely.geometry import MultiPoint, Polygon as ShapelyPolygon
import trimesh

from .schema import (
    AlignmentClause,
    FlushBundleClause,
    IfcMetadata,
    RelationshipComponent,
    RelationshipDiagramSpec,
    RunBetweenClause,
)


GUID_NAMESPACE = uuid.UUID("6c7b3d9e-4f21-4b06-9fbf-2a6e2d6a8b2c")

AxisSign = int
AxisName = str
MM_TO_METERS = 0.001


def _axes_from_pos(pos_token: str) -> List[Tuple[AxisName, AxisSign]]:
    axes: List[Tuple[AxisName, AxisSign]] = []
    token = pos_token.strip()
    if len(token) % 2 != 0:
        return axes
    for i in range(0, len(token), 2):
        sign_char = token[i]
        axis = token[i + 1]
        sign = 1 if sign_char == "+" else -1
        axes.append((axis, sign))
    return axes


def _half_size(component: RelationshipComponent, axis: str) -> float:
    if axis == "x":
        return component.size_xy[0] / 2
    if axis == "y":
        return component.size_xy[1] / 2
    return component.height / 2


def _component_size(component: RelationshipComponent) -> Tuple[float, float, float]:
    return (component.size_xy[0], component.size_xy[1], component.height)


def _ifc_to_dict(ifc: Optional[IfcMetadata]) -> Optional[Dict[str, object]]:
    if ifc is None:
        return None
    return ifc.to_dict()


@dataclass(slots=True)
class Diagnostic:
    level: str
    message: str
    subject: Optional[str] = None


@dataclass(slots=True)
class SolveDiagnostics:
    errors: List[Diagnostic] = field(default_factory=list)
    warnings: List[Diagnostic] = field(default_factory=list)
    degrees_of_freedom: Dict[str, int] = field(default_factory=dict)
    check_results: List[str] = field(default_factory=list)
    constraint_graph: Dict[str, List[str]] = field(default_factory=dict)

    def add_error(self, message: str, *, subject: Optional[str] = None) -> None:
        self.errors.append(Diagnostic(level="error", message=message, subject=subject))

    def add_warning(self, message: str, *, subject: Optional[str] = None) -> None:
        self.warnings.append(Diagnostic(level="warning", message=message, subject=subject))

    def record_graph_edge(self, source: str, target: str) -> None:
        if not target:
            return
        self.constraint_graph.setdefault(source, [])
        if target not in self.constraint_graph[source]:
            self.constraint_graph[source].append(target)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(slots=True)
class ComponentTransform:
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass(slots=True)
class ComponentState:
    id: str
    size: Tuple[float, float, float]
    transform: ComponentTransform
    class_name: Optional[str]


@dataclass(slots=True)
class NeutralPrimitive:
    id: str
    class_name: Optional[str]
    size: Tuple[float, float, float]
    material: Optional[str]
    metadata: Dict[str, object]
    transform: ComponentTransform
    guid: str
    solid: Optional[Any] = None
    footprint: Optional[ShapelyPolygon] = None
    ifc: Optional[Dict[str, object]] = None


@dataclass(slots=True)
class SolvedComponent:
    component: RelationshipComponent
    instance_id: str
    transform: ComponentTransform
    primitive: NeutralPrimitive
    guid: str


@dataclass(slots=True)
class SolveResult:
    components: Tuple[SolvedComponent, ...]
    diagnostics: SolveDiagnostics
    primitives: Tuple[NeutralPrimitive, ...]
    scene: Optional[trimesh.Scene] = None


@dataclass(slots=True)
class InstanceState:
    name: str
    axis_values: Dict[str, float] = field(default_factory=dict)
    rotation_z: float = 0.0


class ReferenceResolver:
    def __init__(
        self,
        spec: RelationshipDiagramSpec,
        component_states: Mapping[str, ComponentState],
        datum_points: Mapping[str, Dict[str, float]],
        datum_planes: Mapping[str, Dict[str, float]],
        datum_bundles: Mapping[str, Dict[str, object]],
    ) -> None:
        self.spec = spec
        self.component_states = component_states
        self.datum_points = datum_points
        self.datum_planes = datum_planes
        self.datum_bundles = datum_bundles

    def coords_for_ref(self, ref: str) -> Optional[Dict[str, float]]:
        if ref in self.component_states:
            pos = self.component_states[ref].transform.position
            return {"x": pos[0], "y": pos[1], "z": pos[2]}
        if ref in self.datum_points:
            return self.datum_points[ref]
        if ref in self.datum_planes:
            return self.datum_planes[ref]
        if ref in self.datum_bundles:
            origin = self.datum_bundles[ref].get("origin", {})
            return origin if isinstance(origin, dict) else None
        return None

    def axis_coordinate(
        self,
        ref: str,
        axis: str,
        sign: int,
    ) -> Optional[float]:
        if ref in self.component_states:
            state = self.component_states[ref]
            half = state.size[0] / 2 if axis == "x" else state.size[1] / 2 if axis == "y" else state.size[2] / 2
            base = state.transform.position[0] if axis == "x" else state.transform.position[1] if axis == "y" else state.transform.position[2]
            return base + sign * half

        if ref in self.datum_bundles:
            bundle = self.datum_bundles[ref]
            origin = bundle["origin"]
            span = bundle["span"]
            if axis not in origin:
                return None
            base = origin.get(axis, 0.0)
            if sign > 0:
                return base + span.get(f"+{axis}", span.get(axis, 0.0))
            return base

        if ref in self.datum_planes:
            coords = self.datum_planes[ref]
            return coords.get(axis, None)

        if ref in self.datum_points:
            coords = self.datum_points[ref]
            return coords.get(axis, None)

        return None


class ConstraintSolver:
    """
    Resolves relationship-first specs into deterministic transforms and neutral
    primitives. Supports box primitives only.
    """

    def __init__(self, spec: RelationshipDiagramSpec) -> None:
        self.spec = spec
        self.datum_points = self._build_points(spec)
        self.datum_planes = self._build_planes(spec)
        self.datum_bundles = self._build_bundles(spec, self.datum_points, self.datum_planes)

    def solve(self) -> SolveResult:
        diagnostics = SolveDiagnostics()
        component_states: Dict[str, ComponentState] = {}
        solved: List[SolvedComponent] = []

        if self.spec.assemblies:
            diagnostics.add_warning(
                "Assembly calls are not yet expanded in the solver output.",
                subject="assemblies",
            )

        resolver = ReferenceResolver(self.spec, component_states, self.datum_points, self.datum_planes, self.datum_bundles)

        for component in self.spec.components:
            solved_instances = self._solve_component(component, resolver, component_states, diagnostics)
            solved.extend(solved_instances)

        self._evaluate_checks(resolver, diagnostics)

        primitives = tuple(item.primitive for item in solved)
        scene = self._build_scene(primitives)
        return SolveResult(components=tuple(solved), diagnostics=diagnostics, primitives=primitives, scene=scene)

    # ------------------------------------------------------------------ #
    def _solve_component(
        self,
        component: RelationshipComponent,
        resolver: ReferenceResolver,
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
    ) -> List[SolvedComponent]:
        instances: List[InstanceState] = [InstanceState(name=component.id)]

        run_between_clause = next((c for c in component.relationships if isinstance(c, RunBetweenClause)), None)
        if run_between_clause:
            instances = self._apply_run_between(component, run_between_clause, resolver, diagnostics)
            diagnostics.record_graph_edge(component.id, run_between_clause.from_ref.ref)
            diagnostics.record_graph_edge(component.id, run_between_clause.to_ref.ref)

        instances = self._apply_relationships(component, instances, resolver, diagnostics)
        instances = self._apply_repeat(component, instances, resolver, diagnostics)

        solved_components: List[SolvedComponent] = []
        for idx, instance in enumerate(instances):
            transform, dof = self._finalise_transform(component, instance, diagnostics)
            guid = self._stable_guid(component.id, instance.name)
            primitive = self._neutral_primitive(component, instance.name, transform, guid)
            solved_components.append(
                SolvedComponent(
                    component=component,
                    instance_id=instance.name,
                    transform=transform,
                    primitive=primitive,
                    guid=guid,
                )
            )
            component_states[instance.name] = ComponentState(
                id=instance.name,
                size=_component_size(component),
                transform=transform,
                class_name=component.class_name,
            )
            if component.id not in component_states:
                component_states[component.id] = component_states[instance.name]
            diagnostics.degrees_of_freedom[instance.name] = dof
        return solved_components

    def _apply_run_between(
        self,
        component: RelationshipComponent,
        clause: RunBetweenClause,
        resolver: ReferenceResolver,
        diagnostics: SolveDiagnostics,
    ) -> List[InstanceState]:
        start_axes = _axes_from_pos(clause.start_pos)
        end_axes = _axes_from_pos(clause.end_pos)

        def point_for(target_ref: str, axes: List[Tuple[str, int]]) -> Dict[str, float]:
            coords: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
            for axis, sign in axes:
                value = resolver.axis_coordinate(target_ref, axis, sign)
                if value is None:
                    diagnostics.add_error(
                        f"component '{component.id}' run_between references unknown target '{target_ref}' on {axis}",
                        subject=component.id,
                    )
                    continue
                coords[axis] = value
            return coords

        start_point = point_for(clause.from_ref.ref, start_axes)
        end_point = point_for(clause.to_ref.ref, end_axes if end_axes else start_axes)

        direction = (
            end_point["x"] - start_point["x"],
            end_point["y"] - start_point["y"],
            end_point["z"] - start_point["z"],
        )
        length = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
        if length <= 1e-6:
            diagnostics.add_error(
                f"component '{component.id}' run_between has zero-length span",
                subject=component.id,
            )
            length = 1.0

        unit = (direction[0] / length, direction[1] / length, direction[2] / length)
        inset_start = clause.inset_start or 0.0
        inset_end = clause.inset_end or 0.0
        effective_length = max(length - inset_start - inset_end, 0.0)

        positions: List[Tuple[float, float, float]] = []
        if clause.count:
            step = effective_length / max(clause.count - 1, 1)
            for i in range(clause.count):
                offset = inset_start + step * i
                positions.append(
                    (
                        start_point["x"] + unit[0] * offset,
                        start_point["y"] + unit[1] * offset,
                        start_point["z"] + unit[2] * offset,
                    )
                )
        elif clause.pitch:
            step = clause.pitch
            if step <= 0:
                diagnostics.add_error(f"component '{component.id}' run_between pitch must be positive", subject=component.id)
                step = effective_length or 1.0
            current = 0.0
            while current <= effective_length + 1e-6:
                offset = inset_start + current
                positions.append(
                    (
                        start_point["x"] + unit[0] * offset,
                        start_point["y"] + unit[1] * offset,
                        start_point["z"] + unit[2] * offset,
                    )
                )
                current += step
        else:
            positions.append(
                (
                    start_point["x"] + unit[0] * inset_start,
                    start_point["y"] + unit[1] * inset_start,
                    start_point["z"] + unit[2] * inset_start,
                )
            )
            positions.append(
                (
                    end_point["x"] - unit[0] * inset_end,
                    end_point["y"] - unit[1] * inset_end,
                    end_point["z"] - unit[2] * inset_end,
                )
            )

        rotation = 0.0
        if clause.orient == "along_run":
            rotation = math.degrees(math.atan2(direction[1], direction[0]))

        instances: List[InstanceState] = []
        for idx, pos in enumerate(positions):
            axis_values = {"x": pos[0], "y": pos[1], "z": pos[2]}
            name = component.id if idx == 0 else f"{component.id}#{idx}"
            instances.append(InstanceState(name=name, axis_values=axis_values, rotation_z=rotation))
        return instances

    def _apply_relationships(
        self,
        component: RelationshipComponent,
        instances: List[InstanceState],
        resolver: ReferenceResolver,
        diagnostics: SolveDiagnostics,
    ) -> List[InstanceState]:
        for clause in component.relationships:
            if isinstance(clause, AlignmentClause):
                for instance in instances:
                    self._apply_alignment_clause(component, instance, clause, resolver, diagnostics)
                diagnostics.record_graph_edge(component.id, clause.obj.ref)
            elif isinstance(clause, FlushBundleClause):
                for instance in instances:
                    self._apply_flush_clause(component, instance, clause, resolver, diagnostics)
                diagnostics.record_graph_edge(component.id, clause.bundle)
            elif isinstance(clause, RunBetweenClause):
                continue
            else:
                diagnostics.add_warning(
                    f"component '{component.id}' uses unsupported helper '{type(clause).__name__}'",
                    subject=component.id,
                )
        return instances

    def _apply_alignment_clause(
        self,
        component: RelationshipComponent,
        instance: InstanceState,
        clause: AlignmentClause,
        resolver: ReferenceResolver,
        diagnostics: SolveDiagnostics,
    ) -> None:
        subject_axes = _axes_from_pos(clause.subject.pos)
        object_axes = {axis: sign for axis, sign in _axes_from_pos(clause.obj.pos)}

        for axis, subject_sign in subject_axes:
            object_sign = object_axes.get(axis, subject_sign)
            target_coord = resolver.axis_coordinate(clause.obj.ref, axis, object_sign)
            if target_coord is None:
                diagnostics.add_error(
                    f"component '{component.id}' alignment references unknown target '{clause.obj.ref}'",
                    subject=component.id,
                )
                continue

            half = _half_size(component, axis)
            gap_direction = 1.0 if subject_sign > 0 else -1.0
            face_target = target_coord + clause.gap * gap_direction
            origin_value = face_target - gap_direction * half
            self._set_axis(instance, axis, origin_value, clause.tolerance, component.id, diagnostics)

    def _apply_flush_clause(
        self,
        component: RelationshipComponent,
        instance: InstanceState,
        clause: FlushBundleClause,
        resolver: ReferenceResolver,
        diagnostics: SolveDiagnostics,
    ) -> None:
        for face in clause.faces:
            subject_axes = _axes_from_pos(face.subject)
            object_axes = {axis: sign for axis, sign in _axes_from_pos(face.obj)}
            for axis, subject_sign in subject_axes:
                object_sign = object_axes.get(axis, subject_sign)
                target_coord = resolver.axis_coordinate(clause.bundle, axis, object_sign)
                if target_coord is None:
                    diagnostics.add_error(
                        f"component '{component.id}' flush_bundle references unknown bundle '{clause.bundle}'",
                        subject=component.id,
                    )
                    continue
                inset_subject = clause.inset_subject.get(face.subject, 0.0)
                inset_object = clause.inset_object.get(face.obj, 0.0)
                effective_gap = inset_object - inset_subject
                half = _half_size(component, axis)
                gap_direction = 1.0 if subject_sign > 0 else -1.0
                face_target = target_coord + effective_gap * gap_direction
                origin_value = face_target - gap_direction * half
                self._set_axis(instance, axis, origin_value, 0.5, component.id, diagnostics)

    def _apply_repeat(
        self,
        component: RelationshipComponent,
        instances: List[InstanceState],
        resolver: ReferenceResolver,
        diagnostics: SolveDiagnostics,
    ) -> List[InstanceState]:
        repeat = component.repeat
        if repeat is None:
            return instances

        axis = repeat.axis[-1]
        sign = 1 if repeat.axis[0] == "+" else -1

        span_length = self._span_length(repeat.span_use, resolver)
        if repeat.span_use:
            diagnostics.record_graph_edge(component.id, repeat.span_use)
        if repeat.span_use and span_length is None:
            diagnostics.add_error(
                f"component '{component.id}' repeat span reference '{repeat.span_use}' could not be resolved",
                subject=component.id,
            )
        available_length = None
        if span_length is not None:
            available_length = max(span_length - repeat.inset_start - repeat.inset_end, 0.0)

        pitch = repeat.pitch
        if pitch is None and available_length is not None and repeat.count and repeat.count > 1:
            pitch = available_length / (repeat.count - 1)

        expanded: List[InstanceState] = []
        for base in instances:
            base_value = base.axis_values.get(axis, 0.0) + sign * repeat.inset_start
            total = repeat.count or 1
            step = pitch or 0.0
            if step == 0.0 and available_length is not None and total > 1:
                step = available_length / (total - 1)
            for idx in range(total):
                if idx == 0 and not repeat.include_seed:
                    continue
                offset = step * idx
                axis_values = dict(base.axis_values)
                axis_values[axis] = base_value + sign * offset
                name = base.name if not expanded else f"{component.id}#{len(expanded)}"
                expanded.append(InstanceState(name=name, axis_values=axis_values, rotation_z=base.rotation_z))
        return expanded or instances

    def _span_length(self, span_use: Optional[str], resolver: ReferenceResolver) -> Optional[float]:
        if span_use is None:
            return None
        ref = span_use
        if ref.endswith(".x"):
            key = ref[:-2]
            axis = "x"
        elif ref.endswith(".y"):
            key = ref[:-2]
            axis = "y"
        else:
            return None
        if key in self.datum_bundles:
            span = self.datum_bundles[key]["span"]
            if isinstance(span, dict):
                return span.get(f"+{axis}", span.get(axis, None))
        coords = resolver.coords_for_ref(key)
        if coords is not None and axis in coords:
            return coords[axis]
        return None

    def _set_axis(
        self,
        instance: InstanceState,
        axis: str,
        value: float,
        tolerance: float,
        component_id: str,
        diagnostics: SolveDiagnostics,
    ) -> None:
        existing = instance.axis_values.get(axis)
        if existing is None:
            instance.axis_values[axis] = value
            return
        if abs(existing - value) > tolerance:
            diagnostics.add_error(
                f"component '{component_id}' is over-constrained on {axis} (values {existing:.3f} vs {value:.3f})",
                subject=component_id,
            )
        else:
            instance.axis_values[axis] = (existing + value) / 2

    def _finalise_transform(
        self,
        component: RelationshipComponent,
        instance: InstanceState,
        diagnostics: SolveDiagnostics,
    ) -> Tuple[ComponentTransform, int]:
        axis_values = dict(instance.axis_values)
        dof = 0
        for axis in ("x", "y", "z"):
            if axis not in axis_values:
                axis_values[axis] = 0.0
                dof += 1
        if dof:
            diagnostics.add_error(
                f"component '{component.id}' remains under-constrained on {dof} axis/axes",
                subject=component.id,
            )
        transform = ComponentTransform(
            position=(axis_values["x"], axis_values["y"], axis_values["z"]),
            rotation=(0.0, 0.0, instance.rotation_z),
        )
        return transform, dof

    def _neutral_primitive(
        self,
        component: RelationshipComponent,
        instance_id: str,
        transform: ComponentTransform,
        guid: str,
    ) -> NeutralPrimitive:
        metadata = dict(component.metadata)
        metadata.setdefault("id", instance_id)
        metadata.setdefault("class", component.class_name)
        metadata.setdefault("guid", guid)
        if component.ifc:
            ifc_dict = component.ifc.to_dict()
            if ifc_dict:
                metadata.setdefault("ifc", ifc_dict)
        if component.description:
            metadata.setdefault("description", component.description)
        solid, footprint = self._build_cadquery_block(component, transform)
        return NeutralPrimitive(
            id=instance_id,
            class_name=component.class_name,
            size=_component_size(component),
            material=component.material,
            metadata=metadata,
            transform=transform,
            guid=guid,
            solid=solid,
            footprint=footprint,
            ifc=_ifc_to_dict(component.ifc),
        )

    def _build_cadquery_block(
        self,
        component: RelationshipComponent,
        transform: ComponentTransform,
    ) -> Tuple[Optional[Any], Optional[ShapelyPolygon]]:
        if component.height <= 0.0 or component.size_xy[0] <= 0.0 or component.size_xy[1] <= 0.0:
            return None, None

        wp = cq.Workplane("XY").box(component.size_xy[0], component.size_xy[1], component.height, centered=True)
        rotation_z = transform.rotation[2]
        if rotation_z:
            wp = wp.rotate((0, 0, 0), (0, 0, 1), rotation_z)
        pos = transform.position
        wp = wp.translate((pos[0], pos[1], pos[2]))
        solid = wp.val()

        try:
            vertices, _faces = solid.tessellate(0.5)
        except Exception:
            return solid, None

        if not vertices:
            return solid, None

        hull = MultiPoint([(vec.x, vec.y) for vec in vertices]).convex_hull
        if hull.is_empty or not isinstance(hull, ShapelyPolygon):
            return solid, None
        return solid, hull

    def _evaluate_checks(self, resolver: ReferenceResolver, diagnostics: SolveDiagnostics) -> None:
        for clause in self.spec.checks:
            subject_axes = _axes_from_pos(clause.subject.pos)
            object_axes = {axis: sign for axis, sign in _axes_from_pos(clause.obj.pos)}
            passed = True
            for axis, subject_sign in subject_axes:
                object_sign = object_axes.get(axis, subject_sign)
                subject_coord = resolver.axis_coordinate(clause.subject.ref, axis, subject_sign)
                object_coord = resolver.axis_coordinate(clause.obj.ref, axis, object_sign)
                if subject_coord is None or object_coord is None:
                    diagnostics.add_error(
                        f"check '{clause.kind}' references unknown target(s)",
                        subject=clause.subject.ref,
                    )
                    passed = False
                    continue
                gap_direction = 1.0 if subject_sign > 0 else -1.0
                expected = object_coord + clause.gap * gap_direction
                if abs(subject_coord - expected) > clause.tolerance:
                    diagnostics.add_error(
                        f"check failed between '{clause.subject.ref}' and '{clause.obj.ref}' on axis {axis}",
                        subject=clause.subject.ref,
                    )
                    passed = False
            result_text = "PASS" if passed else "FAIL"
            diagnostics.check_results.append(f"{result_text}: {clause.kind} {clause.subject.ref}→{clause.obj.ref}")

    def _build_scene(self, primitives: Sequence[NeutralPrimitive]) -> trimesh.Scene:
        scene = trimesh.Scene()
        for primitive in primitives:
            mesh = self._mesh_from_primitive(primitive)
            if mesh is None:
                continue
            mesh.metadata = primitive.metadata.copy()
            mesh.metadata.setdefault("guid", primitive.guid)
            scene.add_geometry(mesh, node_name=primitive.id)
        return scene

    def _mesh_from_primitive(self, primitive: NeutralPrimitive) -> Optional[trimesh.Trimesh]:
        if primitive.solid is not None:
            try:
                vectors, faces = primitive.solid.tessellate(0.5)
            except Exception:
                vectors, faces = (), ()
            if vectors and faces:
                mesh = trimesh.Trimesh(
                    vertices=np.array([[v.x, v.y, v.z] for v in vectors]) * MM_TO_METERS,
                    faces=np.array(faces),
                    process=False,
                )
                return mesh

        if primitive.size[2] <= 0.0:
            return None
        mesh = trimesh.creation.box(extents=np.array(primitive.size) * MM_TO_METERS)
        rotation_z = primitive.transform.rotation[2]
        if rotation_z:
            rot = trimesh.transformations.rotation_matrix(math.radians(rotation_z), [0, 0, 1])
            mesh.apply_transform(rot)
        pos = primitive.transform.position
        mesh.apply_translation((pos[0] * MM_TO_METERS, pos[1] * MM_TO_METERS, pos[2] * MM_TO_METERS))
        return mesh

    # ------------------------------------------------------------------ #
    def _build_points(self, spec: RelationshipDiagramSpec) -> Dict[str, Dict[str, float]]:
        points: Dict[str, Dict[str, float]] = {}
        for name, point in spec.datums.items():
            coords: Dict[str, float] = {}
            for axis_token, value in point.coordinates.items():
                axis = axis_token[-1]
                coords[axis] = value
            self._register_ref(points, name, coords, category="points")
        return points

    def _build_planes(
        self, spec: RelationshipDiagramSpec
    ) -> Dict[str, Dict[str, float]]:
        planes: Dict[str, Dict[str, float]] = {}

        def resolve(name: str) -> Dict[str, float]:
            if name in planes:
                return planes[name]
            plane = spec.planes[name]
            base_coords = self._coords_from_ref(plane.base, {**planes, **self.datum_points})
            coords = dict(base_coords)
            axis = plane.normal[-1]
            sign = 1.0 if plane.normal[0] == "+" else -1.0
            coords[axis] = coords.get(axis, 0.0) + sign * plane.offset
            self._register_ref(planes, name, coords, category="planes")
            return coords

        for name in spec.planes.keys():
            resolve(name)
        return planes

    def _build_bundles(
        self,
        spec: RelationshipDiagramSpec,
        points: Mapping[str, Dict[str, float]],
        planes: Mapping[str, Dict[str, float]],
    ) -> Dict[str, Dict[str, object]]:
        bundles: Dict[str, Dict[str, object]] = {}
        for name, bundle in spec.bundles.items():
            origin_coords = self._coords_from_ref(bundle.origin, {**bundles, **planes, **points})
            origin = dict(origin_coords)
            for axis_token, value in bundle.translate.items():
                axis = axis_token[-1]
                origin[axis] = origin.get(axis, 0.0) + value
            span: Dict[str, float] = {}
            for axis_token, value in bundle.span.items():
                axis = axis_token[-1]
                span[f"+{axis}"] = value
                span[axis] = value
            bundle_record = {"origin": origin, "span": span}
            self._register_ref(bundles, name, bundle_record, category="bundles")
        return bundles

    def _coords_from_ref(
        self,
        ref: str,
        lookup: Mapping[str, Mapping[str, float]],
    ) -> Dict[str, float]:
        if ref in lookup:
            entry = lookup[ref]
            return dict(entry)
        if ref.startswith("datums.planes."):
            key = ref.split(".", 2)[2]
            if key in lookup:
                return dict(lookup[key])
        if ref.startswith("datums."):
            key = ref.split(".", 1)[1]
            if key in lookup:
                return dict(lookup[key])
        return {"x": 0.0, "y": 0.0, "z": 0.0}

    def _register_ref(
        self,
        target: Dict[str, Dict[str, object]],
        name: str,
        value: Dict[str, object],
        *,
        category: str,
    ) -> None:
        target[name] = value
        target[f"datums.{name}"] = value
        target[f"datums.{category}.{name}"] = value

    def _stable_guid(self, component_id: str, instance_id: str) -> str:
        seed = f"{self.spec.schema}|{self.spec.info.option or 'option'}|{component_id}|{instance_id}"
        return str(uuid.uuid5(GUID_NAMESPACE, seed))


__all__ = [
    "ComponentTransform",
    "ConstraintSolver",
    "NeutralPrimitive",
    "SolveDiagnostics",
    "SolveResult",
    "SolvedComponent",
]
