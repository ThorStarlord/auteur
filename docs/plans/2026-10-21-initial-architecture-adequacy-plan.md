# Initial Narrative Architecture Adequacy — Adversarial Investigation Plan

Status: **planning; W1/W2 source review recorded in the companion adversarial
findings report**. This document authorizes no prompt change, schema migration,
freshness change, new generation or UI work. Each of those passes through a
decision gate (§9).

Base: `main` at `3dd2b83a`. Historical evidence:
[Tidal Archive forensic report](../reviews/2026-10-21-tidal-archive-initial-architecture-forensics.md)
(cited as **FR**; this plan does not repeat it).

## 1. The question

> Can a coding agent use Auteur's narrative knowledge to turn an author's
> Story Vision into a coherent, useful initial Narrative Architecture?

The question splits into three parts. Each needs different evidence.

| Part | Question | A failure here looks like |
|---|---|---|
| Availability | Does Auteur possess the narrative-design knowledge? | The needed distinction exists in no Auteur source |
| Delivery | Does the creative agent receive the relevant knowledge in usable form? | The knowledge exists but is absent, compressed or misleading in what the agent sees |
| Application | Does the agent use it to build working mechanisms and relationships? | The knowledge was delivered, but the result classifies rather than designs |

A distinction missing from the prompt is **not** a defect by itself. Agents
know many narrative concepts from general training. An omission matters only
if it changes the architecture.

**Scope:** Story Vision → creative-agent context → `ArchitectureCandidate` →
validation → graph projection.

**Deferred:** alternatives, additional author inputs, manual graph editing,
agent suggestions, revision as a product feature, Story Realization, prose,
mentorship, human UX. The historical *revised* candidate is used only as
evidence. The revision feature is not under evaluation.

## 2. Two agents, two contexts

| | Development agent | Creative host agent |
|---|---|---|
| Role | Changes Auteur's code and docs | Fulfils a Studio `HostAgentRequest` and returns candidate JSON |
| Guided by | `CLAUDE.md`, `AGENTS.md`, repository docs | The request's `system` and `user` messages, **plus whatever its host environment adds** |
| Controlled by Auteur | Yes, through repository files | Only the request. The host environment is outside Auteur's control. |

Consequences the plan must examine (W1):

- **The request is the only guaranteed channel.** A guidance document helps
  the creative agent only if it reaches the request or, unreliably, the host
  environment.
- **The host environment varies, and may also hold Auteur's developer
  instructions.** The handoff recipe runs the creative agent "inside a
  coding-agent environment that can read the local project". If that
  environment is an Auteur checkout, the agent may also load `CLAUDE.md` and
  `AGENTS.md`. These are developer instructions: they can help, contradict the
  request, or make results irreproducible. Historically this is **unknown**
  (FR §1).
- **Developer docs don't reach the creative agent on their own.** Documenting
  a concept for development agents does not deliver it to creative agents.
  Separately, today's prompt-only edits do not invalidate saved work, while
  changes to the delivered context do (§7).
- **Evidence for any generation must record the creative agent's environment:**
  the working directory, whether repository files were loaded, the model and
  the runtime.

## 3. Owner decisions

Status: **D** = decided; **P** = provisional (revisit on evidence);
**U** = unknown fact (investigate; never assume).

