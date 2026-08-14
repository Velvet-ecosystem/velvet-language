# Self-Health Expression

Velvet's self-health speech is part of the broader reflection protocol: the system can assess its own verified operating condition and communicate meaningful losses or recoveries to its human.

This does **not** mean the literal `velvet-ai-core` receipt reviewer owns system health. The boundary remains deliberately split:

```text
body / organ evidence
        |
        v
standard HealthEvent
        |
        v
Velvet Runtime admission and health truth
        |
        v
self-health / reflection-protocol bridge
        |
        v
velvet-language deterministic expression
        |
        v
language.expression.speech_requested
        |
        v
Audio Studio delivery
```

## Core rule

**The body establishes the truth. Language explains it.**

Language must never infer that a subsystem is sick from odd conversation, low answer quality, or a guess. It may only express an admitted health transition supplied by a trusted Runtime/body source.

## Automatic wording

`self_health_expression.py` maps verified transitions into bounded owner-facing language.

Examples:

- degraded microphone path: `Mister, I'm not feeling quite right. I'm having trouble with part of my hearing.`
- failed GNSS path: `Mister, something's wrong. I've lost my position awareness.`
- recovered vehicle network: `Mister, I'm feeling better. My vehicle connection is working normally again.`

The exact HealthEvent remains available for follow-up explanation. Raw diagnostic strings, device paths, errno values, and implementation details are not automatically read aloud.

## Silence policy

Normal startup health is intentionally quiet. An initial `ONLINE`, `AVAILABLE`, or healthy state does not produce a self-congratulatory announcement.

Meaningful degradation, failure, unavailability, staleness, and recovery may speak. Runtime also suppresses near-duplicate fault announcements so a noisy producer cannot make Velvet repeatedly say the same warning.

## Severity

Health severity is converted conservatively into the existing speech severity vocabulary:

- `INFO` / `NOTICE` -> `informational`
- `WARNING` -> `warning`
- `ERROR` / `CRITICAL` / `FATAL` -> `critical`
- `EMERGENCY` -> `emergency`

Failure has a minimum speech severity of `warning`. Critical and emergency self-health expressions may request interruption. Audio Studio still owns acoustic priority, routing, synthesis, and hardware.

## No new authority

Self-health speech grants no command, Court, execution, or actuation authority. The resulting speech draft uses the existing `velvet.speech-expression.v1` contract and remains `authority: none`.

## Manual self-check

A future or existing owner-invoked command such as "Velvet, check yourself" can use the same health truth for a deeper report. It is complementary to this automatic path, not a replacement for it. Velvet should not require Mister to notice degraded behavior before she reports a verified loss.
