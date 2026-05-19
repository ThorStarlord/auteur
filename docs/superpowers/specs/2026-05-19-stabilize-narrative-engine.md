# Grill With Docs — Stabilizing Phase 0: The Narrative Engine

Date: 2026-05-19
Inputs: CONTEXT.md, identity.py, analyzer.py, docs/opinionated-narrative-engine.md

---

## Part 1: StoryIdentity Validation Spec (Locked)

### Q1. Where should structural and coherence validation of the Narrative Engine live, and how should it be executed?
**Answer**: 
We should introduce a dedicated, deterministic validation check directly in the `StoryIdentity` layer. When `auteur identity validate` runs, it must perform Pydantic schema validation *and* execute a suite of deterministic, LLM-free structural rules on the identity itself.

### Q2. What exact validation rules are required to declare a `StoryIdentity` structurally sound?
**Answer**: 
The validation runner must enforce the following rules:
1. **Want-Change Coherence**: The central engine's `want` and `change` must not be duplicate/identical (case-insensitive, whitespace-stripped).
2. **Genre Ending Tone Mismatch**: The chosen mode/ending tone (tragic or hopeful) must not violate the genre contract snapshot's `forbidden_mismatches` (e.g. forbidding tragic endings in Romance or hopeful endings in Grimdark), unless an explicit override is configured in `author_overrides`.
3. **Target Experience Avoidance Clash**: The avoided experiences list must not clash with the primary target experience or progression tone steps.
4. **Genre Runway / Length Class Mismatch**: The resolved length class of a medium must match or exceed the minimum viable length required by the genre contract scope profile, unless overridden by `runway_compression`.

### Q3. How should validation failures be presented to the user?
**Answer**: 
The command `auteur identity validate` should output a structured list of diagnostics (with rule, severity, layer, message, evidence, and repair options) to `stderr`, and exit with code `1` if there is any error.

### Q4. What is the behavior of the compilation step (`auteur blueprint seed` / `auteur identity compile`) when the identity has validation errors?
**Answer**: 
The compiler must run the identity validation checks before compiling. If any validation errors exist, the compilation process must abort, print the diagnostics, and exit with code `1`, preventing the creation of an invalid blueprint.

---

## Part 2: Phase 0 Recommendation Policy (Locked)

### Goals
To build `auteur identity recommend` as the entrypoint for Auteur. It translates a raw premise into a validated `StoryIdentity` YAML document, optimizing for opinionated genre contracts while allowing author-controlled exploration.

### CLI Surface
```bash
# Opinionated Mode (Default)
auteur identity recommend <input.md> --output story_identity.yaml

# Open-Ended Mode (Controlled escape hatch)
auteur identity recommend <input.md> --recommend-mode open-ended --candidates 3

# Acceptance Workflow
auteur identity accept-candidate <candidate.yaml> --output story_identity.yaml [--keep-candidates]
```

### Opinionated Mode (Default)
* Generates exactly **one** recommended story engine.
* Optimizes primarily using the `genre_aligned` basis (the genre-contract benchmark).
* Outputs a single canonical `story_identity.yaml` that is ready for validation and blueprint compilation.
* Automatically includes justification fields: `confidence`, `why_this_is_best`, and `rejected_directions`.

### Open-Ended Mode
* Generates contrasting, strategic candidates saved into a `story_identity_candidates/` directory:
  * `candidate_1.yaml` (flat standard `StoryIdentity` optimized for `genre_aligned`)
  * `candidate_2.yaml` (flat standard `StoryIdentity` optimized for `structurally_coherent`)
  * `candidate_3.yaml` (flat standard `StoryIdentity` optimized for `faithful_to_input`)
  * `recommendation_set.yaml` (machine-readable metadata wrapper storing candidate labels, tradeoffs, risks, and content hashes)
  * `comparison.md` (human-readable comparison file detailing differences)
* Candidate counts map directly to bases:
  * 2 candidates: `genre_aligned`, `structurally_coherent`
  * 3 candidates: `genre_aligned`, `structurally_coherent`, `faithful_to_input`
  * 4 candidates: `genre_aligned`, `structurally_coherent`, `faithful_to_input`, `emotionally_powerful`
* Succeeds if at least one valid candidate survives retries, unless `--strict-candidate-count` is passed.

### Validation and Repair Policy
During recommendation generation:
1. **Validation Check**: Every generated candidate is parsed into `StoryIdentity` and checked using `validate_identity()`.
2. **Repair Loop**: If `ERROR` diagnostics exist, Auteur initiates up to 3 repair retries by prompting the LLM with the previous attempt and the error messages.
3. **Author Override Constraint**: The LLM is strictly prohibited from adding `author_overrides` to escape validation errors.
4. **Warning Outcome**: Candidates with only `WARNING` diagnostics are kept, but lower the candidate's `confidence` score.
5. **No Invalid Emits**: Invalid candidates are never written to the canonical `story_identity.yaml` or candidate list. Failed attempts are only stored in `.auteur/runs/<timestamp>/` if `--debug` is active.

### Candidate Storage
* Every candidate file (e.g. `candidate_1.yaml`) is a standard, flat `StoryIdentity` to maintain portability with all CLI commands.
* Wrapper metadata resides in `story_identity_candidates/recommendation_set.yaml` using the `StoryIdentityRecommendationSet` structure.
* A `content_hash` check validates whether a candidate file has been modified after recommendation set index creation.

