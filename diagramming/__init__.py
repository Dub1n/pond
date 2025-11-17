"""
Core entrypoints for the pond diagramming toolkit.

Phase 1 exposes a minimal API consisting of:

- schema parsing helpers under `diagramming.schema`
- the diagram planner under `diagramming.planner`
- SVG rendering helpers under `diagramming.renderers`
"""

from .planner.planner import DiagramPlanner  # noqa: F401

__all__ = ["DiagramPlanner"]
