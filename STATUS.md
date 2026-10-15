# Auteur — Current Repository Status

**Last reconciled:** 2026-10-15
**Current integrated main:** `ef5ae8c7910fe7b3db38f6e2af87d1f45ed6182c` (PR #438 merge)
**Product-use evidence baseline:** `4122321fe09d1959278fdd087fc29f85e2f3a9d2` (PR #436 merge)
**Latest published release:** `v0.37.1` (`pyproject.toml` `1.0.0` is not publication evidence)

Short operational handoff only; history belongs in Git, PRs, issues, qualification, and evidence records. Read [MISSION.md](MISSION.md), [docs/narrative-architecture.md](docs/narrative-architecture.md), and [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md).

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
- **X3 Browser experience:** the initial completed-Book projection defects
  were repaired on the unmerged local candidate. At
  `aabfe577068f383887709e7bbc695261634e3d66`, automated Chromium on a
  disposable complete fixture verified Book orientation on re-entry, Chapter
  2 navigation to its accepted manuscript/review, return to the graph, and
  390px viewport fit with all 89 non-Studio source files unchanged. Long Book
  details now collapse behind disclosure controls. This is bounded automated
  behavior evidence; broader Browser experience and human UX remain
  unqualified.
- **Human UX:** not tested. No comfort, preference, usability, or production
  readiness claim follows from automated Browser interaction or simulated
  author decisions.

The local X3 repair candidate is separate from integrated `main`; no merge or
release is claimed. On the recorded candidate SHA, focused Browser checks
passed 11/11 and Stage B Chromium passed 16/16. The
`test_book_progress_reuses_accepted_book_as_publication_preflight` assertion
fails identically on the candidate and exact-main checkout (4 passed, 1 failed
in that file on each); it was not weakened or skipped. See the updated Browser
review record for the exact disposable project and observed route.

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

1. Keep the Chapter-generation length deviation visible; the reconstructed run preserved the original Chapter 1 deviation and explicitly revised the under-length Chapter 5 candidate.
2. Continue graph-first Studio improvements at the existing projection boundary, keeping provenance and suggested changes available and testing their comprehension with authors before making human UX claims.
3. Keep pending discoveries separate from accepted story and route any author decision through the existing reconciliation workflow.
4. Use a human walkthrough before making human UX or product-readiness claims.

F3/X4 remains unselected. Do not add a host bridge, new test framework, or feature without evidence from the existing product-use boundaries.

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
