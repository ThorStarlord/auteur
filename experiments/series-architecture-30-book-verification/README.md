# Verify and stress-test the final 30-Book architecture (working, noncanonical)

This directory is a bounded verification and stress-test of the construction in PR #553: the Arc IV conflicts, Book 23, the three Book 30 finale alternatives, and the H1 counterfactual. It asks one question: can the architecture's established mechanisms make three materially different responses to the same Book 30 crisis causally possible, while keeping the Series identity, its earlier history, and the author's open choices?

- **Working and noncanonical.** Nothing here is accepted Identity, Structure, Series or Book canon. No author has approved any alternative.
- **The construction is unchanged.** PR #551, PR #552, PR #553 and their files are not modified. Corrections are new files in this folder, and each round is kept beside the one before it.
- **No product change.** No source, schema or test was changed. Schema validation and the product's review builder were used, and the scripts are in `evidence/`.
- **No prose, no Book outlines, no Books 24 or 25.** The crisis is one bounded situation. The traces are consequence traces, not scenes.

## Read in this order

1. [`00-freeze-and-provenance.md`](00-freeze-and-provenance.md): the starting state, the artifact hashes, the reviewers and their exposure, the freeze point, and the corrections to earlier claims.
2. [`03-shared-crisis.md`](03-shared-crisis.md): the frozen Book 30 crisis. Every invented number is labelled INV.
3. [`04-consequence-traces.md`](04-consequence-traces.md): Alternatives A, B and C traced through the same crisis, with arithmetic checked by [`evidence/recompute_traces.py`](evidence/recompute_traces.py).
4. [`05-comparative-assessment.md`](05-comparative-assessment.md): what differs between the alternatives, what fails, and which assumptions the traces rely on.
5. [`06-adjudication.md`](06-adjudication.md): every Stage A and Stage B finding, classified and decided, with the verification history (§ F) and the residual open items.
6. [`07-product-capability-synthesis.md`](07-product-capability-synthesis.md): the answers to the mission's eight questions, and what Auteur's operations did and did not support.

The reviews and their packets are in `review/`, and the correction rounds are in `corrections/`.

## Folders

- `review/`: the verbatim reports and their packets.
  - `stage-a-report.md`, `stage-a-packet/`, `stage-a-manifest.json`: the review of the final W2 candidate.
  - `stage-b-report.md`, `stage-b-packet/`, `stage-b-manifest.json`: the review of H1-from-W2.
  - `stage-f-report.md`, `stage-f-packet/`: the verification of round 1 corrections.
  - `stage-f2-report.md`, `stage-f2-packet/`: the verification of round 2 corrections.
  - `stage-f3-report.md`, `stage-f3-packet/`: the verification of round 3 corrections.
  - `quote-check-stage-a.txt`, `quote-check-stage-b.txt`: a mechanical check of every quotation in the Stage A and B reports against its packet.
  - `templates/`: the reviewer instructions and packet templates.
- `corrections/`: each correction round, kept as it was verified.
  - `w3-changes.md`, `round-2-changes.md`, `round-3-changes.md`: the candidate and H1 changes, before and after, with the defect each removes.
  - `errata.md`: the prose errata for the PR #553 files, which are not rewritten.
  - `03-working-candidate-v3.json`, `04-working-candidate-v4.json`, `05-working-candidate-v5.json`: the corrected candidates, W3 to W5.
  - `09-h1v2-from-w3.json`, `10-h1v3-from-w4.json`, `11-h1v4-from-w5.json`: the corrected H1 paths.
  - `review-*.json`: the product's review objects for each change.
- `evidence/`: the scripts and their outputs.
  - `make_stage_packet.py`, `make_stage_b_packet.py`: build the Stage A and B packets from committed sources.
  - `make_w3_and_h1v2.py`, `make_round2.py`, `make_round3.py`: derive each correction round.
  - `recompute_traces.py`, `recompute-output.txt`: recompute the traces' arithmetic.
  - `check_quotes.py`: the quotation check.

## Provenance

| Item | Value |
|---|---|
| Base | PR #553, head `aaae0eaaddfbfa98ccb6d239fc01cef5ffe3d478`, branch `experiment/series-architecture-30-book-construction` |
| Original | PR #551, head `3168963b7df262d81354d3fec2cf8ef2ec74cd4b`, branch `experiment/series-architecture-30-book` |
| Challenge | PR #552, head `ac1fbff80ab77cac0c44adc9c91b9568f6689d42`, branch `experiment/series-architecture-30-book-independent-challenge` |
| This branch | `experiment/series-architecture-30-book-verification`, created from `aaae0eaa` in the isolated worktree `H:/GithubRepositories/auteur-30book-verification` |
| Author of this work | The coordinating agent (Claude Haiku 5.5). It built the crisis, the traces, the comparison and every correction. |
| Reviewers | Fresh general-purpose subagents, model Opus, one invocation per check. Five reviews in all: Stage A, Stage B, and one finding-specific verification of each correction round (F, F2, F3). |

## Reproduce

Run from the worktree root, using its own `src` and not an editable install.

```bash
export PYTHONPATH="$PWD/src" PYTHONUTF8=1
V=experiments/series-architecture-30-book-verification
SCRATCH=<a disposable directory outside the repository>

# The frozen Stage A and Stage B packets, built from committed sources.
python $V/evidence/make_stage_packet.py "$PWD" "$SCRATCH/stageA" aaae0eaaddfbfa98ccb6d239fc01cef5ffe3d478 $V/review/stage-a-manifest.json
python $V/evidence/make_stage_b_packet.py "$PWD" "$SCRATCH/stageB" aaae0eaaddfbfa98ccb6d239fc01cef5ffe3d478 $V/review/stage-b-manifest.json

# The correction rounds, each derived from the one before.
python $V/evidence/make_w3_and_h1v2.py "$PWD" $V/corrections
python $V/evidence/make_round2.py "$PWD" $V/corrections
python $V/evidence/make_round3.py "$PWD" $V/corrections

# The traces' arithmetic, and the quotation check.
python $V/evidence/recompute_traces.py
python $V/evidence/check_quotes.py $V/review/stage-a-report.md $V/review/stage-a-packet
```

## Claim ceiling

This exercise shows three things. First, the final architecture can produce three materially different responses to one frozen crisis, and the differences are in who bears the cost and who decides, more than in the water. Second, the architecture's failures under pressure are identified and located: a flood on the orchard in A, an unbounded surfeit trade in B and C, and a ratification the architecture does not yet name. Third, the defects of meaning in the final candidate were found by reading, and the product's checks did not find them.

It does not show that any alternative is good fiction, that the crisis reads well on the page, that any reader would accept it, or that any author would choose any alternative. It does not establish the high cistern's storage, the Harrow Lowe gate, or the ratifying assembly, and it says so where it depends on them. The numbers in the crisis are invented and labelled. The reviews are fresh readings by the same model family as earlier reviews, not by different authors.

## Residual open items

Three correction rounds were verified. The stopping rule then applied, and the residual items are recorded in [06](06-adjudication.md) § F. They are minor: a stale heading in Alternative A, two wrong locators in an erratum, one wording description in the round-3 record, and the open author decisions listed in [07](07-product-capability-synthesis.md) § 8.
