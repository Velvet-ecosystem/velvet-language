# Grounded Core Conversation Replies

Status: grounded Core-to-Language conversation return path with bounded evidence expression.

## Purpose

`ConversationGateway` can accept an optional `meaning_resolver`. The resolver receives the exact normalized `velvet.language.conversation.turn` event already produced for terminal, UI, and speech-transcript input. It returns a `velvet.core.conversation.meaning` event containing structured verified meaning.

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
          +--> exact evidence + source refs retained
          |
          v
 natural deterministic expression
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

Language owns expression only. It may simplify presentation syntax or turn an explicit Markdown heading/list into a sentence, but it does not infer synonyms, add facts, change trust, promote retrieval into belief, or grant authority.

## Response Kinds

### `fact`

Carries a verified fact id, scalar value, optional unit, confidence, qualifiers, and source references. Language owns the wording. Known fact ids receive clean labels; unknown fact ids are deterministically humanized rather than discarded.

### `evidence`

Carries one bounded Library passage, a source label, qualifiers, and stable source references. The exact evidence text remains attached to the grounded expression and conversation reply while Language produces a more natural human-facing sentence.

For example, a flattened retrieved fragment such as:

```text
## Core principles - Local first. - Provenance before confidence. - Preserve the source.
```

may be spoken as:

```text
According to Velour Library README, core principles are local first; provenance before confidence; and preserve the source.
```

The wording changes; the evidence payload and provenance do not.

Stale or superseded source posture is still disclosed explicitly.

### `synthesis`

Carries two or three aligned Library passages plus their source labels and stable source references. Corroborated evidence may receive the same bounded presentation cleanup. Conflicting or mixed evidence stays visibly unresolved rather than being collapsed into a convenient answer.

### `unavailable`

Produces a truthful no-answer response. It does not fabricate a likely value.

### `acknowledge`

Produces a bounded acknowledgement.

### `authority_required`

Explains that Runtime authorization is still required. It does not claim that authorization was granted.

## Provenance Retention

`GroundedConversationExpression` and `ConversationReply` retain read-only grounding metadata separately from display text:

- `source_refs`
- `source_label` or `source_labels`
- exact `evidence_texts`
- grounding `qualifiers`

This allows Runtime or a future UI to expose "why Velvet said that" without reparsing the sentence or treating the realized wording as canonical evidence.

## Action-Like Turns

If Core has no grounded answer for an action-like turn, `ConversationGateway` preserves the existing Language baseline that explicitly says Runtime still has to authorize the action. A lack of grounding must never accidentally weaken the authority boundary.

## Shared Modality

The same grounded result is used for typed text and speech transcripts. Written input displays the answer. Speech-transcript input may additionally request speech output when the current Language context permits it.

This keeps Velvet to one conversation path rather than maintaining separate text and voice brains.
