from __future__ import annotations

from typing import Dict, List, Sequence, Set

from .schema import (
    ArraySpec,
    AxisRelation,
    BooleanOperation,
    MirrorOperation,
    RelationshipComponent,
    RelationshipDiagramSpec,
    RotateOperation,
    TranslateOperation,
)
from .solver import ConstraintSolver



def lint_relationship_spec(spec: RelationshipDiagramSpec) -> List[str]:
    """
    Returns a list of human-friendly error messages describing schema issues.
    Empty list means the spec passed linting.
    """

    errors: List[str] = []
    component_ids = {component.id for component in spec.components}
    placement_ids = {placement.id for component in spec.components for placement in component.place}
    known_ids = _expand_known_ids(component_ids | placement_ids, spec.operations)
    datum_points = set(spec.datums.keys())
    datum_planes = set(spec.planes.keys())
    datum_bundles = set(spec.bundles.keys())

    for check in spec.checks:
        _lint_axis_relation(
            check,
            component_ids=known_ids,
            datum_points=datum_points,
            datum_planes=datum_planes,
            datum_bundles=datum_bundles,
            errors=errors,
            context="checks",
        )

    for component in spec.components:
        _lint_component(
            component,
            known_ids=known_ids,
            datum_points=datum_points,
            datum_planes=datum_planes,
            datum_bundles=datum_bundles,
            errors=errors,
        )

    for operation in spec.operations:
        _lint_operation(operation, known_ids=known_ids, errors=errors)

    # Use the solver to surface inferred size conflicts and under-constrained axes.
    try:
        solver = ConstraintSolver(spec)
        result = solver.solve()
        errors.extend([err.message for err in result.diagnostics.errors])
        _lint_operation_selectors(spec.operations, result.components, errors)
        _lint_resolved_refs(
            spec,
            instance_ids={comp.instance_id for comp in result.components},
            datum_points=datum_points,
            datum_planes=datum_planes,
            datum_bundles=datum_bundles,
            errors=errors,
        )
    except Exception as exc:  # pragma: no cover - guardrail for missing deps
        errors.append(f"lint solver failed: {exc}")

    return errors


def _lint_component(
    component: RelationshipComponent,
    *,
    known_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
    errors: List[str],
) -> None:
    class_lower = (component.class_name or "").lower()
    for relation in component.relations:
        _lint_axis_relation(
            relation,
            component_ids=known_ids,
            datum_points=datum_points,
            datum_planes=datum_planes,
            datum_bundles=datum_bundles,
            errors=errors,
            context=f"component '{component.id}'",
        )

    array = component.array
    if array:
        _lint_array(array, component, known_ids, datum_points, datum_planes, datum_bundles, errors)

    for void in component.voids:
        if void not in known_ids:
            errors.append(f"component '{component.id}' void references unknown component '{void}'")

    axes_present = _axis_coverage(component)
    if component.kind != "reference":
        for axis in ("x", "y", "z"):
            if axis not in axes_present:
                errors.append(f"component '{component.id}' is missing placement on axis {axis}")



def _axis_coverage(component: RelationshipComponent) -> Set[str]:
    axes: Set[str] = set()
    for relation in component.relations:
        for axis, _ in _axes_from_pos(relation.subject):
            axes.add(axis)
    for placement in component.place:
        for relation in placement.relations:
            for axis, _ in _axes_from_pos(relation.subject):
                axes.add(axis)
    array = component.array
    if array:
        for relation in array.relations:
            for axis, _ in _axes_from_pos(relation.subject):
                axes.add(axis)
        for through in array.through:
            for relation in through.relations:
                for axis, _ in _axes_from_pos(relation.subject):
                    axes.add(axis)
    return axes


def _lint_axis_relation(
    relation: AxisRelation,
    *,
    component_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
    errors: List[str],
    context: str,
) -> None:
    if not _ref_known(relation.target.ref, component_ids, datum_points, datum_planes, datum_bundles):
        errors.append(f"{context} references unknown target '{relation.target.ref}'")
    mode = (relation.target.mode or "point").lower()
    if mode not in {"point", "plane", "edge"}:
        errors.append(f"{context} uses unsupported mode '{relation.target.mode}'")
    subject_axes = _axes_from_pos(relation.subject)
    if mode == "plane" and len(subject_axes) != 1:
        errors.append(f"{context} mode 'plane' requires a single-axis subject (got '{relation.subject}')")
    if mode == "edge" and len(subject_axes) != 2:
        errors.append(f"{context} mode 'edge' requires two-axis subject (got '{relation.subject}')")


