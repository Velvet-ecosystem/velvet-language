from velvet_language.context_strategy import StrategyContext
from velvet_language.conversation_state import ConversationState
from velvet_language.orchestrator import TurnInput, orchestrate_turn
from velvet_language.reference_resolution import ReferenceCandidate


def test_request_requires_authority_without_granting_it():
    decision = orchestrate_turn(
        TurnInput(
            text="Can you open the window?",
            state=ConversationState(),
            context=StrategyContext(),
        )
    )
    assert decision.requires_authority_check is True
    assert decision.authority_granted is False


def test_reference_resolution_updates_ephemeral_state():
    decision = orchestrate_turn(
        TurnInput(
            text="What about it?",
            state=ConversationState(),
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
            state=ConversationState(),
            context=StrategyContext(driving_load="high"),
        )
    )
    assert decision.contextual_strategy.allow_humor is False


def test_turn_count_advances_without_creating_memory():
    state = ConversationState(turn_count=3)
    decision = orchestrate_turn(TurnInput(text="The engine sounds rough", state=state, context=StrategyContext()))
    assert decision.state.turn_count == 4
    assert decision.authority_granted is False
