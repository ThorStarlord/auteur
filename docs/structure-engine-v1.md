# Structure Engine v1

Auteur should be a whole-story structure engine first and a chapter drafting
engine second. Drafting remains useful, but it should consume a stable story
structure instead of inventing structure implicitly at chapter time.

## Direction Model

Auteur has two structure operations with opposite directions.

```text
generate = top-down
diagnose = bottom-up
```

Generation starts from global constraints and produces structural choices.
Diagnosis starts from a symptom and traces it back to the deepest likely cause.

Examples:

```text
generate:
target experience -> constraints -> structural forces -> threads -> scenes

diagnose:
"midpoint feels flat" -> representation -> thread -> structural force -> repair
```

The two modes should stay explicit in the CLI/API. A future command shape could
look like:

```text
auteur structure generate <partial-blueprint>
auteur structure diagnose <blueprint> --symptom "The midpoint feels flat."
```

## Layer Model

The structure engine uses these layers:

```text
Target Experience
Promise / Form Contract
Scope / Container
Structural Forces
Threads
Carriers
Representation
Modulation
Resonance / Coherence
```

### Target Experience

The intended audience experience: the emotional promise the story is trying to
produce. This can be a single feeling or a progression of feelings.

### Promise / Form Contract

Genre, subgenre hierarchy, mode, medium contract, and audience. These are not
late decorations. They constrain the whole system from the start because they
shape what the story promises and what forms of causality, revelation, agency,
tone, and payoff are expected.

Genre chooses the promise. Medium chooses the delivery grammar. Scope chooses
the execution budget. The medium contract starts in Layer 2, then cascades into
scope containers, structural modules, carriers, representation units, and
modulation choices.

### Scope / Container

Story length, estimated word count, chapter count, POV count, and subplot
budget. Length is the raw size; scope is what that size can responsibly carry.

### Structural Forces

The core story forces:

- want
- resistance
- conflict
- stakes
- change

These should be represented as meaning-rich author text and, later, sharper
checkable claims. "Character detail" is expressive, but agency is structural:
want implies something wants, stakes imply something can lose, and change
implies something changes.

Consequence scale belongs under stakes, not Layer 3. A small-container story can
still carry city, national, or civilizational stakes if the machinery remains
focused enough for the chosen form.

### Threads

Whole-story structure is threaded. It needs a main thread plus subordinate
threads, each with structural work to do.

Thread types for v1:

- `main_plot`
- `character_arc`
- `relationship_arc`
- `mystery`
- `political`
- `survival`
- `thematic_echo`

Support functions for non-main threads:

- `complicates`
- `mirrors`
- `contrasts`
- `escalates`
- `reveals`
- `pressures_change`
- `pays_off`

Each thread should declare its thematic function.

### Carriers

Characters, setting, situation, institutions, and world systems. These carry or
instantiate the structural forces.

### Representation

Plot, events, scenes, reveals, turns, and sequences. These are visible evidence
that the deeper structure is working.

### Modulation

POV, pacing, tone, mood, prose style, motif emphasis, and framing. These shape
how the structure is felt.

### Resonance / Coherence

Thematic resonance is not a normal generative layer. It is an alignment signal
across layers. Resonance appears when conflict, change, plot outcome, motifs,
and target experience reinforce the same underlying thematic question or
argument.

## Blueprint Shape

The current `StoryBlueprint` should gain a separate optional `story_engine`
nested model. Existing sections should not be blurred together.

```python
class StoryBlueprint(BaseModel):
    identity: ProjectIdentity
    structure: StructuralConstants
    story_engine: StoryEngine | None = None
    contract: AuthorAudienceContract
    emotional_design: EmotionalBlueprint
    characters: list[Character]
    tension_waveform: TensionWaveform
    theme: ThematicCore
```

`story_engine` should be optional while migrating existing blueprints. Structure
diagnosis should require it unless running in an infer/propose mode. A future
major version may make it required.

Conceptual YAML shape:

