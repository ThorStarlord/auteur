# Auteur Future Product Directions Implementation Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this roadmap subplan-by-subplan. Do not execute the whole roadmap as one change set.

**Goal:** Turn the Story Design Pack and Tutor V1 foundation into an evidence-led, decision-oriented creative-writing tutor with progressively deeper narrative intelligence and long-horizon series support, while preserving author authority and the whole-story Structure Engine boundary.

**Architecture:** Treat this as a portfolio of independently testable slices, not a single feature. Experiments come first; each later slice must earn its scope from measured author value. New capabilities remain derived or proposed until explicit author action, and they attach to the existing Identity → Structure → Realization → Expression architecture rather than introducing new semantic layers. Existing `story_design_packs`, `reasoning`, `series`, `impact`, `simulate`, `decision`, `provenance`, and `workflow` modules are extension points; do not create parallel systems for concepts they already own.

**Tech Stack:** Python 3.11+, Pydantic 2, YAML/JSON/Markdown artifacts, deterministic analyzers and graph algorithms, existing `argparse` CLI, pytest, existing provenance and proposal/acceptance workflows. Browser interaction may improve progressively, but a native GUI, cloud service, collaboration service, and auto-publishing remain out of scope.

---

## 0. Scope and sequencing decisions

This roadmap is intentionally split into these separately shippable subplans:

1. **Evidence and product experiments** — validate Pack Effect, Composition Effect, Tutor Comprehension, and Learning Transfer before committing to a large UX build.
2. **Decision-oriented Tutor** — turn existing derived guidance and diagnostics into explicit Decision Cards, tutor depth modes, explanations, alternatives, trade-offs, and author decisions.
3. **Narrative intelligence primitives** — add the minimum explicit state needed for character trajectories, epistemic state, relationship trajectories, promises/payoffs, and causal dependencies.
4. **Revision impact and counterfactuals** — connect the existing `impact` and `simulate` systems to those primitives and produce bounded, evidence-backed “what changes if…” reports.
5. **Long-horizon Series workflow** — extend the existing Series Engine and Global Map/Focus workflow for context reconstruction and Book planning.
6. **Learning progression** — only after transfer evidence supports it, add a concept model that reduces scaffolding without claiming objective skill scores.

Do not begin subplan 3, 4, or 6 merely because the data model is interesting. The product uncertainty is whether writers benefit from each layer enough to justify the authoring cost.

### Non-negotiable invariants for every subplan

- No recommendation or tutor output mutates `StoryIdentity`, Series Identity, Blueprint, accepted Realization, or Expression.
- Any mutation requires an explicit proposal/decision/acceptance path, atomic persistence, provenance, rationale, and rollback-safe failure behavior.
- Deterministic checks remain deterministic and explainable; LLM output may provide hypotheses or creative options but never ungrounded evidence or automatic acceptance.
- Diagnostics, reasoning reports, Decision Cards, simulations, and Global Map projections are derived artifacts unless an existing contract explicitly says otherwise.
- Pack composition can expose tensions and conflicts but must not silently select a canonical winner.
- Structure generation and diagnosis remain whole-story Narrative Engine work. Chapter and scene behavior is added only through an explicit scope-crossing decision.
- Preserve backwards compatibility for existing Story Identity, Book, Series, Genre Pack, Tutor V1, CLI, and packaged-resource behavior.

## 1. Existing seams to reuse

Before each subplan, confirm the current interfaces rather than inventing replacements:

| Capability | Existing seam | Planned extension |
|---|---|---|
| Pack vocabulary and composition | `src/auteur/story_design_packs/models.py`, `composition.py`, `registry.py` | Add pack kinds and synthesis rules only when an experiment requires them. |
| Tutor output | `src/auteur/story_design_packs/tutor.py`, `integration.py`, `cli.py` | Add depth modes and Decision Card envelopes without changing authority status. |
| Diagnostics and reasoning | `src/auteur/reasoning/`, `src/auteur/structure/`, `src/auteur/series/diagnostics.py` | Adapt findings into evidence-backed tutor cards and reasoning reports. |
| Setup/payoff | `src/auteur/reasoning/setup_payoff.py`, series models/validators | Extend IDs, deadlines, promise classes, and emotional/plot payoff distinction. |
| Series context | `src/auteur/series/repeated_map_focus.py`, `vertical_slice_service.py`, `productization.py` | Add bounded context reconstruction and “before Book N” summaries. |
| Revision impact | `src/auteur/impact/` | Add semantic dependency edges only where explicit source references exist. |
| Counterfactuals | `src/auteur/simulation/` and existing `auteur simulate` commands | Add state overlays and evidence classifications for narrative-intelligence changes. |
| Author decisions | `src/auteur/decision/`, `src/auteur/author_decisions/`, proposal/acceptance modules | Reuse readiness, candidate comparison, provenance, and explicit acceptance. |
| Canonical authority | `src/auteur/provenance/`, `docs/architecture-constitution.md` | Register new derived artifact types and freshness dependencies. |

The first implementation task in every subplan is an interface audit and fixture inventory. If an existing interface already satisfies the need, add an adapter or field instead of creating a second service.

## 2. Subplan A — Evidence and product experiments

**Outcome:** A reproducible evidence packet that determines whether to invest in the next Tutor or Pack capability. This is research infrastructure, not a claim that the Tutor is effective.

**Likely files:**

- Create `docs/research/story-design-pack-tutor-v2-protocol.md`.
- Create `docs/research/story-design-pack-tutor-v2-rubric.md`.
- Create `scripts/run_story_design_pack_experiments.py`.
- Create `scripts/analyze_story_design_pack_experiments.py`.
- Create `tests/test_story_design_pack_experiment_protocol.py`.
- Reuse fixtures under `tests/fixtures/` and current `tests/test_story_design_pack_*.py`.

### Steps

- [ ] Define four experiments with pre-registered hypotheses, inputs, blind evaluation criteria, stopping rules, and failure interpretations:
  - **Pack Effect:** pack-informed guidance produces more specific, actionable decisions than generic guidance.
  - **Composition Effect:** composed packs generate useful interactions not present in single packs and do not merely add verbosity.
  - **Tutor Comprehension:** authors can explain the governing craft principle after receiving guidance.
  - **Learning Transfer:** after an assisted example, authors make a structurally similar decision on a new example with reduced help.
- [ ] Keep the experiment runner deterministic about packet construction, seed, pack versions, prompt templates, and output hashes. Do not add production LLM calls to deterministic analyzers.
- [ ] Generate matched packets: control, single-pack, composed-pack, and diagnostic-tutor conditions. Preserve pack provenance and never expose condition labels to evaluators.
- [ ] Score artifact value and learning value separately. Record completion, specificity, causal explanation, option trade-off recognition, independent transfer, and author disagreement; do not collapse them into one quality score.
- [ ] Run analysis against baseline and candidate packet sets. Report collected, completed, excluded, and failed cases separately; a timeout is incomplete evidence.
- [ ] Produce a decision memo selecting one of: proceed with Decision Cards, revise the Tutor hypothesis, expand pack composition, or stop investment in the tested direction.

**Verification gate:** The experiment harness can rerun the same packet set from the same inputs and produce the same hashes and summary. Human evaluation remains explicitly human and is not represented as a green engineering gate.

## 3. Subplan B — Decision-oriented Tutor

**Outcome:** The existing command/artifact Tutor becomes a guided loop: orient → teach → apply → recommend → compare → author chooses → explain consequences. The first surface should be CLI/JSON and a thin browser-friendly projection, not a native GUI.

**Likely files:**

