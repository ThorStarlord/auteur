# Graph-first Book re-entry: human walkthrough

**State:** prepared 2026-10-20; no human session has been observed yet. This is
an exploratory product-use session, not a readiness gate or a claim of human
UX qualification.

## Pins and disposable data

- Auteur source: `main@7043f9cd5b031b218e5e75ca953f496ee7030e90` (PR #437 merge;
  includes the PR #439 Studio navigation repair).
- Original fixture: `C:/Users/Admin/AppData/Local/Temp/glass-archive-fixture-complete-20261015/project`,
  reconstructed against source `ef5ae8c7910fe7b3db38f6e2af87d1f45ed6182c`.
- Existing test-only Working revision source:
  `C:/Users/Admin/AppData/Local/Temp/glass-archive-pr439-chapter-state-20261015/chapters/02/draft_v2.md`.
  It was copied from a prior disposable Browser-state probe. It retains the
  explicit `Disposable state probe` marker; it is not new author prose.
- Walkthrough project:
  `C:/Users/Admin/AppData/Local/Temp/auteur-human-book-walkthrough-20261020/project`.
  This is a copy of the complete fixture plus that existing Chapter 2 Working
  revision. Canonical `final.md` files and acceptance receipts are preserved;
  no acceptance, reconciliation, publication, or provider call was performed.
- The project manifest has `schema_version: 1` and `created_at: null`; this
  format supplies no project ID. Do not invent one. Identify this copy by its
  path and manifest SHA-256:
  `af47fcd7addfafcc6d9268e1c12ab13c4eaa70c6099cdcd2100f507824d520c8`.
  Its 92-file SHA-256 list is beside it at
  `C:/Users/Admin/AppData/Local/Temp/auteur-human-book-walkthrough-20261020/SHA256SUMS.txt`.
- Chapter 2 kept manuscript SHA-256:
  `4381a19074f0a3a421c10a369c2b7e444ccc74e75706fe9e8bab6e378af3c594`.
  The separate test-only Working `draft_v2.md` SHA-256 is
  `169462407b606d70ec7a8653b8ca2dfdc3000e78a9c5a215ea984285798d0861`.
- Before any Browser visit, the source projection reported six kept Chapter
  finals, Chapter 2 Working, six Chapter 2 Suggested updates, and the next
  action `Continue Chapter 2`. This is setup state, not a participant outcome.
- Installed interactive browser available for this session: Google Chrome
  `155.0.8059.84` (verified from the installed executable's version metadata).
  The participant should confirm the actual session at `chrome://version` and
  record it below. No human interaction has run yet.

The two source fixture trees remain untouched. Only the disposable project copy
is served. If the UI creates or saves Studio canvas state, that remains in this
copy and is outside accepted story authority.

## Start the local Browser session

The server is currently running from the pinned Auteur checkout at
`H:\GithubRepositories\_rss-pilot-auteur-human-book-walkthrough` (PID 4820),
using Python `3.14.3`. It was started without provider/model arguments; no
generation request has been made. Open:

**http://127.0.0.1:8876/studio.html**

To restart it in PowerShell after it is stopped:

```powershell
$env:PYTHONPATH = 'H:\GithubRepositories\_rss-pilot-auteur-human-book-walkthrough\src'
python -m auteur.beginner.server `
  --project 'C:\Users\Admin\AppData\Local\Temp\auteur-human-book-walkthrough-20261020\project' `
  --port 8876
```

Then open `http://127.0.0.1:8876/studio.html` in Chrome. Stop the server with
Ctrl+C in its terminal if it was started interactively. The already-running
server is a background process. Before stopping it, confirm PID 4820 still has
the command line above; then use:

```powershell
Stop-Process -Id 4820
```

Do not enter API credentials or invoke an external model during this
walkthrough. Stop before any UI action that requires a model call. The
participant may explore and edit this disposable copy, but any story change
must remain explicitly Working unless the author independently chooses to
accept it.

## Participant task

Read only this task before starting; do not explain the interface or identify a
correct route:

> You are returning to this Book after a break. Use the screen to work out
> where you left off and what you would do next. Review enough of the story to
> decide how you want to continue writing. Stop when you are ready to continue
> or when you reach an action that needs help.

Do not coach. If the participant asks what a control means, respond: “What do
you expect it to do?” Record the question and their expectation before
answering. The participant may stop at any time. Do not ask them to accept a
suggestion or Working revision.

After the task, ask these open questions without correcting their answers:

1. Which parts of this Book do you believe are already kept, still being
   worked on, or only suggested?
2. What do you believe the next action will do? What would you expect after
   that?
3. Was there a point where you were unsure where you were or what changed?
4. What, if anything, would you change before using this to continue your own
   writing?

## Observation record

Keep observations separate from preferences and interpretations. Record exact
actions/words when useful; do not infer confusion from hesitation alone.

- Date/time and participant role (no personal identifying details unless the
  participant explicitly wants them recorded):
- Confirmed browser/version (`chrome://version`):
- Server/source SHA and project path/manifest SHA above:
- Initial screen and first action:
- Route taken to inspect a Chapter/manuscript:
- What the participant thought was kept, Working, and Suggested:
- Route back to the graph and the next action they selected:
- Whether they reached another Chapter's planning/writing surface:
- Exact places they hesitated, misread a label, asked for help, or stopped:
- Participant's own preferences (quote or close paraphrase):
- Observer interpretation, kept separate from the observation:
- Any project files changed; verify kept final hashes and acceptance receipts:
- Explicit limits and follow-up:

No participant has completed this walkthrough yet. Automated Browser checks,
the six-Chapter simulated-author run, and this prepared session do not count as
human evidence.
