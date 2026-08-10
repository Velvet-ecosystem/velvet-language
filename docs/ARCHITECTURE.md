# Velvet Language Architecture

## Boundary

`velvet-language` consumes structured, trusted meaning. It does not infer raw physical truth directly from sensors and it does not grant authority to act.

A typical input should already describe the verified or bounded state:

```json
{
  "event": "vehicle.can.connection_lost",
  "facts": {
    "subsystem": "vehicle_can",
    "state": "disconnected",
    "recovery_attempted": true,
    "recovery_successful": false
  },
  "confidence": 1.0,
  "severity": "warning",
  "mode": "degraded",
  "audience": "owner"
}
```

The language layer turns that meaning into an expression plan and then a rendered utterance.

## Pipeline

```text
Meaning Packet
    |
    v
Intent Builder
    |
    v
Conversation Planner
    |
    v
Policy Gate
    |
    v
Response Selector
    |
    +----> Deterministic fallback
    |
    +----> Approved template family
    |
    +----> Grammar realization
    |
    +----> Optional model adapter
    |
    v
Rendered Expression
    |
    +----> text
    +----> speech request
    +----> UI message
    +----> receipt metadata
```

## Components

### Meaning Packet
Carries the facts and evidence already established elsewhere. Language must not silently upgrade `unknown` or `inferred` facts into verified claims.

### Intent Builder
Determines the communicative purpose, for example:

- inform
- warn
- confirm
- clarify
- request
- explain
- acknowledge
- refuse
- recover
- summarize
- remain silent

### Conversation Planner
Maintains the current conversational goal and decides whether this turn should speak now, defer, ask, answer, summarize, or remain silent.

### Policy Gate
Constrains language according to severity, environment, audience, privacy, and runtime mode. This layer decides how much generative freedom is permitted.

### Response Selector
Chooses a stable response family and variant using event, intent, severity, audience, mode, recent utterances, and policy.

### Language Realizer
Renders the selected semantic content as human language. Implementations may include deterministic strings, templates, grammar rules, or replaceable model adapters.

### Fallback Engine
Must remain available when high-level language components fail. It favors simple, auditable language over naturalness.

## Output Contract

A rendered expression should be representable as:

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

The output may request speech or display, but transport and playback remain outside this repository.

## Failure Behavior

- Missing optional model: fall back to grammar, templates, then deterministic language.
- Missing response family: use generic deterministic fallback based on severity and event class.
- Invalid meaning packet: refuse to fabricate a sentence; produce a bounded error expression when safe.
- Conflicting facts: state uncertainty or conflict rather than choosing whichever phrase sounds best.
- Repeated warning: repetition policy may shorten follow-up messages without weakening the warning.

## Dependency Direction

Language may depend on stable contracts from Runtime, Core, Persona Continuity, and Receipts. Those systems must not depend on `velvet-language` to establish truth or authority.

This keeps language replaceable and prevents fluent output from becoming a hidden control path.
