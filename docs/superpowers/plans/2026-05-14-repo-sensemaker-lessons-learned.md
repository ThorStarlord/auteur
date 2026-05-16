# Repo-Sensemaker Lessons Learned

Date: 2026-05-14
Companion to: docs/handoffs/2026-05-14-repo-sensemaker-research-test-hardening.md

## Purpose

This note captures what we learned about using repo-sensemaker as a workflow.
It is not a session handoff. The handoff remains the source for repo state,
verification status, architectural constraints, and the next task.

## Workflow Chain Used

The research run used this downstream chain after the initial repository
sensemaking brief:

1. grill-with-docs
2. to-prd
3. to-issues
4. triage
5. tdd
6. handoff

Lesson:
- Repo-sensemaker was useful as a front-end diagnostic step, but the value came
  from converting the diagnosis into explicit implementation artifacts and
  tests. The skill should be treated as the first step in a workflow, not the
  whole workflow.

## What Repo-Sensemaker Did Well

- It forced a concrete statement of repository goal, current shape, strong
  signals, missing pieces, and weakest boundary.
- It improved prioritization by pushing the analysis toward the most ambiguous,
  unproven, or unenforced contract.
- It worked well with Auteur's existing language in CONTEXT.md and
  docs/next-step-discovery.md.
- It produced a diagnosis that translated cleanly into AFK slices.

## What Repo-Sensemaker Missed

- The draft skill depended on reference material that was named but not present
  in the repository.
- The draft skill assumed a downstream workflow-orchestrator that does not
  currently exist in this repo.
- The draft skill defined an output format, but did not define how that output
  should be operationalized into documentation, issues, triage, and tests.

## Dependency Model Lessons

The dependency model was too implicit in three ways:

1. Reference docs were assumed to exist.
2. A recommended downstream workflow runner was assumed to exist.
3. Evidence rules were stated in the prompt, but not enforced by a local
   validator or repository convention.

Lesson:
- A usable repo skill should either ship its references in-repo or degrade
  gracefully when they are absent.

## Draft-Skill Research Findings

- Missing references:
  - docs/references/repo-analysis-template.md
  - docs/references/weakness-types.md
  - docs/references/evidence-rules.md
- Missing workflow target:
  - workflow-orchestrator was referenced conceptually, but no corresponding
    implementation or skill package exists in this repository.
- Local substitute used:
  - next-step-discovery was used as the practical local workflow recommendation
    because it already encodes weakest-boundary-first planning in Auteur terms.

## Process Lessons

The weakest-boundary diagnosis led to this implementation order:

1. README contract alignment
2. Reference-pack creation
3. Deterministic validator enforcement

Why this order worked:
- README alignment fixed the highest-traffic boundary first.
- Reference docs removed implicit dependencies so the workflow could be repeated.
- The validator turned the previous two fixes into enforceable repository
  contracts.

Lesson:
- When a weakest-boundary diagnosis points to documentation drift, the best next
  move is often: correct the contract, define the missing reference materials,
  then automate regression detection.

## Reusable Recommendations For Future Runs

Required inputs:
- Repository goal
- Current shape
- Existing domain glossary and ADRs
- Candidate weakest-boundary evidence from docs, code, tests, and file layout

Required reference files:
- docs/references/repo-analysis-template.md
- docs/references/weakness-types.md
- docs/references/evidence-rules.md

Evidence-quality rules:
- Cite exact files and lines where possible.
- Prefer contrastive evidence between docs and code over intuition.
- Follow workflow logic through actual execution paths.
- Avoid vibe-based claims; name the exact unenforced or ambiguous boundary.

Operational recommendations:
- Treat repo-sensemaker output as a planning artifact, not the final artifact.
- Convert the brief into a PRD or issue slices immediately.
- Prefer AFK slices when the weakest boundary can be hardened deterministically.
- Add validator coverage whenever the diagnosis identifies contract drift.

## Recommended Split Going Forward

Handoff should contain:
- What changed in the repo
- What was verified
- Architectural decisions that constrain follow-up work
- The frontier for the next session

