from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Tuple


@dataclass(frozen=True)
class LanguageExperience:
    """Evidence-bearing language experience that cannot apply itself."""

    experience_id: str
    kind: str
    concept: str
    observed_expression: str | None = None
    candidate_expression: str | None = None
    source_role: str = "unknown"
    confidence: float = 0.0
    context: Mapping[str, str] = field(default_factory=dict)
    evidence_refs: Tuple[str, ...] = ()
    proposal_only: bool = True
    change_applied: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.experience_id.strip():
            raise ValueError("experience_id is required")
        if not self.kind.strip():
            raise ValueError("kind is required")
        if not self.concept.strip():
            raise ValueError("concept is required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not self.proposal_only:
            raise ValueError("language experience must remain proposal-only")
        if self.change_applied:
            raise ValueError("language experience cannot apply its own change")
        if self.grants_authority:
            raise ValueError("language experience cannot grant authority")


def correction_experience(
    *,
    experience_id: str,
    concept: str,
    observed_expression: str,
    candidate_expression: str,
    source_role: str,
    confidence: float,
    context: Mapping[str, str] | None = None,
    evidence_refs: Tuple[str, ...] = (),
) -> LanguageExperience:
    """Create a bounded correction observation for governed learning review."""

    return LanguageExperience(
        experience_id=experience_id,
        kind="correction",
        concept=concept,
        observed_expression=observed_expression,
        candidate_expression=candidate_expression,
        source_role=source_role,
        confidence=confidence,
        context={} if context is None else dict(context),
        evidence_refs=evidence_refs,
    )
