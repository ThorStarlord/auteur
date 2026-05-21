# Grill With Docs — Enforce Source Domain In Structure Apply

Date: 2026-05-13
Mode: self-answered grilling (no user pauses)
Inputs: CONTEXT.md, ADR 002, handoff 2026-05-13-structure-workflow-contract-hardening.md

## Q1. What exact contract boundary is still unenforced?
Recommended answer: `auteur structure apply` must reject Decision Packets with `source_domain: bible_audit`.
Answer: Accepted.

## Q2. Which glossary terms govern the behavior?
Recommended answer: Proposal Lifecycle, Proposal Resolution, Structure Diagnostic, Bible Audit, Command Ownership.
Answer: Accepted.

## Q3. Where should enforcement live for smallest reversible change?
Recommended answer: `_cmd_structure_apply` in CLI, immediately after proposal model validation and before blueprint load/apply.
Answer: Accepted.

## Q4. Should legacy proposals with missing source domain be rejected now?
Recommended answer: No. Keep backward compatibility; allow `source_domain: null` artifacts to continue using current structure apply path.
Answer: Accepted.

## Q5. What user-facing failure behavior is required?
Recommended answer: Return exit code `1`, print a clear stderr error that bible-audit proposals must be resolved with `auteur audit --accept ... --option ...`.
Answer: Accepted.

## Q6. What must be protected to uphold the story-spine rule?
Recommended answer: Ensure source blueprint remains unchanged when rejection occurs.
Answer: Accepted.

## Q7. What is the first red test (tracer bullet)?
Recommended answer: Add `test_structure_apply_rejects_bible_audit_proposal` in fixture CLI tests asserting exit code, stderr guidance, and unchanged blueprint.
Answer: Accepted.

## Q8. What is intentionally out of scope for this slice?
Recommended answer: No schema migration, no analyzer changes, no movement of `bible_audit.py`, no generation-path rewrite, no LLM behavior changes.
Answer: Accepted.

## Q9. Does this conflict with locked ADRs?
Recommended answer: No. It implements ADR 002 runtime ownership enforcement; ADR 003 remains unchanged.
Answer: Accepted.

## Design Result
Implement a single guard in `_cmd_structure_apply` that rejects only `source_domain == "bible_audit"`; preserve legacy null behavior; prove with one red-first fixture test that the command fails safely and does not mutate the source blueprint.
