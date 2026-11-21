# 04. Provenance and consolidation edits

Status: **working and noncanonical.** Records where every element of this package comes from, what was changed in consolidation and why, and which product operations produced the machine-readable artifacts. The source archive is not copied into this package. It remains available in the pull requests named below.

## 1. Sources and exact identities

| Source | Identity | Use in this package |
|---|---|---|
| Repository baseline | `origin/main` at `fa432cc33646449cd9de0b2fb92af054fa20a9d3`, branch `experiment/series-architecture-consolidated-baseline` | This branch, created from current main in an isolated worktree |
| PR #551 (original architecture) | head `3168963b7df262d81354d3fec2cf8ef2ec74cd4b`, open draft | Author-fixed intentions (`evidence/intention-1..4.json`) and the fixed rows of §1 of `A-original-architecture.md`. Read through `git show`. |
| PR #552 (independent challenge) | head `ac1fbff80ab77cac0c44adc9c91b9568f6689d42`, open draft | Not used as a source for this package. Its findings were used as evidence in PR #553. |
| PR #553 (construction) | head `aaae0eaaddfbfa98ccb6d239fc01cef5ffe3d478`, open draft | Arc IV, Book 23, the Book 30 alternatives and the errata, used as earlier evidence. The errata (`corrections/errata.md` in PR #554) are reflected in `01-series-architecture.md`. |
| PR #554 (verification) | head `d6dd636d62e23c0138ae0a561bf329332852124c`, open draft | **The W5 candidate, the source of this package's machine-readable artifact.** Also the frozen crisis and the traces, which this package does not carry. |

Every identity above was checked against the remote on the day of this work. The PR #554 head is the one the mission names.

## 2. The machine-readable artifact

`02-working-candidate-W6.json` is W5 with the consolidation edits in §3 applied. It is produced by `evidence/make_consolidated_candidate.py`, which reads W5 from the PR #554 head with `git show`, asserts the exact text it replaces, and writes W6.

| Artifact | SHA-256 |
|---|---|
| W5 (PR #554 head, `corrections/05-working-candidate-v5.json`) | `7336983a79797b192f851c07315f5509d1a7c73247488987f54f998358a0783e` |
| W6 (this package, `02-working-candidate-W6.json`) | `46590a783c88ea7c18848d68966b997503b66497ce522d87d32ffddc838d4c48` |
| Intentions (`03-author-intentions.md`) | `2ef936f9098c9ad43d93ffc819e0d04b77cc53170b10e74af76566b6de67d99c` |
| Architecture (`01-series-architecture.md`) | `2cf51ae67a3bb92e16007497da4a8722787c2d58d80466f8b459da4d14da9bfb` |

**Validation.** W5 and W6 both validate against `ArchitectureCandidate` (schema version 2) on current main. W6 has 32 nodes, 34 links, 5 phases, 7 emotion targets and 16 open questions. The summary is 1,217 characters, under the 3,000 limit.

## 3. Consolidation edits (W5 to W6)

These are the only changes. Each is a label or a merge. None adds, removes or reinterprets an architectural element.

1. **Summary.** The W5 summary, which described W5 as a working construction and named "the agent-proposed working direction for testing", is replaced with a status summary. It states the candidate's status, its relation to PR #554, the author-fixed intentions and their location, the agent-proposed additions, the finale alternatives as not chosen, the undecided items, and the Harrow Lowe gate as recorded separately. It states no preference between the finale alternatives.
2. **Alternative C's title.** "Finale Alternative C (not chosen; working direction for testing)" becomes "Finale Alternative C (not chosen)". This removes the only place where the candidate expressed a preference. The mission says C's apparent advantage in the frozen experiment must not be carried forward as a preference.
3. **Open questions, merged to free two slots.**
   - W5 items 4 (Special Draw Right) and 11 (who carries the Turn when lineages end) are merged into one item, so that both questions survive.
   - W5 items 7 (which channel takes the surge) and 13 (whether the flood is survived without losses) are merged into one item.
   - W5 item 8 (whether a threshold exists) gains the question of who ratifies it.
   - Two items are added, which the mission names as author reservations that W5 never listed: whether the Hollow Gate and the Gate Table are accepted parts of the world, and what the high cistern can physically store.
   The list stays at the schema's cap of 16.

The W5 summary still said that the Hollow Gate and the Gate Table were not decided. W6 keeps that statement and moves it into the open questions as well.

## 4. What is not in the candidate, and where it is

- **H1 (the counterfactual in which the Hall's own head opens the records).** It is a separate hypothetical path. Its candidate is `11-h1v4-from-w5.json` in PR #554. It is not in this package, and this package does not merge it.
- **The Harrow Lowe lower gate.** The original places the Mill Compact at it. It is recorded as a provisional concept in the working canvas (see `evidence/concepts/03-harrow-lowe-gate.json`), and it is not a node in the candidate. The candidate therefore cannot represent the lowland overflow path until someone adds it.
- **The high cistern's storage.** Not in the candidate and not in any canon. The experiment used illustrative values. They are not established, and this package does not carry them.
- **The crisis and the traces.** PR #554 holds them. They are experimental results, not canon, and this package does not carry them.

## 5. Provisional concepts recorded in the canvas

Five provisional concepts are recorded in the working canvas through `record-concept`. Each has `status: provisional`. They are agent-proposed and reversible. The fields and their sources are in `evidence/concepts/`:

1. Hollow Gate.
2. Gate Table.
3. Harrow Lowe lower gate.
4. Compact grain-labour contribution.
5. Book 15 surfeit mechanism.

## 6. Product operations used

The canvas was built with the existing Studio bridge (`python -m auteur.beginner.studio_architecture`) on current main, through `evidence/build_canvas.py`:

- `CanvasStore.create` and one `create-item` for the story vision, which is the author's identity text plus the four intentions verbatim.
- `keep-intention` four times, one for each author directive from PR #551.
- `prepare` and `complete-file`, with W6 as the baseline. The product accepted it as the current proposal (`architecture_status: ready`).
- `record-concept` five times.
- `show`, `resume` and `intentions`, to capture what a fresh agent receives.

Nothing in the repository's source, schema or tests was changed.

## 7. Authority labels

- Author-fixed material is the identity text and the four intentions, which are in `03-author-intentions.md`, unchanged from PR #551.
- The emotion targets in W6 are `agent_proposed`, as in W5. The product records no other provenance on nodes.
- The concepts in §5 are `provisional`. They are not `author_declared`.
- The consolidation edits in §3 were made by the coordinating agent. They are labels and merges, and they are recorded here.
