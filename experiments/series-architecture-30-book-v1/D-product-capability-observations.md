# D — Product-capability observations

Status: **observations from one exercise, run by one agent on one scratch project.** These are not a qualification of Auteur. Every operation below was actually executed; the evidence files are in [evidence/](evidence/). The scratch project lives outside the repository and was not used for anything canonical.

## 1. What was actually performed through Auteur

| # | Operation | How it was executed | Result | Evidence |
|---|---|---|---|---|
| 1 | Create canvas and Story Vision item | `CanvasStore.create()` and `apply("create-item")`, the same calls the tests use | canvas `spring-ledger-30` at revision 1 | `evidence/create_store.py` |
| 2 | Record four author-fixed constraints as intentions | `studio_architecture keep-intention` CLI bridge | four `active` intentions, `author_directed_working_intention` | `intention-1..4.json`, `05-intentions.json` |
| 3 | Develop initial architecture (request) | `studio_architecture prepare` CLI | request awaiting host agent | `01-prepare-original.json` |
| 4 | Submit my candidate as host agent | `complete-file --candidate A-studio-candidate-original.json` | `status: ready`; 20 nodes, 16 links, 5 phases | `02-complete-original.json` |
| 5 | Re-entry packet for a fresh agent | `resume` CLI | about 43,000-character packet: vision, architecture, pending review, open questions, ontology guidance, accepted identity (none), source visibility | `03-resume-original.json` |
| 6 | Read current state and intentions | `show`, `intentions` | consistent with the above | `04`, `05` |
| 7 | Request a revision with an instruction | `prepare --instruction` (H1 + R-A) | awaiting host agent | `06-prepare-revision.json` |
| 8 | Submit the revised candidate | `complete-file` | `review_ready`; before/after component diff | `07-complete-revision.json` |
| 9 | Apply the reviewed working revision | `apply_architecture_review()` (Python; **not in the CLI bridge**) | candidate replaced in the scratch canvas; original kept in request history | `09`, `10` |
| 10 | Stale-response guard | changed one intention to `provisional` after `prepare`, then `complete-file` | `BeginnerConcurrencyError`: response retained as `stale_response.json`; intention restored afterwards | `11`–`14`, `13` |
| 11 | Sparse 30-Book horizon as accepted series contract | `auteur.cli series validate` on a five-plan `limited_series` (book_count 30) | rejected: `book_count must match book_plans` | `15`, `16` |
| 12 | Same five plans as `ongoing` | `series validate` | rejected: `book_plans must be numbered contiguously from 1` | `15b`, `16` |
| 13 | Thirty placeholder plans (`TBD`) | `series validate` on a probe file (deleted from the evidence folder after the run) | **accepted** (exit 0) | `17` |

Verification that the preserved request responses equal the files committed here: the original response equals `A-studio-candidate-original.json`, and the revised response equals `C-studio-candidate-revised.json` (checked after the run).

## 2. What the product supported

- **Schema enforcement that caught a real error.** While producing the revision I wrote a link to a node I had not appended. The validator rejected the candidate with `candidate connection references missing or identical nodes`. This is the strongest evidence in the exercise that the candidate's structural rules work.
- **v2 rules were enforced.** Character and relationship categories are refused. Genre contracts must reference genre nodes. Genre interactions require two distinct existing contracts. Emotional references must resolve.
- **Freshness is enforced.** A changed author intention makes an in-flight host response stale. The response is retained as evidence and does not apply (operation 10).
- **Revision produces a before/after review.** It lists added, removed and changed components and marks preserved IDs. It also states that accepted Identity, Structure, Book, relations and prose are unchanged.
- **Re-entry is a single packet.** `resume` gathers the working context for a fresh agent. Whether a fresh agent reconstructs the architecture from it is **not tested**.
- **Working is kept distinct from accepted.** The candidate, review and intentions are labelled `working_architecture_comparison_not_story_impact` and `author_directed_working_intention`. No accepted artifact was touched.

## 3. Where freeform reasoning was needed

These judgments are not represented in any typed field. They lived in prose written by me.

