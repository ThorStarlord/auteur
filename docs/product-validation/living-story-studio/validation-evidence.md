# Living Story Studio — Validation Evidence and Open Gates

**As-of:** 2026-10-10
**Review target:** \`bd2ba539d2f300941681fa7c7b80ab4765354b79\` (GitHub branch source inspected, no merge)
**Status:** partial source/logic observations; **EXECUTION_ENVIRONMENT_UNAVAILABLE** for full running Auteur and human evaluation.
**Purpose:** preserve execution receipts without promoting drafted tests into PASS claims.

## Evidence obtained

| Check | Observation | Claim ceiling |
| --- | --- | --- |
| GitHub main/candidate identity | Main \`85374e705115ec4884b8e0c85f3f69b6fe1c342a\`; cumulative opt-in candidate \`bd2ba539d2f300941681fa7c7b80ab4765354b79\` | Repository-source identity only |
| PR metadata | #346 and #361 verified OPEN/DRAFT, not merged | No main-branch implementation claim |
| Source inspections | Current Beginner, Studio HTML/JS, working store/API, relations, impact, Book progress, Quick Draft contracts read via connected GitHub tools | Static architecture and interaction claims |
| Isolated JS reproducer | Extracted \`renderInspector\` and \`choose\` from exact candidate, evaluated with minimal DOM stub. Initial A = "Original A"; typed "Unsaved crucial dialogue"; select B then A -> rendered "Original A"; model still "Original A" | Source-derived deterministic logic failure; **not** a real Browser test |
| Container GitHub access | \`git ls-remote https://github.com/ThorStarlord/auteur.git HEAD\` returned "Could not resolve host: github.com" | External DNS/network blocker; no local git checkout established |
| Python pytest / Ruff | Not run against candidate; no mounted Auteur checkout | No test-PASS claim |
| Browser/API/real host agent | Not run | No runtime, user or provider qualification |
| Human author study | No participants available from this workspace | Product value/preference still uncertain |

The original JavaScript logic reproduction is deliberately narrow: an isolated handler behavior, not evidence for the full Browser error rate or server data durability.

## Shared scenario evidence map

| Scenario | Status here | Exact next observable evidence |
| --- | --- | --- |
| S1 no-premise/free-form entry | Source supports | Actual first note persisted/reopened |
| S2 edit A -> B -> A | **Source behavior reproduced** | Confirm browser repro, then targeted repair retest |
| S3 scene Quick Draft | Source supports endpoint route | Real host-agent staging and returned identity via #310 |
| S4 Sister Beatrice discovery/acceptance | Working and guided paths exist separately | Full source-to-accepted roundtrip in one Book |
| S5 ambiguous relationships | Source relationships and working links exist | User can distinguish established/possible relationships |
| S6 large graph | Node/edge caps are explicit | 12 characters/three threads, focus/responsiveness observation |
| S7 impact of accepted revision | Hypothetical traversal source exists | No canonical mutation; comprehensible explanation |
| S8 six-Chapter re-entry | Home link opens new ID without URL; existing Book progress service | Reopen same canvas and Book after restart; #318 evidence |
| S9 keyboard/narrow display | Outline and key handlers in source | Live keyboard/focus/assistive tech task success |
| S10 two tabs/interrupt/recovery | Revision/replay/tombstone mechanisms present | Real concurrent HTTP/browser, crash/reopen tests |
| S11 chapter relationship changes | Change-file scan exists | Accepted/unaccepted source provenance comparison |
| S12 longevity | Unbounded command hashes in code | File-size/latency at 100/1000/10000 saves |

## Exact local commands and execution handoff

In a local checkout with a compatible Python + Node runtime and dependencies installed:

\`\`\`sh
git fetch origin feature/living-story-studio-save-recovery-20261009
git checkout feature/living-story-studio-save-recovery-20261009
git rev-parse HEAD
node --check src/auteur/beginner/browser/studio.js
python -m pytest -q tests -k beginner_studio
python -m ruff check src/auteur/beginner/studio_store.py src/auteur/beginner/studio_projection.py src/auteur/beginner/studio_impact.py src/auteur/beginner/server.py tests/test_beginner_studio_*.py
\`\`\`

Use repository-supported local commands when shell globbing differs (e.g. Windows). Run existing Beginner Browser/Server/Quick Draft and Book regressions in addition to Studio tests. Record command exit codes, counts, exact HEAD and first material failure. Any repair target SHA must be separately named; do not silently swap candidates.

## Comparative author evaluation protocol (not yet run)

1. Same broad story prompt/complexity for A graph-first, B hybrid mock/workflow, C current Beginner. Counterbalance interface/task order.
2. Writer can start from a vague premise, create an unmodeled person/place, explore changing ambiguous relationships, write prose, and return to a six-Chapter Book.
3. Record separately: completed creative decisions, useful novel alternatives, accuracy of relation/canon interpretation, author administration steps, prose flow interruptions, navigation loss and time, qualitative preference.
4. Include writers attracted to spatial planning *and* writers who prefer direct prose, without treating either group as representative by default.
5. Author comments and real task outcomes outrank synthetic agent intuition about intuitiveness. Prototype only the smallest rival needed to decide product direction.
6. Do not define a numerical total score or promotion threshold before knowing which consequence actually matters. Use explicit qualitative benefit/cost tradeoffs.

## Stop / resumption

Current review can resolve source design questions and perform narrow source-based repairs. The remaining claim about *successful author outcomes* is blocked until a running application and genuine author observations exist.

Use [#360](https://github.com/ThorStarlord/auteur/issues/360) for running application qualification, [#318](https://github.com/ThorStarlord/auteur/issues/318) for F2/X3 Book use and [#310](https://github.com/ThorStarlord/auteur/issues/310) for real Quick Draft host-agent use. Do **not** rerun GitHub Actions that incur unavailable credits, claim tests passed, or default-promote the Studio based on these documents.

**Evidence ceiling:** source-inspected with a narrowly executed JavaScript control-flow reproduction. Runtime/UX/author-value PASS remains absent.
