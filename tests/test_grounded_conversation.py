import pytest

from velvet_language import (
    ConversationGateway,
    ConversationModality,
    GroundedResponseKind,
    core_conversation_meaning_from_event,
    realize_core_conversation_meaning,
)


def core_event(**overrides):
    event = {
        "event": "velvet.core.conversation.meaning",
        "schema_version": "0.1",
        "conversation_id": "bench-chat",
        "turn_id": "bench-chat:1",
        "turn_number": 1,
        "response_kind": "fact",
        "fact_id": "cabin.temperature",
        "value": 21.5,
        "unit": "C",
        "confidence": 0.99,
        "qualifiers": ["fresh"],
        "source_refs": ["body-state:cabin-temp"],
        "requires_authority_check": False,
        "authority": "none",
        "grants_authority": False,
        "grants_execution": False,
        "grants_actuation": False,
    }
    event.update(overrides)
    return event


def event_for_request(request, **overrides):
    event = core_event(
        conversation_id=request["conversation_id"],
        turn_id=request["turn_id"],
        turn_number=request["turn_number"],
        requires_authority_check=request["requires_authority_check"],
    )
    event.update(overrides)
    return event


def test_fact_meaning_is_realized_by_language_not_core():
    expression = realize_core_conversation_meaning(core_event())

    assert expression.text == "Cabin temperature is 21.5 °C."
    assert expression.response_kind is GroundedResponseKind.FACT
    assert expression.source_refs == ("body-state:cabin-temp",)
    assert expression.authority_granted is False


def test_stale_and_lower_confidence_are_expressed_explicitly():
    expression = realize_core_conversation_meaning(
        core_event(confidence=0.7, qualifiers=["stale"])
    )

    assert expression.text.startswith("Last known: Based on the verified context")


def test_unavailable_meaning_stays_truthful():
    expression = realize_core_conversation_meaning(
        core_event(
            response_kind="unavailable",
            fact_id=None,
            value=None,
            unit=None,
            confidence=0.0,
            source_refs=[],
            qualifiers=["no-grounded-resolver"],
        )
    )

    assert expression.text == "I don't have enough verified information to answer that yet."


def test_core_meaning_cannot_smuggle_authority():
    with pytest.raises(ValueError, match="cannot carry authority"):
        core_conversation_meaning_from_event(core_event(authority="runtime"))

    with pytest.raises(ValueError, match="cannot grant authority"):
        core_conversation_meaning_from_event(core_event(grants_execution=True))


def test_conversation_gateway_uses_grounded_core_reply_when_bound():
    def resolver(request):
        return event_for_request(request)

    gateway = ConversationGateway(
        conversation_id="bench-chat",
        meaning_resolver=resolver,
    )

    exchange = gateway.submit("What is the cabin temperature?")

    assert exchange.reply.text == "Cabin temperature is 21.5 °C."
    assert exchange.reply.generator == "core-grounded-conversation"
    assert exchange.reply.authority_granted is False


def test_spoken_and_written_turns_share_same_grounded_reply_contract():
    def resolver(request):
        return event_for_request(request)

    gateway = ConversationGateway(
        conversation_id="bench-chat",
        meaning_resolver=resolver,
    )

    written = gateway.submit("What is the cabin temperature?")
    spoken = gateway.submit(
        "What is the cabin temperature?",
        modality=ConversationModality.SPEECH_TRANSCRIPT,
    )

    assert written.reply.text == spoken.reply.text
    assert written.reply.speak is False
    assert spoken.reply.speak is True


def test_action_request_keeps_runtime_authority_baseline_if_core_has_no_grounding():
    def resolver(request):
        return event_for_request(
            request,
            response_kind="unavailable",
            fact_id=None,
            value=None,
            unit=None,
            confidence=0.0,
            source_refs=[],
            qualifiers=["no-grounded-resolver"],
        )

    gateway = ConversationGateway(
        conversation_id="bench-chat",
        meaning_resolver=resolver,
    )

    exchange = gateway.submit("Open the window")

    assert exchange.request.requires_authority_check is True
    assert "Runtime still has to authorize" in exchange.reply.text
    assert exchange.reply.generator == "deterministic-conversation-baseline"


def test_gateway_rejects_core_reply_for_wrong_turn():
    def resolver(request):
        return event_for_request(request, turn_id="another-turn:99")

    gateway = ConversationGateway(
        conversation_id="bench-chat",
        meaning_resolver=resolver,
    )

    with pytest.raises(ValueError, match="turn_id does not match"):
        gateway.submit("What is the cabin temperature?")
