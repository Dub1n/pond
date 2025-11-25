from __future__ import annotations

import os
from typing import Any


_ENV_FLAG = "DIAGRAM_RELATIONSHIPS"
_SCHEMA_PREFIX = "pond-relationship"


def relationship_mode_enabled() -> bool:
    """
    Returns True when the Phase 4 relationship-first pipeline is explicitly
    enabled via environment variable. The legacy planner remains the default.
    """

    raw = os.getenv(_ENV_FLAG)
    if raw is None:
        return False
    return raw.lower() in {"1", "true", "yes", "on"}


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


__all__ = ["relationship_mode_enabled", "is_relationship_schema"]
