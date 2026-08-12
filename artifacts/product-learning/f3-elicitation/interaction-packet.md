# F3 Zero-Code Human Interaction Test — Genuinely Unsettled Cross-Goal Significance

> Cycle: `discovery/f3-elicitation` (worktree `H:/GithubRepositories/auteur-f3-elicitation`,
> base = canonical origin/main `a21bb43` = merged PR #68; local main NOT used — it carries
> unrelated unpushed commits). Zero production change; no schema; no code. Frozen
> presentation authored BEFORE any reaction (F1 precedent @ 2dcf073). Product runs via the
> worktree `.venv` on the shipped state; verbatim reports in `capture/`.

## The gap this test probes (solution-free)

The shipped product (PR #68) supports:
- deterministic cross-goal consequence composition (PR #67);
- authored decision-local relative significance when the author knows it (F1 `ordered`);
- intentional non-precedence when the author explicitly wants no hierarchy (F1 `unranked`).

It intentionally does NOT represent:

> **"I genuinely don't know which of these accepted goals matters more in this decision."**

## Human test question

> Can a lightweight elicitation interaction help the author clarify an unsettled
> tradeoff without manufacturing a priority or forcing them into a ranking?

## Shipped surface (presented to the human first)

Frozen story (Salt of the Earth), decision `goal-significance-absent`/`unsettled-prose`
(identical reports — 7 observations / 2 per-alternative / 2 combinations):

```
AUTHORED GOALS (from the blueprint):
  ending tone = bittersweet (blueprint.contract.mandatory_ending_tone)
  POV contract = third_person_limited_single (blueprint.identity.pov_type)

AUTHORED ANCHOR RELATIONSHIPS:
  Marta's pregnancy  sustains the ending tone · pressures the POV contract
  Signe's marriage   sustains the POV contract · pressures the ending tone

AUTHORED OPERATION: one_of — cut (choose which subplot to cut)

DETERMINISTIC CONSEQUENCES (composed):
  cut marta_pregnancy removes its declared sustaining relationship to the ending tone
  cut marta_pregnancy removes its declared pressuring relationship to the POV contract
  cut signe_marriage  removes its declared sustaining relationship to the POV contract
  cut signe_marriage  removes its declared pressuring relationship to the ending tone
```

The human is placed in the explicit state:

> **"I care about both goals and genuinely do not know which loss matters more."**

## Interaction styles (compared, in order)

### Style 1 — Direct comparison question
Ask the author to compare the two goals abstractly, without consequences in view:

> "Between the ending tone and the POV contract, which of the two goals matters more
> to you **for this decision**?"

### Style 2 — Consequence-focused elicitation
Ask about the concrete losses, not abstract priority — which loss the author would
regret/tolerate more:

> "Cutting Marta removes a *sustainer of the ending tone* and a *pressurer of the POV
> contract*. Cutting Signe does the mirror. **Which of these two losses would you regret
> more — losing the ending-tone sustainer, or losing the POV-contract sustainer?**"

### Style 3 — Explicit refusal / continue-undecided path
Give the author a first-class way to stay unsettled:

> "If neither comparison resolves it — if the tension is genuinely unresolvable for you
> right now — you can leave the significance **undecided** for this decision and carry
> on. Nothing forces a ranking."

### F4 control (separate, clearly labeled)
A provisional Auteur choice, offered as a labeled position to react to — to tell whether
reaction-to-a-position adds anything beyond ordinary elicitation:

> **[F4 CONTROL — labeled provisional Auteur position, not an instruction]**
> "If Auteur were to provisionally act on the goal it can best defend from the
> consequences alone: cutting **Signe's marriage** removes a POV-contract sustainer
> (preserving the ending-tone sustainer Marta's pregnancy). Would reacting to that
> position surface anything the questions above did not?"

## Valid outcomes (any of)
- priority becomes clear;
- intentional non-precedence becomes clear;
- author remains genuinely unsettled;
- Auteur proposal uniquely surfaces a preference;
- none of the interactions help.

## Recording rule
Reactions are recorded **verbatim** before any interpretation. No judgment is attached
during the interaction.
