# Project Format

An Auteur project is a directory-backed story workspace.

```text
project/
  blueprint.yaml
  bible.json
  structure/
    diagnostics/
    proposals/
  chapters/
    01/
      outline.yaml
      draft_v1.md
      validation_v1.json
      draft_v2.md
      validation_v2.json
      final.md
```

## `blueprint.yaml`

The blueprint is the author specification. It is loaded by `StoryBlueprint.from_yaml()` and validated with Pydantic.

Major sections:

- `identity`: title, author intent, target experience, length class, genre, subgenres, mode, medium, audience, POV mode.
- `structure`: estimated chapters, word count, act structure, POV limits, subplot budget.
- `story_engine`: optional whole-story main thread and subordinate threads.
- `contract`: content rating, forbidden tropes, required elements, custom rules.
- `emotional_design`: overall and per-act tonal targets.
- `characters`: roles, arc types, milestones, and current state.
- `tension_waveform`: target tension scores by chapter and realized scores.
- `theme`: central question, thesis, and motifs.

The sample file at `examples/sample_blueprint.yaml` is the best starting point.

## Structure Artifacts

Structure engine outputs live under `structure/` when a workflow creates them:

- `structure/diagnostics/`: deterministic structure diagnostic reports.
- `structure/proposals/`: human-editable generation or repair proposal YAML artifacts.

Project helpers create these directories lazily when callers need them. Creating
or loading a project does not create structure artifact directories by default.

### Structure Engine Fields

The structure engine is optional for backward compatibility. Existing blueprints
can still load without it. When present, it makes whole-story structure explicit
before chapter planning or drafting.

Global constraint fields live in `identity` and `structure`:

```yaml
identity:
  target_experience:
    primary: dread
    progression: "unease -> dread -> catharsis"
    avoid:
      - "triumphant power fantasy"
  genre: grimdark_fantasy
  subgenre: grimdark
  subgenres:
    - grimdark
    - corruption_tragedy
  mode: tragic
  medium: novel

structure:
  subplot_budget: 3
```

The whole-story engine lives in `story_engine`:

```yaml
story_engine:
  main_thread:
    type: main_plot
    want:
      author_text: "The protagonist wants a visible external goal."
      checkable_claims: []
    resistance:
      author_text: "The primary opposition blocks easy success."
      checkable_claims: []
    conflict:
      author_text: "The want and resistance create an unavoidable dilemma."
      checkable_claims: []
    stakes:
      author_text: "Every path carries worsening consequences."
      checkable_claims: []
    change:
      author_text: "The protagonist is transformed by the pressure."
      checkable_claims: []
    thematic_function: "Names how the main thread tests the thesis."
  threads:
    - name: "Subordinate thread"
      type: character_arc
      want:
        author_text: "This thread has its own local desire."
        checkable_claims: []
      resistance:
        author_text: "This thread has local opposition."
        checkable_claims: []
      conflict:
        author_text: "This thread creates pressure that affects the main story."
        checkable_claims: []
      stakes:
        author_text: "This thread has consequences."
        checkable_claims: []
      change:
        author_text: "This thread changes over time."
        checkable_claims: []
      supports_main_by:
        - contrasts
        - pressures_change
      thematic_function: "Names how the thread contributes to resonance."
```

Allowed thread types are `main_plot`, `character_arc`, `relationship_arc`,
`mystery`, `political`, `survival`, and `thematic_echo`. Subordinate threads
cannot use `main_plot`.

Allowed support functions are `complicates`, `mirrors`, `contrasts`,
`escalates`, `reveals`, `pressures_change`, and `pays_off`.

`auteur.structure.analyze_structure()` can inspect these fields and return
deterministic diagnostics. It does not mutate `blueprint.yaml`.

The same deterministic analyzer is available through the CLI:

```powershell
auteur structure diagnose .\examples\sample_blueprint.yaml
auteur structure diagnose .\examples\sample_blueprint.yaml --output .\structure\diagnostics\001_report.json
```

The command prints a JSON report with a `diagnostics` list. It returns `0` when
there are no error diagnostics, `4` when one or more error diagnostics are
present, and `1` for local input failures such as a missing or malformed
blueprint. Writing an output report does not mutate the blueprint.

Diagnostic reports can be converted into human-editable repair proposal
artifacts with
`auteur.structure.proposals.propose_repairs_from_diagnostic_report()`. Code that
already has `StructureDiagnostic` objects can call
`propose_repairs_from_diagnostics()` directly. Each proposal keeps
preserve-intent and challenge-intent repairs as separate options, references the
diagnostic rule, severity, evidence, and report context, and starts with no
selected option. Generated repair option `data` is empty unless an author edits
in a concrete blueprint patch, so proposal creation does not mutate the
blueprint or imply automatic acceptance.

## `bible.json`

The Bible stores live state. Engine v1 initializes it as:

```json
{
  "characters": {},
  "locations": {},
  "items": {},
  "factions": {},
  "events": [],
  "realized_tension": []
}
```

Accepted chapters append to `events`. Accepted or manually accepted chapters can also write an integer tension score into `realized_tension`.

Engine v1 does not yet extract rich character/location/item deltas from prose. It records chapter-level acceptance state.

## Chapter Directories

Chapter directories are zero-padded:

```text
chapters/01/
chapters/02/
chapters/45/
```

`outline.yaml`

The Cartographer output for the chapter. It is a YAML mapping and may include `conflict_report`. Engine v1 parses it as a mapping but does not yet validate it against a dedicated outline schema.

`draft_vN.md`

Bard prose for iteration `N`. Retry continues from the highest existing version.

`validation_vN.json`

The `ValidationReport` for `draft_vN.md`. It contains:

```json
{
  "chapter_index": 1,
  "iteration": 1,
  "findings": [],
  "passed": true
}
```

Each finding has:

- `critic`: `contract`, `arc`, `tension`, `slop`, or `theme`
- `severity`: `error` or `warning`
- `rule`
- `evidence`
- `requested_change`

`final.md`

The accepted chapter. It is written automatically when a draft passes without error findings, or manually by `auteur accept`.
