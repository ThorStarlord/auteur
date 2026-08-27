# Global Map Architecture Value V1 — Condition Specification (A/B/C)

## Research question (preregistered)

> What explicit narrative architecture does Auteur need to make materially better long-horizon creative decisions than a prompt/context-only system and current Repeated Map/Focus, without unacceptable maintenance cost, false precision, stale structure, or authority confusion?

V1 tests **internal representational value** (does richer architecture improve reasoning), not production UI quality or human usability.

---

## Conditions (frozen)

### A — Prompt / Context-Only Baseline

**What generator receives:**
- Frozen narrative sources (see `source-manifest.md`): `series_direction.yaml`, relevant `book_*_direction.yaml` and `book_*_realization.yaml` for that probe's horizon, and derived Canonical State summary as plain context (same values C uses, but as unstructured story context, not as explicit architecture).
- Current planning intent / situation (plain sentence from `book_4_planning_intent.yaml` / `r1-r3-history.yaml` planning_intents).
- Exact creative question + bounded option list (from `decision-probes.md`).
- Authority reminder: recommendation is non-authoritative; do not invent unsupported facts.

**What it does NOT receive:**
- No explicit ledger (`candidate-architecture-ledger.md`), no disposition tags (`active`/`reactivated`/`superseded` etc.), no grouping, no `why-now` derivations, no `CurrentStateEvidence` keys.

**Prompt stance:** Strongest reasonable ordinary-LLM-with-story-context baseline. Do not cripple A. Provide clear, well-structured story context (same facts, just not pre-related). Example prompt frame (frozen):

```
You are a story consultant for the series Archive of Lies (ongoing, pressure: ...).
Accepted history through Book N: [plain summaries of directions + realizations].
Current state: [key=value sentences].
Planning intent: [intent sentence].
Question: [exact question].
Options: [option_id: label — summary — tradeoff].
Task: Analyze tradeoffs, cite which past facts matter now and why, recommend one option (or note none is viable), and explain what you excluded. Recommendation is not canon.
```

### B — Current Auteur (Shipped)

**What B truthfully uses (no modification):**
- At frozen revision `3cc4975...`, B's capability is `repeated_map_focus.py` `select_repeated_continuity` (`_DERIVATION_VERSION=repeated-map-focus-v2-r1`) + `decision_seeds.yaml` seeds via `RepeatedBookPlanningContext` / `NextDecisionProposal` shapes. No finite extent, no universal relevance engine.
- For each probe, B's context is built from the same accepted history snapshot via the real code path: `AcceptedHistorySnapshot` (series + books + realizations + explicitly_resolved ids) → `select_repeated_continuity(history, planning_intent, current_state)` → `RepeatedBookPlanningContext` ( `entries` = active/reactivated, `history_entries` = others, `groups` = pressure groups, `why_matters_now` per entry, `generated_from` refs, `derivation_version` ).

**Neutral adapter (required because B does not itself generate final recommendation prose):**

```
current Auteur context output (entries + groups + CurrentStateEvidence + why-now + generated_from)
        ↓
same decision-generation prompt used by A and C
```

