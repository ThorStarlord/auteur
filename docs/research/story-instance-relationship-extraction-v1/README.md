# Auteur — Global Map — Story-Instance Relationship Extraction Experiment V1

**Status:** PREREGISTERED — NOT EXECUTED

**Design revision:** `v1.0`

**Starting point:** V3 closure merge `d33394e4d0bb905bb68f82e12cfbeb12cd9aad8b`

This is a research-only protocol. It does not define a production schema,
modify the narrative ontology, implement Global Map, or authorize extraction.
The companion [gold reference](gold-reference.md) and
[execution/evaluation contract](execution-and-evaluation.md) are part of this
preregistration and must be frozen together before execution.

## 1. Consequential research question

When the accepted narrative fact set is held constant, does a minimal,
source-backed story-instance relationship overlay improve whole-story
decision reasoning at the V3 Book-4 mechanism family, and can an independently
extracted overlay recover the value of the frozen gold overlay without
unacceptable unsupported relations?

This operationalizes two separate questions:

1. **Extraction fidelity:** can the extractor recover supported causal and
   pressure-grouping relations from accepted history without seeing the gold
   answer key, while abstaining when evidence is insufficient?
2. **Downstream value:** does the relationship overlay improve the same bounded
   decision task that exposed the V3 C-over-B difference, with no additional
   narrative facts?

Extraction quality and downstream decision quality are reported separately.

## 2. Why this follows V3

V3 supplied its clearest incremental evidence in the paired P03/P05 Book-4
family. Condition C preserved a causal/supporting-history trace and grouped
the founding-record, retraction, and treaty-protection consequences as one
`contested-history` pressure. Condition B contained the same underlying
accepted facts but did not preserve that grouping for P05. The result did not
show that every item in the 33-entry ledger was valuable; REL-10 was explicitly
unclear and is not a V1 target.

V1 therefore isolates the smallest supported mechanism: persistent
story-instance causal support and pressure grouping. It does not re-test the
full C architecture package.

## 3. Mechanism under test

The target is **persistent relationship structure**, not current retrieval.
The primary relation family is:

```text
accepted historical facts
        ├── causal/supporting-history relation ──> later accepted constraint
        └── collectively instantiate ────────────> persistent pressure
```

For the Book-4 family, the target structure is:

```text
admission-retracted
        CAUSALLY_SUPPORTS / MOTIVATES
archive-protected

founding-record + admission-retracted + archive-protected
        INSTANTIATE
contested-history pressure
```

The overlay may label each member's role as originating history, causal pivot,
or current constraint. These roles describe the relation's place in the
persistent trajectory; they are not new canon.

Current planning intent is deliberately downstream of extraction. It is used
by the ordinary B0 Map/Focus context and decision prompt to select or reactivate
what matters now. It is not supplied to the extractor and does not create the
persistent relation. The Book-4 overlay itself is never relevance-filtered
after extraction: the same overlay is presented unchanged to P03, P04, and
P05. This prevents V1 from measuring a relevance/retrieval effect while
claiming to measure relationship extraction.

## 4. Existing architecture fit

The current authoritative architecture distinguishes Ontology, Identity,
Structure, Realization, and Expression. The relevant source ownership is:

- accepted Series Direction and commitments: Identity/Structure at Series
  scope;
- accepted Book Directions: Structure at Book scope;
- accepted realization bundles and state transitions: Realization;
- Canonical State: deterministic projection of accepted realization history;
- Map/Focus: derived, non-authoritative current-planning projection;
- author choices: workflow history, not automatic canon.

The existing ontology already provides concept-level relationships such as:

- `Character -> Goal`;
- `Goal -> Conflict`;
- `Setup -> Payoff`;
- `Payoff -> Setup`;
- `Arc -> Beat`, `Arc -> Conflict`, and `Arc -> Theme`;
- `Theme -> Arc` and `Theme -> Symbol`; and
- a generic `Relationship` concept connecting narrative entities.

Those declarations say what kinds of narrative concepts may relate in theory.
They do not assert that a particular accepted transition caused another
particular transition, nor that a set of accepted facts instantiates one
persistent pressure in this story.

The repository's operational distinctions are preserved here: Direction owns
accepted narrative plans and commitments; Realization owns accepted events and
state changes; Canonical State is rebuilt from those accepted transitions;
continuity/Map relevance is a derived projection rather than an authority
state; and fulfillment/resolution is a derived reading of accepted history,
not permission to rewrite the source. Where a dependency is described, the
repository convention is `source affects target`. This protocol applies that
direction to instance relations while keeping all source ownership unchanged.

