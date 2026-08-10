from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class ReflectionExpressionInput:
    """Verified reflection material supplied by Core or another trusted owner."""

    finding: str
    notes: Tuple[str, ...] = ()
    confidence_direction: Optional[str] = None
    speech_approved: bool = False
    audience: str = "owner"

    def __post_init__(self) -> None:
        if not self.finding.strip():
            raise ValueError("finding is required")
        if self.confidence_direction not in {None, "higher", "lower", "unchanged"}:
            raise ValueError("unsupported confidence_direction")
        if any(not note.strip() for note in self.notes):
            raise ValueError("reflection notes cannot be blank")


@dataclass(frozen=True)
class ReflectionExpression:
    text: Optional[str]
    suppressed: bool
    reason: str
    authority: str = "none"

    def __post_init__(self) -> None:
        if self.authority != "none":
            raise ValueError("reflection expression cannot carry authority")
        if self.suppressed and self.text is not None:
            raise ValueError("suppressed reflection expressions cannot contain text")


def realize_reflection(value: ReflectionExpressionInput) -> ReflectionExpression:
    """Express verified reflection without performing reflection or learning."""

    if not value.speech_approved:
        return ReflectionExpression(
            text=None,
            suppressed=True,
            reason="reflection has not been approved for speech",
        )

    text = value.finding.strip()
    if value.confidence_direction == "lower":
        text += " I'm lowering my confidence in that explanation."
    elif value.confidence_direction == "higher":
        text += " I have more confidence in that explanation now."
    elif value.confidence_direction == "unchanged":
        text += " My confidence in that explanation is unchanged."

    if value.audience == "owner" and not text.lower().startswith("mister"):
        text = "Mister, " + text[0].lower() + text[1:]

    return ReflectionExpression(
        text=text,
        suppressed=False,
        reason="verified reflection expressed",
    )
