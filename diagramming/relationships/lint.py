from __future__ import annotations

from typing import Iterable, List, Set

from .schema import (
    AlignmentClause,
    FlushBundleClause,
    RelationshipComponent,
    RelationshipDiagramSpec,
    RunBetweenClause,
)


def lint_relationship_spec(spec: RelationshipDiagramSpec) -> List[str]:
    """
    Returns a list of human-friendly error messages describing schema issues.
    Empty list means the spec passed linting.
    """

    errors: List[str] = []
    component_ids = {component.id for component in spec.components}
    datum_points = set(spec.datums.keys())
    datum_planes = set(spec.planes.keys())
    datum_bundles = set(spec.bundles.keys())

    for check in spec.checks:
        _lint_check(
            check,
            datum_points=datum_points,
            datum_planes=datum_planes,
            datum_bundles=datum_bundles,
            component_ids=component_ids,
            errors=errors,
        )

    for component in spec.components:
        _lint_component(
            component,
            component_ids=component_ids,
            datum_points=datum_points,
            datum_planes=datum_planes,
            datum_bundles=datum_bundles,
            errors=errors,
        )

    return errors


def _lint_component(
    component: RelationshipComponent,
    *,
    component_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
    errors: List[str],
) -> None:
    for clause in component.relationships:
        if isinstance(clause, AlignmentClause):
            _lint_ref(clause.subject.ref, component, component_ids, datum_points, datum_planes, datum_bundles, errors)
            _lint_ref(clause.obj.ref, component, component_ids, datum_points, datum_planes, datum_bundles, errors)
        elif isinstance(clause, FlushBundleClause):
            _lint_ref(clause.bundle, component, component_ids, datum_points, datum_planes, datum_bundles, errors)
        elif isinstance(clause, RunBetweenClause):
            _lint_ref(clause.from_ref.ref, component, component_ids, datum_points, datum_planes, datum_bundles, errors)
            _lint_ref(clause.to_ref.ref, component, component_ids, datum_points, datum_planes, datum_bundles, errors)
            if clause.orient not in {"preserve_axes", "along_run"}:
                errors.append(f"component '{component.id}' run_between uses unsupported orient '{clause.orient}'")

    for void in component.voids:
        if void not in component_ids:
            errors.append(f"component '{component.id}' void references unknown component '{void}'")

    repeat = component.repeat
    if repeat and repeat.span_use:
        _lint_ref(repeat.span_use, component, component_ids, datum_points, datum_planes, datum_bundles, errors)

    if component.class_name.lower().startswith("ifc") and component.ifc is None:
        errors.append(f"component '{component.id}' uses IFC class '{component.class_name}' without an ifc block")


def _lint_ref(
    ref: str,
    component: RelationshipComponent,
    component_ids: Set[str],
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
    errors: List[str],
) -> None:
    if ref == "self":
        return
    if ref in component_ids or ref in datum_points or ref in datum_planes or ref in datum_bundles:
        return
    if ref.startswith("datums."):
        segments = ref.split(".")
        if len(segments) == 2:
            name = segments[1]
            if name in datum_points or name in datum_planes or name in datum_bundles:
                return
        elif len(segments) >= 3:
            category = segments[1]
            name = ".".join(segments[2:])
            if category == "planes" and name in datum_planes:
                return
            if category == "bundles":
                if name in datum_bundles:
                    return
                base = name.split(".")[0]
                if base in datum_bundles:
                    return
            if category in {"points", "point"} and name in datum_points:
                return
    errors.append(f"component '{component.id}' references unknown target '{ref}'")


def _lint_check(
    clause: AlignmentClause,
    *,
    datum_points: Set[str],
    datum_planes: Set[str],
    datum_bundles: Set[str],
    component_ids: Set[str],
    errors: List[str],
) -> None:
    dummy_component = RelationshipComponent(
        id="__checks__",
        class_name="",
        profile="rectangle",
        size_xy=(0.0, 0.0),
        height=0.0,
    )
    _lint_ref(clause.subject.ref, dummy_component, component_ids, datum_points, datum_planes, datum_bundles, errors)
    _lint_ref(clause.obj.ref, dummy_component, component_ids, datum_points, datum_planes, datum_bundles, errors)


__all__ = ["lint_relationship_spec"]
