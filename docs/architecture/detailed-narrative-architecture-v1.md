# Detailed Narrative Architecture V1

Status: proposed for human architecture review. Documentation only. No model
calls, extraction experiments, schema implementation, or Global Map
implementation are part of this document.

## Decision summary

Auteur should use one authoritative narrative history, projected into current
state and rebuildable reasoning views:

```text
accepted direction and realization artifacts
        â†“
accepted history + provenance
        â†“
deterministic current-state projection
        â†“
declared and deterministic relationship/dependency index
        â†“
rebuildable Global Map
        â†“
planning intent + question + horizon
        â†“
rebuildable Focus / Decision Map
        â†“
non-authoritative recommendation
```

The Global Map is a derived view, never a second canonical narrative store.
Focus is a relevance projection over that view, never an authority boundary.
Interpretive relationships may enrich reasoning, but confidence cannot promote
them to canon.

## Current-main provenance

This reconciliation branch starts from `origin/main` at
`a6f7ded7d01cfdd149c526a71e0c751af517e0b1`. The previous candidate was
`b735b90e557bdf4f1475a29b0ae1f58a00958044`, based on
`7544b5c6ff4ef6d9520b544cd92de4807aacc84e`. Current main contains later V3,
V1, and V1.1 research commits absent from the candidate. The prior documents
were ported as content; divergent research ancestry was not merged.

Verified merge base: `1053154f3d23893e2ce6a4e48fa5cb16b2d459ed`.
Representative current-main commits absent from the candidate are V3 result
recording (`d33394e`, with result commits `b6a2d6c` and `5a86e32`), Story-Instance
Relationship Extraction V1 (`dfa5191`), and V1.1 (`a6f7ded`).

## Repository evidence reviewed

The workspace had unrelated uncommitted experiment files; none were changed.

Reviewed evidence includes:

- `docs/architecture-constitution.md`, `docs/narrative-architecture.md`,
  `docs/architecture.md`, and `docs/architecture-roadmap.md`;
- `docs/revision-and-staleness-semantics.md`;
- the accepted repeated Map/Focus contract and its implementation boundary;
- ADRs 012, 013, 015, and 018;
- `src/auteur/series/`, `relations/`, `impact/`, `provenance/`,
  `canonical_story.py`, `bible.py`, `narrative_realization/`, and
  `commitment/`;
- Archive of Lies fixtures under
  `tests/fixtures/archive_of_lies_vertical_slice/` and
  `tests/fixtures/repeated_map_focus_v2/`; and
- the V1 candidate ledger, V2 result, and qualifying V3 result under
  `docs/research/global-map-architecture-value-v1/`,
  `docs/research/global-map-architecture-value-v2/`, and
  `docs/research/global-map-architecture-value-v3/`;
- `docs/research/story-instance-relationship-extraction-v1/` and
  `docs/research/story-instance-relationship-extraction-v1-1/`.

The qualifying V3 run is
`docs/research/global-map-architecture-value-v3/runs/20260829-agent-native-sonnet-opus-v3/result.md`.
It is representation-value evidence, not authorization for extraction or
production Global Map implementation.

## Existing architecture that remains authoritative

The five semantic layers remain unchanged: Ontology, Identity, Structure,
Realization, Expression. Universe, Series, Book, Chapter, and Scene remain
scope containers, not layers. Authority remains Canonical, Derived, or
Candidate; publication is not acceptance. Existing source-to-target dependency
direction means `source affects target`.

The Constitution remains the governing boundary: accepted author contracts are
canonical, derived outputs cannot replace them, stale inputs block unsafe
promotion, history is inspectable, and failed workflows are atomic.

Current mechanisms worth reusing are `SeriesIdentity` and `DependencyEdge`,
accepted Series/Book Direction and realization bundles, ordered
`StateTransition` plus `CanonicalState`, `ArtifactStore` revisions and hashes,
relation and impact projections, and the narrow repeated Map/Focus selector.
The portfolio commitment service remains workflow infrastructure, not the
semantic owner of Series Direction commitments.

## Research findings retained

- Long-horizon reasoning needs explicit accepted history, currentness,
  relevance, and provenance together.
- Currentness and relevance are different: old facts can reactivate.
- Superseded facts remain useful historical evidence.
- Grouping consequences under a carried Series pressure can be more useful than
  a flat list.
