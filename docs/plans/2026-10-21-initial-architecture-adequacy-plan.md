# Initial Narrative Architecture Adequacy — Adversarial Investigation Plan

Status: **planning**. This document authorizes no prompt change, schema
migration, freshness change, new generation or UI work. Each of those passes
through a decision gate (§9).

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
| F20 | Mechanisms may be non-agent: environment, institutions, information, ritual, social structure. No character-like want is imposed. Check whether Phase F already covers this before any ontology change. | P |
| F21 | A genre may introduce, constrain, modify, express or organize mechanisms. A mechanism may serve several genres. A genre-specific renewable mechanism is legitimate when warranted. No fixed one-to-one or one-for-all rule. | P |
| G22 | No arbitrary context-size limit. Aim for sufficient, relevant, coherent, auditable knowledge. Compare curated, selective-structured and hybrid delivery on merit. | D |
| G23 | Schema changes are acceptable for demonstrated representational problems, with migration and compatibility planned | D |
| G24 | A bounded current-context initial generation is allowed when it answers a consequential question that history cannot. It does not need a prior historical defect. | D |
| G25 | Deliverable: this versionable plan | D |
| H1 | Freshness policy (§7) | P |

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

### W1 — Knowledge-delivery adequacy (P0; starts now)

- **Questions:**
  - Which knowledge does initial generation *need*?
  - What does the current request deliver (CF2)?
  - What can the host environment add (§2)?
  - Where is the delivered wording misleading rather than merely silent
    (CF3, CF4)?
- **Method:**
  1. Build a needs inventory from Auteur's sources (FR §2): conceptual
     distinctions, relationships, composition choices, epistemic rules,
     generativity.
  2. Map each need to the request text.
  3. Challenge the request with the counterexample set (§6.1): does any
     wording steer an agent away from a legitimate form?
  4. Compare delivery designs on relevance, coherence, auditability,
     maintainability and freshness cost (§7): curated principles (today),
     selective structured loading, hybrid.
- **Output:** a delivery-adequacy table (need, delivered, misleading, effect
  unknown) and a ranked delivery design.

### W2 — Ontology and `ArchitectureCandidate` representational adequacy (P0; starts now)

- **Questions:** Can the ontology and schema express every legitimate form
  (E18) without distortion? Does each field have a single interpretation?
- **Method:**
  1. For each counterexample, write a paper candidate within the current
     schema.
  2. Record where expression is impossible, possible only by convention, or
     ambiguous.
  3. Examine CF3, CF5, CF6 and CF7, plus whether Phase F's vocabulary already
     covers F20 and F21.
- **Output:** per assumption, one of: *adequate*; *adequate with a stated
  convention* (and where the convention must live: request or docs); or
  *change needed*, with the shape of the change, migration and compatibility
  (G23). FR §7.2 already scopes one case: a typed contract → engine reference.

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

**Current contract** (CF8; `studio_architecture.py`):

| Input | In the fingerprint? | Effect of a change |
|---|---|---|
| Story Vision and working items/links (author) | Yes | Saved candidate shown "stale"; pending response rejected |
| Accepted `story_identity.yaml` (author) | Yes, inside `narrative_design_context` | Same |
| `_DESIGN_PRINCIPLES`, preference vocabulary (developer guidance) | Yes, recomputed from current code | Same, including a *pending* request prepared under older guidance; the message blames the author's source |
| `_SYSTEM` (developer guidance) | No | None. Prompt edits never invalidate anything. |
| Pre-context (legacy) requests | Working context only | Unchanged legacy treatment |

**Provisional policy (H1 decision; planning assumption only):**

1. Changes to **author creative sources** invalidate the affected dependent
   proposals.
2. **Pending requests** stay bound to the generation context they were
   prepared with. A response to such a request is validated against that
   request's own recorded context, not today's code.
3. **Existing working artifacts** stay readable after guidance changes, with
   their generation provenance (prompt and context versions) retained.
4. Distinguish **outdated guidance** from **changed creative sources**
   instead of one "stale" status.

**Conflicts to reconcile before any implementation:**

- Policy 2 conflicts with recomputation at completion and apply.
- Policy 4 conflicts with the single combined digest.
- Accepted Identity is author material but sits inside the guidance digest.
- Tests currently pin "a principle change stales a saved candidate" and
  "`_SYSTEM` does not".

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
| G2 | Canonical ontology or doc amendment | W2 shows a concept missing or contradictory in the sources; F19–F21 promoted from provisional |
| G3 | Schema change | W2 shows expression impossible or ambiguous in a way that matters, and no convention suffices; migration and compatibility planned (G23) |
| G4 | Freshness change | The policy in §7 is reconciled with the existing contract and tests |
| G5 | Bounded fresh generation | A consequential question is defined that history cannot answer; the environment will be recorded |
| G6 | Presentation fix | Demonstrated misrepresentation, and the fix is minor |

## 10. Uncertainty, and what would change the next implementation decision

| Uncertain | Evidence that would decide it | Effect on the next decision |
|---|---|---|
| Whether CF2 omissions matter (H1) | W3 or W4 artifacts handling, or confusing, those distinctions | Confusion → G1 for those rows only. Handled well → no delivery change; focus moves to W2. |
| H2 (genre engine bias) | Duplicated per-genre engines, or contracts ignoring engine nodes, in W3 or W4; a W2 paper test of X2, X5 or X6 | Confirmed → G1 wording first; G3 typed reference only if the untyped convention fails (FR §7.2) |
| H3 (actor bias) | Non-agent Visions (X1, X2) forced into actor framings | Confirmed → G1 wording; G2 if Phase F is insufficient (F20) |
| H4 (hierarchy) | Inconsistent `parent_id` use | Convention in the request first; G3 only if a convention cannot carry it |
| H5 (presentation) | Candidate connected in JSON but drawn scattered | G6 minor fix; weakens the case for G1 |
| H6 (hidden context) | The agent's session log | If the original agent read the ontology itself, the original result says little about delivery, and W4 gains weight |
| R13 / F19 | An ensemble story whose single summary distorts it | Owner Identity decision, outside this milestone |
| §7 conflicts | Reconciliation analysis | Decides whether G1 must wait for G4 |

**Most likely next implementation decision:** after W1 and W2 (no capture
needed), a G1 wording change for CF3 and CF4, gated on the counterexample
evidence, with its freshness cost reconciled under G4. W3 or W4 evidence of
H1 would widen it, and evidence of good handling would shrink it to nothing.
