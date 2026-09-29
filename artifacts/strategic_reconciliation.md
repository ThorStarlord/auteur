# Strategic Repository Reconciliation

## Identity

- **Repository:** `ThorStarlord/auteur`
- **Prior strategic analysis:** `SRA-AUTEUR-2026-09-20-E2FB5EE`
- **Prior source identity:** `main @ e2fb5ee989bb41677150414d7da97b3327d28d81`
- **Current base:** `main @ 3836c26d1edd1b596ae10547aad09a6ff9fcffd4`
- **Current execution surface:** PR #285 / `experiment/beginner-coherence-current-main`
- **Reconciliation date:** 2026-09-24

## Why reconciliation was required

The prior Level-3 analysis ended at `INVESTIGATE` because it treated a real-author
premise-to-Chapter-2 run as the decisive product-selection gate. Contemporary
repository authority later changed that premise:

- `docs/PRD.md` and `STATUS.md` adopted simulation-first, claim-bounded
  evidence for reversible product work;
- issue #249's scripted journey completed and found one mechanical projection
  seam, later repaired;
- a subsequent 2026-09-23 Beginner walkthrough selected a bounded
  Narrative-Architecture Coherence / deterministic-fallback package;
- PR #285 reconciled that selected behavior onto current `main` and formalized
  synthetic E2E evidence for the owner-authorized claim boundary.

The old strategic artifact remains historical evidence; this reconciliation
updates continuation rather than rewriting it.

## Breadth system scan

The current repository was inspected as four interacting planes:

```text
author product
-> narrative authority
-> decision intelligence
-> infrastructure
```

The main opportunity themes were:

1. **Product compression:** internal capability depth is greater than the
   complexity a beginner should have to understand.
2. **Coordination-layer proliferation:** Decision, Review, Impact, Convergence,
   Planning, Simulation, Portfolio, Commitment, Workflow, and related systems
   are individually coherent but can overwhelm product presentation if exposed
   directly.
3. **Authority legibility:** the strongest architectural invariant remains
   advice/candidate/proposal/derived state versus explicit owning-workflow
   authority.
4. **Beginner integration concentration:** the Beginner application is becoming
   the application layer over many mature systems, so integration seams matter
   more than another domain layer.
5. **Advanced-system discoverability:** substantial planning, Book, Series, and
   counterfactual machinery exists, but it should surface through progressive
   disclosure rather than subsystem vocabulary.

## Frontier candidates considered

### Candidate A — Backend-owned primary action hierarchy

Move "what should I do next?" out of browser inference and into a deterministic
read-only product projection over the existing action set.

- Value: shrinks visible complexity and makes misuse harder.
- Authority effect: none; projection does not execute.
- Reversibility: high.
- Evidence: directly follows PR #285's transition-salience/action-hierarchy
  findings.

### Candidate B — System ownership and progressive-disclosure contract

Document semantic owner, authority owner, and product projection for the major
system families; establish that Beginner/UI surfaces compose systems without
becoming parallel authority.

- Value: reduces future architectural drift and subsystem exposure.
- Authority effect: documentation only.
- Reversibility: high.
- Evidence: repository-wide system scan.

### Candidate C — Broader Unified Decision Inbox

Extend Author Attention across more internal systems.

- Value: potentially high.
- Deferral reason: current evidence does not show omitted sources causing a
  concrete author problem; the roadmap already keeps this as a candidate.

### Candidate D — Large Beginner application refactor

Further decompose the Beginner application because it is a complexity hotspot.

- Value: maintainability.
- Deferral reason: file size/complexity alone is not admission evidence; issue
  #248 is intentionally paused at reassessment.

### Candidate E — New semantic/domain architecture

Add another narrative layer or generalized orchestration abstraction.

- Deferral reason: contradicted by current product direction. Existing semantic
  architecture can express the observed problem.

## Selected bounded responsibility

**BUILD — product-compression seam, without new authority or new semantic
architecture.**

Selected work:

1. project one deterministic `primary_action` from the existing
   `available_actions` set;
2. preserve `available_actions` as compatibility/debug capability;
3. make the browser consume `primary_action` for primary styling and
   continuation rather than deriving priority from action ordering;
4. add synthetic/browser assertions for the contract;
5. document the system-ownership and progressive-disclosure rules;
6. reconcile PRD/README/STATUS with the new product contract.

## Returned evidence

Implemented on PR #285's current-main reconciliation branch:

- `src/auteur/beginner/projections.py`
  - added a read-only `PrimaryActionProjection`;
  - action hierarchy prefers forward workflow continuation/review/acceptance
    and leaves optional revision entry secondary;
  - no action is executed by projection.
- `src/auteur/beginner/server.py`
  - exposes the projected primary action in the public Beginner workspace JSON.
- `src/auteur/beginner/browser/app.js`
  - primary styling and continuation consume the backend projection;
  - compatibility fallback remains for older projections.
- `tests/test_beginner_synthetic_walkthrough_claims.py`
  - asserts `propose-outline` is the projected primary action after accepted
    Whole-Story Structure and `accept-outline` becomes primary after proposal.