- State compatibility is a deterministic safety filter.
- V3 demonstrated incremental value beyond shipped Map/Focus for a narrow richer
  representation: A and B were each 6/6/3, while C was 13/2/0; in paired
  P03/P05, C was 4/2/0 and B was 0/3/3.
- Explicit pressure grouping is PROMISING and causal/supporting-history trace
  is the strongest demonstrated C-over-B mechanism. Dormancy/reactivation is
  useful but does not explain C-over-B by itself. Explicit incompatibility is
  promising but not decisive; REL-10 remains UNCLEAR.
- The full 33-item ledger is not justified wholesale.
- No evidence establishes a universal relationship ontology, reliable
  open-world extraction, cross-story generalization, or human usability.

## Research work suspended

Further Story-Instance Relationship Extraction experiments are suspended until
an implementation failure creates a concrete empirical question. V3 supplies
enough representation-value evidence to design the architecture; automatic
extraction is a separate reliability question. V1/V1.1 define that narrower
question, while invalidated attempts do not contribute product evidence. Do not
start another attempt, harness, or production extraction from this review.

## Core architectural model

Authoritative source artifacts are revisioned accepted Direction, Structure, and
Realization artifacts. Each accepted revision has stable identity, revision,
content/projection hashes, acceptance provenance, and the source decision that
accepted it. A new accepted revision supersedes the current one without
erasing the old one.

Canonical current state is a deterministic projection of accepted realization
history in narrative order. It is not a replacement for history.

Relationships and dependencies are an index of links among sources and facts.
Declared relationships inherit authority from their accepted owner.
Deterministic relationships are derived. Interpretive relationships are
candidate/derived reasoning evidence and require explicit author ratification
if they are ever to represent authorial intent.

The minimum pipeline is:

1. Load accepted source revisions within scope and horizon.
2. Validate refs and dependency freshness.
3. Preserve ordered accepted history.
4. Project current values by subject/attribute with deterministic supersession.
5. Build declared and deterministic relationship/dependency edges.
6. Build a full Global Map with source refs and derivation metadata.
7. Apply intent, question, options, and horizon to select Focus.
8. Produce a non-authoritative recommendation.
9. Require explicit author action for Direction or realization changes.

No step writes a derived result into a canonical source.

## Authority and source-of-truth matrix

| Knowledge | Layer/scope | Canonical owner | Stored or derived | Provenance and change boundary |
|---|---|---|---|---|
| Series Direction | Identity/Series | accepted Series Direction | stored, revisioned | author acceptance only; Map/LLM cannot mutate |
| Book/Entry Direction | Identity/Book | accepted Book Direction | stored, revisioned | explicit acceptance against current Series source |
| Direction commitments | Identity/Series or Book | owning accepted Direction | stored with owner revision | author acceptance; realization reports fulfillment only |
| Structure plans | Structure/Series or Book | accepted plan | stored, revisioned | explicit plan acceptance |
| accepted Realization | Realization/Book+ | accepted realization bundle | stored, revisioned | explicit realization acceptance |
| Canonical State | Realization/requested scope | none independently | derived projection | rebuild from accepted bundles and transition lineage |
| accepted transitions | Realization | accepted bundle | stored in history | supersession never deletes them |
| superseded transitions | Realization | accepted history | derived status | later same subject/attribute transition |
| rejected/unaccepted proposals | Candidate/owner scope | proposal history | stored candidate | never canonical projection input |
| commitment fulfillment | Identity/Series or Book | commitment owner plus realization evidence | derived; explicit resolution may be stored | recompute after upstream change |
| planning intent | cross-cutting/Book | planning session | stored workflow input | relevance trigger only |
| dependencies | cross-cutting | declared owner/manifest | declared plus derived traversal | source/target refs and edge origin |
| relationship vocabulary/types | Ontology | accepted ontology vocabulary | stored concept definitions | ontology authority only |
| story-instance relationships | owning narrative scope or derived cross-cutting index | accepted owner only for declared relations | declared, deterministic, or interpretive | source/target facts, origin, evidence, revision, disposition |
| Global Map | cross-cutting/Series/horizon | none | derived, rebuildable | source revisions and derivation version |
| Focus / Decision Map | cross-cutting/Book | none | derived proposal | Map, intent, question, horizon refs |
| recommendations | decision session | none | Candidate/derived | exact inputs and producer provenance |
| impact/staleness reports | cross-cutting | none | derived | dependency path, hashes, revisions |

There is no second canonical database for Global Map, relationship index, or
current state. Persisted caches are disposable accelerators with source
fingerprints, never hidden authority.

