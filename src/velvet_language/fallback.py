from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any


@dataclass(frozen=True)
class FallbackExpression:
    response_id: str
    text: str
    speak: bool
    display: bool
    interrupt: bool
    severity: str
    generator: str = "deterministic-fallback"
    policy_version: str = "0.1"


_DEFAULTS = {
    "casual": ("I don't have enough verified information to answer that yet.", False),
    "informational": ("That information is currently unavailable.", False),
    "warning": ("A required system is unavailable. I'm continuing with reduced capability.", True),
    "critical": ("A critical capability is unavailable.", True),
    "emergency": ("Critical system unavailable. Follow the emergency procedure now.", True),
}


def render_fallback(meaning: Mapping[str, Any]) -> FallbackExpression:
    """Render bounded language when no richer language path is available.

    This function deliberately does not infer missing facts. It consumes only
    the severity and already-established subsystem/event names supplied by the
    caller.
    """

    severity = str(meaning.get("severity", "informational")).lower()
    if severity not in _DEFAULTS:
        severity = "informational"

    base_text, interrupt = _DEFAULTS[severity]
    subsystem = meaning.get("subsystem")

    if subsystem and severity in {"informational", "warning", "critical"}:
        safe_name = str(subsystem).replace("_", " ").strip()
        if safe_name:
            if severity == "informational":
                base_text = f"{safe_name.capitalize()} information is currently unavailable."
            elif severity == "warning":
                base_text = f"{safe_name.capitalize()} is unavailable. I'm continuing with reduced capability."
            else:
                base_text = f"Critical capability unavailable: {safe_name}."

    event = str(meaning.get("event", "unknown"))
    return FallbackExpression(
        response_id=f"fallback.{severity}.{event}",
        text=base_text,
        speak=True,
        display=True,
        interrupt=interrupt,
        severity=severity,
    )
