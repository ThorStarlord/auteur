# Project Format

An Auteur project is a directory-backed story workspace.

```text
project/
  blueprint.yaml
  bible.json
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

- `identity`: title, author intent, length class, genre, audience, POV mode.
- `structure`: estimated chapters, word count, act structure, POV limits.
- `contract`: content rating, forbidden tropes, required elements, custom rules.
- `emotional_design`: overall and per-act tonal targets.
- `characters`: roles, arc types, milestones, and current state.
- `tension_waveform`: target tension scores by chapter and realized scores.
- `theme`: central question, thesis, and motifs.

The sample file at `examples/sample_blueprint.yaml` is the best starting point.

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