## Canonical history versus current state

An accepted transition has at minimum:

```yaml
transition_id: admission-retracted
subject: council
attribute: archive_position
before: admitted fraud
after: retracted admission
order: [book-2, realization-03]
source: {artifact_id: realization-bundle-book-2, revision: 1}
```

The exact schema is implementation work; the semantics are fixed here.
History contains both `public-admission` and `admission-retracted`, their order,
explanations, and source revision. Current projection selects `retracted
admission` and marks the former superseded. Causal queries may traverse the
superseded admission; current-state queries must not present it as current.

Rebuild starts empty, applies accepted bundles in narrative order, and for each
subject/attribute retains the latest applicable transition as current while
retaining every transition in history. Ambiguous order or conflicting
provenance yields a diagnostic, not silent selection.

## Relationship origin model

The three-origin model is sufficient for V1 if origin is mandatory and
consumers treat origins differently. Ontology owns relation type definitions;
an assertion between actual accepted story facts does not become Ontology just
because it uses an ontology-defined type.

### Declared

An author writes a relationship in an accepted owner: a commitment governs
Books 1â€“4, Book 1 sets up a mystery, or Arc A depends on event B. The edge is
canonical only to the extent its owner is canonical, and carries owner revision
and rationale.

### Deterministic

The system derives supersession, current transition, accepted realization
fulfillment, explicit setup/payoff, or a dependency from accepted data and a
named rule. It is rebuildable, versioned, and never a new authorial fact.

### Interpretive

The system or author may propose that A motivates B, facts form a pressure, or
a motif reinforces a theme. The record contains interpreter, evidence refs,
procedure/model metadata, confidence, and status. Confidence changes ranking,
not authority. Rejection is durable negative evidence; it does not rewrite
events or state.

## Minimum relationship vocabulary

| Family | Disposition | V1 use |
|---|---|---|
| `depends_on` / `affects` | BUILD/DECLARE + DERIVE | core direction and impact traversal |
| `supersedes` | DERIVE | ordered state lineage |
| `fulfills` / `satisfies` | DERIVE, explicit resolution when needed | commitment evidence |
| `setup -> payoff` | DECLARE/DERIVE | only with explicit IDs or narrow rules |
| `carries` / `governed_by` | DECLARE/DERIVE | existing commitment refs |
| `incompatible_with` | DERIVE | state/options safety filter |
| pressure/group membership | DECLARE, DERIVE, or INTERPRET | explicit grouping is valuable; origin remains visible |
| dormant -> reactivated | DERIVE | local relevance disposition |
| unresolved -> resolved | DERIVE + resolution evidence | question history |
| source/provenance | BUILD | mandatory metadata relation |
| `causes` | INTERPRET unless explicitly declared | no automatic causal truth |
| `supports` | INTERPRET/DECLARE | only with clear owner/consumer |
| motif/theme reinforcement | DEFER/INTERPRET | not needed in first slice |

Pressure groups have the same three possible origins as other story-instance
relationships. For Archive of Lies, grouping by a shared carried accepted
commitment may be a narrow deterministic derivation. Arbitrary semantic
grouping remains interpretive/candidate work and is never promoted by
confidence. V3 demonstrates the value of preserving the grouping relation, not
the universality of deterministic pressure inference.

The 33-item ledger is research evidence, not a production schema. Its
currentness, grouping, reactivation, incompatibility, and provenance jobs are
covered above; broad causal and thematic claims remain interpretive or deferred.

## Commitment and trajectory model

Direction commitments are authorial promises, not realized facts. They belong
to the accepted Direction that owns them and may be carried by accepted Book
Directions. Their authority lifecycle is `active`, `retired`, or `superseded`
when the owner explicitly changes them. Their fulfillment view is
`unfulfilled`, `partially_satisfied`, or `satisfied`.

Fulfillment evidence comes from accepted realization using explicit resolution
IDs, setup/payoff refs, or a deterministic rule accepted for that commitment
family. An LLM claim cannot satisfy a commitment. Deliberate retirement without
fulfillment is an authorial decision with provenance, shown as retired history.

When upstream canon changes, fulfillment is recomputed; its previous assessment
remains inspectable. The Global Map shows trajectory, status, evidence, and
unresolved consequences. Focus includes it only when relevant.

The existing portfolio commitment execution service is a workflow commitment
system with its own execution states. It can orchestrate work but does not own
Direction commitment semantics.

