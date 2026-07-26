# Genre Packs MVP — Erotic Fiction Vertical Slice Design

## 1. Problem Statement & Product Purpose

Auteur is an opinionated whole-story structure engine. Previously, genre constraints were represented via monolithic genre contracts and isolated subgenre modifiers. This model lacked a modular, versioned product-level container capable of expressing rich genre knowledge—including audience promises, emotional targets, narrative engine families, scene functions, conflict families, boundary rules, failure modes, evaluation rules, and subgenre profile inheritance.

The **Genre Pack** system introduces versioned, reusable genre knowledge packages without compromising Auteur's core philosophy:
> **A Genre Pack supplies versioned genre knowledge used to recommend and evaluate a story direction. Layer 1 records the commitments the author actually accepts.**

### Opinionated Recommendation Contract
1. **Auteur recommends strongly**: Given a raw premise or story input, the engine evaluates available profiles and recommends exactly **one primary subgenre profile**.
2. **Explanation & Rejected Alternatives**: The recommendation explicitly articulates why the primary profile is strongest, while providing clear rationale for every rejected profile (including what premise changes would make a rejected profile stronger).
3. **Author Retains Explicit Authority**: Recommendation is a derived/candidate artifact. Zero mutation occurs on `StoryIdentity` or `StoryBlueprint` prior to explicit author acceptance or override.
4. **Only Accepted Commitments Compile**: Downstream Layer 2 structure compilation and realization consume accepted Layer 1 Identity commitments, not raw unaccepted recommendations.

---

## 2. Canonical Semantic Layer Mapping

Genre Packs do **not** introduce a new "Genre Layer" in Auteur's five-layer semantic architecture:

```text
Layer 0 — Ontology:
  Reusable domain concepts (e.g. DesireArc, IntimacyBoundary, BoundaryTransition, PowerDynamic, IntimacyConsequence)

Layer 1 — Identity:
  Accepted genre, subgenre, target experience, emotional core, central engine, framing, and resolution commitments
  Recorded in StoryIdentity.genre_profile (GenreProfileCommitment) + canonical StoryIdentity fields

Layer 2 — Structure:
  Story-specific arcs, escalation, scene functions, setup/payoff, and ending plans

Cross-cutting:
  Recommendation (candidates), validation (contract enforcement), diagnostics (read-only findings),
  provenance (pack ID, version, hash), freshness, and versioning
```

### Critical Semantic Distinctions
$$\text{Pack Knowledge} \neq \text{Pack Recommendation (Candidate)} \neq \text{Accepted Story Identity (Layer 1)} \neq \text{Compiled Story Structure (Layer 2)}$$

---

## 3. Package Structure & Code Architecture

### Package Code Location
All Genre Pack Python implementation files reside in `src/auteur/genre_packs/`:

```text
src/auteur/genre_packs/
├── __init__.py
├── models.py          # Pack schema, rule strength, subgenre profiles, evaluation rules
├── loader.py          # Versioned YAML loading using importlib.resources
├── registry.py        # Pack registry & profile resolution
├── hashing.py         # Deterministic pack content hashing (SHA-256)
├── recommendation.py  # Recommendation engine & candidate artifact generation
├── validation.py      # Pack schema validation & genre-aware identity validation
├── diagnostics.py     # Read-only genre boundary & structural diagnostics
└── data/
    └── erotic_fiction/
        └── 0.1.0.yaml # Built-in versioned Erotic Fiction base pack + 3 subgenre profiles
```

---

## 4. Generic Genre Pack Schema

The `GenrePack` schema is a typed, versioned model defining reusable genre knowledge.

### Rule Strength Vocabulary
Rules and conventions within a pack are explicitly typed with one of six strengths:
1. `HARD_CONSTRAINT`: Mandatory structural boundary (e.g. erotic desire must be structurally central).
2. `STRONG_DEFAULT`: Expected standard pattern unless explicitly overridden (e.g. intimate scenes perform narrative work).
3. `COMMON_PATTERN`: Typical genre technique (e.g. secret longing or boundary testing).
4. `OPTIONAL_TECHNIQUE`: Available optional framing or beat (e.g. fantasy revelation).
5. `BOUNDARY_WARNING`: Alert for potential tone/genre drift or unintentionally opaque agency.
6. `INTENTIONAL_SUBVERSION_POINT`: Recognized expectation designed for deliberate authorial subversion.

