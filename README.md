# Velvet Language

> **The Language Organ transforms verified meaning into truthful human language.**

`velvet-language` is the language and conversation layer of the Velvet ecosystem.

It does not own sensors, memory, reasoning, authority, actuation, or audio hardware. It receives structured meaning from trusted Velvet systems and renders that meaning into human language for speech, text, UI surfaces, alerts, explanations, questions, and conversation.

## Core Doctrine

Velvet must remain capable of truthful communication even when no generative language model is available.

Language quality may degrade. Truthfulness must not.

The repository therefore treats language generation as a layered capability:

1. deterministic emergency and critical phrasing
2. approved response families and templates
3. grammar and sentence realization
4. conversation planning and response selection
5. optional local or remote language-model adapters

A language model may improve expression. It must never become the sole owner of Velvet's ability to communicate.

## Responsibilities

- transform verified meaning into human-readable language
- select response families according to audience, severity, urgency, mode, and recent context
- manage conversational state and turn goals
- express uncertainty without bluffing
- support clarification and follow-up questions
- avoid needless repetition
- provide deterministic fallback language during degraded operation
- constrain warning, critical, and emergency phrasing
- expose stable response identifiers for receipts and testing
- remain provider-neutral

## Non-Responsibilities

This repository does not:

- decide physical actions
- grant runtime authority
- own canonical memory
- own persona continuity
- interpret raw sensors
- operate CAN or vehicle hardware
- own microphone capture or speaker routing
- publish public communications
- fabricate facts to make language sound natural

## Architectural Boundary

```text
trusted system state / verified meaning
                |
                v
        conversation intent
                |
                v
         response planner
                |
                v
         response selector
                |
                v
       language realization
                |
                v
      speech / text / UI output
```

Meaning comes in. Language goes out.

## Safety Principle

Generative freedom decreases as consequence increases.

Casual conversation may be flexible. Informational messages should remain grounded. Warnings should use constrained language. Critical and emergency messages should be deterministic or nearly deterministic.

Velvet must never become poetic when the human needs precision.

## Initial Layout

```text
.
├── docs/
│   ├── LANGUAGE-DOCTRINE.md
│   ├── ARCHITECTURE.md
│   └── RESPONSE-CATALOG-POLICY.md
├── schemas/
│   └── response-family.schema.json
├── catalogs/
│   └── system/
│       └── can.yaml
├── src/velvet_language/
│   ├── __init__.py
│   ├── models.py
│   ├── selector.py
│   └── fallback.py
└── tests/
    └── test_fallback.py
```

## Relationship to Other Velvet Repositories

- `velvet-ai-core`: cognition, reasoning, canonical memory responsibilities
- `velvet-persona-continuity`: bounded persona context and continuity
- `velvet-runtime`: operational state and enforcement
- `velvet-receipts`: canonical receipts
- `velvet-audio-studio`: microphone, routing, playback, and audio health
- `velvet-communications`: outward-facing project communication

`velvet-language` sits between verified meaning and outward expression.

## Status

Foundation stage. No runtime or actuation authority is granted by this repository.
