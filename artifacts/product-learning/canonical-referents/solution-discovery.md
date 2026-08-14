# Solution Discovery — Canonical Structural Referents for Decision Outcomes

> Cycle: `discovery/canonical-referents` (worktree `H:/GithubRepositories/auteur-referent-discovery`,
> base = canonical `origin/main @ 156b73cb` incl. PR #74). Zero production change. This is
> Solution Discovery only — no implementation design, no construction. A mechanism that
> materially expands canonical story ontology requires human product selection (escalation
> envelope trigger).

## Demonstrated break (behavioral, from Accepted-Decision Downstream Validation)

> **An accepted outcome can explicitly name what the author chose (`chosen:
> [signe_marriage]`, direction `cut`), but the chosen structural element has no stable
> canonical referent. Downstream reasoning consumes canonical structure, so the author
> cannot enact or carry that choice forward without prohibited prose/name inference.**

Condition A: decision-only → `structure diagnose` byte-identical to baseline (downstream
consumer sees nothing). Condition B: explicit canonical application is impossible — no
canonical object exists to edit. Only prose (`author_text`/`thematic_function`/
`central_question`/`tone`) names the subplots; matching it is forbidden.

## Canonical referential substrate (mapped from shipped source)

| Canonical structure | Stable identity? | Can it be the referent for `signe_marriage`? |
|---|---|---|
| `characters[i]` | Yes (list index; decision `participants` already use `identity.characters[i]`) | Only for character-level outcomes, not subplots |
| `blueprint.contract.*` fields | Yes (field path) | Only for goal-level outcomes (the `bears_on` targets) |
| `story_engine.threads[]` (`StoryThread`) | `name: str` only — no stable id | Generic ("Secondary Struggle", "Relationship Echo", "Secondary Subplot 3"); semantically main-thread *support functions*, not the subplots being cut |
| `structure.subplot_budget` | bare `int` | A count, not entities |

**Conclusion:** the demonstrated decision is *about* subplots (`signe_marriage`), and no
canonical entity represents a named subplot. Characters and contract goals have stable
referents; subplots do not.

## Mechanism families compared

### F1 — Explicit decision→canonical binding (author links anchor to an existing element)
Attractive only where a canonical referent already exists. For the demonstrated case there
is **nothing to bind to** — no canonical subplot entity. Fails the demonstrated case;
would suffice for character/goal-level outcomes only.

### F2 — Promotion of an already-authored decision-local anchor
The author has ALREADY explicitly declared `signe_marriage` as a `structural_anchor` with
`participants` (character refs) and `bears_on` (goal refs + natures). Promotion gives that
already-explicit anchor a canonical home, only when the author decides it deserves
durable life. Smallest bridge; reuses authored content; no name-matching (the anchor is
explicit); provenance-preserving (decision-local → canonical, flagged). Still adds a
canonical structural concept (an ontology expansion), so it is escalation-gated.

### F3 — Minimal canonical structural entity (named subplot/structural unit with stable id)
The true ontology-expansion candidate. Largest; only justified if the need is genuinely
for a durable, reusable subplot concept rather than a per-decision bridge.

### F4 — Strengthen/reuse existing `story_engine.threads` via explicit identity/semantics
Threads are a different abstraction (main-thread support functions); retrofitting them
into "the subplots being cut" changes their meaning and would not have encoded the frozen
case (generic placeholder threads). Tested and found semantically mismatched.

### Control — a decision that already has a stable canonical referent
A character-level or goal-level outcome (`bears_on` target, or a `participants` character)
already resolves through existing `_resolve_entity_ref`. The proposed mechanism must NOT
add representation for these — it should be inert when a referent already exists.

## Comparison dimensions

| Family | Author authority | Downstream addressability | Representational cost | Reversibility | Ontology beyond need? |
|---|---|---|---|---|---|
| F1 explicit binding | high (explicit link) | only where referent exists | low | high | **no** (inert when no referent) — but insufficient for the case |
| F2 anchor promotion | high (explicit, provenance-flagged) | yes (gains canonical id) | low-medium | high (flagged, reversible) | minimal new concept |
| F3 new canonical entity | high | yes | medium-high | medium | substantial new ontology |
| F4 thread reuse | high | uncertain (semantic mismatch) | medium | medium | changes existing semantics |

## Verdict

**NEW DURABLE REPRESENTATION EARNED.** The demonstrated case proves current canonical
structure genuinely cannot name the thing authors are deciding about (subplots). The
smallest credible representation is **F2 — explicit promotion of the already-authored
decision-local structural anchor** into a canonical referent, because it reuses the
anchor's explicit content (participants + bears_on + natures) and needs no name-matching.
F1 is the correct answer *only where a referent already exists* (the control); F4 is
semantically mismatched; F3 is larger than the demonstrated need.

**This verdict expands canonical story ontology, so it stops for human product selection
under the escalation envelope.** No mechanism is chosen autonomously; no design or
construction is entered.

## Claim language

- **human-demonstrated:** the outcome/referent chain breaks behaviorally (downstream
  consumer ignores the accepted decision; no canonical object to enact it).
- **agent-validated:** the substrate map + family comparison above.
- **post-merge observed:** n/a (nothing built).