- Modify `src/auteur/story_design_packs/models.py` with `TutorDepth`, `DecisionCard`, `TutorSessionState`, and explicit option/impact references.
- Modify `src/auteur/story_design_packs/tutor.py` and `integration.py` to build cards from packs plus deterministic findings.
- Create `src/auteur/story_design_packs/session.py` for versioned, non-canonical tutor session state.
- Modify `src/auteur/story_design_packs/cli.py` and the root CLI registration/dispatch files for `auteur tutor next|show|choose|explain`.
- Create `tests/test_tutor_decision_cards.py`, `tests/test_tutor_session.py`, and extend `tests/test_story_design_pack_cli.py`.
- Update `docs/product/creative-writing-tutor.md` and create `docs/design/decision-oriented-tutor.md`.

### Steps

- [ ] Define a `DecisionCard` contract containing: stable card ID, source subject, decision question, why it matters, one recommendation, alternatives, trade-offs, beginner trap, downstream consequence preview, pack/diagnostic evidence, authority status, and the exact author action required.
- [ ] Define depth modes as presentation policy only: `recommend`, `explain`, `teach`, `challenge`, `quiz`. The same underlying evidence and options must remain inspectable; depth must not change canonical meaning.
- [ ] Add deterministic selection of the next decision using existing decision/workflow ordering. Do not invent a second priority engine inside the Tutor.
- [ ] Add a session artifact under the project’s non-canonical `.auteur` area. Persist card version, input hashes, viewed cards, author response, and comprehension response atomically. Never persist a tutor response as story canon.
- [ ] Implement explicit responses: choose an existing option, keep unresolved, reject recommendation, or request alternatives. Each response becomes a candidate decision input or a recorded tutor interaction, not an automatic Story Identity mutation.
- [ ] Add `why` and consequence inspection commands that cite source artifact IDs, revisions, pack hashes, diagnostic rules, and recommendation provenance.
- [ ] Add stale-session detection when pack versions, diagnostic inputs, or source revisions change. Mark the card stale and require regeneration rather than silently reusing it.
- [ ] Add a browser-neutral JSON descriptor so the existing browser/runtime can render progressive disclosure later without moving authority into UI code.

**Verification gate:** A golden path demonstrates: load project → receive one card → inspect recommendation and alternatives → answer → produce a non-canonical candidate/decision record → inspect downstream consequence preview → verify canonical files and hashes are unchanged.

## 4. Subplan C — Narrative intelligence primitives

**Outcome:** Explicit, bounded representations for state that the current architecture can reason about. These are not an invitation to model every possible story concept at once.

**Order:** causal references and existing setup/payoff IDs first; character state and relationships second; epistemic state third; broader promise/trajectory synthesis only after the first slices prove useful.

### C1. Character and relationship trajectories

**Likely files:**

- Extend the owning models under `src/auteur/character/`, `src/auteur/relations/`, and `src/auteur/narrative_realization/` after inspecting their canonical ownership.
- Create a focused trajectory module only if no existing owner fits; candidate path `src/auteur/narrative_realization/trajectory.py`.
- Add `tests/test_character_state_trajectory.py` and `tests/test_relationship_trajectory.py`.
- Add `docs/design/character-and-relationship-trajectories.md`.

### C2. Epistemic state

**Likely files:**

- Create `src/auteur/narrative_realization/epistemic.py` for author/reader/character/faction knowledge facts and transitions.
- Extend realization schemas only at the existing event/state owner.
- Add `tests/test_epistemic_state.py` and fixtures for secret, reveal, deception, misunderstanding, and dramatic irony.
- Add `docs/design/epistemic-state-v1.md`.

### C3. Promise, setup, and payoff

**Likely files:**

- Extend `src/auteur/reasoning/setup_payoff.py` and the existing Series setup/payoff models rather than creating another tracker.
- Add explicit promise class, introduced scope, expected effect, deadline policy, payoff kind, status, and evidence references only where the current model lacks them.
- Add `tests/test_setup_payoff_reasoning.py` cases for dormant, escalated, plot-resolved/emotionally-unresolved, intentionally deferred, and out-of-scope promises.
- Update the relevant Series ADR/design doc before changing canonical schemas.

### C4. Causal story graph

**Likely files:**

