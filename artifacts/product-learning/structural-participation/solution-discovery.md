# Solution Discovery — Structural Participation / Accepted-Decision Enactment

> Cycle: `discovery/structural-participation` (worktree `H:/GithubRepositories/auteur-enactment-discovery`,
> base = canonical `origin/main @ c968a747` incl. PR #75). Zero production change.
> Solution Discovery only — stop before Implementation Design; new persistent canonical
> participation/footprint semantics or automatic application is a human product-selection
> point.

## Demonstrated limitation (behavioral, application phase)

> **An accepted `cut`/`keep` operation can identify its chosen member and its durable
> structural referent, but current canonical story state cannot express the operation's
> effect. The referent has identity without sufficient participation/footprint semantics,
> so enactment would require prohibited inference.**

Experiment (Condition A): decision + referent, no enactment → `structure diagnose` shows
no sign of the referent or the cut. Condition B: no canonical field expresses "cut
signe_marriage" — `subplot_budget` is a bare count, threads are generic, the referent
links to neither.

## First falsification — M1: existing F2 `carrier_refs` + Blueprint primitives

Question: **with all mappings explicitly authored, can `cut`/`keep` be represented safely
through ordinary canonical edits?**

Verified against shipped source (`origin/main @ c968a747`):

1. **Nothing downstream consumes `structural_referents` or the referent's `carrier_refs`.**
   Grep across `src/`: both are read only by the `author_decisions` CLI (view/accept/
   promote) and the anchor context builder — **not** by `structure diagnose` /
   `analyze_structure` / planning / portfolio / review / simulation. The referent is an
   *addressability* artifact, not a participation/footprint source.
2. **`StoryThread` has no participation/status field.** Fields: `name`, `type`,
   `want/resistance/conflict/stakes/change`, `supports_main_by`, `thematic_function`.
   No `active`/`included`/`participation`/`status` anywhere in the thread or referent
   models (grep confirms zero hits).
3. **`subplot_budget` is a bare `int`** — says how many, not which; decrementing it cannot
   name the cut referent.
4. **Generic threads** ("Secondary Struggle", "Relationship Echo", "Secondary Subplot 3")
   are main-thread support functions, not the subplots being cut. Even an explicit
   carrier mapping from `signe_marriage` to a thread would (a) be read by nothing
   downstream, and (b) be semantically wrong (a thread is not a subplot).

**M1 falsified:** existing primitives + explicit carrier mapping cannot express the
operation's effect — the mapping would be unread by downstream reasoning, and no
participation/status exists to change.

## Participation vs footprint — the discovery's central question

| Concept | Meaning | Present today? |
|---|---|---|
| **IDENTITY** | "this structural thing is Signe's marriage" | ✅ PR #75 |
| **PARTICIPATION** | "is this structural thing currently part of the story?" | ❌ no field |
| **FOOTPRINT** | "what canonical structures realize this thing?" | ❌ no link read downstream |

The behavioral result shows the demonstrated need is at least **participation** (the
referent exists but its current inclusion is inexpressible). Whether **footprint** is also
required (to realize `cut` destructively) is undetermined — participation alone may
suffice if downstream reasoning only needs "not currently participating."

## Mechanism families compared

### M1 — Existing primitives only (carrier_refs + threads + subplot_budget)
**Falsified above.** No downstream consumer reads the mapping; no status field exists;
thread semantics mismatch subplots.

### M2 — Durable referent + explicit participation state
Keep identity separate from current presence: the referent stays forever; a separate
explicit authored participation fact ("currently participating: yes/no", or similar —
vocabulary deliberately not preselected) changes under `cut`/`keep` without deleting
identity. Directly fits "cut ≠ destroy identity". Smallest persistent semantic increment;
downstream reasoning could consume participation without destructive thread rewriting.
**Smallest surviving candidate on evidence.**

### M3 — Separate explicit application state (provenance-bearing overlay)
Keep the Blueprint referent descriptive; store enactment separately (`target:
structural_referents[...]`, `operation: cut`) as provenance-labeled application context
that downstream reasoning consumes alongside canonical structure. Reversible and
identity-preserving, but creates two sources of truth and every future consumer must
understand the overlay. Larger integration surface than M2.

### M4 — Richer canonical footprint / first-class subplot entity
Give the referent explicit structural linkage (carriers, budget participation) or make it
a full subplot-like entity. Largest semantic commitment; must beat M2/M3 on evidence.

## Comparison dimensions

| Family | Downstream addressability | Identity preserved on cut | Integration cost | Dual-source risk | Ontology beyond need |
|---|---|---|---|---|---|
| M1 existing primitives | none (unread) | — | low | no | — (falsified) |
| M2 participation state | yes (if consumers read it) | yes | low-medium | no | small new fact |
| M3 application overlay | yes (overlay-aware consumers) | yes | medium-high | **yes** | separate state |
| M4 richer footprint | yes | yes | high | no | substantial |

## Verdict (agent-validated, delegated authority — subject to human product selection)

**NEW APPLICATION SEMANTICS EARNED.** The demonstrated need is **participation** —
whether the durable referent currently participates — and the smallest surviving
mechanism is **M2: an explicit per-referent participation state, kept separate from
durable identity**, so `cut` changes participation without destroying identity. M1 is
falsified; M3's dual-source-of-truth and M4's ontology breadth are larger than the
demonstrated need. Whether footprint (M4-style linkage) is also required depends on
whether participation alone satisfies downstream reasoning — to be determined by the
next validation, not preselected.

**Escalation gate (binding):** M2 introduces new persistent canonical participation
semantics → this is a **human product-selection point**. Stop before Implementation
Design. If the human selects M2, the design must not preselect vocabulary
(active/inactive vs included/excluded vs cut/kept); the smallest semantics that survive
the controls must be chosen by design evidence.

## Controls required for the next step (design/validation)

1. Cut one referent — identity remains durable.
2. Keep one referent — no redundant manufactured state.
3. Two referents share one carrier thread — cutting one must not delete the shared
   carrier.
4. One referent has several carriers — no one-to-one assumption.
5. No carrier mapping — fail closed; no name/prose inference.
6. Already-canonical target — no duplicate application representation.
7. Open/unresolved decision — no participation change.
8. `chosen` absent — no application.
9. F1 significance stays decision-local.
10. Existing Blueprint without structural referents remains valid.
11. Revision control — a cut referent remains addressable for later restoration.

## Claim language

- **human-demonstrated:** outcome needs a stable referent (PR #74/#75) and the enactment
  gap (application-phase behavioral test).
- **agent-validated:** this discovery (M1 falsified; M2 smallest; escalation identified).
- **post-merge observed:** n/a (nothing built).
