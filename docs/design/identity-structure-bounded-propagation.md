# Implementation Design — Bounded Identity-to-Structure Propagation

Status: IMPLEMENTATION DESIGN, **Revision 2** (response to human design
review). No production code or tests were changed. Revision 1 was classified
NEEDS_SMALL_DESIGN_REVISION by the human review; all review items are resolved
in this revision (§6-§18). This document is the successor design artifact to
the closed discovery experiments.

Branch: `design/identity-structure-bounded-propagation`
Base: `c73d344be26c7ed310d5753153fda721d63c8e78` (frozen Experiment-3 terminal,
`discovery/identity-structure-role-rule-validation`)

## 1. Problem statement

`compile_to_blueprint` seeds a `StoryBlueprint` from a `StoryIdentity`, but it
currently ignores three author-owned commitment fields and cannot represent
named characters or their structural commitments:

- `StoryIdentity.not_this` (`src/auteur/identity.py:97`) — never read by the
  compiler; used only in contract-fit keyword text
  (`src/auteur/cli_handlers.py:235-250`) and identity validation.
- `StoryIdentity.rejected_directions` (`src/auteur/identity.py:104`) —
  documentation-only.
- `StoryIdentity.author_overrides` (`src/auteur/identity.py:105`) — read only
  as validation-bypass markers (`"ending_tone"`, `"runway_compression"`,
  `identity.py:165,284`).
- Characters are seeded with fixed compiler placeholders
  (`identity.py:915-963`): `Protagonist`/`Antagonist`, `Detective`/`Culprit`,
  `Lover A`/`Lover B`, with hard-coded roles (`PROTAGONIST`/`ANTAGONIST`) and
  arc types. An accepted Identity that names its characters or gives a
  character the central transformation is not represented in the blueprint.

As a result, accepted author commitments made at Identity time are either
silently dropped at compile time or left to be re-derived from prose later.

## 2. Validated product evidence

Three closed discovery experiments (docs-only, in the repository at
`experiment/`, `experiment-2/`, `experiment-3/`), each frozen with terminal
commits and human verdicts:

| Experiment | Terminal commit | Verdict (human-confirmed) |
|---|---|---|
| 1 — identity-structure-validation | `03d8ea2` | PROMISING: stronger propagation appears valuable |
| 2 — identity-structure-deterministic-tier | `0ae48b4` | MIXED_NARROWER_RULES_NEEDED |
| 3 — identity-structure-role-rule-validation | `c73d344be26c7ed310d5753153fda721d63c8e78` | Role rule validated 4/4 semantically; heuristic mechanism NOT production-approved |

Experiment-2 mechanism verdicts (`experiment-2/02-conclusion.md`):

- **A1-A3 direct contract propagation — SUPPORTED NOW (strong).** The
  experiments validated that explicit commitments propagate verbatim into the
  contract with zero invention. **What was validated is the propagation of
  explicit commitments; the exact destination fields were NOT validated as
  final production representation** (see Revision-2 §6 — destinations are
  re-derived from consumer semantics, not from the experiment fixtures).
- **A4 explicit naming — SUPPORTED NOW, modest value.**
- **B1 role-from-engine/change — PROMISING, needed narrower validation.**

Experiment-3 verdict (4/4 falsification pattern):

1. already-correct role → NOT_APPLICABLE (restraint; byte-identical baseline);
2. changing explicit opponent → NOT_APPLICABLE (no recast);
3. ambiguous transformation subject → BLOCKED_INSUFFICIENT_EXPLICIT_INPUT
   (fail-closed);
4. explicit co-transforming lead in contradictory role → DIRECT_DETERMINISTIC
   correction (deuteragonist/growth, 0-100).

The author's recorded distinction: the **semantic rule** is validated for
design; the prototype **detection mechanism** (opposition-verb lists,
first-name token extraction, coordinated-subject regex —
`experiment-2/01-rules.md` §1.2, `experiment-3/01-rules.md` R1/R2) is NOT
production-approved. Design must prefer explicit structured representation
over text recovery, and must keep BLOCK behavior whenever the relationship
cannot be established safely.

The `overthrow` prototype incident (a coverage gap in the textual
mechanism) is the standing evidence that textual heuristics are
coverage-sensitive prototype instruments. This design therefore contains **no
text extraction whatsoever**: no verb lists, no regexes, no name-token
parsing, no coordinated-subject patterns.

Revision-2 additions (human review, 2026-08-XX): the review confirmed the
bounded deterministic direction and added seven engineering/semantic
requirements: (1) prove any Identity schema gap before adding fields; (2) no
invented default `arc_type`; (3) justify contract destinations by semantic
meaning; (4) no magic-string denylist for `author_overrides`; (5) diagnostics
must not depend on the CLI caller; (6) justify any new provenance field; (7)
production feature branch must start from `main`, not discovery history. All
seven are resolved below.

## 3. Non-goals

- No generalized "propagation engine"; no LLM inference; no creative
  inference of characters, locations, organizations, incidents, plot events,
  motivations, relationships, backstory, or unstated genre requirements.
- No genre-knowledge work: no Genre Pack changes, no cozy-mystery templates,
  no fallback genre data (Experiment-2 Case B finding stays a separate
  product hypothesis).
- No changes to the proposal/revision lifecycle for post-hoc repairs, beyond
  emitting diagnostics that the existing proposal machinery can already
  consume.
- No propagation of `StoryIdentity.author_overrides` (workflow/compiler
  control field; see §6.1).
- No new CLI commands in slices 1-3; diagnostics surface through the existing
  compile handler AND the analyzer (universal path, §10).
- No serialization of NOT_APPLICABLE restraint outcomes (see §11 — restraint
  leaves no trace; only applied consequences and BLOCKED refusals are
  recorded).

## 4. Current production architecture

