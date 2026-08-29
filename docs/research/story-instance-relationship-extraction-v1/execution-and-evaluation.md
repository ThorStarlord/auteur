# Story-Instance Relationship Extraction V1 — Execution and Evaluation Contract

**Status:** FROZEN WITH PROTOCOL — NOT EXECUTED

This contract defines a future run. Nothing in it authorizes calls during
preregistration.

## 1. Research-local extraction contract

Each extractor output is a bounded JSON object with exactly these semantic
fields:

```json
{
  "relations": [
    {
      "relation_type": "CAUSAL_SUPPORT | PRESSURE_GROUP",
      "source_fact_refs": ["source-id"],
      "target_ref": "source-id or accepted-commitment-id",
      "member_roles": [{"fact_ref": "source-id", "role": "..."}],
      "authority_class": "ACCEPTED | DETERMINISTIC_DERIVATION | INTERPRETIVE",
      "evidence_refs": ["source-path#stable-anchor"],
      "rationale": "concise source-grounded explanation",
      "support": "strong | moderate | weak"
    }
  ],
  "abstentions": [
    {"candidate_area": "...", "reason": "INSUFFICIENT_EVIDENCE"}
  ]
}
```

The contract is research-local. `relation_type`, source references, target,
roles, authority, evidence, rationale, and abstention exist only because they
are needed for fidelity scoring, provenance, downstream display, or leakage
control. `support` records the extractor's assessment but never changes
authority.

The extractor must not output accepted facts as if they were derived relations.
It must not create a relation solely from confidence or from the question.
Malformed or unsupported output is retained as raw evidence and scored as a
failure; it is not repaired into an observation.

## 2. Execution roles and inputs

### Extractor

Receives accepted history through the probe horizon, stable source references,
the generic research-local relation contract, and no current planning intent.
It produces one relation overlay per independent extraction observation.

### Downstream generator

Receives B0 plus one of the opaque overlays, the same current planning intent,
question, options, and generic bounded recommendation contract used in V3.
It must cite source-faithful facts, not treat relations as canon, and may say
that none of the options is viable when state compatibility requires it.

### Evaluator

Two blinded evaluation streams are kept separate:

1. extraction evaluator sees the source packet, extractor output, and frozen
   gold reference, but not condition labels or downstream outcomes;
2. downstream evaluator sees the generated recommendation and the global plus
   probe-specific rubric, but not condition labels, extraction outputs, gold
   IDs, or expected winners.

Prefer different fixed models for extractor, generator, and evaluator where the
backend permits. Human adjudication remains available for disputed semantic
equivalence or invalidation.

## 3. Conditions and pairing

For each probe, downstream packets contain the same B0 context. The only
condition difference is:

- B0: no overlay;
- R-GOLD: projected frozen gold overlay;
- R-DERIVED: projected extractor overlay using the same schema, maximum entry
  count (two relation entries, with at most three group members), role budget,
  and formatting adapter.

Each observation receives an opaque randomized ID unrelated to condition,
probe, relation count, or worker. The condition mapping is sealed and is not
available to generators or evaluators.

The primary comparison is paired by probe and repetition. P03/P05 are one
Book-4 family for interpretation, not two independent replications. P04 is an
adversarial companion and P02 is the currentness control.

## 4. Repetition and call budget

Three independent extractor observations are produced for the shared accepted
Book-4 history horizon used by P03/P04/P05: **3 extraction calls**. The same
opaque extraction observations feed the corresponding R-DERIVED downstream
packets for all three Book-4 probes; no majority vote or post-hoc selection is
performed. P02 is a downstream-only control with an empty target overlay,
because the Book-4 mechanism is outside its accepted horizon.

For each of four probes, produce three downstream repetitions for each of the
three conditions: **36 generator calls**. B0 and R-GOLD repeat the same frozen
representation; R-DERIVED uses the paired extracted overlay for that
repetition.

Evaluate all 3 extraction outputs once: **3 extraction-evaluator calls**.
Evaluate all 36 downstream outputs once: **36 downstream-evaluator calls**.

Planned total: **78 inference calls** (3 extraction + 36 generation + 3
extraction evaluation + 36 downstream evaluation). The repetitions estimate
extractor stochasticity and generator/evaluator variance without pretending
P03/P05 are independent fixtures. If a backend cannot provide genuinely fresh
contexts or fixed role configuration, execution stops before observations.

## 5. Extraction evaluation

Each output is scored separately for:

- supported relation recovery, with exact endpoint/direction where required;
- semantic equivalence of relation wording;
- source grounding and evidence-reference correctness;
- causal direction and causal-role accuracy;
- pressure-group membership integrity;
- member-role accuracy;
- authority-class accuracy;
- unsupported relation invention;
- over-grouping and under-grouping;
- omission severity by the gold reference; and
- abstention quality when evidence is insufficient or outside the horizon.

String overlap is not sufficient for a correct score. A semantically equivalent
source-grounded relation is accepted; a fluent relation with wrong direction,
unsupported members, or inflated authority is not.

Primary extraction summaries report per-relation and per-probe counts plus
unsupported/abstention rates. No single extraction score determines the gate.

## 6. Downstream evaluation

The evaluator uses the relevant V3 rubric structure while preserving the V1
target. It records criterion-level judgments, rationale, source use,
currentness, option compatibility, and severe failures.

### Primary P03/P05 criteria

- preserves `archive-protected` as the current constraint;
- connects retraction to treaty protection when the relation is relevant;
- groups the founding-record/retraction/treaty consequences as one persistent
  pressure rather than unrelated dormant peers;
- reactivates the monastery testimony only because the current Book-4 intent
  makes it relevant;
- keeps the relationship overlay from becoming new canon; and
- gives a bounded, state-compatible recommendation with a specific tradeoff.

### P04 adversarial criteria

- rejects or marks `burn-archive` incompatible with treaty-protected state;
- does not treat the unaccepted proposal as an accepted fact; and
- preserves the same causal/grouping explanation without hallucinating facts.

### P02 control criteria

- uses the current retraction and resolved falsifier correctly;
- does not import Book-4 treaty facts or relations from beyond the horizon; and
- does not receive credit for a relationship advantage that is unavailable at
  this planning point.

Severe failures include recommending the incompatible burn option as valid,
promoting an unaccepted proposal to canon, inventing unsupported facts,
reversing causal direction, or treating an interpretive relation as accepted
authority. Preserve all severe failures per condition and probe.

## 7. Blinding, provenance, and freeze

Before execution, preregister the backend, requested/resolved model identity,
exposed sampling controls, tools, startup context, fresh-context mechanism,
packet delivery, and output limits separately by role. Unobservable values are
recorded as `UNAVAILABLE`, never guessed from aliases or documentation.

For every call, record an opaque observation ID, role, probe, input hash,
output hash, transport timing, model/runtime provenance, and tool-use audit.
Condition ID is withheld from the pre-unblind manifest.

Raw extractor, generator, and evaluator responses are written once and made
immutable before normalization. Normalized judgments and semantic adjudication
are separate artifacts. A leakage audit checks prompts, paths, filenames,
metadata, startup context, and packet contents.

Create a true pre-unblind Git freeze containing raw outputs, blinded packets,
hashes, normalized judgments, the extraction manifest, downstream manifest,
schedule, and sealed condition mapping commitment. Only after that commit may
the mapping be opened and joined for interpretation. Any post-unblind report
is additive and may not rewrite raw evidence or frozen judgments.

## 8. Qualification and invalidation

The backend must establish fresh isolated contexts, no continuation between
observations, no inherited worker conversation, and no hidden orchestrator
reasoning through the applicable runtime contract and canary evidence. A
sample canary cannot prove an unobservable property; if no independent runtime
guarantee exists, qualification fails.

Execution is invalidated under the conditions listed in the protocol,
including gold leakage, fact imbalance, prompt/configuration drift, condition
identity leakage, output replacement, post-observation gold changes, bad
semantic scoring, unsupported downstream facts, or overwritten raw evidence.

An invalidated run is reported as invalidated, not as a negative result.

## 9. Interpretation rules

Interpret P03/P05 as one primary mechanism family. Use P04 to test robustness
against a state-incompatible option and P02 to test that a Book-4 overlay does
not create value before its target horizon. Do not aggregate away distinct
failure modes.

The decision gate is:

| case | evidence pattern | action boundary |
|---|---|---|
| A | R-GOLD materially improves the primary family and R-DERIVED preserves most value with acceptable fidelity | consider a separately authorized small prototype |
| B | R-GOLD helps but R-DERIVED is unreliable or loses value | research extraction reliability; no productization |
| C | R-GOLD does not reproduce the V3 mechanism | diagnose attribution; no extraction architecture |
| D | evidence is noisy, invalid, or indeterminate | investigate fixture/runtime/evaluator dependence |

No case authorizes a complete Global Map, ontology expansion, or automatic
production mutation. Human review is required before any next boundary.