## Global Map

The full internal map answers what the story is, what was committed, what
happened, what is current, which trajectories and pressures are active, what is
unresolved, what depends on what, and what a revision affects.

```text
MapSnapshot
  scope + horizon + source_revision_set
  direction summaries and accepted history refs
  current state with transition lineage
  commitment trajectories and fulfillment evidence
  declared/deterministic index; interpretive edges by status
  unresolved questions and active pressures
  impact/freshness metadata + derivation version
```

The map contains compact summaries and refs, not duplicated canonical payloads.
Every source artifact/revision and derivation version is recorded. A source
revision, rule version, relationship correction, or scope/horizon change makes
the snapshot stale. Incremental updates may recompute affected branches, but a
full rebuild must be semantically equivalent.

Deleting the Map or relation index deletes a view only. Rebuild reads
authoritative sources. Any non-rebuildable interpretive candidate must be
preserved as an explicit non-canonical record, not hidden state.

## Focus / Decision Map

Focus is a relevance projection over the full map. Inputs are planning intent,
explicit accepted refs, question/options, horizon, active commitments,
dependencies, bounded causal ancestors/descendants when available, state
constraints, and reactivated trajectories.

The selector enforces accepted authority and horizon; includes explicit refs,
active commitments, current constraints, and bounded dependencies; reactivates
dormant facts only through explicit triggers; groups shared-pressure facts;
prioritizes constraints and direct triggers; and preserves exact refs behind
compact explanations. It returns one bounded question, options, rationale,
tradeoff, and recommendation basis.

Focus does not create authority, rewrite canon, accept an interpretation, delete
omitted history, or imply recent means relevant. Choosing an option records
workflow history only. A stale or incompatible proposal is rejected or
recomputed before author action.

## Revision and impact propagation

An accepted earlier fact changes through a new accepted source revision. No
downstream accepted artifact is edited. Declared and deterministic dependency
edges are traversed; dependents are checked against recorded revisions and
projection hashes.

- `VALID`: dependencies and required projections match.
- `STALE`: a dependency changed; the artifact remains structurally valid but
  requires recomputation or review.
- `SUSPECT`: an interpretation is no longer adequately supported and needs
  semantic review.
- `CONTRADICTORY`: accepted downstream content conflicts with new current state
  or an explicit invariant; it remains historical accepted work but cannot be
  used as compatible current guidance.

Traversal, hashes, current-state rebuild, supersession, incompatibility, and
Map/Focus recomputation are deterministic. Causal, motivational, thematic, and
pressure interpretations require review. Derived views rebuild or become
stale; accepted downstream canon remains untouched. Reconciliation produces a
proposal/report and waits for author authority.

## Provenance and rebuildability

Every derived item carries artifact IDs, revisions, fact/transition IDs, rule
version, and relation origin. Interpretive items also carry evidence refs,
producer/procedure metadata, confidence, and acceptance/rejection status.

| Derived artifact | Rebuildable? | If deleted |
|---|---|---|
| current state | YES | no loss |
| supersession lineage | YES | no loss |
| declared/deterministic index | YES | no loss |
| interpretive candidates | YES only if candidate records persist | rationale/evidence lost otherwise |
| Global Map | YES | no loss |
| Focus / Decision Map | YES from Map + intent/question | prior proposal history only is lost |
| impact/staleness report | YES | no loss |
| compiled Bible/state report | YES | no loss |
| author rejection of interpretation | NO as a mere cache | preserve as workflow/evidence history |

## Scaling and context projection

At about 10 entries, the full map may render with history and direct refs. At 50
entries, use grouped trajectories and bounded traversal. At 100+, use indexed
scope/horizon queries, compact provenance, and progressive disclosure.

Filtering is deterministic: authority, horizon, explicit refs/constraints,
bounded ancestors/descendants, grouping, then priority. Summaries orient only;
exact evidence remains available for acceptance, contradiction, revision, and
recommendation claims.

## Interpretive-relation failure

â€œA causes Bâ€ lives in a versioned derived/candidate record, never canon unless
the author explicitly declares an equivalent relationship in an accepted
artifact. If the author says the events are merely correlated, preserve the
rejected interpretation and correction, mark dependent analyses suspect/stale,
remove the edge from causal traversal, rebuild views, and suppress the same
proposal using its rejected evidence/signature. Later ratification is a new
author decision at a named scope/revision; it does not validate other inferred
edges or alter event history.

## Golden-ledger crosswalk

