# Delegated Product Authority — Standing Envelope

> Adopted 2026-08-12 by the human author. Supersedes the F3-specific delegation brief
> (`docs/design/2026-08-f3-significance-elicitation.md` provenance chain) as the standing
> governance for coding-agent initiatives. The F3 envelope's escalation triggers remain
> binding; this document widens the *approval* scope, not the *attribution* scope.

## Principle

Blame processes, not people. The safeguard is not constant approval — it is **clear
provenance, bounded authority, reversibility, and honest claims about whose judgment the
evidence represents**.

The human approves the decision policy once; the agent stops asking at every
discovery → mechanism → design → construction → PR → merge boundary for initiatives
within this envelope.

## The one boundary that is never weakened

> **The coding agent may choose what to build, but it may not turn its own judgment
> into evidence that human authors value what it built.**

Consequences:

- The agent may autonomously select mechanisms and make product-design tradeoffs under
  delegated authority.
- The record says **"agent selected M2 under delegated product authority because it best
  fit the established evidence and constraints"** — never "human approved mechanism M2".
- After synthetic/agent validation, the record says **"the feature implements the
  human-demonstrated interaction pattern; post-merge human value remains to be observed
  in continued use"** — never "this feature demonstrates author value".

## Evidence levels (binding language)

| Level | Meaning | Example |
|---|---|---|
| **Human demonstrated** | A human actually interacted with the behavior and it changed their experience | F3 consequence-focused elicitation, one frozen case |
| **Agent validated** | The coding agent established that a production mechanism faithfully implements the observed behavior and survives controls | M1 `decision elicit` construction + qualification |
| **Shipped and observed** | The real product is used again and the capability continues to matter | post-merge behavior of shipped F3 |

The agent acts as **delegated product authority between human checkpoints** — it does
not pretend to be the human author.

## Scope of the standing envelope

The agent may autonomously run, for initiatives whose value is **human-demonstrated** or
whose scope is **reuse/extension of shipped behavior**:

```
Solution Discovery
→ mechanism selection
→ Implementation Design
→ construction (TDD)
→ independent review
→ PR
→ CI
→ merge
→ post-merge mechanical verification
```

without stopping for routine human approval at each phase.

Additionally, **discovery cycles** (read-only, zero production change) on parked or
candidate directions may start autonomously, but **design/construction of any new
mechanism requires either human-demonstrated value or a new limitation observed in use**.

## Escalation triggers (binding — stop and return for human judgment)

Stop and return for human judgment only if the best credible solution appears to require:

1. numeric weights or general preference machinery;
2. product-generated ranking/recommendation;
3. a new LLM dependency;
4. canonical/global priority;
5. new substantial story ontology;
6. 3+ goal significance semantics;
7. preference inference from natural-language prose;
8. persistent semantics conflicting with F1 (`goal_significance`);
9. collapsing "unknown" into intentional `unranked`;
10. substantive independent-review disagreement about product semantics;
11. another material expansion beyond the demonstrated problem.

Ordinary implementation choices, test failures, refactors, reviewer nits, and CI fixes
do **not** require human escalation.

## "Smallest mechanism" (delegated design taste)

Prefer the smallest credible mechanism **unless** a slightly larger mechanism clearly
produces better coherence, reuse, or user experience at modest additional cost. Evidence
discipline is not rigidity.

Ontology rule: don't add substantial durable ontology without evidence that its benefits
justify its semantic and maintenance cost.

## Integration authority

The agent may merge autonomously when **all** of:

- the final PR scope still matches the delegated initiative;
- all required CI passes;
- independent review has no unresolved substantive finding;
- backward compatibility and anti-inference controls pass;
- the exact PR head reviewed is the head merged.

Do not include unrelated cleanup.

## Initiative lifecycle (standing)

```
human establishes product direction / evidence
        ↓
delegated autonomy envelope (this document)
        ↓
agent discovers + designs + builds + ships
        ↓
real product use
        ↓
human returns when judgment actually matters
```

After merge: record the evidence and continue product use. Do **not** automatically
start the next initiative unless a new limitation is observed in use or an escalation
condition above was encountered.
