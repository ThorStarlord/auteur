# Premise-to-Narrative-Architecture Beginner Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Reorder the Beginner Workspace so a fresh premise first produces an explicit, inspectable, noncanonical Narrative Architecture Analysis; make that analysis the default working guidance context; then let Discovery search coherent story directions, Story Identity ratify explicit commitments, and Structure plan the accepted story.

**Architecture:** Keep Auteur's canonical five-layer model unchanged. Add a bounded Beginner-only derived analysis contract backed by the existing LLM client abstraction and deterministic fallback, persist it inside the existing noncanonical session envelope, project only material active components into WorkingComposition, reuse Story Discovery for direction generation/comparison, and keep all canonical mutation behind the existing Story Identity/Structure authority services.

**Tech Stack:** Python 3.11+, Pydantic v2, existing Auteur LLM client abstraction, existing Story Discovery and StoryIdentity models, Beginner Workspace application/persistence/authority stack, local JSON API, vanilla JavaScript/CSS, pytest, Ruff.

**Spec:** docs/superpowers/specs/2026-09-19-premise-to-narrative-architecture-beginner-flow.md

## Global Constraints

- Canonical semantic architecture remains exactly Ontology → Identity → Structure → Realization → Expression.
- Narrative Architecture Analysis is derived and noncanonical.
- The author can continue without individually confirming every inferred component.
- Guidance activation, author review/confirmation, and canonical authority are separate axes.
- Composition is optional refinement, not an admission gate.
- Discovery searches coherent story directions; Story Identity owns commitments; Structure owns plans.
- Do not preserve the current 3/4/3 card quota as a product invariant.
- Do not expose internal enum tokens in the default beginner UI.
- Provider failure/absence must degrade explicitly and must not fabricate rich interpretation.
- PR #237 remains draft and unmerged during implementation and qualification.
- Reuse its WorkingComposition, Mapping Planner, authority, provenance, revision isolation, crash recovery, and semantic-staleness substrate.
- No provider calls from GET/projection code.
- Legacy session JSON that omits new optional fields must continue to parse.
- Use TDD for every behavior change.
- Do not modify or commit .superpowers/.
- Any source/test change after candidate freeze invalidates downstream evidence.

## Review Focus

1. Ambiguous component alternatives must remain component-scoped rather than becoming competing whole-premise analyses.
2. Provider unavailable/malformed must degrade explicitly without unsupported psychological/aesthetic claims.
3. Active inferred but unconfirmed components must affect guidance while remaining noncanonical.
4. Stale analysis/discovery must not silently drive acceptance.
5. Crash retry must not duplicate provider generation or canonical promotion.

---

## File Structure Locked by This Plan

~~~text
src/auteur/beginner/
├── architecture_models.py
├── architecture_analysis.py
├── architecture_projection.py
├── discovery_models.py
├── discovery.py
├── decision_inventory.py
├── application.py
├── contracts.py
├── dimensions.py
├── guidance.py
├── mapping.py
├── promotion.py
├── projections.py
├── persistence.py
├── server.py
└── browser/
    ├── index.html
    ├── app.js
    └── styles.css
~~~

Do not introduce a generic narrative database or a new semantic layer.