| # | Decision | Status |
|---|---|---|
| A1 | Goal: both prove the approach is viable and find improvements | D |
| A2 | Audience: the owner and future contributors; an architectural assessment, not product validation | D |
| A3 | The development agent judges, using §4 with quoted evidence; the owner may override consequential conclusions | D |
| A4 | Verdicts are graded and qualitative, never numeric; state whether the evidence supports the initial-generation milestone | D |
| B5 | Start with Tidal Archive; make the method reusable; no broad campaign | D |
| B6 | Review both the original historical generation (diagnostic) and the current contract (the target); never conflate them | D |
| B7 | Input is one meaningful Story Vision, plus working notes where supported; accepted Identity is authoritative when present and is never required | D |
| C8 | Current state of the Windows project | U |
| C9 | The original agent's session log and model identity | U |
| C10 | Whether the original creative agent had repository access | U |
| C11 | Analyse the exact Vision in a trusted local workspace; a summary supports only provisional fidelity judgments | D |
| C12 | Candidate prose is needed, through local analysis or authorized sharing | D |
| D13 | Recorded owner view: the original graph was "crude but somewhat functional"; ontology delivery is the main suspect. Invent no further criticism. | D |
| D14 | The revision exists; its quality is unjudged. Do not assume it is better. | D |
| D15 | Derive standards from the Vision and Auteur's contracts; never judge against an invented ideal architecture | D |
| E16 | Six dimensions (§4); prioritize fidelity, causal coherence and generativity | D |
| E17 | Prefer connected mechanisms over decorative coverage; appropriate breadth depends on the Vision | D |
| E18 | Ensemble, contemplative, atmosphere-led, cyclical, nonlinear and non-agent architectures are legitimate | D |
| F19 | `StoryIdentity.central_engine` is read as a possible whole-story summary, not a mandate for one dominant mechanism. FR R13 stays open. Identity is unchanged. | P |
| F20 | **Settled principle:** mechanisms need not be driven by intentional actors; no character-like want is required. **Open representation:** how ontology, prompts and schemas express agent and non-agent mechanisms. | D |
| F21 | **Settled principle:** genres need not have independent engines; mechanisms may serve several genres, and a genre may introduce, constrain, express, organize or modify mechanisms. A genre-specific renewable mechanism remains valid when warranted. **Open representation:** how ontology, prompts and schemas express these functions and shared mechanisms. | D |
| G22 | No arbitrary context-size limit. Aim for sufficient, relevant, coherent, auditable knowledge. Compare curated, selective-structured and hybrid delivery on merit. | D |
| G23 | Schema changes are acceptable for demonstrated representational problems, with migration and compatibility planned | D |
| G24 | A bounded current-context initial generation is allowed when it answers a consequential question that history cannot. It does not need a prior historical defect. | D |
| G25 | Deliverable: this versionable plan | D |
| FP1 | Separate request identity, author-source freshness, and generation-guidance provenance/compatibility (§7); exact compatibility transitions remain open | P |

## 4. Qualitative assessment criteria (reusable for any Story Vision)

**Dimensions.** These are perspectives, not required fields. Weighting:

| Weight | Dimension | Question |
|---|---|---|
| High | Intent fidelity | Does it preserve what the author wanted, including constraints and unknowns? |
| High | Causal coherence | Do the mechanisms create pressures, consequences and changes that connect meaningfully? |
| High | Generativity | Can the design produce varied, meaningful consequences without arbitrary invention? |
| Normal | Structural organization | Are the relationships among mechanisms, genre functions, thematic mechanisms and phases comprehensible? |
| Normal | Reader experience | Do the intended experiences arise from the design, not just appear as labels? |
| Normal | Abstraction | Does it avoid inventing characters, places and events? |
| Cross-cutting | Ontological consistency | Are concepts used in ways Auteur's contracts recognize, without confusing kinds? |
| Cross-cutting | Representation adequacy | Did the schema let the agent say what it meant, or force distortion? |

**Rules for judging:**

1. **Classification is not design.** An architecture that only labels the
   Vision's genres, themes and emotions has classified it. A design explains
   how they work together.
2. **No formulas.** Mechanisms need no fixed number of developments. Phases
   need not change which mechanism dominates. Mechanisms need no actor. There
   is no preferred style.
3. **Connectivity is not coherence.** A dense graph can be shallow. Read what
   the links *say*.
4. **An unused concept is not a failure.** The Vision may not need it.
5. **Evidence:** every significant judgment quotes candidate IDs and text,
   and the Vision where available.
6. **Adversarial challenge:** for each significant judgment, record the
   strongest counter-reading and why it does or does not hold. This guards
   against an agent grading an agent.
7. **Attribution:** list every contributing cause (availability, delivery,
   ontology, schema, generation behaviour, presentation, legitimate
   uncertainty). Allow interacting causes and say when attribution is
   unresolved.

**Verdict format.** For each dimension: strengths, weaknesses, examples,
uncertainty and implications. Then an overall statement: does the evidence
support initial-generation adequacy (Level 2), contradict it, or leave it
undetermined?

## 5. Current findings

### Confirmed (from source; their *effect on outputs* is unestablished)

