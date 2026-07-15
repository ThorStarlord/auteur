# Auteur Reasoning Runtime

The Reasoning Runtime selects and executes registered critics through the
[Critic Integration Contract](critic-integration-contract.md). The Registry
answers what critics exist; the Runtime answers which compatible critics should
run for a requested analysis or changed artifact.

The Runtime is read-only with respect to narrative authority. It persists only
derived execution records and Reasoning Reports.

## Responsibilities

The Runtime owns:

- accepting an explicit analysis request or changed-artifact event;
- discovering critics through the Registry;
- checking compatibility and declared requirements;
- constructing and validating a dependency DAG;
- validating source freshness immediately before execution;
- invoking critics and recording outcomes;
- persisting complete derived Reasoning Reports and execution provenance.

The Registry owns identity, versions, capabilities, compatibility metadata, and
dependency declarations. The Runtime does not own scheduling policy,
concurrency, queues, caching, distribution, synthesis, or user interface.

## Execution request and plan

A request is explicit and bounded:

```yaml
request_id:
reason:
  kind: requested_analysis | changed_artifact
  artifact_ids: []
critic_ids: []
scope:
freshness_policy:
runtime_contract_version:
```

An execution plan is derived from the request and current Registry state:

```yaml
plan_id:
request_id:
selected_critics:
  - critic_id:
    version:
    reason_selected:
dependency_order: []
source_snapshot:
  - artifact_id:
    revision:
    content_hash:
outcomes: []
status: planned | running | completed | failed
```

Identical requests, Registry state, and source snapshots produce equivalent
plans. Selection is explainable: each critic has a requested-analysis,
capability, dependency, or changed-input reason for inclusion.

## Selection and dependency DAG

For a requested analysis, the Runtime selects requested critics and their
required dependencies. For a changed artifact, it selects critics whose
declared requirements include the artifact type and scope, subject to
compatibility and freshness policy.

The Runtime expands dependencies, validates version ranges, and builds a
directed acyclic graph. A self-dependency or cycle is a plan failure with a
diagnostic path; it is never resolved by silently dropping an edge or critic.
Independent branches may be represented in the plan without requiring a
particular execution order.

Dependency reports are passed only through the declared derived-evidence
interface. They retain their own provenance and freshness dependencies.

## Freshness and preflight validation

The plan records a source snapshot, but that snapshot is not permission to
execute stale work. Immediately before each critic runs, the Runtime validates:

- required artifact existence and type;
- required scope and lifecycle status;
- expected revision and content hash;
- freshness policy and dependency reports;
- Critic Integration Contract and report schema compatibility.

A changed source yields a `stale` outcome and blocks that critic. Dependent
critics are also stale or blocked according to their declared policy. The
Runtime never substitutes a newer revision silently.

## Outcomes

Each selected critic produces exactly one outcome:

```yaml
critic_id:
version:
status: success | stale | incompatible | failed | blocked
reason:
report_id:
error:
source_snapshot:
```

`success` requires a complete, schema-valid Reasoning Report. `stale` means a
required source or dependency changed. `incompatible` means registry metadata
cannot satisfy the request or runtime contract. `failed` means execution
raised an explicit error. `blocked` means a dependency did not produce the
required usable report. Errors are persisted as derived diagnostics, never as
partial canonical changes.

## Report persistence

Successful reports are persisted as derived artifacts with the critic ID,
version, runtime and reasoning contract versions, request and plan IDs,
source revisions and hashes, dependency report IDs, execution timestamp, and
freshness dependencies. A report is stale when any declared dependency is
stale or no longer matches its source snapshot.

Persistence is append-only or versioned. A new run creates a new report; it
does not overwrite a prior report or change accepted pointers. Failed runs may
persist execution diagnostics but must not persist incomplete Reasoning Reports.

## Authority boundaries

```text
request / changed artifacts
        ↓
registry discovery and runtime plan
        ↓
read-only critic execution
        ↓
derived Reasoning Reports
        ↓ optional explicit handoff
Transformation Proposal → existing plan/publication/decision boundaries
```

Runtime execution cannot accept or publish candidates, create canonical
Expression or Chapter artifacts, recompose chapters, or mutate Identity,
Structure, Realization, Expression, or Bible/state.

## Invariants

1. Execution is explicitly requested or triggered by a declared change event.
2. Selection and ordering use Registry metadata and are explainable.
3. Dependency graphs are acyclic and cycle failures are explicit.
4. Requirements and freshness are validated against live state immediately
   before execution.
5. Every success produces a complete provenance-rich Reasoning Report.
6. Stale, incompatible, failed, and blocked outcomes are distinguishable.
7. Reports and diagnostics are derived; persistence is append-only/versioned.
8. Repeated deterministic execution over identical snapshots is equivalent.
9. No runtime path mutates canonical narrative state or accepted pointers.
10. Proposal generation, publication, and acceptance remain separate workflows.

## Deferred concerns

Scheduling policy, concurrency, retries, distributed execution, caching,
incremental invalidation, report synthesis, plugin installation, trust policy,
and author-facing UI are intentionally deferred. They may consume this Runtime
contract later without changing critic authority boundaries.

## First implementation boundary

The smallest runtime slice is an in-process planner and executor for one
deterministic registered critic. It should prove selection, dependency-cycle
rejection, pre-execution freshness validation, derived report persistence, and
zero canonical mutation before adding scheduling or multiple critics.

