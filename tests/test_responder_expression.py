import pytest

from velvet_language.responder_expression import (
    ResponderExpressionInput,
    ResponderResponseKind,
    ResponderTruthClass,
    build_responder_speech_draft,
    realize_responder_answer,
    realize_responder_introduction,
    responder_input_from_plan,
)


def _fact(**overrides):
    values = {
        "incident_id": "incident-42",
        "question_id": "q-1",
        "response_kind": ResponderResponseKind.FACT,
        "fact_id": "location.current",
        "truth_class": ResponderTruthClass.KNOWN,
        "value": "49.2827,-123.1207",
        "qualifiers": (),
        "authority": "none",
    }
    values.update(overrides)
    return ResponderExpressionInput(**values)


def test_known_location_is_direct_and_uses_emergency_speech_handoff():
    value = _fact()

    expression = realize_responder_answer(value)
    draft = build_responder_speech_draft(value)

    assert expression.text == "The vehicle location is 49.2827,-123.1207."
    assert expression.generator == "responder-expression-protocol"
    assert expression.severity == "emergency"
    assert draft.metadata["authority"] == "none"
    assert draft.payload["requested_profile"] == "emergency"
    assert draft.payload["audience"] == "responder"
    assert draft.payload["command_authority"] is False
    assert draft.payload["actuation_authority"] is False


def test_inference_is_never_smoothed_into_known_wording():
    expression = realize_responder_answer(
        _fact(
            question_id="q-2",
            fact_id="occupant.responsive",
            truth_class=ResponderTruthClass.INFERRED,
            value=False,
            qualifiers=("inferred",),
        )
    )

    assert expression.text == "Based on the available evidence, the occupant appears unresponsive."
    assert "confirmed" not in expression.text.casefold()


def test_stale_fact_is_explicitly_last_known():
    expression = realize_responder_answer(
        _fact(
            question_id="q-3",
            fact_id="location.last-known",
            truth_class=ResponderTruthClass.STALE,
            value="last-known-fix",
            qualifiers=("stale", "Last verified 90 seconds ago."),
        )
    )

    assert expression.text.startswith("Last known: The vehicle location is last-known-fix.")
    assert "Last verified 90 seconds ago." in expression.text


def test_unavailable_answer_cannot_carry_or_invent_a_value():
    value = ResponderExpressionInput(
        incident_id="incident-42",
        question_id="q-4",
        response_kind=ResponderResponseKind.UNAVAILABLE,
        fact_id="occupant.breathing",
        truth_class=ResponderTruthClass.UNAVAILABLE,
        value=None,
        qualifiers=("unavailable",),
    )

    expression = realize_responder_answer(value)

    assert expression.text == "I cannot verify that."

    with pytest.raises(ValueError, match="cannot carry a value"):
        ResponderExpressionInput(
            incident_id="incident-42",
            question_id="q-4",
            response_kind=ResponderResponseKind.UNAVAILABLE,
            fact_id="occupant.breathing",
            truth_class=ResponderTruthClass.UNAVAILABLE,
            value="probably",
        )


def test_withheld_answer_cannot_leak_sensitive_value():
    value = ResponderExpressionInput(
        incident_id="incident-42",
        question_id="q-5",
        response_kind=ResponderResponseKind.WITHHELD,
        fact_id="medical.allergy",
        truth_class=None,
        value=None,
        qualifiers=("protected-channel-required",),
    )

    expression = realize_responder_answer(value)

    assert expression.text == "I cannot provide that information on this channel."

    with pytest.raises(ValueError, match="cannot carry a value"):
        ResponderExpressionInput(
            incident_id="incident-42",
            question_id="q-5",
            response_kind=ResponderResponseKind.WITHHELD,
            fact_id="medical.allergy",
            truth_class=None,
            value="private-allergy-value",
        )


def test_authority_is_rejected_before_expression():
    with pytest.raises(ValueError, match="cannot carry authority"):
        _fact(authority="responder")


def test_serialized_medical_plan_parses_without_source_or_disclosure_metadata():
    value = responder_input_from_plan(
        {
            "incident_id": "incident-42",
            "question_id": "q-6",
            "response_kind": "fact",
            "truth_class": "known",
            "fact_id": "vehicle.stationary",
            "value": True,
            "qualifiers": [],
            "authority": "none",
            "source_refs": ["vehicle-state-private-ref"],
            "disclosure_decision": "allow",
        }
    )

    expression = realize_responder_answer(value)

    assert expression.text == "The vehicle is stationary."
    assert not hasattr(value, "source_refs")


def test_responder_introduction_identifies_velvet_without_impersonation():
    expression = realize_responder_introduction("incident-42")

    assert "automated local assistant" in expression.text
    assert "occupant may be unable to respond" in expression.text
    assert "verified incident information" in expression.text
    assert "I am the owner" not in expression.text
    assert expression.severity == "emergency"


def test_fact_values_are_bounded_and_non_structured():
    with pytest.raises(ValueError, match="scalar"):
        realize_responder_answer(_fact(value={"raw": "not allowed"}))

    with pytest.raises(ValueError, match="512"):
        realize_responder_answer(_fact(value="x" * 513))
