from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import MeaningPacket


@dataclass(frozen=True)
class ConversationPlan:
    goal: str
    should_speak: bool
    should_display: bool
    should_interrupt: bool
    desired_length: str
    clarification_needed: bool = False
    rationale_code: str = "policy.default"


def plan_response(
    meaning: MeaningPacket,
    *,
    user_is_speaking: bool = False,
    duplicate_recent_event: bool = False,
    explicit_user_query: bool = False,
    ambiguity: bool = False,
) -> ConversationPlan:
    """Plan whether and how Velvet should communicate.

    The planner does not create facts or prose. It only establishes the
    communication goal and constraints that later language stages must obey.
    """
    severity = meaning.severity.lower()

    if severity == "emergency":
        return ConversationPlan(
            goal="communicate_emergency_state",
            should_speak=True,
            should_display=True,
            should_interrupt=True,
            desired_length="minimal",
            rationale_code="severity.emergency",
        )

    if severity == "critical":
        return ConversationPlan(
            goal="communicate_critical_state",
            should_speak=True,
            should_display=True,
            should_interrupt=True,
            desired_length="minimal",
            rationale_code="severity.critical",
        )

    if ambiguity and explicit_user_query:
        return ConversationPlan(
            goal="clarify_user_intent",
            should_speak=True,
            should_display=True,
            should_interrupt=False,
            desired_length="short",
            clarification_needed=True,
            rationale_code="intent.ambiguous",
        )

    if duplicate_recent_event and not explicit_user_query:
        return ConversationPlan(
            goal="avoid_redundant_notification",
            should_speak=False,
            should_display=False,
            should_interrupt=False,
            desired_length="none",
            rationale_code="restraint.duplicate",
        )

    if severity == "warning":
        return ConversationPlan(
            goal="communicate_warning_state",
            should_speak=not user_is_speaking,
            should_display=True,
            should_interrupt=False,
            desired_length="short",
            rationale_code="severity.warning",
        )

    if explicit_user_query:
        return ConversationPlan(
            goal="answer_user",
            should_speak=True,
            should_display=True,
            should_interrupt=False,
            desired_length="normal",
            rationale_code="turn.explicit_query",
        )

    return ConversationPlan(
        goal="inform_when_useful",
        should_speak=False,
        should_display=False,
        should_interrupt=False,
        desired_length="short",
        rationale_code="restraint.default_silence",
    )
