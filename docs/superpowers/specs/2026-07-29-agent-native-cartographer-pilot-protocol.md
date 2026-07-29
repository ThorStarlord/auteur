# Agent-Native Cartographer Pilot Protocol

## Status

Design only; not approved or executed. Baseline: `0653defb05625f2fcde0ac32eac6e59ccf7eeb90`, branch `main`.

## Purpose

Test whether an external coding agent can receive an exact Cartographer task
packet, produce a valid Cartographer artifact, and show useful, bounded,
attributable response to profile emotional-target context under controlled
conditions. The coding agent is a proposed alternate executor, not canonical.

## Runtime context

Canonical implemented executor:

```text
PlanningCall → compile_outline() → LLMClient → provider model → CartographerOutline
```

Proposed alternate executor:

```text
exact agent task packet → coding agent → Cartographer artifact → existing validation
```

The paths are not assumed equivalent. This protocol does not call
`compile_outline()` or a direct provider.

## Definitions

An agent-native executor is an external coding agent that receives an exact,
versioned task packet, performs Cartographer reasoning in its own model context,
writes or returns a Cartographer-compatible output artifact, and submits it to
Auteur’s existing deterministic validation boundary.

## Non-goals

No production code, tests, prompts, schemas, providers, package metadata,
replay artifacts, credentials, or generalized telemetry framework. No canonical
runtime claim, reader-fulfillment claim, or behavioral equivalence claim.

## Executor contract

Auteur supplies the repository SHA, packet version, exact Cartographer
instructions, exact PlanningCall, authored target, profile mapping, output
schema identity, explicit non-goals, allowed tools, output path, validator
command, opaque condition token, and hashes.

The agent supplies one exact output artifact, completion status, validation
attempt, bounded tool-use summary, visible host/model metadata, context-isolation
declaration, and unexpected-change declaration. It must not modify production
files or make unsupported assumptions.

Auteur validates syntax, `CartographerOutline`, required fields, packet identity,
output provenance, repository cleanliness, and pair isolation. Identity,
inputs, output, validation, isolation, and change status are mandatory;
unavailable host metadata is recorded as unknown.

## Execution mode

Use one disposable temporary worktree or copy per condition. Each contains one
required output artifact under a local evaluation directory and no production
modifications. This is the recommended first-pilot mode because it isolates
working-tree state and sibling artifacts.

## Task packet

Use versioned YAML containing:

```yaml
artifact_type: cartographer_agent_task
schema_version: 1
evaluation_id: synthetic-evaluation
pair_id: A1
condition_token: opaque-a
repository_sha: <exact-sha>
instruction_files:
  - path: AGENTS.md
    sha256: <hash>
planning_call: <exact-canonical-content>
authored_emotional_target: mounting dread
profile_emotional_targets: {}
output_contract:
  type: CartographerOutline
  format: yaml
  path: .local/evaluations/cartographer-agent/A1/opaque-a/outline.yaml
validation_command: <existing deterministic validator>
allowed_actions: [read specified files, write one artifact, run validator]
forbidden_actions: [modify source, modify tests, call providers, inspect sibling]
```

The packet includes the exact PlanningCall, authored target, profile targets,
schema identity, repository/instruction hashes, evaluation/pair IDs, opaque
condition, output path, validator, and action limits. It contains no subjective
rubric and does not identify treatment to the generator.

## Wrapper and embedded prompt

Use a thin immutable operational wrapper plus the exact rendered Cartographer
prompt. Do not rewrite the prompt. Hash and retain both. The wrapper may direct
artifact writing, allowed tools, validation, and the repair limit, but may not
add narrative interpretation, hypotheses, or reviewer criteria.

## Control/treatment isolation

Each pair differs only in `profile_emotional_targets` and its derived rendered
prompt section. Repository SHA, instruction hashes, wrapper, PlanningCall,
authored target, story context, schema, tools, permissions, host/model, and
validator must match. Verify canonical pair equality before execution.

Use opaque condition labels and randomize order where practical. Leakage means
exposing the sibling artifact, mapping, weights, hypothesis, or treatment-only
prompt to the generator.

## Session isolation

