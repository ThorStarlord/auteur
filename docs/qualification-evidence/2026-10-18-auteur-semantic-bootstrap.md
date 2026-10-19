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