V1 therefore uses a research-local overlay vocabulary. It does not add a
production `NarrativeRelation`, `NarrativePressure`, lifecycle field, graph
store, or ontology primitive.

The claim ceiling is closed-world and bounded: V1 can test whether Auteur
recovers relevant relations within the preregistered `CAUSAL_SUPPORT` and
`PRESSURE_GROUP` families and this target fixture. It does not test arbitrary
open-world narrative-relation discovery, completeness of a universal
relationship ontology, or general Global Map extraction.

## 5. Hypotheses

### H1 — Minimal relationship value

`R-GOLD` will perform better than `B0` on the primary P03/P05 downstream
criteria, especially causal trace, pressure grouping, and preservation of the
current treaty constraint.

### H2 — Extraction recovery

`R-DERIVED` will retain most of the `R-GOLD` downstream advantage if extraction
recovers the primary relations with adequate grounding, role accuracy, and
abstention discipline.

### H3 — Currentness separation

On the P02 control, where the current retraction and resolved falsifier are
already sufficient and the Book-4 treaty has not yet occurred, the relationship
overlay will not materially improve decision quality. Any gain there is not
counted as evidence for the Book-4 mechanism.

### H4 — Authority preservation

Neither gold nor derived relationships will be treated as accepted authorial
fact. Every overlay item will carry source references and an authority class;
model confidence will not raise authority.

## 6. Experimental conditions

All conditions receive the same accepted narrative facts, current state,
planning intent, question, bounded options, generic output contract, and model
role configuration.

### B0 — Current Map/Focus

The shipped repeated Map/Focus representation, using the frozen accepted
source boundary and the same neutral adapter used by V3 Condition B. No
relationship overlay is added.

### R-GOLD — Minimal gold overlay

`B0` plus only the minimal gold relation entries listed in
`gold-reference.md`. The overlay contains structure over facts already present
in B0; it may not add facts, recommendations, evaluator signals, hidden labels,
or additional ledger concepts.

### R-DERIVED — Extracted overlay

`B0` plus an overlay produced by the preregistered extractor from accepted
history. It uses the same relation vocabulary, fields, source-reference rules,
member-role budget, and maximum entry count as `R-GOLD`. The extractor never
sees the gold reference, expected relation IDs, evaluator rubric, condition
names, or downstream target answers.

The extractor retains a rich record for extraction evaluation, but the
downstream treatment is a separate canonical structural projection. For both
R-GOLD and R-DERIVED, the generator sees only:

```json
{
  "relation_type": "CAUSAL_SUPPORT | PRESSURE_GROUP",
  "source_fact_refs": ["B0-visible-fact-identity"],
  "target_ref": "B0-visible-fact-or-commitment-identity",
  "member_roles": [{"fact_ref": "B0-visible-fact-identity", "role": "..."}],
  "authority_class": "DETERMINISTIC_DERIVATION | INTERPRETIVE"
}
```

The canonical rendering is deterministic: relation entries are ordered by
`relation_type`, then target identity, then sorted source/member identities;
group members are sorted by fact identity. It contains no extractor rationale,
support/confidence field, or free-form explanatory prose. A provenance
reference may appear only when the same source identity is already present in
B0; otherwise provenance remains in the evaluation record and is not shown to
the downstream generator.

The downstream packet uses an opaque condition label. `B0`, `R-GOLD`, and
`R-DERIVED` are never disclosed to the generator or evaluator.

## 7. Information parity

The following must be byte-identical or semantically identical across the three
downstream conditions for a given probe:

- accepted Series/Book facts and source horizon;
- current state and source provenance;
- current planning intent;
- question and options;
- generic recommendation output contract;
- model configuration, startup context, and tools;
- packet length budget, apart from the bounded overlay block; and
- downstream evaluator input and rubric.

The only assigned treatment is the presence and contents of the relationship
overlay. `R-GOLD` is not allowed to contain facts merely because they appear
in the full V3 ledger. `R-DERIVED` is not allowed a larger overlay or richer
explanations than `R-GOLD`.

The same fact may appear in B0 and as a relation member. That is intentional:
the treatment is the explicit connection among already-visible facts.

## 8. Fixtures and probes

The frozen Archive of Lies fixture remains the sole source fixture. V1 is a
mechanism-isolation study, not a broad benchmark.

- **Primary family:** P03 and P05, the same Book-4 horizon and pressure
  cluster. P03 tests downstream decision quality; P05 tests compact grouping
  and irrelevance handling. They count as one independent family.
- **Adversarial companion:** P04, the same Book-4 horizon with the
  state-incompatible `burn-archive` option. This checks that relationship
  structure does not erase current-state compatibility.
