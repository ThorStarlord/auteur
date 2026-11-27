# Mechanism-centered creative deliberation and evidence-grounded relational reasoning (design)

Status: implemented on `feat/mechanism-centered-deliberation` from `main@55cd1da9` (PR #649). Builds on the
[consequence analysis](2026-11-26-consequence-aware-narrative-development.md), its
[mechanism-grounded contract](2026-11-26-mechanism-grounded-prospective-reasoning.md) (version 2), the
[narrative deliberation](2026-11-26-narrative-deliberation.md), the [opportunity discovery](2026-11-26-narrative-opportunity-discovery.md)
and the [reference stewardship](2026-11-27-narrative-reference-stewardship.md) responsibility. Opt-in Atelier. Advisory output only: no
Architecture, Working Book, review or accepted record changes through an analysis or an investigation. Apply is never gated.

## A. Starting capability, and what prevented mechanism-centered development

Verified against `origin/main@55cd1da9`:

- **Graph-anchored inquiry already accepts mechanisms without a question.** `GraphIntent` anchors may be any typed record
  (`node`, `link`, `genre_interaction`, `emotion_target`, `complex_emotion`, `genre_contract`, `phase`) or a question. The operations
  `explain`, `challenge`, `explore`, `compare` and `connect_to_ask` run on `target: current` with no question. Nothing in the inquiry
  owner requires a question for a mechanism investigation.
- **An inquiry alternative can become a revision.** `_selected_alternative_context` records the selected hypothesis, its inquiry and
  the questions the inquiry concerned, so a revision states its scope. Its mechanisms were not stated; a mechanism-only investigation
  produced no `considered_questions` and so no scope line for the mechanisms it concerned.
- **A consequence analysis of a pending revision proposes alternatives, but only question-anchored ones.** The version 2 contract
  requires `questions` (at least one, continuing, baseline) and `keeps` covering the wording of each named question
  (`AlternativeV2`). A change to a mechanism with no question change (PR #647 Exercise B, `l_compact_hands_in_kind`) therefore offered
  no alternative. This is the question-centred limitation the mission names. It is the only structural cause, not a missing owner.
- **Relations are only partly typed.** Recorded links and interactions are read by the graph owner (`_recorded_relations`,
  `_between`). The consequence contract states relations as inheritance kinds (`recorded_inheritance`, `plausible_inheritance`,
  `proposed_inheritance`, `unknown_inheritance`) but has no way to state a relation **between two mechanisms** with its epistemic
  standing. A consequence answer can therefore describe a connection in prose only, and nothing checks it against the recorded
  endpoints.

Not a gap, and not rebuilt here: the graph owner's typed anchors, the inquiry lifecycle, the mechanism inventory with provenance, the
Book element selection, the revision scope line and the Apply protections.

## B. Decision

Extend the existing owners. No new mechanism persistence owner, no mechanism dashboard, no universal ontology.

1. **Consequence contract version 3** (`studio-revision-consequence/3`). New analyses are prepared as version 3. Version 1 and
   version 2 analyses keep their stored meaning and are read unchanged; a version 2 answer is never accepted for a version 3 request.
2. **Mechanism-anchored alternatives.** An alternative names `questions` (0 to 3 continuing baseline questions) and `mechanisms`
   (0 to 3 mechanism evidence items), at least one anchor in all. Its `keeps` covers every anchor. A question anchor keeps wording as
   in version 2. A mechanism anchor keeps its own record, on the side the approach keeps: the baseline record for every approach but
   `accept_proposal`, and the proposed record for `accept_proposal`. An `introduced` record is never a baseline record. A `historical`
   record is never an anchor. Approaches are the version 2 table plus `retire` (deliberately give up the recorded mechanism or question,
   with what is lost stated).
3. **Relational connections** (`connections`, 0 to 4). Each relates exactly two distinct mechanism evidence items, with an epistemic
   standing:
   - `recorded`: the owner checks the graph. Two mechanisms are recorded as connected when a link or genre interaction in the baseline or
     the proposal joins an endpoint of one to a different endpoint of the other, or when both name the same node as an endpoint.
     Otherwise the claim is refused.
   - `inferred`: the agent states its `reasoning` and at least one assumption. The inference is attributed to the agent.
   - `hypothetical`: a creative possibility, stated with `worth_developing` and at least one assumption.
   - `unestablished`: a `basis` is required. `graph_miss` is allowed only when the owner finds no recorded connection in either candidate,
     and it means "not recorded in this Architecture", never "absent from the story". The other bases are `competing_readings`,
     `incomplete_evidence` and `productive_independence`.
   The owner stores, beside every connection, the graph status it computed from the candidates (`joining_link`, `shared_endpoint` or
   `no_recorded_relation`, with the record it found). The agent's standing and the owner's graph fact are shown side by side, so a
   mismatch is visible rather than hidden.
4. **Transfer to investigation.** `from_consequence` now accepts an alternative whose anchors are questions and mechanisms. The inquiry
   takes one anchor per named question or mechanism, on `target: current`, and must name exactly those anchors. A mechanism the proposal
   introduces is not in the current Architecture, so it is refused with that reason. A mechanism that is `preserved`, `transformed` or
   `removed` (baseline side) is resolved against the current Architecture by the graph owner as usual.
5. **Develop with explicit scope.** A revision made from a mechanism investigation states its `considered_mechanisms` beside its
   `considered_questions`. The owner does not widen the revision's authorized change from that scope line.

## C. What is not built here, and why

- **Discovery basis (mission §10).** A discovery's cited records stay as they are. Making a discovery's relation explicit needs a new
  discovery answer contract and is a separate responsibility; it is recorded as a follow-up rather than half-built here.
- **Pending-review investigation of an introduced mechanism.** Investigations run on the current Architecture only, as before.
- **Prospective mechanism seeds from the selected alternative.** The packet does not yet seed the mechanism inventory from a revision's
  `considered_mechanisms`. Exercise C shows the gap through the packet's changed-record seeds; it is not repaired silently.
- **A universal relational verifier.** The owner checks endpoints and bases. It never checks that the agent's reading of a recorded
  link is literarily correct, and never promotes an inferred or hypothetical relation into the Architecture.

## D. Invariants

- Advisory and noncanonical. The analysis writes only under its own folder. An investigation writes only its inquiry record.
- Exact-source binding. Every anchor resolves against the candidate it names. Historical records are never anchors.
- Question identities are never invented to satisfy a structure. A mechanism-only alternative names no question.
- Removing a question or mechanism is never a replacement. An alternative that retires or replaces one says so in its summary.
- Standing is read at projection, as before; only the latest current analysis can be investigated.
- Apply is never gated by an analysis, a connection or an alternative.

## E. Verification plan

- L1 Python: `tests/test_architecture_consequence_v3.py` (contract, mechanical connection checks, mechanism-anchored alternative
  checks, transfer to investigation, scope line), with the existing owner suites updated only where the request version changes.
- L1 node: `tests/test_studio_architecture_consequence.mjs` (mechanism-only alternatives and connection labels).
- Named L2 boundary: the served consequence and investigation journey, `tests/test_beginner_studio_consequence_browser.py`, because the
  served page and the owner share the investigation handoff.
- Exercises (recorded under `docs/qualification-evidence/mechanism-centered-deliberation-20261127/`): Exercise A replays the PR #647
  Exercise B proposal through the owners and has a fresh agent analyse it without the expected conclusion; Exercise C explores a
  mechanism that is not under revision through the graph inquiry and prepares a working revision from the selected alternative. Refused
  outputs are kept.
