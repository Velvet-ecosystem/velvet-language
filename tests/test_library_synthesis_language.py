import pytest

from velvet_language import (
    GroundedResponseKind,
    core_conversation_meaning_from_event,
    realize_core_conversation_meaning,
)


def synthesis_event(**overrides):
    event = {
        "event": "velvet.core.conversation.meaning",
        "schema_version": "0.1",
        "conversation_id": "bench-chat",
        "turn_id": "bench-chat:1",
        "turn_number": 1,
        "response_kind": "synthesis",
        "fact_id": "library.synthesis",
        "value": "170 N·m",
        "unit": None,
        "source_label": None,
        "source_labels": ["Factory Manual", "Service Reference"],
        "evidence_values": ["170 N·m", "125 ft-lb"],
        "evidence_disposition": "corroborated",
        "confidence": 1.0,
        "qualifiers": ["reference-only", "multi-source", "comparison:normalized-measurement"],
        "source_refs": [
            "library:item:manual_a",
            "library:chunk:chunk_a",
            "library:item:manual_b",
            "library:chunk:chunk_b",
        ],
        "requires_authority_check": False,
        "authority": "none",
        "grants_authority": False,
        "grants_execution": False,
        "grants_actuation": False,
    }
    event.update(overrides)
    return event


def test_corroborated_measurement_is_spoken_as_compared_evidence():
    expression = realize_core_conversation_meaning(synthesis_event())

    assert expression.response_kind is GroundedResponseKind.SYNTHESIS
    assert expression.text == "Velour compared 2 Library sources. They agree on 170 N·m."
    assert expression.authority_granted is False


def test_text_corroboration_is_not_called_a_verified_fact():
    expression = realize_core_conversation_meaning(
        synthesis_event(
            value="Disconnect battery power before removing the connector.",
            evidence_values=[
                "Disconnect battery power before removing the connector.",
                "Before connector removal, disconnect battery power.",
            ],
            qualifiers=["reference-only", "multi-source", "comparison:lexical-overlap"],
        )
    )

    assert expression.text.startswith(
        "Velour compared 2 Library sources. They point to the same guidance:"
    )
    assert "verified" not in expression.text.casefold()


def test_conflict_is_shown_and_not_collapsed():
    expression = realize_core_conversation_meaning(
        synthesis_event(
            value=None,
            evidence_values=["170 N·m", "140 N·m"],
            evidence_disposition="conflicted",
            qualifiers=["reference-only", "multi-source", "comparison:measurement-conflict"],
        )
    )

    assert "conflicting Library evidence" in expression.text
    assert "Factory Manual: 170 N·m" in expression.text
    assert "Service Reference: 140 N·m" in expression.text
    assert "won't collapse" in expression.text


def test_mixed_sources_are_presented_as_unresolved():
    expression = realize_core_conversation_meaning(
        synthesis_event(
            value=None,
            evidence_values=[
                "Inspect the belt edge for fraying and glazing.",
                "Keep the tensioner mark inside the reference window.",
            ],
            evidence_disposition="mixed",
            qualifiers=["reference-only", "multi-source", "comparison:unresolved"],
        )
    )

    assert "don't support one clean answer" in expression.text
    assert "Factory Manual" in expression.text
    assert "Service Reference" in expression.text


def test_stale_source_warning_survives_synthesis():
    expression = realize_core_conversation_meaning(
        synthesis_event(qualifiers=[
            "reference-only",
            "multi-source",
            "comparison:normalized-measurement",
            "source-stale",
        ])
    )

    assert expression.text.endswith("One or more sources are marked stale.")


def test_synthesis_contract_rejects_missing_pairs_or_authority():
    with pytest.raises(ValueError, match="align"):
        core_conversation_meaning_from_event(
            synthesis_event(evidence_values=["170 N·m"])
        )

    with pytest.raises(ValueError, match="cannot grant authority"):
        core_conversation_meaning_from_event(
            synthesis_event(grants_execution=True)
        )
