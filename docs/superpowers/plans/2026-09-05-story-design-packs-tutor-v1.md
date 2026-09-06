# Story Design Packs and Creative Writing Tutor V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a backward-compatible Story Design Pack vocabulary, deterministic pack composition, and derived tutor guidance for four built-in V1 packs.

**Architecture:** Keep the qualified `GenrePack` subsystem unchanged as a compatibility surface. Add a separate typed `StoryDesignPack` envelope with reusable pedagogical content, a deterministic composition service that applies rule-strength semantics, and a tutor service that emits non-canonical guidance artifacts. Expose the services through `auteur design pack ...` and `auteur tutor ...` CLI commands without mutating StoryIdentity.

**Tech Stack:** Python 3.11+, Pydantic 2, YAML, pytest, existing argparse CLI.

---

### Task 1: Ratify the product contract

**Files:** `docs/opinionated-narrative-engine.md`, `docs/research/product-design-research.md`, `docs/product/creative-writing-tutor.md`

- [ ] Document learning value as a first-class success dimension, tutor authority, and the six-step interaction loop.
- [ ] State that design-pack knowledge, recommendations, and accepted StoryIdentity remain separate.
- [ ] Verify the docs do not redefine semantic layers or authorize silent mutation.

### Task 2: Add the typed Story Design Pack core

**Files:** create `src/auteur/story_design_packs/models.py`, `loader.py`, `registry.py`, `__init__.py`; test `tests/test_story_design_pack_core.py`

- [ ] Add typed reusable models for design options, craft principles, trade-offs, failures, teaching notes, questions, compatibility rules, decision hooks, applicability, and pack provenance.
- [ ] Add `PackKind` and `RuleStrength` semantics with deterministic content hashing.
- [ ] Load built-in YAML resources and retain the existing Genre Pack loader untouched.
- [ ] Reject malformed payloads and unknown pack kinds.

### Task 3: Add four built-in packs and deterministic composition

**Files:** create four YAML resources under `src/auteur/story_design_packs/data/`; create `composition.py`; test `tests/test_story_design_pack_composition.py`

- [ ] Populate Superhero, Anti-Hero, Hard Determinism, and Corporate Superhuman Metropolis with choices and teaching content.
- [ ] Derive selected options, reinforcing patterns, productive tensions, conflicts, questions, and provenance.
- [ ] Ensure composition is synthesized from explicit pair rules and never silently chooses a winner for conflicts.

### Task 4: Add derived Tutor Guidance

**Files:** create `src/auteur/story_design_packs/tutor.py`; test `tests/test_story_design_pack_tutor.py`

- [ ] Produce orientation, craft principle, story application, recommendation, alternatives, trade-offs, common failure, sources, consequence, next question, and `DERIVED / NOT CANON` authority.
- [ ] Make guidance deterministic and side-effect free.

### Task 5: Add beginner-facing CLI surfaces

**Files:** create `src/auteur/story_design_packs/cli.py`; modify `src/auteur/cli_parser.py`, `src/auteur/cli_dispatch.py`; test `tests/test_story_design_pack_cli.py`

- [ ] Implement `auteur design pack list|inspect|compose` and `auteur tutor recommend|explain|alternatives`.
- [ ] Support JSON output and plain-language output.
- [ ] Keep `auteur genre ...` commands and Erotic Fiction behavior unchanged.

### Task 6: Qualification

- [ ] Run focused tests, then the complete test suite.
- [ ] Run installed-wheel verification if available and record evidence without claiming product experiments are complete.
- [ ] Confirm no StoryIdentity mutation occurs from selection, composition, or tutor commands.

