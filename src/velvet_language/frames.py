from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence


_SLOT_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


@dataclass(frozen=True)
class SentenceFrame:
    frame_id: str
    template: str
    required_slots: tuple[str, ...]
    optional_slots: tuple[str, ...] = ()


@dataclass(frozen=True)
class RealizedFrame:
    frame_id: str
    text: str
    used_slots: Mapping[str, Any]
    generator: str = "sentence-frame"
    policy_version: str = "0.1"


class MissingSlotError(ValueError):
    pass


class UnknownSlotError(ValueError):
    pass


def infer_slots(template: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(_SLOT_RE.findall(template)))


def realize_frame(frame: SentenceFrame, values: Mapping[str, Any]) -> RealizedFrame:
    template_slots = set(infer_slots(frame.template))
    declared = set(frame.required_slots) | set(frame.optional_slots)

    undeclared = template_slots - declared
    if undeclared:
        raise UnknownSlotError(
            f"frame {frame.frame_id} contains undeclared slots: {sorted(undeclared)}"
        )

    missing = [name for name in frame.required_slots if name not in values or values[name] is None]
    if missing:
        raise MissingSlotError(
            f"frame {frame.frame_id} missing required slots: {missing}"
        )

    unknown_values = set(values) - declared
    if unknown_values:
        raise UnknownSlotError(
            f"frame {frame.frame_id} received unknown slots: {sorted(unknown_values)}"
        )

    text = frame.template
    used: dict[str, Any] = {}

    for name in frame.required_slots:
        value = _clean_value(values[name])
        text = text.replace("{" + name + "}", value)
        used[name] = values[name]

    for name in frame.optional_slots:
        token = "{" + name + "}"
        if name in values and values[name] is not None:
            value = _clean_value(values[name])
            text = text.replace(token, value)
            used[name] = values[name]
        else:
            text = text.replace(token, "")

    text = _normalize_spacing(text)

    return RealizedFrame(frame_id=frame.frame_id, text=text, used_slots=used)


def choose_and_realize(
    frames: Sequence[SentenceFrame],
    values: Mapping[str, Any],
) -> RealizedFrame:
    """Choose the first compatible frame without guessing missing information."""
    errors: list[Exception] = []
    for frame in frames:
        try:
            return realize_frame(frame, values)
        except (MissingSlotError, UnknownSlotError) as exc:
            errors.append(exc)

    if errors:
        raise MissingSlotError("no compatible sentence frame could be realized") from errors[-1]
    raise MissingSlotError("no sentence frames were supplied")


def _clean_value(value: Any) -> str:
    text = str(value).strip()
    if not text:
        raise MissingSlotError("slot values may not be empty")
    if "{" in text or "}" in text:
        raise ValueError("slot values may not contain frame delimiters")
    return text


def _normalize_spacing(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip()
