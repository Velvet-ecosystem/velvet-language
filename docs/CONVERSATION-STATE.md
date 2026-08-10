# Conversation State

Velvet Language needs enough short-lived context to keep a conversation coherent without confusing working turn state with canonical memory.

## Purpose

Conversation state tracks the active subject, current conversational goal, unresolved questions, recent entities, and turn count.

It exists so follow-ups such as:

> "What about the spark plugs?"

can remain attached to an already-established engine-diagnosis conversation without forcing the user to restate the full context.

## Boundary

Conversation state is working context only.

It is not:

- canonical memory
- identity continuity
- authority
- a receipt ledger
- a substitute for Persona Continuity
- a mechanism for silently retaining private conversation forever

Long-term retention remains subject to the existing memory, privacy, provenance, and admission boundaries elsewhere in the Velvet ecosystem.

## Initial State Shape

```text
conversation_id
current_subject
current_goal
unresolved_questions
recent_entities
turn_count
metadata
```

## Follow-Up Resolution

When a new turn omits an explicit subject, Language may preserve the current subject if the turn remains compatible with the active conversational goal.

Recent entities provide bounded references for pronouns and shorthand such as:

- it
- that
- the other one
- those plugs
- the network

The initial implementation does not guess ambiguous references. A later resolver may propose a likely referent with confidence and request clarification when ambiguity remains material.

## Lifecycle

Conversation state should be cheap to create, update, and discard.

A conversation ending does not automatically promote its turn state into long-term memory. If an interaction deserves retention, a separate governed memory or episode path must decide that.
