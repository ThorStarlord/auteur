# Auteur repository-semantic-steward initial semantic pilot (candidate)

**Source identity:** `ThorStarlord/auteur@bb9c102d6cc4e9473ca7cffc5253ed72361ef37a`
**Sensemaking source:** integrated `main@d67cfe560a3f649e065ad8adc024c01d1163603a`.
**State at current candidate:** knowledge schema/path checks, source-pinned indexing, one independent engineering/reconciliation episode, and one independent recovery episode completed. Full Issue #554 acceptance remains incomplete.
**Authority:** Auteur MISSION.md and docs/narrative-architecture.md remain primary; these semantic JSON files are a *review proposal*, not canonical story state or product design revisions.

## Historical first-visit baseline — 2026-10-18

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

This proposal began from Auteur `main@bb9c102d6cc4e9473ca7cffc5253ed72361ef37a`, after PR #439's graph-first Book re-entry repair had reached main. It was initially a source-reviewed model only; no test execution or index build was claimed at that baseline.

## Baseline limitations recorded before execution

- This model does not claim comprehensive repository ontology coverage.
- Existing STATUS.md is historically dated and may not describe current main.
- The initial connector-only review had no local Auteur runtime, so it could
  not execute `knowledge-build`, proposal validation, pytest, or Browser.
- At that point there was no independent-agent episode, human author
  validation, or deployment.
- A test file's existence and assertions are not test execution evidence.
- A JSON model is not accepted merely because GitHub stores the blob.
- ADR 019's three-digit filename needs the Sensemaking proposed importer change.
- JavaScript files are path-indexed in the proposed bootstrap, not parsed for
  runtime architecture/dependencies.

## Current status and remaining qualification — 2026-10-19

**Completed pilot evidence:** all three packs pass source-pinned proposal
validation; a clean exact candidate was indexed; an independent engineering
episode source-checked the Book model and corrected one test expectation; a
separate independent recovery episode correctly reconstructed the model and
checked original sources. The focused Book/Studio suite passes 15 tests. No
product behavior changed in this PR.

