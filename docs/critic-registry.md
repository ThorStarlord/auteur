# Auteur Critic Registry

The Critic Registry is the discovery contract for implementations that satisfy
the [Critic Integration Contract](critic-integration-contract.md). It is not a
runtime scheduler, plugin distribution system, or reasoning synthesizer.

```text
registry → discover compatible critic → declare contract → hand off to runtime
```

The registry describes what a critic is capable of and what it requires. A
separate execution layer decides when and how to run it.

## Registry entry

Each registered critic has a stable identity and immutable versioned metadata:

```yaml
critic_id: pacing.transition_density
version: 1.0.0
implementation_ref:
capabilities:
  - observation
  - evidence
  - evaluation
  - recommendation
requires:
  artifacts:
    - type: scene_expression
      scopes: [chapter]
  freshness_policy: require_current_revisions
produces:
  artifact_type: reasoning_report
  schema_version: 1
possible_transformations:
  - id: structure.insert_scene
    target_types: [chapter_structure]
compatibility:
  narrative_contracts: []
  critic_contract_version: 1
dependencies: []
```

`critic_id` identifies the capability, while `version` identifies the
behavior and metadata contract. A new behavior or incompatible input/output
change requires a new version. An implementation reference locates code but
does not grant it authority.

## Capabilities and compatibility

Capabilities describe the stages the critic can produce. They do not permit a
critic to omit required Reasoning Report fields. Compatibility is evaluated
against the Critic Integration Contract version, report schema version,
narrative artifact types, scopes, and declared narrative contracts.

A discovery result must make incompatibility explicit. The registry must not
silently adapt an incompatible critic or downgrade its declared requirements.

## Requirements and freshness

Critics declare every artifact type, scope, accepted/candidate status, and
freshness policy required for execution. Requirements may name accepted
revisions or permit candidates only when the critic contract says so.

The registry records policy; the execution layer performs live validation.
Missing, stale, or mismatched inputs prevent execution or produce an explicit
stale result. Registry metadata never rebinds a requirement to a newer revision
silently.

## Registration and discovery

Registration is explicit and yields a versioned registry entry. Discovery is a
read-only query by critic ID, capability, artifact type, scope, or compatibility
contract. Discovery returns metadata and an implementation reference; it does
not import narrative state, run a critic, create a report, or mutate storage.

Duplicate identity/version entries are rejected unless their metadata and
implementation reference are exactly equivalent. Replacing a registered entry
creates a new registry revision or versioned record; it does not rewrite prior
history invisibly.

The contract does not require a particular mechanism such as Python entry
points, a database, or a filesystem manifest.

## Dependencies

A critic may declare another critic as an optional or required dependency, with
the dependency's ID and compatible version range. Dependencies are metadata for
planning execution order. The dependency graph must be acyclic; registration
or validation rejects self-dependencies and cycles.

Critics consume dependency reports only as declared derived evidence with
normal provenance and freshness checks. A dependency does not become an
authority source merely because it ran first.

## Boundary with orchestration

The registry owns identity, metadata, compatibility, discovery, and dependency
declarations. It does not own:

- scheduling, retries, queues, or concurrency;
- caching or incremental invalidation;
- execution policy or resource limits;
- report synthesis or cross-critic adjudication;
- plugin installation, distribution, or trust policy;
- author UI or workflow completion.

The runtime receives a discovered entry, validates live inputs, invokes the
implementation through the Critic Integration Contract, and persists only a
derived Reasoning Report. Any proposal continues through Transformation
Architecture's existing validation, planning, publication, and acceptance
boundaries.

## Invariants

1. Registry entries are descriptive and noncanonical.
2. Critic identity and version are stable and explicit.
3. Discovery is deterministic for the same registry state and query.
4. Compatibility and requirements are declared, not inferred silently.
5. Dependency graphs are acyclic.
6. Registry operations do not execute critics or mutate narrative artifacts.
7. Execution validates freshness against live source revisions.
8. Every produced report uses the Critic Integration Contract and provenance.
9. Registry metadata cannot bypass Reasoning or Transformation authority
   boundaries.
10. Prior registry history is preserved when metadata changes.

## Deferred implementation boundary

The first implementation may provide an in-process registry and register one
deterministic critic. It must prove registration, discovery, compatibility
rejection, dependency-cycle rejection, and zero narrative mutation.

Runtime scheduling, caching, distribution, concurrency, synthesis, and UI are
later systems and are intentionally outside this contract.

