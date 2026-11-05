# Hybrid Narrative Architecture Revision Review — prototype and opt-in Studio integration

**Status:** Experimental working-architecture review; not the default Studio review and not release-qualified.

## What it does

Given two existing `ArchitectureCandidate v2` JSON snapshots and their distinct request identities, the shared deterministic comparator exposes typed `node`, `link`, `emotion_target`, `complex_emotion`, `genre_contract`, `genre_interaction`, `phase` and `summary` differences. A genre contract uses its real `genre_node_id`. Each side carries exact array positions, not guessed paths.

The UI shows:

1. **Readable summary:** actual added/removed/changed/unchanged counts, author-declared emotion-change warnings, and constraints as unverified requirements (never guaranteed compliance).
2. **Before/After graphs:** two separately labeled candidate graphs with a common stable union layout, scoped internal scrolling and a linear relationship/change index.
3. **Focused overlay:** one-hop recorded neighborhood for a selected graph entity/relationship, explicit Before/After/Differences layers, and complete before/after field values for any typed component—including non-spatial emotions, contracts and phases.

All inspection is read-only. No graph geometry supplies evidence of narrative causality. No model is called and no accepted story commitment is changed by this feature.

## Recorded fixture versus synthetic changes

`fixtures.mjs` loads the **recorded** initial candidate and exact source request from `docs/qualification-evidence/agent-first-ontology-20261103/`. It generates visibly **synthetic** after candidates for holistic, semantic-only, redirected-link, summary-only, and no-op cases. The synthetic SHA is **not** a real agent request. These examples are not evidence of author creativity or external agent execution.

## Run the standalone prototype

From the repository root:

```bash
python -m http.server 8765
```

Open `http://127.0.0.1:8765/docs/prototypes/hybrid-architecture-revision/` in a browser. Unlike the production Beginner Workspace Server, this local static server exposes the repository paths needed to load the recorded fixtures.

## Opt-in Studio review

Inside a real `review_ready` working-architecture revision, the existing revision review now has a collapsed **Compare visually (experimental · working architecture only)** disclosure. Opening it imports the shared read-only comparison modules. Before is `projection.candidate` with `candidate_request_sha256`; After is `projection.review.candidate` with `review.request_sha256`. The review's `prior_request_sha256` must match the current candidate request SHA.

Closing or switching canvases invalidates the comparison. **Apply to working architecture** remains the existing separately triggered, backend-validated, whole-revision operation; no acceptance or partial-apply action was added.

The production modules are `src/auteur/beginner/browser/studio_architecture_revision_compare.mjs`, `studio_architecture_revision_view.mjs`, `studio_architecture_revision_bridge.js`, and a style sheet scoped under `#architecture-visual-review-root`. The prototype re-exports the same modules rather than maintaining a divergent semantic implementation.

## Verification and evidence limits

In the implementing environment, the repository was accessible through the connected GitHub tools but not as a local clone; the container cannot resolve `github.com`. A local mirror of the new JS modules and a minimal comparison fixture produced **26 passing Node tests** and **one passing real Chromium inline-DOM interaction test**. Chromium navigation to localhost and file/data URLs is blocked in that environment. That browser test is therefore **not** proof that the live Studio server, asset routing or host-agent lifecycle has passed.

The repository also contains `tests/test_beginner_studio_architecture_visual_review.py`, intended to validate the real server, stored baseline/proposal, and apply boundaries in a full local checkout. It was syntax-checked but could not be executed against the complete Auteur Python package here. Nor was a human-author study performed.

Run in an actual Auteur checkout:

```bash
node --test docs/prototypes/hybrid-architecture-revision/*.test.mjs tests/test_studio_architecture_revision_*.mjs
python -m pytest tests/test_hybrid_architecture_revision_browser.py tests/test_beginner_studio_architecture_visual_review.py tests/test_beginner_studio_architecture_review.py -q
```

The existing Studio's text review remains the default and fallback. Do **not** claim production qualification or author-effectiveness gains from the isolated tests. See `docs/research/2026-11-05-hybrid-architecture-revision-evaluation.md`.
