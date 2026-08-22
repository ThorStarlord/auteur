# Judgment Benchmark Study (V1–V3)

Status: **closed study summary**.

This document records the durable engineering lessons from a series of judgment-oriented stress tests run against Auteur. It is a repository-facing summary only; the frozen protocols, raw execution evidence, evaluator records, errata, hashes, and cross-version comparison are maintained in the external benchmark-records archive.

The study is closed. This document does not reopen V2 or V3, change any adjudication, or define a new benchmark version.

## What the study tested

The benchmark evolved from measuring implementation activity toward measuring engineering judgment under uncertainty:

- whether an investigation target is consequential enough to spend effort on;
- whether an observed behavior is a verified defect, incomplete contract, structural dead end, behavioral edge, design preference, or no defect;
- whether production mutation is warranted by evidence;
- whether restraint (`NO_MUTATION`) is the correct engineering action;
- whether the execution environment actually delivered the intended treatment;
- whether the executor followed the protocol independently of treatment validity;
- whether evidence supports the action that was taken.

The resulting distinction is important: a run can contain a supported code defect while also containing an executor-protocol failure, and those facts should not be collapsed into one pass/fail judgment.

## Final study disposition

The final cross-version adjudication is:

```text
METHODOLOGY_QUALITY                 = CLEAR IMPROVEMENT
V3_EXECUTION_QUALITY                = MIXED / MESSY
CROSS_VERSION_EMPIRICAL_IMPROVEMENT = PARTIAL / NOT DIRECTLY COMPARABLE
TREATMENT_ADMISSIBILITY_V3          = UNRESOLVED
EXECUTOR_PROTOCOL_COMPLIANCE_V3     = FAIL
RERUN_RECOMMENDED                   = NO
```

`UNRESOLVED` is not equivalent to `FAIL`: no affirmative treatment contamination was established, but required bind-time provenance was incomplete. V3's surviving executor-compliance failure was separate: some validation commands were run without the required `PYTHONPATH`. Invalid results were detected and excluded, so this did not nullify otherwise-supported findings.

## Core engineering lessons

### 1. Restraint is a first-class engineering capability

An agent should not be rewarded merely for changing code. Some of the strongest judgments in the study were decisions not to mutate production because the apparent issue lacked an established contract or belonged to incomplete/unreachable architecture.

A useful benchmark must therefore represent:

```text
observable behavior
    -> investigate
    -> contract not established as violated
    -> NO_MUTATION
```

as a successful outcome when warranted.

### 2. Separate finding, action, and evidence support

These questions are orthogonal:

1. What was found?
2. What repository action was taken?
3. Did the available evidence support that action?

A production commit can be speculative even when the observed behavior is real. Conversely, a confirmed behavioral edge can correctly end in no mutation.

V3's most important methodological improvement was making these dimensions explicit instead of forcing them into a single defect/action label.

### 3. Treatment validity and executor compliance are different axes

The study adopted the rule:

> Treatment violations determine admissibility. Executor violations determine performance.

A wrong workspace, contaminated Git universe, or unresolved launch provenance is a treatment-delivery problem. Failing to follow an executor-visible command rule is a protocol-compliance problem. Neither should automatically erase independently supported code findings.

### 4. Workspace identity is an input to execution

A branch is not a repository boundary, and a linked worktree is not an isolated Git universe. Changing the working directory also does not necessarily rebind an already-running agent session.

The durable invariant is:

> **Workspace identity is an input to execution, not a state the executor should be expected to repair.**

For controlled runs, the harness should establish and verify the intended standalone repository/workspace before the executor begins.

### 5. Machine-enforce experimental hygiene

Rules that are deterministic should not depend on an agent remembering prose instructions.

Prefer machine enforcement for:

- workspace/repository identity;
- base revision;
- Git ref/object isolation where required;
- import path and environment variables;
- runtime qualification;
- cycle accounting;
- launch/session provenance;
- final sensor-artifact preservation;
- required report fields and hashes.

Reserve model judgment for uncertain engineering questions such as contract interpretation, target importance, mutation necessity, and information value.

### 6. Missing evidence must remain missing

A missing sensor value is not zero. Missing provenance is not proof of contamination. A known invalid validation run is not evidence for or against a code finding.

The benchmark should preserve `UNAVAILABLE`, `UNRESOLVED`, and other explicit uncertainty states rather than manufacture certainty for easier scoring.

### 7. Coverage is a sensor, not the reward

Coverage helped expose under-tested areas, but optimizing coverage itself can encourage manufactured tests or low-value work. The study therefore treats statement, raw-branch, and combined coverage as telemetry rather than the objective.

The same principle applies to any easily optimized proxy: measure it, but do not let it replace engineering consequence.

### 8. Stronger observability can reveal more failures

V3 exposed execution and provenance problems more precisely than earlier versions. That does not necessarily mean the underlying process became worse; some failures became visible because the protocol finally had categories for them.

When comparing protocol versions, distinguish improvements in measurement from improvements in the underlying executor.

## Diminishing returns and stopping rule

The V1–V3 sequence produced high-value methodological discoveries early and progressively more reporting/semantic cleanup late in the process. Once the study had:

- frozen protocols;
- preserved raw evidence;
- standalone adjudication;
- bounded additive errata;
- a cross-version comparison;
- a final bounded comparison erratum;
- durable hashed archival evidence;

additional audits of the same evidence had sharply diminishing expected information value.

The study therefore stops rather than continuing an evaluator-of-the-evaluator loop.

A useful rule is:

> If another audit only rearranges already-settled words, stop. If genuinely new evidence or a new experimental configuration exists, start a new prospective study.

## What should be tested next

The most promising next question is not another retrospective V2/V3 audit. It is autonomous investigation-budget allocation:

```text
observe repository
    -> identify consequential uncertainty
    -> choose highest-value hypothesis
    -> probe
    -> update beliefs
    -> decide whether another cycle is worth its cost
        -> CONTINUE
        -> STOP
```

A future experiment should test whether an agent can decide what to investigate next and when further investigation has insufficient expected information value, rather than requiring a fixed number of cycles.

That work should be designed as a new prospective experiment, not appended to this closed study.

## Process-centered interpretation

The study's failures are most useful when translated into process improvements rather than individual blame:

- If executors repeatedly miss an invariant, enforce it in the harness.
- If evaluators repeatedly disagree about a category, specify its semantics prospectively.
- If a rule creates compliance failures without producing useful information, redesign or remove it.
- If no change can be the correct answer, represent restraint explicitly.
- If provenance determines admissibility, capture it transactionally before execution.

The benchmark's main success was becoming better at locating *where* a failure occurred: treatment delivery, executor compliance, evidence capture, classification, action choice, or reporting. That localization makes improvement actionable.
