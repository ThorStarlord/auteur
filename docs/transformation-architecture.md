# Transformation Architecture

This document normalizes the transformations already present in Auteur. It is
cross-cutting and does not add a semantic layer to the canonical architecture:

```text
Ontology → Identity → Structure → Realization → Expression
```

## Canonical definition

A transformation is a bounded operation that consumes artifacts or external
inputs, performs declared interpretation, creation, evaluation, transport, or
authority change, and produces explainable outputs with explicit provenance.

A semantic layer, scope, artifact, LLM provider, workflow coordinator, or CLI
command is not itself a transformation merely because it participates in one.

## Families

### Knowledge creation

Discovery, compilation, and generation produce new narrative information,
candidates, or drafts. Outputs are noncanonical by default and require
explicit acceptance before becoming canonical.

### Knowledge evaluation

Validation, extraction, measurement, and projection produce findings,
observations, metrics, or derived representations. Outputs remain derived by
default and do not mutate their inputs.

### Knowledge evolution

Proposal, acceptance, promotion, adoption, and editing/patching change
authority, lifecycle, or accepted revisions. Proposals are noncanonical;
acceptance or promotion creates a new canonical revision; adoption tracks an
existing artifact without rewriting it.

### Boundary crossing

Import and export move information between Auteur and external
representations. Import does not automatically create canonical knowledge;
export does not transfer Auteur authority outside Auteur.

## Transformation categories

| Category | Purpose | Typical output | Default authority |
|---|---|---|---|
| Discovery | Premise or uncertainty → candidate commitments | Story Identity candidate | Candidate |
| Compilation | Preserve meaning while expanding representation | Blueprint or outline | Candidate/derived |
| Generation | Create new material under constraints | Prose or plan candidate | Draft |
| Projection | Change representation without intended new commitments | Graph, Bible, report | Derived |
| Validation | Evaluate invariants or constraints | Findings | Derived |
| Extraction | Identify structured observations | State deltas or facts | Derived |
| Measurement | Compute metrics | Counts, scores, measures | Derived |
| Proposal | Suggest a canonical change | Proposal artifact | Derived |
| Acceptance | Author-approved candidate becomes canonical | New canonical revision | Canonical |
| Promotion | Select a candidate as canonical | Promoted artifact | Canonical |
| Adoption | Track an existing artifact without rewriting it | Provenance baseline | Existing authority preserved |
| Editing/patching | Propose or apply localized changes | Patch or prose revision | Derived until accepted |
| Import | External representation → Auteur artifact | Imported artifact/reports | Imported/derived |
| Export | Auteur artifact → external representation | Markdown/YAML/JSON | External copy |

Compilation preserves source meaning while making it operational. Generation
creates new authorial material. Projection changes representation; extraction
identifies observations from content. A proposal suggests a change; acceptance
changes authority.

## Transformation Contract

Every meaningful transformation should conceptually declare:

```yaml
id:
category:
version:
inputs:
outputs:
executor:
authority_change:
acceptance_required:
may_create:
must_preserve:
must_not_change:
lossiness:
reversibility:
provenance_requirements:
failure_policy:
```

The contract documents inputs, outputs, authority transitions, preservation
rules, information loss, reversibility, provenance, and failure behavior. It
does not require every serializer or trivial command to create a runtime
contract immediately.

Epistemic behavior and executor type are separate. A transformation may be
constructive, interpretive, translational, evaluative, or administrative, and
may be deterministic, AI-assisted, human-authored, or hybrid. `AI-assisted` is
an executor type, not a transformation category.

## Authority and mutation invariants

1. Discovery and generation produce candidates or drafts by default.
2. Validation, extraction, measurement, and projection remain derived.
3. Proposals remain noncanonical.
4. Acceptance or promotion creates a new canonical revision.
5. Adoption records provenance without changing source content.
6. Transformations do not silently mutate inputs.
7. Candidate creation does not overwrite canonical sources.
8. Failed transformations do not leave partially accepted canonical output.
9. Multi-artifact changes are explicit change sets or proposals.
10. Accepted artifacts retain history.
11. Lossy transformations declare what they discard, resolve, invent, summarize,
    or interpret.
