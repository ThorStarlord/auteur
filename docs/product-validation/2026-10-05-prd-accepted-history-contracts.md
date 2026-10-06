# Unified Author Experience: accepted-history correctness slice

## Scope and authority

This implements a bounded part of the owner-supplied Unified Author Experience
PRD: truthful kept-prose/history projections, exact acceptance retry binding,
and review-evidence freshness. It repairs existing contracts, not the new
F2/X3 frontier. It does not activate #318 or waive the #310/#313 evidence gate.
No provider calls, new dependencies, canonical-story writes from projections,
workflow changes, protected-file changes, merges, or releases are included.

Base: PR #321, `716ecd8a3282293c0ebdca40f2eed2d501232fd6`.
Branch: `fix/prd-accepted-history-contracts`.
The separate draft PR #322 targets Book re-entry. Its six changed files do not
overlap this three-file patch; this branch does not incorporate or qualify it.

## Implemented behavior

- A kept `final.md` remains readable when no working draft file is retained.
  It is not relabeled as a new candidate and does not need another keep action.
- Chapter-outcome references use the actual kept file, including unpadded paths.
- Prior-Chapter references are ordered numerically, include real files only,
  exclude current/future/working-only Chapters, and use the existing padded-path
  owner precedence once per Chapter. Unaddressable aliases are excluded.
- Both started and completed acceptance receipts stay bound to the original
  draft filename and SHA-256. Reusing a command for changed bytes or a new
  version fails before rewriting receipts or invoking the acceptance owner.
- Completed receipts cannot report a missing/replaced accepted file as current.
  Same-draft replay and recovery after owner completion still work. A fresh
  explicit keep decision can accept a revised draft.
- Malformed review JSON, non-object metadata, and invalid declared draft hashes
  suppress unverified findings and explain the metadata problem. Legacy reviews
  without hash metadata retain their existing behavior.

This does not add cross-process locking or claim transactional ownership of the
external acceptance service. The existing service still owns canonical writes.
The full `realized_state` projection is unchanged; this is not relevance filtering.

## PRD traceability and remaining work

| Requirement | Disposition in this slice |
| --- | --- |
| MENTAL-01 | Existing UI unchanged; beginner comprehension not assessed. |
| MENTAL-02 | Working/Kept distinction preserved in final-only review. |
| AUTH-01 | Retry consent cannot silently transfer to another draft. |
| AUTH-02 | Kept prose/reference truthfulness reinforced; history not rewritten by projections. |
| CREATIVE-01 | Quick Draft entry unchanged; not requalified here. |
| CREATIVE-02 | Existing creative-divergence regression tests retained and passing. |
| DISCOVERY-01 | Discovery heuristic unchanged; consequence-only completeness not claimed. |
| DISCOVERY-02 | No new confirmation on final-only review; general no-op discovery unchanged. |
| PROP-01 | Existing noncanonical proposal-owner routing tests retained and passing. |
| PROP-02 | No new pending-update gate; full continuation not requalified. |
| CONT-01 | Ordered, addressable prior kept-Chapter evidence reinforced. |
| CONT-02 | Continuation precedence composer unchanged; not requalified. |
| CONT-03 | Relevance-aware context remains outside this slice. |
| X3-01 | Only kept-prose visibility repaired; complete orientation/browser work remains. |
| X3-02 | Technical-detail UI unchanged. |
| PROG-01 | Interface-depth routing unchanged. |
| PROG-02 | Interface-depth navigation unchanged. |
| DEEP-01 | Invalid review evidence gets an explanation; general recommendation explanations remain. |

## Verification actually performed

Direct cloning failed because this container could not resolve `github.com`.
Three original files were fetched through GitHub and reconstructed locally;
Git blob hashes matched exactly before modification:

| Original file | Verified Git blob |
| --- | --- |
| `src/auteur/beginner/post_draft.py` | `12fbcc3707eb0dcd00d9c3f9d210ca82e36892af` |
| `src/auteur/beginner/creative_divergence.py` | `6556cee8b55e60c48f4dd4a449e3b716783c8287` |
| `tests/test_beginner_post_draft.py` | `695bdd4f34bc1014087f7b275516b3076339f163` |

The source snapshot uses namespace-package directories, not replacement
production modules or LLM stubs. Tests use real temporary story files and the
existing injectable acceptance-owner seam. They do not execute the owning CLI.

Environment: Python 3.13.5, pytest 9.0.2, PyYAML 6.0.3.

1. Unchanged existing tests on baseline: **12 passed**.
2. Initial new regressions on baseline: **18 failed, 1 passed** (expected RED).
3. Candidate, including two additional compatibility controls: **33 passed**
   (12 unchanged existing tests + 21 new cases); 0 failed/errors/skips/xfails.
4. Python source compilation and `git diff --check`: **PASS**.

Focused command:

```bash
PYTHONPATH=src python -m pytest tests/test_beginner_post_draft.py tests/test_beginner_prd_history_contracts.py -q
```

These are module-level results in the scoped source snapshot, NOT a full-repo
or installed-package run. Full repository validators, Ruff, HTTP/browser tests,
provider quality, human preference, F2/X3 qualification, and release gates were
not run. Review was author self-review; no independent reviewer was available.
Keep the PR draft pending exact-head verification in a complete Auteur checkout.
No existing test was weakened, removed, or changed.
