from velvet_language.conversation_state import ConversationState


def test_conversation_state_tracks_subject_goal_and_entities():
    state = ConversationState(conversation_id="conv-1")
    updated = state.with_turn(
        subject="engine",
        goal="diagnose rough running",
        unresolved_questions=("q1",),
        entities=("Tiburon", "engine"),
    )

    assert updated.current_subject == "engine"
    assert updated.current_goal == "diagnose rough running"
    assert updated.unresolved_questions == ("q1",)
    assert updated.recent_entities == ("Tiburon", "engine")
    assert updated.turn_count == 1


def test_follow_up_preserves_subject_when_not_replaced():
    state = ConversationState(
        conversation_id="conv-1",
        current_subject="engine",
        current_goal="diagnose rough running",
    )
    updated = state.with_turn(entities=("spark plugs",))

    assert updated.current_subject == "engine"
    assert updated.current_goal == "diagnose rough running"
    assert updated.recent_entities == ("spark plugs",)


def test_resolving_question_does_not_create_long_term_memory():
    state = ConversationState(
        conversation_id="conv-1",
        unresolved_questions=("q1", "q2"),
        metadata={"scope": "working"},
    )
    resolved = state.resolve_question("q1")

    assert resolved.unresolved_questions == ("q2",)
    assert resolved.metadata["scope"] == "working"
    assert not hasattr(resolved, "canonical_memory")
