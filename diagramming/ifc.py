from __future__ import annotations

from typing import Any, Optional


def normalize_ifc_class(value: Any) -> Optional[str]:
    """
    Canonicalise IFC class names so downstream exporters receive predictable
    identifiers. Non-IFC classes pass through unchanged.
    """

    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if not text.lower().startswith("ifc"):
        return text
    suffix = text[3:]
    if suffix:
        suffix = suffix[0].upper() + suffix[1:]
    return f"Ifc{suffix}"


def normalize_ifc_predefined_type(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text.upper() if text else None


def normalize_pset_name(value: Any) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("pset name cannot be empty")
    if text.lower().startswith("pset_"):
        return f"Pset_{text[len('pset_'):]}"
    return text


__all__ = ["normalize_ifc_class", "normalize_ifc_predefined_type", "normalize_pset_name"]