| Need | Where I put it | Why the product could not hold it |
|---|---|---|
| Causal loops L1–L3 | node summaries and free-text link `function` (max 120 chars) | Link function is a bounded string, not a typed causal relation. |
| Engine governance by arc | phase `narrative_function` text | Only genre participation has a typed role; engine roles do not. |
| Independent agency of institutions and people | node category `other`; characters and relationships forbidden in v2 | No institution or agent category exists, and people cannot be nodes in v2. |
| Book-level functions (Books 1, 6, 15, 23, 30) | `scope` string "books 1-5" etc. in phases | Book scope is free text. The candidate has no Book node. |
| Renewal and whether a conflict is a reskin | the renewal test in [04](04-renewal-test.md) | Nothing in the candidate records renewal, derived conflicts or reskin risk. |
| Authority: fixed, working, hypothetical | intention records, summary text and labels | The candidate's only typed authority field is `emotion_targets.provenance` (`author_declared` or `agent_proposed`). |
| Impact of H1 on Books 8, 12, 15 | my reasoning in [C](C-revision-delta.md) and [05](05-local-global-judgment.md) | The review cannot see Book-level dependencies because they are not in the candidate. |

## 4. Observed limitations and defects

1. **Sparse horizons cannot be expressed as an accepted series.** `limited_series` needs `book_count` to equal the number of plans, and every plan must be contiguous from 1 (operation 11 and 12). Expressing a 30-Book working horizon with five focal Books would need 25 placeholder plans.
2. **Placeholders pass validation.** Thirty `TBD` plans validate with exit 0 (operation 13). Structural validity is not quality. If an author accepted such a file, placeholder text would enter an accepted contract. This matches the coverage assessment's "contract-valid versus art-valid" boundary.
3. **Closed vocabularies bias the design.** `SeriesFunction` has six values: question, complication, collapse, escalation, resolution and cooldown. None names transformation, aftermath or consequence. I used `collapse` for Book 15, which is a stretch. The vocabulary leans toward escalation, which the brief forbids.
4. **One central engine per Book.** `BookPlan.central_engine` is a single `HighLevelCentralEngine` (want, resistance, conflict, stakes, change). Co-governance cannot be represented at Book level.
5. **`preserved` means unchanged, not still valid.** `et_grief_of_orders` still refers to "the Stone Hall's fall and Keeper Corrow's dissent" after H1 reformed the Hall. The review marked it preserved. The product does not check whether preserved elements remain consistent with changed context.
6. **Authority provenance is agent-asserted.** `emotion_targets.provenance: author_declared` is accepted from the host agent. I labelled three targets `author_declared` because the brief is author-fixed. The product has no check that an author actually declared them. This is a real authority-boundary risk.
7. **Phase genre participation is not reference-checked.** `GenreParticipation.genre` is free text. Only `genre_activations` must reference contracts. I used node IDs, but the schema would accept any string.
8. **The bridge cannot finish a revision.** The CLI bridge exposes `prepare`, `complete-file`, `show`, `resume`, `intentions` and intention commands, but not `apply`. Applying a reviewed revision requires the browser server route `/architecture/apply` or a direct Python call. This exercise used the Python call. The HTTP route was not exercised.
9. **Windows output encoding.** `studio_architecture` prints with `ensure_ascii=False` through the console code page. Redirecting `prepare` to a file produced cp1252 bytes (0x97 is an em dash) that are not valid UTF-8. The files were re-encoded, and later runs used `PYTHONUTF8=1`.
10. **Editable install points to the main checkout.** `python -c "import auteur"` resolved to `H:\GithubRepositories\auteur\src`, not the worktree. Every run in this worktree needed `PYTHONPATH=<worktree>/src`. This is the stale-environment hazard that CLAUDE.md warns about, and it was checked before trusting any result.
11. **`python -m auteur` is not a module entry.** Use `python -m auteur.beginner.studio_architecture` for the bridge and `auteur.cli:main` for series commands.
12. **Revision obligations are only in the system prompt.** The Studio prompt asks the agent to "reconsider every materially affected emotion, genre, trope function, engine and structural phase." The product checks structure and freshness, not whether the obligation was met. I found the et_grief omission only by reviewing my own delta.

## 5. Gaps that are real but not yet owner decisions

- Whether accepted series contracts should allow partial, provisional horizons is a schema and owner question. The coverage assessment already says not to change schemas on this evidence alone. This exercise supports that caution.
- Whether `TBD` placeholders should fail validation in accepted contracts is a validation-policy question. It needs an owner decision.
- Whether `author_declared` provenance needs an author action to be recorded is an authority question.

## 6. Summary of the product path

The product path held for the Studio candidate (operations 1–10). It was sufficient for a working, freshness-checked, reviewable abstract architecture with intentions kept separate. It did not express the 30-Book horizon as an accepted series (operations 11–13), and it could not hold the causal loops, Book functions or independence of agents as typed content. The judgments that matter most for this design are in prose, and the product neither checks nor carries them.
