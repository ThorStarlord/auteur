# Accepted-Outcome Solution Discovery

> Cycle: `discovery/accepted-outcome` (worktree `H:/GithubRepositories/auteur-outcome-discovery`,
> base = canonical `origin/main @ d9926b1`). Zero production change in this discovery.
> Upstream of both parked campaigns (Accepted-Decision Downstream; Decision Revision &
> Supersession). Evidence chain: static map (chosen outcome not in schema/acceptance)
> + human-value reaction test (verbatim, below).

## Problem (solution-free)

Auteur preserves the deliberation that leads to a decision — question, alternatives,
what they concern, structural consequences, significance, elicitation, acceptance — but
**not which alternative the author ultimately chose.** `accept` records acceptance of the
deliberation artifact and its resolved context, not acceptance of a particular
alternative or combination. The chosen outcome is not persisted or recoverable.

## Human value (verbatim reaction, recorded before interpretation)

> "Condition B materially changes the usefulness of the record. In Condition A, Auteur
> remembers everything about how I made the decision except the decision itself. A week
> later, that means I still have to rely on memory, external notes, or reverse-engineer
> the current story state to know what I actually committed to. That feels like a real
> break in continuity, not merely missing convenience.
>
> With Condition B, the record becomes self-contained: I can see what I considered, why
> the tradeoff mattered, and what I ultimately chose. That makes it meaningfully easier
> to resume work with confidence.
>
> The value is broader than remembering a fact. The explicit outcome also gives
> downstream work and later revision a stable thing to refer to. But those are secondary
> benefits for me here. The immediate value is that an accepted decision should be able
> to answer 'what did I decide?'
>
> I would not want Auteur to infer the outcome from significance, combination_direction,
> canonical state, or prose. It should be an explicit author-controlled fact. And
> recording it should not automatically mean mutating the Blueprint or treating
> decision-local significance as global canon.
>
> So my primary classification is materially improves continuity, with reduced
> reconstruction burden as a direct consequence."

Classification: **materially improves continuity** (primary), reduced reconstruction
burden (secondary). NOT primarily downstream-application or revision value.

## Discovery question (delegated)

> **What is the smallest explicit, author-controlled representation that lets an accepted
> AuthorDecision preserve and recover its resolved choice across supported combination
> shapes, without inferring the choice or prematurely applying it to canonical state?**

## Binding constraints (from the human)

- outcome must be explicitly authored/confirmed;
- no prose inference; no ranking/recommendation;
- acceptance and resolution semantics must be unambiguous;
- `combination_direction` alone must NOT imply selected membership (operation ≠ member);
- recording the outcome must not automatically mutate Identity/Blueprint;
- existing unresolved decisions remain valid;
- backward compatible with existing artifacts;
- provenance must distinguish deliberation context from resolved outcome;
- downstream application and supersession remain separate future questions.

## Mechanism families compared

### M1 — `chosen: [alternative_id]` (membership list) on AuthorDecision
A single optional list of the author-selected member(s). For `one_of`, exactly one
member; for `choose_k_of_n`, exactly k members (the chosen set). Combined with the
existing authored `combination_direction`, the full resolved outcome is unambiguous:
`chosen = [signe_marriage]` + `cut` ⇒ "cut signe, keep marta". Absent = unresolved
(backward compatible). Explicit, no inference, minimal, general across both shapes.

### M2 — `chosen_alternative_id: str` (single ID)
Smaller for `one_of`, but cannot express `choose_k_of_n` (k>1) chosen *sets* without
schema ambiguity. Rejected: does not cover the supported `choose_k_of_n` shape.

### M3 — outcome in the acceptance record (not the artifact)
Keeps the deliberation artifact immutable and stores the resolution in the `.acceptance`
record. Plausible, but splits "what was decided" across two files and couples the outcome
to the acceptance lifecycle (an author may want to record a choice before formal
acceptance). Larger; rejects the natural reading that the artifact IS the decision.

### M4 — separate resolution object / supersession lineage
Append-only decisions with `supersedes` pointers (the expression/revision pattern). This
is the *revision* campaign's territory, not the outcome question; over-built here. Also
pulls supersession semantics in prematurely.

## Selection (delegated product authority)

**M1 — optional `chosen: list[alternative_id]` on AuthorDecision**, validated to be a
non-empty subset of `alternative_ids` with cardinality matching the combination rule
(exactly 1 for `one_of`; exactly `k` for `choose_k_of_n`; absent/None = still open).
Echo-only in the consumer: surfaced as a provenance-labeled authored fact, never used to
mutate canonical state, never inferred, never ranked. Escalation check: none of the
standing-envelope triggers is hit (no weights/ranking/LLM/ontology/3+ goals/prose
inference/F1 conflict; recording is an explicit author action, not canonical mutation).

## Claim language

- **human-demonstrated:** explicit outcome materially improves continuity (frozen case,
  one case — not generalized).
- **agent-selected/validated:** M1 as the representation + its qualification.
- **post-merge observed:** pending, in continued use.
