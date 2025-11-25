from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .schema import RelationshipComponent, RelationshipDiagramSpec


@dataclass(slots=True)
class Diagnostic:
    level: str
    message: str
    subject: str | None = None


@dataclass(slots=True)
class SolveDiagnostics:
    errors: List[Diagnostic] = field(default_factory=list)
    warnings: List[Diagnostic] = field(default_factory=list)

    def add_error(self, message: str, *, subject: str | None = None) -> None:
        self.errors.append(Diagnostic(level="error", message=message, subject=subject))

    def add_warning(self, message: str, *, subject: str | None = None) -> None:
        self.warnings.append(Diagnostic(level="warning", message=message, subject=subject))

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(slots=True)
class SolvedComponent:
    component: RelationshipComponent
    transform: Dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class SolveResult:
    components: Tuple[SolvedComponent, ...]
    diagnostics: SolveDiagnostics


class ConstraintSolver:
    """
    Placeholder constraint solver for the relationship-first schema.

    The real solver will resolve face/edge relationships into canonical
    transforms. For now we only surface a diagnostics carrier so downstream
    callers can wire the control flow without blocking on implementation.
    """

    def __init__(self, spec: RelationshipDiagramSpec) -> None:
        self.spec = spec

    def solve(self) -> SolveResult:
        diagnostics = SolveDiagnostics()
        # Until the solver is implemented, emit a warning so callers know the
        # result does not contain resolved geometry.
        diagnostics.add_warning(
            "Relationship-first solver scaffold is in place; transforms are not yet resolved.",
            subject=self.spec.info.title or self.spec.schema,
        )
        solved = tuple(SolvedComponent(component=component) for component in self.spec.components)
        return SolveResult(components=solved, diagnostics=diagnostics)


__all__ = ["ConstraintSolver", "SolveDiagnostics", "SolveResult", "SolvedComponent"]
