# Glass Archive Fixture-Complete Qualification Summary

Date: 2026-10-15

## Provenance

- Auteur source checkout: `C:/Users/Admin/AppData/Local/Temp/auteur-glass-reconstruction`
- Exact source HEAD: `ef5ae8c7910fe7b3db38f6e2af87d1f45ed6182c`
- Git common directory: `H:/GithubRepositories/auteur/.git`
- Source worktree was clean after qualification. No repository source files were changed or committed.
- Disposable fixture-complete project: `C:/Users/Admin/AppData/Local/Temp/glass-archive-fixture-complete-20261015/project`
- This is a reconstruction, not recovery of the unavailable original workspace. Fixture references: `docs/qualification-evidence/4122321-post436-product-use.json`, `docs/product-validation/f2-x3-controlled-reference-book.md`, and `docs/product-validation/2026-10-04-f2-x3-controlled-qualification-protocol.md`.
- The separate sparse reconstruction remains at `C:/Users/Admin/AppData/Local/Temp/glass-archive-reconstruction-20261015d/project` and was not modified.

## Reconstruction differences

- Rebuilt the full Book premise, cast, relationships, arcs, initial six-Chapter Structure, and P1-P6 journey from the frozen reference.
- Restored Chapter 1's exact recorded prose. SHA-256 is `32e0b5b10b53c531b0d3436bb9f054ff4ab21cb41e87f27e8ee283912d97db64`; count remains 946 words, preserving the known deviation. Acceptance uses a new fixture-specific receipt.
- The sparse reconstruction retains the 965-word Chapter 2 reference candidate at SHA-256 `f4488ec21f0196c405942d67f9fe8ee6056133d619340446fac5c554eebda3ef` and the 1,520-word diagnostic candidate at SHA-256 `8f1c31645164b89a44604173ab1ccfd86bdb26c359e9fedf4331d8d77b03b67d`.
- The complete project did not transplant either reduced-project response. It prepared a fresh Chapter 2 request after the full fixture and accepted Chapter 1 state existed. Chapter 2 was 1,412 words, SHA-256 `4381a19074f0a3a421c10a369c2b7e444ccc74e75706fe9e8bab6e378af3c594`.
- Original timestamps, request identities, receipts, and persistence history were not fabricated. Acceptance receipts and decisions are new and explicitly attributed to the simulated test author.

## Candidate decisions and outcomes

| Chapter | Decision and evidence | Accepted candidate |
|---|---|---|
| 1 | Restored exact prose; accepted with fixture-specific authority receipt; recorded facts remain limited to observed report, forecast, and investigation. | `draft_v1.md`, 946 words, `32e0b5b1...d97db64` |
| 2 | Keep and reconcile. Beatrice/Saint Orra retained as selected historical witness/source. Covered equipment contents and purpose remain unknown; symbol meaning and report origin remain bounded. | `draft_v1.md`, 1,412 words, `4381a190...8af3c594` |
| 3 | Keep v4 after revisions. Mara is explicitly identified as Nia's older sister; Tom learns of the withheld family history; relay authorization is pending, not completed; Beatrice's crate ledger and the municipal schedule remain separate leads. | `draft_v4.md`, 1,418 words, `61f4e7eb...bc3912d` |
| 4 | Revise then keep. The first draft did not make the public-use choice explicit. The revision withholds Mara's unverified future report from publication, shares a redacted pending authorization with Tom, and grounds possible reporting in the independently observed pump defect. The defect is not yet repaired at the Chapter end. | `draft_v2.md`, 1,177 words, `7f7d1cab...b94dae1` |
| 5 | Initial v1 was 1,002 words, below the 1,066-word minimum. Explicitly revised and reviewed v2 (1,097 words), then kept through the intentional-divergence workflow. The controlled repair prevents the immediate failure before provenance is solved; the old provenance-first plan is recorded as historical divergence, not silently rewritten. | `draft_v2.md`, 1,097 words, `1b1472a4...bb5033e` |
| 6 | Keep v3 after a bounded revision. Authenticated records show the harmful asymmetry of automatic clearance referral versus manual public-warning approval. The public account does not assign individual authorship, make Rook the sole cause, or explain the future report. | `draft_v3.md`, 1,122 words, `187c3a74...f7716d3` |

Full hashes, review notes, decision records, request packets, and receipts are preserved under `.auteur/` in this project. The six accepted finals each match the latest candidate bytes after reopening.

## Generation freshness and persistence

