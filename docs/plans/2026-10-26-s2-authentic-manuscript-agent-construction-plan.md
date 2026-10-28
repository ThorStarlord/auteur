# S2 Manuscript-First Authentic-Agent Journey — Construction Plan

**Date:** 2026-10-26  
**State:** SELECTED BOUNDED EXECUTION PLAN — **not** evidence that the journey or its tests ran.  
**Repository/source:** `ThorStarlord/auteur` `main@1e118ff0d0ad7018630efa1bafbeb8c2c7780428` when scoped. Re-read `main` before work.  
**Product direction:** graph-first, coding-agent-first **Connected Creative Thread**; controlled F2 small-Book and X3 persistent workspace remain separate, unqualified frontiers.  
**Immediate objective:** make one authentic host coding-agent encounter with *existing, ambiguous prose* reproducible, preserve author corrections and exact sources, and improve the **smallest** product owner proven inadequate by that encounter.

## 1. Decision and rationale

**Chosen:** **REVERSIBLE BUILD + AUTHENTIC USAGE PROBE**. Build a small reusable, disposable S2 exercise driver around current `CanvasStore` and the Architecture/Realization host-agent contract; then exercise it with the actually available coding agent, record what happened, and retain only useful, bounded product improvements.

This is a product-construction move, **not** a standalone scientific benchmark and **not** a prerequisite for another large ontology project. An actual agent reply is necessary for a claim that an agent interpreted prose. However, lack of one executable environment must not prevent independently useful work such as a reproducible fixture and honest existing-owner improvements. Tests protect the claims they actually exercise; they are not a proxy for the author's creative judgment.

**Decision trace:**

| Alternative | Value | Decision now |
| --- | --- | --- |
| A. Build a new manuscript importer, narrative-memory system or standalone Story Archaeologist UI | A larger potential future product | **Defer.** No concrete recurring failure shows a new owner or state distinction is needed. |
| B. Run only another prompt-written illustrative analysis | Cheap additional examples | **Insufficient.** [The prior S1/S2 report](../product-validation/2026-10-25-s1-s2-agent-creative-probes.md) already supplies one assistant-authored sample; repeating it would not demonstrate the actual host-agent boundary. |
| C. Build a small retained exercise around current Studio contracts, then call the actual host agent | Reusable input/evidence path **and** direct product learning | **Select.** Uses deployed code's authority boundaries, makes a live claim falsifiable, and leaves room for one bounded repair. |
| D. First stabilize/qualify every previous UI and F2/X3 change | Stronger assurance for unrelated claims | **Do not make a global dependency.** A named failing boundary gets focused handling; unrelated broad suites or six-Chapter repetition do not select S2's next product move. |

## 2. Established baseline — do not rebuild

