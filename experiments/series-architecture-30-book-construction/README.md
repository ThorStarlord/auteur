# Construction of the missing long-form architecture: Arc IV and the Book 30 finale (working, noncanonical)

This directory is a bounded creative-construction exercise for *The Spring Ledger*. It builds on the original 30-Book architecture in PR #551 and on the independent challenge in PR #552. It constructs the missing late-Series causal development (Arc IV, Books 19–22), connects it to Book 23 and to the Book 30 finale, offers three finale mechanisms for author choice, applies the consistency corrections the challenge found, and records the hypothetical H1 path as a separate delta.

- **Working and noncanonical.** Nothing here is accepted Identity, Structure, Series or Book canon. No author has approved it.
- **Original experiment untouched.** `experiments/series-architecture-30-book-v1/` (PR #551) and `experiments/series-architecture-30-book-v1-independent-challenge/` (PR #552) are not modified by this branch.
- **No product change.** No source, schema, or test change. Auteur's Studio operations were run in disposable canvases outside the repository.
- **No prose, no Book outlines.** Only the focal Books and the exported Arc IV state are constructed.

## Read in this order

1. [`01-causal-construction.md`](01-causal-construction.md): inherited state at Book 18, Arc IV Conflicts A and B, Book 23, and the Book 30 causal test.
2. [`02-finale-alternatives.md`](02-finale-alternatives.md): three finale mechanisms (A noncoercive, B allotted binding, C ratified trigger), their failure modes and costs, comparison, the agent's nomination for testing, and the author-reserved choices.
3. [`03-working-candidate-v2.json`](03-working-candidate-v2.json): **the final working candidate ("W2")**, schema v2, validated and applied in a disposable canvas. [`03-working-candidate.json`](03-working-candidate.json) ("W1") is the version the reviews read. It stays as evidence.
4. [`04-h1-focused-delta.md`](04-h1-focused-delta.md): the hypothetical H1 path as a focused delta on W2, with the baseline correction (the original premise is evidence and a coalition, not seizure).
5. [`05-consistency-record.md`](05-consistency-record.md): every contradiction found, where it lives, and whether it is corrected, explicit, open, or a product limit. Section E lists the corrections made after review.
6. [`06-validation-and-review.md`](06-validation-and-review.md): mechanical validation, the two fresh-context reviews and the blind host run, the adjudication of every finding, and the limits.
7. [`07-synthesis.md`](07-synthesis.md): answers to the seven questions in the mission.

## Folders

- `review/causal-packet/`, `review/semantic-packet/`: the reviewers' inputs, with manifests that record hashes and withholdings.
- `review/causal-report.md`, `review/semantic-report.md`: the two reviewers' reports, verbatim.
- `evidence/product/`: the Studio review objects for each revision (W1, W2, H1 from W1, H1 from W2), and `run-summary.json`.
- `evidence/blindtest/`: the blind host's raw response, which the product refused structurally.
- `evidence/`: the scripts that reproduce the work (`make_h1_path.py`, `run_canvas.sh`, `apply_review.py`) and the instructions recorded in the Studio canvases (`instruction-construction.txt`, `instruction-review-corrections.txt`, `instruction-h1.txt`, `instruction-blindtest.txt`).

## Provenance

| Item | Value |
|---|---|
| Original experiment | PR #551 head `3168963b7df262d81354d3fec2cf8ef2ec74cd4b`; branch `experiment/series-architecture-30-book` |
| Independent challenge | PR #552 head `ac1fbff80ab77cac0c44adc9c91b9568f6689d42` (stacked on #551); read as evidence, not copied into this branch |
| This branch | `experiment/series-architecture-30-book-construction`, created from `3168963b` in the isolated worktree `H:/GithubRepositories/auteur-30book-construction` |
| Constructor | The coordinating agent (Claude Haiku 5.5) in this session. It wrote the construction, the candidates, the H1 delta, and the adjudication, and acted as the host agent for the Studio canvases. |
| Causal reviewer (R1) | Fresh general-purpose subagent, model Opus, packet `review/causal-packet/` |
| Semantic reviewer (R2) | Fresh general-purpose subagent, model Opus, packet `review/semantic-packet/` |
| Blind host agent (B) | Fresh general-purpose subagent, model Haiku, given only the request file from canvas `blindtest` |

**Order of work.** The construction (01, 02) was written first. W1 (03) was then written and submitted as the host response for the construction request, so its content was authored before the Studio request was prepared. The product checks structure and freshness, not who wrote the content, and this record says so. The reviews read W1 and H1 from W1. Their findings were adjudicated in one round. W2 and H1 from W2 are the corrected versions. They were not re-reviewed by a fresh reviewer.

## Reproduce

The commands run from the worktree root. They use the worktree's `src`, not an editable install, which points elsewhere on this machine. `SRC_551` is PR #551's files, as a checkout at `3168963b`.

```bash
export PYTHONPATH="$PWD/src" PYTHONUTF8=1
EX=experiments/series-architecture-30-book-construction
PROJ=<scratch>/proj                        # a disposable Auteur project outside the repository
SRC_551=<checkout of 3168963b>/experiments/series-architecture-30-book-v1

# 1. Canvas w1: original baseline, construction revision (W1), then the review corrections (W2)
bash $EX/evidence/run_canvas.sh "$PROJ" w1 "$SRC_551/A-studio-candidate-original.json" \
     $EX/evidence/instruction-construction.txt $EX/03-working-candidate.json
python -m auteur.beginner.studio_architecture --project "$PROJ" --canvas w1 \
     prepare --instruction "$(cat $EX/evidence/instruction-review-corrections.txt)"
python -m auteur.beginner.studio_architecture --project "$PROJ" --canvas w1 \
     complete-file --candidate $EX/03-working-candidate-v2.json
python $EX/evidence/apply_review.py "$PROJ" w1 <request_sha256_from_prepare>

# 2. H1 path, derived from W2, applied to canvas h1final (baseline W2)
python $EX/evidence/make_h1_path.py $EX/03-working-candidate-v2.json <scratch>/h1-from-w2.json
bash $EX/evidence/run_canvas.sh "$PROJ" h1final $EX/03-working-candidate-v2.json \
     $EX/evidence/instruction-h1.txt <scratch>/h1-from-w2.json
```

`run_canvas.sh` reads the four author-fixed intentions from PR #551's `evidence/intention-1..4.json`. The revision request's sha256 is printed by `prepare`, and `apply_review.py` takes it as its third argument.

## Claim ceiling

This exercise shows that the Studio candidate can hold a working, validated, freshness-checked Arc IV and finale, that its revisions are reviewable, and that independent reviewers can test some of its causal and semantic claims. It shows the product's gap: its preserved check compares identifiers, and a fresh agent's semantic repair was not reliable in one run. It does not show that Arc IV is good drama, that the three finale mechanisms work on the page, or that any author would accept any of it. See [06](06-validation-and-review.md) §5 and [07](07-synthesis.md).