Use separate fresh sessions and disposable worktrees for control and treatment.
Share no transcript, scratchpad, output directory, or prior explanation. A
same-session reset is contaminated unless the host guarantees isolation.
Record residual contamination risks.

## Agent environment

Record whether each value is fixed, recorded, or unknown: host/product,
visible model identifier, reasoning mode, agent version, OS, repository SHA,
tools, network, permissions, instruction files, fresh-session status, and
timestamps. Never infer a deterministic model identity from a product label.

## Tool permissions

Allow reading specified files, writing one evaluation artifact, running the
exact validator, inspecting validation errors, and at most two syntax/schema
repair attempts. Retain every attempt; repairs may not introduce new narrative
reasoning after a paired condition is seen.

Disallow source/test/prompt/schema changes, sibling access, direct-provider API
calls, web research, installation, package changes, commits, pushes, and
release operations.

## Output evidence

Retain the packet, wrapper, rendered prompt, repository/instruction hashes,
visible agent metadata, exact final artifact, validation result, repair attempts,
concise execution log, tool summary, timestamps, completion state, unexpected
changes, and isolation declaration. Full transcripts are not required; retain
one only if safely available and necessary. Never request or store hidden
chain-of-thought.

## Agent execution record

Use a separate protocol artifact, not `CartographerCaptureV1` or a production
model. YAML fits existing report/artifact conventions. Required fields are
artifact/schema version; evaluation, pair, opaque condition, repetition, and
repository SHA; host/model/version/session/tools/network/permissions; fresh
session; packet/wrapper/prompt/PlanningCall/instruction hashes; output path/hash;
validation; repair count; completion; timestamps; record hash; and unexpected
changes. A synthetic template is provided beside this specification.

## Deterministic validation

The existing Auteur Cartographer validator is authoritative. Validate YAML
syntax, `CartographerOutline` schema and required fields, packet/repository
identity, output hash, and no source/test/production-file changes. Plausibility
or a model reviewer cannot substitute for schema validation.

## Pilot cases

All controls use `profile_emotional_targets = {}`. Treatments are:

| Pair | Authored target | Treatment |
| --- | --- | --- |
| A1 | mounting dread | `dread: 0.7`, `fascination: 0.4` |
| A2 | grief shaped by delayed recognition | `grief: 0.5` |
| A3 | restrained sorrow | `tenderness: 0.6`, `awe: 0.3` |
| A4 | tense curiosity | `dread: 0.2`, `tenderness: 0.9` |

## Execution count

Eight executions: one fresh execution for each control and treatment. This is
exploratory, not statistically significant; do not infer stable behavior from
one execution per condition.

## Blinded review

Present Output A/B with common context and authored target while hiding
condition, mapping, and weights. Reveal them only after initial ratings. Rate
attributable influence, authored-intent preservation, planning usefulness,
structural coherence, profile alignment, weight-semantic restraint,
prompt-parroting avoidance, and authority separation from -2 to +2. Do not
infer reader-level fulfillment.

## Behavioral failure modes

Retain F1 no meaningful influence, F2 prompt parroting, F3 authored-intent
displacement, F4 weight interpretation, F5 generic genre inflation, F6
structural damage, F7 inconsistent effect, F8 excessive influence, F9
hallucinated semantics, and F10 beneficial bounded influence.

## Agent-execution failure modes

AEF1 context contamination; AEF2 condition leakage; AEF3 unauthorized repository
modification; AEF4 output-contract failure; AEF5 excessive repair dependence;
AEF6 tool/permission drift; AEF7 instruction-file drift; AEF8 executor identity
unavailable; AEF9 non-comparable environments; AEF10 operator intervention
contamination. Keep these separate from behavioral findings.

## Decision gates

**Protocol viable:** all packets isolated; at least six of eight outputs valid;
no leakage or unauthorized source/test changes; evidence capture and blinded
review work.

**Alternate executor promising:** protocol viable; at least two pairs show
useful attributable influence; authored intent is preserved; no invented weight
semantics or severe structural harm occurs.

**Refine:** formatting dominates, repairs are excessive, wrappers/permissions
drift, or isolation is unclear. **Do not promote** if isolation, validation, or
honest retention fails. A four-pair pilot cannot establish canonical status.