```
StoryIdentity (src/auteur/identity.py:89)
    │   fields: title, core_answer, target_experience, story_type,
    │   central_engine (HighLevelCentralEngine, L69: want/resistance/
    │   conflict/stakes/change — all plain str), not_this, open_questions,
    │   alternatives, recommendation_mode, best_basis, why_this_is_best,
    │   rejected_directions, author_overrides, genre_contract_snapshot,
    │   genre_profile
    │   validate_identity() (L116) → list[StructureDiagnostic]
    ▼
compile_to_blueprint(identity) (src/auteur/identity.py:668)
    │  1. ProjectIdentity construction        (L679-692)
    │  2. StructuralConstants / ScopeContract (L694-730)
    │  3. AuthorAudienceContract construction (L749-761)
    │     + profile-derived obligations       (L763-797: genre_profile →
    │       expected_elements / rejected_outcomes / profile_emotional_targets)
    │  4. EmotionalBlueprint                  (L799-840)
    │  5. ThematicCore                        (L842-863)
    │  6. StoryEngine + seeded threads        (L865-913, genre subplot
    │       templates via _get_recommended_subplots L448)
    │  7. Characters                          (L915-963: placeholder names
    │       and roles by genre/mode)
    │  8. TensionWaveform                     (L965-997)
    │  9. Assemble + validate StoryBlueprint  (L1000-1009)
    │     ProfileDerivation provenance        (L1012-1025, only when
    │       profile obligations were applied)
    ▼
StoryBlueprint (src/auteur/blueprint.py:718)
    │  identity: ProjectIdentity, structure: StructuralConstants,
    │  story_engine, contract: AuthorAudienceContract (L466),
    │  emotional_design, characters: list[Character] (L543),
    │  tension_waveform, theme, profile_derivation: ProfileDerivation|None
    │  (L729), agent-model routing fields
    ▼
Analyzer / diagnostics
    │  structure.analyzer.analyze_structure (src/auteur/structure/analyzer.py:67)
    │  run_all_diagnostics (L22) merges bible/outline audits
    │  character.analyzer.analyze_character_categorization
    │    (src/auteur/character/analyzer.py:23; _diagnose_character_roles L283:
    │     characters.multiple_protagonists L294, characters.no_antagonist L309)
    │  Profile contract rules D-RES-001/002/003 (analyzer.py:1595/1647/1707)
    │    gated on blueprint.profile_derivation (L1577)
    ▼
Proposals (author-decision path, never auto-mutates)
    │  StructureProposal (structure/proposal_models.py:53),
    │  propose_repairs_from_diagnostics (proposal_generation.py:342),
    │  apply_proposal_to_blueprint (proposal_application.py:35, .meta.yaml
    │    sidecar), propagate_acceptance (structure/freshness.py:19)
```

Compile callers (the behavior lands in all of them by being inside
`compile_to_blueprint`):

- `cli_handlers.handle_compile_to_blueprint` (`src/auteur/cli_handlers.py:345`,
  compile call L371) — validates first, compiles, returns `CompileBlueprintData`.
- `narrative_orchestration/orchestrator/outline_builder.py:290-293` — reads
  only `estimated_chapters`; unaffected by propagation content.
- `series/compiler.py:9` and `book/builder.py:7` build `StoryIdentity`
  objects (not blueprints) and write `not_this` scoping instructions
  (`series/compiler.py:18`) — see §12 interaction.

Existing provenance precedent: `ProfileDerivation`
(`src/auteur/blueprint.py:689-710`: `source_field`, `recommendation_id`,
`derived_at`, `obligations_applied`) — the only field-level derivation
provenance; set exclusively in `compile_to_blueprint` (L1012-1025) when
obligations were applied. `ArtifactStore` (`src/auteur/provenance/store.py:152`)
is file-level (hash/dependency), not field-level.

Structured character concepts that exist downstream, and why they do not
cover the Identity gap (full demonstration in §8):

