# Expression Boundary

Expression answers how canonical realized events are rendered as language.

## Pilot transformation

```yaml
id: realization.generate_expression
category: generation
version: 1
family: knowledge_creation
```

The pilot transforms one accepted Scene Realization into one versioned prose
candidate. Expression may freely choose language, but it may not silently
change canonical narrative facts.

The adapter reuses Bard's existing prose system contract and LLM request path,
but supplies a Scene Realization-specific context instead of changing the
chapter-oriented PipelineRunner.

## Contract

The input is an accepted Scene Realization and optional Expression constraints:

- POV;
- tense;
- narrative distance;
- voice identifier;
- target scene effect;
- content boundaries.

The candidate may create dialogue wording, imagery, syntax, rhythm, sensory
detail, interiority, paragraph structure, and local pacing.

It must preserve participants, event order, goal, opposition, turn, decision,
outcome, knowledge state, emotional changes, location, action facts, and arc
realizations. It must not change the source Scene Realization, Blueprint,
Chapter Outline, Story Identity, or Bible.

The transformation is constructive, AI-assisted or human-authored, lossy, and
partially reversible. Acceptance is explicit. Prose is not a reversible
encoding of Scene Realization.

## Candidate layout

```text
chapters/<chapter>/scenes/<scene>/
├── prose_v001.md
├── prose_v001.yaml
├── prose_v002.md
└── prose_v002.yaml
```

Candidate metadata records the source Scene artifact ID, revision, content
hash, transformation ID/version, executor and configuration provenance,
Expression constraints, content hash, lifecycle, and acceptance information.

Candidates remain drafts until explicitly accepted. Acceptance promotes one
candidate to canonical Expression authority, preserves earlier candidates, and
never updates Scene Realization or Bible state automatically.

## Candidate lifecycle

Candidates are accepted only when valid, fresh, and not review-required. A
stale candidate must first be revalidated as aligned or have intentional
divergence acknowledged with an author and rationale. Divergent acceptance
requires an explicit `--allow-divergence` action and remains visibly divergent.
Revalidation records a new metadata revision and current Scene dependency
snapshot. Any later relevant Scene, projected-hash, transformation-contract,
or Expression-constraint change reopens acknowledged divergence as
`review_required`; formatting-only changes do not.

Candidates may also be rejected. Rejection preserves prose and provenance and
prevents normal acceptance until explicitly reopened by a future workflow.
Candidates can be compared through a text diff plus lifecycle and validation
summary. Human-readable inspection leads with status and recommended actions;
JSON retains hashes and executor details.

## Validation and proposals

Deterministic contract checks cover source acceptance, source availability,
POV constraint validity, reviewed dependency snapshots, and lifecycle rules.
Semantic prose validation is separate and confidence-bearing: structured
contradictions may block, high-confidence inferred contradictions require
review, and ambiguous knowledge or unreliable narration remains advisory.
Style, voice, tone, pacing, dialogue naturalness, and imagery remain advisory.

Derived realization evidence may be recorded without requiring paragraph-by-
paragraph author annotation:

```yaml
realization_evidence:
  outcome:
    status: realized | contradicted | deferred | ambiguous
    evidence:
      - start_offset: 0
        end_offset: 24
        excerpt_hash: sha256:...
  knowledge_disclosures:
    - fact_id: ledger_exists
      status: disclosed | concealed | contradicted
      evidence: []
  pov_assertions:
    - fact_id: ledger_exists
      holder: mara
      source: entry_state
```

POV validation distinguishes direct private-knowledge exposure from attributed
speech and a character's explicitly marked false belief. Ambiguous cases are
review findings rather than automatic invalidity.

If prose exposes a structural problem, the pilot creates an upstream proposal
identifying the target artifact and layer, target revision and projected hash,
source candidate, transformation version, problem, suggested change, and prose
evidence. A proposal becomes stale when its target revision or projected hash
changes and cannot be applied until regenerated or manually rebased. It never
mutates upstream artifacts automatically.

When the source Scene changes, prose candidates become stale but remain
preserved. No automatic regeneration occurs.

## Creative discovery and deliberate divergence

Unexpected prose is **evidence before it is an error**.

A human-authored or AI-assisted Expression may reveal story material that was
not represented in the accepted planning inputs. Review must classify that
difference before deciding whether it blocks acceptance.

The primary classifications are:

- **Additive discovery** — a new character, place, relationship, object,
  incidental world detail, or other compatible fact appears without negating
  accepted narrative meaning. This is nonblocking evidence. If retained, it may
  generate proposals for the lowest appropriate owning layer or realized state.
- **Plan divergence** — the prose materially changes the planned scene path,
  event ordering, participant set, location, goal, turn, or outcome without
  necessarily contradicting accepted canon. This requires author review but is
  not automatically an error. The author may revise toward the plan, accept the
  divergence explicitly, or keep the prose and reconcile affected upstream
  artifacts through proposals.
- **Hard canon contradiction** — the prose conflicts with an accepted fact or
  authority-owned commitment that cannot simultaneously remain true. This
  requires an explicit author decision at the owning authority boundary before
  the inconsistency can be treated as resolved.

Discovery classification never authorizes silent upward mutation. Expression
may produce evidence and proposals; Identity, Structure, Realization, Bible, or
other owners remain responsible for accepting their own changes.

The default reconciliation rule is:

```text
unexpected prose
-> classify
-> preserve candidate
-> expose author choice
-> create noncanonical proposals when warranted
-> cross each authority boundary explicitly
```

A deliberate divergence may be accepted as Expression while remaining visibly
divergent from its current plan. This does not imply that the plan or any
upstream artifact was updated.

### Validation freshness

Validation evidence must identify the exact candidate content it reviewed.
Matching a draft and validation artifact by version number alone is
insufficient.

At minimum, review evidence should retain the candidate content hash:

```yaml
candidate:
  path: draft_v2.md
  sha256: <content-hash>
```

If the current candidate hash differs from the recorded validation hash, the
review is stale and must not be presented as current evidence. A human edit
must therefore create or enter an unvalidated candidate state rather than
silently inheriting prior critic findings.

## Current limits

Accepted Scene Expressions can be assembled by the focused
`expression.compose_chapter` pilot into a derived Chapter Expression. The
assembly preserves stable Scene markers and source revisions; it does not
become a second canonical prose source and does not modify Scene artifacts.
See [Expression Composition](expression-composition.md) for its ownership and
round-trip boundary.

Chapter manuscript reconciliation is a derived inspection and proposal
workflow. It may suggest Scene Expression or transition revisions, but it does
not apply them or mutate upstream narrative artifacts.

Chapter-owned transitions are explicit dependencies: boundary IDs, lifecycle,
revision, and content hash are recorded and participate in assembly freshness.
Marked manuscript inspection is read-only; malformed or markerless external
prose becomes actionable Chapter divergence and never silently rewrites Scene
Expression.

This pilot does not provide a generic transformation runtime, chapter-wide
drafting overhaul, complete Expression system, automatic Bible mutation,
automatic repair, publishing, collaboration, or repository-wide provenance
normalization.