Lessons note should contain:
- Skill-chain details
- Evaluation of the skill itself
- Missing dependencies and local substitutes
- Process lessons from issue ordering
- Recommendations for making the workflow repeatable

first output:
I will run your six-step sequence end-to-end by loading each skill’s instructions first, then producing artifacts in-repo (brief, PRD, issues, triage, TDD implementation, and final handoff) without waiting for approvals. I’m starting by reading the exact skill definitions so execution follows your requested workflow faithfully.

Read skill grill-with-docs (C:/Users/Admin/.agents/skills/grill-with-docs/SKILL.md)

Read skill to-prd (C:/Users/Admin/.agents/skills/to-prd/SKILL.md)

Read skill triage (C:/Users/Admin/.agents/skills/triage/SKILL.md)

Read skill to-issues (C:/Users/Admin/.agents/skills/to-issues/SKILL.md)

Read skill tdd (C:/Users/Admin/.agents/skills/tdd/SKILL.md)

Read skill handoff (C:/Users/Admin/.agents/skills/handoff/SKILL.md)

I’m moving into your requested skill sequence now: I’ll first synthesize a grill-with-docs output as a self-answered decision chain, then convert it into PRD/issues/triage artifacts in docs, and finally implement the highest-priority AFK issues via TDD with real test runs. I’m collecting a small amount of codebase context needed for the TDD phase.

Searched for files matching `auteur` · `tests/test_*readme*`, no matches

Searched for regex `structure generation/diagnosis CLI commands|proposal/report artifacts|does not yet have` (`**/README.md`), 3 results

Read docs/handoffs

Read pyproject.toml

I’m now executing prompts 1–4 as repository artifacts: a self-answered grill-with-docs decision chain, then PRD, then local issue slices (without GitHub publication), then triage outcomes. After that I’ll start prompt 5 with RED tests for the top AFK issue.

Created docs/superpowers/plans/2026-05-14-grill-with-docs-repo-sensemaker.md

Created docs/prd-repo-sensemaker-research-test.md

Created docs/superpowers/plans/2026-05-14-to-issues-repo-sensemaker.md

Prompts 1–3 are now materialized in-repo. Next I’m running prompt 4 by triaging these local slices into explicit category/state decisions, then I’ll immediately begin prompt 5 with TDD on Slice 1 and Slice 2 before Slice 3.

Created docs/superpowers/plans/2026-05-14-triage-repo-sensemaker.md

I’m starting prompt 5 now with strict RED→GREEN→REFACTOR cycles in priority order: first a failing test for Slice 1 (README contract), then fix README, then repeat for Slice 2 (reference docs), then Slice 3 (deterministic validator + tests). I’ll run real pytest commands between each cycle.

Generating patch (16 lines) in tests/test_repo_contract.py


```

```


Configuring a Python Environment
Completed with input: {
  "resourcePath": "h:\\GithubRepositories\\auteur"
}

Creating a Virtual Environment
Completed with input: {
  "resourcePath": "h:\\GithubRepositories\\auteur"
}

Ran terminal command: H:/Python/Python312/python.exe -m pytest tests/test_repo_contract.py -q --tb=no
Completed with input: H:/Python/Python312/python.exe -m pytest tests/test_repo_contract.py -q --tb=no

Read README.md, lines 16 to 34

Generating patch (6 lines) in README.md


```

```


Ran terminal command: H:/Python/Python312/python.exe -m pytest tests/test_repo_contract.py -q --tb=no

Slice 1 is complete with a red-green cycle. I’m proceeding to Slice 2 by adding a failing existence test for the repo-sensemaker reference pack, then creating the missing docs and re-running tests.

Generating patch (19 lines) in tests/test_repo_contract.py


```

```


Ran terminal command: H:/Python/Python312/python.exe -m pytest tests/test_repo_contract.py -q --tb=no
Completed with input: H:/Python/Python312/python.exe -m pytest tests/test_repo_contract.py -q --tb=no

Created docs/references

Created docs/references/repo-analysis-template.md

Created docs/references/weakness-types.md