- `auteur.character.models.CharacterIdentity` (models.py:357) — rich
  per-character **content** model attached to blueprint `Character.identity`
  (`blueprint.py:552`), populated after compile by character tooling. It has
  **no `name` field** and no primary role ("primary role lives on
  `Character.role`", models.py:32): it is not a character declaration.
- `CharacterCategorization` (models.py:382) / `RoleInference` (models.py:316)
  — inferred, blueprint-side.
- `UniverseIdentity` (`universe/models.py:55`) — settings/mythology/timeline/
  constraints; no cast.
- `StoryBible` characters (`series/bible.py:55`) — live `CharacterState`
  entries, blueprint-side.
- Contract consumers that determine destination semantics:
  `critic/contract.py:57,90` (custom_rules scanned line-by-line,
  unconditionally), `critic/contract.py:92` + `analyzer.py:759,788-792`
  (forbidden_tropes compared against genre-contract trope keys),
  `analyzer.py:1631-1662` (rejected_outcomes enforcement gated on
  `profile_derivation` obligations).

## 5. Proposed architecture

**Recommendation: Option B-lite — one small explicit propagation component,
invoked as the final step of `compile_to_blueprint`, with Option C as the
safety boundary for authored blueprints.** This matches the production shape
preferred in the human review:

```
A1/A3 contract commitments
        ↓
small deterministic propagation logic (identity_propagation module)

A4 naming
        ↓
only when structured correspondence is explicit

role consistency
        ↓
structured evidence available?
   ┌────┴────┐
  yes        no
   ↓          ↓
bounded     diagnostic /
rule        author decision
```

```
StoryIdentity
    ▼
compile_to_blueprint (unchanged entry point, unchanged signature)
    ▼
identity_propagation.propagate_identity(identity, blueprint)
  ├─ contract propagation   (A1, A3) — §6
  ├─ naming                 (A4)    — §8
  └─ role consistency       (B1+R1+R2 semantics) — §7
    → PropagationReport (in-memory; per-rule classifications)
    → outcomes (applied + blocked) persisted on
      blueprint.identity_propagation (new optional field)
    → NOT_APPLICABLE restraint outcomes are NOT persisted
    ▼
StoryBlueprint (existing validator must still pass)
    ▼
Analyzer (universal diagnostics surface)
    │  new rule family identity.propagation.* converts persisted
    │  BLOCKED outcomes into StructureDiagnostics — every caller of
    │  run_all_diagnostics/analyze_structure observes the same semantics
    ▼
Proposals (author-decision path for unresolved contradictions)
```

Design decisions (Revision 2):

1. **New module** `src/auteur/identity_propagation.py` — pure deterministic
   functions, no classes beyond the report models. Chosen over inline code in
   `identity.py` because the role rule is a staged decision with its own
   test matrix, and the report shape is a first-class artifact; chosen over a
   package because YAGNI applies (one module, three rules).
2. **Hook inside `compile_to_blueprint`**, after character construction
   (step 7) and before assemble/validate (step 9), so every caller (CLI and
   outline builder) receives identical behavior and no caller can bypass it.
   The public signature `compile_to_blueprint(identity) -> StoryBlueprint`
   does not change — this remains clean because the outcomes are persisted on
   the blueprint itself (no hidden side channel; §10-§11).
3. **New optional field** `StoryBlueprint.identity_propagation:
   IdentityPropagationDerivation | None = None` — set when at least one
   outcome occurred (applied OR blocked). NOT_APPLICABLE restraint leaves no
   trace, so blueprints of truly inert identities remain byte-identical
   (see §12). Justification vs existing mechanisms: §11.
4. **Small schema addition** to `StoryIdentity` (slices 2-3): an explicit
   structured character declaration. The semantic gap is demonstrated in §8
   (Option C recommended; Option D fallback).
5. **Fail-closed vocabulary in production**: the experiment enums
   (`DIRECT_DETERMINISTIC`, `NOT_APPLICABLE`,
   `BLOCKED_INSUFFICIENT_EXPLICIT_INPUT`) remain outcome classifications in
   the provenance record, not new blueprint semantics; production diagnostics
   use the existing `StructureDiagnostic` model with new rule ids under
   `identity.propagation.*`.

## 6. Exact mappings — contract propagation (slice 1, Revision 2)

All mappings are verbatim, deduplicated, deterministic, idempotent, and
mutate only the freshly constructed blueprint inside `compile_to_blueprint`
(never the identity — the existing no-mutation invariant, asserted by
`tests/test_profile_propagation.py:716-732`, extends to the new rules).

Destinations are chosen by **consumer semantics**, not list-type convenience:

| Rule | Source (model/path) | Source semantics | Destination (model/path) | Why this destination |
|---|---|---|---|---|
| A1 | `StoryIdentity.not_this[]` (`identity.py:97`) | Author-authored negative constraints: "this story is not X" (free sentences, e.g. "a story where only one partner ever has to be vulnerable") | `AuthorAudienceContract.custom_rules` (`blueprint.py:494`) | `custom_rules` is documented as "Free-text rules the Critic checks line-by-line" and is consumed **unconditionally** (`critic/contract.py:57,90`). `forbidden_tropes` is compared against genre-contract trope keys (`analyzer.py:759,788-792`) — free sentences are inert there and would pollute a trope-shaped field. |
| A3 | `StoryIdentity.rejected_directions[]` (`identity.py:104`) | Explicitly rejected directions ("Don't make the mother secretly responsible for the accident") | `AuthorAudienceContract.custom_rules` | Same free-text enforcement bucket; the source distinction is preserved by the provenance record (`source="rejected_directions[i]"`), not by storage location. `rejected_outcomes` was NOT chosen: its documented semantics are tied to the genre-profile resolution contract and its enforcement (D-RES-002) is gated on `profile_derivation` obligations (`analyzer.py:1631-1662`) — identity items there would be stored but never enforced. |
| A2 | ~~`author_overrides`~~ | — | **DROPPED** | See §6.1. |

Behavioral contracts:

- **Deduplication**: exact-match dedupe against the destination list
  (case-sensitive, same policy as the existing profile dedupe at
  `identity.py:780,789-795`). Same commitment appearing twice in the identity
  → one entry. Profile-derived and identity-derived items converging on the
  same string → one entry (both are author-accepted; neither wins).
- **Ordering**: identity items are appended after profile-derived items, in
  source field order, preserving input list order. Deterministic across runs
  (no set iteration). Existing `test_profile_propagation.py:660-671`
  ordering invariant extends to the new appends.
- **Precedence**: no new precedence semantics are invented. All sources are
  author-accepted commitments; the only conflict rule is a **refusal**, not a
  winner: if after propagation the same normalized string (casefold, stripped)
  appears in both `expected_elements` and `custom_rules`, the outcome is
  BLOCKED with an AUTHOR-DECISION-REQUIRED diagnostic
  (`identity.propagation.contract.conflict`); nothing is removed — the author
  resolves it.
- **Idempotence**: propagation runs on a fresh blueprint per compile; repeated
  `compile_to_blueprint` on the same identity yields identical output
  (existing idempotence tests must stay green; new tests cover the new
  fields).
- **Absence**: identity with empty `not_this`/`rejected_directions` → no
  additions, no provenance field (byte-identical blueprint).

### 6.1 Why `author_overrides` is not propagated (Revision 2)

Review finding: propagating `author_overrides` would mix two categories —
story-semantic commitments and workflow/compiler control directives — and any
filter would require an ever-growing magic-string denylist (the same pattern
rejected for the Experiment-3 verb lists).

Established facts:

1. In production today, `StoryIdentity.author_overrides` is consumed as a
   **workflow/compiler control field** by the validation gates: the known
   members `"ending_tone"` (`identity.py:165`) and `"runway_compression"`
   (`identity.py:284`) are exact-match bypass markers consumed by
   `validate_identity`; the CLI contract-fit handler additionally forbids
   auto-generating overrides (`cli_handlers.py:763-776`). **Repository usage
   is semantically mixed, not purely control**: the canonical example
   `examples/story_identity.yaml` carries a free-text story mandate in
   `author_overrides` (`"Keep Kael's final transformation tragic rather than
   redemptive."`). That mandate is not propagated or enforced by this feature;
   the field therefore cannot be relied on as a pure control channel. A future
   identity-level free-text mandates field (e.g. `author_constraints`) is a
   separate product decision (see the fix-pass note, section 19.8).
2. Story-semantic overrides already have a **structured home at profile
   level**: `GenreAuthorOverride` (`genre_packs/models.py:206-226`:
   `target_expectation`, `replacement_value`), propagated through the
   existing profile path (`identity.py:770-786`).
3. The Experiment-2 A2 rule assumed free-text mandates lived in
   `author_overrides`; that assumption is not supported by the current
   production consumers (the mixed usage in fact 1 is example-fixture data,
   not a validated mandate mechanism).

Decision: **A2 is dropped from the design.** `author_overrides` keeps its
existing bypass-marker semantics and is never propagated. If the product later
needs an identity-level free-text mandates field, that is a separate product
decision with its own named field (e.g. `author_constraints`), not a
repurposing of the control field. This eliminates the denylist entirely.

## 7. Role-rule semantic design (slice 3, Revision 2)

The validated semantic rule is translated onto the real model. **Source of
facts: a small explicit schema relationship on StoryIdentity** — no prose
recovery (gap demonstrated in §8). Recommended model (slices 2-3):

```python
class IdentityCharacter(BaseModel):
    """Author-declared named character at Identity time (commitment layer).

    This is a 4-field commitment reference, NOT a duplicate of
    auteur.character.models.CharacterIdentity (the blueprint-side content
    model). It reuses the existing enum vocabularies CharacterRole
    (blueprint.py:225) and ArcType.
    """
    name: str = Field(min_length=1)
    structural_role: CharacterRole | None = None   # explicit author assignment
    undergoes_central_change: bool = False          # participates in the
                                                    # central transformation
    arc_type: ArcType | None = None                 # EXPLICIT ONLY — never
                                                    # defaulted (§7 Stage 4)

# on StoryIdentity:
characters: list[IdentityCharacter] = Field(default_factory=list)
```

Product semantics (independent of the experiments): the author declares the
story's named characters and their structural commitments at Identity time —
the structured counterpart of prose already required in `central_engine`.
Every field except `name` is optional; `characters` defaults to `[]`, so
existing identities are untouched (fail-closed).

Decision stages (translated from Experiment-3 §4, `experiment-3/01-rules.md`):

- **Stage 0 — explicit commitment gate.** `characters` is empty or no entry
  has `undergoes_central_change=True` → `NOT_APPLICABLE` (no explicit
  transformation commitment; no action; this is the production form of
  "subject not extractable"). An identity whose prose implies a change but
  declares no structured subject is deliberately inert.
- **Stage 1 — transformation subjects.** Subjects = declared entries with
  `undergoes_central_change=True`. Any subject with
  `structural_role == CharacterRole.ANTAGONIST` is **explicit opposition
  framing** → that subject is `NOT_APPLICABLE` (opposition precedence; the
  Experiment-3 case-2 outcome — a changing explicit opponent is not recast).
- **Stage 2 — already represented.** Subject whose name already names a
  blueprint slot whose role is not `ANTAGONIST` (or equals the declared
  `structural_role`) → `NOT_APPLICABLE` (restraint; the Experiment-3 case-1
  outcome — the blueprint already represents the accepted transformation).
- **Stage 3 — ambiguity.** `BLOCKED_INSUFFICIENT_EXPLICIT_INPUT` when the
  correspondence cannot be established unambiguously: a subject name matches
  no blueprint slot and no eligible placeholder slot exists; two subjects map
  to the same slot; or more than one eligible placeholder slot exists.
  No mutation. (Fail-closed; the production form of the Experiment-3 case-3
  outcome. The prototype's coordinated-subject regex is replaced by: an
  ambiguous declaration is simply not a single unambiguous subject.)
- **Stage 4 — correction (AUTO-FIXABLE, compile-time only, ATOMIC).**
  Exactly one subject, no opposition framing (Stage 1), no existing
  representation (Stage 2), unambiguous correspondence (Stage 3), the target
  slot is a **compiler placeholder** (`name` in the frozen placeholder set
  `{protagonist, antagonist, lover a, lover b}`) with role `ANTAGONIST` (or a
  role contradicting the declared `structural_role`), **and the declared
  entry provides `arc_type` explicitly** → deterministic correction:
  - `characters[slot].name` := subject name;
  - `characters[slot].role` := declared `structural_role` or `DEUTERAGONIST`
    (the only allowed default — it is the role the validated rule itself
    prescribes for a co-transforming lead, not an invented creative choice);
  - `characters[slot].arc_type` := declared `arc_type` — **never defaulted**;
  - `arc_start_percentage` := 0, `arc_end_percentage` := 100 (the
    transformation spans the story; satisfies the `Character` validator's
    non-flat-arc bounds, `blueprint.py:561-575`).
  This is the Experiment-3 case-4 outcome, classified
  `DIRECT_DETERMINISTIC` and recorded in provenance.
- **Stage 4a — correction without explicit arc → BLOCK.** If the declared
  entry does not provide `arc_type`, the correction is **not** performed
  (atomicity: no name/role mutation without a defensible arc). Outcome:
  `BLOCKED_INSUFFICIENT_EXPLICIT_INPUT` with an AUTHOR-DECISION-REQUIRED
  diagnostic (`identity.propagation.role_rule.arc_undeclared`): the author
  either declares `arc_type` on the Identity, or accepts a repair proposal
  (existing proposal path) that sets name/role/arc together. **No creative
  default arc exists in production** (review decision: "default_arc_type_for_
  role_correction: NONE"). An existing compatible explicit arc is preserved
  where one exists — which in the compile-time path never applies (the
  placeholder slot is `FLAT` 0/0, incompatible with a transformation
  commitment); it applies in the later-lifecycle proposal path, where a
  blueprint character that already carries a non-flat explicit arc keeps that
  arc and only the role/name contradiction is patched.
- **Stage 5 — authored-blueprint boundary (Option C).** If the contradictory
  slot is **not** a compiler placeholder (a real authored name/role), the
  compile step does NOT mutate. The contradiction is AUTHOR-DECISION-REQUIRED:
  outcome recorded as BLOCKED
  (`identity.propagation.role_contradiction.unresolved`), surfaced as a
  `StructureDiagnostic` by the analyzer (§10), and consumable by the existing
  proposal machinery (`propose_repairs_from_diagnostics`,
  `structure/proposal_generation.py:342`) so the author can select a repair.
  No automatic recasting of authored content, ever.

Why placeholder-slot corrections are safe to auto-apply at compile: at
compile time the placeholder slot is a compiler artifact, not an authored
choice — no author-owned value is overwritten. Everything else goes through
the author-decision path. This is the production expression of "ambiguity
should not cause creative guessing".

## 8. Structured-data-vs-text decision (Revision 2: gap demonstration)

### 8.1 What the validated role rule needs, semantically

1. which named character(s) undergo the central transformation (the
   transformation subject);
2. whether such a character is explicitly framed as principal opposition;
3. whether the author explicitly assigns a structural role or arc to that
   character;
4. enough information to detect ambiguity (multiple subjects, conflicting
   assignments).

### 8.2 Is this information already structured anywhere?

Checked inventory (verified against source):

| Candidate | Location | Verdict |
|---|---|---|
| `StoryIdentity` fields | `identity.py:89-107` | No character-bearing field. `central_engine` is prose-only (`identity.py:69-74`). `not_this`/`rejected_directions` are free-text constraints, not character facts. |
| `HighLevelCentralEngine` | `identity.py:69-74` | All five fields are `str`. No structured subject. |
| `CharacterIdentity` | `character/models.py:357-374` | Blueprint-side **content** model. No `name` field; primary role explicitly lives on `Character.role` (`models.py:32` docstring). Attached to blueprint characters (`blueprint.py:552`) and populated after compile by character tooling. Cannot declare a cast. |
| `CharacterCategorization` / `RoleInference` | `models.py:382` / `316` | Inferred, blueprint-side, post-compile. |
| `UniverseIdentity` | `universe/models.py:55-` | Settings, mythology, timeline, cross-story constraints — no cast. |
| `StoryBible` characters | `series/bible.py:55`, `structure/state.py:23` | Live `CharacterState` snapshots, blueprint-side. |
| `GenreProfileCommitment` | `genre_packs/models.py` | Profile-level commitments (emotions, resolution contract, `GenreAuthorOverride` at L206) — no characters. |

**Conclusion: no existing structured model at the Identity boundary can
supply the role rule's facts.** Every existing character concept is
blueprint-side and post-compile; the compiler consumes only `StoryIdentity`.
The required information is genuinely absent, not merely inconvenient to
reach.

### 8.3 Options compared (per review)

**A. Reuse existing structured data** — impossible: there is no identity-side
structured data to reuse (§8.2). Reusing the blueprint-side models would
require the compiler to first create characters and then read
`Character.identity` back — circular; and `CharacterIdentity` lacks `name` and
primary role by design.

**B. Minimal references/commitments added to existing Identity structure**
(e.g. `central_engine.change_subjects: list[str]`, plus separate scalar
fields for protagonist/antagonist names) — analyzed and rejected:
- it adds the **same number of new fields** (a list per concept), scattered
  across `HighLevelCentralEngine` instead of one cohesive declaration;
- opposition framing ("explicitly framed as opposition") has no natural
  scalar home — a bare `opposition: list[str]` is semantically weaker than a
  role assignment and cannot express "this character IS the antagonist"
  without duplicating `CharacterRole`;
- ambiguity detection (two characters claiming the same role) requires
  comparing fields across the engine, which is exactly what a small list
  model does naturally;
- it reuses no existing structure either — the flat fields would be new
  schema with weaker semantics, so it is not smaller, just more fragmented.

**C. `StoryIdentity.characters: list[IdentityCharacter]` (recommended)** —
the smallest relation that expresses the validated semantics: named
character + optional explicit role + central-change commitment + optional
explicit arc. It is a **commitment layer, not a duplicate character model**:
four fields vs `CharacterIdentity`'s 20+; it reuses the existing enum
vocabularies (`CharacterRole`, `ArcType`); it is author-owned Identity input
(the creative brief names its cast — the structured counterpart of what
authors already type into `central_engine` prose); and one addition serves
both validated features (naming A4, role rule B1). Author-owned Identity
commitment — not an experiment storage convenience: the field's product
semantics stand alone ("the author declares who the story's named characters
are and what they commit to structurally").

**D. Diagnostics-only role behavior** — fallback: no schema change; role
contradictions surfaced by a new analyzer rule that can only compare
blueprint-internal facts (it would have no identity commitments to compare
against, so it degrades to existing role heuristics like
`characters.no_antagonist`). Adopted as the fallback if C is rejected
(slices 2-3 then ship as diagnostics/proposals only).

**Recommendation: C**, with D as the documented fallback. If C is rejected at
the implementation gate, slice 1 (contract propagation) ships alone and
naming/role correction are deferred to the author-decision path.

### 8.4 Naming (A4) on the same roster

- Declared entry with explicit `structural_role` → the unique blueprint slot
  with that role whose current name is a compiler placeholder → `name :=`
  declared name (e.g., declared `structural_role=protagonist, name="Rowan"` →
  the `Protagonist`/`Lover A` slot is named `Rowan`).
- Two declared entries claiming the same role → BLOCKED (no naming).
- Declared entry without `structural_role` → no naming.
- No entry → no naming. Unnamed entities are never invented, and opponents
  without a declared name stay unnamed (the Experiment-2 "culprit stays
  unnamed" restraint).
- Naming never depends on arc: a named character without `arc_type` is named
  normally.

## 9. Ambiguity / fail-closed behavior

- Absent structured commitment → no action (`NOT_APPLICABLE`), blueprint
  unchanged, no trace.
- Ambiguous declaration → `BLOCKED_INSUFFICIENT_EXPLICIT_INPUT` recorded in
  the provenance record; blueprint structure unchanged; the analyzer emits a
  WARNING `StructureDiagnostic` (§10) so the refusal is visible to every
  caller.
- Correction without explicit arc → BLOCKED + AUTHOR-DECISION-REQUIRED
  diagnostic (§7 Stage 4a).
- Contradictory authored content → AUTHOR-DECISION-REQUIRED diagnostic +
  proposal path (Stage 5), never auto-mutation.
- The production system has no path that invents narrative facts; the
  no-invention list from `experiment-2/01-rules.md` §5 is adopted verbatim as
  an invariant (no new characters, locations, organizations, incidents,
  relationships, motivations, backstory, trope ids, or normalized labels).

## 10. Universal diagnostic / refusal path (Revision 2, review item 5)

Semantic correctness must not depend on which caller invoked
`compile_to_blueprint`. Design:

1. **Persist outcomes on the blueprint** (not a CLI-only side channel):
   applied consequences AND blocked refusals are recorded in
   `StoryBlueprint.identity_propagation` (§11). The blueprint is
   self-describing: any holder of the blueprint — CLI handler, outline
   builder, analyzer, proposal pipeline — can see what propagation decided.
2. **Analyzer conversion (the universal surface)**: a small new rule family
   in `structure/analyzer.py` (implemented as a helper called from
   `analyze_structure`, `analyzer.py:67`, so `run_all_diagnostics` L22,
   `state_check`, `propose_repairs_from_diagnostics` all inherit it) reads
   `blueprint.identity_propagation.outcomes` and converts each BLOCKED /
   AUTHOR-DECISION-REQUIRED outcome into a `StructureDiagnostic`
   (`identity.propagation.*` rule ids, WARNING severity, `evidence` quoting
   the record's source/reason). Every analysis path produces identical
   semantics regardless of the compile caller.
3. **Immediate feedback stays**: `handle_compile_to_blueprint`
   (`cli_handlers.py:345`) additionally surfaces the outcomes from the
   in-memory report at compile time (fast author feedback). This is a
   convenience on top of step 2, not the only path — removing it would not
   change diagnostic availability.
4. `compile_to_blueprint`'s signature remains
   `(identity) -> StoryBlueprint`; the persisted field is the observable
   contract (no hidden side channel — the reviewer's condition for keeping
   the signature).

## 11. Provenance / explainability (Revision 2, review item 6)

**Decision: keep a new optional blueprint field, justified as follows.**

Alternatives compared:

- **Extend `ProfileDerivation`** (`blueprint.py:689-710`): rejected — it is
  profile-flow-specific (`source_field`, `recommendation_id`,
  `obligations_applied`); overloading it with identity-propagation outcomes
  would conflate two commitment classes and break its consumers (D-RES
  gating reads its obligation strings, `analyzer.py:1583-1662`).
- **`ArtifactStore` sidecars** (`provenance/store.py:152`): rejected —
  file-level metadata keyed by artifact id; `compile_to_blueprint` is
  in-memory and does not persist files; sidecars would not travel with the
  blueprint object and would not be visible to in-memory callers
  (`outline_builder`).
- **No persistent record (CLI-only)**: rejected by review item 5.
- **New in-blueprint field**: chosen — it follows the established
  field-level derivation precedent (`ProfileDerivation` lives in the
  blueprint), makes diagnostics caller-independent (§10), and adds one
  optional serialization field (backward compatible, §12).

Model (replacing Revision 1's applied-only `entries`; now carrying refusals):

```python
class PropagationOutcome(BaseModel):
    rule: str          # e.g. "identity.not_this.custom_rules",
                       #      "identity.naming.protagonist",
                       #      "identity.role_rule.correction",
                       #      "identity.role_rule.arc_undeclared"
    classification: Literal[
        "DIRECT_DETERMINISTIC",
        "BLOCKED_INSUFFICIENT_EXPLICIT_INPUT",
    ]
    destination: str | None = None  # dot path for applied, e.g.
                       # "contract.custom_rules[0]", "characters[1].name"
    value: str | None = None        # verbatim value applied
    source: str | None = None       # e.g. "not_this[0]", "characters[1].name"
    reason: str | None = None       # human-readable refusal reason (blocked)

class IdentityPropagationDerivation(BaseModel):
    derived_at: str = Field(...)    # ISO-UTC, same pattern as ProfileDerivation
    outcomes: list[PropagationOutcome] = Field(default_factory=list)
```

- `StoryBlueprint.identity_propagation: IdentityPropagationDerivation | None =
  None` — set when ≥1 outcome occurred (applied or blocked). NOT_APPLICABLE
  restraint is excluded (it leaves no trace).
- This makes "Why did this structural field change?" answerable as
  `source commitment → rule → destination consequence`, and "why was nothing
  done?" answerable from the blocked records — lightweight, consistent with
  the existing field-level derivation mechanism. No evaluation manifests; no
  `ArtifactStore` changes.

## 12. Compatibility and migration (Revision 2)

- **Existing StoryIdentity documents**: remain valid. `characters` is an
  optional field with `[]` default; all other fields unchanged. No migration.
- **Existing blueprint serialization**: remains valid. New field
  `identity_propagation` is optional and absent when no outcome occurred;
  files with the field still load under older code (unknown-field tolerance
  must be verified against the loader — `narrative_blueprint/loader/` is for
  outlines; blueprint YAML load path is via `StoryBlueprint.model_validate`
  in `proposal_application.py:68` and CLI handlers).
- **Deliberate output changes** (the feature): identities carrying
  `not_this`/`rejected_directions` will now produce populated
  `contract.custom_rules`; identities declaring `characters` may produce
  named/corrected slots and/or a provenance record with blocked outcomes.
  Identities with none of these produce byte-identical blueprints
  (regression-tested). `forbidden_tropes` is NOT populated by this feature
  (destination semantics, §6) — no interaction with the genre
  `required_trope_forbidden` check (`analyzer.py:788`).
- **Genre Packs / profile propagation**: untouched. Profile obligations
  (`identity.py:763-797`) and the new identity propagation coexist;
  exact-match dedupe makes overlap collapse to one entry; `ProfileDerivation`
  and `IdentityPropagationDerivation` are separate records; D-RES gating
  (`analyzer.py:1577`) is unaffected.
- **Series/book compiler interaction**: `series/compiler.py:18` and
  `book/builder.py:15` write `not_this=["Do not resolve the full series
  question outside Book N."]`. Under A1 this lands verbatim in
  `custom_rules` (previously recorded as `forbidden_tropes` in Revision 1).
  Semantically faithful (a book-scoping exclusion enforced as a critic rule),
  but a **visible new interaction**; recorded for review (Open question 5).
  `rejected_directions=[]` and `author_overrides=[]` there are unaffected.
- **Deterministic ordering**: identity items appended in field/list order
  after profile-derived items; serialized output ordering is deterministic
  (list fields preserve order).
- **Cache/hash behavior**: blueprint content hashes (`provenance/store.py`,
  `canonical_content_hash`) follow serialized content; blueprints that gain
  the new field/content will hash differently — which is the point of the
  feature. No hash logic changes.
- **`derived_at`**: new field carries its own `derived_at`; existing
  `profile_derivation.derived_at` behavior unchanged.

## 13. Testing plan (Revision 2)

New file `tests/test_identity_propagation.py` (TDD; run via
`python -m pytest tests/test_identity_propagation.py`, repo config:
`pyproject.toml` addopts `-q --tb=short -W ignore::UserWarning`,
CI Python 3.11-3.13).

**Contract propagation (slice 1):**

- explicit `not_this` item propagates verbatim into `custom_rules`
  (NOT `forbidden_tropes`);
- `rejected_directions` item propagates verbatim into `custom_rules` with
  source-preserving provenance;
- duplicate within identity and duplicate vs profile-derived value → single
  entry;
- absent commitments → destination lists unchanged, no provenance field;
- `author_overrides` (including `ending_tone`/`runway_compression` and
  free-text values) is NEVER propagated — no custom_rules additions, no
  denylist in code;
- expected/custom conflict (same normalized string in both lists) →
  no mutation + BLOCKED outcome + `identity.propagation.contract.conflict`
  diagnostic from the analyzer;
- deterministic ordering (identity items after profile items, list order);
- idempotence (double compile identical) and no identity mutation;
- existing `tests/test_profile_propagation.py` ordering/dedup/no-mutation
  tests stay green.

**Naming (slice 2):**

- declared `structural_role=protagonist` + placeholder slot → slot named;
- two entries claiming the same role → BLOCKED, no naming;
- entry without `structural_role` → no naming; no invented names;
- named entry without `arc_type` → naming still applies (arc is not a naming
  precondition).

**Role semantics (slice 3)** — the four Experiment-3 categories as production
tests, driven by the structured `characters` field (no text fixtures):

1. already-correct role → no mutation (NOT_APPLICABLE, no provenance trace);
2. explicitly framed opponent who changes (`structural_role=antagonist` +
   `undergoes_central_change=True`) → no mutation;
3. ambiguous declaration (subject matching no slot, no placeholder) →
   fail-closed, no mutation, BLOCKED recorded;
4. explicit co-transforming lead in a placeholder antagonist slot WITH
   declared `arc_type` → name/role/arc correction applied, provenance
   recorded;
4a. same declaration WITHOUT `arc_type` → no correction (atomicity), BLOCKED
   + `identity.propagation.role_rule.arc_undeclared` diagnostic.

Plus: authored (non-placeholder) contradictory slot → BLOCKED diagnostic, no
mutation. No regex/verb-list tests are carried forward — the production
design contains no textual heuristics (per `experiment-3/02-conclusion.md`:
do not carry regex-specific tests when the mechanism is removed).

**Universal diagnostics (all slices):**

- a blueprint produced by `compile_to_blueprint` with blocked outcomes,
  analyzed through `analyze_structure`/`run_all_diagnostics`, yields the
  `identity.propagation.*` diagnostics — independently of which caller
  compiled it (test drives both `handle_compile_to_blueprint` and a direct
  `compile_to_blueprint` call; diagnostics must be identical);
- removing the CLI handler's immediate surfacing does not change analyzer
  output (provenance record is the source of truth).

**Compatibility (all slices):**

- identity without `characters` and without commitment fields → blueprint
  byte-identical to pre-feature output (the "overthrow"-class guard by
  construction);
- existing fixtures (`tests/fixtures/workflow/project_identity/story_identity.yaml`,
  `examples/story_identity.yaml`) load and compile;
- `tests/test_blueprint_seeding.py` / `test_identity_compile_dynamic.py`
  contract assertions re-checked in slice 1 (they currently assert
  `mandatory_ending_tone`/`content_rating`; the seeding fixture carries
  `not_this`/`rejected_directions`/`author_overrides`, so `custom_rules`
  will become non-empty — any emptiness assertion must be updated
  deliberately, not silently).

## 14. Alternatives considered (Revision 2)

- **Option A — inline in `compile_to_blueprint`**: minimal abstraction; but
  adds ~150 lines to a 360-line function, scatters policy across contract and
  character blocks, and makes the staged role rule hard to unit-test in
  isolation. Rejected as the sole mechanism.
- **Option B — explicit bounded propagation component**: chosen (module +
  report + provenance), because the report shape matches the repo's
  report-artifact culture and the role rule needs a dedicated test matrix.
  Scoped to ONE module — no package, no rule registry, no extensibility
  machinery (YAGNI).
- **Option C — compiler + diagnostic consistency check only**: retained as
  the **safety boundary for authored blueprints** (Stage 5) and as the
  fallback if the schema addition is rejected (§8.3-D). Not recommended as
  the full design because contract propagation (the strongest validated
  mechanism) is deterministic and safe at compile time, and dropping it would
  forfeit the validated value.
- **A2 verbatim propagation (`author_overrides` → `custom_rules`, with or
  without a bypass-marker denylist)**: rejected — category mixing plus the
  denylist pattern (§6.1).
- **Destination `forbidden_tropes` for `not_this`/`rejected_directions`
  (Experiment-2 mapping)**: rejected in Revision 2 — trope-shaped consumer
  semantics (`analyzer.py:759,788-792`; `critic/contract.py:92`) make free
  author sentences inert and pollute the field (§6).
- **Destination `rejected_outcomes` for `rejected_directions`**: rejected —
  profile-resolution-contract semantics with gated enforcement
  (`analyzer.py:1631-1662`); identity items would be stored but never
  enforced (§6).
- **Extending `ProfileDerivation`**: rejected — profile-flow-specific;
  would break D-RES gating consumers (§11).
- **Schema-free role handling via `CharacterIdentity`**: rejected — content
  model with no `name`/primary role, blueprint-side, post-compile (§8.2).
- **Full structured roster (role, arc, psychology, relationships...)**: more
  expressive, but YAGNI — the validated semantics need four fields.

## 15. Risks (Revision 2)

| Risk | Mitigation |
|---|---|
| Schema addition (slices 2-3) rejected at the gate | Gap demonstrated in §8.2; fallback D (contract-only + diagnostics) ships slice 1 regardless; field is optional with `[]` default |
| Correction friction: arc now required explicitly | Correctness over convenience (review decision): BLOCK + clear `arc_undeclared` diagnostic + proposal path; authors who declare arcs get the validated automatic behavior |
| `custom_rules` becomes the shared bucket for `not_this` + `rejected_directions` | Deliberate: it is the only unconditional free-text enforcement bucket; provenance `source` preserves the distinction; documented in §6 |
| Snapshot churn for identities with commitment fields | Deliberate feature behavior; documented in §12; inert identities remain byte-identical |
| Dedupe/precedence edge cases | Exact-match dedupe only; no new precedence; conflict → BLOCKED diagnostic, never silent resolution |
| Series-compiler `not_this` now lands in `custom_rules` | Semantically faithful; documented interaction (Open question 5) |
| Correction raises `characters.no_antagonist` / milestone-gap diagnostics (observed in Experiment-2 case C) | Acceptable: analyzer warnings are advisory; a corrected deuteragonist without an antagonist is a real structural fact, not a defect; noted for slice-3 tests |
| `outline_builder` receives corrected blueprint | Reads only `estimated_chapters`; harmless |
| Byte-identical compatibility broken unnoticed | Dedicated compatibility tests (§13) |
| Analyzer conversion rule duplicates CLI warnings | Single source of truth: the provenance record; CLI surfacing is a convenience projection (§10) |

## 16. Implementation slices (Revision 2)

Slices chosen by repository coupling (contract construction block first,
schema addition second, role logic last — each slice is independently
reviewable and rollback-able by reverting its hook).

**Slice 1 — contract propagation (A1, A3).**
- Files: `src/auteur/identity_propagation.py` (new: outcome models +
  `apply_contract_propagation`), `src/auteur/identity.py` (hook in the
  contract block, L749-797), `src/auteur/blueprint.py`
  (`PropagationOutcome`, `IdentityPropagationDerivation`,
  `StoryBlueprint.identity_propagation`), `src/auteur/structure/analyzer.py`
  (blocked-outcome → `StructureDiagnostic` conversion, called from
  `analyze_structure`), `src/auteur/cli_handlers.py` (immediate surfacing of
  outcomes), `tests/test_identity_propagation.py` (new).
- Behavior: verbatim propagation of `not_this` + `rejected_directions` into
  `custom_rules`; dedupe + ordering + conflict BLOCK; provenance records
  applied + blocked; analyzer emits `identity.propagation.*` diagnostics.
- Migration risk: none (additive; behavior change only where commitments
  exist). Rollback: remove the hook call.

**Slice 2 — safe explicit naming (A4).**
- Files: `src/auteur/identity.py` (`IdentityCharacter` + `StoryIdentity.characters`
  schema addition), `src/auteur/identity_propagation.py`
  (`apply_character_naming`), `tests/...` (naming tests + schema round-trip).
- Behavior: role-correspondence naming of placeholder slots only; BLOCKED on
  ambiguity; never requires arc.
- Migration risk: low (optional field, `[]` default; old YAMLs valid).
  Rollback: drop the field and the naming call.

**Slice 3 — role consistency (B1+R1+R2 semantics).**
- Files: `src/auteur/identity_propagation.py` (five-stage decision incl.
  Stage 4a arc gate), `src/auteur/cli_handlers.py` (BLOCKED surfacing),
  `tests/...` (four semantic categories + arc-gate + authored-boundary
  tests).
- Behavior: restraint / opposition precedence / fail-closed ambiguity /
  atomic placeholder correction with explicit arc / BLOCK without arc /
  author-decision path for authored slots; provenance records for
  corrections and refusals.
- Migration risk: low (fires only on explicit declarations). Rollback:
  remove the stage-4 mutation call; diagnostics remain.

Slice ordering note: slices 2-3 share the `characters` schema field; slice 2
should land first so the roster exists before the role rule consumes it.

## 17. Explicit open questions (Revision 2)

1. **`StoryIdentity.characters` schema addition (slices 2-3)** — the review
   left this unresolved pending the gap demonstration. §8.2 demonstrates the
   gap; §8.3 recommends option C with option D (diagnostics-only, contract
   slice ships alone) as the fallback. **Human decision required at the
   implementation gate.**
2. **Arc behavior** — RESOLVED per review: no default; explicit `arc_type`
   required for correction; BLOCK + AUTHOR_DECISION_REQUIRED otherwise;
   existing compatible arcs preserved in the proposal path (§7 Stage 4a).
3. **`author_overrides`** — RESOLVED per review: not propagated; documented
   as a workflow/compiler control field; no denylist (§6.1).
4. **Persist refusals** — RESOLVED per review item 5: blocked outcomes are
   persisted on the blueprint and surfaced by the analyzer for all callers
   (§10-§11).
5. **Series/book `not_this` interaction** — now lands in `custom_rules`.
   Recommended: keep verbatim A1 propagation (faithful exclusion, enforced
   by the Critic). Alternative: have `series/compiler.py` and
   `book/builder.py` stop writing `not_this` scoping instructions and use
   `open_questions` instead. Minor; can be decided during slice 1.
6. **`custom_rules` as shared bucket** — accepted in this revision (only
   unconditional free-text enforcement bucket exists; provenance preserves
   source). If a future need for outcome-vs-pattern separation arises, that
   is a separate contract-schema decision.

## 18. Implementation branch strategy (Revision 2, review item 7)

Recorded decision for the implementation phase:

- The production feature branch will start from the **then-current canonical
  `main`**, NOT from `c73d344` or from `design/identity-structure-bounded-
  propagation`.
- Rationale: the discovery branches and the design branch carry the
  experiment history (`experiment/`, `experiment-2/`, `experiment-3/` +
  `docs/discovery/`); the production PR should contain only production
  implementation, production tests, and the approved design document.
- Mechanics: at implementation approval, create
  `feature/identity-structure-bounded-propagation` from `main`; bring the
  approved design document over (cherry-pick the doc commit or recreate the
  file) so the feature branch documents its own decisions; implement slices
  1-3 per §16.
- The discovery branches remain frozen historical evidence; the design
  branch remains the design-review artifact. No merge of either into the
  feature branch.

## Decision gate (Revision 2)

**READY_FOR_IMPLEMENTATION_APPROVAL** — with the explicit condition that
Open question 1 (schema option C vs fallback D, §8.3) is confirmed by the
human at the implementation gate. All seven review items are resolved in this
revision: schema gap demonstrated (§8), no default arc (§7), destinations
justified by consumer semantics (§6), `author_overrides` not propagated with
no denylist (§6.1), diagnostics universal via persisted provenance + analyzer
(§10), provenance field justified (§11), branch strategy recorded (§18).
No genuinely new product uncertainty was found; product discovery was not
reopened.

---

## 19. Implementation alignment notes (feature branch)

Recorded during production implementation on
`feature/identity-structure-bounded-propagation` (base: canonical main
`f7a89d2`). These notes supersede the corresponding sketches above where they
conflict; no historical discovery conclusions are rewritten.

1. **No `derived_at` in `IdentityPropagationDerivation`** (�11 sketch). The
   shipped model carries only `outcomes`. Propagation is fully deterministic
   and a wall-clock timestamp would make otherwise identical compilation
   outputs byte-different (the known `ProfileDerivation.derived_at`
   nondeterminism). This implements the implementation-gate clarification;
   �8 of the implementation prompt.
2. **Frozen placeholder set interpretation** (�7 Stage 4, �8.4). The set
   `{protagonist, antagonist, lover a, lover b}` enumerates the placeholder
   KINDS the compiler seeds. The concrete seeded names are
   `Protagonist`/`Antagonist` (default genres), `Detective`/`Culprit`
   (mystery), `Lover A`/`Lover B` (romance) � all six are compiler
   placeholders (`PLACEHOLDER_NAMES` in `identity_propagation.py`). This keeps
   naming and role correction genre-uniform. Safe because propagation runs
   only inside `compile_to_blueprint` on freshly seeded slots.
3. **Rule ordering: naming (A4) runs before the role rule (B1)**. A declared
   opponent name occupies the antagonist seat first, so the seat is no longer
   a placeholder and the role rule fails closed (Stage 5) instead of recasting
   it � the production form of opposition precedence. A declared protagonist
   name makes the role rule's Stage-2 "already represented" restraint fire
   naturally.
4. **`undergoes_central_change` is tri-state** (`bool | None`, default
   `None`) � UNKNOWN is distinguishable from explicit `False`, per the
   implementation-gate clarification. The role rule triggers only on `True`.
5. **Same-name restraint**: naming and role rules treat a slot that already
   carries the declared name as already represented (no outcome, no trace) �
   the Experiment-3 case-1 guard.
6. **Fixture note**: `tests/fixtures/workflow/project_identity/story_identity.yaml`
   cannot be loaded as a `StoryIdentity` on main (pre-existing: `mode:
   heroic` / `genre: fantasy` are outside the current enum vocabulary; no
   test loads it). Compatibility coverage uses `examples/story_identity.yaml`,
   which loads and compiles with `not_this` propagating to `custom_rules`.
7. **Provenance store integration**: `StoryIdentity.characters` was added to
   `semantic_fields` in `src/auteur/provenance/store.py` so character
   commitment edits invalidate dependent artifacts in dependency inference.
8. **Review-fix pass (MEDIUM-1, LOW-1, LOW-2, LOW-3)**. Recorded after the
   independent code review classified the implementation NEEDS_FIXES; no
   design rollback, no discovery reopened. (a) **Cross-rule fail-closed
   (MEDIUM-1)**: `apply_character_naming` now returns the set of
   `structural_role` values whose naming correspondence was ambiguous
   (BLOCKED), and `apply_role_rule` excludes subjects claiming those roles
   (Stage 0.5). An ambiguity refused by naming can no longer be acted on by
   the role rule; no extra diagnostic is emitted because the naming refusal
   is already recorded. (b) **Final validation (LOW-1)**: the propagation
   hook runs after the `StoryBlueprint` constructor, so `compile_to_blueprint`
   re-validates the final blueprint through
   `StoryBlueprint.model_validate(blueprint.model_dump(mode="json"))` when
   any outcome occurred. Propagation-created state therefore passes the
   normal model validators (including `Character._arc_bounds_consistent` and
   the root `_apply_and_validate` checks), and an invalid propagated state
   fails the compile loudly instead of serializing an unloadable blueprint.
   Note: a correction that creates a second POV-eligible character now fails
   compile for length classes whose `max_pov_characters == 1` (e.g.
   SHORT_STORY) instead of silently producing an invalid blueprint.
   (c) **Case-normalized representation (LOW-2)**: name representation and
   restraint comparisons casefold both sides; authored names are never
   rewritten in serialized output. (d) **`author_overrides` claim softened
   (LOW-3)**: see section 6.1 - repository usage is mixed (the canonical
   example carries a free-text mandate); the A2 decision (never propagated,
   no denylist) is unchanged; a future `author_constraints` field is a
   separate product decision.