Adapter spec (frozen, must not smuggle C):
- Input: B's `entries`/`groups`/`history_entries` formatted as a compact Map (group summaries + entry `summary` + `why_matters_now` + source `entry_id` only — e.g., `founding-record@1` — no ledger categories beyond what B emits).
- Prompt: identical system/role, same creative question/options, same output contract as A/C; only the context block differs (B's derived Map vs A's plain story context vs C's ledger-derived Map).
- Tooling: no extra retrieval; fresh context per run.
- Records: run manifest notes `condition=B`, `adapter: b-context-to-prompt v1` (no architecture enrichment).

**What B proves:** Whether current qualified Map/Focus (activations, resolutions, supersessions, reactivation, grouping, stale/incompatible rejection) already captures the needed architecture.

### C — Architecture-Rich Auteur (Experimental)

**What generator receives:**
- Same frozen narrative sources as A/B, **plus** the research ledger `candidate-architecture-ledger.md` as explicit architecture:

```
experimental explicit architecture (33 items: DIR-*, ST-*, REL-*, FUT-*)
        ↓
Global Map representation (whole-story projection: What is this story / Where going / trajectories / established / unresolved / relationships — per ledger section D)
        ↓
decision-relevant projection (Decision Map = ledger filtered to probe's active/reactivated + current-state + trigger-relevant + grouped, per disposition rules)
        ↓
same creative decision task (identical question/options/contract)
```

- No production Global Map implementation required; research Markdown/structured data is sufficient.
- Ledger is pre-built golden representation, not LLM-extracted (isolates *value of representation* from *extraction quality*). See information-parity rule.

**Categories allowed (only where source supports):** Series/Book direction, character trajectories (investigator change lines from DIR-B* `change` fields), relationship trajectories (e.g., council–archive–witness), threads/arcs (`contested-history` pressure), commitments, setups/payoffs (ST-F1→ST-F3, ST-F2→P03), causal dependencies (REL-05, REL-07), current state (ST-F5/F6), unresolved (FUT-*), future intent (DIR-INT*), thematic tensions (REL-10), reveal/knowledge relationships (archive as only chain). All from ledger.

---

## Information-parity rule (critical)

- All three conditions derive from **same frozen narrative source material** (`source-manifest.md`).
- C **may** contain explicit derived relationships (e.g., REL-04 supersession, REL-06 reactivation, REL-09 grouping, REL-07 incompatibility) that A would have to infer from raw sources — that is the treatment.
- Every C architectural statement is traceable to frozen source rows; ledger column `source` lists exact file + transition. Unsupported fact → exclude or mark `INTERPRETIVE` with provenance. No unavailable narrative facts.
- Advantage from *organization* is valid; advantage from *extra facts* is invalid and triggers invalidation (see `evaluation-rubric.md`).

## Isolate representation from extraction

V1 does **not** test whether an LLM can automatically construct architecture. The Condition C ledger is **hand-constructed, source-faithful, golden** research data. If even golden representation shows little value, investing in automatic extraction is premature. Later V2 can test extraction fidelity separately.

## Control variables (frozen generation policy)

For A/B/C within same probe:

- Same `generator_provider/model/version` (to be recorded at execution, not yet chosen; placeholder `MODEL_TBD` frozen as “same across conditions”)
- Same system-level decision role
- Same current creative question & output contract (see `decision-probes.md`)
- Same `max_output_tokens` (e.g., 1200, frozen at execution)
- Same sampling: `temperature: 0.2`, `top_p: 1.0` (frozen; deterministic seed if supported else explicit “no seed”)
- Same tool availability: **none** (no search, no retrieval) unless treatment requires it — none does for V1
- Fresh context per run; no conversational carry-over
- Same provider latency/cost accounting; input/output hashes recorded per `run-manifest-template.md`

Any deviation is a protocol deviation and must be logged; material deviations invalidate per `evaluation-rubric.md`.

## Repetition / variance

- Default V1: **3 independent generations per condition per probe** = 3 × 3 × 5 = **45 outputs** (unless model is genuinely deterministic under frozen settings, then 1 per condition per probe = 15).
- Do not treat one lucky response as evidence.
- Opaque run IDs per generation (e.g., `X17`, `Q04`) — blind labels, not condition-revealing.
- Cost estimate to be recorded before execution; reduction in reps after seeing results is forbidden without preregistered V2 amendment.

## Blind evaluation

- Outputs exported under randomized opaque labels (e.g., `X17`, `Q04`, `M22`) — never `A`/`B`/`C`/`architecture-rich`.
- Condition mapping (`opaque_id → {A,B,C}`) kept in separate file (`run-manifest` private column `hidden_condition_id`) not shared with evaluator.
- Expected winner, probe must-not-miss, and rubric hidden from evaluator until after blind judgments (see `evaluation-rubric.md`).
- If LLM evaluator later used, prefer distinct model from generator; preserve human adjudication path for close/surprising results.

## Probe packet reproducibility

Each condition packet is defined by:
- `source_revision = 3cc4975...` (source-manifest)
- Probe snapshot (probe ID → history horizon)
- Condition ledger slice (A: plain context; B: `RepeatedBookPlanningContext` JSON; C: Decision Map markdown)
- Shared `question + options` block
- Shared `output_contract` block
- Frozen `generation_policy` block

No execution in this task; packets are specifications for later execution.
