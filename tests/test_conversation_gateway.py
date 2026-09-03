import pytest

from velvet_language.context_strategy import StrategyContext
from velvet_language.conversation_gateway import (
    CONVERSATION_TURN_EVENT,
    MAX_TURN_CHARACTERS,
    ConversationGateway,
    ConversationModality,
)


def test_written_question_uses_shared_turn_path_and_truthful_baseline():
    gateway = ConversationGateway(conversation_id="written-test")

    exchange = gateway.submit("What is the cabin temperature?")

    assert exchange.request.conversation_id == "written-test"
    assert exchange.request.turn_number == 1
    assert exchange.request.modality is ConversationModality.TEXT
    assert exchange.request.act.value == "question"
    assert exchange.reply.display is True
    assert exchange.reply.speak is False
    assert "verified information" in exchange.reply.text
    assert exchange.state.turn_count == 1


def test_speech_transcript_and_text_share_the_same_conversation_contract():
    gateway = ConversationGateway(conversation_id="shared-test")

    written = gateway.submit("The engine sounds rough")
    spoken = gateway.submit(
        "The engine sounds rough",
        modality=ConversationModality.SPEECH_TRANSCRIPT,
    )

    assert written.request.act == spoken.request.act
    assert written.request.strategy == spoken.request.strategy
    assert written.reply.speak is False
    assert spoken.reply.speak is True
    assert spoken.request.turn_number == 2


def test_action_like_request_requires_authority_without_granting_it():
    gateway = ConversationGateway(conversation_id="authority-test")

    exchange = gateway.submit("Open the window")
    event = exchange.request.to_event()

    assert exchange.request.requires_authority_check is True
    assert exchange.request.authority_granted is False
    assert exchange.reply.authority_granted is False
    assert event["event"] == CONVERSATION_TURN_EVENT
    assert event["requires_authority_check"] is True
    assert event["authority_granted"] is False
    assert "Runtime" in exchange.reply.text


def test_context_can_suppress_spoken_humor_without_hiding_written_reply():
    gateway = ConversationGateway(conversation_id="context-test")

    exchange = gateway.submit(
        "That was clever lol",
        modality=ConversationModality.SPEECH_TRANSCRIPT,
        context=StrategyContext(driving_load="high"),
    )

    assert exchange.reply.display is True
    assert exchange.reply.speak is False


def test_correction_and_teaching_do_not_claim_canonical_memory():
    gateway = ConversationGateway(conversation_id="learning-test")

    correction = gateway.submit("Actually, call that the cabin node")
    teaching = gateway.submit("Remember the phrase cabin node")

    assert "correction evidence" in correction.reply.text
    assert "permanent memory" in correction.reply.text
    assert "learning evidence" in teaching.reply.text
    assert "governed review" in teaching.reply.text


def test_empty_and_oversized_turns_fail_closed():
    gateway = ConversationGateway(conversation_id="bounds-test")

    with pytest.raises(ValueError, match="must not be empty"):
        gateway.submit("   ")

    with pytest.raises(ValueError, match=str(MAX_TURN_CHARACTERS)):
        gateway.submit("x" * (MAX_TURN_CHARACTERS + 1))
