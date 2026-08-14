from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Optional, Tuple

from .context_strategy import StrategyContext
from .models import RenderedExpression
from .speech_handoff import SpeechExpressionDraft, build_speech_expression_draft


_HEALTHY_STATES = {"AVAILABLE", "HEALTHY", "NORMAL", "ONLINE", "RECOVERED"}
_DEGRADED_STATES = {"DEGRADED", "STALE", "LIMITED"}
_FAILED_STATES = {"FAILED", "OFFLINE", "UNAVAILABLE"}

_SUBJECT_HINTS: Tuple[Tuple[Tuple[str, ...], str], ...] = (
    (("microphone", "mic", "audio-input", "audio_input"), "part of my hearing"),
    (("camera", "vision"), "part of my vision"),
    (("gnss", "gps", "position"), "my position awareness"),
    (("vehicle-can", "vehicle_can", "can-bus", "can_bus"), "my vehicle connection"),
    (("memory", "archive", "velour"), "part of my memory"),
    (("network", "ethernet", "lan"), "one of my system connections"),
)


@dataclass(frozen=True)
class SelfHealthExpressionInput:
    """Verified self-health transition supplied by Runtime/body evidence."""

    health_event_id: str
    module_id: str
    transition: str
    state_before: str
    state_after: str
    severity: str
    reason_code: Optional[str] = None
    audience: str = "owner"
    subject: Optional[str] = None

    def __post_init__(self) -> None:
        for name in (
            "health_event_id",
            "module_id",
            "transition",
            "state_before",
            "state_after",
            "severity",
            "audience",
        ):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError("{} must be a non-empty string".format(name))
        if self.reason_code is not None and not self.reason_code.strip():
            raise ValueError("reason_code cannot be blank")
        if self.subject is not None and not self.subject.strip():
            raise ValueError("subject cannot be blank")


def self_health_input_from_event(
    event_type: str,
    payload: Mapping[str, Any],
    *,
    audience: str = "owner",
    subject: Optional[str] = None,
) -> SelfHealthExpressionInput:
    """Parse one already-verified standard HealthEvent payload.

    This adapter does not decide whether the health evidence is true. Runtime/body
    systems own that decision. Language only receives the admitted transition and
    turns it into bounded human language.
    """

    if not isinstance(payload, Mapping):
        raise TypeError("health event payload must be a mapping")

    outer = _required_text_value(event_type, "event_type").upper()
    if not outer.startswith("HEALTH_"):
        raise ValueError("self-health expression requires a HEALTH_ event")

    transition = str(payload.get("event_type") or outer[7:]).strip().upper()
    health_event_id = str(
        payload.get("event_id") or payload.get("receipt_id") or ""
    ).strip()
    module_id = str(payload.get("module_id") or "").strip()
    state_before = str(payload.get("state_before") or "UNKNOWN").strip().upper()
    state_after = str(payload.get("state_after") or "UNKNOWN").strip().upper()
    severity = str(payload.get("severity") or "INFO").strip().upper()

    diagnostic = payload.get("diagnostic_payload")
    reason_code = None
    if isinstance(diagnostic, Mapping):
        raw_reason = diagnostic.get("reason_code")
        if isinstance(raw_reason, str) and raw_reason.strip():
            reason_code = raw_reason.strip()

    return SelfHealthExpressionInput(
        health_event_id=_required_text_value(health_event_id, "health_event_id"),
        module_id=_required_text_value(module_id, "module_id"),
        transition=_required_text_value(transition, "transition"),
        state_before=_required_text_value(state_before, "state_before"),
        state_after=_required_text_value(state_after, "state_after"),
        severity=_required_text_value(severity, "severity"),
        reason_code=reason_code,
        audience=_required_text_value(audience, "audience"),
        subject=subject,
    )


