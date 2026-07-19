# Auteur Capability Coverage and Pilot Plan

This inventory separates architectural completeness from product completeness.
It is a planning artifact, not a claim that every artifact scope has equal
implementation depth.

The canonical reference now provides evidence for the bounded single-Chapter
path. The matrix below reflects that evidence; it does not imply Book-level or
long-form completeness.

## Coverage matrix

| Artifact stage | Create | Validate | Reason | Propose | Publish | Accept | Author UX |
|---|---:|---:|---:|---:|---:|---:|---:|
| Story Identity | yes | yes | partial | partial | partial | yes | partial |
| Blueprint | yes | yes | limited | partial | no | yes | partial |
| Chapter Structure | yes | yes | partial | no | no | yes | partial |
| Scene Realization | yes | yes | partial | partial | partial | yes | partial |
| Scene Expression | yes | yes | yes | yes | yes | yes | yes |
| Chapter Expression | yes | yes | yes | yes | yes | yes | yes |
| Book Manuscript | yes | yes | no | yes | yes | yes | partial |

The matrix is intentionally qualitative. “Partial” means a path exists but
does not yet have the same reasoning, proposal, freshness propagation, and
author-facing depth as the proven Expression path.

## Proven and incomplete verticals

The deepest current path is:

```text
Scene Realization → Scene Expression → Chapter Expression
→ Chapter external editing → reconciliation → proposal → publication
→ independent decision → recomposition → Chapter acceptance
→ Book Manuscript assembly → Book external editing
→ Book reconciliation → Book proposal → Book publication
→ Book candidate decisions → Book recomposition → Book comparison
→ Book acceptance → Book reconciliation completion
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

## Canonical-story evidence update

`The Lantern at Low Water` has now traversed the bounded single-Chapter path:

```text
Identity → Blueprint → Chapter Structure → 5 Scene Realizations
→ 5 accepted Scene Expressions → accepted Chapter Expression
→ external edit → reasoning review → reconciliation
→ publication → mixed decisions → accepted-source recomposition
→ Chapter acceptance → partially_reconciled completion
```

The dogfood verified one accepted Scene candidate, one rejected Scene candidate,
and a deferred Chapter transition. It also verified that the committed
reference project is not used as a write target.

This evidence upgrades Scene Realization acceptance from `partial` to `yes` for
the bounded canonical path. It does not upgrade Book Manuscript: multiple
Chapters, Book-level assembly, and export remain untraversed.

## Evidence-selected next slice

The next candidate is Book-level workflow:

```text
multiple accepted Chapters → Book Manuscript
→ Book-level reasoning/editing → export-ready artifact
```

This bounded Book Manuscript slice is now proven on the canonical two-Chapter
fixture. Book external-edit inspection and ownership routing (Phase A) produce
noncanonical Book proposals, and Book proposal planning plus atomic candidate
publication (Phase B) materialize durable, unaccepted Book candidates with a
noncanonical preview and manifest — publication is not acceptance, and no
accepted Book, Chapter, or upstream artifact is mutated. See
[book-reconciliation-application.md](book-reconciliation-application.md).
Book candidate acceptance (Phase C3), Book recomposition from accepted sources,
Book comparison, and Book reconciliation completion (Phase C4) are now
implemented: the full Book workflow from inspection through completion has been
committed with 300+ passing tests. Book-level reasoning/editing remains deferred.
**HTML and EPUB3 publishing formats are now implemented** (`auteur publish` with
52 tests — see `docs/v1-architecture-completion-report.md` section Priority 2).
Structural revision propagation remains deferred because the canonical pilot
produced no evidence that it is the highest-impact blockage.