### Schema Definition Summary (`GenrePack`)
* `pack_id`: Unique identifier (e.g. `erotic_fiction`)
* `display_name`: Human-readable title
* `version`: Semantic version string (e.g. `0.1.0`)
* `schema_version`: Integer schema version (e.g. `1`)
* `description`: Concise summary of genre scope
* `audience_promises`: List of `AudiencePromise` objects
* `emotional_targets`: List of `EmotionalTarget` objects (e.g. desire, anticipation, intimacy, vulnerability, transgression, release)
* `narrative_engines`: List of `NarrativeEngineFamily` objects (e.g. desire_and_resistance, intimacy_and_emotional_exposure, erotic_identity_transformation, power_negotiation, taboo_and_consequence)
* `core_conventions`: List of `CoreConvention` objects with rule strength
* `scene_functions`: List of `SceneFunction` objects (e.g. establish_attraction, test_boundary, renegotiate_power, transform_identity, deliver_release)
* `conflict_families`: List of `ConflictFamily` objects (e.g. desire_vs_duty, desire_vs_self_image, intimacy_vs_autonomy, control_vs_surrender)
* `framing_modes`: List of available framing modes (affirmative, romantic, heroic, horrific, tragic, comic, unsettling)
* `subgenre_profiles`: List of `SubgenreProfile` objects inheriting from the base pack
* `resolution_patterns`: List of `ResolutionPattern` objects
* `escalation_patterns`: List of `EscalationPattern` objects
* `boundary_rules`: List of `BoundaryRule` objects
* `failure_modes`: List of `FailureModeDefinition` objects
* `evaluation_rules`: List of `EvaluationRule` objects
* `revision_strategies`: List of `RevisionStrategy` objects

---

## 5. Subgenre Profile Inheritance (Erotic Fiction)

The base pack `erotic_fiction` (v0.1.0) supplies common genre knowledge. Three subgenre profiles inherit from and weight the base pack:

1. **`erotic_romance`**:
   * *Emphasis*: Desire, affection, trust, relational vulnerability.
   * *Resolution*: Emotionally satisfying relationship resolution (HEAV/HFN).
2. **`erotic_psychological_drama`**:
   * *Emphasis*: Desire, ambivalence, identity conflict, relational consequence.
   * *Resolution*: Psychological transformation and self-realization.
3. **`erotic_horror`**:
   * *Emphasis*: Desire, dread, fascination, vulnerability, destabilization.
   * *Resolution*: Survival, corruption, entrapment, or terrifying revelation.

---

## 6. Opinionated Recommendation Engine

Given premise inputs or Story Discovery data:
1. Evaluates all subgenre profiles in the pack.
2. Selects **exactly one primary profile** based on premise alignment.
3. Generates a derived `GenreRecommendation` artifact containing:
   * `recommendation_id`: Unique identifier
   * `recommended_pack_id`, `recommended_pack_version`, `pack_content_hash`
   * `recommended_profile_id`
   * `confidence`: Float between 0.0 and 1.0
   * `best_basis`: Basis for recommendation (`GENRE_ALIGNED`, `EMOTIONALLY_POWERFUL`, etc.)
   * `why_this_is_best`: Detailed rationale
   * `supporting_evidence`: Key premise phrases backing the decision
   * `recommended_emotional_targets`, `recommended_narrative_engine`, `recommended_framing`, `recommended_resolution_contract`
   * `rejected_profiles`: Detailed list of rejected profiles, why each was weaker, and premise changes that would strengthen it
   * `warnings` and `questions_or_uncertainties`

---

## 7. Layer 1 Identity Integration & Reconciliation Model

### Zero Pre-Acceptance Mutation
Generating or inspecting a recommendation leaves `StoryIdentity` completely untouched.

### `GenreProfileCommitment` Envelope
Upon explicit author acceptance or override, `StoryIdentity.genre_profile` is set:

```python
class GenreProfileCommitment(BaseModel):
    primary_pack_id: str
    primary_pack_version: str
    pack_content_hash: str
    primary_profile_id: str
    secondary_genres: list[str] = Field(default_factory=list)
    accepted_target_emotions: dict[str, float] = Field(default_factory=dict)
    accepted_narrative_engine: str
    accepted_framing: FramingCommitment
    accepted_resolution_contract: ResolutionContractCommitment
    adherence_posture: AdherencePosture = AdherencePosture.CONVENTIONAL
    source_recommendation_id: str | None = None
    author_overrides: list[GenreAuthorOverride] = Field(default_factory=list)
    accepted_at: str | None = None
```

