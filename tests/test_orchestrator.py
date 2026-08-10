from velvet_language.context_strategy import StrategyContext
from velvet_language.conversation_state import ConversationState
from velvet_language.orchestrator import TurnInput, orchestrate_turn
from velvet_language.reference_resolution import ReferenceCandidate


def state(turn_count: int = 0) -> ConversationState:
    return ConversationState(conversation_id="test-conversation", turn_count=turn_count)


def test_request_requires_authority_without_granting_it():
    decision = orchestrate_turn(
        TurnInput(
            text="Can you open the window?",
            state=state(),
            context=StrategyContext(),
        )
    )
    assert decision.requires_authority_check is True
    assert decision.authority_granted is False


def test_reference_resolution_updates_ephemeral_state():
    decision = orchestrate_turn(
        TurnInput(
            text="What about it?",
            state=state(),
            context=StrategyContext(),
            reference_text="it",
            reference_candidates=(ReferenceCandidate("engine", "engine", 0.95),),
        )
    )
    assert decision.reference is not None
    assert decision.reference.resolved_id == "engine"
    assert "engine" in decision.state.recent_entities


def test_high_driving_load_can_reduce_speech():
    decision = orchestrate_turn(
        TurnInput(
            text="That was clever lol",
            state=state(),
            context=StrategyContext(driving_load="high"),
        )
    )
    assert decision.contextual_strategy.allow_humor is False


def test_turn_count_advances_without_creating_memory():
    decision = orchestrate_turn(
        TurnInput(text="The engine sounds rough", state=state(3), context=StrategyContext())
    )
    assert decision.state.turn_count == 4
    assert decision.authority_granted is False