def _lint_array(
    array: ArraySpec,
    component: RelationshipComponent,
    component_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
    errors: List[str],
) -> None:
    label = array.source or "array"
    if not array.relations:
        errors.append(f"component '{component.id}' {label} requires axis-map relations")
    for relation in array.relations:
        _lint_axis_relation(
            relation,
            component_ids=component_ids,
            datum_points=datum_points,
            datum_planes=datum_planes,
            datum_bundles=datum_bundles,
            errors=errors,
            context=f"component '{component.id}' {label}",
        )
    for through in array.through:
        for relation in through.relations:
            _lint_axis_relation(
                relation,
                component_ids=component_ids,
                datum_points=datum_points,
                datum_planes=datum_planes,
                datum_bundles=datum_bundles,
                errors=errors,
                context=f"component '{component.id}' {label}.through",
            )
    for axis, spec in array.repeat.items():
        if spec.count is not None and spec.count < 1:
            errors.append(f"component '{component.id}' {label} repeat.{axis} count must be >= 1")


def _lint_operation(operation: object, *, known_ids: Set[str], errors: List[str]) -> None:
    selectors: List[str] = []
    if isinstance(operation, RotateOperation):
        selectors.extend(operation.targets)
        selectors.extend(operation.id_map.keys())
        for base, mapped in operation.id_map.items():
            if base not in known_ids:
                errors.append(f"rotate.id_map references unknown base '{base}'")
            if len(mapped) != operation.count:
                errors.append(
                    f"rotate.id_map for '{base}' provides {len(mapped)} ids but count={operation.count}"
                )
    elif isinstance(operation, (MirrorOperation, TranslateOperation)):
        selectors.extend(operation.targets)
    elif isinstance(operation, BooleanOperation):
        selectors.append(operation.target)
        selectors.extend(operation.subtract)

    for selector in selectors:
        base = selector.split(".", 1)[0]
        base_id = base.split("#", 1)[0]
        if base and base not in known_ids and base_id not in known_ids:
            errors.append(f"operation references unknown selector '{selector}'")


def _axes_from_pos(pos_token: str) -> List[tuple[str, int]]:
    axes: List[tuple[str, int]] = []
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


def _ref_known(
    ref: str,
    component_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
) -> bool:
    if ref in {"self", "__world__"}:
        return True
    if "#" in ref:
        base, _, suffix = ref.partition("#")
        if base and suffix.isdigit() and base in component_ids:
            return True
    if ref in component_ids or ref in datum_points or ref in datum_planes or ref in datum_bundles:
        return True
    if ref.startswith("datums."):
        segments = ref.split(".")
        if len(segments) == 2:
            name = segments[1]
            return name in datum_points or name in datum_planes or name in datum_bundles
        if len(segments) >= 3:
            category = segments[1]
            name = ".".join(segments[2:])
            if category == "planes":
                return name in datum_planes
            if category == "bundles":
                return name in datum_bundles or name.split(".")[0] in datum_bundles
            if category in {"points", "point"}:
                return name in datum_points
    return False


def _selector_index(components: Sequence[object]) -> Dict[str, Dict[str, set[str]]]:
    index: Dict[str, Dict[str, set[str]]] = {}
    for item in components:
        template_id = getattr(item, "template_id", None)
        if not template_id:
            continue
        entry = index.setdefault(template_id, {"all": set(), "original": set(), "clones": set()})
        entry["all"].add(item.instance_id)
        if getattr(item, "origin", "original") == "original":
            entry["original"].add(item.instance_id)
        else:
            entry["clones"].add(item.instance_id)
        seed_id = getattr(item, "seed_id", None)
        if seed_id:
            seed_entry = index.setdefault(seed_id, {"all": set(), "original": set(), "clones": set()})
            seed_entry["all"].add(item.instance_id)
            if getattr(item, "origin", "original") == "original":
                seed_entry["original"].add(item.instance_id)
            else:
                seed_entry["clones"].add(item.instance_id)
    return index


