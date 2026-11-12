# Working-revision lifecycle: end-to-end evidence (The Spring Ledger, 2026-11-12)

This folder records one disposable-project walkthrough of the Studio architecture bridge's working-revision lifecycle, using The Spring Ledger's consolidated architecture and its Book 24 revision. It is evidence about the product's operations. It is not canon, and it is not a creative qualification of the Series.

## What was run

`run_walkthrough.py` drives the real command-line bridge. Each step is a separate `python -m auteur.beginner.studio_architecture` process. The inputs were read read-only from two commits with `git show`, and nothing in those commits was modified:

- the consolidated working architecture, `experiments/spring-ledger-working-architecture/02-working-candidate-W6.json`, and the corrected Book 24 candidate, `.../cold-start/output/book-24-candidate.corrected-2.json`, both at PR #555's head `fa85b7f1c2fbfdf8d5b8b35f6ce64c27bf438e04`;
- the four author intentions, at PR #551's head `3168963b7df262d81354d3fec2cf8ef2ec74cd4b`.

The bridge is the code on this branch, built from main `fa432cc3` plus the change in this PR.

## The sequence and what it showed

`transcript.json` lists all 20 steps with their exit codes, statuses and key fields. The full bridge output is hashed, not copied.

| Step | Command | Result |
|---|---|---|
| 1–4 | `keep-intention` ×4 | The author's four intentions recorded, verbatim. |
| 5 | `resume` | `not_started`: no working architecture yet. |
| 6–7 | `prepare`, `complete-file` (W6) | The baseline is `ready`, with 32 nodes, and it is the working architecture. |
| 8 | `resume` | Confirms the baseline and no pending review. |
| 9–10 | `prepare --instruction`, `complete-file` (Book 24) | A revision is `review_ready`. The review reports 2 nodes, 8 links and 1 emotion target added. The live architecture is still 32 nodes. |
| 11–12 | `show`, `resume` | The review is pending, not applied. `pending_review` names the review's request. |
| 13 | `apply-review --request-sha256 <review>` | `applied`. The live architecture has 34 nodes. |
| 14 | `resume` (new process) | Recovers 34 nodes, `pending_review: null`, and the applied request. |
| 15 | `apply-review` again | `already_applied`. Nothing changed. |
| 16 | `prepare` (a newer request) | A later request supersedes the applied review. |
| 17 | `apply-review` of the older review | Rejected: `a newer architecture request superseded this review`. |
| 18 | `apply-review` of an unknown identifier | Rejected: `no architecture request has this identity in this canvas`. |
| 19 | `apply-review` of a malformed identifier | Rejected: `request_sha256 must be a 64-character lowercase SHA-256`. |
| 20 | `resume` | Shows the newer request awaiting its host agent, and the applied architecture (34 nodes) still in place. |

Step 17 is worth noting. Once a newer request is prepared, the older review is refused, even though it is the candidate that was applied. That is the existing pointer rule, and the bridge keeps it.

## Continuity check

`continuity.json` compares the recovered architecture with W6. It passes all of these:

- the two added nodes are the Book 24 capability record and the crew: `str_b24_capability_mark` and `str_b24_uncounted_crew`;
- the three engines (`eng_ledger`, `eng_source`, `eng_old_hand`) are unchanged;
- the governing-variable node (`th_hands_and_draw`) keeps its summary;
- the three finale alternatives are unchanged and still titled "not chosen";
- the open questions are unchanged;
- every emotion target keeps `agent_proposed` provenance, and none is `author_declared`.

## What the product recovered, exactly

The bridge recovers a **condensed architectural representation** of Book 24: two structure nodes, eight links, one emotion target and a summary sentence. The Book's prose function (its causal chains, its ten provisional assumptions, its alternatives and its missing information) is not in the candidate. It remains in the cold-start output of PR #555. The phase narrative and the open-question list were already at their schema caps, so the Book could not be added to them. The product does not claim more than that, and this record does not either.

## What this is not

- It is not a fresh-context creative qualification. Every step ran in separate processes, but one coordinating agent drove them.
- It does not show that the Book 24 function is good fiction, or that the Series' commitments are better served by it.
- It does not accept any element as canon. The applied material remains working and noncanonical, and the walkthrough checks that no story record was written.

## Reproduce

    python docs/qualification-evidence/studio-architecture-revision-lifecycle-20261112/run_walkthrough.py <repo_root> <scratch_dir>

Requires the PR #555 and PR #551 commits to be present in the repository's object store (fetch them first). It writes `transcript.json` and `continuity.json` to `<scratch_dir>`.
