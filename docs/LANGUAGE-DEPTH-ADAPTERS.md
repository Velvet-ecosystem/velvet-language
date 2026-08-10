# Language Depth Adapters

## Purpose

These adapters deepen Velvet's conversational behavior without moving cognition, memory, authority, or capability truth into `velvet-language`.

The rule is simple:

> Language may express, simplify, personalize, and explain verified understanding. It does not become the owner of that understanding.

## Pre-implementation conflict check

Before adding these modules, the relevant ecosystem owners were checked.

Existing ownership already includes:

- bounded curiosity in `velvet-ai-core`
- reflection and receipt review in `velvet-ai-core`
- pattern formation and memory associations in `velvet-ai-core`
- verified capability context and authorization separation in `velvet-runtime`
- canonical memory and governed learning outside `velvet-language`

Therefore this repository adds expression adapters only.

## Question realization

`question_realization.py` consumes an upstream question candidate.

It does not decide that Velvet is curious and it does not decide that the moment is appropriate for speech. An explicit `speech_approved` input is required before wording is emitted.

This preserves the Core rule that curiosity may create a question candidate while remaining silent itself.

## Reflection expression

`reflection_expression.py` converts a verified reflection finding into human-facing wording.

It does not review receipts, compare outcomes, update confidence, write memory, or apply learning. Those decisions remain upstream.

A reflection that has not been approved for speech remains silent.

## Capability expression

`capability_expression.py` turns verified body or Runtime capability state into truthful language.

It distinguishes availability from authorization. A proposed capability is explicitly described as still requiring authorization, and the adapter rejects inputs that claim Language itself granted actuation.

This lets Velvet say what she can, cannot, or cannot yet verify without creating a second capability registry.

## Concept lexicon

`concept_lexicon.py` owns terminology only.

A lexical concept may contain:

- a stable external concept identifier
- technical wording
- common wording
- owner-preferred wording
- synonyms

It must not contain causal truth, diagnostic rules, physical relationships, authority, or canonical memory. Those belong to the systems that define and learn the concept.

## Analogy realization

`analogy_realization.py` turns an already verified relationship into an explanatory comparison.

It cannot invent the relationship. If `relationship_verified` is false, no analogy is emitted.

This allows approachable explanations while keeping conceptual truth upstream.

## Boundary summary

```text
Core curiosity --------> approved question candidate ---\
Core reflection -------> verified reflection finding ----+--> velvet-language --> expression
Runtime/body truth ----> capability state ---------------+
Core/domain meaning ---> concept id + verified relation --/
```

Language owns the right-hand side of that boundary.

It never gains authority, canonical memory ownership, autonomous curiosity, reflection ownership, world-model ownership, or actuation rights through these adapters.
