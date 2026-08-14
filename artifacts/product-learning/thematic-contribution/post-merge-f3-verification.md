# Post-Merge Verification — F3 Referent-Level Thematic Contribution (PR #76)

> Recorded 2026-08-14 after PR #76 merged (merge commit `30529b99` on origin/main;
> exact head `edb45f7`). Product-learning follow-up per the delegation envelope:
> re-run the F3 controls against shipped main and confirm the end-to-end Case-4
> composition is delivered by the shipped surface. Runs used the repo `.venv` with the
> merged main source; source-qualified at the PR head before merge (4235 collected /
> exit 0; ruff + check.py green).

## The claim (what PR #76 ships)

A durable structural referent can carry opaque, author-authored thematic contribution
text, and its current **operative** state is an explicit canonical assertion. When a
referent is explicitly non-operative AND declares contributions, the structure analyzer
emits a deterministic **contribution-loss finding** — composing two independently
authored facts (explicit non-operative + declared contribution) into "contribution
absent from the operative story". That consequence is the one the Case-4 zero-code test
demonstrated changes the author's next structural action.

## End-to-end dogfood on merged main (canonical SHA 30529b99)

Salt of the Earth frozen story, `goal-significance-absent` decision, anchor
`signe_marriage`:

```
$ auteur decision promote goal-significance-absent --anchor signe_marriage ...
→ Promoted durable structural referent: signe_marriage
  kind=subplot participants=['identity.characters[0]'] carriers=[]
  (bears_on/nature and chosen outcome NOT applied — promotion is not enactment.)

$ auteur decision contribution goal-significance-absent --referent signe_marriage \
    --add "supplies the relational counterweight that keeps the bittersweet ending
           emotionally credible" ...
→ Declared thematic contribution state for referent: signe_marriage
  + contribution: supplies the relational counterweight that keeps the bittersweet
    ending emotionally credible
  operative = unset (explicit canonical current-state assertion; decision history
  not consulted)

$ auteur decision contribution goal-significance-absent --referent signe_marriage \
    --operative no ...
→ Declared thematic contribution state for referent: signe_marriage
  operative = no (explicit canonical current-state assertion; decision history
  not consulted)

$ analyze_structure(blueprint)
→ info [representation] structural_referent.contribution_non_operative:
  Durable structural referent 'signe_marriage' is not operative; its authored
  thematic contribution(s) are absent from the operative story. 1 contribution(s)
  declared.
```

Every step of the validated composition is reproduced by shipped commands: explicit
contribution → durable referent → explicitly non-operative → deterministic
contribution-loss finding → authored contribution shown faithfully (count only, never
parsed). `chosen`/`combination_direction` were never consulted (authority semantics);
`operative=unset` recorded an explicit undeclared declaration with provenance; the
finding fired only on explicit `no`.

## Post-merge test evidence

```
tests\test_author_decisions_contribution.py:
22 passed in ~10s  (merged main, repo .venv)
```

## Invariants re-confirmed on merged main

- operative never derived from `chosen` (promote output unchanged; contribution action
  reads only the decision id for provenance);
- default `operative=None` → no assertion; finding only on explicit `False`;
- contribution text opaque (message carries count, never prose);
- no thread aggregator / `theme.*` changes (diff = 5 scoped files);
- `StructuralReferent.kind` stays `"subplot"`;
- no automatic application; backward compatible (defaults `[]`/`None`/`None`);
- F1 significance stays decision-local; restoration representable (`--operative yes`).

## Claim check

The shipped surface delivers the recorded narrow claim. The R2-bounded thematic/
contribution slice is closed end to end. General contribution ontology, structural
footprint expansion, broad analyzer redesign, and Decision Revision & Supersession
remain NOT-earned/parked — nothing in this slice earned them.
