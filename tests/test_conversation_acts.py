from velvet_language.conversation_acts import ConversationAct, interpret_conversation_act


def test_question_detected():
    result = interpret_conversation_act("What is the CAN doing?")
    assert result.act is ConversationAct.QUESTION
    assert result.confidence >= 0.8
    assert result.authority_granted is False


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