def _resolve_selector(selector: str, index: Dict[str, Dict[str, set[str]]]) -> List[str]:
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
    for entry in index.values():
        if selector in entry.get("all", set()):
            return [selector]
    return []


def _lint_operation_selectors(operations: Sequence[object], components: Sequence[object], errors: List[str]) -> None:
    index = _selector_index(components)
    for operation in operations:
        selectors: List[str] = []
        if isinstance(operation, RotateOperation):
            selectors.extend(operation.targets)
        elif isinstance(operation, (MirrorOperation, TranslateOperation)):
            selectors.extend(operation.targets)
        elif isinstance(operation, BooleanOperation):
            selectors.append(operation.target)
            selectors.extend(operation.subtract)
        for selector in selectors:
            if selector and not _resolve_selector(selector, index):
                errors.append(f"operation references unknown selector '{selector}'")


def _expand_known_ids(component_ids: Set[str], operations: Sequence[object]) -> Set[str]:
    known_ids = set(component_ids)
    for operation in operations:
        if isinstance(operation, RotateOperation):
            expanded: Set[str] = set()
            if operation.id_map:
                for mapped in operation.id_map.values():
                    expanded.update(mapped)
            else:
                targets = operation.targets or tuple(known_ids)
                for selector in targets:
                    base = selector.split(".", 1)[0]
                    base_id = base.split("#", 1)[0]
                    if base_id in known_ids:
                        for turn in range(1, operation.count):
                            expanded.add(f"{base_id}_rot{turn}")
            known_ids.update(expanded)
        elif isinstance(operation, MirrorOperation):
            targets = operation.targets or tuple(known_ids)
            for selector in targets:
                base = selector.split(".", 1)[0]
                base_id = base.split("#", 1)[0]
                if base_id in known_ids:
                    known_ids.add(f"{base_id}_mirrored")
        elif isinstance(operation, TranslateOperation):
            targets = operation.targets or tuple(known_ids)
            for selector in targets:
                base = selector.split(".", 1)[0]
                base_id = base.split("#", 1)[0]
                if base_id in known_ids:
                    known_ids.add(f"{base_id}_translated")
    return known_ids


def _ref_known_instance(
    ref: str,
    instance_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
) -> bool:
    if ref in {"self", "__world__"}:
        return True
    if ref in instance_ids:
        return True
    if ref in datum_points or ref in datum_planes or ref in datum_bundles:
        return True
    if ref.startswith("datums."):
        segments = ref.split(".")
        if len(segments) == 2:
            name = segments[1]
            return name in datum_points or name in datum_planes or name in datum_bundles
        if len(segments) >= 3:
            category = segments[1]
            name = ".".join(segments[2:])
            if category == "planes":
                return name in datum_planes
            if category == "bundles":
                return name in datum_bundles or name.split(".")[0] in datum_bundles
            if category in {"points", "point"}:
                return name in datum_points
    return False


def _lint_resolved_refs(
    spec: RelationshipDiagramSpec,
    *,
    instance_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
    errors: List[str],
) -> None:
    def validate_relations(relations: Tuple[AxisRelation, ...], context: str) -> None:
        for relation in relations:
            if not _ref_known_instance(
                relation.target.ref,
                instance_ids,
                datum_points,
                datum_planes,
                datum_bundles,
            ):
                errors.append(f"{context} references unknown target '{relation.target.ref}'")

    for check in spec.checks:
        if not _ref_known_instance(
            check.target.ref,
            instance_ids,
            datum_points,
            datum_planes,
            datum_bundles,
        ):
            errors.append(f"checks references unknown target '{check.target.ref}'")

    for component in spec.components:
        validate_relations(component.relations, f"component '{component.id}'")
        for placement in component.place:
            validate_relations(placement.relations, f"component '{component.id}' place '{placement.id}'")
        array = component.array
        if array:
            label = array.source or "array"
            validate_relations(array.relations, f"component '{component.id}' {label}")
            for through in array.through:
                validate_relations(through.relations, f"component '{component.id}' {label}.through")


__all__ = ["lint_relationship_spec"]