Identity/Direction rows are already represented by Series and Book Direction.
State rows are represented by accepted transitions and current-state
projection. Explicit resolution, supersession, source refs, and unaccepted
proposals should remain production behavior. V3 demonstrates incremental value
from preserving explicit pressure grouping and causal/supporting-history trace,
but their origins must remain visible. Dormant reactivation and incompatibility
remain useful projection jobs; they are not evidence for universal inference.
Causal chains, psychological motivation, thematic reinforcement, and the full
33-item ledger remain interpretive/research-only until an author-owned contract
requires them. Lantern irrelevance is a fixture test of filtering, not a
universal concept.

## Worked Archive of Lies trace

Using `tests/fixtures/repeated_map_focus_v2/`:

1. Series Direction establishes `contested-history` and `commitment-falsifier`.
2. Book 1 accepts forged founding record, preserved monastery testimony, and
   broken lantern.
3. Book 2 names the falsifier and records ordered admission then retraction;
   the falsifier resolves and retraction is current.
4. Book 3 accepts treaty-protected archive and repaired lantern; treaty is
   current and lantern facts remain accepted but irrelevant to Book 4.
5. Current state is rebuilt from all accepted transitions.
6. Relationships derive from carried commitment, resolution, supersession,
   explicit Book 4 refs, and incompatibility.
7. Global Map groups founding fraud, retraction, and treaty protection under
   the active pressure while retaining exact refs and lineage.
8. Book 4 intent reactivates monastery testimony and retains treaty as current
   constraint; unaccepted burn-archive is excluded.
9. A recommendation may prefer verified testimony over burning the archive,
   with rationale and tradeoff, but remains non-authoritative.

If the Book 2 retraction changes, the new revision invalidates the old Map and
Focus source set. Current state changes; downstream plans become stale and
interpretations relying on the old retraction become suspect. A Book 4 proposal
using old inputs cannot execute. Rebuild produces a new Map and Focus; accepted
downstream artifacts remain accepted but may be contradictory. Reconciliation
shows paths and asks the author whether to revise, acknowledge, or preserve the
divergence.

## Proposed minimum production model

| Entity | Layer/scope | Authority | Reasoning job |
|---|---|---|---|
| AcceptedArtifactRevision | owning layer/scope | canonical | stable accepted source history |
| AcceptedRealizationBundle | Realization/Book+ | canonical | ordered event/state history |
| StateEvidence | Realization/requested scope | derived | current value plus lineage |
| RelationshipRecord | owning narrative scope or derived cross-cutting index | declared/derived/candidate | origin/evidence-aware story-instance links |
| CommitmentAssessment | Identity/Series or Book | derived plus explicit resolution | trajectory fulfillment |
| MapSnapshot | cross-cutting/Series/horizon | derived | full continuity view |
| PlanningIntent | cross-cutting/Book | non-canonical input | current relevance trigger |
| DecisionMapProposal | cross-cutting/Book | candidate/derived | bounded decision context |
| ImpactReport | cross-cutting | derived | explain propagation/status |
| InterpretationRecord | cross-cutting | candidate/derived | corrigible semantic judgment |

No universal graph database, lifecycle field, or entity for every ledger row is
justified.

## Existing-code crosswalk

| Area | Classification | Reason |
|---|---|---|
| `narrative_ontology` | REUSE AS-IS | concept vocabulary boundary |
| `identity`, `book`, `series` | EXTEND carefully | existing Direction/Series owners and refs are correct |
| `narrative_blueprint`, `structure` | REUSE AS-IS for structure | completeness stays separate from continuity |
| `narrative_realization` | EXTEND | transitions/bundles need richer lineage only as proven |
| `bible.py`, canonical-state paths | EXTEND selectively | expose cross-book lineage without replacing sources |
| `series/repeated_map_focus.py` | EXTEND | correct seam for generalized deterministic selection |
| `series/vertical_slice_*` | REUSE/EXTEND | acceptance, refs, fixtures, and Focus boundary exist |
| `relations` | EXTEND | preserve explicit changes; align origin/provenance |
| `impact` | REUSE/EXTEND | traversal/report machinery exists |
| `provenance` | REUSE AS-IS first | revisions, hashes, projections, atomic writes exist |
| `commitment` | REUSE AS-IS as workflow | distinct from narrative commitment semantics |
| `reconciliation` | EXTEND | author review for stale/contradictory work |
| `roundtrip` | REUSE AS-IS | controlled import/export remains valid |
| LLM orchestration | DEFER | deterministic continuity proof needs no model |