- [PR #495](https://github.com/ThorStarlord/auteur/pull/495) merged source-format-2 Architecture and Realization context: up to **24** non-Vision working items for Architecture, **12** for Realization, first **1,000 characters** per visible item, full character counts, excerpt flags, appropriate omitted counts/fingerprints, legacy source-format-1 compatibility, and prompt instructions against guessing unseen material.
- [PR #496](https://github.com/ThorStarlord/auteur/pull/496) reconciled the exploratory roadmap. Focused source tests added in #495 were **committed but not executed**. No authentic host-agent manuscript exercise is yet evidenced.
- `src/auteur/beginner/studio_store.py` owns atomic, noncanonical working Canvas items. `studio_architecture.py` and `studio_realization.py` own pending request, working candidate, revisions, freshness and explicit review. `src/auteur/host_agent.py` owns exact request/response binding; the CLI bridges stage and complete operations **without invoking a model itself**.
- [Earlier S2 synthetic report](../product-validation/2026-10-25-s1-s2-agent-creative-probes.md) freezes four ferry paragraphs **P1–P4**, source observations **O1–O5**, two competing interpretations **I1/I2**, and fictional author correction **C1**. It is test *material*, not authentic host output or accepted story.
- Existing Quick Draft `discoveries` → user-checkbox selection → `shape_handoff` carries only selected working details into Beginner shaping. **S3's basic selective carry-forward already exists.** No second Inbox or canon updater is warranted.

**Non-negotiable authority:** original paragraphs remain intact; all inferences stay `WORKING / NOT ACCEPTED`; do not mutate `story_identity.yaml`, `blueprint.yaml`, accepted Chapter files or relations as a side effect; any proposed movement to accepted owners needs an existing **explicit** author action. Do not scrape or import third-party manuscripts.

## 3. Scope, responsibility and source owners

| Responsibility | Owning existing surface | Planned output |
| --- | --- | --- |
| Freeze and stage original fictional source | `scripts/` or a bounded `tests/` helper using `CanvasStore.create/apply` | Disposable source fixtures + manifest; **no** new manuscript database |
| Form bounded source packets | `src/auteur/beginner/studio_architecture.py::_source` and `studio_realization.py::_source_snapshot` | Reuse existing source-format-2; repair only observed failures |
| Execute actual model work | The **active host coding agent** reading a staged `HostAgentRequest` | Raw independent model output and true provider/runtime identification when known |
| Bind output to exact request | `src/auteur/host_agent.py` + the two `complete-file` CLI commands or existing API | Exact request ID/hash, validated working candidate or explicit failure |
| Preserve correction and revision | Existing working Canvas note, `prepare_architecture(..., instruction=...)` and working review | C1-aware revised candidate, no changed P1–P4 text |
| Develop a concrete option if warranted | Existing `prepare_realization(..., focus_ids=...)` | Source-linked, noncanonical Realization candidate |
| Optional prose continuation | Existing Quick Draft, Studio working scene and author selection | Working draft only; no automatic acceptance |
| Reconcile evidence | Existing `docs/product-validation/` and `STATUS.md` when state changes | Authenticated run receipt, claim ceiling, next bounded change |

**No new agents-as-services, agent provider adapter, accepted state enum, retriever, manuscript parser, UI family, or generalized claim-scoring engine.**

## 4. Work package P0 — Reconstruct the execution surface

1. Confirm source identity (`git rev-parse HEAD`, branch/worktree, `git status --short`), actual repository root, Python interpreter, host-agent environment and disposable project directory. Current GitHub source can be inspected through the connector, but **a connector read is not a runnable local checkout**.
2. Read `STATUS.md`, `MISSION.md`, [repository idea frontier](../research/auteur-repository-idea-frontier-2026-10-25.md), [Living Story Studio design](../design/2026-10-09-living-story-studio.md), and the current `host_agent.py` / Studio modules. Do not assume the October 25 commit remains the latest head.
3. Ensure the actual active coding agent can access the **same project filesystem** as the staged request. Do **not** treat a fake `LLMResponse` or a standalone assistant-authored sample as a host-agent execution. If the active coding agent cannot see the request, classify `HOST_AGENT_EXECUTION_UNAVAILABLE`; do not re-label a simulated response as live.
4. Place all mutable scenes and outputs in a fresh disposable project outside the source checkout. Record its temporary path **only in an internal receipt**; never commit author-private filesystem paths or third-party prose.

**Exit:** source and execution identity reported, a disposable project ready, or a named environment blocker. If blocked, independently construct the reusable fixture driver and documentation; stop claiming live execution until that environment exists.

## 5. P1 — Build one durable, small S2 fixture driver

**Implementation shape:** a small, optional script such as `scripts/probe_s2_manuscript_host_agent.py` that reuses `CanvasStore`, `HostAgentRequest`, and existing CLI functions; no new production service. Separate fixture preparation from response completion, so it can run in a local coding-agent session without hidden dependencies.

**Implementation artifact (2026-10-27; correction-integrity follow-up 2026-10-28):** `scripts/probe_s2_manuscript_host_agent.py` supplies the reversible fixture driver with `stage`, `stress`, `correct`, `apply-working-review`, `prepare-realization` and `audit` commands. The focused mechanical test is `tests/test_probe_s2_manuscript_host_agent.py`. **Source committed, not yet executed in a runnable Auteur checkout; no host-agent literary result is claimed.** C1 is withheld from Canvas/request data until the explicit `correct` action; it is not exposed in an initial request or staged file. After the first Architecture completion, `correct` writes the exact C1 as a separate `<SCRATCH_PROJECT>/.auteur/s2_manuscript_probe/correction.json` containing its SHA-256, and creates an author-labelled working note. The audit checks **both** copies; a missing or modified frozen C1 blocks applying the revised working Architecture and preparing manuscript-mode Realization. This file is only synthetic scratch evidence, not an accepted story artifact.

**Execution on a real checkout (use fresh empty disposable project directories outside the repository):**

~~~sh
# Freeze four manuscript paragraphs and stage the actual Architecture request.
PYTHONPATH=src python scripts/probe_s2_manuscript_host_agent.py stage \
  --project /tmp/auteur-s2-primary --canvas s2-primary
PYTHONPATH=src python -m auteur.beginner.studio_architecture \
  --project /tmp/auteur-s2-primary --canvas s2-primary show
# A real coding agent reads the precise request_path reported above, answers
# that system+user contract, and writes RAW architecture JSON in scratch.
PYTHONPATH=src python -m auteur.beginner.studio_architecture \
  --project /tmp/auteur-s2-primary --canvas s2-primary \
  complete-file --candidate /tmp/auteur-s2-primary/architecture-raw.json

# Only after that first valid reply: reveal author correction as WORKING note.
PYTHONPATH=src python scripts/probe_s2_manuscript_host_agent.py correct \
  --project /tmp/auteur-s2-primary --canvas s2-primary
# Coding agent now answers the *new* exact revision request and records raw JSON.
PYTHONPATH=src python -m auteur.beginner.studio_architecture \
  --project /tmp/auteur-s2-primary --canvas s2-primary \
  complete-file --candidate /tmp/auteur-s2-primary/architecture-revision.json
PYTHONPATH=src python scripts/probe_s2_manuscript_host_agent.py apply-working-review \
  --project /tmp/auteur-s2-primary --canvas s2-primary

# Choose an existing engine/theme node ID from that real working candidate.
PYTHONPATH=src python scripts/probe_s2_manuscript_host_agent.py prepare-realization \
  --project /tmp/auteur-s2-primary --canvas s2-primary --focus <EXISTING_NODE_ID>
# A real coding agent handles this exact Realization request and returns raw JSON.
PYTHONPATH=src python -m auteur.beginner.studio_realization \
  --project /tmp/auteur-s2-primary --canvas s2-primary \
  complete-file --candidate /tmp/auteur-s2-primary/realization-raw.json
PYTHONPATH=src python scripts/probe_s2_manuscript_host_agent.py audit \
  --project /tmp/auteur-s2-primary --canvas s2-primary

# Separate 25-item fixture: inspect the actual 24-item/1,000-char boundaries.
PYTHONPATH=src python scripts/probe_s2_manuscript_host_agent.py stress \
  --project /tmp/auteur-s2-stress --canvas s2-stress
~~~

The `complete-file` commands **validate** model-supplied raw candidates; they do not themselves execute a model. Keep raw model output, exact SHA/ID, and truthfully known model/runtime receipt separate. The examples above are an **operator procedure**, not a report that any command succeeded. Tests may be run narrowly with `PYTHONPATH=src python -m pytest -q tests/test_probe_s2_manuscript_host_agent.py` when a checkout is available. Never use a hardcoded candidate from the mechanical test to claim live literary behavior.



### Fixture A — interpret an ambiguous, *complete* excerpt

- Copy the exact original P1–P4 paragraphs from the [prior S2 report](../product-validation/2026-10-25-s1-s2-agent-creative-probes.md) **verbatim** into **four** Canvas working items with stable IDs `s2-p1`, `s2-p2`, `s2-p3`, `s2-p4`. Use source-appropriate working item kinds; do not convert these into accepted Chapters.
- Deliberately omit a premise or authoritative character motive. The aim is to infer possible *abstract* narrative mechanisms from already-written scenes, not invent a settled premise.
- Before running the agent, freeze original UTF-8 bytes and SHA-256 for each paragraph. Record source positions, original word/character counts, and the Canvas revision.
- Keep the correction C1 in a **separate frozen file**, unseen by the model until P3. C1 says Mara did **not** cause or arrange the fire; the brass key opens a **temporary shelter**, not a ledger or valuables store; the traveler's reason for potentially false testimony stays unresolved; P1–P4 must remain untouched.

### Fixture B — incomplete context / omitted material

A second, independent stress fixture should have (i) a scene longer than 1,000 characters whose decisive-looking suffix is unseen by the agent, (ii) a 13th working source beyond Realization's 12-item cutoff, and (iii) a 25th beyond Architecture's 24-item cutoff. Do **not** flood the primary literary exercise with all these distractions.

Confirm that the **staged packet**, not just the source code, reports the correct `content_is_excerpt` / `content_characters`, omitted item counts, source item IDs, hashes and stable request identity. An unseen suffix fingerprint must not become a readable story claim.

### Durable fixture deliverable

- Source text reference, source/manifest hashes, reproducible Canvas setup, exact request path, and a simple command to re-create in a fresh disposable project.
- Never copy personal manuscripts into repository fixtures. Use the existing original four-paragraph synthetic material.
- Prefer code that can be rerun and maintained over a second copy of the S2 explanatory report.

**Exit:** the driver can stage a fresh Canvas and Architecture request with frozen item IDs, without touching Story Identity, Structure, chapters or an author's actual project.

## 6. P2 — Obtain the **actual** host-agent Architecture interpretation

**Exact existing boundary:** `src/auteur/beginner/studio_architecture.py`.

Portable command shape (replace the angle-bracket placeholders with actual scratch locations):

~~~sh
python -m auteur.beginner.studio_architecture \
  --project <SCRATCH_PROJECT> --canvas <CANVAS_ID> prepare
python -m auteur.beginner.studio_architecture \
  --project <SCRATCH_PROJECT> --canvas <CANVAS_ID> show
~~~

1. Read `.auteur/beginner/studio/canvases/<CANVAS_ID>/architecture/requests/<REQUEST_SHA256>/request.json` from the actual scratch project. Verify request schema, role `studio_architecture`, request fingerprint, source-format-2, item IDs, omissions, and unchanged source hashes.
2. The *real* coding agent processes **this exact request**: use the packet's `system` and `user` fields, not a loosely paraphrased assistant instruction. Obtain a raw **ArchitectureCandidate schema-version-2 JSON** response; its node categories express *abstract narrative mechanisms*, not invented canonical cast, scene chronology or prose. Keep a separate source-observation ledger if useful—**do not put an extra ledger field into a strict candidate schema**.
3. Retain the exact raw agent output and metadata known from execution (host environment, model if actually identified, request ID, request SHA-256, source SHA, elapsed time if measured, raw output digest). Report unknown metadata as `UNAVAILABLE`. Do not fabricate timings, judge labels or model IDs.
4. Submit the candidate through the existing exact-request completion bridge:

~~~sh
python -m auteur.beginner.studio_architecture \
  --project <SCRATCH_PROJECT> --canvas <CANVAS_ID> \
  complete-file --candidate <RAW_ARCHITECTURE_JSON>
~~~

5. Inspect the returned working status, candidate and file changes. The CLI's `complete-file` wraps the supplied raw candidate into a bound `HostAgentResponse`; **it does not prove the model ran unless the raw output and truthful external execution receipt are independently retained**.

**Source-grounded content review:**

- Every affirmative source-dependent claim can be traced to `s2-p1` through `s2-p4` (the author-supplied prose), or to an explicitly labelled later author correction.
- O1–O5 from the frozen report are *reference observations*, not mandatory exact wording; conflicting first/second-bell accounts, Neri's *belief* about the coat, the key, and uncertain traveler/Mara chronology must not be silently promoted into unambiguous facts.
- At least two materially different provisional causal interpretations can be discussed **outside the strict candidate** (for example protection/secrecy versus strategic-cover/evidence uncertainty). They should entail different potential decisions/scenes, not merely different titles.
- A visible author's manuscript is not proof of an invented arsonist, clock chronology, stolen ledger, hidden faction or motive. Label unknowns and hypothesis status explicitly.
- A valid candidate with ungrounded claims is a *semantic failure* even if schema validation passes.

**Exit:** authentic source-specific host output + valid working response **or** a concrete classified failure: unavailable host, request/response mismatch, invalid candidate, unsupported source assertion, insufficient excerpt, or runtime/CanvasStore defect. One narrow repair attempt is acceptable; do not enter open-ended retries for aesthetic preference.

## 7. P3 — Simulate the fictional author's correction without rewriting prose

1. After recording the initial raw response, reveal frozen C1. Write it as a **separate author-supplied WORKING note**, e.g. `s2-c1-author-correction`, and/or pass it in a clear `revision_instruction`. Keep P1–P4 byte-for-byte identical.
2. Use the existing **revision** operation, not a canonical Identity edit:

~~~sh
python -m auteur.beginner.studio_architecture \
  --project <SCRATCH_PROJECT> --canvas <CANVAS_ID> \
  prepare --instruction "Revise the working interpretation using the author correction in working note s2-c1-author-correction. Preserve P1-P4 exactly, retract contradicted hypotheses, and identify what is still unknown."
~~~

3. Ask the same real host agent to answer the *new* exact staged request. Validate the raw revision candidate via `complete-file`. Inspect `review_ready` and its working-candidate diff before invoking any explicit apply of the working review through the existing Studio/API owner.
4. Verify the revision rejects "Mara arranged the fire" and "key opens a ledger/valuables room" as settled premises; treats a *shelter key* as coming from **C1**, not as if P1–P4 proved it; and preserves the unresolved traveler motive.
5. Record both first and corrected outputs. Do not overwrite the original response merely because the later interpretation is better.
6. If the author correction can only be supplied by changing a separate source note, that is an **input-authority distinction**, not automatic Story Identity acceptance.

**Exit:** explicit noncanonical source-aware revision with preserved original paragraphs and causal hypotheses altered consistently with C1. Failure belongs first to the source/prompt/revision owners, not to a new "author memory" model.

## 8. P4 — Carry one chosen Architecture focus into Realization

**Prerequisite:** a usable, current **working Architecture candidate** exists, and any P3 review has been explicitly applied to *working* architecture (not accepted story). The copied manuscript must be unchanged; a stale architecture cannot be a reliable focus source.

1. Choose one existing Architecture `engine` or `theme` node ID *from the real candidate*, not a fabricated preselected name. Record why that mechanism is the relevant one.
2. Stage `src/auteur/beginner/studio_realization.py` against the exact scratch Canvas:

~~~sh
python -m auteur.beginner.studio_realization \
  --project <SCRATCH_PROJECT> --canvas <CANVAS_ID> \
  prepare --focus <EXISTING_ARCHITECTURE_NODE_ID>
python -m auteur.beginner.studio_realization \
  --project <SCRATCH_PROJECT> --canvas <CANVAS_ID> show
~~~

3. The real host agent answers that request with a strict `RealizationCandidate` schema-version-1 JSON, including at least one element whose `architecture_refs` contains the selected node. The response should show its *causal function* in a possible concrete scene; citing the right ID on unrelated text is **not** literary fidelity.
4. Submit via `complete-file --candidate <RAW_REALIZATION_JSON>`. Keep the candidate working and trace each inferred event/motive to the observed excerpt versus explicit hypothesis; no acceptance.
5. If useful, copy one proposed scene into the existing editable Studio working scene and preserve `scene_intent` + provenance. **Optional:** stage a Quick Draft request through the existing explicit author action, supply an actual host response, save/reopen, and confirm the prior manuscript and acceptance files remain unchanged.
6. Do **not** turn Quick Draft, a new chapter, or a six-Chapter run into a mandatory S2 precondition. These steps are only warranted if a named failure lies at the Realization→scene or scene→Quick Draft seam.

**Exit:** one author-readable source-linked concrete working possibility or a precise blockage at the existing Realization/scene boundary.

## 9. P5 — Focused falsifiers and smallest warranted repair

The program must be capable of revealing failure, not just demonstrating an attractive example.

| Adversarial check | Correct behavior | First repair owner if observed |
| --- | --- | --- |
| Same-length edit **after** character 1,000 of a staged source | Source hash/freshness changes; stale response cannot replace current working proposal | `studio_architecture._source` / fingerprint, and Realization snapshot |
| Item 13 unavailable to Realization; item 25 unavailable to Architecture | Agent sees **omitted counts**, does not cite or invent omitted content | Existing source projection and request prompt |
| Agent claims the rescuer definitely is Mara, without textual support | Treat as hypothesis or correct attribution to Neri's belief | Existing prompt/mentor guidance and candidate explanation |
| C1 contradicts a prior explanation | Retract incompatible inference; retain P1–P4 and unresolved motive | Existing architecture revision instruction and working note |
| Candidate has a wrong request fingerprint or earlier source | Reject the stale/mismatched completion and preserve prior source | `host_agent.py` + existing Studio completion |
| Selected focus ID is attached to unrelated concrete text | Source reference **integrity** may pass, but semantic case fails review | Existing `studio_realization._SYSTEM` and candidate interpretation |
| Reopen working scene after copying a candidate | Saved prose and original source retained; no surprise acceptance | Existing CanvasStore and Studio scene handoff |
| Source-format-1 saved request is reopened after source-format-2 deployment | Its original fingerprint projection still determines freshness | Existing legacy compatibility branch |
| Real host execution is unavailable | Report `BLOCKED_HOST_EXECUTION`, not a fabricated model run | Environment/access only; continue independent fixture construction |

### Repair policy

- **Build-first:** when an actual failure identifies a small reversible source/prompt/presentation change, implement that retained improvement in the existing owner and add only the relevant focused regression. Do not "experiment then rebuild" the same simple capability.
- **Scope discipline:** one smallest owning layer per fix; do not introduce a new semantic layer, general memory engine or parallel manuscript importer for a prompt/context bug.
- **False-success discipline:** a test that did not run is not green; a structurally valid candidate is not evidence of correct literary interpretation; an unrun regression is not a reason to describe the fix as verified.
- **Test economy:** narrow `pytest -k` / only affected source-unit cases and the smallest adjacent invariant when useful. A targeted served Browser test is warranted only if actual Browser→HTTP→CanvasStore interaction is touched. A full suite or fresh F2 six-Chapter journey is **not** a default merge task.
- **Owner's development instruction:** integrate scoped completed PRs without waiting for unit/evidence tests where GitHub permits; record the explicit owner-directed exception to the ordinary L1 policy on code PRs. Never claim an unexecuted test passed, knowingly merge a demonstrated regression, or treat this as release/deployment approval.

## 10. P6 — Record returned evidence and decide the *next* construction move

Write the actual report at **`docs/product-validation/2026-10-26-s2-authentic-host-agent-manuscript-journey.md`** **only when real work returns**. Use this table or equivalent; the filename is a planned artifact, not evidence that a model has run.

| Required record | Intended meaning |
| --- | --- |
| Source base SHA, branch/head, local root and active host | Which source/runtime was exercised |
| Exact fixture IDs, frozen P1–P4 hashes, C1 hash | What the agent could legitimately observe and when |
| Request role, ID, request hash, context/source SHA | What was actually staged; source-format 2 and omitted scope |
| Raw model candidate and known runtime/model/tool provenance | **Authentic model output** distinct from a fixture |
| Exact completion operation, returned status/exception | Which Auteur boundary actually executed |
| Observations with P1–P4 citations; separate hypotheses | Which facts are supported versus proposed |
| Before/after correction, retracted claims, remaining unknowns | Whether author feedback truly changed the model's position |
| Explicit check of unchanged original prose and accepted artifacts | No accidental canon or author-data loss |
| Focused tests **run** with command/results; tests **not run** marked incomplete | Reproducible claim ceiling |
| User-visible value, observed first material failure, smallest next owner | Concrete product responsibility, not roadmap wish list |

**Possible dispositions:**

- **A — useful independent source-grounded interpretation:** Retain the S2 fixture/receipt, continue normal Connected Creative Thread construction; no new subsystem.
- **B — specific prompt or context failure:** Implement a bounded reversible fix in `studio_architecture`, `studio_realization` or projection presentation. Merge under standing owner instruction, report unfinished execution truthfully, retry the same *failed* case when feasible.
- **C — S2 needs a real missing author operation:** Only after repeated authentic runs, compare a small existing Studio affordance for selecting source/interpretation against a new persistent state distinction. Default to existing owners.
- **D — genuine host/runtime blocker:** Keep the reproducible fixture/driver and execution blocker visible. Continue another *independently warranted* build, but do **not** replace authentic evidence with a synthetic run.
- **E — author-dependent preference or literary satisfaction:** Do not manufacture an agent verdict as the owner's preference. Preserve the working alternatives; the user decides if they wish to choose one.

Only record **NO_MODEL_CHANGE / REAFFIRM**, **RESPONSIBILITY_REVISION**, or a warranted strategy reconsideration when actual evidence supports it. Do not automatically mark S2 complete or promote S4/F3/F4/F5/F7.

## 11. Dependency order, PR boundaries, and stopping conditions

~~~text
G0  Recheck current main + operating context
 |
 +-- B1  Reusable disposable P1-P4/C1 + source-limit fixture driver
 |        (retained capability; independently valuable)
 |
 +-- A1  Authentic Architecture request -> live agent -> exact completion
          |
          +-- A2  Delayed C1 -> working revision -> preserved source
                   |
                   +-- R1  One source-linked Realization focus
                            |
                            +-- Q1  Quick Draft only if author-workflow value warrants
 |
 +-- F1  Smallest actual defect repair, if any (one owner)
 |
 +-- E1  Honest run receipt, source state, next bounded responsibility
~~~

**PR architecture:**

1. **PR A (build/fixture):** self-contained S2 source fixture driver, reproducible setup, focused tests/README if needed; no provider code. Merge after source/diff inspection under the owner's standing merge rule.
2. **PR B (conditional repair):** **only if** an actual failure exists. Touch the minimal source/prompt/working-view owner; regression case reaches that owner. Don't pre-create it just to show velocity.
3. **PR C (evidence / reconciliation):** real run receipt and `STATUS.md` changes after an actual execution; keep it separate from assertions about tests or publication. Docs-only changes need no product-test gate.
4. **No deployment, release, protected policy edit, or automatic Story Identity/Chapter change** in this plan.

**Stop the active S2 package when** a valid source-bound authentic run and correction are recorded, *or* the actual agent execution is demonstrably unavailable after the fixture is ready and no independent build remains warranted, *or* an owner-reserved decision is truly needed. Do **not** keep expanding to S4–S6 merely because those tasks are named in the exploration map.

## 12. Follow-on roadmap selection — not an automatic backlog

| Candidate | Selection trigger | Correct next unit of work |
| --- | --- | --- |
| **S1 — Story Opportunity/Premise Fitness** | A real no-premise author workflow lacks causally distinct, source-labelled directions | Reuse documented protocols + current Architecture host, then one bounded prompt/context improvement |
| **S3 — selective discoveries** | An actual prose change cannot be carried as **only one selected** working discovery through the existing Quick Draft/Beginner path | Repair the existing discovery→shape handoff; **do not** build another queue |
| **S4 / F3 — multi-thread relevant memory** | A qualified extended Book exposes irrelevant or prematurely revealed context | One Chapter-N included/omitted source trace before any new retrieval architecture |
| **S5 / F4 — belief vs. truth/reveal** | A genuine mystery scene cannot express reader/protagonist/world-knowledge distinction using present Realization/provenance | An exact unexpressible operation + small source-linked diagnostic; ontology only after evidence |
| **S6 / F5 — mid-Book change** | A revision invalidates unrelated saved prose or loses author choices | Changed/untouched artifact preview and minimum-scope repair within current impact owners |
| **F2/X3** | Existing issue #318's complete author/reopen frontier has new decision-changing execution evidence | Continue that frontier on its own authority, not as a declaration that S2 has already validated it |

**Recommended next execution instruction to the coding agent:** Start at `G0` and `B1`, choose the available real host execution surface, stage fixture A, execute the exact Architecture request, delay C1 until the first raw candidate has been recorded, then make the smallest warranted repair. Proceed without repeated owner prompts, but stop at a genuine external or protected decision boundary. Record PR heads and results exactly; merge scoped development PRs without waiting for the test suite under the owner's standing instruction.


## 13. Execution return — 2026-10-27 (real work, no fabricated agent response)

The user delegated implementation of this plan without further approvals. The bounded P1 source-construction action was performed via GitHub connector and merged as [PR #498](https://github.com/ThorStarlord/auteur/pull/498), merge `58e4b42fcca88cb624d0fa48f0f027e71b280bf2`. This entry reports what actually happened and **must not be mistaken for completion of the full S2 journey**.

| Stage | Actual state | Executed evidence and limitation |
| --- | --- | --- |
| P0 source/environment | **Partial / external blocker** | GitHub connector read/write succeeded; container's `git ls-remote https://github.com/ThorStarlord/auteur.git HEAD` failed DNS and no runnable full checkout was found. The existing `/mnt/data` Auteur files were isolated excerpts/UI fixtures, not source checkout. |
| P1 retained reusable driver | **Source built and merged; runtime unverified** | `scripts/probe_s2_manuscript_host_agent.py` created with `stage`, `stress`, `correct`, `apply-working-review`, `prepare-realization` and `audit`. Four focused mechanical pytest cases added. Source and changed paths inspected; **no tests run**, no actual scratch Canvas created here. |
| P2 authentic initial agent Architecture reply | **BLOCKED before stage/host execution** | No actual file-backed `HostAgentRequest` was produced in an Auteur runtime, and no real raw coding-agent candidate was obtained. The script alone cannot fulfill this. |
| P3 delayed correction | **Not executed** | C1 can be revealed by the driver's explicit command only after P2 completion; no first response exists here. The correction text was committed as an isolated fixture constant and was **not** injected into a story project. |
| P4 focused Story Realization | **Not executed** | A current source-bound Architecture candidate and a model/host reply are prerequisites. The driver exposes the existing prepare operation but does not invent a completed candidate. |
| P5 smallest observed repair | **No product defect yet demonstrated** | The checkout/host gap is an **environment dependency**, not a model or Auteur bug. No conditional product-source fix is warranted from this blocker alone. |
| P6 evidence reconciliation | **Completed for returned evidence only** | `STATUS.md` updated with the P1 merge and P2–P4 unavailable ceilings. `docs/product-validation/2026-10-26-s2-authentic-host-agent-manuscript-journey.md` was **not** manufactured, because no authentic host run returned evidence. |

**Next autonomous boundary:** obtain a genuine shared filesystem with the active coding agent and run the exact P1 staging command already documented in section 5. Then obtain a real P2 candidate, use the existing `complete-file` validation, reveal C1, and proceed within the original P3/P4 scope. Do not re-plan S2, re-create the fixture, claim a synthetic response as real, or promote S4–S6 merely to avoid the blocker.

**Standing owner instruction:** merge scoped completed PRs without waiting for unit/evidence tests while preserving that an unexecuted check is **not** passing evidence. No release, deployment, accepted story mutation, Level-4 thesis change or cross-repository work was authorized.
