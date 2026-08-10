from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .conversation_acts import ActInterpretation, ConversationAct
from .response_strategy import ResponseStrategy, strategy_for_act


@dataclass(frozen=True)
class StrategyContext:
    audience: str = "owner"
    driving_load: str = "low"
    emergency: bool = False
    degraded: bool = False
    confidence: float = 1.0
    repeated_recently: bool = False
    guest_present: bool = False
    active_goal: bool = False


@dataclass(frozen=True)
class ContextualStrategy:
    base: ResponseStrategy
    brevity: str
    allow_humor: bool
    may_interrupt: bool
    should_speak: bool
    require_clarification: bool
    notes: Tuple[str, ...] = ()
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("language strategy cannot grant authority")


def contextualize_strategy(
    interpretation: ActInterpretation,
    context: StrategyContext,
) -> ContextualStrategy:
    base = strategy_for_act(interpretation)
    notes: list[str] = []
    brevity = "normal"
    allow_humor = interpretation.act is ConversationAct.JOKE
    may_interrupt = False
    should_speak = True
    require_clarification = False

    if context.emergency:
        brevity = "minimal"
        allow_humor = False
        may_interrupt = True
        notes.append("emergency_context")
    elif context.driving_load == "high":
        brevity = "short"
        allow_humor = False
        notes.append("high_driving_load")
    elif context.driving_load == "medium":
        brevity = "short"
        notes.append("medium_driving_load")

    if context.degraded:
        notes.append("degraded_context")
        allow_humor = False

    if context.guest_present and context.audience == "owner":
        notes.append("guest_present")

    if context.confidence < 0.55:
        require_clarification = True
        notes.append("low_confidence")

    if context.repeated_recently and interpretation.act in {
        ConversationAct.OBSERVATION,
        ConversationAct.CONFIRMATION,
        ConversationAct.JOKE,
    }:
        should_speak = False
        notes.append("recent_repeat_suppressed")

    if interpretation.act in {ConversationAct.COMMAND_LIKE, ConversationAct.REQUEST}:
        notes.append("authority_check_required")

    if interpretation.act is ConversationAct.JOKE and (context.emergency or context.driving_load == "high"):
        should_speak = False
        notes.append("humor_suppressed")

    if interpretation.act is ConversationAct.QUESTION and context.active_goal:
        notes.append("advance_active_goal")

    return ContextualStrategy(
        base=base,
        brevity=brevity,
        allow_humor=allow_humor,
        may_interrupt=may_interrupt,
        should_speak=should_speak,
        require_clarification=require_clarification,
        notes=tuple(notes),
    )
