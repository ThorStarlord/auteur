# Auteur Genre Packs Guide

## What is a Genre Pack?

A **Genre Pack** is a versioned, product-level package of reusable genre knowledge. It provides audience promises, emotional targets, narrative engine families, scene functions, conflict families, boundary rules, failure modes, evaluation rules, and subgenre profiles.

## Core Architectural Distinction

> **A Genre Pack supplies versioned genre knowledge used to recommend and evaluate a story direction. Layer 1 records the commitments the author actually accepts.**

* **Pack Knowledge**: Reusable, immutable definitions shipped in versioned files (e.g. `erotic_fiction` v0.1.0).
* **Recommendation**: A derived, read-only candidate artifact (`GenreRecommendation`). Recommending causes **zero mutation** on project state.
* **Accepted Story Identity**: Layer 1 commitments recorded in `StoryIdentity.genre_profile` after explicit author acceptance or override.
* **Compiled Structure**: Downstream Layer 2 arcs and realization built strictly from accepted Layer 1 commitments.

## Preserving Opinionated Mode

1. **Auteur Recommends Strongly**: Given premise inputs, the engine analyzes subgenre profiles and recommends **one primary profile**.
2. **Explanation of Rejected Alternatives**: Every rejected profile includes clear rationale for why it was weaker and what premise changes would make it stronger.
3. **Author Retains Explicit Authority**: Recommendations are not acceptances.
4. **Explicit Acceptance Boundary**: Only accepted commitments compile downstream.

## Versioning & Provenance

* Every Genre Pack is assigned a semantic version (e.g. `0.1.0`) and a deterministic content hash (SHA-256).
* When an author accepts a recommendation, `StoryIdentity.genre_profile` records `primary_pack_id`, `primary_pack_version`, and `pack_content_hash`.
* If a built-in pack is later updated on disk, existing accepted projects remain pinned to their accepted version/hash, ensuring stability.

## Recommendation Persistence & Project Isolation

* **Authoritative Location**: Project-local storage at `.auteur/genre_recommendations/<rec_id>.json` is primary and authoritative.
* **Process-Restart Durability**: Recommendations are written atomically (`_atomic_write_json`) to prevent partial/corrupted files during interrupted writes.
* **Cross-Project Isolation**: Recommendations are strictly scoped to their project directory when project context is specified. Loading a recommendation from another project root is rejected to prevent cross-project leaks.
* **Project Relocation**: Because recommendation artifacts reside inside `.auteur/genre_recommendations/` within the project root directory, moving or renaming a project preserves inspectability.

## MVP Diagnostic Limitations

* **Deterministic Proxies**: Diagnostic rules in the MVP (e.g. `genre.erotic_fiction.desire_affects_decisions`) use deterministic lexical and structural proxies derived from explicit fields like `central_engine.want` or scene summary texts.
* **Explicit Evidence**: Rule evaluations report exact evidence snippets and level of proof, ensuring clear diagnostic feedback without claiming unrestricted semantic understanding.
