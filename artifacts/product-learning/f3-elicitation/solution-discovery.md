# F3 Solution Discovery — Elicitation for Genuinely Unsettled Cross-Goal Significance

> Cycle: `discovery/f3-elicitation` (worktree `H:/GithubRepositories/auteur-f3-elicitation`,
> base = canonical origin/main `a21bb43` = merged PR #68; local main NOT used). Zero
> production change; no schema; no code. Human-demonstrated value hypothesis (zero-code
> interaction test @ `fd12ced` packet + `ed02cd8` verbatim reactions): consequence-focused
> elicitation helped the author discover a preference; continue-undecided is a required
> non-coercive outcome; provisional Auteur position added no distinct value. Delegated
> product authority (human brief 2026-08-11): agent selects the mechanism; the record
> attributes selection to delegated authority, not human approval.

## Problem (solution-free, per the human's test)

The shipped product (PR #68) supports deterministic cross-goal consequence composition,
authored decision-local relative significance (`ordered`), and intentional non-precedence
(`unranked`). It intentionally does NOT represent:

> **"I genuinely don't know which of these accepted goals matters more in this decision."**

The human interaction test established the interaction pattern that helps:

```text
abstract priority question        -> did not help
consequence-focused elicitation   -> helped the author DISCOVER a preference
continue-undecided                -> required non-coercive outcome (safety/epistemic honesty)
provisional Auteur position (F4)  -> no distinct discovery value; more directional pressure
```

## Discovery question (delegated)

> **What is the smallest production mechanism that implements the human-demonstrated
> consequence-focused elicitation interaction safely, reusing the shipped surface, and
> ends only in valid author states?**

## Binding constraints (from the delegation brief)

1. The mechanism must help a genuinely unsettled author examine the **concrete
   consequences already known by Auteur** — never an abstract goal ranking.
2. Valid outcomes only:
   - author discovers A > B → may explicitly record **existing F1 `ordered`**;
   - author discovers intentional non-precedence → may explicitly record **existing F1
     `unranked`**;
   - author still does not know → **remains genuinely undecided** (valid; no field).
3. Never silently convert uncertainty into non-precedence.
4. Never infer author significance from prose.
5. Never manufacture a ranking or recommendation.
6. Prefer reuse: existing F1 `goal_significance` is the likely destination; **no parallel
   preference state** unless F1 provably cannot represent the result.

## Mechanism families compared

### M1 — Deterministic CLI elicitation subcommand (`decision elicit`)

A read-then-record command: renders the already-composed loss statements (verbatim
`nature_consequence` findings from `build_consequences` — no new inference) grouped as
"if you cut X, you remove ... / if you cut Y, you remove ...", presents the
consequence-focused question in view of those losses, then records the author's explicit
outcome into the existing F1 field (or leaves it absent).

- Reuses: composed findings, F1 `GoalSignificance` + fail-closed validation,
  `persistence.atomic_write_yaml`, CLI subcommand pattern.
- Zero new schema; no new state; no inference; no recommendation.
- Record is an explicit author action (`--record ordered REF1 REF2` / `--record unranked`
  / `--record undecided` = no write), auditable in the authored YAML.
- Deterministic and testable end-to-end (goldens for the render; fail-closed for record).

### M2 — Passive probe/observation in the existing report

Adds an observation to the consequence report that restates the elicitation question.
- Weak: a report is passive; it cannot record the outcome. The demonstrated value was the
  interaction (author answers and the result is preserved), not a static prompt.
- Rejected: does not implement the interaction; adds report noise.

### M3 — Interactive multi-turn prompt session

A multi-turn conversational flow (ask → react → re-ask).
- The human evidence does not show multi-turn value: ONE well-framed consequence-focused
  question did the work. More machinery, harder to test deterministically, higher surface
  for coercion.
- Rejected: over-built for the demonstrated interaction.

### M4 — Proposal artifact flow (proposal YAML → apply)

Generates a proposal artifact the author later applies to set `goal_significance`.
- Matches the "prefer proposal artifacts" pattern in general, but F1's field is authored
  YAML; a direct explicit record command is the natural minimal mutation. A proposal
  cycle adds a file + apply step for no added safety (the record is already explicit +
  atomic + validated).
- Rejected as larger than necessary for this slice (may matter if elicitation ever needs
  review before recording, which is out of scope).

## Selection (delegated product authority)

**M1 — `decision elicit` subcommand**, smallest credible mechanism that implements the
demonstrated interaction:

- **Renders** the composed loss statements from the shipped consequence surface
  (verbatim, deterministic, no prose parsing, no ranking).
- **Asks** the consequence-focused question in view of those losses (the interaction that
  human-demonstrated value).
- **Records** only the author's explicit outcome into the existing F1 field
  (`ordered` / `unranked`), or leaves the field absent for continue-undecided.
- Escalation check: none of the delegation brief's triggers are hit (no weights, no
  preference machinery, no LLM, no canonical priority, no new ontology, no 3+ goals, no
  prose inference, no parallel state, no unknown→unranked collapse).

**Claim language:** the interaction pattern is **human-demonstrated** (frozen F3 case);
M1 as the production mechanism and its qualification are **agent-selected/validated**
under delegated product authority; post-merge behavior will be **observed** in use.

## Escalation check (recorded)

No escalation condition was encountered during this discovery. The selected mechanism
fits entirely within the delegated envelope.
