from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from .conversation_acts import ActInterpretation, ConversationAct


class ResponseStrategy(str, Enum):
    ANSWER = "answer"
    ACKNOWLEDGE = "acknowledge"
    CLARIFY = "clarify"
    COMPARE = "compare"
    CAPTURE_EXPERIENCE = "capture_experience"
    ADVANCE_GOAL = "advance_goal"
    REQUEST_AUTHORITY_CHECK = "request_authority_check"
    SOCIAL_REPLY = "social_reply"
    HOLD = "hold"


@dataclass(frozen=True)
class StrategyPlan:
    primary: ResponseStrategy
    secondary: Tuple[ResponseStrategy, ...] = ()
    create_language_experience: bool = False
    create_or_advance_goal: bool = False
    requires_authority_check: bool = False
    treat_as_fact: bool = True
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


def strategy_for_act(interpretation: ActInterpretation) -> StrategyPlan:
    """Map interpreted conversational acts to bounded next-step strategies.

    This layer plans language-side behavior only. It never grants runtime
    authority or executes a requested action.
    """

    act = interpretation.act
    secondary_acts = set(interpretation.secondary_acts)

    if act is ConversationAct.QUESTION:
        return StrategyPlan(
            primary=ResponseStrategy.ANSWER,
            secondary=(ResponseStrategy.ADVANCE_GOAL,),
            create_or_advance_goal=True,
            confidence=interpretation.confidence,
        )

    if act is ConversationAct.REQUEST:
        secondary = [ResponseStrategy.ADVANCE_GOAL]
        if interpretation.execution_requested:
            secondary.append(ResponseStrategy.REQUEST_AUTHORITY_CHECK)
        return StrategyPlan(
            primary=ResponseStrategy.ACKNOWLEDGE,
            secondary=tuple(secondary),
            create_or_advance_goal=True,
            requires_authority_check=interpretation.execution_requested,
            confidence=interpretation.confidence,
        )

    if act is ConversationAct.COMMAND_LIKE:
        return StrategyPlan(
            primary=ResponseStrategy.REQUEST_AUTHORITY_CHECK,
            secondary=(ResponseStrategy.ACKNOWLEDGE,),
            requires_authority_check=True,
            confidence=interpretation.confidence,
        )

    if act is ConversationAct.CORRECTION:
        return StrategyPlan(
            primary=ResponseStrategy.ACKNOWLEDGE,
            secondary=(ResponseStrategy.CAPTURE_EXPERIENCE,),
            create_language_experience=True,
            confidence=interpretation.confidence,
        )

    if act is ConversationAct.TEACHING:
        return StrategyPlan(
            primary=ResponseStrategy.ACKNOWLEDGE,
            secondary=(ResponseStrategy.CAPTURE_EXPERIENCE,),
            create_language_experience=True,
            confidence=interpretation.confidence,
        )

    if act is ConversationAct.DISAGREEMENT:
        return StrategyPlan(
            primary=ResponseStrategy.COMPARE,
            secondary=(ResponseStrategy.CLARIFY,),
            confidence=interpretation.confidence,
        )

    if act is ConversationAct.CONFIRMATION:
        return StrategyPlan(
            primary=ResponseStrategy.ACKNOWLEDGE,
            secondary=(ResponseStrategy.ADVANCE_GOAL,),
            create_or_advance_goal=True,
            confidence=interpretation.confidence,
        )

    if act is ConversationAct.JOKE:
        return StrategyPlan(
            primary=ResponseStrategy.SOCIAL_REPLY,
            treat_as_fact=False,
            confidence=interpretation.confidence,
        )

    if act is ConversationAct.OBSERVATION:
        if ConversationAct.JOKE in secondary_acts:
            return StrategyPlan(
                primary=ResponseStrategy.SOCIAL_REPLY,
                secondary=(ResponseStrategy.ACKNOWLEDGE,),
                treat_as_fact=False,
                confidence=interpretation.confidence,
            )
        return StrategyPlan(
            primary=ResponseStrategy.ACKNOWLEDGE,
            confidence=interpretation.confidence,
        )

    return StrategyPlan(
        primary=ResponseStrategy.HOLD,
        treat_as_fact=False,
        confidence=interpretation.confidence,
    )
