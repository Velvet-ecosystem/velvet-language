from velvet_language.goals import ConversationGoal, GoalStatus, update_goal


def test_goal_completes_when_required_slots_resolved():
    goal = ConversationGoal(
        goal_id="diagnose-engine",
        description="Understand engine hesitation",
        required_slots=("symptom", "severity"),
    )
    goal = update_goal(goal, newly_resolved_slots=("symptom",))
    assert goal.status == GoalStatus.ACTIVE
    assert goal.is_complete is False
    goal = update_goal(goal, newly_resolved_slots=("severity",))
    assert goal.status == GoalStatus.SATISFIED
    assert goal.is_complete is True


def test_blocked_goal_is_not_complete():
    goal = ConversationGoal(goal_id="clarify", description="Resolve ambiguous reference")
    goal = update_goal(goal, blocked=True)
    assert goal.status == GoalStatus.BLOCKED
    assert goal.is_complete is False


def test_explicit_completion_can_finish_slotless_goal():
    goal = ConversationGoal(goal_id="chat", description="Answer owner question")
    goal = update_goal(goal, explicit_completion=True)
    assert goal.status == GoalStatus.SATISFIED
    assert goal.is_complete is True
