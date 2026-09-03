"""Surface-neutral conversation ingress for Velvet Language.

This module provides the missing written/spoken turn seam without acquiring
Runtime authority, canonical memory, or audio ownership. Typed text and speech
transcripts enter the same conversation session and produce the same bounded
turn contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping, Optional
from uuid import uuid4

from .context_strategy import StrategyContext
from .conversation_acts import ConversationAct
from .conversation_state import ConversationState
from .fallback import render_fallback
from .grounded_conversation import GroundedResponseKind, realize_core_conversation_meaning
from .orchestrator import TurnDecision, TurnInput, orchestrate_turn
from .response_strategy import ResponseStrategy

MAX_TURN_CHARACTERS = 4096
CONVERSATION_TURN_EVENT = "velvet.language.conversation.turn"
CONVERSATION_TURN_SCHEMA_VERSION = "0.1"

GroundedMeaningResolver = Callable[
    [Mapping[str, object]],
    Mapping[str, object],
]


class ConversationModality(str, Enum):
    """Human-input modality feeding the shared conversation path."""

    TEXT = "text"
    SPEECH_TRANSCRIPT = "speech_transcript"


@dataclass(frozen=True)
class ConversationRequest:
    """Normalized user turn ready for Core/Runtime integration.

    This is a request/observation contract only. It can report that an
    authority check is required, but it can never grant authority itself.
    """

    conversation_id: str
    turn_number: int
    text: str
    modality: ConversationModality
    audience: str
    act: ConversationAct
    strategy: ResponseStrategy
    requires_authority_check: bool
    may_speak: bool
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("conversation request cannot grant authority")

    @property
    def turn_id(self) -> str:
        return f"{self.conversation_id}:{self.turn_number}"

    def to_event(self) -> Mapping[str, object]:
        """Serialize the turn for a future local Velvet Gateway or event bus."""

        return {
            "event": CONVERSATION_TURN_EVENT,
            "schema_version": CONVERSATION_TURN_SCHEMA_VERSION,
            "conversation_id": self.conversation_id,
            "turn_id": self.turn_id,
            "turn_number": self.turn_number,
            "text": self.text,
            "modality": self.modality.value,
            "audience": self.audience,
            "act": self.act.value,
            "strategy": self.strategy.value,
            "requires_authority_check": self.requires_authority_check,
            "may_speak": self.may_speak,
            "authority_granted": False,
        }


@dataclass(frozen=True)
class ConversationReply:
    """Bounded baseline reply for a human-facing conversation surface."""

    conversation_id: str
    turn_number: int
    text: str
    display: bool
    speak: bool
    generator: str = "deterministic-conversation-baseline"
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("conversation reply cannot grant authority")

    @property
    def turn_id(self) -> str:
        return f"{self.conversation_id}:{self.turn_number}"


@dataclass(frozen=True)
class ConversationExchange:
    """One complete local turn: normalized request, baseline reply, new state."""

    request: ConversationRequest
    reply: ConversationReply
    state: ConversationState


def _baseline_reply(decision: TurnDecision) -> str:
    """Return truthful deterministic language when no richer responder is bound."""

    if decision.contextual_strategy.require_clarification:
        return "I need a little more verified context before I answer that."

    act = decision.act.act

    if act is ConversationAct.QUESTION:
        return render_fallback(
            {"severity": "casual", "event": "conversation.question"}
        ).text

    if act in {ConversationAct.REQUEST, ConversationAct.COMMAND_LIKE}:
        if decision.requires_authority_check:
            return (
                "I understand the request. If it would cause an action, "
                "Runtime still has to authorize it."
            )
        return "I understand the request."

    if act is ConversationAct.CORRECTION:
        return (
            "Understood. I'll treat that as correction evidence, not silent "
            "permanent memory."
        )

    if act is ConversationAct.TEACHING:
        return (
            "Understood. I'll treat that as learning evidence for governed review."
        )

    if act is ConversationAct.DISAGREEMENT:
        return (
            "I understand. I need the competing verified information before I "
            "compare it."
        )

    if act is ConversationAct.CONFIRMATION:
        return "Understood."

    if act is ConversationAct.JOKE:
        return "I caught that."

    if act is ConversationAct.OBSERVATION:
        return "I heard you."

    return "I couldn't interpret that turn reliably."


class ConversationGateway:
    """Manage one ephemeral conversation session across text or speech input."""

    def __init__(
        self,
        conversation_id: Optional[str] = None,
        context: Optional[StrategyContext] = None,
        meaning_resolver: Optional[GroundedMeaningResolver] = None,
    ) -> None:
        resolved_id = (conversation_id or f"conversation-{uuid4().hex}").strip()
        if not resolved_id:
            raise ValueError("conversation_id must not be empty")
        self._state = ConversationState(conversation_id=resolved_id)
        self._context = context or StrategyContext()
        self._meaning_resolver = meaning_resolver

    @property
    def state(self) -> ConversationState:
        return self._state

    def submit(
        self,
        text: str,
        *,
        modality: ConversationModality = ConversationModality.TEXT,
        context: Optional[StrategyContext] = None,
    ) -> ConversationExchange:
        """Submit one human turn through the shared Language conversation path."""

        if not isinstance(text, str):
            raise TypeError("conversation text must be a string")

        normalized = text.strip()
        if not normalized:
            raise ValueError("conversation text must not be empty")
        if len(normalized) > MAX_TURN_CHARACTERS:
            raise ValueError(
                f"conversation text must be <= {MAX_TURN_CHARACTERS} characters"
            )

        strategy_context = context or self._context
        decision = orchestrate_turn(
            TurnInput(
                text=normalized,
                state=self._state,
                context=strategy_context,
            )
        )
        self._state = decision.state

        request = ConversationRequest(
            conversation_id=self._state.conversation_id,
            turn_number=self._state.turn_count,
            text=normalized,
            modality=modality,
            audience=strategy_context.audience,
            act=decision.act.act,
            strategy=decision.strategy.primary,
            requires_authority_check=decision.requires_authority_check,
            may_speak=decision.may_speak,
        )

        reply_text = _baseline_reply(decision)
        generator = "deterministic-conversation-baseline"

        if self._meaning_resolver is not None:
            meaning_event = self._meaning_resolver(request.to_event())
            expression = realize_core_conversation_meaning(meaning_event)
            if expression.conversation_id != request.conversation_id:
                raise ValueError("Core meaning conversation_id does not match request")
            if expression.turn_id != request.turn_id:
                raise ValueError("Core meaning turn_id does not match request")
            if expression.turn_number != request.turn_number:
                raise ValueError("Core meaning turn_number does not match request")

            if not (
                expression.response_kind is GroundedResponseKind.UNAVAILABLE
                and request.requires_authority_check
            ):
                reply_text = expression.text
                generator = expression.generator

        reply = ConversationReply(
            conversation_id=request.conversation_id,
            turn_number=request.turn_number,
            text=reply_text,
            display=True,
            speak=(
                modality is ConversationModality.SPEECH_TRANSCRIPT
                and decision.may_speak
            ),
            generator=generator,
        )

        return ConversationExchange(
            request=request,
            reply=reply,
            state=self._state,
        )
