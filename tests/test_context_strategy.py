from velvet_language.context_strategy import StrategyContext, contextualize_strategy
from velvet_language.conversation_acts import interpret_conversation_act


def test_high_driving_load_shortens_response_and_disables_humor():
    act = interpret_conversation_act("That was clever lol")
    result = contextualize_strategy(act, StrategyContext(driving_load="high"))
    assert result.brevity == "short"
    assert result.allow_humor is False
    assert result.should_speak is False
    assert "humor_suppressed" in result.notes


def test_emergency_allows_interrupt_and_minimal_language():
    act = interpret_conversation_act("What happened?")
    result = contextualize_strategy(act, StrategyContext(emergency=True))
    assert result.brevity == "minimal"
    assert result.may_interrupt is True
    assert result.allow_humor is False


def test_low_confidence_requires_clarification():
    act = interpret_conversation_act("What about it?")
    result = contextualize_strategy(act, StrategyContext(confidence=0.4))
    assert result.require_clarification is True
    assert "low_confidence" in result.notes


def test_repeated_observation_can_be_silent():
    act = interpret_conversation_act("The engine sounds rough")
    result = contextualize_strategy(act, StrategyContext(repeated_recently=True))
    assert result.should_speak is False


def test_request_marks_authority_check_without_granting_authority():
    act = interpret_conversation_act("Can you open the window?")
    result = contextualize_strategy(act, StrategyContext())
    assert "authority_check_required" in result.notes
    assert result.authority_granted is False
