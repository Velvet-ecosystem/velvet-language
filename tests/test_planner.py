from velvet_language.models import MeaningPacket
from velvet_language.planner import plan_response


def test_duplicate_noncritical_event_stays_quiet():
    meaning = MeaningPacket(event="door.open", severity="informational")
    plan = plan_response(meaning, duplicate_recent_event=True)

    assert plan.should_speak is False
    assert plan.rationale_code == "restraint.duplicate"


def test_warning_does_not_talk_over_user_by_default():
    meaning = MeaningPacket(event="can.connection_lost", severity="warning")
    plan = plan_response(meaning, user_is_speaking=True)

    assert plan.should_speak is False
    assert plan.should_display is True
    assert plan.should_interrupt is False


def test_critical_state_interrupts():
    meaning = MeaningPacket(event="brake.control_lost", severity="critical")
    plan = plan_response(meaning, user_is_speaking=True)

    assert plan.should_speak is True
    assert plan.should_interrupt is True
    assert plan.desired_length == "minimal"


def test_ambiguous_direct_question_requests_clarification():
    meaning = MeaningPacket(event="conversation.query", severity="informational")
    plan = plan_response(meaning, explicit_user_query=True, ambiguity=True)

    assert plan.clarification_needed is True
    assert plan.goal == "clarify_user_intent"
