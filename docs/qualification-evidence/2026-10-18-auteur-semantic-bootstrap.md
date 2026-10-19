# Auteur repository-semantic-steward initial semantic pilot (candidate)

**Source identity:** `ThorStarlord/auteur@bb9c102d6cc4e9473ca7cffc5253ed72361ef37a`
**Sensemaking candidate:** `ThorStarlord/sensemaking-skills` PR #555, stacked on PR #553.
**State:** source-reviewed proposed knowledge, NOT independently agent-qualified.
**Authority:** Auteur MISSION.md and docs/narrative-architecture.md remain primary; these semantic JSON files are a *review proposal*, not canonical story state or product design revisions.

## First-visit result

Created a focused, deliberately cross-layer authored semantic proposal:

- `product-and-domain.json`: author authority, non-goals, five narrative layers, independent scope axis, canonical vs derived, ADR 019.
- `studio-and-workspace.json`: working canvas, Book re-entry, Chapter Working/Kept distinction, existing HTTP/UI integration, tests as *source evidence*.
- `engineering-history.json`: exact main-specific source observations, historical STATUS limitations and an unqualified real Browser hypothesis.

Selected original sources inspected: `MISSION.md`, `docs/narrative-architecture.md`,
`docs/adr/019-derived-global-map-and-story-instance-relation-authority.md`,
`docs/product/auteur-system-interaction-map.md`,
`docs/architecture/system-ownership-and-product-compression.md`,
`src/auteur/beginner/book_orientation.py`,
`src/auteur/beginner/book_progress.py`,
`src/auteur/beginner/studio_store.py`,
`src/auteur/beginner/browser/studio.js`,
`src/auteur/beginner/server.py`, and their named focused source tests.

The relations deliberately distinguish documented rules, observed source code,
and hypotheses. The semantic relation `implemented_by` was used only for
manually inspected code paths, not inferred from shared filenames.

## Known limitations

- This model does not claim comprehensive repository ontology coverage.
- Existing STATUS.md is historically dated and may not describe current main.
- No full Auteur checkout was available in this connector workspace for
  `semantic knowledge-build`, `knowledge-proposal-check`, pytest, or Browser.
- No executable coding-agent CLI, independent new agent context, human author
  validation or deployment was operated in this pilot.
- A test file's existence and assertions are not test execution evidence.
- A JSON model is not accepted merely because GitHub stores the blob.
- ADR 019's three-digit filename needs the Sensemaking proposed importer change.
- JavaScript files are path-indexed in the proposed bootstrap, not parsed for
  runtime architecture/dependencies.

## Next qualification

In a real clean Auteur checkout, install an exact tested Sensemaking candidate,
check these draft claims/edges against original current sources, then run
`knowledge-proposal-check` on the working proposal and `knowledge-build` on
its committed source revision in an isolated clean worktree. Inspect
`explain`, `why`, `impact`, `history`, and source `knowledge-audit` output.

Select a warranted, real Issue #318 Book-reentry engineering responsibility.
Start a genuinely **new, independent** coding-agent session for actual reuse,
then update the affected semantic records after the returned engineering
evidence. Do not report an independent-agent PASS before that happens.

## Independent coding-agent episode B — Book re-entry source check

