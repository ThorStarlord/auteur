# Evidence-grounded reconsideration of a consequence analysis (design, 2026-11-27)

Status: design for the increment on `feat/evidence-grounded-reconsideration`, from `main@8199e720`. Advisory. It changes no
narrative record, applies nothing, and invokes no agent or critic on its own.

## 1. What the author gets

From an accepted consequence analysis, the author can ask Auteur to reconsider one consequential claim: a concern, a mechanism
reading, a connection, an inheritance, the reach, or an alternative. Auteur prepares a request that quotes the original claim
from the saved analysis and recovers the exact source wording it needs. A fresh agent answers a focused contract. The owner
validates the answer and stores it beside the original. The original stays as it was.

## 2. Reuse decision

| Existing piece | Decision | Reason |
|---|---|---|
| Consequence analysis owner (`studio_architecture_consequence.py`) | Reuse: request lineage, `requests/<sha>/` storage, standing, refusal sidecars, `model_output_contract`, `build_host_agent_request`/`response` | The reconsideration must bind to a saved analysis and its evidence packet. The owner already holds both. |
| Consequence packet and saved `evidence` | Reuse as the original evidence. The request file carries the full baseline and proposed candidates the analysis read, so exact wording can be recovered from the version the analysis used. | Clipped packet text is the source of the misreading in PR #651's Exercise B. The request is the exact version record. |
| Inquiry `challenge` and `prior_exchanges` | Examined, not used for this responsibility. | Inquiry answers a question about the Architecture as a whole, with anchors on nodes, links, questions or one Book element. It has no binding to one claim of an earlier analysis, no recovery of source wording and no coverage accounting. Renaming it to "reconsider" would leave those gaps. Prior exchanges carry text, not a binding to a claim or its evidence. |
| Reasoning subsystem (`src/auteur/reasoning/`, Critic Integration Contract) | Not routed through. Its invariants are reused: critics are read-only, observation is kept apart from hypothesis, provenance is recorded, and criticism is not canonical. | The runtime runs Python critics over chapter drafts, book manuscripts and blueprints, and writes derived reports for the story pipeline. The Atelier's analyses are host-agent records with owner validation. Joining the two would add a second persistence system. |
| Served consequence panel (`studio_architecture_consequence.js`) | Extend: a per-claim disclosure "Reconsider this claim", and the reconsideration beneath the claim it concerns. | The mission asks for the existing surfaces. |

No new critic persistence system is introduced. Independent criticism, when an author brings it, enters as a text input to the
reconsideration request, with an owner-assigned identifier and a category. Nothing runs a critic.

## 3. Binding

A reconsideration request records, in its settings and in its payload:

- the consequence analysis request sha (`analysis_request_sha256`) and the sha of the saved result it reads (`analysis_result_sha256`);
- the revision request, baseline request and proposal sha, and the packet's `evidence_sha256`;
- the claim: kind, reference, and `claim_sha256` of the claim as the saved result stored it;
- the author's instruction (`instruction_sha256`) and any supplied criticism (`criticism_sha256`);
- the recovered records, each with its owner, version and freshness.

Request identity is deterministic: it has no random invocation nonce. The same inputs give the same request, so an exact
replay is possible and a reconsideration is idempotent. Completion refuses if the saved analysis result has changed since
preparation (`analysis_result_sha256` mismatch). It never silently rebinds.

Historical analyses are not rewritten. A reconsideration is stored under `reconsiderations/<sha>/`, beside the analysis's own
folder. Its standing is read at projection time: `current` when the analysis is still the current analysis of the live
proposal; otherwise `historical`, with the analysis's own standing (applied, superseded or stale) carried through.

## 4. Evidence recovery (owner-qualified, bounded)

The owner recovers, for the selected claim only:

1. **Exact source wording.** The full record of each mechanism the claim cites, read from the candidate the analysis read
   (baseline or proposed, by record id). Clipped packet text is replaced by the full record, labelled with its side and the
   analysis request sha. A record longer than the cap is cut and labelled `truncated`.
2. **Endpoint records.** For a mechanism or connection, the full records of its endpoint nodes (bounded).
3. **Coverage of Working Book elements.** For a claim about Books or inheritance, the owner reads every readable Working Book
   element and reports the count considered, the count the packet supplied, and the element identifiers that cite the claim's
   nodes. The count is exact; the returned element list is bounded and says when it is.

