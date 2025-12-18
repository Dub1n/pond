from __future__ import annotations

import os
from typing import Any


_ENV_FLAG = "DIAGRAM_RELATIONSHIPS"
_SCHEMA_PREFIX = "pond-relationship"
_COLLISION_FLAG = "DIAGRAM_RELATIONSHIPS_COLLISIONS"
_FAIL_ON_WARN_FLAG = "DIAGRAM_RELATIONSHIPS_FAIL_ON_WARN"
_COLLISION_IGNORE_CLASSES_FLAG = "DIAGRAM_RELATIONSHIPS_COLLISIONS_IGNORE_CLASSES"


def relationship_mode_enabled() -> bool:
    """
    Returns True when the Phase 4 relationship-first pipeline is explicitly
    enabled via environment variable. The legacy planner remains the default.
    """

    raw = os.getenv(_ENV_FLAG)
    if raw is None:
        return False
    return raw.lower() in {"1", "true", "yes", "on"}


def collision_handling_mode() -> str:
    """
    Controls how the solver treats solid collisions. Defaults to 'error'.
    Supported values:
      - 'error' (default): collisions raise errors
      - 'warn': collisions are recorded as warnings
      - 'ignore': collisions are skipped
    """

    raw = os.getenv(_COLLISION_FLAG)
    if raw is None:
        return "error"
    value = raw.strip().lower()
    if value in {"warn", "warning"}:
        return "warn"
    if value in {"ignore", "skip", "off"}:
        return "ignore"
    return "error"


def fail_on_warn() -> bool:
    """
    When set, upgrades solver warnings to errors (e.g., collisions, guardrails).
    """

    raw = os.getenv(_FAIL_ON_WARN_FLAG)
    if raw is None:
        return False
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def collision_ignore_classes() -> set[str]:
    """
    Returns a set of IFC class names to skip during collision detection.
    Defaults to ignoring `ifcfooting`.
    """

    raw = os.getenv(_COLLISION_IGNORE_CLASSES_FLAG)
    ignores = {"ifcfooting"}
    if raw is None:
        return ignores
    entries = [item.strip().lower() for item in raw.split(",") if item.strip()]
    ignores.update(entries)
    return ignores


def is_relationship_schema(schema_field: Any) -> bool:
    """
    Lightweight check to decide whether a YAML document should be parsed using
    the relationship-first loader. Accepts any value starting with the schema
    prefix recorded in the relationship-first prep report.
    """

    if schema_field is None:
        return False
    try:
        text = str(schema_field).strip().lower()
    except Exception:
        return False
    return text.startswith(_SCHEMA_PREFIX)


__all__ = [
    "relationship_mode_enabled",
    "collision_handling_mode",
    "collision_ignore_classes",
    "fail_on_warn",
    "is_relationship_schema",
]
