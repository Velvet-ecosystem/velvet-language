# Grounded Core Conversation Replies

Status: first Core-to-Language conversation return path.

## Purpose

`ConversationGateway` can now accept an optional `meaning_resolver`. The resolver receives the exact normalized `velvet.language.conversation.turn` event already produced for terminal, UI, and speech-transcript input. It returns a `velvet.core.conversation.meaning` event containing structured verified meaning.

Language then validates and realizes that meaning into human-facing text.

```text
text / UI / Vosk transcript
          |
          v
 ConversationGateway
          |
          | velvet.language.conversation.turn
          v
 grounded Core resolver
          |
          | velvet.core.conversation.meaning
          v
 grounded_conversation.py
          |
          v
 display text / optional speech handoff
```

## Boundary

Core meaning is not trusted merely because it came from Core. Language validates:

- event type and schema version
- conversation id, turn id, and turn number correlation
- response kind
- confidence bounds
- scalar fact values
- qualifier and source-reference shapes
- `authority=none`
- `grants_authority=false`
- `grants_execution=false`
- `grants_actuation=false`

Any mismatch fails closed instead of being silently presented to the user.

## Response Kinds

### `fact`

Carries a verified fact id, scalar value, optional unit, confidence, qualifiers, and source references. Language owns the wording. Known fact ids receive clean labels; unknown fact ids are deterministically humanized rather than discarded.

### `unavailable`

Produces a truthful no-answer response. It does not fabricate a likely value.

### `acknowledge`

Produces a bounded acknowledgement.

### `authority_required`

Explains that Runtime authorization is still required. It does not claim that authorization was granted.

## Action-Like Turns

If Core has no grounded answer for an action-like turn, `ConversationGateway` preserves the existing Language baseline that explicitly says Runtime still has to authorize the action. A lack of grounding must never accidentally weaken the authority boundary.

## Shared Modality

The same grounded result is used for typed text and speech transcripts. Written input displays the answer. Speech-transcript input may additionally request speech output when the current Language context permits it.

This keeps Velvet to one conversation path rather than maintaining separate text and voice brains.
