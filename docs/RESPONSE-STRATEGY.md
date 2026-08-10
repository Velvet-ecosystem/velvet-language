# Response Strategy

## Purpose

Conversation-act interpretation identifies what a turn appears to be doing. Response strategy decides what the Language Organ should do next.

This is a language-side planning boundary only. It does not grant Runtime authority, validate capabilities, execute commands, or convert conversational intent into physical permission.

## Strategy Types

- `answer`: provide grounded information when available
- `acknowledge`: show receipt of the turn without implying action approval
- `clarify`: ask for missing information when ambiguity materially affects meaning
- `compare`: examine competing interpretations, claims, or evidence
- `capture_experience`: prepare bounded language-learning evidence for governed review
- `advance_goal`: create or progress a conversational goal
- `request_authority_check`: hand an execution-shaped request toward the existing authority path
- `social_reply`: respond socially without treating the content as factual evidence
- `hold`: remain quiet or defer when no safe/useful strategy is available

## Act Mapping

### Question

Primary strategy: `answer`.

Questions may create or advance a conversational goal. If information is unavailable or reference resolution is ambiguous, the answer path may become clarification rather than invention.

### Request

Primary strategy: `acknowledge`.

Requests create or advance a conversational goal. If the request implies external execution, Language marks that an authority check is required. Acknowledgement does not mean the requested action is approved or underway.

### Command-like utterance

Primary strategy: `request_authority_check`.

The Language Organ recognizes imperative form but cannot grant authority. Runtime/Court/capability systems retain their existing responsibilities.

### Correction

Primary strategy: `acknowledge`.

Secondary strategy: `capture_experience`.

A correction may become a language-experience proposal, but not learned truth. Promotion remains governed and evidence-based.

### Teaching

Primary strategy: `acknowledge`.

Secondary strategy: `capture_experience`.

Teaching language is evidence of a proposed association or preference. It is not an instruction to rewrite protected language policy.

### Disagreement

Primary strategy: `compare`.

Disagreement should open comparison rather than automatic concession or contradiction. When the disagreement is under-specified, clarification may follow.

### Confirmation

Primary strategy: `acknowledge`.

Confirmation may advance an existing goal when it resolves a required field or decision point.

### Joke

Primary strategy: `social_reply`.

`Treat_as_fact` must remain false. Humor must never be silently promoted into canonical memory, system state, or operational evidence merely because it occurred in conversation.

### Observation

Primary strategy: `acknowledge`.

An observation can later feed other bounded interpretation paths, but a plain conversational statement is not automatically system truth.

## Key Boundaries

### Acknowledgement is not approval

"Understood" and "I heard you" are language acts. They do not mean:

- action authorized
- action executed
- safety gate passed
- Court approved
- capability granted
- physical state changed

### Humor is not evidence

A joke may affect social response and conversational rhythm. It cannot be treated as factual state without independent grounding.

### Correction is not immediate learning

A correction may generate a language-experience proposal. Repeated and sufficiently confident experience may become a promotion candidate. Actual learning remains governed by the existing Core plasticity boundary.

## Result

The Language Organ can now move from:

```text
What kind of turn was that?
```

to:

```text
What should I do conversationally because of it?
```

without confusing conversational behavior with operational authority.
