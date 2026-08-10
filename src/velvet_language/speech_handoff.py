from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .context_strategy import StrategyContext
from .models import RenderedExpression

SPEECH_EXPRESSION_EVENT = "language.expression.speech_requested"
SPEECH_EXPRESSION_CONTRACT = "velvet.speech-expression.v1"
SPEECH_EXPRESSION_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class SpeechExpressionDraft:
    """Transport-neutral Language output for Event Protocol publication.

    The draft deliberately stops before hardware, synthesis, routing, Runtime
    authority, or receipt decisions. Runtime/Event Protocol wiring may wrap this
    value in the canonical event envelope.
    """

    event_type: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any]

    def __post_init__(self) -> None:
        if self.event_type != SPEECH_EXPRESSION_EVENT:
            raise ValueError("unexpected speech expression event type")
        if self.metadata.get("contract") != SPEECH_EXPRESSION_CONTRACT:
            raise ValueError("unexpected speech expression contract")
        if self.metadata.get("authority") != "none":
            raise ValueError("speech expression draft cannot carry authority")
        if self.payload.get("speech_approved") is not True:
            raise ValueError("speech expression draft must be approved for speech")
        if self.payload.get("command_authority") is not False:
            raise ValueError("speech expression draft cannot carry command authority")
        if self.payload.get("actuation_authority") is not False:
            raise ValueError("speech expression draft cannot carry actuation authority")
        if self.payload.get("hardware_selected") is not False:
            raise ValueError("language cannot select speech hardware")
        if self.payload.get("synthesis_selected") is not False:
            raise ValueError("language cannot select speech synthesis implementation")


def build_speech_expression_draft(
    expression: RenderedExpression,
    context: StrategyContext,
    *,
    requested_profile: Optional[str] = None,
    quiet_requested: bool = False,
    social_allowed: bool = False,
) -> Optional[SpeechExpressionDraft]:
    """Convert one approved RenderedExpression into a nervous-system draft.

    Silent/display-only expressions intentionally produce no speech event.
    Presentation context may request a named delivery posture, but Language does
    not choose a TTS model, speaker, ALSA device, channel, gain, or authority.
    """

    if not expression.speak:
        return None

    severity = expression.severity.strip().casefold()
    if severity not in {"casual", "informational", "warning", "critical", "emergency"}:
        raise ValueError("unsupported speech expression severity")
    driving_load = context.driving_load.strip().casefold()
    if driving_load not in {"low", "medium", "high"}:
        raise ValueError("driving_load must be low, medium, or high")
    audience = context.audience.strip().casefold()
    if not audience:
        raise ValueError("speech audience must be non-empty")

    profile = (requested_profile or _default_profile(expression, context, quiet_requested)).strip()
    if not profile:
        raise ValueError("requested_profile must be non-empty")
    if profile == "playful_social" and not social_allowed:
        profile = "owner_default"

    text = " ".join(expression.text.split())
    if not text:
        raise ValueError("spoken expression text must be non-empty")
    if len(text) > 4096:
        raise ValueError("spoken expression text exceeds 4096 characters")

    payload: Dict[str, Any] = {
        "schema_version": SPEECH_EXPRESSION_SCHEMA_VERSION,
        "expression_id": expression.response_id.strip(),
        "text": text,
        "severity": severity,
        "audience": audience,
        "requested_profile": profile,
        "driving_load": driving_load,
        "emergency_context": bool(context.emergency),
        "quiet_requested": bool(quiet_requested),
        "social_allowed": bool(social_allowed),
        "interrupt": bool(expression.interrupt),
        "generator": expression.generator.strip(),
        "policy_version": expression.policy_version.strip(),
        "speech_approved": True,
        "command_authority": False,
        "actuation_authority": False,
        "hardware_selected": False,
        "synthesis_selected": False,
    }
    for name in ("expression_id", "generator", "policy_version"):
        if not payload[name]:
            raise ValueError("{} must be non-empty".format(name))

    return SpeechExpressionDraft(
        event_type=SPEECH_EXPRESSION_EVENT,
        payload=payload,
        metadata={
            "contract": SPEECH_EXPRESSION_CONTRACT,
            "schema_version": SPEECH_EXPRESSION_SCHEMA_VERSION,
            "family": "speech-expression",
            "authority": "none",
            "expression_only": True,
        },
    )


def _default_profile(
    expression: RenderedExpression,
    context: StrategyContext,
    quiet_requested: bool,
) -> str:
    if context.emergency or expression.severity.strip().casefold() == "emergency":
        return "emergency"
    if expression.severity.strip().casefold() in {"warning", "critical"}:
        return "warning"
    if context.driving_load.strip().casefold() == "high":
        return "high_driving_load"
    if context.audience.strip().casefold() != "owner":
        return "guest_reserved"
    if quiet_requested:
        return "quiet_night"
    return "owner_default"