```yaml
identity:
  title:
  author_intent:
  target_experience:
  genre:
  subgenres:
  mode:
  medium:
  medium_contract:
    medium:
    format:
    release_model:
    interaction_model:
    unit_of_delivery:
    representation_units: []
    modulation_biases: []
    medium_failure_modes: []
  target_audience:
  pov_type:

structure:
  length_class:
  estimated_word_count:
  estimated_chapters:
  act_structure:
  max_pov_characters:
  max_characters_total:
  subplot_budget:

story_engine:
  main_thread:
    type: main_plot
    want:
      author_text:
      checkable_claims: []
    resistance:
      author_text:
      checkable_claims: []
    conflict:
      author_text:
      checkable_claims: []
    stakes:
      author_text:
      checkable_claims: []
    change:
      author_text:
      checkable_claims: []
    thematic_function:
  threads:
    - name:
      type:
      want:
        author_text:
        checkable_claims: []
      resistance:
        author_text:
        checkable_claims: []
      conflict:
        author_text:
        checkable_claims: []
      stakes:
        author_text:
        checkable_claims: []
      change:
        author_text:
        checkable_claims: []
      supports_main_by: []
      thematic_function:
```

Theme should stay separate from `story_engine`, because theme is a coherence
test across the full design rather than one thread. Threads should link back to
theme through `thematic_function`.

## Proposal And Report Strategy

Structural choices are authorial. Auteur should propose or diagnose them, not
silently rewrite the story spine.

Generation should produce human-editable proposal YAML:

```text
structure/
  proposals/
    001_generate_story_engine.yaml
```

Diagnosis should produce machine-checkable report JSON, and may also produce a
repair proposal YAML:

```text
structure/
  diagnostics/
    001_midpoint_feels_flat.json
  proposals/
    002_repair_midpoint_feels_flat.yaml
```

If a required structural field is missing, Auteur should:

1. propose 2-3 plausible options,
2. explain the tradeoff,
3. ask the author to choose or edit,
4. only then lock the field.

## Diagnostic Model

Structure diagnostics should be structured so they can power CLI output, JSON
reports, and later repair proposals.

```yaml
severity: error | warning
layer: target_experience | constraints | scope | structural_forces | threads | theme
rule: "threads.exceeds_subplot_budget"
message: "Declared 6 subordinate threads but subplot_budget is 3."
evidence:
  - "structure.subplot_budget = 3"
  - "story_engine.threads count = 6"
repair_options:
  preserve_intent:
    - "Merge the political and succession threads."
    - "Increase subplot_budget and length_class if this is intended to be epic-scale."
  challenge_intent:
    - "Reduce the story from ensemble epic to protagonist-focused tragedy."
```

Errors should block downstream structure commands. Warnings should inform but not
block.

Repair options should be split into:

- `preserve_intent`: keep the declared target experience and repair inside it.
- `challenge_intent`: expose contradictions in higher-level constraints and
  suggest changing them.

## First Implementation Slice

The first slice is schema plus deterministic validation only. It should not call
an LLM and should not add structure generation yet.

Scope:

1. Add optional `story_engine` models to `StoryBlueprint`.
2. Add `target_experience`, `mode`, `medium`, `subgenres`, and `subplot_budget`
   fields where appropriate.
3. Add sample YAML fields.
4. Add a separate structure analyzer for deterministic diagnostics.
5. Add tests.

Pydantic should handle parseable shape:

- required fields inside provided models
- enum values
- list shapes
- string presence
- allowed thread types
- allowed support functions

The structure analyzer should handle narrative completeness and coherence:

- missing `story_engine`
- missing main thread fields
- non-main thread missing `supports_main_by`
- thread missing `thematic_function`
- scope/subplot budget missing when threads exist
- thread count exceeds subplot budget
- main thread `change` should not be identical to `want`
- ending tone should not fight target experience
- theme thesis should be referenced by at least one thread thematic function

The analyzer should check completeness and coherence, not judge whether the
story is good.