- **CF1 — The original request delivered no narrative ontology** (FR §3–4).
- **CF2 — The current develop request delivers only part of the knowledge.**
  - Delivered: composition choice (single center, primary with layers,
    ensemble); separation of author commitments from agent proposals; one
    compressed "craft propagation" chain.
  - Not stated: what "renewable" means; engine vs genre; reversal vs
    revelation; structural vs causal hierarchy; theme tested vs theme named
    (only "themes manifest through narrative change"); reader emotion vs
    character emotion (only "reader-directed effects").
  - These are delivery facts. Whether they affect output is H1.
- **CF3 — Every genre contract must carry an engine description.**
  `GenreContract.narrative_engine` is a required non-empty string, and the
  prompt asks contracts for "renewable narrative engines". This requires an
  engine *description* per contract, not an independent engine per genre.
  Whether it biases agents toward duplicate per-genre engines, or leaves the
  link between a contract's engine and the engine nodes ambiguous, is H2.
- **CF4 — The prompt's mechanism vocabulary leans toward actors.** It speaks
  of "causal ownership" and "actor action patterns". Nothing forbids non-agent
  mechanisms, and Phase F has `pressure_system` and `causal_owner: ensemble`.
  Classified as a **delivery concern**, H3.
- **CF5 — `parent_id` has no defined meaning** (decomposition, subordination
  or grouping) in the prompt, schema or docs, and the graph does not draw it.
- **CF6 — Several kinds of relationship lack definitions:**
  - three unreconciled "governing" notions (contract role, phase
    participation, `engine_hierarchy`);
  - free-text `ArchitectureLink.function` alongside typed
    `GenreInteraction.kind`;
  - a single phase `order` for both chronology and disclosure;
  - provenance only on emotion targets.
- **CF7 — Identity requires a single `central_engine`** alongside an optional
  `ensemble` preference (FR R13; decision F19).
- **CF8 — Freshness behaviour** (§7). Fingerprints recompute guidance from
  *current code* when a response arrives or a review is applied, so pending
  requests are not bound to the context they were prepared with. One
  "stale" status covers both guidance and creative-source changes, and the
  rejection message names the author's source in both cases.

### Open hypotheses

- **H1** — Some CF2 omissions measurably weaken architectures; others are
  covered by the agent's general knowledge.
- **H2** — CF3's wording biases agents toward independent per-genre engines,
  or leaves the contract–engine relationship ambiguous.
- **H3** — CF4's wording pushes non-agent mechanisms into actor framings.
- **H4** — Undefined `parent_id` (CF5) produces inconsistent hierarchy use.
- **H5** — The Tidal Archive graph looked "crude" mainly because of how it
  was drawn (FR C4), not its content. The two can coexist.
- **H6** — The original creative agent had repository or conversational
  context beyond the request (C10).

## 6. Workstreams

These are independent sources of evidence. A structural counterexample can
establish a limitation without a real historical defect.

### W1 — Knowledge-delivery adequacy (P0; source review complete, output effect unknown)

See the [adversarial findings review](../reviews/2026-10-21-initial-narrative-architecture-adversarial-review.md) for the needs-to-request crosswalk, delivery-strategy comparison, and freshness implications. Whether any delivery gap changes a real candidate remains unresolved pending W3/W4 evidence.

### W2 — Ontology and `ArchitectureCandidate` representational adequacy (P0; counterexample sweep complete, narrative quality untested)

See the companion review for X1–X6 paper candidates, validator results, representational limits, ambiguities that conventions can address, and the reasons no schema change is yet warranted. These probes do not establish narrative quality.

### W3 — Historical Tidal Archive forensics (P1; needs the original files)

- **Questions:** What did the original creation and the later revision
  actually produce, judged by §4? Which CF and H items appear? What
  additional context did the agent have?
- **Method:**
  1. Capture with `scripts/tidal_forensic_capture.py`.
  2. Analyse locally or through authorized sharing (C11, C12).
  3. Recover the agent's session log where possible (C9, C10).
  4. Compare the original and revised candidates, keeping in mind that the
     revision also had the previous candidate and a targeted instruction.
  5. Recompute what the pre-#471 graph drew, for H5.
- **Output:** a forensic judgment with quoted examples, attribution per §4
  rule 7, and the H items confirmed, weakened or unresolved.
- **Success criterion:** a stable (VALID) capture containing the original
  develop request and its response candidate, correctly associated with each
  other.

