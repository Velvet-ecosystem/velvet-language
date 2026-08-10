from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .models import MeaningPacket, RenderedExpression, ResponseVariant
from .fallback import render_fallback


_SEVERITY_ORDER = {
    "casual": 0,
    "informational": 1,
    "warning": 2,
    "critical": 3,
    "emergency": 4,
}


@dataclass(frozen=True)
class SelectionContext:
    recent_response_ids: Sequence[str] = ()
    allow_generation: bool = True
    force_deterministic: bool = False


def _eligible(meaning: MeaningPacket, variant: ResponseVariant) -> bool:
    audience_ok = variant.audience in {meaning.audience, "any"}
    mode_ok = variant.mode in {meaning.mode, "any"}
    return audience_ok and mode_ok


def select_response(
    meaning: MeaningPacket,
    variants: Iterable[ResponseVariant],
    context: SelectionContext | None = None,
) -> RenderedExpression:
    """Choose a truthful response variant without inventing state.

    High-consequence severities prefer deterministic catalog language. Recent
    response IDs are avoided when an equivalent unused variant exists.
    """
    context = context or SelectionContext()
    severity = meaning.severity.lower()
    deterministic_required = context.force_deterministic or severity in {"critical", "emergency"}

    candidates = [variant for variant in variants if _eligible(meaning, variant)]
    if not candidates:
        fallback = render_fallback(meaning.__dict__)
        return RenderedExpression(
            response_id=fallback.response_id,
            text=fallback.text,
            speak=fallback.speak,
            display=fallback.display,
            interrupt=fallback.interrupt,
            severity=fallback.severity,
            generator=fallback.generator,
            policy_version=fallback.policy_version,
        )

    recent = set(context.recent_response_ids)
    unused = [variant for variant in candidates if variant.response_id not in recent]
    chosen_pool = unused or candidates

    # Catalog variants are already approved language. For deterministic-required
    # states this is the only permitted path in the foundation implementation.
    chosen = chosen_pool[0]
    generator = "catalog-deterministic" if deterministic_required else "catalog"

    return RenderedExpression(
        response_id=chosen.response_id,
        text=chosen.text,
        speak=chosen.speak,
        display=chosen.display,
        interrupt=chosen.interrupt or _SEVERITY_ORDER.get(severity, 1) >= _SEVERITY_ORDER["critical"],
        severity=severity,
        generator=generator,
    )
