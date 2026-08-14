import pytest

from velvet_language.self_health_expression import (
    build_self_health_speech_draft,
    realize_self_health,
    self_health_input_from_event,
)


def _payload(**overrides):
    values = {
        "event_id": "health-1",
        "event_type": "DEGRADED",
        "module_id": "microphone-input-main",
        "node_id": "founder-up2",
        "owning_handmaiden": "Velvet",
        "timestamp": 1.0,
        "severity": "WARNING",
        "state_before": "ONLINE",
        "state_after": "DEGRADED",
        "diagnostic_payload": {
            "reason_code": "CAPTURE_FAILURE",
            "detail": "device stopped responding",
        },
        "receipt_id": "health-1",
    }
    values.update(overrides)
    return values


def test_degraded_health_becomes_natural_owner_speech() -> None:
    draft = build_self_health_speech_draft("HEALTH_DEGRADED", _payload())

    assert draft is not None
    assert draft.event_type == "language.expression.speech_requested"
    assert draft.payload["text"] == (
        "Mister, I'm not feeling quite right. I'm having trouble with part of my hearing."
    )
    assert draft.payload["severity"] == "warning"
    assert draft.payload["requested_profile"] == "warning"
    assert draft.payload["speech_approved"] is True
    assert draft.metadata["authority"] == "none"


def test_failed_health_is_direct_and_can_interrupt_when_critical() -> None:
    draft = build_self_health_speech_draft(
        "HEALTH_FAILED",
        _payload(
            event_type="FAILED",
            state_after="FAILED",
            severity="ERROR",
            module_id="gnss-main",
        ),
    )

    assert draft is not None
    assert draft.payload["text"] == (
        "Mister, something's wrong. I've lost my position awareness."
    )
    assert draft.payload["severity"] == "critical"
    assert draft.payload["interrupt"] is True
    assert draft.payload["requested_profile"] == "warning"


def test_recovery_reports_feeling_better_without_warning_profile() -> None:
    draft = build_self_health_speech_draft(
        "HEALTH_RECOVERED",
        _payload(
            event_type="RECOVERED",
            state_before="FAILED",
            state_after="ONLINE",
            severity="NOTICE",
            module_id="vehicle-can-primary",
        ),
    )

    assert draft is not None
    assert draft.payload["text"] == (
        "Mister, I'm feeling better. My vehicle connection is working normally again."
    )
    assert draft.payload["severity"] == "informational"
    assert draft.payload["interrupt"] is False
    assert draft.payload["requested_profile"] == "owner_default"


def test_initial_healthy_state_is_silent() -> None:
    value = self_health_input_from_event(
        "HEALTH_ONLINE",
        _payload(
            event_type="ONLINE",
            state_before="UNKNOWN",
            state_after="ONLINE",
            severity="INFO",
        ),
    )

    assert realize_self_health(value) is None
    assert build_self_health_speech_draft("HEALTH_ONLINE", _payload(
        event_type="ONLINE",
        state_before="UNKNOWN",
        state_after="ONLINE",
        severity="INFO",
    )) is None


def test_raw_diagnostic_detail_is_not_read_aloud() -> None:
    draft = build_self_health_speech_draft(
        "HEALTH_DEGRADED",
        _payload(
            diagnostic_payload={
                "reason_code": "CAPTURE_FAILURE",
                "detail": "ALSA hw:0,0 returned errno 19",
            }
        ),
    )

    assert draft is not None
    assert "errno" not in draft.payload["text"]
    assert "hw:0,0" not in draft.payload["text"]


def test_unknown_module_gets_conservative_system_label() -> None:
    draft = build_self_health_speech_draft(
        "HEALTH_DEGRADED",
        _payload(module_id="forge-temperature-primary"),
    )

    assert draft is not None
    assert "my forge temperature system" in draft.payload["text"]


def test_rejects_non_health_event() -> None:
    with pytest.raises(ValueError, match="HEALTH_"):
        build_self_health_speech_draft("SENSOR_PACKET_OBSERVED", _payload())