### W4 — Evidence for current-context initial generation (P1)

- **Questions:**
  - Does today's develop request produce an architecture that meets §4 for a
    real Vision?
  - Do CF3 and CF4 matter in practice?
  - Does the host environment affect the result?
- **Method:**
  1. Define each fresh-generation question before running anything, and
     record the creative agent's environment (§2).
  2. Run one generation per condition, on Tidal Archive's Vision or a
     counterexample Vision, judged qualitatively.
  3. Admit a run only if W1–W3 leave a consequential question that history
     cannot answer (G24).
- **Not:** a repeat of the generic E2E demonstration, statistical
  benchmarking, or clean-room requirements.

### W5 — Presentation (P2, constrained)

Make minor recommendations only, and only where W3 or W4 shows the graph
misrepresenting the candidate (for example, direction or hierarchy
invisible). No general layout or hierarchy redesign in this milestone.

### 6.1 Counterexample set (paper Visions; never generated)

| ID | Form | What it stresses |
|---|---|---|
| X1 | Ensemble: institutional pressure, intimate loyalty, environmental change | Co-governing mechanisms, non-agent causes, CF3, CF7 |
| X2 | Contemplative ritual recurrence | No conventional engine; CF3; generativity without escalation |
| X3 | Cyclical return with changing meaning | Phases versus progression; theme tested by repetition |
| X4 | Nonlinear disclosure (consequence first) | Revelation vs reversal; single `order` (CF6) |
| X5 | Atmosphere-led place story | Genre that expresses rather than drives; reader experience from aesthetics |
| X6 | Multi-genre with one shared mechanism | F21; contract–engine relationship (CF3, CF6) |

## 7. Freshness as a design consideration

**Current contract** (CF8; `host_agent.py` and `studio_architecture.py`):

| Responsibility/input | Current representation | Effect of a change |
|---|---|---|
| Exact request identity | `request_sha256` hashes the canonical request body: schema, candidate ID, role, system prompt, user message and settings. It excludes `created_at` and the derived `request_id`. | Binds a response to the exact generation payload; it is not a source-freshness policy. |
| Story Vision, working items/connections, previous candidate (working sources) | Included in `source_sha256` through `working_context` | A changed source makes a completed candidate stale or rejects a pending response. |
| Accepted `story_identity.yaml` | Projected into `narrative_design_context`, then included in `source_sha256` | A changed accepted commitment also changes the same combined digest. |
| `_DESIGN_PRINCIPLES` and preference vocabulary (developer design context) | Recomputed into `narrative_design_context` when checking `source_sha256` | A guidance-context edit is treated like a changed author source; a pending request prepared under the old context can be rejected with an author-source message. |
| `_SYSTEM` (developer prompt) | Included in `request_sha256`; excluded from `source_sha256` recomputation | A response is tied to its original prompt, but a later `_SYSTEM` edit alone does not stale a saved candidate or block a pending response. |
| Runtime/model and guidance compatibility | Runtime/model are recorded on the response; no separate compatibility status is modeled | Exact prompt provenance can be recovered through the request, but compatibility with current guidance is not evaluated. |
| Pre-context legacy requests | Preserve their original working-context fingerprint treatment | No explicit guidance provenance/compatibility claim is available. |

**Provisional policy (FP1; design recommendation, not implemented):**

1. Keep exact request identity separate from freshness: a response must match
   its saved request, including the original system and user messages/settings.
2. Freshness of author-controlled sources must be checked independently.
   Changes to the Story Vision or accepted Identity must continue to block
   applying a proposal built from the old source state; they must never be
   silently overwritten by a generated candidate.
3. Record generation-guidance provenance and assess compatibility separately.
   A pending response remains attributable to the instructions it received;
   changed guidance must not be mislabeled as changed author input. Define an
   explicit compatibility outcome before deciding whether a proposal made
   under older guidance may be applied or must be regenerated.
4. Preserve completed working artifacts and their provenance across guidance
   changes. Historical or legacy artifacts with incomplete provenance remain
   readable but have unknown compatibility rather than an invented status.

**Conflicts to reconcile before any implementation:**

- Current completion/apply checks recompute developer design context as part of
  the same `source_sha256` used for creative-source freshness.
