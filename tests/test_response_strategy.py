from velvet_language.conversation_acts import ConversationAct, ActInterpretation
from velvet_language.response_strategy import ResponseStrategy, strategy_for_act


def test_question_advances_goal():
    plan = strategy_for_act(ActInterpretation(ConversationAct.QUESTION, 0.9))
    assert plan.primary is ResponseStrategy.ANSWER
    assert plan.create_or_advance_goal is True


def test_correction_creates_language_experience():
    plan = strategy_for_act(ActInterpretation(ConversationAct.CORRECTION, 0.85))
    assert plan.create_language_experience is True
    assert ResponseStrategy.CAPTURE_EXPERIENCE in plan.secondary


def test_teaching_creates_language_experience():
    plan = strategy_for_act(ActInterpretation(ConversationAct.TEACHING, 0.85))
    assert plan.create_language_experience is True


def test_disagreement_opens_comparison():
    plan = strategy_for_act(ActInterpretation(ConversationAct.DISAGREEMENT, 0.8))
    assert plan.primary is ResponseStrategy.COMPARE


def test_joke_is_not_fact():
    plan = strategy_for_act(ActInterpretation(ConversationAct.JOKE, 0.8))
    assert plan.treat_as_fact is False


def test_command_like_requires_authority_check():
    plan = strategy_for_act(
        ActInterpretation(
            ConversationAct.COMMAND_LIKE,
            0.8,
            execution_requested=True,
        )
    )
    assert plan.primary is ResponseStrategy.REQUEST_AUTHORITY_CHECK
    assert plan.requires_authority_check is True


def test_request_with_execution_requires_authority_check():
    plan = strategy_for_act(
        ActInterpretation(
            ConversationAct.REQUEST,
            0.8,
            secondary_acts=(ConversationAct.QUESTION,),
            execution_requested=True,
        )
    )
    assert plan.requires_authority_check is True
    assert plan.create_or_advance_goal is True