- Extend `src/auteur/series/graph.py` or the current structure dependency graph owner after confirming edge ownership.
- Add typed edge kinds distinguishing temporal order from causal dependency, decision pressure, knowledge change, promise, and relationship transition.
- Preserve the ADR 013 direction: `source --type--> target` means source affects target.
- Add `tests/test_causal_story_graph.py` for temporal-without-causality, multi-hop causality, cycles, orphan references, and deterministic traversal.
- Update `docs/adr/` only if the existing graph semantics must change; otherwise add a design doc and preserve ADR 013.

### Shared rules for C

- [ ] Every fact has scope, source artifact, revision/hash, and authority status.
- [ ] State transitions are explicit and validate against known prior state; do not infer a canonical transition from prose text.
- [ ] Unknown state is represented as unknown, not false.
- [ ] The first analyzers answer narrow questions such as “what does Character A know at event E?” or “which relationship transition lacks a declared cause?”
- [ ] Produce reports and proposals, not direct artifact mutation.

**Verification gate:** The same fixture produces the same state projection and diagnostic set; malformed or contradictory explicit facts fail with actionable diagnostics; absent facts remain unknown; existing Book/Series/Story Identity fixtures remain valid.

## 5. Subplan D — Interactive diagnostics, revision impact, and counterfactuals

**Outcome:** A user can move from a deterministic finding to a bounded set of repairs, compare consequences, and choose a proposal without the system claiming that one creative answer is objectively correct.

**Likely files:**

- Modify `src/auteur/story_design_packs/tutor.py` to build diagnostic cards from reasoning reports, not ad hoc message formatting.
- Modify `src/auteur/reasoning/` adapters to emit the repository’s observation/evidence/hypothesis/claim/recommendation vocabulary.
- Extend `src/auteur/impact/graph.py`, `analyzer.py`, and `models.py` with explicit semantic dependency edges from Subplan C.
- Extend `src/auteur/simulation/` models and services with narrative-state overlays and consequence evidence classes.
- Reuse `src/auteur/decision/` and proposal/acceptance modules; do not create a second acceptance path.
- Add `tests/test_diagnostic_tutor_integration.py`, `tests/test_narrative_revision_impact.py`, and `tests/test_counterfactual_narrative_state.py`.
- Create `docs/design/interactive-diagnostics-and-counterfactuals.md`.

### Steps

- [ ] Adapt one existing deterministic critic first, preferably setup/payoff or structure coherence, into a complete reasoning report with source evidence, competing hypotheses, confidence method, recommendation, and possible transformations.
- [ ] Render that report as a Decision Card with three bounded repair options and explicit trade-offs. Preserve “keep intentionally” and “reject finding” as valid author choices when the diagnostic is advisory.
- [ ] Add impact edges only from explicit IDs and provenance references. Keep free-form semantic inference out of the first version.
- [ ] Make a simulation scenario an immutable baseline plus an isolated overlay. Compute direct consequences, dependent artifacts, likely contradictions, preserved artifacts, thematic shift hypotheses, and unknowns.
- [ ] Classify each consequence as `KNOWN`, `DERIVED`, `INFERRED`, or `UNKNOWN`, with evidence and confidence method. Never present an inferred thematic interpretation as a deterministic fact.
- [ ] Add comparison without automatic winner selection. Promotion creates an existing author-review candidate or proposal; it does not accept it.
- [ ] Add stale-baseline refusal when accepted source revisions changed after scenario creation.

**Verification gate:** “What if the protagonist does not kill the villain in Book 1?” produces a reproducible, non-mutating report with direct/dependent/preserved/unknown categories, and promotion stops at the existing explicit decision boundary.

## 6. Subplan E — Long-horizon Series workflow

**Outcome:** A writer can return to a long series and ask what matters before designing a later Book without receiving an unbounded dump of notes.

**Likely files:**

