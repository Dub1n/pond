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
    AXIS_ORDER,
    AxisRelation,
    AxisMapTarget,
    BooleanOperation,
    MirrorOperation,
    Operation,
    ArraySpec,
    RelationshipComponent,
    RelationshipDiagramSpec,
    RotateOperation,
    TranslateOperation,
    canonical_pos_token,
)
from .flags import collision_handling_mode, collision_ignore_classes, fail_on_warn


GUID_NAMESPACE = uuid.UUID("6c7b3d9e-4f21-4b06-9fbf-2a6e2d6a8b2c")

AxisName = str
MM_TO_METERS = 0.001
OrientationMatrix = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]
FRAME_ALIGNMENT_THRESHOLD = 0.995
IDENTITY_ORIENTATION: OrientationMatrix = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)


def _axes_from_pos(pos_token: str) -> List[Tuple[str, int]]:
    axes: List[Tuple[str, int]] = []
    token = pos_token.strip()
    if len(token) < 2:
        return axes
    idx = 0
    while idx < len(token):
        if token[idx] == "c":
            axes.append((token[idx + 1], 0))
            idx += 2
            continue
        sign_char = token[idx]
        axis = token[idx + 1]
        sign = 1 if sign_char == "+" else -1
        axes.append((axis, sign))
        idx += 2
    return axes


def _half_size(size: Tuple[float, float, float], axis: str) -> float:
    if axis == "x":
        return size[0] / 2
    if axis == "y":
        return size[1] / 2
    return size[2] / 2


def _axis_vector(orientation: OrientationMatrix, axis: str) -> Tuple[float, float, float]:
    if axis == "x":
        return orientation[0]
    if axis == "y":
        return orientation[1]
    return orientation[2]


def _orientation_from_z_rotation(angle_deg: float) -> OrientationMatrix:
    radians = math.radians(angle_deg)
    cos_a = math.cos(radians)
    sin_a = math.sin(radians)
    return (
        (cos_a, sin_a, 0.0),
        (-sin_a, cos_a, 0.0),
        (0.0, 0.0, 1.0),
    )


def _orientation_from_direction(direction: Tuple[float, float, float], twist_deg: float = 0.0) -> OrientationMatrix:
    x_axis = _normalise_vector(direction)
    if x_axis == (0.0, 0.0, 0.0):
        return IDENTITY_ORIENTATION
    up = (0.0, 0.0, 1.0)
    if abs(sum(a * b for a, b in zip(x_axis, up))) > 0.999:
        up = (0.0, 1.0, 0.0)
    y_axis = _normalise_vector(
        (
            up[1] * x_axis[2] - up[2] * x_axis[1],
            up[2] * x_axis[0] - up[0] * x_axis[2],
            up[0] * x_axis[1] - up[1] * x_axis[0],
        )
    )
    z_axis = _normalise_vector(
        (
            x_axis[1] * y_axis[2] - x_axis[2] * y_axis[1],
            x_axis[2] * y_axis[0] - x_axis[0] * y_axis[2],
            x_axis[0] * y_axis[1] - x_axis[1] * y_axis[0],
        )
    )
    orientation = (x_axis, y_axis, z_axis)
    if twist_deg:
        twist_rad = math.radians(twist_deg)
        axis = np.array(x_axis)
        axis = axis / (np.linalg.norm(axis) or 1.0)
        twist_matrix = trimesh.transformations.rotation_matrix(twist_rad, axis)[:3, :3]
        orientation_matrix = np.array(orientation).T
        oriented = twist_matrix @ orientation_matrix
        orientation = (
            tuple(float(val) for val in oriented[:, 0]),
            tuple(float(val) for val in oriented[:, 1]),
            tuple(float(val) for val in oriented[:, 2]),
    )
    return orientation


def _reflect_point(point: Tuple[float, float, float], axis: str, coordinate: float) -> Tuple[float, float, float]:
    idx = AXIS_ORDER[axis]
    reflected = list(point)
    reflected[idx] = coordinate - (point[idx] - coordinate)
    return (reflected[0], reflected[1], reflected[2])


def _reflect_vector(vector: Tuple[float, float, float], axis: str) -> Tuple[float, float, float]:
    if axis == "x":
        return (-vector[0], vector[1], vector[2])
    if axis == "y":
        return (vector[0], -vector[1], vector[2])
    return (vector[0], vector[1], -vector[2])


def _reflect_orientation(orientation: OrientationMatrix, axis: str) -> OrientationMatrix:
    x_axis = _normalise_vector(_reflect_vector(orientation[0], axis))
    y_axis = _normalise_vector(_reflect_vector(orientation[1], axis))
    z_axis = _normalise_vector(
        (
            x_axis[1] * y_axis[2] - x_axis[2] * y_axis[1],
            x_axis[2] * y_axis[0] - x_axis[0] * y_axis[2],
            x_axis[0] * y_axis[1] - x_axis[1] * y_axis[0],
        )
    )
    if z_axis == (0.0, 0.0, 0.0):
        z_axis = _normalise_vector(orientation[2])
    # Re-orthogonalise to keep a right-handed basis after the reflection.
    y_axis = _normalise_vector(
        (
            z_axis[1] * x_axis[2] - z_axis[2] * x_axis[1],
            z_axis[2] * x_axis[0] - z_axis[0] * x_axis[2],
            z_axis[0] * x_axis[1] - z_axis[1] * x_axis[0],
        )
    )
    return (x_axis, y_axis, z_axis)


