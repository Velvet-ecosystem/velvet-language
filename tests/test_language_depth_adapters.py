import pytest

from velvet_language.analogy_realization import AnalogyInput, realize_analogy
from velvet_language.capability_expression import (
    CapabilityExpressionInput,
    CapabilityStatus,
    realize_capability,
)
from velvet_language.concept_lexicon import LexicalConcept, LexicalRegister
from velvet_language.question_realization import QuestionCandidateInput, realize_question
from velvet_language.reflection_expression import ReflectionExpressionInput, realize_reflection


def test_question_candidate_cannot_speak_without_upstream_approval():
    result = realize_question(
        QuestionCandidateInput(
            candidate_text="Was that noise there before?",
            speech_approved=False,
        )
    )
    assert result.suppressed is True
    assert result.text is None
    assert result.authority == "none"


def test_approved_owner_question_keeps_candidate_meaning():
    result = realize_question(
        QuestionCandidateInput(
            candidate_text="Was that noise there before?",
            speech_approved=True,
        )
    )
    assert result.text == "Mister, was that noise there before?"


def test_reflection_is_expression_not_learning():
    result = realize_reflection(
        ReflectionExpressionInput(
            finding="The restart did not resolve the fault.",
            confidence_direction="lower",
            speech_approved=True,
        )
    )
    assert "lowering my confidence" in result.text
    assert result.authority == "none"


def test_unapproved_reflection_stays_silent():
    result = realize_reflection(
        ReflectionExpressionInput(
            finding="The evidence is incomplete.",
            speech_approved=False,
        )
    )
    assert result.suppressed is True
    assert result.text is None


def test_proposed_capability_never_implies_authorization():
    result = realize_capability(
        CapabilityExpressionInput(
            capability_label="window control",
            status=CapabilityStatus.PROPOSED,
            source="runtime-capability-context",
        )
    )
    assert "authorization is still required" in result.text
    assert result.authority == "none"


def test_capability_input_rejects_actuation_grant():
    with pytest.raises(ValueError):
        CapabilityExpressionInput(
            capability_label="window control",
            status=CapabilityStatus.AVAILABLE,
            source="runtime",
            actuation_granted=True,
        )


def test_lexicon_selects_terms_without_defining_world_truth():
    concept = LexicalConcept(
        concept_id="engine.combustion_instability",
        technical_term="combustion instability",
        common_term="rough running",
        owner_preferred_term="sputtering",
        synonyms=("stumbling",),
    )
    assert concept.term_for(LexicalRegister.TECHNICAL) == "combustion instability"
    assert concept.term_for(LexicalRegister.COMMON) == "rough running"
    assert concept.term_for(LexicalRegister.OWNER) == "sputtering"
    assert concept.recognizes("stumbling") is True


def test_analogy_requires_verified_relationship():
    result = realize_analogy(
        AnalogyInput(
            subject_label="CAN",
            comparison_label="a nervous system",
            shared_relation="carry signals between distributed parts",
            relationship_verified=False,
        )
    )
    assert result.suppressed is True
    assert result.text is None


def test_verified_analogy_can_be_realized():
    result = realize_analogy(
        AnalogyInput(
            subject_label="CAN",
            comparison_label="a nervous system",
            shared_relation="carry signals between distributed parts",
            relationship_verified=True,
        )
    )
    assert result.text == (
        "Mister, think of CAN as a nervous system: "
        "both carry signals between distributed parts."
    )
