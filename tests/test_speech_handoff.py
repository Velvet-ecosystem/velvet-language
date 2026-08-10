import pytest

from velvet_language.context_strategy import StrategyContext
from velvet_language.models import RenderedExpression
from velvet_language.speech_handoff import (
    SPEECH_EXPRESSION_CONTRACT,
    SPEECH_EXPRESSION_EVENT,
    build_speech_expression_draft,
)


def _expression(**overrides):
    values = {
        "response_id": "response-1",
        "text": "Mister, systems nominal.",
        "speak": True,
        "display": True,
        "interrupt": False,
        "severity": "informational",
        "generator": "catalog",
        "policy_version": "0.1",
    }
    values.update(overrides)
    return RenderedExpression(**values)


def test_builds_event_protocol_draft_without_audio_or_authority_selection() -> None:
    draft = build_speech_expression_draft(
        _expression(),
        StrategyContext(audience="owner", driving_load="low"),
    )

    assert draft is not None
    assert draft.event_type == SPEECH_EXPRESSION_EVENT
    assert draft.metadata["contract"] == SPEECH_EXPRESSION_CONTRACT
    assert draft.metadata["authority"] == "none"
    assert draft.payload["requested_profile"] == "owner_default"
    assert draft.payload["speech_approved"] is True
    assert draft.payload["command_authority"] is False
    assert draft.payload["actuation_authority"] is False
    assert draft.payload["hardware_selected"] is False
    assert draft.payload["synthesis_selected"] is False
    assert "output_channels" not in draft.payload
    assert "model_path" not in draft.payload
    assert "volume" not in draft.payload


def test_display_only_or_silent_expression_emits_no_speech_draft() -> None:
    draft = build_speech_expression_draft(
        _expression(speak=False),
        StrategyContext(),
    )
    assert draft is None


def test_context_selects_bounded_delivery_request_without_physical_routing() -> None:
    emergency = build_speech_expression_draft(
        _expression(severity="informational"),
        StrategyContext(emergency=True),
    )
    assert emergency is not None
    assert emergency.payload["emergency_context"] is True
    assert emergency.payload["requested_profile"] == "emergency"

    guest = build_speech_expression_draft(
        _expression(),
        StrategyContext(audience="guest"),
    )
    assert guest is not None
    assert guest.payload["requested_profile"] == "guest_reserved"

    high_load = build_speech_expression_draft(
        _expression(),
        StrategyContext(driving_load="high"),
    )
    assert high_load is not None
    assert high_load.payload["requested_profile"] == "high_driving_load"


def test_playful_profile_requires_explicit_social_permission() -> None:
    blocked = build_speech_expression_draft(
        _expression(),
        StrategyContext(),
        requested_profile="playful_social",
        social_allowed=False,
    )
    assert blocked is not None
    assert blocked.payload["requested_profile"] == "owner_default"

    allowed = build_speech_expression_draft(
        _expression(),
        StrategyContext(),
        requested_profile="playful_social",
        social_allowed=True,
    )
    assert allowed is not None
    assert allowed.payload["requested_profile"] == "playful_social"
    assert allowed.payload["social_allowed"] is True


def test_rejects_invalid_severity_and_oversized_text() -> None:
    with pytest.raises(ValueError, match="severity"):
        build_speech_expression_draft(
            _expression(severity="dramatic"),
            StrategyContext(),
        )

    with pytest.raises(ValueError, match="4096"):
        build_speech_expression_draft(
            _expression(text="x" * 4097),
            StrategyContext(),
        )
