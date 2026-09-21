# Auteur — Repository Status

**Last reconciled:** 2026-09-20  
**Validation-policy activation baseline:** `main @ 8b53efdd99e0a67d375df0e828b32edc77643221`  
**Behavior baseline reconciled:** `main @ c633d1b155ff72ef9ba502d4b7c9a294716fe98a` (post-draft continuation, Realization reconciliation, Beginner whole-book orientation, and bounded maintainability extractions merged)  
**Current maintenance/product-contract reconciliation baseline:** `main @ e1ee3957f6761d4f63c77120a2d99568ae26908c` (#248 Book reconciliation seams through the Phase C4 completion-validator extraction in PR #274 plus PRD reconciliation in PR #276)  
**Known-good stabilization baseline:** `main @ 2aba74b64f2434d11954a8627fc3d95fd83fdb7d` (L3 tested)  
**Package metadata:** `1.0.0` — development metadata; not a publication claim  
**Latest published GitHub release/tag:** `v0.37.1`  
**Role of this file:** living operational status and handoff; not a release record or idea backlog.

The current development line includes the tiered validation and bounded-agent-autonomy policy, the human-qualified Beginner Workspace foundation, the premise-to-architecture and first-draft continuation work, PR #246's contemporary post-draft / Chapter N → N+1 loop, PR #250's commitment/Review authority correction, PR #253's Realization-contract reconciliation, PR #258's read-only whole-book Beginner orientation, and bounded #248 maintainability extractions through PRs #256, #259, #260, #265, #266, #267, #268, #271, and #274. The Book reconciliation slices keep `BookReconciliationStore` as the compatibility facade while separating accepted-source state, acceptance/completion persistence, derived recomposition/comparison evidence persistence, Phase A/B application-artifact access, and the read-only Phase C3 acceptance and Phase C4 completion eligibility gates. PR #276 also reconciled `docs/PRD.md` with the integrated product without changing product scope or hard invariants. The exact current HEAD may advance after this living document is merged; the reconciled behavior baseline above identifies the code state this status describes.

For product intent, read [MISSION.md](MISSION.md) and [docs/PRD.md](docs/PRD.md). For the canonical domain model, read [docs/narrative-architecture.md](docs/narrative-architecture.md). For forward-looking candidates, read [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md). Release evidence lives under [docs/releases/](docs/releases/README.md).

## Development Validation Posture

- **L1 Focused Validation** is the normal development and PR gate.
- **L2 Targeted Integration** requires a named changed boundary or concrete risk.
- **L3 Full Regression** is reserved for explicit stabilization, recovery, milestone, or release-candidate checkpoints.
- **Release Qualification** is separate from L3 and requires an explicitly frozen candidate SHA.
- Normal integration into `main` does not imply release qualification; `main` represents the latest stable development state.

Canonical policy: [docs/engineering/release-qualification.md](docs/engineering/release-qualification.md).

The PR #233 stabilization checkpoint recorded the prior baseline lint disposition. After PR #235 removed those four whitespace findings, the clean L3 checkpoint on `main @ 2aba74b64f2434d11954a8627fc3d95fd83fdb7d` passed full regression and the verification stack. No release qualification is implied. Return to Auteur product development and use real-author dogfood evidence to select the next bounded package.

## Current Selected Responsibility

**SIMULATION-FIRST PRODUCT EVIDENCE / MAINTENANCE REASSESSMENT** — The post-draft / Chapter N → N+1 continuation is merged, the Beginner surface exposes read-only whole-book progress and publication handoff readiness, and the currently warranted bounded #248 seams have landed through the Phase C4 completion validator. No additional #248 slice is presently selected. Further decomposition requires a newly identified concrete responsibility that can move behavior-preservingly behind stable public/authority semantics with focused regression evidence; file size alone is not admission evidence.

Issue #249 is now a simulation-first product-evidence responsibility, not automatic feature authority. A scripted novice journey may establish mechanical/workflow coherence and may select a provisional, reversible intervention from concrete exercised friction without additional human approval. It may not be relabeled as evidence of real-author usefulness, relevance, comprehension, or subjective story quality. Changes to semantic architecture, story authority, irreversible migration, or permanent product scope still require stronger evidence/authority.

The first scripted premise-to-Chapter-2 probe in PR #280 produced one concrete **workflow** finding: after explicit Whole-Story Structure acceptance, the read-only Beginner projection left `continuation=None`, so the existing `propose-outline` transition was not discoverable even though the transition itself already supported the state. The bounded fix projects an empty continuation frontier after accepted Structure without persisting state or crossing authority; the first continuation command still creates durable continuation state. The same scripted journey then reached contextual Chapter 2 planning and the focused verification stack passed. Post-fix result: **`NO_SIMULATED_MATERIAL_FRICTION` beyond the corrected projection seam**. This does not establish real-author usability or subjective-quality evidence, and it does not select PATH-1/2/3/4 feature expansion.

The Level-3 strategic decision space remains preserved in [artifacts/strategic_repository_analysis.md](artifacts/strategic_repository_analysis.md), merged via PR #264, but its earlier human-only evidence gate is superseded by the current owner-authorized simulation-first policy. #248 remains paused at reassessment after the C4 extraction and may resume only if another concrete behavior-preserving responsibility boundary is independently warranted.

Correctness/evidence debt from this session is reconciled: #247 (Book/full-suite evidence) and #251 (legacy Realization xfails) are closed. Historical qualification issues #49–53 were reconciled against the contemporary release path and closed; #54 remains partially satisfied pending an actual cross-platform candidate run, and #55 remains reproduction-gated on that Windows qualification evidence.

## Current Product Direction

Auteur is a local-first literary compiler and guided narrative-decision system for long-form fiction. The current product loop is now executable end to end:

```text
accepted narrative authority
→ derived context / diagnostics / craft knowledge
→ one bounded author decision
→ advisory recommendation + trade-offs
→ explicit advisory response
→ derived authority handoff
→ concrete noncanonical proposal when supported
→ explicit proposal selection
→ revision plan + validation
→ derived change preview
→ explicit owning-workflow authority action
→ bounded reassessment
→ project orientation
```

Derived systems may orient, diagnose, compare, explain, recommend, prepare, preview, and reassess. Determinism, persistence, currentness, or user selection do not grant story authority.

The next evidence task is issue #249's simulation-first journey on merged `main`:

```text
premise → narrative architecture → accepted foundation → outline/planning
→ scripted Chapter 1 draft → post-draft review → explicit simulated acceptance
→ accepted outcome → contextual Chapter 2 plan
```

The post-draft package is an integration continuation, not a new semantic layer. Record concrete mechanical/workflow friction separately from any proposed fix. If the scripted journey reaches Chapter 2 without a material dead end, `NO_SIMULATED_MATERIAL_FRICTION` is a valid result and no feature must be invented.

## Canonical Architecture

Auteur retains five semantic layers: **Ontology → Identity → Structure → Realization → Expression**. The independent scope axis remains **Universe → Series → Book → Chapter → Scene**. Scopes are containers, not additional semantic layers. Validation, orchestration, diagnostics, provenance, maps, Tutor guidance, planning, simulation, dashboards, and browser presentation remain cross-cutting capabilities.

## Authority Model

The central invariant remains explicit author authority.

- Story Discovery candidates remain advisory until explicit StoryIdentity acceptance.
- Decision Cards are `DERIVED / NOT CANON`.
- Tutor sessions are `LOCAL / NONCANONICAL`.
- Decision Handoffs are derived routing, not mutation.
- Tutor-generated Structure proposals are noncanonical working artifacts until explicitly selected.
- Structure revision plans and Narrative Change Preview are not applied story state.
- `structure revision apply --confirm` is the explicit Structure authority boundary in the qualified Tutor-to-Structure path.
- Decision Reassessment, Author Attention, Dashboard, and Guided Author Workspace V1 are read-only projections.
- Failure at an authority-bearing boundary must leave prior authoritative state intact.

## Stable Capability Families on `main`

The production baseline includes:

- **Story Discovery and StoryIdentity** — multiple plausible story engines, recommendation/search support, explicit author acceptance, and validation.
- **Genre knowledge and authoring** — Genre Packs, overrides, diagnostics, and interactive genre-pipeline infrastructure.
- **Story Design Packs / Tutor** — reusable craft priors, Decision Cards, source-aware Tutor sessions, `next/explain/show/choose/handoff/propose`, and stale-source blocking.
- **Structure engine** — generation/diagnostics plus explicit proposal inspect/select, fail-closed revision planning/validation, derived preview, confirmed application, and read-only reassessment.
- **Project orientation** — deterministic Author Attention in the existing dashboard and loopback-only Guided Author Workspace V1.
- **Beginner story-development continuation** — accepted foundation → outline/Chapter planning → post-draft review → explicit existing-owner Chapter acceptance → contextual Chapter N+1 planning, plus read-only whole-book/reconciliation/publication orientation.
- **Realization/state/provenance** — state coordination plus impact, convergence, decision, review, planning, simulation, and portfolio support.
- **Series / long-horizon infrastructure** — accepted-history/current-state reconstruction, derived Global Map/Focus, continuity support, and Guided Series Continuity Review V1.
- **Outline and drafting** — Cartographer outline compilation, chapter contracts, Bard/Critics drafting, retry, and explicit acceptance.

## Decision-Loop Milestone — Complete

The evidence-led continuation after Tutor M1 is merged and qualified:

| Package | Result |
| --- | --- |
| Beginner Decision Golden Path | Exposed the missing post-choice authority route without mutating accepted story state. |
| Decision-to-Authority Handoff | Routes a resolved supported Tutor choice to the existing owning authority workflow without executing it. |
| Tutor → Structure Proposal Bridge | Produces one validated, unselected, noncanonical concrete Structure proposal. |
| Structure Proposal Review / Selection | Adds explicit inspect/select while keeping blueprint authority unchanged. |
| Revision continuation + fail-closed hardening | Selected Tutor proposals create meaningful plans; stale/invalid/destructive paths fail closed. |
| Narrative Change Preview | Read-only preview over existing revision/dependency evidence; no second impact engine. |
| Decision Reassessment | Re-runs exact native diagnostic evidence when available and returns `not_assessable` rather than inventing craft certainty. |
| Unified Project Orientation | Dashboard Author Attention prioritizes the next safe decision artifact/action. |
| Full Beginner Decision Loop | Hermetic integration proof crosses the explicit Structure authority boundary only at confirmed application. |
| Guided Author Workspace V1 | Local `127.0.0.1` GET-only beginner presentation over dashboard/attention semantics; no mutation endpoints. |

The beginner-facing walkthrough is [docs/guides/guided-author-decision-loop.md](docs/guides/guided-author-decision-loop.md).

## Qualification State

The code-bearing packages in the completed stack were qualified on their exact candidate heads with:

- Linux Python 3.11 / 3.12 / 3.13 validation;
- full Windows Python 3.13 test coverage;
- repository verification;
- installed-wheel smoke.

The full Golden Path proves:

1. StoryIdentity remains byte-identical through the complete Tutor/Structure decision loop.
2. `blueprint.yaml` remains byte-identical until explicit `structure revision apply --confirm`.
3. proposal selection, planning, validation, preview, and reassessment preserve their documented boundaries.
4. Tutor/craft reassessment does not manufacture a deterministic resolution claim.
5. after the blueprint changes, prior source-bound Tutor advice is surfaced as stale by project orientation.

This is hermetic repository evidence, not an external-provider or subjective story-quality claim.

The 2026-09-20 consolidation packages (#253, #256, #258, #259, #260, #265, #266, #267, #268, #271, #274) passed their exact-head L1 validation before merge. PR #271 selected and passed the complete 76-test `tests/test_book_acceptance.py` suite plus the focused verification stack on candidate `bf5c45d7d4bec5ec5b5f7e332ee913d036a3f5bf`. PR #274 selected both Book authority-adjacent suites and passed 138 tests (`tests/test_book_reconciliation_completion.py` + `tests/test_book_acceptance.py`) plus the focused verification stack on candidate `abe3670a7317ed7d8f0c5bc105e240b55d7e3f46`; the subsequent `main @ 27356e7c9b0793eec70014aaf29a678af610f5fc` push validation also passed. PR #276 was documentation-only and passed its contemporary exact-head L1 gate. These results do **not** establish a new L3 checkpoint or release qualification. The last explicitly recorded L3 stabilization baseline remains the one named at the top of this file.

## Next Product Selection

**No additional product package is implicitly authorized by the completed roadmap sequence or by the post-draft continuation merge.**

The next product package should be selected from observed use of the now-complete loop rather than extending ontology or adding another subsystem by default. Strong preserved candidates include:

- Unified Decision Inbox / broader attention-source coverage;
- Current Author Intent if relevance friction appears;
- demand-driven Story Design Pack growth;
- Existing-Manuscript Reverse Engineering;
- Book-Level Reasoning and Editing;
- bounded Episode 1 Direction reconstruction when the serial lane is deliberately selected.

A small discoverability follow-up may also be warranted if beginner use shows the new workspace/decision surfaces are hard to find from root CLI help. That is a UX problem, not a reason for new narrative architecture.

## Serial / Episode Posture

Historical PR #167 is **closed / not merged / superseded**. Its bounded Episode 1 Direction contract remains useful, but the old 4k-line implementation is not contemporary production evidence.

Fresh issue #218 preserves the reconstruction contract: Episode 1 remains a Series-scope, Identity-layer entry-unit Direction artifact for explicitly episodic Series and **does not become a sixth canonical scope**. Any future implementation must start from contemporary `main` in bounded packages.

Broader Episode 2+/season expansion remains subject to the separate long-horizon evidence gate.

## Long-Horizon Campaign Posture

The long-horizon campaign remains `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION` with **no active implementation responsibility**.

Do not manufacture another long-horizon experiment; do not start new ontology, automatic extraction, V2 continuity-review, or scale expansion without the campaign's documented natural Auteur-native evidence trigger. Global Map/Focus remain derived/rebuildable projections rather than second canon.

See [docs/campaign/auteur-long-horizon-campaign-state.md](docs/campaign/auteur-long-horizon-campaign-state.md).

## Repository / CI Notes

- Ordinary PR/main validation now uses the L1 focused gate from PR #229; full regression is an explicit stabilization action, and release qualification is an explicit frozen-candidate action.
- Historical Episode 1 PR #167 is closed/superseded by contemporary reconstruction issue #218.
- Historical divergent PRs #131, #221, #222, #225, #227, and #245 have been reconciled and closed rather than bulk-merged. Still-relevant responsibilities were reconstructed on contemporary `main` or preserved as explicit current issues.
- #247 is closed after classifying the later Book/full-suite reports as incomplete bounded executions rather than a reproduced Book-authority regression; a focused Book acceptance sentinel and better L3 timing/JUnit evidence now exist.
- #251 is closed after replacing obsolete Layer-3 `xfail` assumptions with current-schema Realization coverage and bounded temporal/knowledge fixes.
- #248 is an incremental maintainability program, not evidence that the repository is incomplete: merged slices have extracted Beginner continuation transitions, reasoning CLI dispatch, Book accepted-source/pointer persistence, Book acceptance persistence, Book completion persistence, derived recomposition/comparison artifact persistence, Phase A/B application-artifact access, the Phase C3 acceptance validation gate, and the Phase C4 completion eligibility gate behind compatibility seams. `BookReconciliationStore` still owns authority-bearing orchestration, publication ordering, pointer movement, rollback, and the remaining workflow semantics. After PR #274 the largest remaining methods are mixed comparison/routing/publication responsibilities rather than another comparably obvious read-only gate, so #248 is paused at reassessment rather than continuing from file size alone.
- Historical qualification issues #49–53 are closed as superseded/no-current-change; #54 and #55 remain evidence-gated against a future exact candidate.
- Issue #272 records the remaining GitHub-admin enforcement gap: `main` is still unprotected and the stable `L1 focused validation (Python 3.12)` check is not yet required. PRs #271 and #274 hardened focused-test selection for the Book acceptance/completion seams, but branch-protection/ruleset application remains an external administration action because the connected GitHub integration exposes those settings read-only.
- `pyproject.toml` reports `1.0.0`, but remote release/tag inspection on 2026-09-20 shows the latest published GitHub release remains `v0.37.1`; package metadata alone is not publication evidence.

## Documentation Map

- [artifacts/strategic_repository_analysis.md](artifacts/strategic_repository_analysis.md) — durable Level-3 decision space; current disposition is `INVESTIGATE`, not product implementation authority.
- [docs/guides/guided-author-decision-loop.md](docs/guides/guided-author-decision-loop.md) — beginner-facing end-to-end decision loop.
- [docs/design/decision-oriented-tutor.md](docs/design/decision-oriented-tutor.md) — Tutor/session/handoff authority and staleness model.
- [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md) — candidate directions/evidence gates.
- [docs/reviews/beginner-decision-golden-path.md](docs/reviews/beginner-decision-golden-path.md) — original post-M1 evidence that selected the handoff gap.
- [docs/narrative-architecture.md](docs/narrative-architecture.md) — canonical five-layer × scope architecture.
- [docs/architecture-roadmap.md](docs/architecture-roadmap.md) — architecture integrity/history, not the current product queue.
- [CHANGELOG.md](CHANGELOG.md) / [docs/releases/](docs/releases/README.md) — release history/evidence.

## Reconciliation Rule

When behavior changes materially, update living surfaces in this order:

1. `STATUS.md` — current state and next action.
2. `README.md` — when user-facing capability, framing, or entry path changes.
3. `CHANGELOG.md` / `docs/releases/` — for release history.
4. `CONTEXT.md` — for runtime/domain terminology or compatibility changes.
5. `docs/product-evolution-roadmap.md` — when candidate state, evidence gate, or product-evolution policy changes.
6. Mission, PRD, canonical architecture, ADRs, and historical evidence only through their own change processes.