def realize_self_health(
    value: SelfHealthExpressionInput,
) -> Optional[RenderedExpression]:
    """Express a verified self-health transition without diagnosing or authorizing.

    Healthy startup announcements are intentionally silent. Degradation, loss,
    and recovery can speak. Exact technical diagnostics stay in the HealthEvent
    so a follow-up explanation can remain evidence-backed instead of reading raw
    diagnostic strings aloud automatically.
    """

    transition = value.transition.strip().upper()
    state_before = value.state_before.strip().upper()
    state_after = value.state_after.strip().upper()

    recovered = transition == "RECOVERED" or (
        state_after in _HEALTHY_STATES
        and state_before not in _HEALTHY_STATES
        and state_before != "UNKNOWN"
    )

    if not recovered and state_after in _HEALTHY_STATES:
        return None
    if transition in {"ONLINE", "AVAILABLE", "HEALTHY"} and not recovered:
        return None

    subject = (value.subject or _subject_for_module(value.module_id)).strip()
    owner_prefix = "Mister, " if value.audience.strip().casefold() == "owner" else ""

    if recovered:
        text = "{}I'm feeling better. {} is working normally again.".format(
            owner_prefix,
            _sentence_subject(subject),
        )
        severity = "informational"
        interrupt = False
    elif state_after in _FAILED_STATES or transition in {"FAILED", "UNAVAILABLE", "OFFLINE"}:
        text = "{}something's wrong. I've lost {}.".format(owner_prefix, subject)
        severity = _speech_severity(value.severity, floor="warning")
        interrupt = severity in {"critical", "emergency"}
    elif state_after in _DEGRADED_STATES or transition in {"DEGRADED", "STALE"}:
        text = "{}I'm not feeling quite right. I'm having trouble with {}.".format(
            owner_prefix,
            subject,
        )
        severity = _speech_severity(value.severity, floor="warning")
        interrupt = severity in {"critical", "emergency"}
    else:
        severity = _speech_severity(value.severity, floor="informational")
        if severity == "informational":
            return None
        text = "{}I'm not functioning normally. {} needs attention.".format(
            owner_prefix,
            _sentence_subject(subject),
        )
        interrupt = severity in {"critical", "emergency"}

    return RenderedExpression(
        response_id="self-health-{}".format(value.health_event_id),
        text=text,
        speak=True,
        display=True,
        interrupt=interrupt,
        severity=severity,
        generator="self-health-protocol",
        policy_version="1.0",
    )


def build_self_health_speech_draft(
    event_type: str,
    payload: Mapping[str, Any],
    *,
    audience: str = "owner",
    driving_load: str = "low",
    emergency: bool = False,
    subject: Optional[str] = None,
) -> Optional[SpeechExpressionDraft]:
    """Convert verified HealthEvent meaning into the existing speech handoff."""

    health = self_health_input_from_event(
        event_type,
        payload,
        audience=audience,
        subject=subject,
    )
    expression = realize_self_health(health)
    if expression is None:
        return None

    context = StrategyContext(
        audience=health.audience,
        driving_load=driving_load,
        emergency=bool(emergency) or expression.severity == "emergency",
        degraded=health.state_after.strip().upper() not in _HEALTHY_STATES,
    )
    return build_speech_expression_draft(expression, context)


def _speech_severity(value: str, *, floor: str) -> str:
    incoming = value.strip().upper()
    if incoming == "EMERGENCY":
        result = "emergency"
    elif incoming in {"CRITICAL", "ERROR", "FATAL"}:
        result = "critical"
    elif incoming in {"WARNING", "WARN"}:
        result = "warning"
    else:
        result = "informational"

    order = {"informational": 0, "warning": 1, "critical": 2, "emergency": 3}
    return result if order[result] >= order[floor] else floor


def _subject_for_module(module_id: str) -> str:
    normalized = module_id.strip().casefold()
    for hints, subject in _SUBJECT_HINTS:
        if any(hint in normalized for hint in hints):
            return subject

    label = re.sub(r"[_.:-]+", " ", normalized)
    label = " ".join(
        part for part in label.split() if part not in {"main", "primary", "module"}
    ).strip()
    if not label:
        return "one of my systems"
    return "my {} system".format(label)


def _sentence_subject(subject: str) -> str:
    return subject[0].upper() + subject[1:] if subject else "One of my systems"


def _required_text_value(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
    return value.strip()
