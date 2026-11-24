# Atelier: a working Book discovery, considered for the Architecture — evidence

**What was tested:** branch `feat/atelier-book-discovery`, built on `main@b91f5c78` (#636).

**How the data was made:** every project was seeded through its owners with
`scripts/seed_book_discovery_study.py`. That is Spring Ledger after the #635 run: Book 24, reconciled by
the coding agent's recorded answer, records the open question `unk-tally-hours`, which cites the Ledger
engine.

**Who did what:**
- **The author (simulated):** every author action, including the choice of alternative and the Apply, was
  operated by an agent in a served Studio driven by Playwright. That is qualification, not a human decision.
- **The coding agents (for real):** separate subagents answered the inquiry and the Architecture revision.
  Each was given only an author-style request, and each used the owners' own commands.

**Limit:** this is not evidence of human usability, and it does not judge literary quality.

## Before (`main@b91f5c78`)

The inquiry contract had no way to carry a Book element: `GraphIntent` refuses `book_evidence` as an extra
input. The Book owner had no evidence read, and the inquiry module never mentions a Book. An author could
only paste the Book's words into the question, where they would read as the author's own statement.

## Authentic journey (`authentic/`)

| Step | Evidence |
|---|---|
| 1. Book 24's open question, considered for the Architecture | `discovery-desktop.txt`. It shows what the Book records, the element's standing (agent proposal, undecided), the recorded reference ("Ledger engine", unchanged), and what is established and what is not |
| 2. Asked through the existing panel, with the element as Book evidence (the question was written by the author) | The request packet's `book_evidence` section; its settings record the Book revision and element identity |
| 3. The coding agent's answer | `coding-agent-inquiry-answer.json`. It was `ready` on the first submission, with three distinct alternatives. The agent judged that the question can stay in Book 24, and flagged one Architecture-level ambiguity (does the hours column set draw?) |
| 4. The author's choice (agent-operated) | `author-choice-agent-operated.json`: develop h1 narrowly, as a clarification |
| 5. The Architecture revision, through the selected-alternative contract | The request carries h1 and the Book evidence (`status_at_revision: current`). A second coding agent's candidate (`coding-agent-architecture-candidate.json`) was `review_ready` on its first submission and changed one field, `eng_ledger.summary` |
| 6. Review and explicit Apply | `architecture-review-desktop.txt` |

After Apply:
- **The Architecture's adoption lineage** records that h1 came from Book 24's `unk-tally-hours`.
- **No Book record changed:** `books_unchanged_by_architecture_apply: true`.

## Final view (`final-view/`, desktop)

The same journey was run again with the final code on a fresh project, replaying both coding agents'
recorded answers through the owners' CLIs. Results (`log-desktop.json`):
- **No errors:** 0 page errors and 0 sideways scroll.
- **Writes:**
  - the inquiry prepare, the revision prepare and the Apply;
  - two canvas saves made by the Studio's existing behaviour: the view save from "Check agent result", and
    the save before an Architecture apply.
- **Place:** the atlas place was kept, and the atlas marks the Architecture revision.
- **Discovery:** still open on Book 24 after Apply. It now shows the Ledger engine as changed since the Book
  was written.

What the author sees:
- **The review** (`architecture-review-desktop.txt`) says the revision was "Developed from alternative h1 …
  of an inquiry asked with Book 24's unresolved unk-tally-hours, a working Book proposal, not Architecture
  fact".
- **The impact overview** (`impact-desktop.txt`) lists Books 24 and 25 as citing the changed Ledger engine.
  Neither Book was modified or reconciled.

## No-change outcome (`no-change/`, phone 390 × 844)

On a fresh project the author takes these steps:
1. Asks with the Book evidence.
2. Reads the same real answer.
3. Develops no alternative.
4. Returns to the discovery card.
5. Keeps the element in Book 24.

Results (`log-phone.json`):
- **The story's records:** `narrative_unchanged_without_revision: true`. The Architecture, every Book record,
  and the canvas items, positions and connections are as they were.
- **The only writes:** the inquiry request, and the Studio's view save from "Check agent result".
- **No errors:** 0 page errors and 0 sideways scroll.
