# Beginner Flow Headless Comparison — Architecture-First vs Compressed vs Quick Draft

**Date:** 2026-10-03  
**Scope:** product ergonomics only  
**Branch:** feat/beginner-quick-draft-loop

## Question

How much author-facing ceremony occurs before the writer can react to prose?

This comparison is deliberately mechanical. It does **not** claim that fewer
interactions are automatically better, nor that a headless trace establishes
creative quality, ownership, joy, confidence, or preference.

## Conditions

| Condition | Designed path to first prose | Visible interactions to prose |
|---|---|---:|
| A — corrected pre-compression Beginner | premise → interpretation → direction select/accept → Identity → three Structure choices/review → outline approve → Chapter plan approve → scene plan approve → handoff → draft → review | 22 |
| B — compressed Beginner | premise → Explore → interpretation → Direction → story core → recommended story shape → Plan Chapter 1 → Draft Chapter 1 | 8 |
| C — Quick Draft | premise + first-scene intent → scene generation | 2 |

### What C defers

Quick Draft does not make the missing decisions disappear. It defers them until
the author has concrete prose to react to.

Before prose, C performs **zero explicit acceptance actions**.

Its temporary scaffold is marked `inferred_provisional` and does not create
accepted root Story Identity, Structure, Bible, Chapter, or final prose.

## Inference-boundary stress

The prototype is intentionally tested with four premise families:

1. mystery with named characters;
2. character-driven contemporary premise;
3. speculative hook;
4. intentionally vague premise with no named protagonist, genre, or location.

The vague case surfaced an important correction during implementation:
provisional scaffolding must not invent a fake POV label or location merely to
complete a schema.

The Quick Draft scene plan therefore leaves POV and location blank when the
author did not establish them. The Bard still receives the premise and
first-scene intent as the controlling creative evidence.

## Post-draft bridge

Condition C is only a useful product path if it can re-enter Auteur without
punishing the writer for discoveries made during drafting.

The integrated branch therefore pairs Quick Draft with:

~~~text
draft
-> edit freely
-> What did we discover?
-> keep writing or Shape this story
~~~

and the normal Chapter path now pairs review with:

~~~text
Auteur noticed the story changed while you were writing
-> Keep draft & reconcile
-> Keep as intentional divergence
-> Revise to match plan
~~~

This is the same product rule applied before and after prose:

> The author decides meaning; Auteur manages the machinery.

## Runtime probe

Run:

~~~text
python scripts/quick_draft_product_probe.py --project .
~~~

for the mechanical comparison and scenario manifest.

Run:

~~~text
python scripts/quick_draft_product_probe.py --project . --live
~~~

to dogfood all four premises through the currently configured provider.

The live run records:

- time to first prose;
- whether the 30-second target was met;
- output length;
- provider;
- provisional authority state.

It deliberately does not manufacture qualitative scores.

## Evidence ceiling

Repository/static evidence can establish:

- designed interaction counts;
- exact author inputs;
- number of acceptance actions before prose;
- provisional/accepted artifact boundaries;
- whether editing and discovery escape hatches exist;
- whether review freshness is bound to exact draft content.

A live provider probe can additionally establish real latency and inspectable
prose output for those scenarios.

Only real-author observation can establish:

- whether Quick Draft feels liberating or reckless;
- whether inferred scaffolding changes the writer's intent;
- whether the writer feels ownership;
- whether post-draft reconciliation feels helpful;
- whether the author prefers A, B, or C.

## Selected continuation

The integrated prototype keeps both entry tempos:

~~~text
Explore this story
~~~

for writers who want interpretation and shaping first, and

~~~text
Start writing now
~~~

for writers who want concrete prose first.

Neither path silently accepts inferred material.