- Extend `src/auteur/series/vertical_slice_service.py`, `vertical_slice_models.py`, `repeated_map_focus.py`, and `productization.py`.
- Reuse `src/auteur/series/bible.py`, `diagnostics.py`, `graph.py`, and `continuity_validators.py`.
- Add `src/auteur/series/context_reconstruction.py` only if the existing Global Map/Focus service cannot own the projection cleanly.
- Add `tests/test_series_context_reconstruction.py` and extend existing repeated-map-focus and vertical-slice tests.
- Create `docs/design/series-context-reconstruction.md`.

### Steps

- [ ] Define a bounded `SeriesContextSnapshot` containing active character states, unresolved conflicts, open promises, relationship trajectories, knowledge asymmetries, thematic commitments, institutional pressures, relevant previous decisions, and stale/uncertain items.
- [ ] Build the snapshot from accepted artifacts and explicit dependency edges only. Derived reports and tutor sessions may explain it but cannot become its source of truth.
- [ ] Add relevance filtering for a target Book/Focus: direct dependencies first, active unresolved items second, recent decisions third, then explicit author-requested context. Record why each item was included.
- [ ] Add a “before Book N” CLI/read-only workflow that shows a compact map, current Focus decision, blockers, and unresolved promises.
- [ ] Add progressive disclosure: summary, inspect item, inspect evidence, inspect full graph. Do not require the beginner to understand the entire ontology.
- [ ] Integrate Tutor Decision Cards so the next series decision can cite the context snapshot without embedding the whole snapshot into the card.
- [ ] Add freshness and reconstruction tests across accepted Book revisions, deleted/archived artifacts, unresolved decisions, and unrelated books.

**Verification gate:** A multi-book fixture can reconstruct the context for a later Book deterministically, excludes unrelated facts, identifies stale or uncertain items honestly, and leaves all canonical artifacts unchanged.

## 7. Subplan F — Learning progression and reduced scaffolding

**Prerequisite:** Subplan A must show a meaningful comprehension/transfer signal. If it does not, stop at Tutor depth controls and revise the pedagogy instead of adding mastery tracking.

**Outcome:** Auteur remembers which concepts were introduced, practiced, or independently demonstrated, and uses that history to adjust help without pretending to measure literary talent.

**Likely files:**

- Create `src/auteur/learning/models.py`, `persistence.py`, and `service.py`.
- Add `src/auteur/learning/concepts.py` for the curated concept vocabulary and prerequisites.
- Extend `src/auteur/story_design_packs/session.py` with learning-event references, not embedded skill scores.
- Add `tests/test_learning_progression.py` and `tests/test_learning_privacy_and_authority.py`.
- Create `docs/design/learning-progression-v1.md`.

### Steps

- [ ] Define the minimal states `introduced`, `practiced`, `demonstrated_independently`, and `needs_reinforcement`; allow uncertainty and conflicting evidence.
- [ ] Record only observable learning events: viewed explanation, answered comprehension check, selected an option with rationale, solved a novel transfer prompt, requested more help. Do not infer mastery from prose quality or recommendation agreement.
- [ ] Keep the learning record local, inspectable, editable, and non-canonical. It must not affect story validity or block author progress.
- [ ] Implement scaffolding policy: early prompts ask explicit questions; later prompts may omit explanations when independent evidence is sufficient; the author can always request `teach me`.
- [ ] Add regression cases proving that reduced scaffolding never removes access to explanations, changes story recommendations silently, or writes narrative artifacts.
- [ ] Add an evaluation report for retention/transfer, not a gamified score.

**Verification gate:** A fixture author receives help, demonstrates a concept on a new decision, receives less scaffolding, and can inspect/edit the evidence used for that adjustment.

## 8. Pack ecosystem expansion

Do this only after Pack Effect and Composition Effect are positive enough to justify the content cost. Expand categories incrementally:

1. Relationship packs: rivals → allies, betrayal → reconciliation, mentor → rival.
2. Structure packs: investigation, quest, revenge, manhunt, disaster escalation.
3. Character packs: fallen hero, reluctant leader, manipulator, outsider.
4. Theme packs: freedom vs security, identity vs duty, sacrifice, meaning under nihilism.
5. Setting/world packs only when their rules can express concrete pressures without becoming a lore encyclopedia.

