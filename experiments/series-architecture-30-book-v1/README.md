# Experiment — Series architecture for a 30-Book fantasy Series (v1)

This is one bounded creative-construction exercise. It builds and stress-tests a
working 30-Book Series architecture (*The Spring Ledger*) using Auteur's Studio
architecture candidate, revision, review and validation operations. It is **not**
a product change, a canonical story, or an ontology decision.

## Status and authority

- **Working / noncanonical.** Nothing here is accepted Identity, Structure, Series or Book canon.
- **Not author-approved.** The author brief is recorded as fixed input and as Studio intentions; the architecture itself is a proposal.
- **Hypothetical:** only the counterfactual H1 in `C-revision-delta.md`.
- **Independent review:** none. Every judgment is by the agent that designed the architecture (Claude Haiku 5.5). See `E-synthesis-and-evaluation.md`.
- No source, schema, test or canonical project file was changed. The scratch Studio canvas lived outside the repository.

## Read in this order

1. `01-concept-comparison.md` — **B.** Two whole-Series concepts, compared on causal organization, and the synthesis selected.
2. `A-original-architecture.md` — **A.** The original working 30-Book architecture: identity, engines, five macro arcs, Books 1, 6, 15, 23 and 30, promise ledger, admitted thinness.
3. `A-studio-candidate-original.json` — the product-validated form of A (schema v2).
4. `04-renewal-test.md` — renewal test on the Stone Hall monopoly.
5. `05-local-global-judgment.md` — which level owns the Old Hand weakness, and why.
6. `C-revision-delta.md` — **C.** One counterfactual (H1), affected dependencies, preserved invariants, two-plus repair alternatives, and the focused delta.
7. `C-studio-candidate-revised.json` — the revised working candidate (hypothetical).
8. `D-product-capability-observations.md` — **D.** Which Auteur operations ran, what they supported, where freeform reasoning was needed, observed defects.
9. `E-synthesis-and-evaluation.md` — **E.** Feasibility, per-dimension evaluation, strongest weakness, strongest counterargument, next warranted responsibility.

## Evidence

`evidence/` holds the raw outputs of each product command (`01`–`17`), the four
intention records, the revision instruction, the script that produced the revised
candidate (`make_revised_candidate.py`), and the scratch-canvas creation script
(`create_store.py`). Sparse series probes are kept as rejected evidence
(`15`, `15b`, `16`). A thirty-plan placeholder probe was run and not kept.

## Reproduce (from the worktree root; use the worktree `src`, not an editable install)

```bash
export PYTHONPATH="$PWD/src" PYTHONUTF8=1
python experiments/series-architecture-30-book-v1/evidence/create_store.py <scratch>/project spring-ledger-30
python -m auteur.beginner.studio_architecture --project <scratch>/project --canvas spring-ledger-30 prepare
python -m auteur.beginner.studio_architecture --project <scratch>/project --canvas spring-ledger-30 complete-file --candidate experiments/series-architecture-30-book-v1/A-studio-candidate-original.json
```

## Claim ceiling

This exercise shows that the Studio candidate can hold a working, freshness-checked,
reviewable abstract architecture, and that a 30-Book accepted series contract cannot
be expressed without placeholders. It does not show that the architecture is good
fiction, that its arcs hold beyond Book 19, or that any agent can reliably reconstruct
it from the resume packet. See `E-synthesis-and-evaluation.md` §5.
