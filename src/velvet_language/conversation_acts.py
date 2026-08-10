from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class ConversationAct(str, Enum):
    QUESTION = "question"
    CORRECTION = "correction"
    OBSERVATION = "observation"
    CONFIRMATION = "confirmation"
    DISAGREEMENT = "disagreement"
    REQUEST = "request"
    TEACHING = "teaching"
    JOKE = "joke"
    COMMAND_LIKE = "command_like"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ActInterpretation:
    act: ConversationAct
    confidence: float
    evidence: Tuple[str, ...] = ()
    authority_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.authority_granted:
            raise ValueError("conversation-act interpretation cannot grant authority")


def interpret_conversation_act(text: str) -> ActInterpretation:
    """Bounded first-pass interpretation of what a human turn is doing.

    This is intentionally conservative and language-surface only. It does not
    authorize actions, infer hidden permissions, or bypass Runtime/Court.
    """

    raw = text.strip()
    lower = raw.lower()
    if not raw:
        return ActInterpretation(ConversationAct.UNKNOWN, 0.0)

    evidence: list[str] = []

    if raw.endswith("?") or lower.startswith(("what ", "why ", "how ", "when ", "where ", "who ", "can you ", "could you ", "would you ")):
        evidence.append("question_form")
        return ActInterpretation(ConversationAct.QUESTION, 0.9, tuple(evidence))

    if lower.startswith(("no, ", "no ", "actually ", "i mean ", "that's not ", "that is not ", "you mean ")):
        evidence.append("correction_marker")
        return ActInterpretation(ConversationAct.CORRECTION, 0.82, tuple(evidence))

    if lower in {"yes", "yep", "yeah", "correct", "exactly", "right", "that's right", "that is right"}:
        evidence.append("confirmation_marker")
        return ActInterpretation(ConversationAct.CONFIRMATION, 0.9, tuple(evidence))

    if lower.startswith(("i disagree", "nope", "not really", "i don't think", "i do not think")):
        evidence.append("disagreement_marker")
        return ActInterpretation(ConversationAct.DISAGREEMENT, 0.86, tuple(evidence))

    if lower.startswith(("remember ", "learn ", "call that ", "we call ", "i call ", "from now on ", "the word for ")):
        evidence.append("teaching_marker")
        return ActInterpretation(ConversationAct.TEACHING, 0.82, tuple(evidence))

    if lower.startswith(("please ", "could you ", "can you ", "would you ", "i'd like ", "i would like ")):
        evidence.append("request_marker")
        return ActInterpretation(ConversationAct.REQUEST, 0.8, tuple(evidence))

    imperative_starts = (
        "open ", "close ", "start ", "stop ", "turn ", "set ", "move ",
        "send ", "delete ", "create ", "run ", "shut ", "unlock ", "lock ",
    )
    if lower.startswith(imperative_starts):
        evidence.append("imperative_surface")
        return ActInterpretation(
            ConversationAct.COMMAND_LIKE,
            0.78,
            tuple(evidence),
            execution_requested=True,
        )

    if any(token in lower for token in ("lol", "haha", "😆", "😂")):
        evidence.append("humor_marker")
        return ActInterpretation(ConversationAct.JOKE, 0.75, tuple(evidence))

    evidence.append("default_statement")
    return ActInterpretation(ConversationAct.OBSERVATION, 0.55, tuple(evidence))
