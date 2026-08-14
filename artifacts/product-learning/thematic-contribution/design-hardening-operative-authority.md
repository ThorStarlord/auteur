# Design Hardening Addendum — Contribution Operative-State Authority (approved 2026-08-14)

> Applies to `implementation-design.md` §2/§5. Authorized by the human before TDD:
> "make one narrow design hardening pass around contribution operative-state authority."
> Binding for construction.

## A. Operative-state authority semantic (binding)

`operative` is an **explicit canonical assertion about whether this authored
contribution currently operates in the story.** Changing it is an
**author-controlled enactment/state declaration** — NOT an inference from `chosen` or
`combination_direction`, and NOT a second statement of the decision outcome
masquerading as derivation.

Three distinct facts, related but not interchangeable:

```
DECISION HISTORY        "I chose to cut Signe's marriage"        (author_decisions)
THEMATIC CONTRIBUTION   "what work this referent explicitly performs"  (canonical)
OPERATIVE STATE         "whether that contribution currently operates in the story" (canonical)
```

They may often move together, but Auteur must not claim they are universally
equivalent. Contribution operation is a narrower **current-state** fact — the
contribution could move elsewhere, survive in altered form, or later be restored.

## B. Default-state resolution (binding)

**`operative: bool | None = None`** — unset = current operative state NOT explicitly
declared. NOT `True` by default.

Rationale (per human): a silent `True` default would make Auteur assert current
creative-state semantics the author never declared. Declaring a contribution is
deliberately NOT defined as declaring it operative — the two declarations are separate
author acts. `None` is the honest state: Auteur asserts nothing about current operation.

Semantics:

```
operative = None   current operative state not explicitly declared → NO finding, no
                   assertion of operative or non-operative (fail honestly)
operative = True   explicitly operative → no loss finding
operative = False  explicitly non-operative → contribution-loss finding (with non-empty
                   contributions)
```

## C. The explicit author action (binding)

New `decision contribution` subcommand (author_decisions CLI), two explicit modes:

```
auteur decision contribution <decision_id> --referent <id> --add "<opaque text>"...
auteur decision contribution <decision_id> --referent <id> --operative yes|no|unset
```

- `--add` appends opaque author-authored contribution text (idempotent on exact
  duplicate; fail closed on empty);
- `--operative yes|no|unset` declares the current operative state (unset → None);
- both fail closed on unknown referent / unknown decision;
- `chosen`/`combination_direction` are NEVER consulted — the action is purely an
  explicit author declaration;
- provenance: each mutation records `declared_in_decision_id` + ISO timestamp on the
  referent (auditable; the decision is provenance context, not the source of the state);
- contribution text is NEVER parsed (presence/absence only).

## D. Schema (final)

```python
class StructuralReferent(BaseModel):
    referent_id: str
    kind: str = "subplot"  # unchanged, validated
    participants: list[str]
    carrier_refs: list[str]
    provenance: ReferentProvenance  # unchanged (promotion provenance)
    thematic_contributions: list[str] = Field(default_factory=list)  # NEW
    operative: bool | None = None                                      # NEW
    contribution_provenance: ContributionProvenance | None = None      # NEW
```

`ContributionProvenance`: `{declared_in_decision_id: str, declared_at: str}` (last
declaration). Backward compatible: existing referents default to `[]`/`None`/`None`.

## E. Finding (unchanged from §3, now unambiguous)

`structural_referent.contribution_non_operative` (INFO, layer=REPRESENTATION),
emitted from `analyze_structure` for each referent where `operative is False` AND
`thematic_contributions` non-empty:

> "Durable structural referent '<id>' is not operative; its authored thematic
> contribution(s) are absent from the operative story. [N] contribution(s) declared."

Evidence: `referent_id`, `operative: false`, `contribution_count`. No thread
aggregator / theme.* changes.

## F. Controls (updated)

- operative=True → no loss finding;
- operative=False + non-empty contributions → loss finding;
- **operative=None → NO finding (honest non-assertion)**;
- no contributions → no finding regardless of operative;
- two referents → one non-operative does not erase the other;
- `pressures` relationship coexists with a valuable contribution;
- thread remains declared and untouched;
- F1 stays decision-local;
- `chosen` alone produces no contribution/operative mutation (action never reads it);
- no prose/name/fuzzy/LLM inference;
- old Blueprint/referent artifacts remain compatible;
- restoration representable (`--operative yes` after `no`).

## G. Construction stop conditions (re-affirmed)

General contribution ontology; footprint; automatic decision enactment; broad
theme-analyzer redesign; revision/lifecycle machinery. None are required by this
hardened design → construction may proceed per the envelope.
