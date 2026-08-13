# A2 Solution Discovery — Surface F3 elicitation in the author-decision surface

> Cycle: `discovery/f3-elicitation` (worktree `H:/GithubRepositories/auteur-f3-elicitation`,
> base = canonical origin/main `2ee0081` = merged PR #69 + #70). Direction A2 selected by
> the human (2026-08-13) from the standing-envelope candidate list: "Surface F3 in the
> decision workspace". Reuse/extension of shipped F3 behavior — in-envelope, no escalation
> triggers. Zero production change in this discovery.

## Survey finding (evidence)

The `decision` CLI has TWO separate surfaces:

1. **Workspace surface** — `decision status|list|inspect|next|...`: assembles decisions
   from impact findings + convergence targets via `DecisionWorkspaceService`; requires a
   `.auteur` project marker; uses its own `auteur.decision.models.AuthorDecision`. It does
   NOT read `author_decisions/*.yaml` artifacts (probe: `decision list` errors "Not an
   Auteur project" on an artifact-only project).
2. **Artifact surface** — `decision create|accept|evaluate|view|elicit`: operates directly
   on `author_decisions/<id>.yaml` via `auteur.author_decisions` persistence; NO `.auteur`
   requirement. This is where F3 lives and where the author inspects decisions.

**Gap:** `decision view` prints `Goal significance (authored, decision-scoped): None` when
unsettled, but gives the author no indication that F3 elicitation is available for this
decision, what it would do, or how to invoke it. The capability is effectively invisible
from the surface the author actually uses.

## Discovery question (delegated)

> **What is the smallest credible mechanism that surfaces F3 elicitation availability in
> the author-decision surface where the author already inspects decisions, without
> inventing new semantics?**

## Mechanism families compared

### M1 — Elicitation-availability hint in `decision view`
Extend `handle_view` to render, in text and JSON, whether this decision is
elicitation-eligible and what the author can do:
- **eligible + unsettled** (`goal_significance` absent, composed consequences exist):
  show the `decision elicit` invocation as the next available action;
- **settled** (`goal_significance` present): state significance is declared (F1) — no
  elicit hint;
- **not eligible** (no direction / no composed consequences): honest "no composed
  consequences to elicit against" (mirrors the elicit render's own honest surface).
- Reuses: existing `build_report`, the same eligibility logic the `elicit` handler
  already implies (direction present → composed combos exist), F1 field state.
- Zero new schema, zero new state, deterministic, testable in text + JSON.

### M2 — Surface in workspace `status`/`list`/`inspect`
Show elicitation availability from the workspace surface.
- **Rejected:** the workspace model is assembled from impact/convergence and does not
  hold the artifacts F3 operates on (survey probe). Bridging the two models would be a
  new cross-surface integration (substantially larger, and arguably a new mechanism)
  — beyond "surface F3", risks inventing semantics the envelope says not to invent.

### M3 — New `decision status`-style summary of artifact significance
A new subcommand listing artifact significance state across the project.
- **Rejected as larger than needed:** M1 covers the author's inspection moment; a new
  aggregate command adds surface without an observed need (no author has hit "I can't
  see which decisions are unsettled across the project").

## Selection (delegated product authority)

**M1 — elicitation-availability hint in `decision view`.** Smallest credible mechanism:
the author inspects a decision with `view`; the surface tells them elicitation is
available, what it does, and how to invoke it — without new schema, new state, or
cross-surface integration. Escalation check: none of the envelope triggers hit (no
weights/ranking/LLM/ontology/3+ goals/prose inference/F1 conflict).

**Claim language:** the F3 interaction pattern is **human-demonstrated**; M1 as the
surfacing mechanism and its qualification are **agent-selected/validated**; post-merge
behavior will be **observed** in use.
