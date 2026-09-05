"""Naturalize verified evidence without changing what the evidence says.

This module is deliberately deterministic. It may remove Markdown presentation
syntax and turn an explicit heading-plus-list into a sentence, but it never
adds synonyms, inferred facts, trust, authority, or conclusions. The exact
source excerpt remains available separately on the grounded expression.
"""

from __future__ import annotations

import re
from typing import Iterable, Tuple

_HEADING_LIST_RE = re.compile(
    r"(?:^|\s)#{1,6}\s+(.{1,96}?)\s+(?=-\s+)",
    re.DOTALL,
)
_BULLET_RE = re.compile(
    r"(?:^|\s)-\s+(.+?)(?=(?:\s+-\s+)|(?:\s+#{1,6}\s+)|$)",
    re.DOTALL,
)
_MARKDOWN_HEADING_RE = re.compile(r"(?:^|\s)#{1,6}\s+")


def realize_evidence_text(
    excerpt: str,
    *,
    source_label: str,
    qualifiers: Iterable[str] = (),
) -> str:
    """Return human-facing wording while preserving source posture explicitly."""

    if not isinstance(excerpt, str) or not excerpt.strip():
        raise ValueError("evidence excerpt must be non-empty text")
    if not isinstance(source_label, str) or not source_label.strip():
        raise ValueError("evidence source label must be non-empty text")

    natural = naturalize_evidence_excerpt(excerpt)
    qualifier_set = {str(item).casefold() for item in qualifiers}
    text = "According to %s, %s" % (source_label.strip(), _lower_leading(natural))

    if "source-superseded" in qualifier_set:
        text += " That source has been superseded."
    elif "source-stale" in qualifier_set:
        text += " That source is marked stale."
    return text


def naturalize_evidence_excerpt(excerpt: str) -> str:
    """Restructure only syntax that is explicit in the retrieved excerpt.

    A flattened Markdown fragment such as ``## Core principles - Local first.
    - Trust is graded.`` becomes ``Core principles are local first and trust is
    graded.``. Ordinary prose is left substantively unchanged.
    """

    clean = " ".join(excerpt.split()).strip()
    if not clean:
        raise ValueError("evidence excerpt must be non-empty text")

    heading_match = _HEADING_LIST_RE.search(clean)
    if heading_match is not None:
        heading = _clean_fragment(heading_match.group(1))
        tail = clean[heading_match.end() :]
        items = tuple(
            _clean_list_item(match.group(1))
            for match in _BULLET_RE.finditer(tail)
        )
        items = tuple(item for item in items if item)
        if len(items) >= 2:
            subject = _lower_leading(_strip_terminal_punctuation(heading))
            return "%s are %s." % (subject, _join_items(items))

    # No safe structural rewrite was found. Remove heading markers only; keep
    # the source wording otherwise intact.
    plain = _MARKDOWN_HEADING_RE.sub("", clean).strip()
    return _ensure_terminal_punctuation(plain)


def _clean_fragment(value: str) -> str:
    return " ".join(value.replace("**", "").replace("__", "").split()).strip()


def _clean_list_item(value: str) -> str:
    return _strip_terminal_punctuation(_clean_fragment(value))


def _strip_terminal_punctuation(value: str) -> str:
    return value.rstrip().rstrip(".;:")


def _join_items(items: Tuple[str, ...]) -> str:
    normalized = tuple(_lower_leading(item) for item in items if item)
    if len(normalized) == 1:
        return normalized[0]
    if len(normalized) == 2:
        return "%s and %s" % normalized
    return "%s, and %s" % ("; ".join(normalized[:-1]), normalized[-1])


def _lower_leading(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    first = value[0]
    if first.isalpha() and not (len(value) > 1 and value[:2].isupper()):
        return first.lower() + value[1:]
    return value


def _ensure_terminal_punctuation(value: str) -> str:
    if not value:
        return value
    if value[-1] in ".!?":
        return value
    return value + "."
