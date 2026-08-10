from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ReferenceCandidate:
    entity_id: str
    label: str
    recency_rank: int
    semantic_match: float
    role_match: float = 0.0

    def score(self) -> float:
        recency_bonus = max(0.0, 1.0 - (self.recency_rank * 0.1))
        return (0.5 * self.semantic_match) + (0.3 * recency_bonus) + (0.2 * self.role_match)


@dataclass(frozen=True)
class ReferenceResolution:
    phrase: str
    resolved_entity_id: str | None
    confidence: float
    ambiguous: bool
    requires_clarification: bool
    candidate_ids: tuple[str, ...]


def resolve_reference(
    phrase: str,
    candidates: Sequence[ReferenceCandidate],
    *,
    minimum_confidence: float = 0.62,
    ambiguity_margin: float = 0.08,
) -> ReferenceResolution:
    """Resolve a conversational reference without inventing a referent.

    The resolver consumes only caller-supplied candidates. If the best match is
    weak or too close to the runner-up, it requests clarification instead of
    choosing silently.
    """

    ranked = sorted(candidates, key=lambda c: c.score(), reverse=True)
    ids = tuple(c.entity_id for c in ranked)

    if not ranked:
        return ReferenceResolution(
            phrase=phrase,
            resolved_entity_id=None,
            confidence=0.0,
            ambiguous=False,
            requires_clarification=True,
            candidate_ids=(),
        )

    best = ranked[0]
    best_score = best.score()
    second_score = ranked[1].score() if len(ranked) > 1 else 0.0
    ambiguous = len(ranked) > 1 and (best_score - second_score) < ambiguity_margin
    weak = best_score < minimum_confidence

    return ReferenceResolution(
        phrase=phrase,
        resolved_entity_id=None if (ambiguous or weak) else best.entity_id,
        confidence=best_score,
        ambiguous=ambiguous,
        requires_clarification=ambiguous or weak,
        candidate_ids=ids,
    )
