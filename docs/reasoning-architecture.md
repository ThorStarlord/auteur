# Auteur Reasoning Architecture

Reasoning Architecture defines how Auteur justifies recommendations without
silently changing narrative authority. It is distinct from Narrative
Architecture, Provenance Architecture, and Transformation Architecture:

```text
Narrative    → what knowledge exists
Provenance   → which revision is authoritative
Transformation → how approved knowledge moves
Reasoning    → why a change is justified
```

Reasoning outputs are explanations and recommendations. They are not canonical
narrative facts and do not mutate Identity, Structure, Realization, Expression,
or Bible/state.

## Reasoning pipeline

The canonical conceptual flow is:

```text
Observation
    ↓
Evidence Collection
    ↓
Hypothesis
    ↓
Claim / Diagnosis
    ↓
Confidence
    ↓
Recommendation
    ↓
Transformation Proposal
```

The stages are deliberately separate. Evidence supports hypotheses; hypotheses
explain observations; claims summarize the selected diagnosis; recommendations
describe actionable responses; proposals instantiate a recommendation as an
author-decidable transformation.

## Reasoning artifact

A reasoning artifact is a derived, provenance-rich explanation of a narrative
observation. A minimal abstract shape is:

```yaml
reasoning_id:
artifact_type: reasoning_report
subject:
  artifact_id:
  artifact_type:
observations:
  - observation_id:
    statement:
evidence:
  - evidence_id:
    source_artifact:
    source_revision:
    source_hash:
    extraction:
hypotheses:
  - hypothesis_id:
    statement:
    supporting_evidence: []
    contradicting_evidence: []
claims:
  - claim_id:
    statement:
    hypothesis_id:
confidence:
  score:
  method:
  explanation:
recommendations:
  - recommendation_id:
    statement:
    claim_ids: []
    possible_transformations: []
transformation_contract:
  id:
  version:
provenance:
  source_artifacts: []
  created_at:
status: derived
```

The artifact records reasoning, not a canonical story decision.

## Vocabulary

### Observation

An observation is a bounded statement about a detectable property of one or
more artifacts. It should be reproducible from declared inputs.

Bad:

```text
This chapter is weak.
```

Good:

```text
Scenes 4, 5, and 6 repeat the same emotional polarity transition.
```

Observations should avoid causal language and recommendations.

### Evidence

Evidence is the source-backed material used to evaluate an observation or
hypothesis. It must identify source artifact, revision, content hash, and the
deterministic extraction or measurement that produced it.

Evidence may be qualitative text spans, structural metrics, dependency facts,
or validator findings. A model-generated assertion without source linkage is a
hypothesis or claim, not evidence.

### Hypothesis

A hypothesis is a possible explanation for an observation. Multiple hypotheses
may coexist, including competing explanations:

```text
repetition is monotonous
repetition is intentionally oppressive
a transition is missing
```

Hypotheses remain provisional. They must list supporting and contradicting
evidence where available. One hypothesis must not silently replace alternatives.

### Claim / diagnosis

A claim is the current explanatory conclusion selected from evaluated
hypotheses. A diagnosis is a claim presented in a form useful for deciding
whether intervention is warranted. Claims must identify their hypothesis basis,
evidence, confidence, and unresolved alternatives.

### Confidence

Confidence expresses support for a claim under a declared method. It is not a
probability that the story is objectively bad or that an author must agree.

```yaml
score: 0.82
method: deterministic_metric
explanation: three consecutive transitions share the same polarity direction
```

Confidence scores are comparable only within the same method and contract.
Unknown or uncalibrated confidence must be represented explicitly rather than
inventing a numeric score.

### Recommendation

A recommendation is an actionable response to a claim. It must state what could
change, why that change addresses the claim, and what authority boundary it
would cross. Recommendations may offer alternatives and must not imply that one
has been chosen.

### Transformation proposal

A recommendation becomes a transformation proposal only when it identifies a
supported target, proposed operation, expected source revision, and evidence
for author review. Proposal creation does not accept or publish the change.

## Canonical and derived status

Reasoning artifacts are derived by default. They may be preserved, versioned,
superseded, or archived, but they do not become canonical narrative knowledge.

Reasoning may refer to canonical inputs and accepted revisions. It may also
refer to candidates or external imports, provided their status and freshness are
recorded. A stale source makes dependent reasoning stale; it does not silently
rewrite the reasoning result.

Only an explicit Transformation Proposal can cross from reasoning into a later
proposal, plan, publication, or acceptance workflow.

## Provenance integration

Every reasoning result should record:

- source artifact IDs and types;
- source revisions and hashes;
- transformation or analysis ID and version;
- executor kind, when relevant;
- creation time;
- freshness dependencies;
- superseded reasoning artifacts, if any.

Provenance answers where reasoning came from. It does not convert a claim into
truth. Acceptance remains owned by the target artifact’s lifecycle.

## Transformation integration

Reasoning may produce a recommendation with possible transformations:

```yaml
possible_transformations:
  - id: expression.revise_scene_candidate
    target: scene_07_05
  - id: structure.insert_scene
    target: chapter_07
```

These are options, not executed operations. Transformation Architecture
consumes a selected recommendation only through an explicit proposal and its
normal validation, planning, publication, and acceptance boundaries.

## Implementation neutrality

The reasoning contract is independent of implementation technology. A
deterministic validator, heuristic algorithm, statistical model, or LLM may
produce a reasoning artifact if it supplies the same evidence, hypothesis,
confidence, recommendation, and provenance fields.

LLM output without source evidence is not authoritative reasoning. It may be
stored as an unverified hypothesis or suggestion for review.

## Validity invariants

1. Every claim has declared evidence or is explicitly marked unsupported.
2. Evidence identifies source artifact, revision, and content hash when the
   source is revisioned.
3. Multiple hypotheses may coexist.
4. Hypotheses do not become claims without an explicit evaluation result.
5. Confidence always declares its method or is unknown.
6. Recommendations identify the claim they address.
7. Recommendations do not mutate narrative artifacts.
8. Proposals remain author-decidable and noncanonical until accepted.
9. Stale inputs make dependent reasoning stale or require re-evaluation.
10. Reasoning cannot bypass Provenance or Transformation boundaries.
11. A reasoning report never silently replaces a prior report.
12. Failed reasoning runs leave no partial canonical mutation.

## Scope boundaries

In scope:

- observations from narrative artifacts;
- source-backed evidence collection;
- competing hypotheses;
- explainable claims and confidence;
- actionable recommendations;
- adapters to existing deterministic critics and analyzers.

Deferred:

- generic AI workflow engines;
- multi-user voting or approval;
- automatic proposal acceptance;
- hidden model-based quality scores;
- causal claims without evidence;
- automatic Scene merge/split or markerless mapping;
- optimization across the entire narrative without author decisions.

## First implementation boundary

The smallest useful implementation is a deterministic reasoning-report adapter
around one existing critic or analyzer. It should produce observations,
evidence, competing hypotheses, confidence method, and recommendations without
creating proposals or mutating narrative state. A later slice may convert one
selected recommendation into an existing proposal format.
