import pytest

from velvet_language import GroundedResponseKind, realize_core_conversation_meaning


def evidence_event(**overrides):
    event = {
        "event": "velvet.core.conversation.meaning",
        "schema_version": "0.1",
        "conversation_id": "bench-chat",
        "turn_id": "bench-chat:1",
        "turn_number": 1,
        "response_kind": "evidence",
        "fact_id": "library.evidence",
        "value": "Tighten the pulley bolt to 170 N·m after seating the pulley.",
        "unit": None,
        "source_label": "Tiburon Workshop Manual",
        "confidence": 1.0,
        "qualifiers": ["reference-only", "trust-class:primary"],
        "source_refs": [
            "library:item:item_manual",
            "library:sha256:" + "a" * 64,
            "library:chunk:chk_123",
        ],
        "requires_authority_check": False,
        "authority": "none",
        "grants_authority": False,
        "grants_execution": False,
        "grants_actuation": False,
    }
    event.update(overrides)
    return event


def test_reference_only_library_passage_is_naturally_worded_but_stays_evidence():
    expression = realize_core_conversation_meaning(evidence_event())

    assert expression.response_kind is GroundedResponseKind.EVIDENCE
    assert expression.text == (
        "According to Tiburon Workshop Manual, "
        "tighten the pulley bolt to 170 N·m after seating the pulley."
    )
    assert expression.evidence_texts == (
        "Tighten the pulley bolt to 170 N·m after seating the pulley.",
    )
    assert expression.source_label == "Tiburon Workshop Manual"
    assert expression.source_refs[0] == "library:item:item_manual"
    assert expression.authority_granted is False


def test_flattened_markdown_list_is_realized_as_a_natural_sentence():
    excerpt = (
        "Velour keeps provenance for another component. ## Core principles "
        "- Local first. - Provenance before confidence. - Preserve the source. "
        "- Trust is graded. - Retrieval is not belief. - Receipts matter. "
        "- Knowledge is modular. - Models are optional. "
        "- Currency is metadata, not truth."
    )
    expression = realize_core_conversation_meaning(
        evidence_event(value=excerpt, source_label="Velour Library README")
    )

    assert expression.text == (
        "According to Velour Library README, core principles are local first; "
        "provenance before confidence; preserve the source; trust is graded; "
        "retrieval is not belief; receipts matter; knowledge is modular; "
        "models are optional; and currency is metadata, not truth."
    )
    assert expression.evidence_texts == (excerpt,)


def test_stale_and_superseded_library_sources_are_disclosed():
    stale = realize_core_conversation_meaning(
        evidence_event(qualifiers=["reference-only", "source-stale"])
    )
    superseded = realize_core_conversation_meaning(
        evidence_event(qualifiers=["reference-only", "source-superseded"])
    )

    assert "source is marked stale" in stale.text
    assert "source has been superseded" in superseded.text


def test_evidence_requires_source_and_stable_refs():
    with pytest.raises(ValueError, match="source_label"):
        realize_core_conversation_meaning(evidence_event(source_label=None))
    with pytest.raises(ValueError, match="source_refs"):
        realize_core_conversation_meaning(evidence_event(source_refs=[]))


def test_evidence_cannot_smuggle_authority():
    with pytest.raises(ValueError, match="cannot grant authority"):
        realize_core_conversation_meaning(evidence_event(grants_execution=True))
