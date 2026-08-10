from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

from .context_strategy import ContextStrategy, StrategyContext, apply_context_strategy
from .conversation_acts import ActInterpretation, interpret_conversation_act
from .conversation_state import ConversationState
from .goals import ConversationGoal
from .reference_resolution import ReferenceCandidate, ReferenceResolution, resolve_reference
from .response_strategy import StrategyPlan, strategy_for_act


@dataclass(frozen=True)
class TurnInput:
    text: str
    state: ConversationState
    context: StrategyContext
    reference_candidates: Tuple[ReferenceCandidate, ...] = ()
    reference_text: str | None = None
    goal: ConversationGoal | None = None


@dataclass(frozen=True)
class TurnDecision:
    act: ActInterpretation
    strategy: StrategyPlan
    contextual_strategy: ContextStrategy
    reference: ReferenceResolution | None
    state: ConversationState
    goal: ConversationGoal | None
    requires_authority_check: bool
    may_speak: bool
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("language turn orchestration cannot grant authority")


def orchestrate_turn(turn: TurnInput) -> TurnDecision:
    """Run a bounded language-side conversation turn pipeline.

    The orchestrator composes existing language modules. It does not perform
    memory admission, Core learning, Runtime authority checks, actuation, or
    audio playback.
    """

    act = interpret_conversation_act(turn.text)
    strategy = strategy_for_act(act)
    contextual = apply_context_strategy(strategy, turn.context)

    reference = None
    if turn.reference_text and turn.reference_candidates:
        reference = resolve_reference(turn.reference_text, turn.reference_candidates)

    next_state = turn.state.next_turn()
    if reference is not None and reference.resolved_id:
        next_state = next_state.with_entity(reference.resolved_id)

    requires_authority = strategy.requires_authority_check or act.execution_requested

    return TurnDecision(
        act=act,
        strategy=strategy,
        contextual_strategy=contextual,
        reference=reference,
        state=next_state,
        goal=turn.goal,
        requires_authority_check=requires_authority,
        may_speak=contextual.may_speak,
    )
