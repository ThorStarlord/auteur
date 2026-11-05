# Hybrid Narrative Architecture Revision — Evidence and Decision Ledger

**Date:** 2026-11-05. **Branch:** feat/hybrid-narrative-revision-review-20261105. **Base:** main after PR #513.

## Decision and scope

The author selected hybrid before/after review and explicitly authorized implementation of every task with delegated owner decisions. This author direction is recorded as permission for a **narrow opt-in experimental Studio integration**, not approval to make it the default or claim release readiness without real-author evaluation. The experimental option is separate from the previously unmet author-effectiveness evidence gate.

## Implemented experiment and opt-in functionality

- Source-bound typed diff for `node`, `link`, `emotion_target`, `complex_emotion`, `genre_contract`, `genre_interaction`, `phase` and `summary`, with exact per-side source refs and stable IDs.
- Readable semantic change summary; counts, author-declared emotion warnings, and accepted constraints as **requirements to check**, not verified compliance.
- Separate synchronized graph snapshots using union coordinates and only recorded directed links and genre interactions; accessible typed index for all non-spatial components.
- Focused comparison of selected node/relationship/phase/genre/emotion with full field values, exact before and after records, recorded one-hop neighborhood and Before/After/Differences layer options.
- Isolated recorded initial-candidate fixture with a **synthetic** after candidate and explicit provenance label, plus tests of semantic-only, redirected-link, summary-only and no-op cases.
- Shared browser modules reused by standalone prototype and an opt-in disclosure inside the existing Studio `architecture-review` panel. The opt-in bridge lazily loads modules and invalidates on review or canvas change. No changes to the existing host-agent prepare/complete/apply endpoints, accepted story owners, or persistence schemas.

## Verification performed in this execution

| Gate | Observed result | Evidence ceiling |
| --- | --- | --- |
| Node comparison, layout and view tests | 21 passed | Local new-module mirror; not full Auteur source tree |
| Node promoted comparator/view and lazy bridge tests | 6 passed | Local code and contract tests, including opt-in/load/invalidation |
| Combined Node tests | **27 passed** | `node --test docs/prototypes/hybrid-architecture-revision/*.test.mjs tests/test_studio_architecture_revision_*.mjs` |
| Real Chromium DOM journey | **1 passed** | Scripts injected on `about:blank`; local URL navigation blocked by admin policy |
| Python server/lifecycle test | Syntax compiled; not executed | No full checkout or installed Auteur package |
| Served Studio / end-to-end host-agent interaction | **Not verified** | GitHub is accessible only via connected app; container cannot clone and browser blocks local URL navigation |
| Human author comprehension/creative quality | **Not obtained** | No author study, no effectiveness claim |
| Independent agent result | **Not obtained** | After fixture is explicitly synthetic |

The full repository tests, native browser serving, response-to-review flow and host-agent interactions require a real Auteur checkout. The current browser test is **actual Chromium DOM manipulation**, but is not the current served Studio or a human usability observation.

## Baseline comparison and uncertainty

The existing Studio offers an actual working revision, a textual changed-component review and its current architecture graph. The hybrid adds mechanically inspectable exact typed before/after field values, matched node positions, and a focused local view even when graph topology does not change. The human value of those surfaces remains unmeasured. In particular, the design must not imply that a change in JSON guarantees improved narrative coherence or accepted-constraint compliance.

## Rulings made autonomously

- **Isolated GitHub branch instead of a local worktree:** the container has no repo checkout, DNS cannot resolve github.com, and connected GitHub APIs support scoped file writes. Cost: real full repository tests could not be run.
- **Opt-in experimental integration instead of default activation:** the user delegated owner decisions but no human outcome validates default promotion. Cost: authors must explicitly open the visual review.
- **One shared promoted semantic model:** prototype modules re-export production modules to avoid divergence. Cost: standalone static prototype requires serving the repository root, not the docs folder alone.
- **Chromium inline DOM test rather than served Studio:** administrator policy blocks HTTP/file/data URL navigation in this environment. Cost: server routing and full browser integration remain unqualified.

## Next evidence gates

1. Run the full test commands in the prototype README on the exact PR head in a real checkout, including `tests/test_beginner_studio_architecture_visual_review.py` and actual served Chromium review with pending and applied revisions.
2. Run an author-facing comparison against the current Studio text review with semantic-only edits, redirected links and changed/removed author-declared preferences. Record decision quality, comprehension and misunderstandings, not merely clicks.
3. Keep the experimental option off by default until this evidence or a new explicit owner policy decision warrants promotion. Do not claim release qualification or narrative-quality improvement.

**Disposition:** Preserve isolated research and narrowly opt-in visual review as development functionality. No automatic canon acceptance, partial entity acceptance, model invocation, new ontology class or graph persistence owner.
