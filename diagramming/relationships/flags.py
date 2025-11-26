from __future__ import annotations

import os
from typing import Any


_ENV_FLAG = "DIAGRAM_RELATIONSHIPS"
_SCHEMA_PREFIX = "pond-relationship"
_COLLISION_FLAG = "DIAGRAM_RELATIONSHIPS_COLLISIONS"


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


__all__ = ["relationship_mode_enabled", "collision_handling_mode", "is_relationship_schema"]
