# Working Book Architecture: worked example and probe (The Uncounted Crew, Book 24)

**Status:** design evidence. It is not canon, not a creative qualification, and not production code. The probe under `spike/` is disposable and is not imported by any production module.
**Design:** [Working Book Architecture: design](../../superpowers/specs/2026-11-12-working-book-architecture-design.md)
**Baseline:** `origin/main` at `8b53b32f`.

## What was run

`spike/probe_book24.py` reads two files from the PR #555 commit `fa85b7f1c2fbfdf8d5b8b35f6ce64c27bf438e04`, read-only with `git show`:

- the corrected Book 24 function, `cold-start/output/book-24-function.corrected-2.md` (17,113 characters);
- the corrected Book 24 Studio candidate, `cold-start/output/book-24-candidate.corrected-2.json`, which contains the consolidated W6 Series architecture plus the Book 24 additions.

It parses the function into structured items, then runs four measurements and one authority probe. The output is `spike/output/probe-output.json`. Nothing in the repository is written except that file.

Each measurement is labelled as either **measured** (computed from the fixtures) or **authored** (the probe's own design judgement, listed in full below).

## Measurement limits

Read these before relying on any number.

- **The typed edges are authored, not extracted.** The eight Book-to-Series edges in `probe_book24.py` were written by the design agent from the Book text. No independent writer produced them, so they show what the schema can hold, not what an agent produces.
- **The parser is structural only.** It splits on headings, bullets, blank lines and bracket tags. It does not understand prose.
- **No model wrote the artifact.** The probe does not test whether an agent produces a valid artifact from the packet. That is untested and is an explicit later evidence gate (see the implementation plan).
- **The traversal is a measurement tool, not a proposed component.** It reaches Series nodes through free-text links, so reachability does not establish which consequences are real.
- **The packet is not tuned.** It is measured as the probe builds it.
- **Capture is not fidelity.** Verbatim capture measures whether every source block became an item. It does not measure whether a structured field holds what the source says. See Demonstration A.

## Demonstration A: preservation

**Measured.** All 11 sections are present. The artifact holds 74 items, 10 assumptions, and 8 typed edges, and every id-style reference in the text resolves against the W6 and Book 24 candidates. The artifact round-trips through JSON to an equal object.

**Read as verbatim capture, not fidelity.** Items are built from the source's own blocks, so the capture ratio shows only that every block became an item. The four engine blocks have structured fields (condition, choice, consequence, changed state, new possibility). Sections 4–8 hold verbatim text items, not the structured fields the design specifies for them. Whether those fields can be filled faithfully is untested.

| Section | Items | Verbatim capture (ceiling 1.000) | Provenance tags |
|---|---|---|---|
| 1. Question and pressure | 2 | 1.000 | agent, derived |
| 2. Inherited conditions | 7 | 1.000 | 6 tagged, 1 untagged |
| 3. Engines and interaction | 4 | 1.000 | agent, derived |
| 4. Agency | 8 | 1.000 | agent, derived |
| 5. Choice and transformation | 8 | 1.000 | 3 tagged, 5 untagged |
| 6. Local resolution | 5 | 1.000 | 2 tagged, 3 untagged |
| 7. Changes to the Series | 6 | 1.000 | all untagged |
| 8. Later possibilities | 12 | 1.000 | all untagged (includes two header lines) |
| 9. Assumptions | 10 | 0.955 | agent |
| 10. Alternatives | 6 | 1.000 | hypothetical by section |
| 11. Unknowns | 6 | 1.000 | unresolved by section |

Provenance across all 74 items: 26 agent-proposed, 9 derived, 6 hypothetical, 6 unresolved, **27 unlabelled**.

**What is preserved as structured fields** (stable id, provenance, references, reversal, typed edges):

- every id-style reference (for example `th_hands_and_draw`, `inst_lineage_crews`, `str_long_return`), which all resolve against the Series candidate;
- the three finale alternatives, which are referenced by id and resolve;
- the eight typed Book-to-Series edges, whose targets all resolve;
- the four engine blocks, split into condition, choice, consequence, changed state and new possibility.

**What is preserved as verbatim source-grounded text.** Everything else. Capture is 1.000 in ten sections and 0.955 in section 9. The residue in section 9 is the reversal label, which is stored separately.

**What is deliberately outside the artifact.** The Series candidate's 32 whole-story nodes, which remain in Studio and are referenced rather than copied. The Books 27–29 Compact bid and anything after Book 24, which the artifact does not write. The revision note that the Book 24 candidate appended to the Series summary, which belongs to revision provenance and not to the Book's content (gap G10).

**What is lost, or cannot be represented as the source states it.**

1. **Provenance for 27 items.** The source does not tag them, so the writer must assign provenance at creation. It cannot be recovered afterwards.
2. **Reversal conditions for 8 of 10 assumptions.** Only P1 and P2 state one.
3. **Finale consequences.** Section 8 says the craft-mark bears on the finale, but no link reaches any finale alternative (see Demonstration B).
4. **Decision pointers.** The text points to 13 locations in the prose 01 document. None resolves inside the artifact.
5. **Named characters without a candidate source.** `Idrun Sallow` and `Oona Brisk` appear in neither the Series candidate nor the Book candidate.
6. **A reader promise.** Section 1 states the question and the pressure, but no reader experience. Section 6 implies one (belonging and wonder), and the Series `rx_*` nodes carry it.

Items 1–5 are the reasons the design requires provenance, reversal, resolvable decision references, and a name-source field. Item 6 is covered by typed references to the Series `rx_*` nodes (`function.reader_experience_refs`), not by a new free-text field.

## Demonstration B: local revision and consequence trace

**Change.** The proof-of-training condition is no longer met by the craft-mark alone. The changed element is `str_b24_capability_mark`.

**Measured.**

- **Book items to inspect: 12 of 74.** Engine 4, the Ledger's new record form; section 5 items 6–8 (the choice and its third path); section 6 items 1 and 5; section 7 item 2; section 8 items 3 and 4; assumptions P5, P6 and P9. The match is lexical on the mark's own terms, so this is a conservative inspection list. A reviewer still reads each item. An earlier run used a looser pattern and reported 13; the extra item was engine 3, which matched the bare word "capability" in an unrelated sentence.
- **Direct typed targets: 3.** `th_hands_and_draw` (the governing variable), `inst_lineage_crews` (the Right's training condition), `str_long_return` (the finale's labour gap).
- **Series nodes reachable through links: 14**, including `eng_source`, `th_maintenance` and `str_hollow_gate`.
- **Finale alternatives reached: none.** `alt_a_reciprocal`, `alt_b_allotted` and `alt_c_ratified_trigger` are not reachable. This is gap G5. Section 8 says the record lowers costs in all three, so a revision would have to consider them, and nothing in the artifact tells a reviewer so.
- **Author-reserved pointers reached: two**, `01 §8.5` and `01 §8.7`. The second is the Right's revocability and final condition, which the source reserves to the author.
- **Unaffected Book items: 62.**

**Consequence reading (authored from the measured trace).**

- *Changes inside Book 24:* the local closure in section 6 (the Council's one-cycle acceptance) no longer holds as written; the third path in section 5 loses its sufficiency; P5, P6 and P9 need revision. The crew, the Balance Stones reading, the Reading Hall's refusal, the remnant's offer and Oona's offer are unaffected by the trace.
- *Whole-Series commitments that may need review:* the Right's training condition (`inst_lineage_crews`), the labour-readiness claim behind the Long Return (`str_long_return`), and the governing-variable note (`th_hands_and_draw`).
- *Should remain untouched:* the uncounted crew and its gift labour, the aggregate Balance Stones reading, and the Reading Hall's refusal to attribute balance to persons.
- *Author decisions that remain open:* the Right's final condition and revocability (`01 §8.7`), and whether reform comes from within the Council (`01 §8.5`). The revision must not decide them.

**Caveat.** The consequence reading is the design agent's judgement. The probe establishes what the artifact can surface, not what the story should do.

## Demonstration C: continuation packet for a Book 25 agent

The packet is built from the Book 24 artifact, not from the conversation.

**Measured.** 10,055 characters, which is **31.7%** of the Book artifact's JSON (31,708 characters) and **24.4%** of the full Series-plus-Book candidate JSON (41,189 characters).

| Component | Characters |
|---|---|
| Series constraints (9 nodes, including Book 24's own crew node) | 4,354 |
| Exported pressures and consequences (17 items from sections 7 and 8) | 2,813 |
| Provisional assumptions (P1–P10 with reversals) | 1,696 |
| Open questions and author decisions (section 11) | 609 |
| Identity (title, question) | 223 |
| Source identity (fingerprint and content hash) | 190 |

**Revision adequacy (measured).** The packet omits six of the twelve craft-mark revision targets: `s3_engine_04`, `s5_06`, `s5_07`, `s5_08`, `s6_01` and `s6_05`. The packet is enough to orient a fresh agent, but not enough to revise the craft-mark. A revision request must carry the full text of each target and of its dependents.

**What a Book 25 agent would receive, and whether it is enough.**

- *What Book 24 changed:* the exported section 7 items. Sufficient.
- *What remained provisional:* P1–P10 with reversal conditions where they exist. Eight of ten have no reversal, so the agent is told that openly.
- *Pressures exported:* the section 8 enabled items, including the capability record and the Books 25–26 falsifiability and hand-light draw pressures. Sufficient.
- *Consequences available for development:* the same items, which the agent can select from. No consequence is typed, so selection is by reading, not by graph query.
- *Series commitments that constrain its choices:* the nine constraint nodes, including the governing variable, the Right, the three finale alternatives and the Balance Stones. Sufficient for this example.

**Tuning rule (decided, not yet measured).** Remove Book-internal ids from the constraint block, and show alternatives by title only. The 1,559-character crew summary is the largest duplicated piece.

## Demonstration D: counterfactual rejection of the craft-mark

**Measured.**

- **Series candidate unchanged, by construction.** Book artifacts reference Series nodes and never write them. The probe reports this as a design property. It is not measured, and the probe does not compare a value with itself to show it.
- **Items that must be revised after rejection: 12**, the same set as Demonstration B.
- **Items that survive without revision: 62.** The crew items survive.
- **Typed edges: 3 removed, 5 survive.** Edges from the crew, from the Old Hand, and from the Reading Hall are not affected.

**What the design lets a reviewer do.** Reject the craft-mark as one element, record the rejection and its rationale, and keep the 62 surviving items as they are. The 12 items that name the mark are then revised, and that revision is itself reviewable. Nothing is accepted, and the Series architecture is untouched. The other branch, the craft-mark kept, remains a recorded alternative. This answers the mission's question: rejecting the mark does not destroy the rest of the Series architecture, and multiple working alternatives can coexist without one being accepted.

**What it does not show.** The current Studio candidate holds one current version per canvas. Two full alternative Book artifacts at once would need branch-keyed storage, which is deferred. Recording alternatives as elements within one artifact is enough for this example.

## Authority probe

**Measured.** The production validator accepted an emotion target with `provenance: author_declared` in an agent response (`authority_probe.author_declared_accepted_from_agent_response = true`). The validator's `Literal` allows both values, and nothing checks the source. The prompt tells the agent to use `agent_proposed`, but that is an instruction, not a guard.

**Consequence.** The working candidate can currently carry an author-declared label that no author wrote. This is the sharpest authority gap found in the investigation. It is independent of the Book artifact and is the first increment in the plan.

## Other observations

- `_BOOK_CONTEXT_STATE_TRANSITIONS` (`src/auteur/series/vertical_slice_service.py`, lines 66–77) hard-codes one fixture series and Book in production code. It is not used by the design and must not be extended.
- The Book 24 candidate's whole-Series summary carries a revision note. The note is useful to a reviewer, but it does not belong in the Series summary.
- Idrun Sallow and Oona Brisk have no candidate source, so a validator that checks name sources will flag them. That is correct behaviour.

## Reproduction

    PYTHONUTF8=1 python docs/qualification-evidence/working-book-architecture-design-20261112/spike/probe_book24.py <repo_root> <output_dir>

It requires the PR #555 commit `fa85b7f1` to be present in the repository's object store (fetch it first). It writes `probe-output.json` to `<output_dir>`.

## Challenge and reconciliation

An independent reviewer, a fresh agent with no shared context and read-only access, challenged the frozen design. It returned eight objections and checked four factual claims. Each objection was verified against the source before disposition.

| # | Objection | Verified | Disposition |
|---|---|---|---|
| 1 | Book acceptance is a constant author label in code (`src/auteur/series/cli.py`, 289–291), and Increment 0 overclaims "every working response" | Yes | **Accepted.** The design no longer treats the existing acceptance as an author confirmation (G12). Increment 0 is narrowed to host-agent responses through `complete_architecture`. Increment 1 adds a test that no Book command reaches an accept function. Any acceptance UI depends on O1 and an interactive confirmation the owner specifies. |
| 2 | The resume packet cannot support revision: six of twelve craft-mark targets lie outside the packet's sections | Yes. The probe now counts six missing | **Accepted.** A revision request carries the full text of every target and dependent. The packet orients a fresh agent but does not revise. Increment 2 adds a craft-mark adequacy test. |
| 3 | The riskiest assumption, that a fresh agent can write a valid artifact, is tested last | Sequencing yes. The value judgement is the reviewer's | **Accepted.** The fresh-agent develop trial is Increment 1's exit gate. |
| 4 | No path propagates a Book revision to the Series; Demonstration D's Series check compared a value with itself; Increment 4 depends on Increment 3 and its test 3 cannot be met | Yes | **Accepted, in part.** The self-comparison is relabelled as by construction. A Book change that needs a Series change now produces a Studio revision request, which the Series lifecycle reviews and applies. Increment 4 depends on Increment 2 and on a working-predecessor reference that moves into Increment 1. Its test 3 is replaced, because accepted Book directions hold no working elements. |
| 5 | Preservation holds by construction; sections 4–8 are flat text, so the structured fields are not produced; coverage is a ceiling | Yes | **Accepted.** The metric is renamed verbatim capture, and its limit is stated. Structured fidelity for sections 4–8 is untested and is part of the Increment 1 exit gate. |
| 6 | Increment 1 cannot pass its own validator. Decision references need open-question ids, which the Studio schema does not have, and `unlabelled` is missing from the enum | Yes (`open_questions` is `list[str]`) | **Accepted.** Decision references use the Series open question's index and the SHA-256 of its text, checked against the referenced revision. This needs no Studio schema change. `unlabelled` is an ingest state. A schema write must assign provenance. |
| 7 | Complexity precedes measurement. The extraction is overstated (the lock and atomic writer are already shared helpers). `reader_promise` duplicates the `rx_*` nodes. Option A's rejection rests on an unmeasured cost | Yes (`persistence.py` 377, `host_agent.py` 38) | **Accepted.** The extraction is narrowed to pointer and record handling. `reader_promise` becomes typed references to `rx_*` nodes. Option A's blast-radius cost is labelled as inferred. Its measured reason is the representation caps. |
| 8 | `agents[]` stores character commitments that the Studio validator forbids. The character contract assigns commitments to Identity | Partly. The validator forbids character nodes (`studio_architecture.py`, 197–199). The contract places Structure-level planning elsewhere | **Accepted, with a narrower reading.** `agents[]` are Structure-level planning. They refer to named characters through `name_source` and create no commitments, character nodes or relationship states. Commitments stay with Identity. |

The reviewer found no consequential confusion between layer and scope (risk 2). It confirmed the four factual claims it checked: the probe figures, the sparse-Book contiguity rule, the `author_declared` acceptance, and the fixture-specific carry-forward table.

**Not resolved by this pass.** The design still has no evidence that an agent can write the artifact well. That is the Increment 1 exit gate. Structured fidelity for sections 4–8 is also open. Both are tests to run, not claims to make here.
