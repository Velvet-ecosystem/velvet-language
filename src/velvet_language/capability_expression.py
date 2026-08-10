from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CapabilityStatus(str, Enum):
    AVAILABLE = "available"
    PROPOSED = "proposed"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    NOT_INSTALLED = "not_installed"
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class CapabilityExpressionInput:
    capability_label: str
    status: CapabilityStatus
    source: str
    audience: str = "owner"
    authorization_required: bool = True
    actuation_granted: bool = False

    def __post_init__(self) -> None:
        if not self.capability_label.strip():
            raise ValueError("capability_label is required")
        if not self.source.strip():
            raise ValueError("verified capability source is required")
        if self.actuation_granted:
            raise ValueError("language capability input cannot grant actuation")


@dataclass(frozen=True)
class CapabilityExpression:
    text: str
    status: CapabilityStatus
    source: str
    authority: str = "none"

    def __post_init__(self) -> None:
        if self.authority != "none":
            raise ValueError("capability expression cannot carry authority")


def realize_capability(value: CapabilityExpressionInput) -> CapabilityExpression:
    """Express verified capability state without converting it into authority."""

    label = value.capability_label.strip()
    if value.status is CapabilityStatus.AVAILABLE:
        text = f"{label} is available to this body."
    elif value.status is CapabilityStatus.PROPOSED:
        text = f"I can request {label}, but authorization is still required."
    elif value.status is CapabilityStatus.DEGRADED:
        text = f"{label} is available with reduced capability."
    elif value.status is CapabilityStatus.UNAVAILABLE:
        text = f"{label} is currently unavailable."
    elif value.status is CapabilityStatus.NOT_INSTALLED:
        text = f"This body does not currently have {label} installed."
    else:
        text = f"I cannot currently verify {label}."

    if value.authorization_required and value.status is CapabilityStatus.AVAILABLE:
        text += " Authorization is separate."

    if value.audience == "owner" and not text.lower().startswith("mister"):
        text = "Mister, " + text[0].lower() + text[1:]

    return CapabilityExpression(text=text, status=value.status, source=value.source)
