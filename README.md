# Auteur

Auteur is an agentic narrative engineering toolkit for long-form fiction. It turns a structured story blueprint into whole-story structure checks, chapter plans, drafts, validation reports, and accepted chapter artifacts.

The current Engine v1 is a hybrid system:

- Deterministic code owns schemas, project files, validation models, artifact writing, and retry flow.
- LLM calls provide creative planning, prose generation, and critic judgment.
- The pipeline keeps LLM output inside a repeatable plan -> draft -> critique -> iterate loop.

## Status

This repository currently contains a working Engine v1 CLI and Python library. It supports:

- Blueprint loading and validation.
- Optional whole-story `story_engine` fields for target experience, structural forces, threads, and thematic function.
- Deterministic structure diagnostics through the Python API.
- Cartographer prompt rendering.
- Project initialization with a `blueprint.yaml`, `bible.json`, and chapter artifact tree.
- Chapter drafting through Anthropic or OpenAI adapters.
- Five critic passes: contract, arc, tension, slop, and theme.
- Automatic rewrite attempts up to a configurable iteration cap.
- Manual accept and retry flows.

The implementation is still early. It does not yet have structure generation/diagnosis CLI commands, proposal/report artifacts, structured Pydantic models for Cartographer outlines, deterministic outline validation, transient API retry/backoff, or per-agent model routing.

## Install

Use Python 3.11 or newer.

```powershell
python -m pip install -e ".[dev]"
```

For Anthropic support:

```powershell
python -m pip install -e ".[dev,anthropic]"
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

For OpenAI support:

```powershell
python -m pip install -e ".[dev,openai]"
$env:OPENAI_API_KEY = "sk-..."
```

Install both production adapters with:

```powershell
python -m pip install -e ".[dev,all]"
```

## Quick Start

Initialize a project from the sample blueprint:

```powershell
auteur init .\tmp\shattered_crown --from .\examples\sample_blueprint.yaml
```

Render a Cartographer prompt without making an LLM call:

```powershell
auteur plan .\examples\sample_blueprint.yaml 1
```

Draft chapter 1 with Anthropic:

```powershell
auteur draft .\tmp\shattered_crown 1 --provider anthropic --max-iterations 3
```

Draft with OpenAI:

```powershell
auteur draft .\tmp\shattered_crown 1 --provider openai --model gpt-4o
```

If drafting exhausts the iteration cap, edit the latest draft and accept it manually:

```powershell
auteur accept .\tmp\shattered_crown 1
```

Or continue from the latest failed draft and validation:

```powershell
auteur retry .\tmp\shattered_crown 1 --max-iterations 2
```

## CLI Commands

`auteur init <path> --from <blueprint.yaml>`

Creates a project directory with `blueprint.yaml`, `bible.json`, and `chapters/`.

`auteur plan <blueprint.yaml> <chapter>`

Renders the Cartographer system prompt and user message. This is useful for prompt debugging and does not call an LLM.

`auteur draft <project> <chapter> [--max-iterations N] [--provider anthropic|openai] [--model NAME]`

Runs Cartographer -> Bard -> Critics. On pass, writes `final.md` and updates `bible.json`. On failure, keeps drafts and validation reports on disk.

`auteur accept <project> <chapter>`

Promotes the latest `draft_v*.md` to `final.md` and records the chapter event/tension in the Bible.

`auteur retry <project> <chapter> [--max-iterations N] [--provider anthropic|openai] [--model NAME]`

Loads the existing `outline.yaml`, latest draft, and latest validation report, then continues with the next draft version.

## Project Artifacts

Generated project directories use this shape:

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

See [docs/project-format.md](docs/project-format.md) for the full artifact contract.

## Structure Engine

Auteur is moving toward a whole-story structure engine. The current groundwork is library-level:

- `StoryBlueprint` can carry optional global structure fields such as `target_experience`, `mode`, `medium`, `subgenres`, `subplot_budget`, and `story_engine`.
- `auteur.structure.analyze_structure()` runs deterministic completeness/coherence diagnostics.
- Chapter drafting still works independently while the structure engine matures.

See [docs/structure-engine-v1.md](docs/structure-engine-v1.md) for the design direction.

## Documentation

- [Architecture](docs/architecture.md)
- [Engine v1 Workflow](docs/engine-v1-workflow.md)
- [Project Format](docs/project-format.md)
- [Next Step Discovery](docs/next-step-discovery.md)
- [LLM Adapters](docs/llm-adapters.md)
- [Structure Engine v1](docs/structure-engine-v1.md)

The files under `docs/superpowers/` are implementation design and planning notes for development work. The user-facing docs above describe the current repository behavior.

## Tests

Run the full test suite with:

```powershell
python -m pytest
```

The manual real-LLM smoke script is not part of pytest because it spends real tokens:

```powershell
python .\scripts\smoke_real_llm.py
```
