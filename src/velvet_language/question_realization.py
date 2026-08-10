from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class QuestionCandidateInput:
    """Language-side view of an upstream-approved question candidate.

    Curiosity, Presence, or another trusted upstream owner decides whether a
    question is appropriate. Language only realizes approved wording.
    """

    candidate_text: str
    speech_approved: bool = False
    audience: str = "owner"
    interrupt_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_text.strip():
            raise ValueError("candidate_text is required")


@dataclass(frozen=True)
class QuestionExpression:
    text: Optional[str]
    suppressed: bool
    reason: str
    interrupt: bool = False
    authority: str = "none"

    def __post_init__(self) -> None:
        if self.authority != "none":
            raise ValueError("question realization cannot carry authority")
        if self.suppressed and self.text is not None:
            raise ValueError("suppressed question expressions cannot contain text")


def realize_question(candidate: QuestionCandidateInput) -> QuestionExpression:
    """Realize a question only after an upstream speech decision exists."""

    if not candidate.speech_approved:
        return QuestionExpression(
            text=None,
            suppressed=True,
            reason="question candidate has not been approved for speech",
        )

    text = candidate.candidate_text.strip()
    if candidate.audience == "owner" and not text.lower().startswith("mister"):
        text = "Mister, " + text[0].lower() + text[1:]

    return QuestionExpression(
        text=text,
        suppressed=False,
        reason="upstream-approved question realized",
        interrupt=candidate.interrupt_allowed,
    )
