---
name: docs-aligner
description: autonomously align a codebase's documentation with its implementation by detecting contradictions, sharpening fuzzy language, discovering undocumented concepts, and updating CONTEXT.md. use as the first step in any implementation workflow.
---

# docs-aligner

Automated domain alignment for autonomous workflows. Reads the codebase and existing documentation, detects all contradictions and ambiguities in a single pass, updates `CONTEXT.md` directly, creates ADRs for hard-to-reverse decisions, and produces a consolidated `domain_alignment_report` artifact.

This skill performs the same conceptual function as the interactive `grill-with-docs` skill (challenge domain language, sharpen terminology, update CONTEXT.md) but operates autonomously without human Q&A. Suitable for `gate: none` steps in autonomous workflows.

## Workflow

1. **Inventory**: Read `CONTEXT.md` and `docs/adr/` (if they exist), plus the repository structure.
2. **Analyze Codebase**: Scan source code, configuration files, registries, and key artifacts for domain concepts.
3. **Detect Contradictions**: Identify all conflicts between code and documentation in one pass.
   - Term in `CONTEXT.md` glossary that doesn't exist in code
   - Code concept not defined in glossary
   - Code behavior that contradicts documented design
4. **Sharpen Fuzzy Language**: For ambiguous or overloaded terms, propose a precise canonical term.
5. **Discover Undocumented Concepts**: Identify domain-significant concepts in code that belong in `CONTEXT.md`.
6. **Identify ADR Candidates**: Locate hard-to-reverse decisions that lack an ADR.
7. **Mutate**: Update `CONTEXT.md` with resolved terms and flagged ambiguities. Create ADR files for qualified candidates.
8. **Synthesize**: Produce the `domain_alignment_report` artifact documenting all findings.

## Output Format

Every response and output artifact must follow the [Domain Alignment Report](references/domain-alignment-report-template.md) structure.

## Boundary Rules

1. **No Implementation Planning**: This skill aligns domain language. It does not create PRDs, issues, or implementation plans. Feed the `domain_alignment_report` to `to-prd` for that.
2. **Domain Language Only**: Only include terms that are meaningful to domain experts. General programming concepts (timeouts, error types, utility patterns) do not belong in `CONTEXT.md` even if the project uses them extensively.
3. **Skip Single-Use Code Terms**: Not every variable or function name belongs in the glossary. Only add terms that represent domain-significant concepts — objects, boundaries, events, policies, or relationships that a domain expert would recognize.
4. **Concrete Evidence**: Every contradiction, fuzzy term, or undocumented concept MUST cite specific file paths and line numbers. No vague claims.
5. **Context Boundaries**: If `CONTEXT-MAP.md` exists, scope analysis to the active context. If not, treat repo as single context.
6. **Idempotency**: Running the skill on an already-aligned codebase should produce an empty or near-empty contradictions section and no CONTEXT.md mutations.

## ADR Eligibility

Create an ADR file in `docs/adr/` only when ALL three conditions are met:

1. **Hard to reverse** — changing the decision later has meaningful cost
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **Result of a real trade-off** — genuine alternatives existed and one was chosen for specific reasons

Use the minimal ADR format: a title and 1-3 sentences explaining context, decision, and rationale. Only add optional sections (Status, Considered Options, Consequences) when they add genuine value.

## Relationship to Other Skills

- **repo-sensemaker** diagnoses the weakest boundary; **docs-aligner** resolves language drift so implementation (via `to-prd`, `tdd`) operates on a clean domain model.
- **grill-with-docs** (interactive) asks one question at a time and is designed for human-in-the-loop sessions; **docs-aligner** is the automated equivalent for autonomous workflows.
- **sensemaking-docs-reconciler** focuses on vocabulary/contract drift within the sensemaking ecosystem itself; **docs-aligner** is a general-purpose domain alignment skill for any codebase.

## References
- [Domain Alignment Report Template](references/domain-alignment-report-template.md)