**Date:** 2026-10-19. **Agent identity:** fresh independent coding-agent episode with no inherited conversation history; model/runtime identity and agent token/time accounting were unavailable. **Source pins:** Sensemaking Skills `main@d67cfe560a3f649e065ad8adc024c01d1163603a`; Auteur `7bd985113ed26074240500807c732aee5d09e913` (draft PR #466 source revision). **Skill:** `repository-semantic-steward` at the pinned Sensemaking SHA, RECALL followed by RECONCILE disposition.

### Retrieval and original-source check

The exact-clean Auteur checkout was oriented and indexed outside the checkout using the pinned Sensemaking source. The first attempt through the globally installed `sensemaking-skills.exe` did not expose the requested commands; the episode then invoked the pinned source directly through `PYTHONPATH`. `knowledge-orient` returned 2,412 tracked files with no path truncation and explicitly did not establish semantic truth. `knowledge-build` indexed 746 claims and 705 relations at the pinned Auteur SHA, digest `ffaf9a57b4db5d93c76d0366d55ed426d091d9f88b3927889ee9615bb63117de`. The resulting SQLite index was `H:\GithubRepositories\_rss-pilot-auteur-episode-b.sqlite`, outside the Auteur checkout.

Queries used `search` for “Book re-entry current Chapter Working Kept Studio canvas” (no matches; lexical search did not add useful evidence), then `explain` for `cap:book-reentry-orientation` and `cap:book-studio-view`. The retrieved statements were checked against their current cited sources. The three candidate JSON packs were source-read; this episode found their relevant Book claims accurate at this SHA.

Original sources inspected: `MISSION.md`, `docs/narrative-architecture.md`, `docs/adr/019-derived-global-map-and-story-instance-relation-authority.md`, `docs/architecture/system-ownership-and-product-compression.md`, `docs/product/auteur-system-interaction-map.md`, `src/auteur/beginner/book_orientation.py`, `src/auteur/beginner/book_progress.py`, `src/auteur/beginner/studio_store.py`, `src/auteur/beginner/browser/studio.js`, `src/auteur/beginner/server.py`, `src/auteur/status.py`, `src/auteur/expression/book.py`, and the four focused Book-progress, Studio-view, Studio-re-entry and Studio-authority test modules.

### Engineering decision and verification

The evidence does not show a product-code defect in the requested flow. The read-only `/api/beginner/book/progress` projection identifies the first unfinished Chapter from `chapters/<n>/final.md` kept prose and the latest `draft_vN.md`; a draft byte difference makes that Chapter Working while its `final.md` remains in accepted history. The blueprint supplies planned count; discovered folders alone do not establish completion. Studio restores the most recent ready working canvas when reopening without an explicit canvas, then loads the derived Book orientation when Book artifacts exist. It marks that view `DERIVED / NOT CANON`, routes opening a Chapter into the existing Beginner review interface, protects unsaved canvas work when switching, and does not accept Book content. `CanvasStore` persists only revision-checked working documents separately from accepted story state. These findings match the existing knowledge; disposition: **NO_MODEL_CHANGE** for the semantic records.

The requested focused runtime suite exposed one faulty test expectation: `test_book_progress_reuses_accepted_book_as_publication_preflight` expected accepted Book-expression sources to count as the separate `final.md` Chapter history. `BookExpressionStore` accepts a composed Book from Chapter Expressions; it does not create `final.md` history. Corrected that assertion to encode the separation. No product code or controlled #318 fixture/data was changed. Focused verification after the correction:

- `python -m pytest tests/test_beginner_book_progress.py tests/test_beginner_studio_book_view.py tests/test_beginner_studio_reentry.py tests/test_beginner_studio_authority_integration.py -q` — **15 passed**.
- `git diff --check` — passed.

### Qualification boundary

This episode demonstrates independent retrieval followed by original-source checking, and practical usefulness in finding a mistaken test assumption. It does not demonstrate a product-code repair, live Browser usability, completion of Issue #318, or comparative causal benefit over retrieval without the semantic pack. It is one independent re-entry episode after the initial proposal; it does not establish full Issue #554 acceptance or transfer to a second product. No hourly/token/cost metrics were available. No semantic pack proposal was necessary or changed; all three authored packs remain unmodified.

The test/evidence update was committed locally as `325e117c453c9a3ba89d676eae457f42f210b964` (`test: clarify book expression and chapter history`). At that exact clean commit, `knowledge-orient` again covered 2,412 tracked files and `knowledge-build` indexed 746 claims / 705 relations, digest `50cb5d1f9633da57c594d6b079bc8d6671c69f4d45198e526febef8f60fb64ff`, to `H:\GithubRepositories\_rss-pilot-auteur-episode-b-result.sqlite`; `explain cap:book-reentry-orientation` returned the same checked Book boundary. The first post-commit pytest invocation inherited Sensemaking's `PYTHONPATH` and failed collection because Auteur's `src` was not on that invocation's import path; rerunning with `PYTHONPATH=src` passed all 15 focused tests.

## Fresh-session accumulated-knowledge recovery check

**Date:** 2026-10-19. **Agent identity:** separate no-history coding-agent session; model/runtime identity and agent token/time accounting unavailable. **Source pins:** Sensemaking Skills `main@d67cfe560a3f649e065ad8adc024c01d1163603a`; Auteur `06a0f53f3d03000e03c41cb04c6da9c6ab324f2a`. This was a recovery check only; no files were changed.

The fresh agent read the persisted `studio-and-workspace.json` records (`cap:book-reentry-orientation`, `comp:book-orientation`, `inv:working-vs-kept`, `inv:book-plan-not-discovery`, `cap:book-studio-view`, `comp:book-progress`, and `inv:book-progress-not-canon`) and independently verified them against `book_orientation.py`, `book_progress.py`, Studio UI/server code, and the focused tests. It accurately recovered that `final.md` remains kept Chapter history while a differing latest `draft_vN.md` is Working; planned Chapter count comes from the blueprint; Studio's orientation is derived and read-only; and opening a Chapter enters the existing review flow. It found no product defect in this read-only check.

The installed CLI available to that fresh agent lacked `knowledge-build` and `knowledge-query`, so **that fresh session did not execute an SQLite query**. Separately, using the pinned Sensemaking source module from the main agent, `knowledge-build` on the same clean Auteur HEAD indexed 1,269 claims and 1,705 relations, digest `9d703a2d0aa4a457ee851b04ec4eb33ccd50c4192877f5cd0be91ec187595f10`, to `H:\GithubRepositories\_rss-pilot-index\auteur-final.sqlite`. `explain` queries for `cap:book-reentry-orientation`, `inv:working-vs-kept`, and `inv:book-progress-not-canon` returned the expected source-linked records and relations. This demonstrates index mechanics and fresh-session recovery independently, but not fresh-session use of the SQLite index. Selection/import truncation and non-authoritative claim limits applied.

At the final exact Auteur HEAD, all three candidate packs passed source-pinned `knowledge-proposal-check` (15/6 product claims/relations; 16/17 Studio/workspace; 4/3 engineering history), and the focused runtime suite passed **15 tests**. No semantic model edits were warranted. The two fresh-session episodes provide accurate source-checked recall, but do not satisfy Issue #554's complete product-value qualification: the second fresh session read the authored records directly rather than querying SQLite, no Issue #318 product-code responsibility or live Browser session was completed, and comparative benefit plus time/token costs remain unmeasured.
