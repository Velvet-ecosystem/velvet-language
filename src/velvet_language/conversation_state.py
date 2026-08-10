from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping, Tuple


@dataclass(frozen=True)
class ConversationState:
    """Short-lived turn state for coherent conversation.

    This is not canonical memory. It tracks the active conversational surface
    and may be discarded without changing identity or long-term memory.
    """

    conversation_id: str
    current_subject: str | None = None
    current_goal: str | None = None
    unresolved_questions: Tuple[str, ...] = ()
    recent_entities: Tuple[str, ...] = ()
    turn_count: int = 0
    metadata: Mapping[str, str] = field(default_factory=dict)

    def with_turn(
        self,
        *,
        subject: str | None = None,
        goal: str | None = None,
        unresolved_questions: Tuple[str, ...] | None = None,
        entities: Tuple[str, ...] = (),
    ) -> "ConversationState":
        recent = list(self.recent_entities)
        for entity in entities:
            entity = entity.strip()
            if entity and entity not in recent:
                recent.append(entity)
        recent = recent[-8:]

        return replace(
            self,
            current_subject=self.current_subject if subject is None else subject,
            current_goal=self.current_goal if goal is None else goal,
            unresolved_questions=(
                self.unresolved_questions
                if unresolved_questions is None
                else unresolved_questions
            ),
            recent_entities=tuple(recent),
            turn_count=self.turn_count + 1,
        )

    def resolve_question(self, question_id: str) -> "ConversationState":
        remaining = tuple(q for q in self.unresolved_questions if q != question_id)
        return replace(self, unresolved_questions=remaining)

    def clear_goal(self) -> "ConversationState":
        return replace(self, current_goal=None)
