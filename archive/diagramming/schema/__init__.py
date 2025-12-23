"""
Schema parsing utilities for pond diagram specs.

Phase 1 keeps things intentionally light-weight: YAML specs are parsed into
dataclasses with only the validation required to keep authoring ergonomic.
"""

from .spec import DiagramSpec, load_spec  # noqa: F401

__all__ = ["DiagramSpec", "load_spec"]