**Likely files:** new versioned resources under `src/auteur/story_design_packs/data/<slug>/`, registry metadata, focused content-validation tests, and one catalog guide under `docs/guides/`. Avoid a marketplace, community scripting, arbitrary plugin execution, or AI-generated packs in this phase.

### Content acceptance checklist

- [ ] Every option states its craft function, trade-offs, failure mode, questions, and architecture targets.
- [ ] Every cross-pack relation is explicit, symmetric or deliberately directional, versioned, and tested.
- [ ] Every pack has applicability signals and can honestly be inapplicable.
- [ ] Pack prose does not claim universal genre truth; strengths are labeled as defaults, patterns, warnings, or subversion points.
- [ ] Pack content is reviewed as teaching material separately from code qualification.

## 9. Verification and release protocol

Each subplan gets its own candidate and qualification record. Do not qualify the roadmap as one release.

### Focused checks

- Unit tests for each new model and deterministic analyzer.
- Golden-path tests for non-mutation, provenance, stale inputs, and explicit acceptance.
- CLI tests with human-readable and JSON output.
- Packaged-resource tests for every new built-in pack or schema.
- Existing Story Design Pack, Genre Pack, Story Identity, Book, Series, Impact, Simulation, Decision, and workflow regressions.

### Evidence to record

- Exact candidate SHA before qualification.
- Test accounting: collected, passed, skipped, xfailed, xpassed, failed, errors.
- Baseline comparison for any pre-existing failure.
- Artifact hash and installed import path for package-bearing changes.
- Human experiment results separately from engineering pass/fail evidence.
- Canonical mutation audit showing unchanged files/hashes before and after derived workflows.

### Release boundaries

- Experiments may land as research tooling and reports without claiming product qualification.
- Tutor/session and reasoning changes require source qualification and, if packaged, artifact qualification.
- Schema migrations, new data leaving the machine, authentication, secrets, or provider changes require human review before implementation.
- Publication remains separately authorized; this roadmap does not authorize publishing.

## 10. Recommended first execution slice

Start with **Subplan A**, then implement only the smallest successful vertical slice from **Subplan B**:

```text
matched experiment packets
    → evidence memo
    → one DecisionCard model
    → one setup/payoff diagnostic adapter
    → CLI show/choose flow
    → non-canonical candidate/decision record
    → no canonical mutation
```

Do not start with a GUI, a giant pack catalog, a full ontology expansion, adaptive curriculum, or automatic manuscript rewriting. Those are downstream bets whose value depends on the experiment results and the narrow vertical slice above.

## 11. Self-review against the proposal

- Interactive Tutor: covered by Subplan B and Subplan D.
- Composable Pack ecosystem: covered by Subplan A and Section 8.
- Persistent Story Design Workspace: intentionally represented first as the existing project/CLI/browser-neutral session and Series context projections; a visual workspace remains a later presentation layer, not a new domain model.
- Character state: covered by C1.
- Knowledge/epistemic state: covered by C2.
- Setup/promise/payoff: covered by C3.
- Causal Story Graph: covered by C4.
- Relationship trajectories: covered by C1.
- Interactive diagnostic teaching: covered by Subplan B and D.
- Learning system: covered by Subplan F, gated by evidence.
- Long-form Series intelligence: covered by Subplan E.
- “What happens if I change this?” and counterfactuals: covered by Subplan D, reusing `impact` and `simulate`.
- Realization without prose-first generation: preserved by the architecture and explicit scope boundaries.
- Deferred ideas: marketplace, arbitrary plugins, full-manuscript rewriting, native GUI, multiplayer, automatic adaptive curriculum, huge ontology expansion, prose-style packs, and AI-generated packs remain out of the first roadmap horizon.

The roadmap is complete as a planning artifact when each proposed implementation has a named owner, fixture, deterministic contract, authority boundary, and verification gate. Product success is not established by code tests alone; it requires the separate human evidence from Subplan A.
