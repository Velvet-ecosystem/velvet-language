# Velvet Language Architecture

## Boundary

`velvet-language` consumes structured, trusted meaning and bounded conversational context. It does not infer raw physical truth directly from sensors, own canonical memory, perform Core learning, grant authority, issue canonical receipts, or control audio hardware.

A typical system-originated input should already describe the verified or bounded state. A human-originated turn may additionally carry short-lived conversation state and reference candidates supplied by the surrounding body.

## Turn Pipeline

```text
human/system turn
      |
      v
conversation-act interpretation
      |
      v
reference resolution + ephemeral state
      |
      v
conversation goal
      |
      v
response strategy
      |
      v
context strategy
      |
      v
frames / grammar / response catalogs
      |
      v
response selection
      |
      v
truthful expression
      |
      +----> text / UI
      +----> speech request to Audio Studio
      +----> receipt metadata for canonical receipt producer
```

`orchestrator.py` composes the language-side turn stages. It cannot grant Runtime or Court authority, admit canonical memory, apply learning, execute an action, or play audio.

## Developmental Loop

```text
expression
  -> human/system outcome
  -> language experience
  -> bounded evidence accumulation
  -> language promotion candidate
  -> velvet-ai-core governed learning review
  -> approved future language competence
```

Language experience is evidence only. A correction or repeated preference does not rewrite permanent language state by itself.

## Ownership Split

### Velvet AI Core

Core owns cognition, canonical memory responsibilities, shared conversational abstractions, reflection, learning, and governed plasticity.

Language owns only the concrete language-side realization of a live turn: ephemeral turn state, language goals, reference resolution, response strategy, and expression. Any state worth retaining beyond the live conversation must leave Language through the governed Core memory/learning boundary.

### Velvet Persona Continuity

Persona Continuity supplies bounded persona policy and eligible receipted recall context. Language may use that context to shape expression, but does not own identity, privacy admission, provenance, or recall authority.

### Velvet Runtime and Court

Runtime supplies verified operational context and owns the authority/execution path. A request or command-like sentence may cause Language to mark `requires_authority_check`, but Language cannot satisfy that check itself.

### Velvet Receipts

Language may expose response IDs, policy versions, source meaning references, and language-experience evidence. `velvet-receipts` remains the canonical receipt/evidence chain owner.

### Velvet Audio Studio

Language produces text or a speech request. Audio Studio owns microphone capture, transcription front-end behavior, audio routing, channel/resource booking, and playback.

### Velvet Communications

Language owns live conversational expression. `velvet-communications` owns outward-facing project communication such as journals, releases, media, documentation summaries, and public updates. Neither repository gains authority merely because it can produce words.

## Meaning and Truth

A Meaning Packet carries facts and evidence already established elsewhere. Language must not silently upgrade `unknown`, inferred, stale, conflicting, or simulated facts into verified claims.

## Conversation State

Conversation state is deliberately ephemeral. It may track:

- current subject
- current language-side goal
- unresolved questions
- recently referenced entities
- turn count

It is not canonical memory and may be discarded without changing Velvet's identity or long-term history.

## Conversation Acts

A turn may be interpreted as question, correction, observation, confirmation, disagreement, request, teaching, joke, command-like speech, or unknown. Interpretation describes language function only. It never grants operational authority.

## Response Strategy

Response strategy maps the language act into bounded next steps such as answer, acknowledge, clarify, compare, capture language experience, advance a goal, request an authority check, reply socially, or hold.

Humor is not treated as fact. Acknowledgement is not approval. Correction is not immediate learning.

## Context Strategy

Context may alter brevity, humor, interruption posture, clarification requirements, and whether nonessential speech should occur. Driving load, emergency posture, degraded operation, confidence, repeated speech, audience, and guest presence can shape delivery without changing underlying truth.

## Language Realization

Implementations may use:

1. deterministic approved language
2. response families
3. sentence frames with verified typed slots
4. grammar realization
5. learned language competence promoted through governed Core review
6. optional replaceable language-model assistance

A missing high-level component causes graceful degradation rather than silence.

## Output Contract

A rendered expression should be able to expose stable metadata such as:

```json
{
  "response_id": "vehicle.can.loss.degraded.owner.001",
  "text": "I've lost CAN communication, Mister. I'm entering degraded operation.",
  "speak": true,
  "display": true,
  "interrupt": true,
  "severity": "warning",
  "generator": "catalog",
  "policy_version": "0.1"
}
```

The output may request speech or display. Transport and physical playback remain outside this repository.

## Failure Behavior

- Missing optional model: use learned language, grammar, frames, catalogs, then deterministic fallback.
- Missing response family: use generic deterministic fallback based on verified severity and event class.
- Missing required frame slot: refuse to invent it.
- Ambiguous reference: ask for clarification rather than selecting an arbitrary referent.
- Invalid meaning packet: refuse to fabricate a sentence; produce a bounded error expression when safe.
- Conflicting facts: state uncertainty or conflict.
- Repeated low-value message: context policy may suppress it.
- Critical or emergency event: narrow language freedom and preserve deterministic wording.

## Dependency Direction

Language may consume stable contracts and bounded views from Core, Persona Continuity, Runtime, Receipts, and Audio Studio. Those systems must not depend on `velvet-language` to establish truth, identity, memory admission, authority, receipt validity, or audio resource ownership.

This keeps fluent output from becoming a hidden control path while still allowing the organs to cooperate as one body.
