# Auteur — Current Repository Status

**Last reconciled:** 2026-10-25
**Main reviewed for this reconciliation:** `9b923eb477cf1fc0c67167dff35c88e4409e9dac` (through Quick Draft PR #493; development integration, not release qualification)
**Product-use evidence baseline:** `4122321fe09d1959278fdd087fc29f85e2f3a9d2` (PR #436 merge)
**Latest published release:** `v0.37.1` (`pyproject.toml` `1.0.0` is not publication evidence)

Short operational handoff only; history belongs in Git, PRs, issues, qualification, and evidence records. Read [MISSION.md](MISSION.md), [docs/narrative-architecture.md](docs/narrative-architecture.md), and [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md).

## 2026-10-25 Studio integration — explicit owner-directed development exception

Seven pull requests were merged into `main` in this integration round:
[#485](https://github.com/ThorStarlord/auteur/pull/485) (unranked UI possibility landscape),
[#486](https://github.com/ThorStarlord/auteur/pull/486) (strategic UI comparison and isolated synthetic stress report),
[#488](https://github.com/ThorStarlord/auteur/pull/488) (repository-wide creative futures and noncanonical S1/S2 probe records),
[#484](https://github.com/ThorStarlord/auteur/pull/484) (Realization reference coverage for selected Architecture focus),
[#487](https://github.com/ThorStarlord/auteur/pull/487) (editable scene intent, explicit premise copy, safe provenance and stale-source warnings),
[#489](https://github.com/ThorStarlord/auteur/pull/489) (prompt instructions for substantive causal development of selected focus), and
[#490](https://github.com/ThorStarlord/auteur/pull/490) (Quick Draft source-input freshness warning and superseded-response guard).
PR #486 was integrated after its base #485; the other code changes remained in existing Studio/Realization owners.

**Evidence boundary / owner exception:** The owner explicitly requested immediate integration without waiting for unit or evidence tests. The code-bearing merges **did not run exact-head required L1/L2, repository checkout-based Browser integration, provider quality, or release qualification** in this session. This is a recorded owner-directed exception to the normal [merge evidence policy](docs/engineering/release-qualification.md), **not** a passing or waived-as-passing test result. Earlier 13-assertion source-derived Python stress, 3/4-case Node excerpts and 9-checkpoint Chromium fixtures remain **isolated synthetic evidence**, not proof of the merged full application. The new #489/#490 contract tests were committed but **not executed**.

**Effect:** The selected graph-first, coding-agent-first **Connected Creative Thread** direction remains unchanged. These integrations add bounded working-author controls and a stronger noncanonical request contract. They do **not** complete the F2 small-Book or X3 persistent Book frontier, human usability testing, an end-to-end provider execution, release readiness, or automatic story acceptance. Continue normal development without presenting these as qualified claims; triage any observed defects at the smallest existing owner.

**Additional 2026-10-25 connected-author continuation:** [PR #492](https://github.com/ThorStarlord/auteur/pull/492) protects an existing working scene from silent replacement when the author copies generated Quick Draft prose: nonempty different text requires explicit confirmation; overlength candidates and unavailable persistence are refused. [PR #493](https://github.com/ThorStarlord/auteur/pull/493) exposes the existing pending host-agent request's project-relative file and SHA-256 as collapsed, read-only details in both Studio and Beginner. Neither change launches an agent, accepts story canon, or adds a state owner. Both **merged by explicit owner instruction without waiting for unit/evidence tests**; their source-reading regression tests are **committed but were not executed**, and the complete served Browser/CanvasStore/host-agent journey remains **unverified**. The current product direction remains Connected Creative Thread; release and F2/X3 qualification status do not change.

## Current Frontier: F2 + X3

Issue #318 remains open. The latest full six-Chapter execution used a
fixture-complete disposable reconstruction from source `ef5ae8c7910fe7b3db38f6e2af87d1f45ed6182c`.
It does not recover the unavailable original workspace or replace the
historical Windows execution below. The full report and independent Browser
review are in [qualification evidence](qualification-evidence/glass-archive-fixture-complete-20261015.md)
and [the X3 Browser review](qualification-evidence/glass-archive-x3-browser-review-20261015.md).

- **F2 narrative behavior:** bounded simulated-author pass for this six-Chapter
  reconstruction. It does not establish human creative judgment or general
  story quality.
- **X3 persistence:** API/file-level pass. Six accepted final prose files
  matched the recorded SHA-256 values after a fresh process load.
- **X3 Browser experience:** the graph-first Book re-entry and Chapter
  navigation repair is integrated by PR #439 (`bb9c102d6cc4e9473ca7cffc5253ed72361ef37a`).
  The exact candidate passed focused Browser checks and Stage B Chromium
  21/21; a baseline-identical publication-preflight test failure was preserved
  on `main@be212c7`, a fresh Chromium run against
  a disposable copy of the complete six-Chapter fixture verified Chapter 6
  re-entry, Chapter 2 accepted manuscript review (8,269 characters), the
  `Plan Chapter 3` continuation action, browser Back, and ordinary Studio
  re-entry. All 89 story files retained their hashes and no page errors
  occurred. This is bounded automated behavior evidence; broader Browser
  experience and human UX remain unqualified. Later docs-only merges #437
  and #469 do not upgrade this Browser evidence or change product code.
- **Human UX:** not tested. No comfort, preference, usability, or production
  readiness claim follows from automated Browser interaction or simulated
  author decisions.

PR #439 is integrated on current `main`; no release or human UX qualification
is claimed. The current-main product-use evidence and the earlier exact
candidate test results are recorded separately in the updated Browser review.

## Historical Windows execution — 2026-10-14

Issue #318 remains open. The controlled six-Chapter **The Glass Archive** journey began against the exact merged baseline above. The Windows persistence defect was repaired and passed a clean Chapter 1 retry; the controlled run stopped at Chapter 2 after repeated under-target chapter prose.

- The first Chapter completion wrote LF candidate text as CRLF, so its persisted bytes did not match the completion receipt hash. Acceptance then encountered the same translation in `final.md`.
- `Project.write_draft` and `Project.write_final` now preserve LF bytes; byte-level regression assertions were added. Focused chapter-generation, acceptance, and project persistence tests pass (34 tests).
- On a clean fixture, Chapter 1 (946 words) completed and was explicitly accepted. Draft and final bytes matched; reopening showed Chapter 2, recent accepted facts, and the next action. The earlier interrupted fixture had duplicate Bible events from retrying its CRLF acceptance failure; those records were confined to that disposable project.
- The generated Chapter 2 outline was corrected before drafting so Sister Beatrice and Saint Orra were absent from the initial plan, as the frozen fixture requires. Chapter 2 then surfaced Beatrice, Saint Orra and historical ledger evidence in a 965-word Working candidate. Both Chapter outputs were below the requested 1,066-word minimum. Chapter 2 remains unaccepted; the run stopped at this recurring under-target output. F2 and X3 are blocked/incomplete, not passed. No production story was used.

The repair is committed as `c17771db218565625915fd9d90b6cb9f2fd5a396` on top of merge SHA `4122321`. At this code SHA, Node passed 64/64, focused mentorship Python passed 28, `-k studio` exited successfully (163 tests), and Stage B passed 16/16. The full Python run collected 5,617: 5,599 passed, 16 failed, 2 skipped; all 16 failure IDs were reproduced with the same assertions on exact merge baseline. This is engineering regression evidence, not completion of the F2/X3 book journey. Continue from a clean fixture at Chapter 1, then proceed only while the controlled checkpoint succeeds.

## Quick Draft (#310)

Four core host-agent Quick Draft scenarios were run (mystery, character-driven, speculative, intentionally vague), plus the requested Sister Beatrice / convent follow-up. All generated responses remained Working drafts (`accepted: false`). The follow-up selected only Sister Beatrice and the convent for a noncanonical handoff; other detected discoveries were excluded. The complete requests, responses, outputs, hashes, and measured word counts are in [post-#436 product-use evidence](qualification-evidence/4122321-post436-product-use.json).

Observed issue: a Browser session displayed `awaiting_host_agent`, disabled its editor, and did not expose the request prompt/hash in the page. No natural notification to the active coding-agent environment was observed; this run required task context and local request inspection. The API accepted a response, but the page did not update during the observed wait; reopening the session displayed the saved draft. This does not establish a general host bridge or successful unattended fulfillment.

Model identity and reliable per-request latency were unavailable, so they are recorded as unavailable. The four scenarios are agent-generated dogfood evidence, not human author feedback. Two outputs were below the prompt’s approximate 1,400-word target (1,030 and 1,076 words); the other two were 1,147 and 1,129 words.

## Current-main Beginner Narrative-Architecture Coherence

`CURRENT_MAIN_BEGINNER_COHERENCE_RECONCILIATION`: the Beginner path reuses the accepted whole-story Structure to derive Chapter and scene plans. Scene plans mark the **Structure → Realization** boundary; outline and Chapter plans remain derived proposals until the author explicitly accepts them. L3 verification and human qualification remain separate evidence gates. This handoff records agent product use only; no human author walkthrough occurred in this run.
## PR #436 integration and qualification evidence

PR #436 is merged. Its exact source qualification was recorded at `97354ee6ea293df6c6b15783406e6c1d560403bf`; the integration commit is `4122321fe09d1959278fdd087fc29f85e2f3a9d2`.

Recorded exact-source checks: Node 64/64; focused Python 28; `-k studio` 163; Stage B browser check 16/16; focused unfolding 11/11. The serial full Python suite had 5,591 passed, 24 failed, 2 skipped; all 24 failures matched the exact-main baseline and no candidate-only failure was recorded. GitHub Actions had no runs. These results do not qualify the subsequent Windows persistence repair.

A fresh mentorship response was also sampled through CanvasStore: one response passed the strict backend contract and offered three distinct options while preserving supplied constraints. It remains one agent sample, not a human study or product-readiness finding.

## Claim ceiling and next execution

The original Windows run remains a valid partial product-use record; it stopped at the under-length Chapter 2 and did not run Chapters 3–6. The later reconstructed run adds separate, bounded F2 simulated-author, X3 persistence, and automated Browser results. Human UX remains untested; the Browser review records the remaining density and interaction questions.

1. Keep the Chapter-generation length deviation visible; the reconstruction preserved the original Chapter 1 deviation and explicitly revised the under-length Chapter 5 candidate.
2. Do not repeat the Chapter 2 generation probe solely to revisit word-count adherence: the reconstructed run produced a fresh 1,412-word Chapter 2 and continued the six-Chapter journey under explicit simulated-author decisions.
3. **Agent-first Studio progress:** on 2026-10-20, the existing disposable
   Tidal Archive working architecture was revised through the real host-agent
   handoff using the ontology-grounded request context. The source project keeps
   the request, response, staged review, and applied working candidate. This
   exercises revision of an existing candidate; it does not qualify a fresh
   premise-to-architecture journey, human creative quality, or production
   readiness. Do not repeat Tidal Archive's initial generation or this revision
   solely for qualification. Continue only where a concrete product gap remains.
4. **Separate human-evidence lane:** the graph-first Book re-entry walkthrough
   is prepared in
   `docs/product-validation/auteur-graph-first-book-reentry-human-walkthrough.md`
   but has not been performed. It remains useful for genuine comprehension and
   usability questions, not a mandatory gate before reversible agent-first
   construction. Automated Browser checks cannot establish author preference
   or creative quality.
5. Keep pending discoveries separate from accepted story and route any canonical
   author decision through existing acceptance/reconciliation owners. Manual
   node editing remains optional; generating or revising working architecture
   is not canonical acceptance.

F3/X4 remains unselected. This narrower Studio interaction responsibility does
not select that frontier, authorize a new host bridge or test framework, or
imply release readiness.

## Governance / External Gates

- **#338:** human protected commit — replace the absolute 500-line/12-file rejection rule and consolidate AGENTS/CLAUDE guidance.
- **#272:** GitHub admin — require PR-only `main`, no mandatory hosted Actions.
- **#295 / #218:** separate qualification lanes; neither blocks current F2 product-use evidence.

## Simplification Rule

```text
accepted story
+ Working candidate
+ source freshness
+ explicit promotion
```

Preserve authorial authority and auditable provenance; reduce machinery that mainly administers the repository.
