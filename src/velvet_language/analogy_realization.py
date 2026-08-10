from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AnalogyInput:
    """Verified relationship supplied for explanatory realization."""

    subject_label: str
    comparison_label: str
    shared_relation: str
    relationship_verified: bool = False
    speech_approved: bool = True
    audience: str = "owner"

    def __post_init__(self) -> None:
        for value, name in (
            (self.subject_label, "subject_label"),
            (self.comparison_label, "comparison_label"),
            (self.shared_relation, "shared_relation"),
        ):
            if not value.strip():
                raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class AnalogyExpression:
    text: Optional[str]
    suppressed: bool
    reason: str
    authority: str = "none"

    def __post_init__(self) -> None:
        if self.authority != "none":
            raise ValueError("analogy realization cannot carry authority")
        if self.suppressed and self.text is not None:
            raise ValueError("suppressed analogy cannot contain text")


def realize_analogy(value: AnalogyInput) -> AnalogyExpression:
    """Explain a verified relationship without inventing conceptual links."""

    if not value.relationship_verified:
        return AnalogyExpression(
            text=None,
            suppressed=True,
            reason="analogy relationship is not verified",
        )
    if not value.speech_approved:
        return AnalogyExpression(
            text=None,
            suppressed=True,
            reason="analogy has not been approved for speech",
        )

    text = (
        f"Think of {value.subject_label.strip()} as {value.comparison_label.strip()}: "
        f"both {value.shared_relation.strip()}."
    )
    if value.audience == "owner":
        text = "Mister, " + text[0].lower() + text[1:]

    return AnalogyExpression(
        text=text,
        suppressed=False,
        reason="verified relationship realized as analogy",
    )
