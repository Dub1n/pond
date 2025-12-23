"""
Relationship-first schema scaffolding and helpers.
"""

from .flags import is_relationship_schema
from .lint import lint_relationship_spec
from .solver import ComponentTransform, ConstraintSolver, NeutralPrimitive, SolveDiagnostics, SolveResult, SolvedComponent
from .schema import (
    AxisRelation,
    AxisMapTarget,
    BooleanOperation,
    DimensionResolver,
    MirrorOperation,
    RotateOperation,
    TranslateOperation,
    canonical_pos_token,
    RelationshipComponent,
    RelationshipDiagramSpec,
    SchemaError,
    load_relationship_spec,
)
from .planner import RelationshipPlanner, RelationshipPlannedView, RelationshipOption
from .validation import (
    DualRenderDiff,
    ValidationReport,
    dual_render_compare,
    mesh_checksum,
    relationship_bundle,
    validate_relationship_spec,
)

__all__ = [
    "AxisRelation",
    "AxisMapTarget",
    "BooleanOperation",
    "DualRenderDiff",
    "canonical_pos_token",
    "DimensionResolver",
    "MirrorOperation",
    "RotateOperation",
    "TranslateOperation",
    "ComponentTransform",
    "ConstraintSolver",
    "lint_relationship_spec",
    "NeutralPrimitive",
    "RelationshipComponent",
    "RelationshipDiagramSpec",
    "SchemaError",
    "SolveDiagnostics",
    "SolveResult",
    "SolvedComponent",
    "ValidationReport",
    "RelationshipPlanner",
    "RelationshipPlannedView",
    "RelationshipOption",
    "relationship_bundle",
    "dual_render_compare",
    "is_relationship_schema",
    "load_relationship_spec",
    "mesh_checksum",
    "validate_relationship_spec",
]
