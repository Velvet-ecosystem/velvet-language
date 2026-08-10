from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class LexicalRegister(str, Enum):
    TECHNICAL = "technical"
    COMMON = "common"
    OWNER = "owner"


@dataclass(frozen=True)
class LexicalConcept:
    """Language-owned names for an externally defined concept.

    This object stores terminology only. It does not define causal, physical,
    diagnostic, or authority relationships for the concept.
    """

    concept_id: str
    technical_term: str
    common_term: str
    owner_preferred_term: Optional[str] = None
    synonyms: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.concept_id.strip():
            raise ValueError("concept_id is required")
        if not self.technical_term.strip() or not self.common_term.strip():
            raise ValueError("technical_term and common_term are required")
        if self.owner_preferred_term is not None and not self.owner_preferred_term.strip():
            raise ValueError("owner_preferred_term cannot be blank")
        if any(not synonym.strip() for synonym in self.synonyms):
            raise ValueError("synonyms cannot be blank")

    def term_for(self, register: LexicalRegister) -> str:
        if register is LexicalRegister.TECHNICAL:
            return self.technical_term
        if register is LexicalRegister.OWNER and self.owner_preferred_term:
            return self.owner_preferred_term
        return self.common_term

    def recognizes(self, term: str) -> bool:
        normalized = " ".join(term.strip().lower().split())
        candidates = {
            " ".join(self.technical_term.lower().split()),
            " ".join(self.common_term.lower().split()),
        }
        if self.owner_preferred_term:
            candidates.add(" ".join(self.owner_preferred_term.lower().split()))
        candidates.update(" ".join(value.lower().split()) for value in self.synonyms)
        return normalized in candidates
