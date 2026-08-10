from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class GoalStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    SATISFIED = "satisfied"
    ABANDONED = "abandoned"


@dataclass(frozen=True)
class ConversationGoal:
    goal_id: str
    description: str
    required_slots: Tuple[str, ...] = ()
    resolved_slots: Tuple[str, ...] = ()
    status: GoalStatus = GoalStatus.ACTIVE
    evidence_refs: Tuple[str, ...] = ()

    @property
    def missing_slots(self) -> Tuple[str, ...]:
        resolved = set(self.resolved_slots)
        return tuple(slot for slot in self.required_slots if slot not in resolved)

    @property
    def is_complete(self) -> bool:
        return self.status == GoalStatus.SATISFIED and not self.missing_slots


def update_goal(
    goal: ConversationGoal,
    *,
    newly_resolved_slots: Tuple[str, ...] = (),
    explicit_completion: bool = False,
    blocked: bool = False,
    abandoned: bool = False,
    evidence_refs: Tuple[str, ...] = (),
) -> ConversationGoal:
    if abandoned:
        next_status = GoalStatus.ABANDONED
    elif blocked:
        next_status = GoalStatus.BLOCKED
    else:
        merged_resolved = tuple(dict.fromkeys((*goal.resolved_slots, *newly_resolved_slots)))
        required = set(goal.required_slots)
        complete_by_slots = bool(required) and required.issubset(set(merged_resolved))
        next_status = GoalStatus.SATISFIED if (explicit_completion or complete_by_slots) else GoalStatus.ACTIVE
        return ConversationGoal(
            goal_id=goal.goal_id,
            description=goal.description,
            required_slots=goal.required_slots,
            resolved_slots=merged_resolved,
            status=next_status,
            evidence_refs=tuple(dict.fromkeys((*goal.evidence_refs, *evidence_refs))),
        )

    return ConversationGoal(
        goal_id=goal.goal_id,
        description=goal.description,
        required_slots=goal.required_slots,
        resolved_slots=goal.resolved_slots,
        status=next_status,
        evidence_refs=tuple(dict.fromkeys((*goal.evidence_refs, *evidence_refs))),
    )
