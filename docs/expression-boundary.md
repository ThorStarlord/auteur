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

## Validation and proposals

Deterministic checks cover source acceptance, source revision, participant and
POV validity, explicit outcome contradiction, and representable unavailable
knowledge. Style, voice, tone, pacing, dialogue naturalness, and imagery remain
advisory.

If prose exposes a structural problem, the pilot creates an upstream proposal
identifying the target artifact and layer, source Scene revision, problem,
suggested change, and prose evidence. It never mutates upstream artifacts.

When the source Scene changes, prose candidates become stale but remain
preserved. No automatic regeneration occurs.

## Current limits

This pilot does not provide a generic transformation runtime, chapter-wide
drafting overhaul, complete Expression system, automatic Bible mutation,
automatic repair, publishing, collaboration, or repository-wide provenance
normalization.
