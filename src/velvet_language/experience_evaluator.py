from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

from .experience import LanguageExperience


@dataclass(frozen=True)
class LanguagePromotionCandidate:
    concept: str
    candidate_expression: str
    supporting_experience_ids: Tuple[str, ...]
    evidence_refs: Tuple[str, ...]
    support_count: int
    mean_confidence: float
    source_roles: Tuple[str, ...]
    status: str = "candidate_for_core_review"
    requires_core_learning_review: bool = True
    requires_external_promotion: bool = True
    change_applied: bool = False
    grants_authority: bool = False


def evaluate_experiences(
    experiences: Iterable[LanguageExperience],
    *,
    min_support: int = 2,
    min_mean_confidence: float = 0.75,
) -> Tuple[LanguagePromotionCandidate, ...]:
    """Aggregate compatible language experiences without applying changes.

    Grouping is intentionally strict: the concept and candidate expression must
    match exactly. This avoids silently collapsing similar-looking concepts or
    synonyms before governed Core learning has reviewed them.
    """

    groups: dict[tuple[str, str], list[LanguageExperience]] = {}

    for experience in experiences:
        candidate = (experience.candidate_expression or "").strip()
        if not candidate:
            continue
        key = (experience.concept.strip(), candidate)
        groups.setdefault(key, []).append(experience)

    candidates: list[LanguagePromotionCandidate] = []

    for (concept, candidate_expression), group in groups.items():
        if len(group) < min_support:
            continue

        mean_confidence = sum(item.confidence for item in group) / len(group)
        if mean_confidence < min_mean_confidence:
            continue

        experience_ids = tuple(sorted({item.experience_id for item in group}))
        evidence_refs = tuple(
            sorted({ref for item in group for ref in item.evidence_refs if ref})
        )
        source_roles = tuple(sorted({item.source_role for item in group if item.source_role}))

        candidates.append(
            LanguagePromotionCandidate(
                concept=concept,
                candidate_expression=candidate_expression,
                supporting_experience_ids=experience_ids,
                evidence_refs=evidence_refs,
                support_count=len(group),
                mean_confidence=mean_confidence,
                source_roles=source_roles,
            )
        )

    return tuple(sorted(candidates, key=lambda item: (item.concept, item.candidate_expression)))