## Gap matrix summary

See [`detailed-narrative-architecture-v1-gap-matrix.md`](detailed-narrative-architecture-v1-gap-matrix.md).
The principal gap is composition of accepted multi-Book history,
current-state lineage, dependency impact, and revision-aware Map/Focus beyond
the current narrow sliceâ€”not a missing universal graph.

## Architecture-section reconciliation

| Section | Status | Evidence |
|---|---|---|
| authority and source of truth | UNCHANGED | Constitution and accepted artifact boundaries remain current |
| canonical history/current state | UNCHANGED | Current realization and provenance contracts preserve revision and projection |
| relationship origins | TIGHTENED | V3 gold separates ontology types from instance assertions and preserves origin |
| minimum vocabulary | TIGHTENED | V3 prioritizes causal support and pressure grouping without adopting all 33 items |
| commitments/trajectories | UNCHANGED | Direction and fulfillment ownership remain separate |
| Global Map | UNCHANGED | V3 strengthens derived representation value, not Map authority |
| Focus / Decision Map | TIGHTENED | V3 shows persistent grouping must survive projection |
| revision/impact | UNCHANGED | Existing provenance and reconciliation boundaries still apply |
| rebuildability | UNCHANGED | No evidence requires hidden derived authority |
| scaling/context | UNCHANGED | No new evidence changes progressive disclosure |
| interpretive correction | TIGHTENED | Causal/supporting-history edges may be interpretive and corrigible |

## Death-test results

The reconciled suite contains D1-D13; D13 is the additional pressure-group
projection invariant.

D1â€“D12 are defined in
[`detailed-narrative-architecture-v1-death-tests.md`](detailed-narrative-architecture-v1-death-tests.md).
The proposed model passes each test by preserving accepted history, separating
current projection from lineage, treating derived views as rebuildable, and
requiring explicit author reconciliation for downstream change. They are
architecture acceptance criteria, not current implementation evidence.

## Recommended vertical slice

The exact implementation-proof plan is in
[`detailed-narrative-architecture-v1-vertical-slice.md`](detailed-narrative-architecture-v1-vertical-slice.md):
Archive of Lies, accepted Series plus Books 1â€“3, current state, declared and
deterministic relationships, Global Map, Book 4 Focus, one non-authoritative
recommendation, one upstream revision, impact propagation, and rebuild.

## Explicitly rejected or deferred architecture

Defer universal graph ontology, graph database storage, entity-per-ledger-row
models, universal lifecycle semantics, open-world LLM extraction, automatic
semantic rewriting, thematic/psychological inference as a required dependency,
and a full Map serialized into every prompt. Defer these until a concrete
implementation failure proves the narrower architecture insufficient.

## Candidate ADRs

No ADR is created in this task. Existing ADRs 012, 013, 015, and 018 cover the
durable foundations, and this architecture is still proposed for human review.
After review, create at most one ADR if implementation depends on freezing the
decision that Global Map/Focus and relationship indexes are rebuildable views
over accepted source revisions, with interpretive edges non-authoritative and
corrigible. Its alternatives are a second canonical graph or fully ephemeral
analysis; neither is suitable for the stated authority/rebuild requirements.

## Open questions

- Which exact accepted-realization artifact is the first cross-book transition
  lineage contract?
- Should `SUSPECT` and `CONTRADICTORY` extend provenance health, or remain
  impact/Map classifications?
- What explicit author action ratifies a declared relationship beyond current
  `relation_changes.yaml`?

## Validation

The required `scripts/probe-repo.py` was attempted but is absent from the
checkout, so no probe metrics are claimed. No model or empirical experiment
calls were made. Validation is documentation inspection and the existing
fixture/code crosswalk; unrelated baseline failures were not repaired.

## Git / PR

Branch: `architecture/detailed-narrative-architecture-v1-reconciled`, from
`origin/main` at `a6f7ded7d01cfdd149c526a71e0c751af517e0b1`. No publication or PR
was performed yet.
Pre-existing dirty experiment files remain untouched.

## Recommendation

Approve this as a review candidate, resolve the open questions, then implement
only the companion vertical slice with explicit pressure grouping and
causal/supporting-history inputs, without requiring automatic extraction.

DETAILED NARRATIVE ARCHITECTURE V1:
RECONCILED - READY FOR HUMAN ARCHITECTURE REVIEW