- Chapter 2 fresh request: `chapter-02-fixture-c2-fresh-generation-20261015-v2:b5ce3a41068942ef`; source fingerprint `2dadb5b9c4af799046d2b6fe2f3a5cd5bd434a0b4c17b180b40a84e66dc4b0db`.
- Chapter 3 request: `chapter-03-fixture-c3-p2-p3-generation-20261015:2b65e9e451976e95`; source fingerprint `07cd262ab1800c890cfc91fe3443dec29d6cbc48f7e7da509151392ba907bde2`. v4 is a separately recorded author revision of the generated source.
- Chapter 4 request: `chapter-04-fixture-c4-after-accepted-c3-20261015:ad3fd37dac0f69fa`; source fingerprint `95bdeff95de67ed5b8bdb70889a84599e2c1c832e3882436e0f3b0cc5a78749d`.
- Chapter 5 request: `chapter-05-fixture-c5-p5-before-provenance-20261015:8acc144c592ea10b`; source fingerprint `d9ca4d7202a1c05a3965fcffa48e8d5b6a33bff727a825f10a791e5fabc319ac`. The revision changed prose only; current accepted Chapter 5 is 1,097 words.
- Chapter 6 was re-prepared after Chapter 5 v2 acceptance: `chapter-06-fixture-c6-refreshed-after-c5-v2-20261015:e838c7396405ec1c`; source fingerprint `2f26a57d8e30e4537e706d84d508bab662e65d70aedeedd9903d4e47ffd94e78`. Earlier Chapter 6 candidates remain unaccepted; v3 is bound to this refreshed request.
- A separate Python process loaded the project with `Project.load`. Chapters 1-6 all returned accepted; `project_draft_review` found each final equal to its latest candidate; Chapter 1 retained the required SHA. Re-preparing the current Chapter 6 request returned the same source fingerprint.

## Verification

- Focused tests: `tests/test_beginner_story_development_application.py`, `tests/test_beginner_post_draft.py`, and `tests/test_chapter_generation.py` — 32 collected, 32 passed, 0 skipped, 0 xfailed, 0 xpassed, 0 failed, 0 errors.
- An initial run imported the stale editable package under `auteur-studio-ux-checkout` and failed 7 generation-receipt tests. Import-path inspection confirmed the mismatch; setting `PYTHONPATH` to this exact source checkout made the same 32 tests pass. This was an environment issue, not a source change.
- No validation reports were fabricated. The existing review projection reports `review artifact missing` for the accepted chapters; manual content review and missing automated review artifacts are recorded separately.

## Separate dispositions

- **F2 narrative capability:** Bounded simulated-author pass for this reconstructed six-Chapter journey. The run preserved P1 discovery, propagated P2/P3, maintained P4 relationship consequences, explicitly revised underlength Chapter 5, recorded P5 compatible divergence, and preserved P6 uncertainty. This does not establish independent human creative judgment or prove general narrative quality.
- **X3 persistent workspace:** API/file-level pass in the reconstructed project. The six accepted outputs and selected facts survived a fresh process load and retained matching candidate/final bytes. This does not qualify browser interaction, mobile layout, or human UX.

## PR #343 relevance

PR #343 proposes exact source references to retain older accepted evidence when lexical overlap would otherwise omit it. In this journey, Chapter 6's current outline named Beatrice, displacement evidence, and public history; the actual fresh Chapter 6 context selected both `bible.json#/events/3` and `chapters/02/final.md`, and the resulting prose used that evidence. The specific omission failure addressed by PR #343 was not observed, so this run does not justify merging it speculatively. It remains open and unqualified by this reconstruction.

## Remaining limits

- No browser or mobile interaction was run, and no human UX session was performed.
- Automated post-draft validation artifacts are absent; acceptance here was based on explicit, documented simulated test-author review.
- The original workspace's identity and historic persistence state remain unavailable. This report describes only new evidence from the disposable reconstruction.
- Chapter 1's 946-word deviation was intentionally preserved. Chapter 5's short v1 was preserved as evidence and superseded by the explicitly reviewed 1,097-word v2.
- No product code changed, no PR was merged, and no production readiness is claimed.

At the time of this October 15 report, the next warranted responsibility was a Browser workflow. That follow-up was completed later on current integrated source and is recorded in [the X3 Browser review](glass-archive-x3-browser-review-20261015.md). This fixture report remains the historical record for the separate simulated-author six-Chapter reconstruction; it is not recovery of the original Windows project. Human UX and broader product readiness remain unqualified.