- **Control:** P02, the Book-3 horizon before `archive-protected` exists. The
  target Book-4 relation overlay is empty at this horizon, so a material
  overlay advantage is not expected. P02 is downstream-only; it is not used to
  expand the extraction target with unrelated earlier relations.

P01 is excluded from the downstream sample because it tests the earlier
  dormancy/currentness failure mode rather than the V3 relationship mechanism.
It remains part of source-history leakage auditing only. This is the smallest
scope that tests the demonstrated family plus one horizon control without
creating a new benchmark.

## 9. Persistent relation versus current relevance

Extraction input is accepted history through the probe horizon:

- accepted Series Direction and commitments;
- accepted Book Directions through the prior Book;
- accepted realization transitions through the prior Book;
- deterministic current-state evidence and transition lineage; and
- stable source IDs and source text needed for citation.

The extractor does **not** receive the current planning intent, options,
question, V3 rubric, or downstream outputs. It extracts persistent relations
from the historical record.

At downstream time, the B0 projection and current planning intent determine
what is surfaced for the decision. The overlay is not a second relevance
engine. The shared Book-4 overlay is presented unchanged to P03, P04, and P05;
the model's use of it is the downstream behavior under test. P02 receives the
preregistered empty overlay because its horizon predates `archive-protected`.

## 10. Gold-reference boundary

The gold set is a minimal subset of the frozen V3 ledger, not the whole
33-item ledger. Its relation IDs, evidence, authority, equivalence policy, and
severity are frozen in [gold-reference.md](gold-reference.md).

The gold set is constructed before any extraction output is produced. Any
proposed change after extraction begins invalidates the run and requires a new
preregistration or explicitly approved protocol amendment.

## 11. Decision gate

The gate is applied only after raw outputs, extraction judgments, downstream
judgments, and reconciliation are frozen and unblinded. It does not
automatically authorize implementation.

### CASE A — Relationship value plus extraction success

`R-GOLD` shows a meaningful, mechanism-specific advantage over `B0` in the
P03/P05 family, and `R-DERIVED` preserves most of that advantage with grounded
relations, acceptable role/grouping accuracy, and no material unsupported
relation pattern.

**Implication:** a small production prototype may be considered in a separate
human-authorized decision. No Global Map implementation is authorized here.

### CASE B — Relationship value, extraction failure

`R-GOLD` helps, but `R-DERIVED` is unreliable, over-groups, invents unsupported
relations, or loses the downstream benefit.

**Implication:** do not productize extraction; investigate extraction
reliability and authority boundaries.

### CASE C — Minimal overlay does not reproduce V3

`R-GOLD` does not show a meaningful advantage over `B0` on the primary family,
even if full V3 C previously did.

**Implication:** the V3 mechanism attribution was incomplete; diagnose before
building relationship extraction.

### CASE D — Noisy or indeterminate

Results are unstable, invalidated, underpowered, or evaluator/model dependent
in a way that prevents a stable comparison.

**Implication:** do not add architecture; investigate fixture, evaluator, or
runtime dependence.

“Meaningful” is defined by the preregistered criterion-level rubric and
paired evidence, not by a single aggregate score or an unapproved threshold.
Human product decision remains required in every case.

## 12. Invalidation conditions

The run is invalidated, in whole or in the affected comparison, if any of the
following occurs:

- gold relations or expected IDs are visible to the extractor;
- filenames, paths, worker prompts, metadata, or labels leak condition or
  relation answers;
- `R-DERIVED` receives facts, context, or a larger representation budget not
  available to `B0`/`R-GOLD`;
- current planning intent, evaluator targets, or downstream answer cues are
  supplied to the extractor;
- condition-specific model, startup context, tool policy, or prompt wording
  changes outside the frozen adapter;
- raw output is replaced by a template, heuristic, parent-agent prose, or
  post-hoc rewrite;
- the gold reference changes after extraction outputs are observed;
- semantic extraction scoring rewards vocabulary matching while rejecting
  source-grounded equivalents;
- an unsupported model-invented fact is promoted into a downstream packet;
- relation extraction is forced to output a relation where abstention is
  warranted;
- evaluator identity is revealed or evaluator receives expected winners or
  condition labels; or
- raw outputs, hashes, manifests, or frozen judgments are overwritten.

The execution contract defines the audit and freeze procedure.

## 13. Explicitly deferred

This preregistration creates no:

- production code or Pydantic model;
- production ontology change or ontology migration;
- Global Map implementation or UI;
- universal relationship/pressure/lifecycle abstraction;
- graph database or extraction runtime;
- new narrative agent;
- model inference call;
- empirical observation; or
- authorization to begin the next experiment after V1.

The relationship vocabulary is research-local and disposable until evidence and
human review justify a separate boundary.
