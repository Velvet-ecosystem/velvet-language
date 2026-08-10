# Sentence Frames

Sentence frames let Velvet realize many truthful utterances from a smaller set of approved language structures.

A frame is a mostly-finished sentence with typed slots supplied only from verified meaning.

Example:

```text
"Mister, the {subject} is {condition} a bit."
```

With verified slot values this may become:

```text
"Mister, the engine is sputtering a bit."
"Mister, the LAN is lagging a bit."
```

Frames are not free-form prompts. They are bounded language structures.

## Rules

1. Every required slot must be present before realization.
2. Slot values must come from trusted meaning packets or approved lexical maps.
3. Unknown values must never be guessed.
4. Critical and emergency messages should prefer deterministic fixed phrases over highly variable frames.
5. A frame may define allowed slot vocabularies, aliases, units, comparison operators, and optional clauses.
6. Realized language should retain a stable frame ID for receipts and tests.
7. Optional clauses may be omitted, but required truth may not be omitted merely for elegance.

## Example families

```yaml
id: observation.condition.small_change
frames:
  - "The {subject} is {condition} a bit."
  - "Mister, the {subject} is {condition} slightly."
slots:
  subject:
    type: entity
  condition:
    type: approved_condition
```

```yaml
id: observation.threshold.exceeded
frames:
  - "Mister, the {subject} is {state} more than {reference}."
  - "The {subject} is running {degree} above {reference}."
slots:
  subject:
    type: entity
  state:
    type: approved_state
  reference:
    type: measured_reference
  degree:
    type: degree_word
    optional: true
```

## Why frames matter

Frames give Velvet useful grammatical flexibility without requiring a generative model for every sentence. They also reduce the response catalog from thousands of near-duplicate finished sentences to reusable, testable structures.

The Language Organ should therefore use three increasingly flexible forms:

1. fixed approved phrases
2. sentence frames with bounded slots
3. generative realization when policy permits

The system must always be able to fall back toward the more constrained form.