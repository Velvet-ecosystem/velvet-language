"""Realize structured Core conversation meaning into human language.

Core owns verified meaning. This module owns the final deterministic wording
for that meaning and rejects any Core payload that attempts to carry authority
or execution claims across the Language boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional, Tuple

CORE_CONVERSATION_MEANING_EVENT = "velvet.core.conversation.meaning"
CORE_CONVERSATION_SCHEMA_VERSION = "0.1"


class GroundedResponseKind(str, Enum):
    FACT = "fact"
    EVIDENCE = "evidence"
    UNAVAILABLE = "unavailable"
    ACKNOWLEDGE = "acknowledge"
    AUTHORITY_REQUIRED = "authority_required"


@dataclass(frozen=True)
class CoreConversationMeaning:
    conversation_id: str
    turn_id: str
    turn_number: int
    response_kind: GroundedResponseKind
    confidence: float
    fact_id: Optional[str] = None
    value: Any = None
    unit: Optional[str] = None
    source_label: Optional[str] = None
    qualifiers: Tuple[str, ...] = ()
    source_refs: Tuple[str, ...] = ()
    requires_authority_check: bool = False
    authority: str = "none"
    grants_authority: bool = False
    grants_execution: bool = False
    grants_actuation: bool = False

    def __post_init__(self) -> None:
        _require_text("conversation_id", self.conversation_id)
        _require_text("turn_id", self.turn_id)
        if isinstance(self.turn_number, bool) or not isinstance(self.turn_number, int):
            raise ValueError("turn_number must be an integer")
        if self.turn_number < 1:
            raise ValueError("turn_number must be positive")
        if not isinstance(self.response_kind, GroundedResponseKind):
            raise ValueError("response_kind must be GroundedResponseKind")
        if isinstance(self.confidence, bool) or not isinstance(self.confidence, (int, float)):
            raise ValueError("confidence must be numeric")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.fact_id is not None:
            _require_text("fact_id", self.fact_id)
        if self.unit is not None:
            _require_text("unit", self.unit)
        if self.source_label is not None:
            _require_text("source_label", self.source_label)
        _require_text_tuple("qualifiers", self.qualifiers)
        _require_text_tuple("source_refs", self.source_refs)
        if not isinstance(self.requires_authority_check, bool):
            raise ValueError("requires_authority_check must be boolean")
        if self.authority != "none":
            raise ValueError("Core conversation meaning cannot carry authority")
        if self.grants_authority or self.grants_execution or self.grants_actuation:
            raise ValueError("Core conversation meaning cannot grant authority or execution")

        if self.response_kind is GroundedResponseKind.FACT:
            if self.fact_id is None:
                raise ValueError("fact response requires fact_id")
            _require_scalar("value", self.value)
        elif self.response_kind is GroundedResponseKind.EVIDENCE:
            if self.fact_id is None:
                raise ValueError("evidence response requires fact_id")
            if self.source_label is None:
                raise ValueError("evidence response requires source_label")
            if not self.source_refs:
                raise ValueError("evidence response requires source_refs")
            _require_scalar("value", self.value)
            if not isinstance(self.value, str) or not self.value.strip():
                raise ValueError("evidence response value must be non-empty text")
        elif self.value is not None:
            raise ValueError("non-fact response cannot carry value")


@dataclass(frozen=True)
class GroundedConversationExpression:
    conversation_id: str
    turn_id: str
    turn_number: int
    text: str
    response_kind: GroundedResponseKind
    confidence: float
    source_refs: Tuple[str, ...]
    generator: str = "core-grounded-conversation"
    authority_granted: bool = False

    def __post_init__(self) -> None:
        if self.authority_granted:
            raise ValueError("grounded conversation expression cannot grant authority")


def core_conversation_meaning_from_event(event: Mapping[str, Any]) -> CoreConversationMeaning:
    if not isinstance(event, Mapping):
        raise TypeError("Core conversation meaning must be a mapping")
    if event.get("event") != CORE_CONVERSATION_MEANING_EVENT:
        raise ValueError("unexpected Core conversation meaning event")
    if event.get("schema_version") != CORE_CONVERSATION_SCHEMA_VERSION:
        raise ValueError("unsupported Core conversation schema version")
    try:
        response_kind = GroundedResponseKind(str(event.get("response_kind")))
    except ValueError as exc:
        raise ValueError("unsupported grounded response kind") from exc
    return CoreConversationMeaning(
        conversation_id=_text_value(event, "conversation_id"),
        turn_id=_text_value(event, "turn_id"),
        turn_number=event.get("turn_number"),
        response_kind=response_kind,
        confidence=event.get("confidence"),
        fact_id=_optional_text(event.get("fact_id")),
        value=event.get("value"),
        unit=_optional_text(event.get("unit")),
        source_label=_optional_text(event.get("source_label")),
        qualifiers=_text_sequence(event.get("qualifiers", ()), "qualifiers"),
        source_refs=_text_sequence(event.get("source_refs", ()), "source_refs"),
        requires_authority_check=event.get("requires_authority_check", False),
        authority=str(event.get("authority", "")),
        grants_authority=event.get("grants_authority") is True,
        grants_execution=event.get("grants_execution") is True,
        grants_actuation=event.get("grants_actuation") is True,
    )


def realize_core_conversation_meaning(event: Mapping[str, Any]) -> GroundedConversationExpression:
    meaning = core_conversation_meaning_from_event(event)
    if meaning.response_kind is GroundedResponseKind.FACT:
        label = _fact_label(meaning.fact_id or "fact")
        value = _format_value(meaning.value, meaning.unit)
        if meaning.confidence < 0.55:
            text = "With limited confidence, %s is %s." % (label.lower(), value)
        elif meaning.confidence < 0.8:
            text = "Based on the verified context, %s is %s." % (label.lower(), value)
        else:
            text = "%s is %s." % (label, value)
        if "stale" in {item.casefold() for item in meaning.qualifiers}:
            text = "Last known: %s" % text
    elif meaning.response_kind is GroundedResponseKind.EVIDENCE:
        excerpt = str(meaning.value).strip()
        qualifier_set = {item.casefold() for item in meaning.qualifiers}
        if "source-superseded" in qualifier_set:
            text = "Velour found this in %s, but that source has been superseded: %s" % (
                meaning.source_label,
                excerpt,
            )
        elif "source-stale" in qualifier_set:
            text = "Velour found this in %s, but the source is marked stale: %s" % (
                meaning.source_label,
                excerpt,
            )
        else:
            text = "Velour found this in %s: %s" % (meaning.source_label, excerpt)
    elif meaning.response_kind is GroundedResponseKind.AUTHORITY_REQUIRED:
        text = "I understand the request. Runtime authorization is required before any action can occur."
    elif meaning.response_kind is GroundedResponseKind.ACKNOWLEDGE:
        text = "Understood."
    else:
        text = "I don't have enough verified information to answer that yet."
    return GroundedConversationExpression(
        conversation_id=meaning.conversation_id,
        turn_id=meaning.turn_id,
        turn_number=meaning.turn_number,
        text=text,
        response_kind=meaning.response_kind,
        confidence=float(meaning.confidence),
        source_refs=meaning.source_refs,
    )


def _fact_label(fact_id: str) -> str:
    known = {
        "cabin.temperature": "Cabin temperature",
        "outside.temperature": "Outside temperature",
        "cabin.humidity": "Cabin humidity",
        "cabin.ambient_light": "Cabin ambient light",
        "vehicle.voltage": "Vehicle voltage",
        "vehicle.speed": "Vehicle speed",
        "engine.rpm": "Engine RPM",
        "ignition.state": "Ignition state",
        "engine.o2_fault": "O2 fault state",
    }
    if fact_id in known:
        return known[fact_id]
    cleaned = fact_id.replace("_", " ").replace(".", " ").strip()
    return cleaned[:1].upper() + cleaned[1:] if cleaned else "Verified value"


def _format_value(value: Any, unit: Optional[str]) -> str:
    rendered = "true" if value is True else "false" if value is False else str(value)
    if not unit:
        return rendered
    display_unit = {"C": "°C", "F": "°F", "rpm": "RPM"}.get(unit, unit)
    if display_unit == "%":
        return "%s%%" % rendered
    return "%s %s" % (rendered, display_unit)


def _text_value(event: Mapping[str, Any], key: str) -> str:
    value = event.get(key)
    _require_text(key, value)
    return str(value).strip()


def _optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    _require_text("optional text", value)
    return str(value).strip()


def _text_sequence(value: Any, name: str) -> Tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError("%s must be a list or tuple" % name)
    items = tuple(value)
    _require_text_tuple(name, items)
    return items


def _require_text(name: str, value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be non-empty text" % name)


def _require_text_tuple(name: str, value: Tuple[str, ...]) -> None:
    for item in value:
        _require_text(name, item)


def _require_scalar(name: str, value: Any) -> None:
    if isinstance(value, (dict, list, tuple, set)):
        raise ValueError("%s must be a scalar" % name)
    if isinstance(value, str) and len(value) > 512:
        raise ValueError("%s text must be <= 512 characters" % name)
