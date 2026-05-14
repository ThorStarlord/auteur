# Grill-With-Docs Output: Repo Sensemaker Research Test (Self-Answered)

Date: 2026-05-14
Mode: autonomous Q/A (no user pauses)
Source context: CONTEXT.md, README.md, docs/project-format.md, src/auteur/cli.py, tests/*

## Goal Extraction (from context)

Primary goal:
- Make weak contract boundaries explicit, testable, validated, and documented, with the smallest high-leverage change first.

Repository-specific target:
- Use a repeatable repository sensemaking flow to diagnose weakest boundaries and convert findings into executable slices.

## Question Chain (Answered Without User Input)

1. What is the system promise we must preserve?
- Recommended answer: Auteur turns a StoryBlueprint into deterministic structure diagnostics, proposal artifacts, and explicit authorial choice with bounded LLM behavior.
- Evidence: CONTEXT.md, docs/next-step-discovery.md, docs/architecture.md.

2. Which boundary is currently most ambiguous/unproven/unenforced?
- Recommended answer: Entry-point documentation contract drift in README status claims versus implemented/tested CLI behavior.
- Evidence: README.md says structure diagnose/propose artifacts are missing; cli.py and tests show they exist.

3. Is this a vocabulary conflict or behavior conflict?
- Recommended answer: Behavior conflict expressed as vocabulary drift in status wording.
- Why: Terms in README imply absent capability while code exposes commands and tests enforce behavior.

4. What is the smallest change that hardens the boundary immediately?
- Recommended answer: Correct README status section to match implemented CLI and tests.

5. What makes this boundary durable instead of one-off?
- Recommended answer: Add an automated repository contract check that fails if stale README claims reappear.

6. Which dependencies are implicit in the draft repo-sensemaker skill?
- Recommended answer: references/repo-analysis-template.md, references/weakness-types.md, references/evidence-rules.md, and workflow-orchestrator are referenced but not present in this repo.

7. What should be done about missing dependencies to make the skill runnable in-repo?
- Recommended answer: Add docs/references equivalents and keep workflow recommendation local (next-step-discovery) until workflow-orchestrator exists.

8. Should this require ADRs?
- Recommended answer: No new ADR needed for README alignment and diagnostic references. These are reversible and unsurprising documentation/validation hardening steps.

9. What testability contract should be added?
- Recommended answer: A deterministic script check plus pytest coverage that verifies:
  - README does not claim missing implemented structure CLI/proposal capabilities.
  - Required repo-sensemaker reference docs exist.

10. Final approved design (auto-approved per instruction)?
- Recommended answer: Approved.
  - Slice A: README status contract alignment.
  - Slice B: Add repo-sensemaker reference docs in-repo.
  - Slice C: Add repository validation check + tests.

## Output for to-prd
- Problem: weakest-boundary diagnosis exists but draft-skill dependencies and top-level contract are not enforced.
- Solution: codify references, align README, add deterministic validation and tests.
