from velvet_language.conversation_acts import ConversationAct, interpret_conversation_act


def test_question_detected():
    result = interpret_conversation_act("What is the CAN doing?")
    assert result.act is ConversationAct.QUESTION
    assert result.confidence >= 0.8
    assert result.authority_granted is False


def test_informational_polite_request_is_question_not_execution():
    for text in (
        "Can you tell me the cabin temperature?",
        "Could you tell me the vehicle voltage",
        "Please tell me the outside temperature",
        "Tell me the cabin humidity",
        "Can you explain the ignition state?",
    ):
        result = interpret_conversation_act(text)
        assert result.act is ConversationAct.QUESTION
        assert result.execution_requested is False
        assert "informational_request" in result.evidence
        assert result.authority_granted is False


def test_practical_polite_request_still_requires_execution_path():
    result = interpret_conversation_act("Can you open the window?")
    assert result.act is ConversationAct.REQUEST
    assert ConversationAct.QUESTION in result.secondary_acts
    assert result.execution_requested is True
    assert result.authority_granted is False


def test_copula_question_without_question_mark_is_still_question():
    result = interpret_conversation_act("Is the ignition on")
    assert result.act is ConversationAct.QUESTION
    assert result.execution_requested is False


def test_correction_detected():
    result = interpret_conversation_act("Actually, I'd call that sputtering")
    assert result.act is ConversationAct.CORRECTION
    assert "correction_marker" in result.evidence


def test_teaching_detected():
    result = interpret_conversation_act("From now on call that sputtering")
    assert result.act is ConversationAct.TEACHING
    assert result.authority_granted is False


def test_command_like_does_not_grant_authority():
    result = interpret_conversation_act("Unlock the doors")
    assert result.act is ConversationAct.COMMAND_LIKE
    assert result.execution_requested is True
    assert result.authority_granted is False


def test_humor_detected():
    result = interpret_conversation_act("That was clever lol")
    assert result.act is ConversationAct.JOKE


def test_plain_statement_defaults_to_observation():
    result = interpret_conversation_act("The engine sounds rough")
    assert result.act is ConversationAct.OBSERVATION