12. Orchestration coordinates transformations but does not own semantic output.

## Provenance

Artifact provenance answers what an artifact is, what it depends on, and
whether it is fresh. Transformation provenance answers what operation produced
it and with which context. A conceptual transformation record is:

```yaml
transformation_id:
transformation_version:
category:
executor:
inputs:
outputs:
configuration_hash:
model_context:
lossiness:
reversibility:
acceptance:
status:
diagnostics:
failure_reason:
```

Transformation records complement artifact sidecars; they do not duplicate
artifact lifecycle, content hash, or dependency metadata.

The artifact dependency graph answers:

```text
What becomes stale when this artifact changes?
```

The transformation graph answers:

```text
What process produced this artifact?
```

Both relationships are useful, but this specification does not require a
database or universal graph engine.

## Current alignment

Current operations map to this vocabulary: Story Discovery is Discovery;
Identity-to-Blueprint is Compilation; Cartographer and Bard are Generation;
critics and structure analyzers are Validation; Bible and state extraction are
Extraction; reports and graphs are Projection; structure repairs are Proposal
and Acceptance; provenance adoption is Adoption; and round-trip handlers are
Import and Export.

Known normalization gaps include inconsistent transformation metadata, coupled
draft acceptance and Bible updates, extraction becoming operational state,
patch source-revision checks, and incomplete AI configuration provenance.
These are targeted follow-up concerns, not justification for a generic runtime.

## Progressive adoption

1. Use this vocabulary in architecture and operation documentation.
2. Document selected transformation contracts without changing runtime design.
3. Attach transformation identity, input revisions, executor, configuration,
   and lossiness where provenance matters.
4. Normalize verified acceptance and mutation inconsistencies only when needed.

Recommended pilots are `identity.compile_blueprint`,
`realization.generate_expression`, and `candidate.accept`.

The Expression pilot applies the lifecycle boundary explicitly: stale prose
cannot be accepted normally; aligned revalidation creates a metadata revision;
intentional divergence requires author acknowledgement, rationale, and an
explicit divergent acceptance action; later relevant dependency changes reopen
review. Candidate rejection preserves history, and comparison is a derived
text-diff/report operation.

Expression validation separates deterministic contract checks from semantic
prose findings. Structured realization evidence can support outcome and
knowledge findings without making arbitrary natural-language interpretation a
deterministic guarantee. High-confidence contradictions require review or are
blocking when explicitly structured; ambiguous knowledge, unreliable
narration, and style remain advisory.

Upstream proposals record target revision and projected hash. Target changes
make proposals stale; proposal application is never automatic.

`expression.compose_chapter` is a focused deterministic Projection. It creates
a derived, versioned Chapter Expression assembly from accepted Scene
Expressions, preserving Scene IDs, selected revisions, stable internal
markers, and transition ownership. Its acceptance selects an assembly snapshot
without changing canonical Scene or upstream artifacts.

Composition inspection and export remain derived boundary operations. Clean
exports intentionally remove traceability markers, while marked exports retain
them for future reconciliation. External manuscript inspection reports section
ownership and divergence but does not apply edits automatically.

`expression.reconcile_chapter` is a bounded derived inspection/proposal
transformation. It records source assembly and imported manuscript provenance,
classifies ownership, and creates noncanonical proposals. Proposal application
and canonical authority changes remain outside this pilot.

`expression.reconcile_chapter` records imported manuscript provenance and
creates derived findings and proposals. It does not apply proposals or change
canonical authority.

## Non-goals

This specification does not introduce a generic transformation runtime,
workflow DSL, event-sourcing system, transformation database, universal graph
engine, visual workflow editor, automatic semantic rewriting, or automatic
candidate acceptance.
