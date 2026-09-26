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