**Historical product-use evidence:** Issue #318's original Windows run accepted
a 946-word Chapter 1 and stopped at a 965-word, unaccepted Chapter 2 against a
1,066-word minimum. It did not complete Chapters 3–6. A separate
fixture-complete reconstruction received six simulated-author decisions and
qualified only bounded F2 behavior plus API/file persistence. The later
graph-first Browser work reached main in PR #439; exact candidate checks cover
named navigation and re-entry paths. These executions are separate and do not
combine into a six-Chapter live-author or human-UX pass. Details remain in
[Issue #318](https://github.com/ThorStarlord/auteur/issues/318), [PR #437](https://github.com/ThorStarlord/auteur/pull/437), and its linked evidence.

**Current limitations:** F2's full controlled journey remains incomplete; the
current-runtime Chapter-2 continuation probe has not run. Overall Browser
experience, long-history density, manuscript navigation, and human UX remain
unqualified. The independent recovery session read the authored JSON directly;
it did not query SQLite. Comparative benefit and agent time/token costs remain
unmeasured. No Issue #554 PASS is claimed.

**Remaining work:** resume the existing Issue #318 Chapter-2 checkpoint using
the frozen fixture and its explicit minimum/self-check procedure, if the
configured target runtime and required observability are available. Preserve
the accepted Chapter 1 and unaccepted Chapter 2; do not relax the threshold or
change the fixture. Continue later Chapters only after that checkpoint. For
Issue #554, use the pinned installed CLI in another fresh session to retrieve
and source-check accumulated knowledge during that real responsibility, then
compare observed work with ordinary source inspection without claiming causal
benefit. Keep all F2, X3 persistence, Browser, and human-UX verdicts separate.

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

## CLI installation and retrieval check — 2026-10-19

The earlier fresh agent's missing-command report came from executable
resolution, not an unavailable implementation. In the active Windows agent
environment, Get-Command sensemaking-skills -All selected
C:\Users\Admin\AppData\Roaming\Python\Python314\Scripts\sensemaking-skills.exe
first. Its installed package was 1.0.0rc3, editable from the older, dirty
H:\GithubRepositories\sensemaking-skills checkout. A second script existed
under H:\Python\Python312\Scripts. The first executable's semantic --help did
not list knowledge-orient, knowledge-build, knowledge-query, knowledge-audit,
or knowledge-proposal-check.

Installed a separate persistent tool environment from the integrated source
pin, leaving those existing scripts untouched:

    uv tool install --python C:\Python314\python.exe --with click==8.5.0 --with PyYAML==6.0.3 --from git+https://github.com/ThorStarlord/sensemaking-skills.git@d67cfe560a3f649e065ad8adc024c01d1163603a sensemaking-skills
    uv tool run --from git+https://github.com/ThorStarlord/sensemaking-skills.git@d67cfe560a3f649e065ad8adc024c01d1163603a sensemaking-skills --version

The pinned invocation reports 1.0.0rc5.dev0; help confirmed all five
commands. Calling uv tool run sensemaking-skills without --from resolved an
unrelated 0.2.1 command with no semantic group, so the exact source ref must
remain on each invocation.

From this same installed environment, the clean candidate at
4fc9b75a51e55e976a940fd32090bfcd9d8a6ea0 indexed 1,269 claims and 1,705
relations, digest
255102a92786da196da447e7fbd4579fc6ff077c6031517473b181c5b1f3f7b5. All
three knowledge-proposal-check commands passed. Search for
'Book re-entry current Chapter Working Kept Studio canvas' returned no claims;
search for 'Book re-entry' returned three relevant claims. The implementation
confirms the reason: search performs case-insensitive literal substring
matching against one claim statement or ID. It is not natural-language search.
The RECALL instructions now tell agents to use known claim IDs or short literal
phrases, inspect returned IDs, and open the original cited sources.

## Fresh-session accumulated-knowledge recovery check

**Date:** 2026-10-19. **Agent identity:** separate no-history coding-agent session; model/runtime identity and agent token/time accounting unavailable. **Source pins:** Sensemaking Skills `main@d67cfe560a3f649e065ad8adc024c01d1163603a`; Auteur `06a0f53f3d03000e03c41cb04c6da9c6ab324f2a`. This was a recovery check only; no files were changed.

The fresh agent read the persisted `studio-and-workspace.json` records (`cap:book-reentry-orientation`, `comp:book-orientation`, `inv:working-vs-kept`, `inv:book-plan-not-discovery`, `cap:book-studio-view`, `comp:book-progress`, and `inv:book-progress-not-canon`) and independently verified them against `book_orientation.py`, `book_progress.py`, Studio UI/server code, and the focused tests. It accurately recovered that `final.md` remains kept Chapter history while a differing latest `draft_vN.md` is Working; planned Chapter count comes from the blueprint; Studio's orientation is derived and read-only; and opening a Chapter enters the existing review flow. It found no product defect in this read-only check.

The installed CLI available to that fresh agent lacked `knowledge-build` and `knowledge-query`, so **that fresh session did not execute an SQLite query**. Separately, using the pinned Sensemaking source module from the main agent, `knowledge-build` on the same clean Auteur HEAD indexed 1,269 claims and 1,705 relations, digest `9d703a2d0aa4a457ee851b04ec4eb33ccd50c4192877f5cd0be91ec187595f10`, to `H:\GithubRepositories\_rss-pilot-index\auteur-final.sqlite`. `explain` queries for `cap:book-reentry-orientation`, `inv:working-vs-kept`, and `inv:book-progress-not-canon` returned the expected source-linked records and relations. This demonstrates index mechanics and fresh-session recovery independently, but not fresh-session use of the SQLite index. Selection/import truncation and non-authoritative claim limits applied.

At the final exact Auteur HEAD, all three candidate packs passed source-pinned `knowledge-proposal-check` (15/6 product claims/relations; 16/17 Studio/workspace; 4/3 engineering history), and the focused runtime suite passed **15 tests**. No semantic model edits were warranted. The two fresh-session episodes provide accurate source-checked recall, but do not satisfy Issue #554's complete product-value qualification: the second fresh session read the authored records directly rather than querying SQLite, no Issue #318 product-code responsibility or live Browser session was completed, and comparative benefit plus time/token costs remain unmeasured.
