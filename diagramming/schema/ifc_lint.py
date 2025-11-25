from __future__ import annotations

from typing import List

from ..ifc import normalize_ifc_class
from .spec import DiagramSpec


def lint_ifc_metadata(spec: DiagramSpec) -> List[str]:
    """
    Lightweight IFC readiness checks for legacy specs.

    - Components using IFC classes must declare an ifc block with a predefined type.
    - Pset names must be non-empty.
    """

    errors: List[str] = []
    for option in spec.options.values():
        for component in option.components:
            class_name = normalize_ifc_class(getattr(component, "class_name", None))
            ifc_meta = getattr(component, "ifc", None)

            if class_name and class_name.lower().startswith("ifc") and ifc_meta is None:
                errors.append(
                    f"option '{option.key}' component '{component.id}' uses IFC class '{class_name}' without an ifc block"
                )
                continue

            if ifc_meta is None:
                continue

            if ifc_meta.predefined_type is None:
                errors.append(
                    f"option '{option.key}' component '{component.id}' ifc block is missing predefined_type"
                )
            for pset in ifc_meta.psets:
                if not pset.name:
                    errors.append(
                        f"option '{option.key}' component '{component.id}' ifc block has an empty pset name"
                    )
    return errors


__all__ = ["lint_ifc_metadata"]
