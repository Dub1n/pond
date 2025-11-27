from __future__ import annotations

from typing import List, Set

from .schema import (
    AxisRelation,
    BooleanOperation,
    MirrorOperation,
    RelationshipComponent,
    RelationshipDiagramSpec,
    RotateOperation,
    RunBetweenSpec,
    TranslateOperation,
)
from .solver import ConstraintSolver


IFC_REQUIREMENTS = {
    "ifcbeam": {"predefined": True, "material": True},
    "ifcmember": {"predefined": True, "material": True},
    "ifcslab": {"predefined": True, "material": True},
    "ifcopeningelement": {"predefined": True, "material": False},
}


def lint_relationship_spec(spec: RelationshipDiagramSpec) -> List[str]:
    """
    Returns a list of human-friendly error messages describing schema issues.
    Empty list means the spec passed linting.
    """

    errors: List[str] = []
    component_ids = {component.id for component in spec.components}
    placement_ids = {
        placement.id for component in spec.components for placement in component.place
    }
    known_ids = component_ids | placement_ids
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
        _lint_operation(
            operation,
            known_ids=known_ids,
            errors=errors,
        )

    # Use the solver to surface inferred size conflicts and under-constrained axes.
    try:
        solver = ConstraintSolver(spec)
        result = solver.solve()
        errors.extend([err.message for err in result.diagnostics.errors])
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

    run_between = component.run_between
    if run_between:
        _lint_run_between(run_between, component, known_ids, datum_points, datum_planes, datum_bundles, errors)

    for void in component.voids:
        if void not in known_ids:
            errors.append(f"component '{component.id}' void references unknown component '{void}'")

    axes_present = _axis_coverage(component)
    if component.kind != "reference":
        for axis in ("x", "y", "z"):
            if axis not in axes_present:
                errors.append(f"component '{component.id}' is missing placement on axis {axis}")

    requirements = IFC_REQUIREMENTS.get(class_lower)
    if requirements:
        if requirements.get("predefined") and (component.ifc is None or component.ifc.predefined_type is None):
            errors.append(
                f"component '{component.id}' ({component.class_name}) must declare ifc.predefined_type per mapping table"
            )
        if requirements.get("material") and not component.material:
            errors.append(f"component '{component.id}' ({component.class_name}) must declare a material")


def _axis_coverage(component: RelationshipComponent) -> Set[str]:
    axes: Set[str] = set()
    for relation in component.relations:
        for axis, _ in _axes_from_pos(relation.subject):
            axes.add(axis)
    run_between = component.run_between
    if run_between:
        for axis, _ in _axes_from_pos(run_between.start_pos):
            axes.add(axis)
        for axis, _ in _axes_from_pos(run_between.end_pos):
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


def _lint_run_between(
    run_between: RunBetweenSpec,
    component: RelationshipComponent,
    component_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
    errors: List[str],
) -> None:
    for target in (run_between.from_ref, run_between.to_ref):
        if not _ref_known(target.ref, component_ids, datum_points, datum_planes, datum_bundles):
            errors.append(f"component '{component.id}' run_between references unknown target '{target.ref}'")
    if run_between.orient not in {"preserve_axes", "along_run"}:
        errors.append(f"component '{component.id}' run_between uses unsupported orient '{run_between.orient}'")


def _lint_operation(operation: object, *, known_ids: Set[str], errors: List[str]) -> None:
    selectors: List[str] = []
    if isinstance(operation, RotateOperation):
        selectors.extend(operation.targets)
        selectors.extend(operation.id_map.keys())
    elif isinstance(operation, (MirrorOperation, TranslateOperation)):
        selectors.extend(operation.targets)
    elif isinstance(operation, BooleanOperation):
        selectors.append(operation.target)
        selectors.extend(operation.subtract)

    for selector in selectors:
        base = selector.split(".", 1)[0]
        if base and base not in known_ids:
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


def _ref_known(ref: str, component_ids: Set[str], datum_points: Set[str], datum_planes: Set[str], datum_bundles: Set[str]) -> bool:
    if ref == "self":
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


__all__ = ["lint_relationship_spec"]