def _rotation_from_orientation(orientation: OrientationMatrix) -> Tuple[float, float, float]:
    matrix = np.array(
        [
            [orientation[0][0], orientation[1][0], orientation[2][0], 0.0],
            [orientation[0][1], orientation[1][1], orientation[2][1], 0.0],
            [orientation[0][2], orientation[1][2], orientation[2][2], 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    try:
        rx, ry, rz = trimesh.transformations.euler_from_matrix(matrix, axes="sxyz")
    except Exception:
        return (0.0, 0.0, 0.0)
    return (math.degrees(rx), math.degrees(ry), math.degrees(rz))


def _world_axis_component(axis: str, vector: Tuple[float, float, float]) -> float:
    idx = AXIS_ORDER[axis]
    return vector[idx]


def _normalise_vector(vec: Tuple[float, float, float]) -> Tuple[float, float, float]:
    length = math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
    if length <= 1e-9:
        return (0.0, 0.0, 0.0)
    return (vec[0] / length, vec[1] / length, vec[2] / length)


def _dominant_world_axis(vector: Tuple[float, float, float]) -> Tuple[str, int, float]:
    magnitudes = [abs(val) for val in vector]
    idx = int(np.argmax(magnitudes))
    axis = ("x", "y", "z")[idx]
    sign = 1 if vector[idx] >= 0 else -1
    return axis, sign, magnitudes[idx]


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
    collisions: List[Tuple[str, str, float]] = field(default_factory=list)

    def add_error(self, message: str, *, subject: Optional[str] = None) -> None:
        self.errors.append(Diagnostic(level="error", message=message, subject=subject))

    def add_warning(self, message: str, *, subject: Optional[str] = None) -> None:
        self.warnings.append(Diagnostic(level="warning", message=message, subject=subject))

    def escalate_warnings(self) -> None:
        for warning in self.warnings:
            self.errors.append(Diagnostic(level="error", message=warning.message, subject=warning.subject))

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
    orientation: OrientationMatrix = IDENTITY_ORIENTATION


@dataclass(slots=True)
class ComponentState:
    id: str
    size: Tuple[float, float, float]
    transform: ComponentTransform
    class_name: Optional[str]
    orientation: OrientationMatrix
    template_id: str
    origin: str = "original"


@dataclass(slots=True)
class ConnectionHint:
    target: str
    subject_pos: str
    object_pos: str


@dataclass(slots=True)
class NeutralPrimitive:
    id: str
    template_id: str
    class_name: Optional[str]
    profile: str
    profile_params: Dict[str, object]
    size: Tuple[float, float, float]
    material: Optional[str]
    metadata: Dict[str, object]
    transform: ComponentTransform
    guid: str
    seed_id: Optional[str] = None
    origin: str = "original"
    solid: Optional[Any] = None
    footprint: Optional[ShapelyPolygon] = None
    mesh: Optional[Any] = None
    ifc: Optional[Dict[str, object]] = None
    connections: Tuple[ConnectionHint, ...] = ()
    voids: Tuple[str, ...] = ()


@dataclass(slots=True)
class SolvedComponent:
    component: RelationshipComponent
    instance_id: str
    transform: ComponentTransform
    primitive: NeutralPrimitive
    guid: str
    template_id: str
    origin: str = "original"
    seed_id: Optional[str] = None


@dataclass(slots=True)
class SolveResult:
    components: Tuple[SolvedComponent, ...]
    diagnostics: SolveDiagnostics
    primitives: Tuple[NeutralPrimitive, ...]
    scene: Optional[trimesh.Scene] = None


@dataclass(slots=True)
class OperationState:
    operation: Operation
    processed: set[str] = field(default_factory=set)


@dataclass(slots=True)
class InstancePlan:
    id: str
    template_id: str
    component: RelationshipComponent
    relations: Tuple[AxisRelation, ...]
    array: Optional[ArraySpec]
    origin: str = "original"
    seed_id: Optional[str] = None


@dataclass(slots=True)
class AxisState:
    center: Optional[float] = None
    faces: Dict[int, float] = field(default_factory=dict)
    size: Optional[float] = None
    locked_center: bool = False


class ReferenceResolver:
    def __init__(
        self,
        component_states: Mapping[str, ComponentState],
        datum_points: Mapping[str, Dict[str, float]],
        datum_planes: Mapping[str, Dict[str, float]],
        datum_bundles: Mapping[str, Dict[str, object]],
    ) -> None:
        self.component_states = component_states
        self.datum_points = datum_points
        self.datum_planes = datum_planes
        self.datum_bundles = datum_bundles

    def _frame_orientation(self, frame: str, ref: str) -> OrientationMatrix:
        if frame == "world":
            return IDENTITY_ORIENTATION
        if frame.startswith("component:"):
            component_id = frame.split(":", 1)[1]
            state = self.component_states.get(component_id)
            if state is not None:
                return getattr(state, "orientation", IDENTITY_ORIENTATION)
        if frame == "local":
            state = self.component_states.get(ref)
            if state is not None:
                return getattr(state, "orientation", IDENTITY_ORIENTATION)
        return IDENTITY_ORIENTATION

    def world_axis_for(self, frame: str, ref: str, axis: str) -> Tuple[str, int, float]:
        orientation = self._frame_orientation(frame, ref)
        axis_vec = _axis_vector(orientation, axis)
        return _dominant_world_axis(axis_vec)

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
        frame: str = "world",
        *,
        mapped_axis: Optional[str] = None,
        mapped_sign: Optional[int] = None,
    ) -> Optional[float]:
        world_axis, world_sign, _ = self.world_axis_for(frame, ref, axis)
        if mapped_axis is not None:
            world_axis = mapped_axis
        if mapped_sign is not None:
            world_sign = mapped_sign
        world_idx = AXIS_ORDER[world_axis]
        if ref in self.component_states:
            state = self.component_states[ref]
            base = state.transform.position
            offset = 0.0 if sign == 0 else _half_size(state.size, axis) * float(sign * world_sign)
            return base[world_idx] + offset

        if ref in self.datum_bundles:
            bundle = self.datum_bundles[ref]
            origin = bundle["origin"]
            span = bundle["span"]
            if world_axis not in origin and axis not in origin:
                return None
            base = origin.get(world_axis, origin.get(axis, 0.0))
            if sign >= 0:
                return base + span.get(f"+{world_axis}", span.get(world_axis, span.get(axis, 0.0)))
            return base

        if ref in self.datum_planes:
            coords = self.datum_planes[ref]
            return coords.get(world_axis, coords.get(axis, None))

        if ref in self.datum_points:
            coords = self.datum_points[ref]
            return coords.get(world_axis, coords.get(axis, None))

        return None


class ConstraintSolver:
    """
    Resolves relationship-first specs into deterministic transforms and neutral
    primitives using the axis-map schema shape.
    """

    def __init__(self, spec: RelationshipDiagramSpec) -> None:
        self.spec = spec
        self.components = list(spec.components)
        self.components_by_id: Dict[str, RelationshipComponent] = {component.id: component for component in self.components}
        self.datum_points = self._build_points(spec)
        self.datum_planes = self._build_planes(spec)
        self.datum_bundles = self._build_bundles(spec, self.datum_points, self.datum_planes)
        self.collision_mode = collision_handling_mode()
        self.fail_on_warn = fail_on_warn()
        self.collision_ignore = collision_ignore_classes()
        self._frame_warning_cache: set[str] = set()
        self._frame_summary: Dict[Tuple[str, str, str], set[str]] = {}

    def solve(self) -> SolveResult:
        diagnostics = SolveDiagnostics()
        component_states: Dict[str, ComponentState] = {}
        solved: List[SolvedComponent] = []

        plans = self._expand_components()
        pending = list(plans)
        pending_ops = [OperationState(operation=operation) for operation in self.spec.operations]

        while pending or pending_ops:
            progressed = False
            for plan in list(pending):
                if not self._can_resolve(plan, component_states):
                    continue
                solved_instances = self._solve_plan(plan, component_states, diagnostics)
                solved.extend(solved_instances)
                pending.remove(plan)
                progressed = True
            if pending_ops:
                op_state = pending_ops[0]
                solved, applied, completed = self._apply_operation_state(
                    op_state,
                    solved,
                    component_states,
                    diagnostics,
                    pending,
                )
                if applied or completed:
                    progressed = True
                if completed:
                    pending_ops.pop(0)
            if not progressed:
                for plan in pending:
                    diagnostics.add_error(
                        f"component '{plan.id}' could not resolve references for placement",
                        subject=plan.id,
                    )
                if pending_ops:
                    diagnostics.add_error(
                        f"operation '{pending_ops[0].operation.type}' could not resolve references for targets",
                        subject=pending_ops[0].operation.type,
                    )
                break

        resolver = ReferenceResolver(component_states, self.datum_points, self.datum_planes, self.datum_bundles)
        self._evaluate_checks(resolver, diagnostics)

        primitives = tuple(item.primitive for item in solved)
        self._emit_frame_summaries(diagnostics)
        self._detect_collisions(primitives, diagnostics)
        if self.fail_on_warn:
            diagnostics.escalate_warnings()
        scene = self._build_scene(primitives)
        return SolveResult(components=tuple(solved), diagnostics=diagnostics, primitives=primitives, scene=scene)

    # ------------------------------------------------------------------ #
    def _expand_components(self) -> List[InstancePlan]:
        plans: List[InstancePlan] = []
        for component in self.components:
            base_relations = tuple(component.relations)
            placements = component.place or (None,)
            if placements == (None,):
                relations = base_relations
                plans.append(
                    InstancePlan(
                        id=component.id,
                        template_id=component.id,
                        component=component,
                        relations=relations,
                        array=component.array,
                        origin="original",
                        seed_id=component.id,
                    )
                )
                continue
            for placement in placements:
                if placement is None:
                    continue
                relations = base_relations + tuple(placement.relations)
                plans.append(
                    InstancePlan(
                        id=placement.id,
                        template_id=component.id,
                        component=component,
                        relations=relations,
                        array=component.array,
                        origin="original",
                        seed_id=placement.id,
                    )
                )
        return plans

    def _can_resolve(self, plan: InstancePlan, component_states: Mapping[str, ComponentState]) -> bool:
        resolver = ReferenceResolver(component_states, self.datum_points, self.datum_planes, self.datum_bundles)
        refs: List[str] = []
        for relation in plan.relations:
            refs.append(relation.target.ref)
        array = plan.array
        if array:
            for relation in array.relations:
                refs.append(relation.target.ref)
            for through in array.through:
                for relation in through.relations:
                    refs.append(relation.target.ref)
        for ref in refs:
            if resolver.coords_for_ref(ref) is None and ref not in component_states:
                return False
        return True

    def _solve_plan(
        self,
        plan: InstancePlan,
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
    ) -> List[SolvedComponent]:
        component = plan.component
        base_orientation = IDENTITY_ORIENTATION
        base_rotation_z = float(component.metadata.get("_rotation_z", 0.0)) if component.metadata else 0.0
        if base_rotation_z:
            base_orientation = _orientation_from_z_rotation(base_rotation_z)

        resolver = ReferenceResolver(component_states, self.datum_points, self.datum_planes, self.datum_bundles)
        instances = self._instances_for_plan(
            plan,
            resolver=resolver,
            base_orientation=base_orientation,
            base_rotation=base_rotation_z,
            diagnostics=diagnostics,
        )

        solved_components: List[SolvedComponent] = []
        for idx, instance in enumerate(instances):
            axis_states = {
                "x": AxisState(),
                "y": AxisState(),
                "z": AxisState(),
            }
            size_axis_map: Dict[str, str] = {"x": "x", "y": "y", "z": "z"}
            for axis, value in instance.get("preset_axes", {}).items():
                axis_states[axis].center = value
                axis_states[axis].locked_center = True

            for relation in plan.relations:
                self._apply_axis_relation(
                    component,
                    axis_states,
                    relation,
                    resolver,
                    diagnostics,
                    instance_id=instance["id"],
                    axis_size_map=size_axis_map,
                )

            size = list(component.size)
            overrides = instance.get("size_overrides") or {}
            for axis, value in overrides.items():
                if axis in AXIS_ORDER:
                    size[AXIS_ORDER[axis]] = value
            final_center: Dict[str, float] = {}

            dof_count = 0
            for axis in ("x", "y", "z"):
                size_axis = size_axis_map.get(axis, axis)
                explicit = size[AXIS_ORDER[size_axis]]
                state = axis_states[axis]
                center_value, size_value, axis_dof = self._resolve_axis_state(
                    component,
                    axis,
                    state,
                    explicit,
                    diagnostics,
                    allow_default_zero=component.kind == "reference",
                    instance_id=instance["id"],
                    size_axis=size_axis,
                )
                dof_count += axis_dof
                final_center[axis] = center_value
                size[AXIS_ORDER[axis]] = size_value

            transform = ComponentTransform(
                position=(final_center["x"], final_center["y"], final_center["z"]),
                rotation=_rotation_from_orientation(instance.get("orientation", base_orientation)),
                orientation=instance.get("orientation", base_orientation),
            )

            size_tuple = (float(size[0] or 0.0), float(size[1] or 0.0), float(size[2] or 0.0))
            component_states[instance["id"]] = ComponentState(
                id=instance["id"],
                size=size_tuple,
                transform=transform,
                class_name=component.class_name,
                orientation=transform.orientation,
                template_id=plan.template_id,
                origin=instance.get("origin", plan.origin),
            )
            if plan.template_id not in component_states:
                component_states[plan.template_id] = component_states[instance["id"]]
            diagnostics.degrees_of_freedom[instance["id"]] = 0

            if component.kind == "reference":
                diagnostics.degrees_of_freedom[instance["id"]] = dof_count
                continue
            diagnostics.degrees_of_freedom[instance["id"]] = dof_count

            guid = self._stable_guid(plan.template_id, instance["id"])
            primitive = self._neutral_primitive(
                component,
                instance["id"],
                plan.template_id,
                size_tuple,
                transform,
                guid,
                tuple(),
                origin=instance.get("origin", plan.origin),
                seed_id=plan.seed_id,
            )
            solved_component = SolvedComponent(
                component=component,
                instance_id=instance["id"],
                transform=transform,
                primitive=primitive,
                guid=guid,
                template_id=plan.template_id,
                origin=instance.get("origin", plan.origin),
                seed_id=plan.seed_id,
            )
            solved_components.append(solved_component)
        return solved_components

    def _instances_for_plan(
        self,
        plan: InstancePlan,
        resolver: ReferenceResolver,
        base_orientation: OrientationMatrix,
        base_rotation: float,
        diagnostics: SolveDiagnostics,
    ) -> List[Dict[str, Any]]:
        array = plan.array
        if array is None:
            return [
                {"id": plan.id, "orientation": base_orientation, "preset_axes": {}, "origin": plan.origin},
            ]
        positions = self._array_positions(plan, array, resolver, diagnostics)
        instances: List[Dict[str, Any]] = []
        for idx, pos in enumerate(positions):
            name = plan.id if idx == 0 else f"{plan.id}#{idx}"
            origin_kind = "original" if idx == 0 else "clone"
            orientation = base_orientation
            instances.append(
                {
                    "id": name,
                    "preset_axes": pos["axis_values"],
                    "size_overrides": pos.get("size_overrides", {}),
                    "orientation": orientation,
                    "origin": origin_kind,
                }
            )
        return instances

    def _axis_amount_for(self, axis: str, subject_sign: int, mapping: Dict[str, float]) -> float:
        total = mapping.get("*", 0.0)
        for key, value in mapping.items():
            if key == "*":
                continue
            axes = _axes_from_pos(key)
            if any(a == axis and (s == 0 or s == subject_sign) for a, s in axes):
                total += value
        return total

    def _apply_axis_relation(
        self,
        component: RelationshipComponent,
        axis_states: Dict[str, AxisState],
        relation: AxisRelation,
        resolver: ReferenceResolver,
        diagnostics: SolveDiagnostics,
        *,
        instance_id: str,
        axis_size_map: Optional[Dict[str, str]] = None,
    ) -> set[str]:
        touched_axes: set[str] = set()
        subject_axes = _axes_from_pos(relation.subject)
        mode = (relation.target.mode or "point").lower()
        max_axes = {"plane": 1, "edge": 2}.get(mode, None)
        if max_axes is not None and len(subject_axes) > max_axes:
            diagnostics.add_warning(
                f"component '{component.id}' relation '{relation.subject}' uses mode '{mode}' and extra axes will be ignored",
                subject=instance_id,
            )
            subject_axes = subject_axes[:max_axes]
        target_axes = {}
        for axis, sign in _axes_from_pos(relation.target.pos):
            target_axes.setdefault(axis, set()).add(sign)

        for axis, subject_sign in subject_axes:
            world_axis, world_sign, alignment = resolver.world_axis_for(relation.target.frame, relation.target.ref, axis)
            if axis_size_map is not None:
                current_axis = axis_size_map.get(world_axis)
                if current_axis is None or current_axis == world_axis:
                    axis_size_map[world_axis] = axis
            if alignment < FRAME_ALIGNMENT_THRESHOLD:
                message = (
                    f"component '{component.id}' relation '{relation.subject}' using frame '{relation.target.frame}' on '{relation.target.ref}' "
                    f"maps local {axis} to world {world_axis} (alignment {alignment:.3f}); gaps/offsets use projected axis"
                )
                if message not in self._frame_warning_cache:
                    self._frame_warning_cache.add(message)
                    diagnostics.add_warning(message, subject=instance_id)
                summary_key = (component.id, relation.target.frame, relation.target.ref)
                self._frame_summary.setdefault(summary_key, set()).add(f"{axis}->{world_axis} ({alignment:.3f})")
            target_sign = subject_sign
            if axis in target_axes:
                if subject_sign in target_axes[axis]:
                    target_sign = subject_sign
                elif 0 in target_axes[axis]:
                    target_sign = 0
                else:
                    # Fall back to the first explicit sign provided on the target
                    target_sign = sorted(target_axes[axis])[0]
            coord = resolver.axis_coordinate(
                relation.target.ref,
                axis,
                target_sign,
                frame=relation.target.frame,
                mapped_axis=world_axis,
                mapped_sign=world_sign,
            )
            if coord is None:
                diagnostics.add_error(
                    f"component '{component.id}' relation references unknown target '{relation.target.ref}'",
                    subject=component.id,
                )
                continue
            offset_amount = self._axis_amount_for(axis, subject_sign, relation.target.offset)
            gap_amount = self._axis_amount_for(axis, subject_sign, relation.target.gap)
            gap_direction = subject_sign * world_sign if subject_sign != 0 else 0
            adjusted = coord + offset_amount * world_sign + gap_amount * gap_direction
            state = axis_states[world_axis]
            if subject_sign == 0:
                if state.center is not None and abs(state.center - adjusted) > 1e-6 and not state.locked_center:
                    diagnostics.add_error(
                        f"component '{component.id}' has conflicting center on {axis}",
                        subject=instance_id,
                    )
                if not state.locked_center:
                    state.center = adjusted
            else:
                state.faces[subject_sign] = adjusted
            touched_axes.add(world_axis)
        self._enforce_relation_mode(component, relation, axis_states, diagnostics, instance_id=instance_id)
        return touched_axes

    def _enforce_relation_mode(
        self,
        component: RelationshipComponent,
        relation: AxisRelation,
        axis_states: Dict[str, AxisState],
        diagnostics: SolveDiagnostics,
        *,
        instance_id: str,
    ) -> None:
        mode = (relation.target.mode or "point").lower()
        if mode not in {"point", "plane", "edge"}:
            diagnostics.add_error(
                f"component '{component.id}' relation uses unsupported mode '{relation.target.mode}'",
                subject=instance_id,
            )
            return
        axes = _axes_from_pos(relation.subject)
        if mode == "plane":
            # keep only the axis matching the plane; others stay free
            if len(axes) != 1:
                diagnostics.add_warning(
                    f"component '{component.id}' relation '{relation.subject}' should use a single axis for plane mode",
                    subject=instance_id,
                )
            return
        if mode == "edge":
            if len(axes) != 2:
                diagnostics.add_warning(
                    f"component '{component.id}' relation '{relation.subject}' should use two axes for edge mode",
                    subject=instance_id,
                )
            return

    def _resolve_axis_state(
        self,
        component: RelationshipComponent,
        axis: str,
        state: AxisState,
        explicit_size: Optional[float],
        diagnostics: SolveDiagnostics,
        *,
        allow_default_zero: bool,
        instance_id: str,
        size_axis: Optional[str] = None,
    ) -> Tuple[float, float, int]:
        size_axis = size_axis or axis
        center = state.center
        size_value = explicit_size
        pos_plus = state.faces.get(1)
        pos_minus = state.faces.get(-1)

        axis_dof = 0
        inferred_size = None
        if pos_plus is not None and pos_minus is not None:
            inferred_size = pos_plus - pos_minus
            if inferred_size < 0:
                inferred_size = abs(inferred_size)
        elif center is not None:
            if pos_plus is not None:
                inferred_size = abs((pos_plus - center) * 2)
            elif pos_minus is not None:
                inferred_size = abs((center - pos_minus) * 2)

        if size_value is not None and inferred_size is not None and abs(size_value - inferred_size) > 1e-6:
            diagnostics.add_error(
                f"component '{component.id}' size on {size_axis} conflicts with inferred span ({size_value:.3f} vs {inferred_size:.3f})",
                subject=instance_id,
            )
        if size_value is None and inferred_size is not None:
            size_value = inferred_size
        if size_value is None:
            size_value = 0.0
            if component.kind != "reference":
                axis_dof += 1

        if center is None:
            if pos_plus is not None and pos_minus is not None:
                center = (pos_plus + pos_minus) / 2
            elif pos_plus is not None:
                center = pos_plus - size_value / 2
            elif pos_minus is not None:
                center = pos_minus + size_value / 2
            elif allow_default_zero:
                center = 0.0
            else:
                diagnostics.add_warning(
                    f"component '{component.id}' remains under-constrained on axis {axis}",
                    subject=instance_id,
                )
                center = 0.0
                axis_dof += 1

        if size_value <= 0 and component.kind != "reference":
            diagnostics.add_warning(
                f"component '{component.id}' has non-positive size on axis {size_axis}",
                subject=instance_id,
            )

        return center, size_value, axis_dof

    def _array_positions(
        self,
        plan: InstancePlan,
        array: ArraySpec,
        resolver: ReferenceResolver,
        diagnostics: SolveDiagnostics,
    ) -> List[Dict[str, Any]]:
        component = plan.component
        axis_states = {axis: AxisState() for axis in ("x", "y", "z")}
        size_axis_map: Dict[str, str] = {"x": "x", "y": "y", "z": "z"}

        for relation in array.relations:
            self._apply_axis_relation(
                component,
                axis_states,
                relation,
                resolver,
                diagnostics,
                instance_id=plan.id,
                axis_size_map=size_axis_map,
            )

        repeat_axes = set(array.repeat.keys())
        explicit_sizes: Dict[str, Optional[float]] = {}
        for axis in ("x", "y", "z"):
            size_axis = size_axis_map.get(axis, axis)
            explicit_sizes[axis] = component.size[AXIS_ORDER[size_axis]]

        axis_info: Dict[str, Dict[str, Optional[float]]] = {}
        for axis in ("x", "y", "z"):
            state = axis_states[axis]
            face_plus = state.faces.get(1)
            face_minus = state.faces.get(-1)
            center = state.center
            span = None
            if face_plus is not None and face_minus is not None:
                span = abs(face_plus - face_minus)
            elif axis not in repeat_axes:
                if explicit_sizes[axis] is not None:
                    span = explicit_sizes[axis]
                elif center is not None:
                    if face_plus is not None:
                        span = abs((face_plus - center) * 2)
                    elif face_minus is not None:
                        span = abs((center - face_minus) * 2)
            axis_info[axis] = {
                "face_plus": face_plus,
                "face_minus": face_minus,
                "center": center,
                "span": span,
            }

        def _axis_anchor(axis: str) -> Tuple[Optional[float], int]:
            info = axis_info[axis]
            face_minus = info["face_minus"]
            face_plus = info["face_plus"]
            if face_minus is not None:
                return face_minus, 1
            if face_plus is not None:
                return face_plus, -1
            return info["center"], 1

        through_points: List[Dict[str, float]] = []
        for through in array.through:
            constraints: Dict[str, float] = {}
            for relation in through.relations:
                subject_axes = _axes_from_pos(relation.subject)
                target_axes = {axis: sign for axis, sign in _axes_from_pos(relation.target.pos)}
                for axis, subject_sign in subject_axes:
                    world_axis, world_sign, _ = resolver.world_axis_for(relation.target.frame, relation.target.ref, axis)
                    target_sign = target_axes.get(axis, subject_sign)
                    coord = resolver.axis_coordinate(
                        relation.target.ref,
                        axis,
                        target_sign,
                        frame=relation.target.frame,
                        mapped_axis=world_axis,
                        mapped_sign=world_sign,
                    )
                    if coord is None:
                        diagnostics.add_error(
                            f"component '{component.id}' array.through references unknown target '{relation.target.ref}'",
                            subject=plan.id,
                        )
                        continue
                    offset_amount = self._axis_amount_for(axis, subject_sign, relation.target.offset)
                    gap_amount = self._axis_amount_for(axis, subject_sign, relation.target.gap)
                    gap_direction = subject_sign * world_sign if subject_sign != 0 else 0
                    adjusted = coord + offset_amount * world_sign + gap_amount * gap_direction
                    existing = constraints.get(world_axis)
                    if existing is not None and abs(existing - adjusted) > 1e-6:
                        diagnostics.add_error(
                            f"component '{component.id}' array.through has conflicting constraints on {world_axis}",
                            subject=plan.id,
                        )
                    constraints[world_axis] = adjusted
            if constraints:
                through_points.append(constraints)

        direction_components: Dict[str, float] = {}
        for axis in ("x", "y", "z"):
            anchor, sign = _axis_anchor(axis)
            span = axis_info[axis]["span"]
            repeat_spec = array.repeat.get(axis)
            component_length = 0.0
            if axis in repeat_axes:
                count = repeat_spec.count if repeat_spec else None
                pitch = repeat_spec.pitch if repeat_spec else None
                if span is not None:
                    component_length = span * sign
                elif count is not None and pitch is not None and count > 1:
                    component_length = pitch * (count - 1) * sign
            direction_components[axis] = component_length

            if abs(direction_components[axis]) < 1e-6 and through_points and anchor is not None:
                through_axis = through_points[0].get(axis)
                if through_axis is not None:
                    direction_components[axis] = through_axis - anchor

        origin: Dict[str, float] = {}
        axis_centers: Dict[str, List[float]] = {}
        size_overrides: Dict[str, float] = {}

        for axis in ("x", "y", "z"):
            info = axis_info[axis]
            anchor, sign = _axis_anchor(axis)
            repeat_spec = array.repeat.get(axis)
            size_value = explicit_sizes[axis]

            if size_value is None and axis in repeat_axes:
                count = repeat_spec.count if repeat_spec else None
                if count is None or count > 1:
                    diagnostics.add_error(
                        f"component '{component.id}' array repeat requires explicit size on {axis}",
                        subject=plan.id,
                    )
                    size_value = 0.0

            if axis in repeat_axes:
                count = repeat_spec.count if repeat_spec else None
                pitch = repeat_spec.pitch if repeat_spec else None
                span = info["span"]
                if size_value is None and span is not None and count == 1:
                    size_value = span

                if size_value is None:
                    size_value = 0.0

                if pitch is not None and pitch < size_value:
                    diagnostics.add_error(
                        f"component '{component.id}' array repeat.{axis} pitch {pitch:.3f} overlaps size {size_value:.3f}",
                        subject=plan.id,
                    )
                if count is None and pitch is not None:
                    if span is None:
                        diagnostics.add_error(
                            f"component '{component.id}' array repeat.{axis} requires count when span is undefined",
                            subject=plan.id,
                        )
                        count = 1
                    else:
                        available = span - size_value
                        if available < 0:
                            diagnostics.add_error(
                                f"component '{component.id}' array span on {axis} is smaller than size",
                                subject=plan.id,
                            )
                            available = 0.0
                        count = int(available // pitch) + 1
                        occupied = size_value + (count - 1) * pitch
                        if abs(occupied - span) > 1e-6:
                            diagnostics.add_warning(
                                f"component '{component.id}' array repeat.{axis} does not align to span",
                                subject=plan.id,
                            )
                if count is not None and pitch is None:
                    if count <= 1:
                        pitch = 0.0
                    else:
                        if span is None:
                            diagnostics.add_error(
                                f"component '{component.id}' array repeat.{axis} requires span for count without pitch",
                                subject=plan.id,
                            )
                            pitch = 0.0
                        else:
                            available = span - size_value
                            if available < 0:
                                diagnostics.add_error(
                                    f"component '{component.id}' array span on {axis} is smaller than size",
                                    subject=plan.id,
                                )
                                available = 0.0
                            pitch = available / max(count - 1, 1)
                if count is None:
                    count = 1
                if pitch is None:
                    pitch = 0.0

                if span is not None and count > 1:
                    occupied = size_value + (count - 1) * pitch
                    if pitch and abs(occupied - span) > 1e-6:
                        diagnostics.add_warning(
                            f"component '{component.id}' array repeat.{axis} does not align to span",
                            subject=plan.id,
                        )
                    if occupied - span > 1e-6:
                        diagnostics.add_error(
                            f"component '{component.id}' array repeat.{axis} exceeds span (occupied {occupied:.3f} vs span {span:.3f})",
                            subject=plan.id,
                        )

                if anchor is None and info["center"] is None:
                    diagnostics.add_error(
                        f"component '{component.id}' array repeat.{axis} is missing an anchor",
                        subject=plan.id,
                    )
                    anchor_center = 0.0
                elif anchor is not None:
                    anchor_center = anchor + sign * (size_value / 2)
                else:
                    anchor_center = info["center"] or 0.0

                axis_centers[axis] = [anchor_center + sign * (pitch * i) for i in range(count)]
                origin[axis] = axis_centers[axis][0] if axis_centers[axis] else anchor_center
                size_overrides[axis] = size_value
                continue

            size_axis = size_axis_map.get(axis, axis)
            center_value, size_value, _ = self._resolve_axis_state(
                component,
                axis,
                axis_states[axis],
                explicit_sizes[axis],
                diagnostics,
                allow_default_zero=component.kind == "reference",
                instance_id=plan.id,
                size_axis=size_axis,
            )
            axis_centers[axis] = [center_value]
            origin[axis] = center_value
            if explicit_sizes[axis] is None and size_value is not None:
                size_overrides[axis] = size_value

        if array.through:
            direction = (direction_components["x"], direction_components["y"], direction_components["z"])
            if abs(direction[0]) + abs(direction[1]) + abs(direction[2]) < 1e-9:
                diagnostics.add_error(
                    f"component '{component.id}' array.through requires a non-zero direction vector",
                    subject=plan.id,
                )
            else:
                for constraints in through_points:
                    t_value: Optional[float] = None
                    valid = True
                    for axis, coord in constraints.items():
                        dir_axis = direction_components.get(axis, 0.0)
                        origin_axis = origin.get(axis, 0.0)
                        if abs(dir_axis) < 1e-9:
                            if abs(origin_axis - coord) > 1e-6:
                                valid = False
                                break
                            continue
                        t_candidate = (coord - origin_axis) / dir_axis
                        if t_value is None:
                            t_value = t_candidate
                        elif abs(t_candidate - t_value) > 1e-6:
                            valid = False
                            break
                    if not valid:
                        diagnostics.add_error(
                            f"component '{component.id}' array.through does not intersect array direction",
                            subject=plan.id,
                        )

        xs = axis_centers["x"]
        ys = axis_centers["y"]
        zs = axis_centers["z"]
        instances: List[Dict[str, Any]] = []
        for x in xs:
            for y in ys:
                for z in zs:
                    instances.append(
                        {
                            "axis_values": {"x": x, "y": y, "z": z},
                            "size_overrides": size_overrides,
                        }
                    )
        return instances

    # ------------------------------------------------------------------ #
    def _selector_index(self, solved: Sequence[SolvedComponent]) -> Dict[str, Dict[str, set[str]]]:
        index: Dict[str, Dict[str, set[str]]] = {}
        for item in solved:
            entry = index.setdefault(item.template_id, {"all": set(), "original": set(), "clones": set()})
            entry["all"].add(item.instance_id)
            if item.origin == "original":
                entry["original"].add(item.instance_id)
            else:
                entry["clones"].add(item.instance_id)
            # Placement id indexing
            if item.seed_id:
                seed_entry = index.setdefault(item.seed_id, {"all": set(), "original": set(), "clones": set()})
                seed_entry["all"].add(item.instance_id)
                if item.origin == "original":
                    seed_entry["original"].add(item.instance_id)
                else:
                    seed_entry["clones"].add(item.instance_id)
        return index

    def _resolve_selector(self, selector: str, index: Dict[str, Dict[str, set[str]]]) -> List[str]:
        if selector.endswith(".original"):
            base = selector[: -len(".original")]
            return sorted(index.get(base, {}).get("original", []) or index.get(base, {}).get("all", []))
        if selector.endswith(".clones"):
            base = selector[: -len(".clones")]
            clones = index.get(base, {}).get("clones", set())
            if clones:
                return sorted(clones)
            return sorted(index.get(base, {}).get("all", []))
        if selector in index:
            return sorted(index[selector].get("all", []))
        # direct instance id
        for entry in index.values():
            if selector in entry.get("all", set()):
                return [selector]
        return []

    def _mapped_rotate_id(
        self,
        base: SolvedComponent,
        op: RotateOperation,
        turn: int,
        diagnostics: SolveDiagnostics,
    ) -> str:
        suffix = ""
        if "#" in base.instance_id:
            suffix = "#" + base.instance_id.split("#", 1)[1]
        mapping_keys = [base.instance_id]
        if base.seed_id:
            mapping_keys.append(base.seed_id)
        mapping_keys.append(base.template_id)
        for key in mapping_keys:
            mapped = op.id_map.get(key)
            if mapped is None:
                continue
            if turn >= len(mapped):
                diagnostics.add_error(
                    f"rotate.id_map for '{key}' is missing an entry for turn {turn}",
                    subject=base.instance_id,
                )
                break
            return f"{mapped[turn]}{suffix}"
        return f"{base.instance_id}_rot{turn}"

    def _apply_operations(
        self,
        solved: List[SolvedComponent],
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
    ) -> List[SolvedComponent]:
        if not self.spec.operations:
            return solved
        result = list(solved)
        for operation in self.spec.operations:
            result = self._apply_operation(operation, result, component_states, diagnostics)
        return result

    def _apply_operation(
        self,
        operation: Operation,
        solved: List[SolvedComponent],
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
    ) -> List[SolvedComponent]:
        result = list(solved)
        index = self._selector_index(result)
        if isinstance(operation, RotateOperation):
            result.extend(self._rotate(operation, result, component_states, diagnostics, index))
        elif isinstance(operation, MirrorOperation):
            result.extend(self._mirror(operation, result, component_states, diagnostics, index))
        elif isinstance(operation, TranslateOperation):
            result.extend(self._translate(operation, result, component_states, diagnostics, index))
        elif isinstance(operation, BooleanOperation):
            self._apply_boolean(operation, result, diagnostics, index)
        return result

    def _apply_operation_state(
        self,
        op_state: OperationState,
        solved: List[SolvedComponent],
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
        pending: Sequence[InstancePlan],
    ) -> Tuple[List[SolvedComponent], bool, bool]:
        operation = op_state.operation
        if isinstance(operation, BooleanOperation):
            return self._apply_boolean_state(operation, solved, diagnostics, pending)
        if isinstance(operation, (RotateOperation, MirrorOperation, TranslateOperation)):
            return self._apply_clone_operation_state(
                operation,
                op_state,
                solved,
                component_states,
                diagnostics,
                pending,
            )
        return solved, False, True

    def _apply_clone_operation_state(
        self,
        operation: RotateOperation | MirrorOperation | TranslateOperation,
        op_state: OperationState,
        solved: List[SolvedComponent],
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
        pending: Sequence[InstancePlan],
    ) -> Tuple[List[SolvedComponent], bool, bool]:
        if isinstance(operation, RotateOperation) and self._reference_coordinates(operation.about, component_states) is None:
            return solved, False, False
        if not operation.targets:
            if pending:
                return solved, False, False
            return self._apply_full_clone_operation(operation, solved, component_states, diagnostics)
        index = self._selector_index(solved)
        selected_ids: List[str] = []
        for selector in operation.targets:
            selected_ids.extend(self._resolve_selector(selector, index))
        if not selected_ids:
            if self._selectors_pending(operation.targets, pending):
                return solved, False, False
            diagnostics.add_error(f"{operation.type} operation matched no components for targets {operation.targets}")
            return solved, False, True
        unprocessed = [instance_id for instance_id in selected_ids if instance_id not in op_state.processed]
        if not unprocessed:
            if self._selectors_pending(operation.targets, pending):
                return solved, False, False
            return solved, False, True
        if isinstance(operation, RotateOperation):
            created = self._rotate(operation, solved, component_states, diagnostics, index, selected_ids=unprocessed)
        elif isinstance(operation, MirrorOperation):
            created = self._mirror(operation, solved, component_states, diagnostics, index, selected_ids=unprocessed)
        else:
            created = self._translate(operation, solved, component_states, diagnostics, index, selected_ids=unprocessed)
        op_state.processed.update(unprocessed)
        op_state.processed.update(item.instance_id for item in created)
        return solved + created, bool(unprocessed), False

    def _apply_full_clone_operation(
        self,
        operation: RotateOperation | MirrorOperation | TranslateOperation,
        solved: List[SolvedComponent],
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
    ) -> Tuple[List[SolvedComponent], bool, bool]:
        result = self._apply_operation(operation, solved, component_states, diagnostics)
        return result, result != solved, True

    def _apply_boolean_state(
        self,
        operation: BooleanOperation,
        solved: List[SolvedComponent],
        diagnostics: SolveDiagnostics,
        pending: Sequence[InstancePlan],
    ) -> Tuple[List[SolvedComponent], bool, bool]:
        index = self._selector_index(solved)
        target_ids = self._resolve_selector(operation.target, index)
        if not target_ids:
            if self._selectors_pending((operation.target,), pending):
                return solved, False, False
            diagnostics.add_error(f"boolean target '{operation.target}' matched no components")
            return solved, False, True
        subtract_ids: List[str] = []
        for selector in operation.subtract:
            subtract_ids.extend(self._resolve_selector(selector, index))
        if not subtract_ids:
            if self._selectors_pending(operation.subtract, pending):
                return solved, False, False
            diagnostics.add_error(
                f"boolean subtract list {operation.subtract} matched no components for target '{operation.target}'"
            )
            return solved, False, True
        self._apply_boolean(operation, solved, diagnostics, index)
        return solved, True, True

    def _selectors_pending(self, selectors: Sequence[str], pending: Sequence[InstancePlan]) -> bool:
        pending_ids = self._pending_selector_ids(pending)
        for selector in selectors:
            if self._selector_waits_on_pending(selector, pending_ids):
                return True
        return False

    def _pending_selector_ids(self, pending: Sequence[InstancePlan]) -> set[str]:
        pending_ids: set[str] = set()
        for plan in pending:
            pending_ids.add(plan.id)
            pending_ids.add(plan.template_id)
        return pending_ids

    def _selector_waits_on_pending(self, selector: str, pending_ids: set[str]) -> bool:
        base = selector
        if selector.endswith(".original") or selector.endswith(".clones"):
            base = selector.rsplit(".", 1)[0]
        base = base.split("#", 1)[0]
        return base in pending_ids

    def _rotate(
        self,
        op: RotateOperation,
        solved: List[SolvedComponent],
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
        index: Dict[str, Dict[str, set[str]]],
        *,
        selected_ids: Optional[Sequence[str]] = None,
    ) -> List[SolvedComponent]:
        created: List[SolvedComponent] = []
        if selected_ids is None:
            targets = op.targets or list(index.keys())
            selected_ids_list: List[str] = []
            for selector in targets:
                selected_ids_list.extend(self._resolve_selector(selector, index))
            selected_ids = selected_ids_list
        if not selected_ids:
            diagnostics.add_error(f"rotate operation matched no components for targets {op.targets}")
            return created
        about_coords = self._reference_coordinates(op.about, component_states)
        if about_coords is None:
            diagnostics.add_error(f"rotate about target '{op.about}' not found")
            return created

        axis = op.axis[-1]
        angle_step = 360.0 / max(op.count, 1)

        for instance_id in selected_ids:
            base = next((s for s in solved if s.instance_id == instance_id), None)
            if base is None:
                continue
            for turn in range(op.count):
                if turn == 0 and not op.include_seed:
                    continue
                if turn == 0:
                    # already exists
                    continue
                angle = angle_step * turn
                new_id = self._mapped_rotate_id(base, op, turn, diagnostics)
                if new_id in component_states:
                    diagnostics.add_error(
                        f"rotate operation would create duplicate id '{new_id}'",
                        subject=instance_id,
                    )
                    continue
                rotated_transform = self._rotate_transform(base.transform, about_coords, axis, angle)
                guid = self._stable_guid(base.template_id, new_id, angle)
                primitive = self._neutral_primitive(
                    base.component,
                    new_id,
                    base.template_id,
                    base.primitive.size,
                    rotated_transform,
                    guid,
                    base.primitive.connections,
                    voids=base.primitive.voids,
                    ifc_data=base.primitive.ifc,
                    origin="clone",
                    seed_id=base.seed_id,
                )
                solved_component = SolvedComponent(
                    component=base.component,
                    instance_id=new_id,
                    transform=rotated_transform,
                    primitive=primitive,
                    guid=guid,
                    template_id=base.template_id,
                    origin="clone",
                    seed_id=base.seed_id,
                )
                created.append(solved_component)
                component_states[new_id] = ComponentState(
                    id=new_id,
                    size=primitive.size,
                    transform=rotated_transform,
                    class_name=base.component.class_name,
                    orientation=rotated_transform.orientation,
                    template_id=base.template_id,
                    origin="clone",
                )
                diagnostics.degrees_of_freedom[new_id] = diagnostics.degrees_of_freedom.get(base.instance_id, 0)
        return created

    def _mirror(
        self,
        op: MirrorOperation,
        solved: List[SolvedComponent],
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
        index: Dict[str, Dict[str, set[str]]],
        *,
        selected_ids: Optional[Sequence[str]] = None,
    ) -> List[SolvedComponent]:
        created: List[SolvedComponent] = []
        if selected_ids is None:
            selected_ids_list: List[str] = []
            targets = op.targets or list(index.keys())
            for selector in targets:
                selected_ids_list.extend(self._resolve_selector(selector, index))
            selected_ids = selected_ids_list
        if not selected_ids:
            diagnostics.add_error(f"mirror operation matched no components for targets {op.targets}")
            return created
        axis = op.axis
        coordinate = op.coordinate
        for instance_id in selected_ids:
            base = next((s for s in solved if s.instance_id == instance_id), None)
            if base is None:
                continue
            if not op.include_seed and base.origin == "original":
                continue
            mirrored_pos = _reflect_point(base.transform.position, axis, coordinate)
            orientation = _reflect_orientation(base.transform.orientation, axis)
            rotation = _rotation_from_orientation(orientation)
            transform = ComponentTransform(position=mirrored_pos, rotation=rotation, orientation=orientation)
            new_id = f"{instance_id}_mirrored"
            guid = self._stable_guid(base.template_id, new_id, coordinate)
            primitive = self._neutral_primitive(
                base.component,
                new_id,
                base.template_id,
                base.primitive.size,
                transform,
                guid,
                base.primitive.connections,
                voids=base.primitive.voids,
                ifc_data=base.primitive.ifc,
                origin="clone",
                seed_id=base.seed_id,
            )
            solved_component = SolvedComponent(
                component=base.component,
                instance_id=new_id,
                transform=transform,
                primitive=primitive,
                guid=guid,
                template_id=base.template_id,
                origin="clone",
                seed_id=base.seed_id,
            )
            created.append(solved_component)
            component_states[new_id] = ComponentState(
                id=new_id,
                size=primitive.size,
                transform=transform,
                class_name=base.component.class_name,
                orientation=transform.orientation,
                template_id=base.template_id,
                origin="clone",
            )
            diagnostics.degrees_of_freedom[new_id] = diagnostics.degrees_of_freedom.get(base.instance_id, 0)
        return created

    def _translate(
        self,
        op: TranslateOperation,
        solved: List[SolvedComponent],
        component_states: Dict[str, ComponentState],
        diagnostics: SolveDiagnostics,
        index: Dict[str, Dict[str, set[str]]],
        *,
        selected_ids: Optional[Sequence[str]] = None,
    ) -> List[SolvedComponent]:
        created: List[SolvedComponent] = []
        if selected_ids is None:
            selected_ids_list: List[str] = []
            targets = op.targets or list(index.keys())
            for selector in targets:
                selected_ids_list.extend(self._resolve_selector(selector, index))
            selected_ids = selected_ids_list
        if not selected_ids:
            diagnostics.add_error(f"translate operation matched no components for targets {op.targets}")
            return created
        for instance_id in selected_ids:
            base = next((s for s in solved if s.instance_id == instance_id), None)
            if base is None:
                continue
            pos = (
                base.transform.position[0] + op.vector[0],
                base.transform.position[1] + op.vector[1],
                base.transform.position[2] + op.vector[2],
            )
            transform = ComponentTransform(position=pos, rotation=base.transform.rotation, orientation=base.transform.orientation)
            new_id = f"{instance_id}_translated"
            guid = self._stable_guid(base.template_id, new_id, sum(op.vector))
            primitive = self._neutral_primitive(
                base.component,
                new_id,
                base.template_id,
                base.primitive.size,
                transform,
                guid,
                base.primitive.connections,
                voids=base.primitive.voids,
                ifc_data=base.primitive.ifc,
                origin="clone",
                seed_id=base.seed_id,
            )
            solved_component = SolvedComponent(
                component=base.component,
                instance_id=new_id,
                transform=transform,
                primitive=primitive,
                guid=guid,
                template_id=base.template_id,
                origin="clone",
                seed_id=base.seed_id,
            )
            created.append(solved_component)
            component_states[new_id] = ComponentState(
                id=new_id,
                size=primitive.size,
                transform=transform,
                class_name=base.component.class_name,
                orientation=transform.orientation,
                template_id=base.template_id,
                origin="clone",
            )
            diagnostics.degrees_of_freedom[new_id] = diagnostics.degrees_of_freedom.get(base.instance_id, 0)
        return created

    def _apply_boolean(
        self,
        op: BooleanOperation,
        solved: List[SolvedComponent],
        diagnostics: SolveDiagnostics,
        index: Dict[str, Dict[str, set[str]]],
    ) -> None:
        target_ids = self._resolve_selector(op.target, index)
        subtract_ids: List[str] = []
        for selector in op.subtract:
            subtract_ids.extend(self._resolve_selector(selector, index))
        if not target_ids:
            diagnostics.add_error(f"boolean target '{op.target}' matched no components")
            return
        if not subtract_ids:
            diagnostics.add_error(f"boolean subtract list {op.subtract} matched no components for target '{op.target}'")
            return
        for target_id in target_ids:
            target = next((s for s in solved if s.instance_id == target_id), None)
            if target is None:
                diagnostics.add_error(f"boolean target '{target_id}' not found")
                continue
            existing = set(target.primitive.voids)
            target.primitive.voids = tuple(sorted(existing | set(subtract_ids)))

    # ------------------------------------------------------------------ #
    def _reference_coordinates(
        self,
        ref: str,
        component_states: Mapping[str, ComponentState],
    ) -> Optional[Tuple[float, float, float]]:
        if ref in component_states:
            pos = component_states[ref].transform.position
            return (pos[0], pos[1], pos[2])
        if ref in self.datum_points:
            coords = self.datum_points[ref]
            return (coords.get("x", 0.0), coords.get("y", 0.0), coords.get("z", 0.0))
        if ref in self.datum_planes:
            coords = self.datum_planes[ref]
            return (coords.get("x", 0.0), coords.get("y", 0.0), coords.get("z", 0.0))
        if ref in self.datum_bundles:
            origin = self.datum_bundles[ref].get("origin", {})
            if isinstance(origin, dict):
                return (origin.get("x", 0.0), origin.get("y", 0.0), origin.get("z", 0.0))
        return None

    def _rotate_transform(
        self,
        transform: ComponentTransform,
        about: Tuple[float, float, float],
        axis: str,
        angle: float,
    ) -> ComponentTransform:
        if axis != "z":
            return transform
        radians = math.radians(angle)
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)
        x, y, z = transform.position
        cx, cy, cz = about
        dx = x - cx
        dy = y - cy
        rotated_x = cx + dx * cos_a - dy * sin_a
        rotated_y = cy + dx * sin_a + dy * cos_a
        rotation = (
            transform.rotation[0],
            transform.rotation[1],
            transform.rotation[2] + angle,
        )
        orientation = _orientation_from_z_rotation(rotation[2])
        return ComponentTransform(position=(rotated_x, rotated_y, z), rotation=rotation, orientation=orientation)

    # ------------------------------------------------------------------ #
    def _stable_guid(self, template_id: str, instance_id: str, salt: float | int | None = None) -> str:
        text = f"{template_id}:{instance_id}"
        if salt is not None:
            text = f"{text}:{salt}"
        return str(uuid.uuid5(GUID_NAMESPACE, text))

    def _neutral_primitive(
        self,
        component: RelationshipComponent,
        instance_id: str,
        template_id: str,
        size: Tuple[float, float, float],
        transform: ComponentTransform,
        guid: str,
        connections: Sequence[ConnectionHint],
        *,
        voids: Sequence[str] | None = None,
        ifc_data: Optional[Dict[str, object]] = None,
        origin: str = "original",
        seed_id: Optional[str] = None,
    ) -> NeutralPrimitive:
        metadata = dict(component.metadata)
        metadata.setdefault("id", instance_id)
        metadata.setdefault("component_id", component.id)
        metadata.setdefault("template_id", template_id)
        metadata.setdefault("class", component.class_name)
        metadata.setdefault("profile", component.profile)
        metadata.setdefault("guid", guid)
        if component.material:
            metadata.setdefault("material", component.material)
        if ifc_data:
            ifc_dict = dict(ifc_data)
        else:
            ifc_dict = component.ifc.to_dict() if component.ifc else None
        if component.profile_params:
            metadata.setdefault("profile_params", dict(component.profile_params))
        if component.ifc:
            if ifc_dict:
                metadata.setdefault("ifc", ifc_dict)
        if component.description:
            metadata.setdefault("description", component.description)
        solid, footprint = self._build_cadquery_block(component, size, transform)
        return NeutralPrimitive(
            id=instance_id,
            template_id=template_id,
            class_name=component.class_name,
            profile=component.profile,
            profile_params=dict(component.profile_params),
            size=size,
            material=component.material,
            metadata=metadata,
            transform=transform,
            guid=guid,
            seed_id=seed_id,
            origin=origin,
            solid=solid,
            footprint=footprint,
            connections=tuple(connections),
            ifc=ifc_dict,
            voids=tuple(voids or component.voids),
        )

    def _build_cadquery_block(
        self,
        component: RelationshipComponent,
        size: Tuple[float, float, float],
        transform: ComponentTransform,
    ) -> Tuple[Optional[Any], Optional[ShapelyPolygon]]:
        if component.kind == "reference":
            return None, None
        if size[2] <= 0.0 or size[0] <= 0.0 or size[1] <= 0.0:
            return None, None

        wp = self._workplane_for_component(component, size)
        if wp is None:
            return None, None
        rotation = transform.rotation
        if rotation[0]:
            wp = wp.rotate((0, 0, 0), (1, 0, 0), rotation[0])
        if rotation[1]:
            wp = wp.rotate((0, 0, 0), (0, 1, 0), rotation[1])
        if rotation[2]:
            wp = wp.rotate((0, 0, 0), (0, 0, 1), rotation[2])
        pos = transform.position
        wp = wp.translate((pos[0], pos[1], pos[2]))
        solid = wp.val()
        return solid, footprint_from_solid(solid)

    def _workplane_for_component(self, component: RelationshipComponent, size: Tuple[float, float, float]) -> Optional[cq.Workplane]:
        profile = component.profile.lower().strip()
        if profile == "wedge":
            return self._build_wedge_workplane(component, size)
        if profile == "sweep":
            return self._build_sweep_workplane(component, size)
        return cq.Workplane("XY").box(size[0], size[1], size[2], centered=True)

    def _build_wedge_workplane(self, component: RelationshipComponent, size: Tuple[float, float, float]) -> Optional[cq.Workplane]:
        slope = float(component.profile_params.get("slope", component.profile_params.get("rise", 0.0)) or 0.0)
        hx = size[0] / 2
        hy = size[1] / 2
        hz = size[2] / 2
        if hx <= 0 or hy <= 0 or hz <= 0:
            return None
        top_positive = max(hz - slope, -hz)
        points = [
            (-hy, -hz),
            (hy, -hz),
            (hy, top_positive),
            (-hy, hz),
        ]
        return cq.Workplane("YZ").polyline(points).close().extrude(size[0], both=True)

    def _build_sweep_workplane(self, component: RelationshipComponent, size: Tuple[float, float, float]) -> Optional[cq.Workplane]:
        height = size[2]
        if height <= 0:
            return None
        points_raw = component.profile_params.get("points") or component.profile_params.get("profile") or ()
        points: List[Tuple[float, float]] = []
        if isinstance(points_raw, Sequence) and not isinstance(points_raw, (str, bytes)):
            for item in points_raw:
                if isinstance(item, Sequence) and len(item) >= 2:
                    try:
                        points.append((float(item[0]), float(item[1])))
                    except (TypeError, ValueError):
                        continue
        if len(points) < 3:
            half_x = size[0] / 2
            half_y = size[1] / 2
            points = [
                (-half_x, -half_y),
                (half_x, -half_y),
                (half_x, half_y),
                (-half_x, half_y),
            ]
        return cq.Workplane("XY").polyline(points).close().extrude(height, both=True)

    def _evaluate_checks(self, resolver: ReferenceResolver, diagnostics: SolveDiagnostics) -> None:
        for clause in self.spec.checks:
            subject_axes = _axes_from_pos(clause.subject)
            target_axes = {axis: sign for axis, sign in _axes_from_pos(clause.target.pos)}
            passed = True
            tolerance = clause.tolerance if clause.tolerance is not None else 0.0
            on_fail = (clause.on_fail or "error").lower()
            for axis, subject_sign in subject_axes:
                target_sign = target_axes.get(axis, subject_sign)
                world_axis, world_sign, alignment = resolver.world_axis_for(clause.target.frame, clause.target.ref, axis)
                if alignment < FRAME_ALIGNMENT_THRESHOLD:
                    message = (
                        f"check '{clause.subject}' using frame '{clause.target.frame}' on '{clause.target.ref}' maps local {axis} "
                        f"to world {world_axis} (alignment {alignment:.3f}); gaps/offsets use projected axis"
                    )
                    if message not in self._frame_warning_cache:
                        self._frame_warning_cache.add(message)
                        diagnostics.add_warning(message, subject=clause.target.ref)
                    summary_key = (f"check:{clause.subject}", clause.target.frame, clause.target.ref)
                    self._frame_summary.setdefault(summary_key, set()).add(f"{axis}->{world_axis} ({alignment:.3f})")
                subject_coord = resolver.axis_coordinate(
                    "self",
                    axis,
                    subject_sign,
                    frame=clause.target.frame,
                    mapped_axis=world_axis,
                    mapped_sign=world_sign,
                )
                object_coord = resolver.axis_coordinate(
                    clause.target.ref,
                    axis,
                    target_sign,
                    frame=clause.target.frame,
                    mapped_axis=world_axis,
                    mapped_sign=world_sign,
                )
                if object_coord is None:
                    diagnostics.add_error(f"check references unknown target '{clause.target.ref}'", subject=clause.target.ref)
                    passed = False
                    continue
                if subject_coord is None:
                    subject_coord = 0.0
                offset_amount = self._axis_amount_for(axis, subject_sign, clause.target.offset)
                gap_amount = self._axis_amount_for(axis, subject_sign, clause.target.gap)
                gap_direction = subject_sign * world_sign if subject_sign != 0 else 0
                adjusted_target = object_coord + offset_amount * world_sign + gap_amount * gap_direction
                delta = abs(subject_coord - adjusted_target)
                if delta > tolerance:
                    message = (
                        f"check failed between '{clause.subject}' and '{clause.target.ref}' on axis {axis} "
                        f"(delta {delta:.3f} > tolerance {tolerance:.3f})"
                    )
                    if on_fail == "warn":
                        diagnostics.add_warning(message, subject=clause.target.ref)
                    elif on_fail != "ignore":
                        diagnostics.add_error(message, subject=clause.target.ref)
                    passed = passed and on_fail == "ignore"
            result_text = "PASS" if passed else "FAIL"
            diagnostics.check_results.append(f"{result_text}: {clause.subject}->{clause.target.ref}")

    def _build_scene(self, primitives: Sequence[NeutralPrimitive]) -> trimesh.Scene:
        return build_scene_from_primitives(primitives)

    def _emit_frame_summaries(self, diagnostics: SolveDiagnostics) -> None:
        for key, mappings in sorted(self._frame_summary.items()):
            if not mappings:
                continue
            component_id, frame, ref = key
            mapping_text = ", ".join(sorted(mappings))
            message = (
                f"frame '{frame}' on '{ref}' projection summary for '{component_id}': {mapping_text}"
            )
            if message in self._frame_warning_cache:
                continue
            self._frame_warning_cache.add(message)
            diagnostics.add_warning(message, subject=component_id if component_id else None)

    def _detect_collisions(self, primitives: Sequence[NeutralPrimitive], diagnostics: SolveDiagnostics) -> None:
        if self.collision_mode == "ignore":
            return
        solids: List[tuple[str, Any]] = []
        void_map: Dict[str, set[str]] = {prim.id: set(prim.voids) for prim in primitives}
        prim_index: Dict[str, NeutralPrimitive] = {prim.id: prim for prim in primitives}
        for prim in primitives:
            if prim.solid is None:
                continue
            solids.append((prim.id, prim.solid))

        for idx, (first_id, first_solid) in enumerate(solids):
            for second_id, second_solid in solids[idx + 1 :]:
                if second_id in void_map.get(first_id, set()) or first_id in void_map.get(second_id, set()):
                    continue
                first_class = (prim_index.get(first_id).class_name or "").lower()
                second_class = (prim_index.get(second_id).class_name or "").lower()
                if first_class in self.collision_ignore or second_class in self.collision_ignore:
                    continue
                try:
                    intersection = first_solid.intersect(second_solid)
                except Exception:
                    continue
                volume = 0.0
                if intersection is not None and hasattr(intersection, "Volume"):
                    try:
                        volume = float(intersection.Volume())
                    except Exception:
                        volume = 0.0
                if volume > 1e-6:
                    diagnostics.collisions.append((first_id, second_id, volume))
                    message = (
                        f"collision detected between '{first_id}' and '{second_id}' (overlap {volume:.3f} mm³)"
                    )
                    if self.collision_mode == "warn":
                        diagnostics.add_warning(message)
                    else:
                        diagnostics.add_error(message)

    # ------------------------------------------------------------------ #
    def _build_points(self, spec: RelationshipDiagramSpec) -> Dict[str, Dict[str, float]]:
        points: Dict[str, Dict[str, float]] = {}
        for name, point in spec.datums.items():
            coords: Dict[str, float] = {}
            for axis_token, value in point.coordinates.items():
                axis = axis_token[-1]
                coords[axis] = value
                coords[axis_token] = value
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


def footprint_from_solid(solid: Any) -> Optional[ShapelyPolygon]:
    if solid is None:
        return None
    try:
        verts = solid.Vertices()
        points = [(float(v.X), float(v.Y)) for v in verts]
        hull = MultiPoint(points).convex_hull
        if hull.is_empty or not isinstance(hull, ShapelyPolygon):
            return None
        return hull
    except Exception:
        return None


def mesh_from_primitive(primitive: NeutralPrimitive, *, to_meters: bool = True) -> Optional[trimesh.Trimesh]:
    if primitive.mesh is not None:
        mesh = primitive.mesh.copy()
        if to_meters:
            mesh.apply_scale(MM_TO_METERS)
        return mesh
    if primitive.solid is not None and hasattr(primitive.solid, "tessellate"):
        try:
            vertices, faces = primitive.solid.tessellate(1.0)
        except Exception:
            vertices, faces = ((), ())
        if vertices and faces:
            converted: List[Tuple[float, float, float]] = []
            for v in vertices:
                try:
                    if hasattr(v, "toTuple"):
                        converted.append(tuple(float(coord) for coord in v.toTuple()))  # type: ignore[attr-defined]
                    elif hasattr(v, "X"):
                        converted.append((float(v.X), float(v.Y), float(v.Z)))  # type: ignore[attr-defined]
                    elif hasattr(v, "x"):
                        converted.append((float(v.x), float(v.y), float(v.z)))  # type: ignore[attr-defined]
                    else:
                        converted.append((float(v[0]), float(v[1]), float(v[2])))  # type: ignore[index]
                except Exception:
                    continue
            if converted:
                vertices = converted
            mesh_mm = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=False)
            rotation = primitive.transform.rotation
            if any(rotation):
                try:
                    rot = trimesh.transformations.euler_matrix(
                        math.radians(rotation[0]),
                        math.radians(rotation[1]),
                        math.radians(rotation[2]),
                        axes="sxyz",
                    )
                    mesh_mm.apply_transform(rot)
                except Exception:
                    pass
            pos = primitive.transform.position
            mesh_mm.apply_translation((pos[0], pos[1], pos[2]))
            primitive.mesh = mesh_mm.copy()
            mesh = mesh_mm.copy()
            if to_meters:
                mesh.apply_scale(MM_TO_METERS)
            return mesh

    if primitive.size[2] <= 0.0:
        return None

    mesh_mm = trimesh.creation.box(extents=np.array(primitive.size))
    rotation = primitive.transform.rotation
    if any(rotation):
        try:
            rot = trimesh.transformations.euler_matrix(
                math.radians(rotation[0]), math.radians(rotation[1]), math.radians(rotation[2]), axes="sxyz"
            )
            mesh_mm.apply_transform(rot)
        except Exception:
            pass
    pos = primitive.transform.position
    mesh_mm.apply_translation((pos[0], pos[1], pos[2]))
    primitive.mesh = mesh_mm.copy()
    mesh = mesh_mm.copy()
    if to_meters:
        mesh.apply_scale(MM_TO_METERS)
    return mesh


def build_scene_from_primitives(primitives: Sequence[NeutralPrimitive], *, to_meters: bool = True) -> trimesh.Scene:
    scene = trimesh.Scene()
    for primitive in primitives:
        mesh = mesh_from_primitive(primitive, to_meters=to_meters)
        if mesh is None:
            continue
        mesh.metadata = primitive.metadata.copy()
        mesh.metadata.setdefault("guid", primitive.guid)
        scene.add_geometry(mesh, node_name=primitive.id)
    return scene


__all__ = [
    "ConnectionHint",
    "ComponentTransform",
    "ConstraintSolver",
    "NeutralPrimitive",
    "SolveDiagnostics",
    "SolveResult",
    "SolvedComponent",
    "build_scene_from_primitives",
    "footprint_from_solid",
    "mesh_from_primitive",
]