### Single Operational Source of Truth & Synchronization
Existing `StoryIdentity` fields (`story_type`, `target_experience`, `central_engine`, `author_overrides`) remain the operational commitments for downstream compilation. Acceptance performs atomic synchronization:
1. `story_type.genre` $\rightarrow$ `Genre.EROTIC_FICTION` (or canonical mapping) and `story_type.subgenres` $\rightarrow$ `[primary_profile_id]`.
2. `target_experience` $\rightarrow$ updated with primary emotional target and progression.
3. `central_engine` $\rightarrow$ validated for compatibility with the accepted engine family without overwriting story-specific text.
4. `author_overrides` $\rightarrow$ preserves existing overrides and adds namespaced genre override keys.

---

## 8. Pack Provenance & Freshness

* `GenreProfileCommitment` pins the `primary_pack_version` and `pack_content_hash`.
* If a pack file on disk is updated to a newer version, existing accepted identities remain pinned to their accepted version/hash and continue to validate cleanly.
* A recommendation created against an older pack version is flagged as `RECOMMENDATION_STALE` if the pack definition changes before explicit acceptance.

---

## 9. Genre-Aware Validation & Diagnostics

### Identity Validation (`identity.validate_identity()`)
Validates that accepted commitments in `genre_profile` are coherent with `StoryIdentity`:
* Referenced pack and profile exist.
* Engine family and primary emotions are valid for the profile.
* Un-overridden contradictions produce `DiagnosticSeverity.ERROR`.
* Explicit author overrides downgrade expected deviations to `DiagnosticSeverity.WARNING`.

### Genre-Aware Diagnostics (Layer 2 Read-Only)
Four required evaluation rules for Erotic Fiction:
1. `desire_affects_decisions`: Desire must materially influence key decisions.
2. `intimate_scenes_change_state`: Intimate scenes must alter narrative/character state.
3. `scene_function_diversity`: Consecutive intimate scenes must not blindly repeat the same scene function.
4. `resolution_erotic_arc_payoff`: The final act must resolve the accepted erotic arc.

Diagnostics are strictly read-only findings that cite exact evidence without mutating structure.

---

## 10. Typed Failure Behavior

All failures raise structured errors without partial mutation:
* `PACK_NOT_FOUND`: Referenced pack ID does not exist in registry.
* `PACK_INVALID`: Pack schema validation failed.
* `PROFILE_NOT_FOUND`: Referenced subgenre profile ID not found in pack.
* `RECOMMENDATION_NOT_FOUND`: Recommendation ID invalid or missing.
* `RECOMMENDATION_STALE`: Pack updated after recommendation was generated.
* `ACCEPTANCE_REQUIRED`: Attempted to compile downstream without accepted Identity.
* `INVALID_OVERRIDE`: Override syntax or rationale malformed.
* `IDENTITY_CONFLICT`: Unreconciled contradiction between genre profile and identity fields.
* `ALREADY_ACCEPTED`: Attempted duplicate acceptance without explicit force flag.

---

## 11. CLI Workflow

Human-readable and JSON outputs agree on all commands:
* `auteur genre pack list`: List all installed genre packs.
* `auteur genre pack inspect <pack_id>`: Inspect pack schema, rules, profiles.
* `auteur genre recommend [--project P] [--pack P]`: Generate opinionated recommendation candidate.
* `auteur genre recommendation inspect <rec_id>`: Inspect candidate recommendation details.
* `auteur genre recommendation accept <rec_id>`: Explicitly accept candidate into `StoryIdentity`.
* `auteur genre recommendation override <rec_id> --override <spec>`: Accept candidate with explicit author overrides.
* `auteur genre profile show [--project P]`: Display active accepted `genre_profile`.
* `auteur genre validate [--project P]`: Validate accepted Identity against genre pack.
* `auteur genre diagnose [--project P]`: Run Layer 2 structural diagnostics.

---

## 12. Deferred Scope

The following items are explicitly deferred from the MVP:
* Remote pack download/registry.
* Multi-genre blending engines.
* Automatic prose drafting or manuscript mutation.
* Full superhero mode or mystery pack implementations.
* LLM-only validation without typed evidence.
* Automated pack migration scripts for existing projects.