- Accepted Identity is author material but sits inside that combined digest.
- `_SYSTEM` is protected by exact request identity, but not compared for
  compatibility with current guidance.
- Existing tests pin that a design-principle change stales a saved candidate
  while an `_SYSTEM`-only edit does not; revise them only with a deliberate
  compatibility contract and legacy reopening behavior.

Any change needs legacy-compatible reopening, its own decision gate (G4), and
updated tests. The cost of each W1 delivery design is assessed against this
policy.

## 8. Evidence requirements

| Evidence | Feeds | Source | Status |
|---|---|---|---|
| Auteur knowledge sources | W1, W2 | Repository | Available |
| Current request text | W1 | Generated from `main` | Available |
| Original request, response and candidate; revision; versions | W3 | Windows capture | Pending (C8) |
| Exact Story Vision | W3 fidelity, W4 | Owner's machine | Pending; a summary allows provisional judgment only |
| Agent session log and model | W3 attribution, H6 | Owner's host agent | Unknown (C9) |
| Fresh-generation outputs with recorded environment | W4 | Bounded run | Only through G5 |

**What the Windows capture contributes:** the W3 evidence; whether CF2–CF5
appear in a real artifact; H5 and H6; and the Vision against which W4 can be
compared. It is not needed for W1 or W2, nor for planning.

## 9. Implementation decision gates

| Gate | Change | Admissible when |
|---|---|---|
| G1 | Delivery change (prompt or context) | W1 identifies a need that is absent or misleading, **and** W2, W3 or W4 shows that it matters, or a counterexample shows harmful steering. Freshness cost assessed (§7). |
| G2 | Canonical ontology or doc amendment | W2 shows a concept missing or contradictory in the sources. F20/F21 principles are settled; their ontology/prompt/schema representation remains open. F19 remains provisional and owner-reserved. |
| G3 | Schema change | W2 shows expression impossible or ambiguous in a way that matters, and no convention suffices; migration and compatibility planned (G23) |
| G4 | Freshness change | The policy in §7 is reconciled with the existing contract and tests |
| G5 | Bounded fresh generation | A consequential question is defined that history cannot answer; the environment will be recorded |
| G6 | Presentation fix | Demonstrated misrepresentation, and the fix is minor |

## 10. Uncertainty, and what would change the next implementation decision

| Uncertain | Evidence that would decide it | Effect on the next decision |
|---|---|---|
| Whether CF2 omissions matter (H1) | W3 or W4 artifacts handling, or confusing, those distinctions | Confusion → G1 for those rows only. Handled well → no delivery change; focus moves to W2. |
| H2 (genre engine bias) | W2's X6 validator probe accepts two genre contracts describing one shared mechanism, but cannot test agent behavior; W3/W4 candidates would show whether engines are duplicated or ignored | Confirmed in output → consider G1 wording; G3 typed reference only if the untyped convention fails (FR §7.2) |
| H3 (actor bias) | Non-agent Visions (X1, X2) forced into actor framings | Confirmed → consider G1 wording; consider G2 only if source ontology cannot represent the settled non-agent principle (F20). |
| H4 (hierarchy) | Inconsistent `parent_id` use | Convention in the request first; G3 only if a convention cannot carry it |
| H5 (presentation) | Candidate connected in JSON but drawn scattered | G6 minor fix; weakens the case for G1 |
| H6 (hidden context) | The agent's session log | If the original agent read the ontology itself, the original result says little about delivery, and W4 gains weight |
| R13 / F19 | An ensemble story whose single summary distorts it | Owner Identity decision, outside this milestone |
| FP1 compatibility transitions in §7 | A decision table for pending, completed and legacy proposals, tested against author-source changes | Determines the freshness implementation boundary (G4); prompt-only delivery work can proceed separately if it does not alter hashed design context. |

**Next evidence steps:** W1/W2 findings and validator probes are recorded in
the companion adversarial review. They establish delivery gaps and schema
representational limits, but do not show that a generated candidate was harmed
or that the current prompt misuses them. W3 historical Tidal Archive forensics
and W4 current-context initial-generation evidence are independent: pursue W3
if the private project is located, and run W4 without waiting for that recovery.
Do not implement a delivery or schema change from paper probes alone. See the
review's freshness analysis before changing hashed design context.
