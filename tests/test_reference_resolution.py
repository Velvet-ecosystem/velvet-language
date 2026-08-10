from velvet_language.reference_resolution import ReferenceCandidate, resolve_reference


def test_resolves_clear_recent_reference():
    result = resolve_reference(
        "it",
        [
            ReferenceCandidate("engine", "engine", recency_rank=0, semantic_match=0.9, role_match=1.0),
            ReferenceCandidate("battery", "battery", recency_rank=3, semantic_match=0.2, role_match=0.0),
        ],
    )
    assert result.resolved_entity_id == "engine"
    assert result.requires_clarification is False


def test_ambiguous_reference_requests_clarification():
    result = resolve_reference(
        "that one",
        [
            ReferenceCandidate("left_module", "left module", recency_rank=0, semantic_match=0.8, role_match=0.5),
            ReferenceCandidate("right_module", "right module", recency_rank=0, semantic_match=0.78, role_match=0.5),
        ],
    )
    assert result.resolved_entity_id is None
    assert result.ambiguous is True
    assert result.requires_clarification is True


def test_no_candidates_never_invents_referent():
    result = resolve_reference("it", [])
    assert result.resolved_entity_id is None
    assert result.requires_clarification is True
