# Velvet Language

> **The Language Organ transforms verified meaning into truthful human language.**

`velvet-language` is the language and conversation layer of the Velvet ecosystem.

It does not own sensors, canonical memory, cognition, authority, actuation, or audio hardware. It receives structured meaning and bounded context from trusted Velvet systems and turns them into human language for speech, text, UI surfaces, alerts, explanations, questions, and conversation.

## Core Doctrine

Velvet must remain capable of truthful communication even when no generative language model is available.

Language quality may degrade. Truthfulness must not.

Language is also developmental. Vocabulary, phrase preferences, sentence patterns, and conversational habits may improve through receipted experience, but `velvet-language` does not silently rewrite itself. Learning remains governed by `velvet-ai-core` plasticity and memory boundaries.

The capability ladder is:

1. deterministic emergency and critical phrasing
2. approved response families and templates
3. sentence frames and bounded grammar realization
4. conversation acts, goals, reference resolution, and response strategy
5. context-sensitive turn orchestration
6. grounded question, reflection, capability, lexical, and analogy realization
7. learned language competence promoted through governed Core review
8. optional local or remote language-model assistance

A language model may improve expression or provide temporary breadth. It must never become the sole owner of Velvet's ability to communicate.

## Responsibilities

- transform verified meaning into human-readable language
- interpret bounded conversational acts without granting authority
- track short-lived conversational state and goals
- resolve references conservatively and request clarification when ambiguous
- select response strategy according to act, audience, severity, urgency, mode, confidence, and recent context
- construct language from approved response families, sentence frames, and grammar
- realize upstream-approved curiosity questions without owning curiosity
- express verified reflection without performing reflection or learning
- express verified capability state without turning availability into authorization
- maintain lexical terminology for externally defined concepts
- construct analogies only from verified conceptual relationships
- express uncertainty without bluffing
- avoid needless repetition and permit intentional silence
- provide deterministic fallback language during degraded operation
- constrain warning, critical, and emergency phrasing
- create proposal-only language-experience evidence for governed learning review
- expose stable identifiers and policy metadata for receipts and testing
- remain provider-neutral

## Non-Responsibilities

This repository does not:

- decide physical actions
- grant Runtime or Court authority
- own canonical memory admission or storage
- own persona continuity
- own Core learning or plasticity
- own curiosity, reflection, pattern formation, or world-model truth
- invent conceptual relationships for analogies
- interpret raw sensors
- operate CAN or vehicle hardware
- capture microphones or route speaker hardware
- issue canonical receipts
- publish public project communications
- fabricate facts to make language sound natural

## Architectural Boundary

```text
trusted meaning + bounded context
              |
              v
      conversation act
              |
              v
   references + turn goals
              |
              v
      response strategy
              |
              v
     context constraints
              |
              v
 frames / grammar / catalog
              |
              v
      truthful expression
              |
              v
 speech request / text / UI
```

Meaning comes in. Language goes out.

Audio playback remains the responsibility of `velvet-audio-studio`. Operational authority remains the responsibility of `velvet-runtime` and Court.

## Grounded Depth Adapters

Some conversational depth begins elsewhere in the ecosystem and enters Language only for expression:

```text
Core curiosity --------> approved question candidate ---\
Core reflection -------> verified reflection finding ----+--> velvet-language --> expression
Runtime/body truth ----> capability state ---------------+
Core/domain meaning ---> concept id + verified relation --/
```

The adapters never acquire the authority or cognitive ownership of their upstream source.

## Developmental Loop

```text
expression
   -> human/system outcome
   -> language experience
   -> evidence accumulation
   -> promotion candidate
   -> governed Core review
   -> future language competence
```

A correction, preference, or successful phrase is evidence, not an immediate permanent rewrite.

## Safety Principle

Generative freedom decreases as consequence increases.

Casual conversation may be flexible. Informational messages remain grounded. Warnings use constrained language. Critical and emergency messages become deterministic or nearly deterministic.

Velvet must never become poetic when the human needs precision.

## Repository Shape

```text
.
├── catalogs/
│   ├── conversation/
│   ├── frames/
│   └── system/
├── docs/
├── schemas/
├── src/velvet_language/
│   ├── analogy_realization.py
│   ├── capability_expression.py
│   ├── concept_lexicon.py
│   ├── conversation_acts.py
│   ├── conversation_state.py
│   ├── context_strategy.py
│   ├── experience.py
│   ├── experience_evaluator.py
│   ├── fallback.py
│   ├── frames.py
│   ├── goals.py
│   ├── orchestrator.py
│   ├── planner.py
│   ├── question_realization.py
│   ├── reference_resolution.py
│   ├── reflection_expression.py
│   ├── response_strategy.py
│   └── selector.py
└── tests/
```

## Relationship to Other Velvet Repositories

- `velvet-ai-core`: cognition, canonical memory, curiosity, reflection, patterns, learning, and governed plasticity
- `velvet-persona-continuity`: bounded persona policy and receipted recall context
- `velvet-runtime`: verified identity and capability context, authority, Court, coordination, and execution boundary
- `velvet-receipts`: canonical append-only evidence
- `velvet-audio-studio`: microphone capture, transcription front end, channel routing, and voice playback
- `velvet-communications`: outward-facing project communication

`velvet-language` owns expression, not the truth sources that feed it and not the authority that may follow from a request.

## Status

Foundation plus grounded depth-adapter stage. No Runtime, Court, memory, learning, receipt, curiosity, reflection, world-model, or actuation authority is granted by this repository.