- `tests/test_beginner_workspace_browser.py`
  - asserts the browser binds to `projection.primary_action`.
- `docs/architecture/system-ownership-and-product-compression.md`
  - records semantic owner / authority owner / product projection boundaries and
    the progressive-disclosure contract.
- `docs/PRD.md`, `README.md`, `STATUS.md`
  - integrate the product rule into durable/current documentation.

## Strategic effect

**REVISE_STRATEGY — bounded integration rule, not a new product thesis.**

The earlier strategic conclusion "architecture-led construction has diminishing
returns" is reaffirmed and sharpened:

```text
internal specialization may continue when warranted
+
visible beginner complexity should decrease
+
product projections should compose existing owners
+
new subsystems require evidence that presentation/workflow/craft/domain owners
cannot already express the need
```

This does not select Unified Decision Inbox, Current Author Intent,
Existing-Manuscript Reverse Engineering, Book-scale reasoning expansion,
Episode 1, or long-horizon ontology expansion.

## Final responsibility state

2026-09-25 continuation selected the earliest broken Beginner transition:
accepted scene plans -> Chapter 1 draft. PR #288 now composes the existing Bard,
critic, post-draft, and chapter-acceptance owners into one in-app path. Candidate
drafts remain noncanonical; only explicit Chapter acceptance creates `final.md`
and accepted Bible state.

## Authority boundary

```text
durable strategy -> bounded construction -> exact-head validation -> merge
```

The current owner prompt explicitly authorizes repository-owned integration.
Chapter 2, release qualification, publication, and subjective prose/usability
claims remain outside this bounded responsibility.

## 2026-09-26 post-merge continuity reconciliation

A fresh journey scan on `main @ de0551421c7d7d6b657c7534c00a94ecad625cb3`
found that PR #288's product direction remained correct but one execution claim
was too strong. `draft-chapter-1` existed in projection/browser wiring and the
application owner was implemented, yet the HTTP dispatcher omitted that slug
from the rich-command path. The real browser transition therefore could not
reach `draft_chapter_one(expected_session_version=..., command_id=...)`.

Selected bounded repair: PR #289. It adds the missing dispatch membership and an
HTTP-level regression that executes candidate drafting through the same command
surface used by the browser, while retaining the noncanonical-candidate /
explicit-acceptance boundary.

Strategic effect: **NO_MODEL_CHANGE / REAFFIRM**.

The product-compression direction is strengthened rather than revised:

```text
existing specialized owner
+ product projection
+ browser control
+ executable API/application composition
= beginner-facing continuity
```

Projection or presentation evidence alone is insufficient for a cross-layer
continuity claim. This does not warrant a new subsystem, new narrative ontology,
Chapter 2 expansion, release qualification, or a new experiment. Provider
credentials remain an external runtime prerequisite; prose quality and real
beginner usability remain human validation claims.

## 2026-09-26 closure

PR #289 merged to `main @ e6700044d5813bcb2041714f7c6bed6cdb128aee`.
Its exact candidate head
`690bb90a60807b67331959e8c7fd0fc07e3b8be0` passed the repository's
GitHub Validation run #793 before merge.

A final post-merge scan found no further demonstrated repository-owned
mechanical discontinuity in the bounded raw-premise -> explicit accepted
Chapter 1 journey once a provider-enabled runtime is available.

Disposition: **NO_FURTHER_REPOSITORY_WORK_SELECTED** for this responsibility.

Stop boundaries are now genuine rather than missing application composition:

- provider credentials / adapter availability are external runtime
  prerequisites for prose generation;
- prose quality and real-beginner usability require human evidence;
- Chapter 2, publishing, release qualification, and new semantic architecture
  require separate evidence or owner selection.

Do not reopen this package merely because additional systems or roadmap
candidates exist.

## 2026-09-28 Layer-3 stabilization / Episode-1 qualification reconciliation

### Resume point

- **Source:** `main @ 7f5da9485afdc974a15db32b23971607669b69d3`
- **Episode posture:** bounded Episode 1 Direction implemented through PRs #291 -> #292 -> #293; issue #218 still open.
- **Blocking evidence:** Stabilization run `36370311870` failed in Layer-3 knowledge validation. The failure reproduced before the Episode stack and had no file overlap with it.
- **Repository-owned repair issue:** #295.

### Reconciled diagnosis

The exact-knowledge validator introduced by the contemporary Realization contract is the intended deterministic behavior. The failing fixtures were stale: they mixed identifier-like values, paraphrases, capitalization differences, or omitted carry-forward facts between `Outcome.knowledge_added` and `exit_state.knowledge[].what`.

The selected repair therefore preserves the validator and reconciles the data contract:

```text
knowledge_added fact
= exact persisted exit-state fact value

entry knowledge
-> remains in exit state
unless that exact fact is explicitly questioned

no deterministic paraphrase inference
```

If stable fact IDs and display prose are both needed later, they require an explicit schema distinction rather than fuzzy matching in validation.

### Execution surface

PR #296 / `fix/layer3-knowledge-continuity`:

- repaired the two affected Layer-3 executable fixture suites;
- reconciled the Chapter 7 dogfood YAML with the executable state contract;
- documented the exact current-schema continuity rule;
- reconciled README and product-roadmap Episode 1 posture;
- preserved the evidence gate against Episode 2+, season planning, Episode realization, or generalized Book/Episode abstraction.

### Returned evidence

Exact repair head before status/artifact-only reconciliation:
`323c71a8c54b164a5a5f48b3c41393dadd3aacb5`.

GitHub Validation run `36508279451`:

```text
affected Layer-3 suites        63 / 63 PASS
validator verification        25 / 25 PASS
repository validator          PASS
release-scope validator       PASS
vendored contract             OK
Ruff                           PASS
```

The targeted evidence covers the eight failures reported by stabilization run
`36370311870`. It does not convert L1 evidence into an L3 or release-
qualification claim.

### Strategic effect

**NO_MODEL_CHANGE / REPAIR_AND_REAFFIRM**

The episode strengthens the existing strategy:

```text
deterministic contract
+ stale evidence/fixture mismatch
-> repair fixtures and contract documentation

not

deterministic failure
-> add semantic guessing to the validator
```

No new semantic layer, Episode ontology, generalized entry-unit abstraction, or
new product-expansion path is warranted by this defect.

### Current bounded state and stop boundaries

- **Engineering:** PR #296 is the bounded repair surface; targeted L1 evidence is green.
- **Stabilization:** issue #295 remains open until the repository's formal L3 full-regression workflow runs green on a candidate containing the repair.
- **Episode qualification:** issue #218 remains open until the required cross-platform / verification / wheel qualification and its bounded human-validation questions are satisfied.
- **Product direction:** no new expansion responsibility is selected from this repair.
- **Serial expansion:** Episode 2+/season/generalized Episode work remains evidence-gated.
- **Authority:** this reconciliation does not authorize merge, release, publication, or substitution of agent evidence for required human validation.

The connected GitHub execution surface can read/rerun existing Actions but does
not expose starting a new `workflow_dispatch` run, so formal L3 and release-
qualification dispatch remain outside this execution surface in this episode.



## 2026-09-28 post-merge stabilization/documentation closure

### Returned evidence

The owner explicitly authorized the previously reserved repository transitions.

- PR #296 merged to `main @ 519e4a6e94903535a6b129a9a17bf070ca7ef09a`.
- Exact #296 head `6a6133ed31dc4dd73e396a39516828fe140b03b0` retains green GitHub Validation run #811 (`36508577436`): affected Layer-3 boundary **63/63 PASS**, validator verification **25/25 PASS**, repository validation PASS, release-scope validation PASS, vendored contract OK, Ruff PASS.
- PR #297 was retargeted from the repair branch to `main`; the post-#296 merge tree exactly matched the #296 head tree (`dd344e111ddc3cc124971e284098c7f5220502ff`), so the reviewed documentation diff remained the same eight files.
- PR #297 merged to `main @ b9233ffe5b5748ad1b0355ecb00b4289a7b2e45b`.
- Exact #297 head `7b2c3ad50a6d7f787e6cde2e06a6b81c3f4395c5` retains green Validation run #812 (`36514785358`), including docs-fallback smoke **4/4 PASS**, validator verification **25/25 PASS**, repository/release-scope validators PASS, vendored contract OK, plus a zero-broken-relative-link audit across all eight changed documentation files.

### Reconciled state

The repair and semantic-documentation responsibilities are now **MERGED / COMPLETE**.

```text
exact deterministic knowledge contract
+ repaired stale fixtures
+ canonical Realization/emotion/character/relationship/theme ownership docs
-> repository contract convergence
```

This changes execution state, not product strategy.

### Strategic effect

**NO_MODEL_CHANGE / REPAIR_AND_REAFFIRM**

The merged evidence reinforces the prior conclusion:

- strict deterministic validation exposed stale evidence rather than a need for semantic guessing;
- canonical semantic contracts reduce the cost of reconstructing ownership from source + historical plans;
- no new layer, generalized Episode ontology, Episode 2+/season path, or speculative product package is warranted.

### Remaining bounded responsibilities

- **#295 — formal L3 requalification:** OPEN. A fresh Stabilization/full-regression run must execute on a candidate containing the merged repair and pass before the last formal-red L3 evidence is superseded.
- **#218 — Episode 1 qualification:** OPEN. The bounded capability is implemented; remaining closure requires the documented cross-platform / verification / wheel qualification and the contract's human-validation questions.
- **Release/publication:** not selected or claimed.
- **Episode 2+/season/generalized entry-unit expansion:** not selected; remains evidence-gated.

### External execution boundary

The connected GitHub tool surface still does not expose creating a new
`workflow_dispatch` run. Rerunning the historical failed Stabilization run would
re-execute its old SHA and would not qualify the merged repair, so it is not a
valid substitute.

No independently warranted repository repair remains behind that blocker after
the status/issue reconciliation. The correct stop state is therefore:
**QUALIFICATION_BLOCKED_EXTERNALLY / NO_NEW_PRODUCT_WORK_SELECTED**.
