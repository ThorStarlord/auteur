# Atelier: Architecture-to-Book impact and reconciliation — evidence

**What was tested:** branch `feat/atelier-book-impact`, built on `main@c57fa763` (#634).

**How the data was made:** every project was seeded through its owners with
`scripts/seed_book_impact_study.py`.
- `impact`: Books 24–29 in the six cases.
- `current`: Books 24 and 25, both current.

**Who did what:**
- **The author (simulated):** every author action ran in a served Studio, driven by Playwright.
- **The coding agent (for real):** a separate subagent fulfilled the Book reconciliation request. It was
  given only the message the Studio displayed (`authentic/agent_message.txt`), and it used the Working
  Book owner's own commands.
- **The Architecture revision (constructed):** its coding-agent answer was built by a script and is
  recorded as such (`authentic/architecture-candidate-constructed.json`). It rewords the Ledger engine and
  removes the Gate Table.

**Limit:** agents operated every walkthrough. This is not evidence of human usability, and it does not
judge the Book's literary quality.

## Before (`before/`)

`main` served the same `impact` records:
- Book 24 said only "A concept it refers to is no longer in the working Architecture", and showed the
  removed concept as `inst_gate_table · no longer recorded`.
- The reworded Ledger engine was not mentioned (`mentions_ledger_rewording: false`): the owner's single
  impact flag stops at the first removed node.
- There was no view across Books, and nothing led from an Architecture revision to the Books.

## Authentic journey (`authentic/`)

| Step | Evidence |
|---|---|
| 1. The author revises the Architecture in the Studio and applies it | `log-A-desktop.json`. The writes are the Architecture prepare and apply, plus the canvas save the Studio makes before an apply. `books_unchanged_by_architecture_revision: true` |
| 2. "What this means for the Books" | `overview-desktop.txt` |
| 3. Book 24's evidence: the Ledger engine before and now; the Gate Table as the Book recorded it; the citing elements | `evidence-24-desktop.txt` |
| 4. Reconcile, then the author adds a note, then Prepare (the only Book write) | `instruction.txt`, `agent_message.txt` |
| 5. The coding agent's response | `coding-agent-candidate.json`. It was `review_ready` on the first submission: 7 changed, 6 added, 81 unchanged, 0 outside scope |
| 6. Review on a phone at 390×844, without applying | `review-phone.txt`, `log-B-phone.json` (no writes, no overflow) |
| 7. Apply on desktop, then back to the atlas | `log-B-desktop.json` and `after-apply-desktop.txt`: apply was the only write, there were no revision marks, the place was kept after Apply and after Escape, and the overview now lists Book 24 as current while Book 25 is still flagged |
| 8. Integrity | 0 of the 12 project files outside Book 24's records changed. `fresh-resume-24.json` shows a new process reading revision 1 as `ready`, with lineage `develop`, then `revise` recorded `currentness: current` |
| 9. A blocked attempt and the CLI rule | `stale.txt`: a whole-Book reconciliation made stale by another Architecture revision is refused, and Book 25 is unchanged. A CLI targeted revision of out-of-date Book 25 applies with `currentness: kept_baseline` and stays `stale`. A repeated Apply gives `already_applied` |

The coding agent pointed out one thing that matters beyond this change. The Architecture revision removed
the Gate Table node, but three of the Architecture's open questions still name it. A Book revision cannot
change them. This is an Architecture-side inconsistency, and the reverse direction (Book findings proposing
Architecture changes) is the next opportunity.

## Final view (`final-view/`)

The same journey was run again with the final UI on a fresh `current` project, replaying the coding agent's
recorded candidate through `book-complete-file`. It also shows the six-Book overview at desktop and phone
width, with Book 25's evidence (source changed) and Book 26's evidence (out of date; every cited concept
unchanged; what changed is not cited). Every view has 0 page errors and 0 horizontal overflow.