## Operator workflow

1. Synchronize and record SHA and source/test status.
2. Create disposable worktrees/copies per condition.
3. Render unchanged prompts and hash packet, wrapper, prompt, and instructions.
4. Create packets and verify pair equality.
5. Randomize order and open a fresh session per condition.
6. Provide only the assigned packet and wrapper.
7. Permit at most two format/schema repairs.
8. Retain artifacts/records and inspect unexpected changes.
9. Run deterministic validation and reject invalid outputs.
10. Assemble blinded pairs and conduct human review.
11. Reveal conditions and classify behavioral versus execution findings.
12. Decide whether to refine or expand; do not promote from this pilot.

Human judgment occurs in packet approval, isolation declaration, blinded review,
failure classification, and the expansion decision.

## Host capability requirements

A host must provide a fresh isolated session, repository read access, exact
output return/write, validator execution, visible host/product identity,
operator retention, and no sibling-condition access. ChatGPT coding agent,
Codex, Claude Code, GitHub Copilot agent, and other hosts must be assessed
individually. Missing model/session/transcript metadata is recorded as unknown;
a host lacking minimum isolation or exact-output retention is unsuitable.

## Credential requirements

The agent-native pilot does not require Auteur’s `ANTHROPIC_API_KEY` or
`OPENAI_API_KEY`, does not call `compile_outline()`, and does not call a direct
provider. The host may require its own paid/authenticated account; that
credential is outside Auteur and never enters an artifact.

## Relationship to direct-provider evaluation

The direct-provider reports and setup guide remain executor-specific evidence.
The replay harness remains valid for provider request/response replay and parser
validation, but does not evaluate agent reasoning. A later cross-executor study
may test contract equivalence; it is deferred.

## Implementation decision

Run the first pilot manually with versioned YAML packets, existing validators,
and execution records. No helper, production model, capture extension, or
telemetry framework is needed before the first pilot.

## Risks

Context contamination, hidden model changes, operator intervention, tool drift,
repair masking, and unavailable exact outputs can invalidate attribution. A
valid artifact proves contract conformance, not usefulness.

## Open decisions

- Which host meets the minimum capability contract.
- The exact existing focused validation command to place in packets.
- Whether host metadata is sufficient for comparability.
- Approval for local-only fictional-output retention.

## Recommendation

Approve the manual protocol for review. After packet hashes, host capabilities,
isolation, retention, and validator commands are confirmed, run the bounded
eight-execution pilot. Add code only after protocol friction is observed.

## Explicit answers

1. Agent-native executor: external coding agent executing an exact packet and submitting an artifact to existing validation.
2. Coding agent canonical today: **NO**.
3. Contract: exact inputs, immutable instructions, bounded tools, one artifact, provenance, isolation, and validation.
4. Input: versioned packet with exact PlanningCall, target, mapping, hashes, schema, path, and rules.
5. Exact rendered prompt: **YES**, unchanged and hashed.
6. Wrapper: operational only; no narrative criteria.
7. Output: one YAML `CartographerOutline` plus execution record.
8. Validator: existing deterministic Auteur Cartographer validation.
9. Isolation: pair equality, opaque labels, disposable worktrees, fresh sessions.
10. Sessions: one fresh session per condition; no shared context.
11. Metadata: host/model/version, OS, tools, network, permissions, SHA, hashes, freshness, timestamps.
12. Unavailable model ID: record **unknown**; do not guess.
13. Full transcripts: **NO**.
14. Hidden reasoning: **NO**.
15. First pilot: eight executions.
16. Repair: **YES**, syntax/schema only.
17. Repair limit: two attempts, all retained.
18. Leakage: sibling, mapping, weights, hypothesis, or treatment-only context exposure.
19. Protocol success: six valid outputs minimum plus isolation, evidence, and review gates.
20. Promising evidence: two useful attributable pairs with preserved intent and no invented semantics or severe harm.
21. Anthropic/OpenAI keys: **NO**.
22. Calls `compile_outline()`: **NO**.
23. Replay evaluates agent-native execution: **NO**.
24. Production code first: **NO**.
25. Next action: approve packet/host details, then run the bounded pilot.
