# Simulated Author / Coding-Agent UI Stress Test — Auteur

**Recorded:** 2026-10-25  
**Source:** `ThorStarlord/auteur` `main@a8a090580e98cd5f6dcee1645375e2867e644350`; comparison with **open draft** [PR #484](https://github.com/ThorStarlord/auteur/pull/484) at `2f606d54ae7f71db34f9244ada8cf30a8cb3460d`.  
**Parent analysis:** [UI Strategic Evolution](../../research/auteur-ui-strategic-evolution-2026-10-24.md), based on [UI Possibility Landscape](../../research/auteur-ui-possibility-landscape.md).  
**Role:** decision-relevant synthetic evidence / adverse contract probes. **Not** human user research, a real Auteur runtime pass, release qualification, or automated product authorization.  
**Strategic effect:** **NO_MODEL_CHANGE / REAFFIRM PATH A**, with more specific integration responsibilities and explicit counterevidence conditions.

## 1. Question and method

**Question:** Can simulated author scenarios and a coding-agent adversarial review resolve current UI strategy uncertainties *without* needing the real owner to answer more creative questions?

**Yes, for mechanical constraints and some strategic eliminations; not for subjective author experience.**

This session had access to exact repository source through the GitHub connector but **could not clone the repository in the isolated execution container** (network DNS lookup of GitHub failed). Consequently the executable portion used **isolated, transparently source-derived Pydantic contract replicas and workflow-state functions** rather than importing Auteur production modules or running its HTTP server and Chromium.

Two exercise types were completed:

1. **Contract and flow stress:** 12 explicit executable isolated assertions, using artificially constructed Realization candidates. Compared the current `_assert_refs` rule with the precise additional focus-coverage rule on open PR #484, copied a Realization scene into working-note state, and checked the scene-premise/scene-intent eligibility gate. All 12 harness assertions passed **about the expected source-derived behavior**; this is **not** 12 passing Auteur integration tests. Four cases reproduced undesirable behavior in the replica.
2. **Coding-agent creative divergence:** this assistant authored two *working, noncanonical* ArchitectureCandidate-v2-style proposals for one synthetic Story Vision and checked both through an isolated schema replica. The two use different sustaining engines rather than superficial relabeling. This was **not** a call to an independent host coding agent, an actual Auteur response envelope, production schema validation, or a live generation/quality evaluation.

We separately challenged UI hypotheses as a **simulated author** (not real humans) across premise-free entry, spatial reasoning, divergent whole-story alternatives, scene writing, and Book re-entry. A simulated author's tastes and task durations are **not observations**.

### Synthetic creative context

> A welcoming lighthouse conservatory shelters families during storms; hope and belonging matter, but protection has a difficult, initially unknown cost.

The context deliberately leaves the cost **unknown**. Any causal explanation not supplied by that sentence must remain explicitly **agent-proposed**, not retrospectively attributed to the author. No named cast, accepted story, or private project was used.

The two constructed alternatives were:

| Alternative | Renewable mechanism | Distinct story choice | Limit |
| --- | --- | --- | --- |
| **A: reciprocal care** | Each storm renews mutual-aid decisions, social debt, and unequal burdens | What does the community owe one another, and who bears costs? | Keeps the protection cost materially unknown; scene quality and generative runway untested |
| **B: memory tithe** | Storm protection requires recurring sacrifice of memories; the loss transforms consent and belonging | Is protection worthwhile if it removes memories that make belonging meaningful? | Speculative cost was **invented as an agent proposal**, not present in author Vision; could violate the intended genre if mistakenly accepted |

Each synthetic v2-style candidate validated in the isolated replica with **7 abstract nodes, 6 directed links, 3 phases, 2 genre contracts, and 2 reader-emotion targets**. They do **not** establish independent model performance or production-schema correctness. Both remain competing provisional interpretations.

**Strategic implication:** The alternative whole-story directions are causally different, so a future complete-candidate comparison UI has a plausible use. However, `studio_architecture.py` exposes a singular `current.json` candidate and staged revision reviews; that is not yet evidence of side-by-side whole-story option management. Repeated source-bound request/response files may retain history, but history retention is not automatically a usable alternative-atlas UI. PATH C stays conditional, not selected.

## 2. Executed isolated contract-probe ledger

Each result below is a **PASS for the harness's predicted assertion**, not proof that the underlying product behavior is desirable.

| Probe | Adversarial scenario | Isolated observed outcome | Interpretation |
| --- | --- | --- | --- |
| **S01** | Selected `care_engine`, candidate references `care_engine` | Current and draft checks accept | Expected positive case |
| **S02** | Selected `care_engine`, source-valid proposal references only `secret_cost` | **Current check accepts off-focus** | Current semantic relevance gap: global reference integrity is insufficient |
| **S03** | Same off-focus output under draft PR #484 rule | Draft rule rejects with selected-focus coverage error | A narrowly targeted repair is proposed; not qualified/merged |
| **S04** | Two focuses selected, response covers only one | **Current check accepts incomplete coverage** | A second illustration of the same missing focus constraint |
| **S05** | Same multi-focus output under draft rule | Draft rule rejects | Proposed repair covers each requested focus |
| **S06** | Whole-story Realization without selected focus | Both checks accept | Fix should not restrict legitimate global work |
| **S07** | Model returns invented non-existent Architecture reference | Current check rejects | Existing basic reference integrity is effective |
| **S08** | Model attempts to smuggle `accepted=true` into RealizationCandidate | Strict schema rejects extra field | No such direct acceptance key in the candidate contract |
| **S09** | Story Vision changes after a prepared request | Source digest changes | Supports the documented stale-response guard; not an actual HTTP/reload test |
| **S10** | Copy an agent-proposed scene to working canvas, then request Quick Draft | **Missing scene premise and intent blocks generation** | Realization->scene copy is not automatically draft-ready |
| **S11** | Click *Use my existing scene notes as intent* | Intent is filled but premise remains missing; appended source metadata also enters the editable intent | A recovery affordance exists, but source-to-prose transition is not a single clean author action |
| **S12** | Supply explicit author premise and cleaned scene intent | Eligibility gate permits request | Existing system can proceed; no prose model was actually called |

**Current source anchors:**

- `src/auteur/beginner/studio_realization.py`: `_source_snapshot` validates focus IDs (approximately lines 105–122), `_assert_refs` on `main` checks only references against all existing architecture nodes (approximately lines 204–209), `complete_realization` enforces request/response SHA and source freshness (approximately lines 212–245). The unmerged draft PR #484 adds `set(focus_ids).issubset(covered)`.
- `src/auteur/beginner/browser/studio.js`: focused Realization request includes `focus_ids` (approximately lines 400–414); `copyRealization` copies description and `Architecture refs`/`Origin` labels into **freeform content** but does not populate `scene_premise`/`scene_intent` (approximately lines 1379–1396); `generateScene` requires both fields (approximately lines 2131–2147); clicking `use-scene-as-intent` copies the entire scene text into the editable intent (approximately lines 2535–2543).
- `src/auteur/beginner/browser/studio.html`: the Advanced host handoff, Architecture/Realization separation, editable scene, and explicit unaccepted-state descriptions are visible in source.
- `src/auteur/beginner/studio_architecture.py`: `_candidate` reads the singular `current.json` (around line 230); history/request/review paths remain distinct from currently presented candidate. The schema's v2 abstract Architecture forbids instantiating concrete character/relationship nodes; Story Realization owns concrete proposals.
- Existing tests include `tests/test_beginner_studio_realization.py`, `tests/test_beginner_studio_architecture_to_realization_browser.py`, `tests/test_beginner_studio_reentry_browser.py`. They are evidence of intended and previously reported integration behavior; **none was executed in this session**.

## 3. Simulated author stress across four strategic paths

The table distinguishes **source-grounded prediction** from **unanswered preference**.

| Synthetic author task | Candidate path | Grounded finding / simulated prediction | Confidence boundary |
| --- | --- | --- | --- |
| Author starts from atmosphere without knowing a plot | A + possible P1 Intent Constellation | Studio already accepts premise-optional Story Vision and working fragments. An extra 'start from mood' tool would risk duplicating what exists. | Strong on entry capability; no evidence that a spatial constellation improves story quality |
| Author picks an abstract engine and asks for a concrete scene | **A Connected Creative Thread** | Focus reaches request; candidate can ignore it on main; copied scene is not Quick-Draft-ready without extra fields. | Strong source-backed specific gaps; actual user difficulty unmeasured |
| Author asks to revise multiple abstract mechanisms while preserving stable IDs | A | Source-bound requests and staged review exist; propagation of one sentence through graph, Realization and prose remains an integration question. | Existing components proven at source; complete live creative chain untested |
| Author explores 12 characters, three arcs, multiple changing relationships | B Spatial Reasoning | Existing focus/facet, semantic trail, graph search and Book scope offer real substrates; likely future information-density pressure. | No live stress measurement, no demonstrated X4 failure; path not yet selected |
| Author keeps two incompatible whole-story hypotheses | C Parallel Architecture | Two distinct working designs can be formulated in isolated contract form; current presented candidate slot is singular and there is no verified first-class whole-candidate comparison UI. | Plausible candidate-identity/product gap; actual demand and cheapest presentation unknown |
| Author drafts uninterrupted, then returns weeks later | D Quiet/Re-entry | Focus writing, local selected-view/caret preservation, Book orientation already exist; source-backed 'why I was considering this' may not exist if no working question/decision was recorded. | Strong on existing source features; no simulated preference proves an improved quiet/re-entry mode |
| Author sees a causal projection and must decide whether it is true | B or C | Existing counterfactual subsystem distinguishes baseline, hypothetical deltas and assumptions; status/provenance must remain visible. | Code/documentation contract supports protection; human interpretation untested |
| Author wants physical setting as vivid character | B / P5 | Working places and Realization locations can carry concrete setting; abstract v2 Architecture cannot instantiate invented locations under its contract. | Source-bound layer ownership; no evidence a geographical map is the right UI |

### Adversarial evaluation of the synthetic alternative architectures

- **Creative-divergence win:** A and B are meaningfully different in *causal ownership*, not merely mood palettes. A renews social obligations; B renews information loss and consent dilemmas. An agent can propose both without having the user fill in genre/plot questionnaires.
- **Authority challenge:** B invents a supernatural cost that the author did not declare. It is valid *only as an explicitly marked candidate*. Choosing B from the artist's aesthetic alone would be a preference-sensitive owner decision, not something the simulation authorizes.
- **Presentation challenge:** The ability to write and schema-check two candidate JSON objects is not proof that multiple large graphs are the easiest way to compare them. A two-paragraph engine/reader-promise comparison might be more effective.
- **Literary quality challenge:** An abstract repeated mechanism does not prove convincing characters, distinctive scene situations, emotionally effective prose, or a sustained Book. Both candidates would require Story Realization and author-quality evaluation before a stronger claim.

## 4. Questions answered, unanswered, and actively falsified

**Answered mechanically / high source confidence:**

1. A focused request **can** specify a selected abstract node.
2. On current main, a structurally valid response **can** omit that focus; the open PR #484 source guard covers this narrow case.
3. Existing source/freshness and working-versus-accepted distinctions are materially protective at inspected boundaries.
4. Copying a Realization element into working scene content does **not** populate the fields required by the scene-generation request.
5. A native side-by-side UI for complete working architectures is **not established** by the singular current-candidate and decision-portfolio interfaces.

**Answered only as plausible hypotheses / medium to low confidence:**

- Source-linked Intent Constellation may benefit someone who begins with atmosphere, but default text entry may already be sufficient.
- Focused causal/temporal views may help a dense Book, but X4 graph navigation failure has not been demonstrated.
- A visually rich reader-emotion timeline can express *intent*, but no automated predictor proves actual reader feeling.
- A 'return to my creative question' view may outperform saved graph focus only when that prior question has been recorded accurately.

**Not answerable without actual use or new execution access:**

- Which workflow *feels* fastest, clearest, or emotionally engaging to real writers?
- Whether the connected agent-first path works correctly with the **actual host agent** on a fresh disposable project, including generation, revision, scene, and re-entry.
- Whether two alternatives are worth retaining as full architectural versions versus concise comparative synopses for a particular author.
- The literary merit of generated prose, the perceived coherence of an entire Book, or widespread UX/release readiness.

**Falsified simplifications:**

- 'Focus ID is passed, therefore focus is honored' is false on current main.
- 'Copy Realization scene, therefore Quick Draft is ready' is false when premise and intent are absent.
- 'Valid graph candidate, therefore high-quality story' is unsupported.
- 'A simulated author prefers it, therefore users prefer it' is invalid.

## 5. Strategic reconciliation and responsibility

**Previous Level-3 recommendation:** PATH A, Connected Creative Thread, while respecting current F2/X3 frontier.  
**New returned evidence:** two distinct **source-grounded integration gaps** (selected-focus coverage and scene-intent/Quick-Draft continuity); two synthetic, meaningfully different architecture models; valid existing protective checks; no new user preference evidence.  
**Strategic effect:** **NO_MODEL_CHANGE / REAFFIRM**, with a more precise nearest engineering responsibility.

**Recommended ordered work under separate ordinary authorization and access:**

1. **Qualify** the already open draft [PR #484](https://github.com/ThorStarlord/auteur/pull/484) against the real repository, with focused, multi-focus and empty-focus cases. Avoid independently implementing a competing duplicate focus guard. A draft's source code is not a merged or qualified repair.
2. **Trace one Realization scene -> Quick Draft roundtrip** in a disposable Browser/HTTP setup, preserving exact source and author intent. Distinguish freeform note content from the exact **author-authored** premise/scene intention, which the existing Quick Draft contract requires. Determine whether controlled, editable prefilling from saved author inputs would avoid repeated manual meaning without guessing canon.
3. If the seam is confirmed, **reversibly build** the smallest existing-owner composition change; ensure status truth, source/revision freshness, accessible alternative entry, and no automatic acceptance. Do not add new global agent orchestration or story storage merely for smoother UI.
4. Keep **PATH B** and **PATH C** available when real X4/multiple-candidate demand exists, and **PATH D** when re-entry/drafting work exhibits lost intent or distraction. Do not implement all candidate modes from the exploration.
5. **Stop or lower the claim** if execution still lacks the owner's private environment, real repository checkout, or host coding agent. Local contract replicas are not substitute evidence for a complete end-to-end run.

**Why a bounded repair is more warranted than more brainstorming:** The off-focus and scene-intent discontinuities can be located to existing behavior; another round of UI metaphors will not remove them. **Why a sweeping redesign is less warranted:** no observed author task has shown an irreducible deficit in the current semantic architecture or selected graph-first default.

## 6. Evidence provenance and reproduction limits

- GitHub source and [PR #484](https://github.com/ThorStarlord/auteur/pull/484) were read without modifying application code.
- Isolated standalone scripts were executed with Python 3.13 and Pydantic 2.13.5. The first generated a JSON ledger for 12 contract-state cases; the second generated two abstract synthetic candidate structures checked through a recreated subset of ArchitectureCandidate-v2 constraints.
- The **12/12 pass** figure is about the correctness of the *isolated scenario assertions*, **not** product success, not an execution of original Auteur's validators, not a passing Chromium suite, and not a test of a real coding-agent host.
- Actual repository checkout was unavailable because the execution container could not resolve GitHub; no production import, request submission, fixture writing to the owner's project, or clean-room release qualification occurred.
- No human participant, empirical preference survey, external LLM comparison, model-independent coding-agent run, or private W4 project was used.
- The landscape and strategic synthesis remain separate authorities: evidence constrains what is reasonable to build, but this file does not promote a candidate into `NOW` or authorize a merge/release.

**Conclusion:** A simulated coding-agent review can materially narrow the next UX responsibility without interviewing the owner. It cannot justify confident claims about the experience real authors will prefer. **PATH A remains the warranted integration direction, not because simulation proves users like it, but because specific compositional gaps exist in today's graph/agent/writing chain while broader alternatives remain untriggered.**
