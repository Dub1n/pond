"""
Relationship-first schema scaffolding and helpers.

This package intentionally avoids touching the legacy planner until the
constraint solver and CadQuery integration are ready. The loader and lints
let us validate relationship-first specs and iterate on the schema surface
behind a feature flag.
"""

from .flags import is_relationship_schema, relationship_mode_enabled
from .lint import lint_relationship_spec
from .solver import ComponentTransform, ConstraintSolver, NeutralPrimitive, SolveDiagnostics, SolveResult, SolvedComponent
from .schema import (
    AlignmentClause,
    DimensionResolver,
    FlushBundleClause,
    canonical_pos_token,
    RelationshipComponent,
    RelationshipDiagramSpec,
    RunBetweenClause,
    SchemaError,
    load_relationship_spec,
)
from .planner import RelationshipPlanner, RelationshipPlannedView, RelationshipOption

__all__ = [
    "AlignmentClause",
    "canonical_pos_token",
    "DimensionResolver",
    "FlushBundleClause",
    "ComponentTransform",
    "ConstraintSolver",
    "lint_relationship_spec",
    "NeutralPrimitive",
    "RelationshipComponent",
    "RelationshipDiagramSpec",
    "RunBetweenClause",
    "SchemaError",
    "SolveDiagnostics",
    "SolveResult",
    "SolvedComponent",
    "RelationshipPlanner",
    "RelationshipPlannedView",
    "RelationshipOption",
    "is_relationship_schema",
    "load_relationship_spec",
    "relationship_mode_enabled",
]
