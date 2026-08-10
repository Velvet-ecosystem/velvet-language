import pytest

from velvet_language.experience import LanguageExperience, correction_experience


def test_correction_experience_is_proposal_only():
    experience = correction_experience(
        experience_id="lang-exp-001",
        concept="engine.combustion_instability",
        observed_expression="running irregularly",
        candidate_expression="sputtering",
        source_role="owner",
        confidence=0.91,
        context={"domain": "vehicle", "subsystem": "engine"},
        evidence_refs=("event-123", "receipt-456"),
    )

    assert experience.kind == "correction"
    assert experience.proposal_only is True
    assert experience.change_applied is False
    assert experience.grants_authority is False


def test_language_experience_rejects_self_application():
    with pytest.raises(ValueError):
        LanguageExperience(
            experience_id="lang-exp-002",
            kind="preference",
            concept="network.latency",
            candidate_expression="lagging",
            confidence=0.8,
            change_applied=True,
        )


def test_language_experience_rejects_authority():
    with pytest.raises(ValueError):
        LanguageExperience(
            experience_id="lang-exp-003",
            kind="correction",
            concept="runtime.state",
            candidate_expression="degraded",
            confidence=0.8,
            grants_authority=True,
        )


def test_confidence_is_bounded():
    with pytest.raises(ValueError):
        LanguageExperience(
            experience_id="lang-exp-004",
            kind="correction",
            concept="engine.sound",
            candidate_expression="knocking",
            confidence=1.2,
        )
