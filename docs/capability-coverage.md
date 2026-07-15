# Auteur Capability Coverage and Pilot Plan

This inventory separates architectural completeness from product completeness.
It is a planning artifact, not a claim that every artifact scope has equal
implementation depth.

## Coverage matrix

| Artifact stage | Create | Validate | Reason | Propose | Publish | Accept | Author UX |
|---|---:|---:|---:|---:|---:|---:|---:|
| Story Identity | yes | yes | partial | partial | partial | yes | partial |
| Blueprint | yes | yes | limited | partial | no | yes | partial |
| Chapter Structure | yes | yes | partial | no | no | yes | partial |
| Scene Realization | yes | yes | partial | partial | partial | partial | partial |
| Scene Expression | yes | yes | yes | yes | yes | yes | yes |
| Chapter Expression | yes | yes | yes | yes | yes | yes | yes |
| Book Manuscript | partial | partial | no | no | no | partial | no |

The matrix is intentionally qualitative. “Partial” means a path exists but
does not yet have the same reasoning, proposal, freshness propagation, and
author-facing depth as the proven Expression path.

## Proven and incomplete verticals

The deepest current path is:

```text
Scene Realization → Scene Expression → Chapter Expression
→ external editing → reconciliation → proposal → publication
→ independent decision → recomposition → Chapter acceptance
```

The main unbalanced path is structural revision:

```text
Structure change → affected Realizations stale
→ preserve unaffected prose → repair impacted material
```

That path should be selected only after pilot evidence shows it is the highest
friction gap.

## Controlled pilot boundary

Use one bounded real project: a short story, novella, one five-to-ten-chapter
book, or one complete arc. Do not begin with a large series.

The minimum pilot path is:

```text
Story Identity
    → Blueprint
    → 3–5 Scene Realizations
    → accepted prose
    → one external edit
    → reasoning review
    → reconciliation
    → accepted Chapter Expression
```

The pilot must preserve author authority and record derived artifacts only at
inspection, reasoning, and planning stages.

## Friction log

Every pilot issue receives exactly one primary classification:

- missing capability;
- poor author UX;
- wrong artifact design;
- unclear terminology;
- excessive required data;
- weak critic;
- unnecessary validation;
- transformation gap.

Each entry should include the command or artifact involved, the author intent,
observed friction, severity, affected scope, and a smallest reproducible case.
Prioritize by author impact and authority risk, not by number of occurrences
alone.

## Candidate next implementation boundary

If the pilot confirms the expected gap, implement one deterministic structural
revision slice:

```text
structure reasoning
    → noncanonical Structure proposal
    → explicit author decision
    → affected-source freshness propagation
    → preservation of unaffected Realization/Expression
```

The slice must not apply a proposal automatically, rewrite accepted prose, or
recompute unaffected artifacts. It should use the existing proposal, planning,
publication, and acceptance boundaries where they apply.

## Completion criteria for the pilot phase

The pilot phase is complete when:

1. One bounded project has traversed the minimum path.
2. Each observed issue has a primary friction classification.
3. At least one clean author-facing review has been evaluated without raw JSON.
4. The highest-impact missing capability has a reproducible example.
5. The next implementation slice is selected from evidence rather than theory.