### Acceptance Workflow
* `auteur identity accept-candidate` accepts any flat `StoryIdentity` YAML path (whether `recommendation_set.yaml` is present or not).
* It runs `validate_identity()` on the target. If errors exist, it aborts. If warnings exist, it promotes but logs the warnings.
* By default, promoting cleans up `story_identity_candidates/` unless `--keep-candidates` is provided.

### best_basis Strategy
* **genre_aligned**: Optimize for primary genre contract promise, core truth, and tropes.
* **structurally_coherent**: Optimize for tight causal engines, conflict tightness, and act progression.
* **emotionally_powerful**: Optimize for stakes, trajectory, and psychology budgets (without exceeding the genre's ceiling unless explicitly requested).
* **faithful_to_input**: Optimize for preserving original, quirky premise details and author intentions.

### Subgenre Modifier Policy
* Treated as prompt-primary, validation-light modifiers via the `SubgenreModifier` class.
* Prompt guidance is injected dynamically into the compiler.
* `story_type.subgenres` is optional. An empty subgenre list is valid and means the story should be interpreted through the primary `GenreContract` only.
* Unknown, unsupported, or mismatched subgenres must emit `WARNING` diagnostics, never `ERROR` diagnostics. Subgenres are prompt modifiers, not required contracts, and they must not block StoryIdentity validation or blueprint seeding.


### Non-goals
* We will not build multi-contract inheritance or merge complex rules for subgenres.
* Open-ended mode is not the default behavior and is kept behind a flag.

---

## Part 3: MVP CLI Policy Grill (Locked)

### Q1. Should open-ended mode and `accept-candidate` be hidden or deleted from the CLI for the initial MVP?

**Recommended Answer**: Keep the code and tests for open-ended mode and candidate promotion, but hide them from MVP docs and default CLI help. The first public workflow should be relentlessly opinionated.

**Answer**: Approved. For the initial MVP, Auteur should expose only the opinionated recommendation path in user-facing docs and CLI help. Open-ended mode and `accept-candidate` remain implemented for internal/experimental use, but are hidden from onboarding, README examples, and default help output.

**Implementation**: Applied `argparse.SUPPRESS` to `--recommend-mode`, `--candidates`, `--strict-candidate-count`, and the `accept-candidate` subparser. All 249 tests continue to pass.

**MVP CLI policy**:
```yaml
mvp_cli_policy:
  public_default_path:
    command: "auteur identity recommend raw_idea.md --output story_identity.yaml"
    mode: "opinionated"
    status: "documented"

  open_ended_mode:
    status: "experimental_hidden"
    keep_implemented: true
    show_in_readme: false
    show_in_quickstart: false
    show_in_default_help: false

  accept_candidate:
    status: "experimental_hidden"
    keep_implemented: true
    show_in_readme: false
    show_in_quickstart: false
    show_in_default_help: false
```

### Q2. What exact content should the README Quick Start show, and what must be removed?

**Recommended Answer**: Replace the Quick Start with the strict 4-command opinionated path. Remove open-ended and `accept-candidate` examples entirely.

**Answer**: Approved. The Quick Start now shows exactly:
1. `auteur identity recommend … --output story_identity.yaml`
2. `auteur identity validate story_identity.yaml`
3. `auteur blueprint seed story_identity.yaml --output blueprint.yaml`
4. `auteur structure diagnose blueprint.yaml`

The open-ended `--recommend-mode` example and `accept-candidate` example are removed from the Quick Start and from the CLI Commands reference section.

**Implementation**: README `## Quick Start` and `### 1. Identity & Narrative Engine Seeding` sections rewritten. `accept-candidate` command block removed entirely from the CLI Commands section.

### Q3. Should the CLI Commands section `identity recommend` and `accept-candidate` entries be trimmed?

**Recommended Answer**: Yes. `identity recommend` description should be opinionated-only. `accept-candidate` entry should be removed entirely. No footnote needed in the CLI Commands section — the doc is reference, not tutorial.

**Answer**: Approved. `identity recommend` now describes the single opinionated path with constraint flags. `accept-candidate` entry is gone.

**Implementation**: Done as part of Q2 implementation.

### Q4. How should the argparse `==SUPPRESS==` display be cleaned up?

**Recommended Answer**: Apply a custom `_HideSuppressedFormatter(argparse.HelpFormatter)` to the `identity` parser that returns `""` for any action with `help == argparse.SUPPRESS`. This removes the `accept-candidate ==SUPPRESS==` line from subparser listing.

**Answer**: Approved. The suppressed subcommand name still appears in the usage line's `{…}` choices (an argparse limitation), but the description row is fully hidden.

**Implementation**: `_HideSuppressedFormatter` added to `cli.py`. Applied via `formatter_class=_HideSuppressedFormatter` on `p_identity`.

### Q5. Should `docs/opinionated-narrative-engine.md` be updated?

**Recommended Answer**: Keep the Open-Ended Mode section but retitle it `Experimental: Open-Ended Mode` to signal it is not the default user journey.

**Answer**: Approved. Retitled and a note added that it is hidden from default help output.

**Implementation**: Done in `docs/opinionated-narrative-engine.md`.

---

## Design Result (Part 3)

The MVP CLI surface is now exactly:

```bash
auteur identity recommend <premise> --output story_identity.yaml
auteur identity validate story_identity.yaml
auteur blueprint seed story_identity.yaml --output blueprint.yaml
auteur structure diagnose blueprint.yaml
```

Open-ended mode and `accept-candidate` remain implemented, tested, and functional but are suppressed from all user-facing surfaces (README, Quick Start, CLI help, and docs).

