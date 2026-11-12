# Stage A packet manifest

Frozen before the reviewer started. Verify with `sha256sum stage-a/packet/*`.

## Source identity

- Experiment: PR #551 (`experiment: 30-Book Series architecture exercise (working, noncanonical)`), branch `experiment/series-architecture-30-book`, head `3168963b7df262d81354d3fec2cf8ef2ec74cd4b`.
- Source blobs at that head:
  - `experiments/series-architecture-30-book-v1/A-original-architecture.md` — blob `dd84d1eb56f5309288ac9f2a345310bb06982bee`, sha256 `368de05cd99c4d2e432960a242b73722bb6ce86c066d84e766a95ba458ebc65e`
  - `experiments/series-architecture-30-book-v1/A-studio-candidate-original.json` — blob `31b8ede7557504bbaeba544626c9217e3540da44`, sha256 `a78ce7d5bd4f6ffc3d8507e7bd84a23c07c8f0cac98341775aa6456e0af53bbf`
- Fixed author brief: no separate verbatim brief file exists in the repository. The packet represents it with the `[Fixed]` row of `A-original-architecture.md` §1 and the four author-fixed intention records `evidence/intention-1.json` to `evidence/intention-4.json`.

## Packet files

| Packet file | sha256 | Source | Treatment |
|---|---|---|---|
| `00-reviewer-instructions.md` | `b4fd20d69ad71aed281bee539b2b914cbe9f58252e1d47cac56ef2b5616e7537` | Written by the coordinator for this review | Mandate, dimensions, required judgments, report format (verbatim from the mission §4.2–4.4, plus scope limits) |
| `01-fixed-author-brief.md` | `2c71f98363069afac632831a3e4079b34fc86e3a730b83a9449b2c68e5a72c5f` | `[Fixed]` row of A §1 + intention-1…4 directives | Assembled verbatim from source text |
| `02-original-architecture.md` | `d233c6de7eab3b6bd038a2e56031dd77ba37709bb1b13e217d07271114fd4034` | `A-original-architecture.md` | Edited (see withholdings) |
| `03-original-studio-candidate.json` | `254b85808ece1d0da018ebca01acbb8b75b3ceda10b6057db309c118b57198f8` | `A-studio-candidate-original.json` | Edited (one clause) |

## Withholdings (exact)

Included in full: A §1–§7 (identity, world and characters, engines, macro arcs, Book functions for 1/6/15/23/30, promise ledger, planning posture), and all of the candidate JSON except the one clause below.

Withheld from `02-original-architecture.md`:
1. **§8 "Where the design is thin (admitted)"** — the entire section. Classified as retrospective self-assessment, per the mission's rule to separate primary design claims from retrospective commentary.
2. **One sentence in §4**, "Arc IV is deliberately the thinnest. It is the place where filler is most likely (see §8)." — retrospective commentary.
3. **Two cross-reference links** to withheld files (`01-concept-comparison.md` in the header, and `D-product-capability-observations.md` in §1). The surrounding text was kept; the link text was replaced by `[WITHHELD reference]`.

Withheld from `03-original-studio-candidate.json`:
4. In the `ph_4_settled_water` phase, `narrative_function`, the clause "and it is the most likely place for filler." — retrospective commentary. The preceding design rule, "This arc is deliberately lighter; its conflicts must come from settled practice," was kept as a primary design statement. The JSON still validates.

The reviewer was told that bracketed `[WITHHELD ...]` markers mark removed passages and not to speculate about them.

## Known exposure and limits

- **Coordinator exposure.** The coordinator wrote the original architecture and its evaluation in an earlier session. It has read `E-synthesis-and-evaluation.md` and the original verdict. The coordinator therefore cannot be treated as blind to the designer's conclusions. The selection of withholdings above was made by the coordinator and is a documented judgment, not a neutral process.
- **Reviewer context.** The reviewer was launched as a fresh general-purpose subagent with the model set to `opus`. Its only task prompt is the one-line pointer to `00-reviewer-instructions.md`. The reviewer's launch environment may include generic repository and user guidance, which does not mention this experiment. The reviewer's own section 0 records what it actually opened.
- **Visible evaluative text.** Residual evaluative wording that the packet still contains, disclosed rather than hidden: the candidate phase `ph_4_settled_water` still says the arc "is deliberately lighter; its conflicts must come from settled practice" (kept as a design rule); the candidate's `open_questions` are the designer's own open questions and were kept; A §7 says the posture is "recommended in the strategy document" (kept as a planning statement).
- **Not included at Stage A (by design):** `C-revision-delta.md`, `C-studio-candidate-revised.json`, `04-renewal-test.md`, `05-local-global-judgment.md`, `01-concept-comparison.md`, `D-product-capability-observations.md`, `E-synthesis-and-evaluation.md`, and the `evidence/` directory.
