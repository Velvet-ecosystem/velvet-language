# Conversation Planner

The conversation planner decides whether Velvet should communicate, what the immediate communication goal is, and how constrained the resulting expression must be.

It does not write prose and it does not decide physical action.

## Inputs

The planner may consume bounded conversational metadata such as:

- verified meaning packet
- severity
- audience
- active mode
- whether the user is already speaking
- whether the event was recently communicated
- whether the user asked an explicit question
- whether the user's intent is ambiguous

## Outputs

The planner emits a conversation plan containing:

- goal
- speak / do-not-speak decision
- display / do-not-display decision
- interruption permission
- desired response length
- clarification requirement
- stable rationale code

## Restraint Doctrine

Silence is a valid output.

Velvet should not narrate ordinary state changes merely because she can observe them. Repeated informational events should normally be suppressed unless the user asks, the state meaningfully changes, or policy requires disclosure.

Warnings may be displayed without immediately interrupting speech. Critical and emergency states may interrupt because consequence outranks conversational politeness.

## Severity Posture

### Casual

Flexible language is permitted when grounded in known context. No system state may be invented for conversational effect.

### Informational

Prefer concise, useful communication. Repetition suppression is active.

### Warning

Use constrained language. Avoid talking over the user when safe to defer briefly. Display remains available even when speech is deferred.

### Critical

Speak and display. Interrupt. Keep wording minimal and deterministic or catalog-bound.

### Emergency

Speak and display immediately. Interrupt. Use deterministic, tested phrasing. No stylistic embellishment.

## Conversation Goal Principle

Velvet should generate toward a goal rather than merely predicting a next sentence.

Examples include:

- answer_user
- clarify_user_intent
- communicate_warning_state
- communicate_critical_state
- communicate_emergency_state
- avoid_redundant_notification
- inform_when_useful

The goal remains visible to tests and future receipts so that language behavior can be reviewed independently from the words ultimately rendered.
