# Creative Author Experience — implementation and evidence boundary (2026-11-06)

**Status:** Development candidate on `feat/author-intention-experience-20261106`, **NOT L1/L2 verified, NOT merged, NOT human-qualified**.
**Baseline:** `main` PR #519, merge `d0ead25f361a071274ea8456c5947b6da902cede`.
**Scope:** Five planned responsibilities consolidated in one dependent, reversible development branch for review. No new persistence owner, provider, canonical story state or default promotion.

## 1. Product question

Can an author keep an active narrative intention, challenge it without silently overriding it, apply an explicitly chosen revision, and carry the same artistic direction into Realization and a fresh agent context?

PR #519 established bounded continuity and typed Realization anchors, but Realization did not receive a dedicated continuing-intention projection. The browser lacked intention management and a pending-review critique entry point. Several source-integrity boundaries were identified in a follow-on review.

## 2. Implemented development candidates

| Concern | Proposed solution | Owner |
|---|---|---|
| Claimed alternative provenance | CLI checks that the referenced completed inquiry and exact hypothesis exist on this canvas; independent manual intentions remain valid | `studio_architecture.py` |
| Disclosure budget | Bounded, priority-ordered agent intention view with explicit omitted count; complete records remain in resume | `studio_architecture.py`, `studio_mentor.py` |
| Mentor attribution | Citable, disclosed intention references join the existing source allowlist | `studio_mentor.py` |
| Current intention authority | Prompts distinguish binding active guidance, nonbinding provisional possibilities and nonbinding historical states | Architecture, Mentor, Realization |
| Realization continuity | Optional versioned source context for active/provisional intentions. New requests carry guidance; older source snapshots do not acquire it retroactively | `studio_realization.py` |
| Request freshness | Changed current guidance invalidates an in-flight Realization response; existing architecture remains applied | `studio_realization.py` |
| Creative anchor coverage | Read-only cited/uncited projection; citation alone is explicitly not literary evidence | `studio_realization.py` |
| Stale UI response race | Exact canvas/baseline/generation checks and retry on failed inquiry refresh | `browser/studio.js` |
| Intention management | Working Studio panel supports create, activate, make provisional, withdraw and explicit successor replacement | Studio HTML/JS |
| Supersession integrity | Atomic CanvasStore snapshot replaces old active note and creates a new active successor linked by `supersedes-intention`; validator rejects absent endpoints, competing successors, non-superseded predecessors and cycles | `studio_store.py` |
| Pending revision critique | Existing read-only pending-review inquiry reachable from hybrid review with prepared packet and signed-response fallback | Studio HTML/JS |
| Realization from semantic focus | Selected graph relationship/emotion/component can prepare typed Realization anchors; handoff appears in Realization workspace | Creative panel / Studio |

### Authority boundaries

- A canvas intention is **noncanonical author-directed working guidance**; it is never Story Identity or accepted Realization.
- **Active** is a working commitment: preserve it or explicitly expose a creative conflict for the author's decision.
- **Provisional** is a possibility; treat it as exploratory, not mandatory.
- **Superseded / withdrawn** remain historical evidence; do not resurrect them as current directions.
- The author must explicitly initiate a successor relationship. No automatic acceptance or auto-supersession exists.
- A pending-review critique is read-only. It does not apply or revise the working candidate.
- Validation of an anchor citation is not verification that a literary effect was achieved.

### Known limitations

1. Human author usefulness and literary improvement remain unmeasured. The independent PR #519 critic previously judged one Explore set **PARTLY-RENAMED**; this work does not establish that reasoning problem is solved.
2. New intentional guidance is prioritized by status and recorded focus, not inferred semantic relevance. Omission metadata distinguishes unseen notes.
3. `keep-intention` validates the reported **inquiry hypothesis** when explicitly attributing origin; it does not claim that every retained hypothesis had previously been applied as an architecture revision.
4. The user-facing successor graph uses a reserved canvas relationship label, not a new metadata store. Existing canon acceptance remains separate.
5. Realization's anchor coverage is structural only. Human narrative judgment remains necessary.
6. The Studio still uses explicit host-agent packet handoff and response validation, not an automatic provider call.
7. The Studio intention UI uses the existing atomic `replace-working-document` command. On write failure the existing canvas recovery/export behavior remains authoritative; there is no silent rebase across unrelated edits.
8. There is no participant study, release qualification or default promotion.

## 3. Verification to run against the exact frozen source commit

**Current verification state:** source and tests committed via GitHub connector; no full local checkout available to run package tests. The local container's `git ls-remote` failed due DNS resolution for github.com. All commands below are **planned, not executed**.

### L1 — focused

```bash
python -m pytest -q -o addopts="" tests/test_studio_intention_followthrough.py tests/test_beginner_studio_creative_intentions.py tests/test_beginner_studio_realization_anchors.py tests/test_studio_mentor_agent.py tests/test_studio_mentor_disclosure.py
node --test tests/test_studio_architecture_creative_deliberation.mjs
python -m ruff check src/auteur/beginner/studio_architecture.py src/auteur/beginner/studio_mentor.py src/auteur/beginner/studio_realization.py src/auteur/beginner/studio_store.py tests/test_studio_intention_followthrough.py tests/test_studio_author_experience_browser.py
node --check src/auteur/beginner/browser/studio.js
node --check src/auteur/beginner/browser/studio_architecture_creative_panel.js
```

**L1 policy:** The touched compact pre-existing Python modules may already have E701/E702 baseline findings; distinguish existing findings from additions rather than treating an unchanged baseline as a new regression.

### L2 — boundary-specific

```bash
python -m pytest -q -o addopts="" tests/test_studio_author_experience_browser.py tests/test_beginner_studio_architecture_interactive_browser.py tests/test_beginner_studio_inquiry_pending_review.py
```

Then run the established Studio/Beginner Python and Node suites if the targeted browser/CanvasStore/host-agent boundaries warrant further confidence.

### Behavioral assertions

- An invalid inquiry/hypothesis provenance cannot be created through the official CLI.
- Agent guidance discloses bounded current intentions; resume preserves all historical records.
- An active intention affects a new Realization packet; a withdrawn one does not.
- Changing current intention guidance invalidates an in-flight dependent Realization request.
- Realization projection reports an uncited selected anchor without pretending it was used.
- The Studio saves a successor plus predecessor status **atomically** and recovers the typed successor in resume.
- Out-of-order inquiry responses cannot restore obsolete selectable alternatives.
- Pending-review critique remains read-only and cannot apply a proposed architecture.
- A graph-selected emotion or relationship reaches the Realization handoff.
- Old node-only Realization callers and old source snapshots remain compatible.

Any failing tests require finding-specific repairs before integration. No check is counted as a pass without an actual execution receipt.

## 4. Product qualification

Follow `docs/qualification-evidence/author-intention-experience-20261106/human-walkthrough-protocol.md` when 2–3 willing participants and an executable Studio environment are available.

Never convert simulated authors, coordinator-authored answers or served-Chromium fixtures into human evidence. A smaller authentic exercise may be used for reversible development learning but cannot justify default promotion.

## 5. Continuation / merge boundary

Repository policy in `docs/engineering/release-qualification.md` requires appropriate exact-head L1 evidence for code-bearing merges. The current branch has **no executed L1/L2**, so a source merge would not satisfy the ordinary policy. The user has authorized implementation and autonomous continuation, not falsification of verification.

Next owner-independent action when a checkout/runtime becomes available: run the focused commands above, repair any failures, record exact SHA and observed test counts, review the diff, and only then merge the applicable PRs. No product-thesis change or release authorization is requested.
