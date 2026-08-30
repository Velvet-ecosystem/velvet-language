from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional, Tuple

from .context_strategy import StrategyContext
from .models import RenderedExpression
from .speech_handoff import SpeechExpressionDraft, build_speech_expression_draft


class ResponderTruthClass(str, Enum):
    KNOWN = "known"
    INFERRED = "inferred"
    STALE = "stale"
    UNAVAILABLE = "unavailable"


class ResponderResponseKind(str, Enum):
    FACT = "fact"
    UNAVAILABLE = "unavailable"
    WITHHELD = "withheld"


@dataclass(frozen=True)
class ResponderExpressionInput:
    """Authority-free responder answer plan already approved upstream.

    Medical/incident systems decide whether the fact is true, current, and
    permitted for disclosure. Language preserves those decisions and realizes
    concise deterministic wording. It does not reopen disclosure policy.
    """

    incident_id: str
    question_id: str
    response_kind: ResponderResponseKind
    fact_id: Optional[str] = None
    truth_class: Optional[ResponderTruthClass] = None
    value: Optional[Any] = None
    qualifiers: Tuple[str, ...] = ()
    authority: str = "none"

    def __post_init__(self) -> None:
        for name in ("incident_id", "question_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("{} must be a non-empty string".format(name))
        if self.authority != "none":
            raise ValueError("responder expression input cannot carry authority")
        if any(not isinstance(item, str) or not item.strip() for item in self.qualifiers):
            raise ValueError("qualifiers must contain non-empty strings")

        if self.response_kind is ResponderResponseKind.FACT:
            if self.truth_class not in {
                ResponderTruthClass.KNOWN,
                ResponderTruthClass.INFERRED,
                ResponderTruthClass.STALE,
            }:
                raise ValueError("fact responses require known, inferred, or stale truth")
            if not isinstance(self.fact_id, str) or not self.fact_id.strip():
                raise ValueError("fact responses require fact_id")
            if self.value is None:
                raise ValueError("fact responses require a value")
        elif self.response_kind is ResponderResponseKind.UNAVAILABLE:
            if self.truth_class is not ResponderTruthClass.UNAVAILABLE:
                raise ValueError("unavailable responses require unavailable truth")
            if self.value is not None:
                raise ValueError("unavailable responses cannot carry a value")
        elif self.response_kind is ResponderResponseKind.WITHHELD:
            if self.truth_class is not None:
                raise ValueError("withheld responses cannot expose a truth class")
            if self.value is not None:
                raise ValueError("withheld responses cannot carry a value")
        else:
            raise ValueError("unsupported responder response kind")


def responder_input_from_plan(plan: Mapping[str, Any]) -> ResponderExpressionInput:
    """Parse a serialized Medical Mobility responder answer plan.

    The adapter accepts only the authority-free semantic fields Language needs.
    Source references and disclosure internals intentionally do not enter the
    spoken expression object.
    """

    if not isinstance(plan, Mapping):
        raise TypeError("responder answer plan must be a mapping")

    kind = ResponderResponseKind(_required_text(plan.get("response_kind"), "response_kind"))
    raw_truth = plan.get("truth_class")
    truth = None if raw_truth is None else ResponderTruthClass(_required_text(raw_truth, "truth_class"))
    raw_qualifiers = plan.get("qualifiers") or ()
    if isinstance(raw_qualifiers, str) or not isinstance(raw_qualifiers, (list, tuple)):
        raise ValueError("qualifiers must be a list or tuple")

    return ResponderExpressionInput(
        incident_id=_required_text(plan.get("incident_id"), "incident_id"),
        question_id=_required_text(plan.get("question_id"), "question_id"),
        response_kind=kind,
        fact_id=_optional_text(plan.get("fact_id")),
        truth_class=truth,
        value=plan.get("value"),
        qualifiers=tuple(str(item).strip() for item in raw_qualifiers),
        authority=_required_text(plan.get("authority", "none"), "authority"),
    )


def realize_responder_answer(value: ResponderExpressionInput) -> RenderedExpression:
    """Turn one governed responder answer plan into deterministic emergency language."""

    if value.response_kind is ResponderResponseKind.WITHHELD:
        if "protected-channel-required" in value.qualifiers:
            text = "I cannot provide that information on this channel."
        else:
            text = "I cannot provide that information."
    elif value.response_kind is ResponderResponseKind.UNAVAILABLE:
        text = "I cannot verify that."
    else:
        core = _fact_text(value.fact_id or "fact", value.value)
        if value.truth_class is ResponderTruthClass.INFERRED:
            text = "Based on the available evidence, {}".format(_lower_first(core))
        elif value.truth_class is ResponderTruthClass.STALE:
            text = "Last known: {}".format(core)
        else:
            text = core

        spoken_qualifiers = [
            item
            for item in value.qualifiers
            if item not in {"inferred", "stale", "unavailable"}
        ]
        if spoken_qualifiers:
            text = "{} {}".format(text.rstrip("."), ". ".join(spoken_qualifiers)).rstrip() + "."

    return RenderedExpression(
        response_id="responder-{}-{}".format(value.incident_id.strip(), value.question_id.strip()),
        text=text,
        speak=True,
        display=True,
        interrupt=False,
        severity="emergency",
        generator="responder-expression-protocol",
        policy_version="1.0",
    )


def realize_responder_introduction(
    incident_id: str,
    *,
    occupant_may_be_unable: bool = True,
) -> RenderedExpression:
    """Provide the deterministic role disclosure at responder-session start."""

    incident = _required_text(incident_id, "incident_id")
    if occupant_may_be_unable:
        text = (
            "This is Velvet, the vehicle's automated local assistant. "
            "My occupant may be unable to respond. I can provide verified incident "
            "information and state when something is unknown."
        )
    else:
        text = (
            "This is Velvet, the vehicle's automated local assistant. "
            "I can provide verified incident information and state when something is unknown."
        )

    return RenderedExpression(
        response_id="responder-introduction-{}".format(incident),
        text=text,
        speak=True,
        display=True,
        interrupt=False,
        severity="emergency",
        generator="responder-expression-protocol",
        policy_version="1.0",
    )


def build_responder_speech_draft(
    value: ResponderExpressionInput,
    *,
    driving_load: str = "low",
) -> SpeechExpressionDraft:
    """Reuse the canonical Language -> Audio speech-expression handoff."""

    expression = realize_responder_answer(value)
    draft = build_speech_expression_draft(
        expression,
        StrategyContext(
            audience="responder",
            driving_load=driving_load,
            emergency=True,
        ),
    )
    if draft is None:
        raise RuntimeError("responder expression unexpectedly produced no speech draft")
    return draft


def _fact_text(fact_id: str, raw_value: Any) -> str:
    normalized = fact_id.strip().casefold()
    value = _bounded_value_text(raw_value)

    if normalized in {"location.current", "location.last-known"}:
        return "The vehicle location is {}.".format(value)
    if normalized == "vehicle.stationary" and isinstance(raw_value, bool):
        return "The vehicle is stationary." if raw_value else "The vehicle is not confirmed stationary."
    if normalized == "occupant.responsive" and isinstance(raw_value, bool):
        return "The occupant is responsive." if raw_value else "The occupant appears unresponsive."
    if normalized == "occupant.breathing" and isinstance(raw_value, bool):
        return "Breathing-related sensor evidence is present." if raw_value else "Breathing-related sensor evidence is not detected."
    if normalized == "medical.allergy":
        return "Configured emergency allergy information: {}.".format(value)

    label = " ".join(part for part in normalized.replace("_", " ").replace(".", " ").split())
    if not label:
        label = "incident information"
    return "{}: {}.".format(label.capitalize(), value)


def _bounded_value_text(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return str(value)
    if not isinstance(value, str):
        raise ValueError("responder fact values must be scalar text, number, or boolean")
    text = " ".join(value.split())
    if not text:
        raise ValueError("responder fact value cannot be blank")
    if len(text) > 512:
        raise ValueError("responder fact value exceeds 512 characters")
    return text


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


def _required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
    return value.strip()


def _optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError("optional text values cannot be blank")
    return value.strip()