Each recovered record gets an owner-assigned identifier that continues the packet's numbering (so it satisfies the evidence
identifier pattern), a source label (`recovered`), its owner, version (candidate side and sha, or Book request sha) and a
freshness label: `as_analysed` for candidate records, `current_read` for Book records.

Discipline: recovery is never a search. It reads only the nodes, links and elements the claim names, and the response must
cite identifiers the owner gave. Nothing is inferred to exist; an uncited record is not evidence.

## 5. Focused response contract

`ReconsiderationAnswer` (schema version 1), generated from the model through `model_output_contract`:

- `disposition`: one of `retained`, `qualified`, `narrowed`, `corrected`, `expanded`, `reframed`, `withdrawn`, `unresolved`.
- `new_consideration`: what criticism, evidence or reasoning prompted the reconsideration.
- `reconsidered_judgment`: what is now retained, corrected, qualified, expanded or withdrawn.
- `evidence`: 1 to 6 identifiers from the claim's original evidence or the owner's recovered records.
- `criticism_assessments`: 0 to 4 objects with `criticism` (an owner-assigned identifier), `verdict` (`accepted`,
  `partly_accepted`, `rejected` or `unresolved`) and `reason`.
- `creative_significance`: optional; how the reconsideration affects the author's possibilities.
- `remaining_uncertainty`: 0 to 4 strings.
- `downstream`: 0 to 3 objects with `text` and `evidence`, for consequences of a correction that matter downstream.

Owner rules, checked on completion:

- every evidence identifier resolves to the request's original claim evidence or recovered records (refused by name otherwise);
- `corrected` cites at least one recovered record: a correction rests on exact source, not on the earlier clipped text;
- every criticism assessment names a criticism the request supplied, once; `accepted`, `partly_accepted` and `rejected` state a reason;
- `withdrawn` states a `new_consideration`;
- a refused answer is kept with the owner's message; it never becomes the reconsideration, and it never changes the analysis.

The agent provides judgement; the owner derives the original claim's text, its evidence list, its standing and its recovered
records. The agent does not restate the original.

## 6. Authority

- A reconsideration is advisory. It is not a narrative revision, not canon, and not an accepted Architecture.
- It cannot add or change an alternative. Alternatives remain the original analysis's. An author who wants to develop an
  alternative investigates the original alternative through the existing `from_consequence` path, which validates the original
  anchors. A reconsideration's disposition of an alternative (for example `withdrawn`) is shown beside it; it does not make the
  alternative unactionable, and it does not make any other alternative actionable.
- Criticism is evidence for reconsideration. A criticism's assertion does not become narrative evidence; an accepted criticism
  changes only the reconsidered judgment.
- Apply is not gated by a reconsideration, and no reconsideration applies, settles, adopts or promotes anything.
- Reconsidering a claim does not change the original analysis or its standing.

## 7. Served journey

On an accepted analysis, each concern, mechanism connection, inheritance and alternative has a collapsed control "Reconsider
this claim". Opening it shows the claim's original text (owner-derived), a textarea for the author's question (unsent text is
kept while the author works), an optional criticism textarea, and "Prepare reconsideration". The request is prepared; the page
states that it is awaiting a coding agent. A completed reconsideration appears beneath its claim: disposition, the original
text, what changed, the evidence (recovered records in progressive disclosure, with owner and version), the criticism verdicts,
and remaining uncertainty. No new step appears in Apply's path.

## 8. Verification plan

- Owner tests: binding and idempotence; refusal of an unknown claim; exact recovery from the analysed version (a clipped packet
  line replaced by the full record); coverage counts; evidence resolution; corrected-needs-recovery; criticism rules; refused
  answer kept beside its message; original `result.json` byte-identical before and after; historical standing.
- Served: the control appears per claim; preparation shows the awaiting state; a completed reconsideration renders beneath its
  claim at 1440 px and 390 px with no overflow or page errors; unsent text survives a re-render.
- Exercises (section 9 of the mission): reconsideration of PR #651's accepted analyses, with replay only where exact equivalence
  is established.
