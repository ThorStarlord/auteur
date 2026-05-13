# Next Step Discovery

This document captures the repeatable way to decide what to do next in Auteur.

## Core Question

Ask this first:

> What part of the contract is currently ambiguous, unproven, or unenforced?

That question is better than asking for a task list, because it points at the weakest boundary in the system.

## The Loop

1. Name the system promise.
   - Auteur's promise is to turn a structured story blueprint into deterministic structure diagnostics, human-editable proposals, and explicit authorial choice.

2. Name the core object.
   - The core object is the StoryBlueprint plus its structure artifacts: diagnostics, proposals, and accepted follow-through in the project.

3. Ask what must be true for that object to work.
   - Blueprint parsing and validation must be stable.
   - Structure fields must be explicit when required.
   - Diagnostics must be deterministic.
   - Proposal artifacts must preserve author choice.
   - Apply behavior must be explicit and non-destructive by default.
   - Bible state must stay separate from structure work.

4. Ask what is currently weakest.
   - The weakest part becomes the next step.

## How To Choose A Next Step

Prefer the smallest change that makes the weak point one of these:

- explicit
- testable
- validated
- documented
- discoverable

## Common Auteur Weak Spots

- Ambiguous terminology between structure diagnostics and Bible audit.
- Proposal resolution semantics that are not yet obvious from the CLI.
- Artifact layout under `structure/` that is not yet fully standardized.
- End-to-end workflow behavior that is not yet covered by a fixture.
- Documentation that explains the idea but not the lifecycle.

## A Good Next-Step Question

Use this prompt when you feel stuck:

> Which part of the current Auteur contract is most likely to confuse a future agent, author, or validator if I do nothing?

The answer should usually point to one of these:

- a doc update
- a fixture
- a validator
- a CLI contract
- an ADR

## Rule Of Thumb

If a change would only add more options, pause.

If a change makes the existing contract clearer, stronger, or easier to prove, it is probably a good next step.