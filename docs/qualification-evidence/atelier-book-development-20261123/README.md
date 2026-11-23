# Atelier × Working Book development — evidence (2026-11-23)

**Design note:** [`../../design/2026-11-23-atelier-book-development.md`](../../design/2026-11-23-atelier-book-development.md).

Every file here was written by a script or a served run. Nothing was reconstructed by hand.

## The same author task, before and after

**Task:** from the Ledger engine concept, revise one element of Spring Ledger working Book 24 (`eng-record-form`, an Engine that records a reference to `eng_ledger`).

| | `main@19ec9dc2` (`baseline.json`) | this branch (`authentic/`) |
|---|---|---|
| Where | outside the Studio: three Working Book CLI commands | inside the Atelier, from the concept |
| Choosing the element | type its id after `--target` | **Develop this element** beside what the Book records about the concept |
| Request | `book-prepare` prints about 160 KB | the target, scope and standing in words, then Prepare |
| Coding agent | `book-complete-file` | the same owner commands (`book-show`, `book-complete-file`), quoted in a message the Studio shows |
| Review | 6.9 KB of raw JSON keyed by element ids | each change in words, with before and after, links to re-read, and the Architecture concepts cited |
| Apply | `book-apply-review --request-sha256 <copied 64 hex>` | **Apply this revision to working Book 24** |
| Back in the atlas | not applicable | same focus, trail, camera and positions; no Architecture concept marked |

## Authentic journey (`authentic/`)

- **Project:** a disposable project seeded by `scripts/seed_series_context_study.py`. It holds the Spring Ledger W6 Architecture and Book 24, plus the test Series plan and Directions, so their isolation can be checked.
- **Server:** `python -m auteur.beginner.server` on a local port.
- **Author steps:** played with Playwright.
- **Coding-agent step:** done by a separate coding agent. It was given only the message the Studio displayed (`agent_message.txt`) and the environment path. It used `book-show`, wrote the revised Book (`coding-agent-candidate.json`) and submitted it with `book-complete-file`. The owner accepted the first submission as `review_ready`.

The steps:
1. `log-A-desktop.json`: the author prepares the request at 1440 × 900. The only write is `POST …/books/24/prepare`. Focus moves into the instruction, then to Check.
2. `log-B-phone.json` and `review-phone.txt`: the author returns at 390 × 844 and reads the review. There are no writes and no horizontal overflow.
3. The review covers:
   - 2 changed elements: the engine's wording, condition, choice, consequence, changed state and new possibility, and one link's stated function;
   - 3 added elements: an assumption and two typed edges;
   - 86 unchanged elements;
   - no unexpected changes, author decisions or standing changes.
4. `log-B-desktop.json`: Apply. The only write is `POST …/books/24/apply`.
   - `revision_marks` is `null`, so no Architecture concept was marked as changed.
   - The atlas place was kept after Apply and after Escape, and focus returned to `series-open:24`.
5. `after-integrity.json`:
   - 0 of the 16 files outside Book 24's records changed, including `series_identity.yaml`, the 5 Direction files, the canvas and the working Architecture.
   - A fresh process (`book-resume`) returns working revision 1, with lineage develop → revise and freshness `ready`.
6. `stale.txt`: on a copy, a second request is prepared, and an applied Architecture revision then removes a node the Book refers to. The view reports that the request no longer matches and why, and offers to prepare it again.

## Final view (`final-view/`)

After the independent reviews changed the view, the same journey was captured again on a fresh project with the final head. The coding agent's recorded candidate (`authentic/coding-agent-candidate.json`) was submitted to the new request with the same owner command, `book-complete-file`, so the review content is the agent's. Prepare and Apply are again the only writes; `revision_marks` is `null`; the atlas place is kept after Apply and after Escape; there is no horizontal overflow at 390 × 844.

The fixtures are recorded agent output and test fixtures. No author has used this, and nothing here judges the revision's literary quality.

## Scripts

- `measure_baseline.py <sha> <out>`: the baseline task on a checkout of `main`, through the CLI.
