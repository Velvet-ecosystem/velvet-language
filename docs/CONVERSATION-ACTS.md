# Conversation Acts

## Purpose

Velvet Language should distinguish what a human turn is doing before deciding how to respond.

The same words can serve different purposes: asking, correcting, teaching, confirming, disagreeing, requesting, joking, observing, or sounding like a command.

This layer classifies the conversational act. It does not grant authority.

## Initial Acts

- `question`
- `correction`
- `observation`
- `confirmation`
- `disagreement`
- `request`
- `teaching`
- `joke`
- `command_like`
- `unknown`

## Critical Boundary

A command-like utterance is a language observation only.

For example:

```text
"Unlock the doors."
```

may be classified as:

```yaml
act: command_like
execution_requested: true
authority_granted: false
```

Runtime, Court, authentication, capability, and physical-control policy remain external to Velvet Language.

Language must never convert imperative grammar into permission.

## Learning Relationship

Corrections and teaching turns may become `LanguageExperience` evidence.

Examples:

```text
"Actually, I'd call that sputtering."
"From now on, call that connector the founder plug."
```

The conversation-act layer may identify these as correction or teaching events. It still does not write permanent vocabulary directly.

Language experience remains proposal-only and must follow governed learning and memory boundaries.

## Conservative Interpretation

Initial interpretation is intentionally bounded.

Low confidence should remain visible. Ambiguous acts should be treated as uncertain rather than upgraded into stronger claims.

Future versions may combine:

- current conversation goal
- reference resolution
- speaker identity and scope
- recent turn history
- learned language patterns
- prosody or other audio cues

Those sources may improve interpretation, but none may grant authority through language classification.
