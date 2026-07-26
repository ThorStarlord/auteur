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

## Author Overrides & Subversion

Authors can explicitly override recommended profile preferences (e.g., changing primary framing or resolution contracts).
* Overrides are explicitly stored in `genre_profile.author_overrides`.
* Intentional subversions downgrade potential genre warnings to informative logs rather than disabling validation entirely.
