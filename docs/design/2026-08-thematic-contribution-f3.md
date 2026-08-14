# F3 — Referent-Level Thematic Contribution (construction)

> Phase: construction (authorized by the human 2026-08-14 after the design-hardening
> pass @ `0623b48`). Approved design: `artifacts/product-learning/thematic-contribution/`
> (implementation-design.md @ `0068489` + design-hardening-operative-authority.md @
> `0623b48`) on `discovery/thematic-contribution`. Base SHA: `c968a747` (origin/main,
> PR #75 merged). This doc is the in-branch engineering record.

## Product claim (what this slice delivers)

A durable structural referent can carry opaque, author-authored thematic contribution
text, and its current **operative** state is an explicit canonical assertion. When a
referent is explicitly non-operative AND declares contributions, the structure analyzer
emits a deterministic **contribution-loss finding**:

> "Durable structural referent '<id>' is not operative; its authored thematic
> contribution(s) are absent from the operative story. [N] contribution(s) declared."

This composes two independently authored facts (explicit non-operative state + declared
contribution) into the consequence the Case-4 test demonstrated changes the author's
next structural action. It does NOT parse contribution prose, does NOT change thread
aggregators or `theme.*`, does NOT apply the decision outcome.

## Authority semantics (binding)

- `operative` is an explicit canonical current-state assertion: `yes` / `no` / `unset`
  (None = not explicitly declared → honest non-assertion, no finding).
- The `decision contribution` action NEVER consults `chosen`/`combination_direction`;
  the decision is provenance context only.
- Contribution text is opaque — presence/absence only.
- Decision history ≠ canonical contribution state ≠ thematic contribution. They are
  related but not interchangeable.

## Schema (blueprint.py)

```python
class ContributionProvenance(BaseModel):
    declared_in_decision_id: str
    declared_at: str  # ISO-8601

class StructuralReferent(BaseModel):
    referent_id: str
    kind: str = "subplot"          # unchanged, validated to single value
    participants: list[str]
    carrier_refs: list[str]
    provenance: ReferentProvenance # promotion provenance (unchanged)
    thematic_contributions: list[str] = Field(default_factory=list)  # NEW
    operative: bool | None = None                                    # NEW
    contribution_provenance: ContributionProvenance | None = None    # NEW
```

Backward compatible: existing referents default to `[]` / `None` / `None`.

## CLI

`auteur decision contribution <decision_id> --referent <id> --add "<text>"...`
`auteur decision contribution <decision_id> --referent <id> --operative yes|no|unset`

- `--add` appends opaque text (idempotent on exact duplicate; fail closed on empty);
- `--operative yes|no|unset` declares current state (unset → None, recorded as an
  explicit "currently undeclared" declaration with fresh provenance — NOT the same
  as never-declared);
- fail closed on unknown referent / unknown decision / no mode flag;
- `--referent` defaults to the single referent when unambiguous;
- provenance records `declared_in_decision_id` + ISO timestamp on each declaration.

## Consumer

`structural_referent.contribution_non_operative` (INFO, `DiagnosticLayer.REPRESENTATION`)
from `analyze_structure` — composed from explicit non-operative + declared
contribution; evidence includes `referent_id`, `operative = false`, and declared count.

## Tests

`tests/test_author_decisions_contribution.py` — 22 tests: 12 hardened controls +
action fail-closed + provenance + idempotency + mode requirement.

## Verification (merge path)

Full suite, ruff, `scripts/check.py`, independent review, autonomous merge per the
standing envelope (scope matches, CI green, review clean, exact head merged), then
post-merge mechanical verification.