Created docs/references/evidence-rules.md

Ran terminal command: H:/Python/Python312/python.exe -m pytest tests/test_repo_contract.py -q --tb=no

I’m starting Slice 3 now. I’ll add failing tests for a deterministic repository validator (current-repo pass case and failure cases for stale README/missing references), then implement the validator script and drive those tests to green.

Generating patch (54 lines) in tests/test_validate_repo.py


```

```


Ran terminal command: H:/Python/Python312/python.exe -m pytest tests/test_validate_repo.py -q --tb=no
Completed with input: H:/Python/Python312/python.exe -m pytest tests/test_validate_repo.py -q --tb=no

Created scripts/validate_repo.py

Ran terminal command: H:/Python/Python312/python.exe -m pytest tests/test_validate_repo.py -q --tb=no

All three prioritized AFK issues are now implemented through red-green cycles. I’m doing the refactor/verification phase next by running the new contract tests together and then running the full test suite to confirm nothing regressed before writing the handoff summary.

Ran terminal command: H:/Python/Python312/python.exe -m pytest tests/test_repo_contract.py tests/test_validate_repo.py -q --tb=no

Ran terminal command: H:/Python/Python312/python.exe -m pytest tests -q --tb=no

Ran terminal command: git -C h:/GithubRepositories/auteur branch --show-current

Ran terminal command: git -C h:/GithubRepositories/auteur log --oneline -20

Ran terminal command: git -C h:/GithubRepositories/auteur diff --stat

Ran terminal command: git -C h:/GithubRepositories/auteur status --short

I’ve finished prompt 5 and gathered git/test evidence for prompt 6. I’m now assembling the handoff document in docs/handoffs with full verification details (commits, files changed, test counts, decisions, ADR locks, and frontier), then I’ll verify it exists on disk.

Read docs/adr/001-structure-proposal-format.md

Read docs/adr/002-shared-structure-proposal-format.md

Read docs/adr/003-bible-audit-placement.md

Created docs/handoffs/2026-05-14-repo-sensemaker-research-test-hardening.md

Read docs/handoffs

Ran terminal command: Get-Item h:/GithubRepositories/auteur/docs/handoffs/2026-05-14-repo-sensemaker-research-test-hardening.md | Select-Object Name,Length

Executed your full 6-step sequence end-to-end without pausing for approvals, and completed prompt 5 with real red-green-refactor cycles plus full-suite verification.

What was produced

1. Prompt 1 (grill-with-docs, self-answered)
- 2026-05-14-grill-with-docs-repo-sensemaker.md

2. Prompt 2 (to-prd, auto-approved, saved in repo docs)
- prd-repo-sensemaker-research-test.md

3. Prompt 3 (to-issues, no GitHub publication)
- 2026-05-14-to-issues-repo-sensemaker.md

4. Prompt 4 (triage on local issue output)
- 2026-05-14-triage-repo-sensemaker.md

5. Prompt 5 (tdd, highest-priority-first, issue list exhausted)
Implemented slices in dependency order:
- Slice 1: README contract alignment
  - Updated README.md
  - Added test in test_repo_contract.py
- Slice 2: repo-sensemaker reference pack
  - repo-analysis-template.md
  - weakness-types.md
  - evidence-rules.md
  - Existence test in test_repo_contract.py
- Slice 3: deterministic validator + tests
  - validate_repo.py
  - test_validate_repo.py

Red-green evidence run:
- Red then green for README contract test
- Red then green for reference-doc existence test
- Red then green for validator behavior tests

Verification commands run:
- Focused: pytest on new contract tests passed (5 passed)
- Full suite: 161 passed

6. Prompt 6 (handoff skill, feature completion summary created and persistence-checked)
- 2026-05-14-repo-sensemaker-research-test-hardening.md
- File presence and non-empty size verified (length 4662 bytes)

Summary outcome
- Yes, your draft skill workflow can be used in this repo.
- The requested workflow chain was executed and materialized as repo artifacts.
- Highest-priority AFK issues were implemented with TDD and fully validated.
