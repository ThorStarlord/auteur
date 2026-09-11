# Auteur V1 Product Contract

**Status:** selected closure contract for the `1.0.0` program.  
**Authority:** product-scope contract; changing a `SUPPORTED` or `BOUNDED` row requires an explicit product-scope decision.  
**Architecture:** `../narrative-architecture.md`.  
**Release policy:** `../engineering/release-qualification.md`.

## Product promise

Auteur 1.0 is a local-first literary compiler and guided narrative-decision system for single-author long-form fiction. It helps an author establish an explicit story direction, plan and diagnose structure, make bounded creative decisions, preserve accepted narrative authority across revisions, draft/reconcile prose, resume safely after interruption, and produce accepted-book HTML/EPUB artifacts.

Auteur does not claim to determine whether literature is good, to infer all story facts automatically, or to replace author authority.

## Supported author journey

The release must support this end-to-end route from a fresh installed artifact:

```text
raw premise
→ Story Discovery
→ explicit StoryIdentity acceptance
→ Blueprint / Structure
→ diagnostics / Tutor decision support
→ explicit advisory choice
→ noncanonical proposal
→ revision plan + validation + preview
→ explicit owning-workflow authority action
→ reassessment / project orientation
→ Scene/Chapter planning and drafting
→ accepted Expression / Book assembly
→ HTML or EPUB publication artifact
```

Not every author must execute every optional stage, but every advertised stage must have a documented, authority-safe path.

## Scope support

| Scope / lane | V1 disposition | Claim boundary |
| --- | --- | --- |
| Scene | `SUPPORTED` | Realization and Expression workflows may be used and accepted with explicit authority boundaries. |
| Chapter | `SUPPORTED` | Planning, drafting, reconciliation, and accepted Expression are supported. |
| Book | `SUPPORTED` | Primary complete long-form unit; assembly/reconciliation/publishing are supported. |
| Series | `BOUNDED` | Accepted-history/current-state reconstruction and continuity guidance are supported within qualified bounded use. |
| Universe | `EXPERIMENTAL / OPTIONAL CONTEXT` | Existing Universe tooling may provide supporting context, but V1 does not claim a provenance-normalized Universe authoring vertical and the primary journey does not require it. |
| Episode 1 Direction | `EXPERIMENTAL / NOT REQUIRED` | Issue #218 preserves a future bounded contract; it is not a V1 blocker. |
| Episode 2+ / generalized serial entry abstraction | `OUT OF V1` | No sixth canonical scope and no automatic generalization from Episode 1. |
| 50/100+ Book scale | `OUT OF CLAIM` | Long-horizon architecture exists in bounded form; very-large-scale performance/relevance is not a V1 guarantee. |

## Interfaces

| Interface | V1 disposition | Intended user |
| --- | --- | --- |
| Guided local browser workspace | `SUPPORTED` for the core decision loop | beginner/default author experience |
| CLI | `SUPPORTED` | advanced authors and engineers |
| YAML/JSON/Markdown artifacts | `SUPPORTED / TRANSPARENT` | advanced inspection and portability |
| Python internals | `INTERNAL UNLESS DOCUMENTED` | not a blanket compatibility promise |
| Cloud/multi-user service | `OUT OF V1 / MISSION NON-GOAL` | — |

The browser workspace must reuse existing application/authority services. It must not create a parallel canonical-state store or a second acceptance path.

## Runtime environments

| Environment | V1 disposition |
| --- | --- |
| Python 3.11 | supported on Linux |
| Python 3.12 | supported on Linux |
| Python 3.13 | supported on Linux and Windows |
| macOS | best-effort / not release-qualified unless qualification evidence is added before freeze |

The supported matrix may be expanded before release, but unqualified environments must not be advertised as release-qualified.

## LLM providers

| Provider | V1 disposition |
| --- | --- |
| Anthropic | `SUPPORTED` when `auteur[anthropic]` is installed and credentials are supplied |
| OpenAI | `SUPPORTED` when `auteur[openai]` is installed and credentials are supplied |
| Fake/hermetic client | test infrastructure, not a production provider |

Provider support means adapter execution, error normalization, retry/recovery behavior, and authority safety are qualified. It does **not** mean that model output is guaranteed to be artistically good.

## Storage and publication

- Project state is local-filesystem first.
- Schema/version metadata and documented migration compatibility apply to supported project artifacts.
- HTML and EPUB are V1 publication outputs.
- PDF is not required for 1.0.
- Publishing to external platforms is not supported and remains a Mission non-goal.

## Claim ceiling

### Claims permitted when release evidence passes

- "Supports author-controlled long-form fiction development."
- "Preserves explicit accepted narrative authority through supported revision workflows."
- "Supports bounded Series continuity and long-horizon context reconstruction."
- "Runs the documented V1 author journey from a fresh installed package on the qualified platform matrix."
- "Supports Anthropic and OpenAI adapters when their optional dependencies and credentials are present."

### Claims prohibited without new evidence

- "Proven for 50/100+ Book projects."
- "Automatically maintains perfect continuity."
- "Determines whether a creative choice is good."
- "Fully autonomous novelist."
- "Automatically infers all canonical narrative facts."
- "Production cloud collaboration platform."

## V1 non-goals

The following do not block 1.0 unless this contract is explicitly revised: generalized Episode progression, universal relationship/trajectory ontology, automatic story-instance extraction, generic graph database, adaptive writer skill model, collaboration/cloud service, automatic external publishing, broad emotional-trajectory state machine, speculative Story Design Pack breadth, a provenance-normalized Universe vertical, and 50/100+ entry scale optimization.

## Definition of Done

> Auteur 1.0 is complete when a fresh installation on every supported platform can traverse the documented V1 author journey, using every production-supported provider where applicable, while preserving explicit narrative authority, deterministic validation, revision history, freshness/staleness semantics, failure atomicity, restartability, and supported publication output; and every advertised V1 capability is backed by reproducible evidence from the exact frozen release candidate.

A capability outside this contract is not a release blocker merely because it appears in an architecture document, historical audit, issue, experiment, or future roadmap.
