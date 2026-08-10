from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MeaningPacket:
    event: str
    severity: str
    audience: str = "owner"
    mode: str = "normal"
    subsystem: Optional[str] = None
    confidence: Optional[float] = None


@dataclass(frozen=True)
class ResponseVariant:
    response_id: str
    text: str
    audience: str
    mode: str
    speak: bool = True
    display: bool = True
    interrupt: bool = False


@dataclass(frozen=True)
class RenderedExpression:
    response_id: str
    text: str
    speak: bool
    display: bool
    interrupt: bool
    severity: str
    generator: str
    policy_version: str = "0.1"
