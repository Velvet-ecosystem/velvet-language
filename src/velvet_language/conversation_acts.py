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
    secondary_acts: Tuple[ConversationAct, ...] = ()
    authority_granted: bool = False
    execution_requested: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if self.authority_granted:
            raise ValueError("conversation-act interpretation cannot grant authority")


def interpret_conversation_act(text: str) -> ActInterpretation:
    """Bounded first-pass interpretation of what a human turn is doing.

    Informational phrasing such as ``Can you tell me the temperature?`` is a
    question, not an execution request. Practical requests such as ``Can you
    open the window?`` remain authority-gated. Classification never grants
    authority.
    """

    raw = text.strip()
    lower = raw.lower()
    if not raw:
        return ActInterpretation(ConversationAct.UNKNOWN, 0.0)

    evidence: list[str] = []

    informational_starts = (
        "can you tell me ",
        "could you tell me ",
        "would you tell me ",
        "please tell me ",
        "tell me ",
        "can you explain ",
        "could you explain ",
        "would you explain ",
        "please explain ",
        "explain ",
    )
    if lower.startswith(informational_starts):
        evidence.extend(("informational_request", "question_form"))
        return ActInterpretation(
            ConversationAct.QUESTION,
            0.9,
            tuple(evidence),
            execution_requested=False,
        )

    request_starts = (
        "please ",
        "could you ",
        "can you ",
        "would you ",
        "i'd like ",
        "i would like ",
    )
    if lower.startswith(request_starts):
        evidence.append("request_marker")
        secondary: list[ConversationAct] = []
        if raw.endswith("?") or lower.startswith(("could you ", "can you ", "would you ")):
            evidence.append("question_form")
            secondary.append(ConversationAct.QUESTION)
        return ActInterpretation(
            ConversationAct.REQUEST,
            0.88,
            tuple(evidence),
            tuple(secondary),
            execution_requested=True,
        )

    if lower.startswith(("no, ", "no ", "actually,", "actually ", "i mean ", "that's not ", "that is not ", "you mean ")):
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

    question_starts = (
        "what ", "what's ", "whats ", "why ", "how ", "when ", "where ", "who ",
        "is ", "are ", "do ", "does ", "did ", "has ", "have ", "was ", "were ",
    )
    if raw.endswith("?") or lower.startswith(question_starts):
        evidence.append("question_form")
        return ActInterpretation(ConversationAct.QUESTION, 0.9, tuple(evidence))

    if any(token in lower for token in ("lol", "haha", "😆", "😂")):
        evidence.append("humor_marker")
        return ActInterpretation(ConversationAct.JOKE, 0.75, tuple(evidence))

    evidence.append("default_statement")
    return ActInterpretation(ConversationAct.OBSERVATION, 0.55, tuple(evidence))
