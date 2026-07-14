# Auteur Critic Integration Contract

The Critic Integration Contract defines how an analyzer, validator, critic, or
future model-backed adapter produces a Reasoning Report. It is an integration
contract built on Auteur's four foundations, not a fifth architecture.

```text
Narrative       → what knowledge exists
Provenance      → which revision is authoritative
Transformation  → how approved change moves
Reasoning       → why change is justified
Critic contract → how a producer supplies reasoning
```

Critics are read-only. They explain observations and recommend possible
transformations; they never accept, publish, or mutate narrative artifacts.

## Lifecycle

Every critic follows the same conceptual lifecycle:

```text
Analyzer output
    ↓
Observation adapter
    ↓
Evidence extraction
    ↓
Hypothesis generation
    ↓
Evaluation
    ↓
Reasoning Report
    ↓
Optional Transformation Proposal
```

The final proposal step is optional and remains owned by Transformation
Architecture. A critic may describe supported transformations without creating
one.

## Critic contract

A critic implementation declares a stable contract:

```yaml
critic_id:
critic_version:
input_contract:
  artifact_types: []
  required_scopes: []
  required_revisions: []
  freshness_policy:
output_contract:
  artifact_type: reasoning_report
  report_schema_version:
  deterministic:
  confidence_method:
```

Given declared inputs, a critic returns either a complete Reasoning Report or
an explicit diagnostic failure. It must not return a partial report that could
be mistaken for a conclusion.

The report must contain observations, source-backed evidence, one or more
hypotheses, evaluation results, claims, confidence, recommendations, and
provenance. Each claim identifies its evaluation and hypothesis basis. Each
recommendation identifies the claim it addresses.

## Producer classes

Deterministic, heuristic, statistical, and LLM-backed critics share the same
output contract:

| Producer | Required discipline |
|---|---|
| Deterministic | Reproducible extraction and declared rule/version |
| Heuristic | Named heuristic, inputs, and limitations |
| Statistical | Model/version, feature inputs, calibration status, and uncertainty |
| LLM-backed | Prompt/model/version, source evidence, and explicit unverified inferences |

Implementation technology does not grant authority. A model-generated assertion
without source linkage is a hypothesis or claim, never evidence. Uncalibrated
confidence must be marked unknown rather than presented as an objective score.

## Provenance and freshness

Each report records:

- critic ID and implementation version;
- every source artifact, revision, and content hash;
- extraction or measurement version;
- executor kind and model metadata when relevant;
- creation time and freshness dependencies;
- the reasoning contract/schema version.

Before producing a report, the adapter validates required inputs and their
freshness policy. A changed or missing dependency makes the report stale or
causes an explicit failure. Staleness never silently rebinds a report to a new
revision.

## Composition

Critics compose through reports, not hidden shared mutation. A critic may read
another report only when that report is declared as derived evidence with its
own provenance and freshness dependency. Critics must not form dependency
cycles, silently replace another critic's conclusion, or require a particular
critic to run first unless that dependency is explicit in the contract.

Cross-critic synthesis is a separate adapter. It evaluates its input reports
and preserves their provenance; it does not make one critic's claim canonical.

## Authority boundaries

```text
critic input
    ↓ read
Reasoning Report (derived)
    ↓ optional, explicit handoff
Transformation Proposal (noncanonical)
    ↓ existing validation / plan / publication / decision
Accepted artifact (canonical)
```

Critic execution cannot create accepted candidates, modify accepted pointers,
recompose chapters, or change Identity, Structure, Realization, Expression, or
Bible/state. Proposal generation, when supported, must use the existing
proposal format and normal freshness validation.

## Invariants

1. The adapter is read-only with respect to narrative and canonical state.
2. Inputs, revisions, hashes, and freshness dependencies are declared.
3. Observations are separated from hypotheses and recommendations.
4. Evidence is source-backed and distinguishable from inference.
5. Multiple hypotheses may coexist and are explicitly evaluated.
6. Reasoning dependencies are acyclic.
7. A report is complete, derived, and provenance-rich or the run fails.
8. Confidence declares its method, calibration, or unknown status.
9. Repeated deterministic runs with identical inputs produce equivalent reports.
10. Stale inputs cannot produce a falsely fresh report.
11. Critics do not silently overwrite reports or canonical artifacts.
12. Optional proposals remain author-decidable and noncanonical.

## Extension points

Future critics may add domain-specific evidence, hypothesis strategies,
evaluation methods, and transformation options while retaining the common
report schema. Domain packs and plugins may provide adapters through this
contract without importing authority into their own code.

The contract does not define scheduling, queues, retries, multi-agent
coordination, user interface, voting, or workflow completion. Those concerns
belong to later systems built on these boundaries.

## First implementation boundary

The smallest implementation is one deterministic adapter around an existing
critic or analyzer. It should emit a validated Reasoning Report and demonstrate
freshness rejection and zero canonical mutation. Proposal generation and
orchestration remain separate follow-up slices.

