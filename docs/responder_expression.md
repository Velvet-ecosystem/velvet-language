# Responder Expression

`velvet-language` provides a deterministic responder-expression adapter for incident-scoped answer plans that have already been admitted by the owning medical/safety policy.

This layer does not decide whether an incident exists, whether a medical fact is true, whether disclosure is permitted, whether a responder is authorized, or whether a requested physical action may execute.

## Boundary

```text
Medical Mobility / Temperance
  -> active incident
  -> approved responder answer plan
  -> truth class + fact + disclosure outcome
  -> velvet-language responder expression
  -> RenderedExpression
  -> canonical speech-expression handoff
  -> Event Protocol / Runtime
  -> Audio Studio
```

The responder expression path uses the same `language.expression.speech_requested` handoff as ordinary Velvet speech. It does not open a direct TTS, microphone, phone, network, or speaker path.

## Truth preservation

The adapter preserves four upstream truth outcomes:

- `known`: state the approved fact directly;
- `inferred`: explicitly mark the answer as based on available evidence;
- `stale`: explicitly identify the answer as last-known and preserve freshness qualifiers;
- `unavailable`: say that Velvet cannot verify the answer.

Language cannot promote `inferred` or `stale` into `known` for smoother conversation.

## Withheld information

A withheld answer cannot carry a value into the responder expression object.

If the upstream plan says `protected-channel-required`, Language may say that the information cannot be provided on the current channel. It does not reveal the protected value, source references, or internal disclosure metadata.

## Authority

Responder expression inputs require `authority=none`.

A responder asking for a consequential action is handled separately as a proposal to Runtime/Court/Safety Gate. This module does not convert action requests into commands and does not report an action as completed without measured outcome evidence from the owning execution path.

## Session introduction

A deterministic introduction is available for responder sessions:

> This is Velvet, the vehicle's automated local assistant. My occupant may be unable to respond. I can provide verified incident information and state when something is unknown.

The purpose is role clarity. Velvet does not impersonate the owner, dispatcher, emergency-service operator, or medical professional.

## Privacy

The serialized-plan adapter intentionally accepts only the expression fields it needs. Source references and unrelated disclosure internals are not copied into the spoken expression object.

Fact values are bounded to scalar text, numbers, or booleans. Structured raw records are rejected. Long text values are rejected rather than read aloud.

## Relationship to Medical Mobility

`velvet-medical-mobility` owns the incident-scoped responder fact planner and disclosure policy. Its simulation boundary establishes the active incident requirement, truth class, protected-channel requirement, and `authority=none` before the answer reaches Language.

Language owns only deterministic human wording and the normal authority-free speech-expression handoff.
