from velvet_language.experience import correction_experience
from velvet_language.experience_evaluator import evaluate_experiences


def test_single_correction_does_not_promote():
    exp = correction_experience(
        experience_id="exp-1",
        concept="engine_combustion_instability",
        observed_expression="running irregularly",
        candidate_expression="sputtering",
        source_role="owner",
        confidence=0.95,
        evidence_refs=("receipt-1",),
    )
    assert evaluate_experiences([exp]) == ()


def test_repeated_high_confidence_correction_becomes_candidate_only():
    experiences = [
        correction_experience(
            experience_id="exp-1",
            concept="engine_combustion_instability",
            observed_expression="running irregularly",
            candidate_expression="sputtering",
            source_role="owner",
            confidence=0.9,
            evidence_refs=("receipt-1",),
        ),
        correction_experience(
            experience_id="exp-2",
            concept="engine_combustion_instability",
            observed_expression="irregular firing",
            candidate_expression="sputtering",
            source_role="owner",
            confidence=0.95,
            evidence_refs=("receipt-2",),
        ),
    ]
    (candidate,) = evaluate_experiences(experiences)
    assert candidate.candidate_expression == "sputtering"
    assert candidate.support_count == 2
    assert candidate.requires_core_learning_review is True
    assert candidate.requires_external_promotion is True
    assert candidate.change_applied is False
    assert candidate.grants_authority is False


def test_low_confidence_repetition_does_not_promote():
    experiences = [
        correction_experience(
            experience_id="exp-1",
            concept="network_latency",
            observed_expression="slow",
            candidate_expression="lagging",
            source_role="guest",
            confidence=0.4,
        ),
        correction_experience(
            experience_id="exp-2",
            concept="network_latency",
            observed_expression="slow",
            candidate_expression="lagging",
            source_role="guest",
            confidence=0.5,
        ),
    ]
    assert evaluate_experiences(experiences) == ()
