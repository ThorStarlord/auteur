# Auteur

Auteur is an opinionated narrative-engine toolkit for long-form fiction. It helps beginner-to-intermediate writers turn raw creative input into a recommended story engine, validates that engine deterministically, and treats chapter outlining and prose generation as optional downstream stages.

Auteur coordinates high-level narrative-engine recommendation with deterministic execution rails under a unified narrative compilation lifecycle:

```text
raw idea
  ↓
opinionated interpretation
  ↓
story_identity.yaml (accepted recommended story engine)
  ↓
blueprint.yaml (structural design canvas)
  ↓
structure diagnostics (deterministic audit)
  ↓
optional cartographer outline (chapter coordination)
  ↓
optional chapter contracts (TDD specifications)
  ↓
optional draft / critique / accept (Bard & Critics)
```

The current Engine v1 is a hybrid system:

- Deterministic code owns schemas, project files, validation models, artifact writing, and retry flow.
- LLM calls provide creative planning, prose generation, and critic judgment.
- The pipeline keeps LLM output inside a repeatable plan -> draft -> critique -> iterate loop.

## Status

This repository currently contains a working Engine v1 CLI and Python library. It supports:

- **Opinionated Story Identity**: Recommended story-engine validation and seeding via Pydantic model contracts, including rationale, rejected directions, and author overrides.
- **Deterministic Diagnostics**: Complete, non-destructive structure diagnostics and repair proposals.
- **Outline Compiling**: Generating character-aligned chapter outline coordinates.
- **TDD Drafting**: Running multi-critic verification loops against structured chapter contracts.
- Project initialization with a `blueprint.yaml`, `bible.json`, and chapter artifact tree.
- Chapter drafting through Anthropic or OpenAI adapters.
- Five critic passes: contract, arc, tension, slop, and theme.
- Automatic rewrite attempts up to a configurable iteration cap.
- Manual accept and retry flows.

The implementation is still early. Cartographer outline validation exists as a deterministic local validator backed by dedicated Pydantic outline models (`CartographerOutline` in `src/auteur/cartographer_outline.py`). Transient API errors are handled by `RetryingClient` with exponential backoff. Per-agent model routing is configurable via blueprint-level `cartographer_model`, `bard_model`, and `critic_model` fields.

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

Generate a recommended story engine from a raw premise, validate it, and compile the blueprint:

```powershell
# 1. Recommend a story engine from a raw premise
auteur identity recommend "A detective investigates a locked manor murder" --output .\tmp\story_identity.yaml

# 2. Validate the story identity
auteur identity validate .\tmp\story_identity.yaml

# 3. Compile into a blueprint skeleton
auteur blueprint seed .\tmp\story_identity.yaml --output .\tmp\blueprint.yaml

# 4. Run whole-story structure diagnostics
auteur structure diagnose .\tmp\blueprint.yaml
```

Initialize a project from the seeded blueprint:

```powershell
auteur init .\tmp\shattered_crown --from .\tmp\blueprint.yaml
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

### 1. Identity & Narrative Engine Seeding

`auteur identity recommend <premise> --output <path>`

Translates a raw premise (text or path to a file) into a validated `StoryIdentity` YAML document. Auteur recommends exactly one story engine optimized for the genre contract promise, explains its reasoning in `why_this_is_best`, and records `rejected_directions`. Accepts optional `--genre`, `--medium`, and `--mode` constraints.

`auteur identity validate <story_identity.yaml>`

Validates an accepted story identity against the Pydantic schema constraints and deterministic narrative validation rules (want-change coherence, genre ending tone, target experience avoidance, runway length class).

`auteur blueprint seed <story_identity.yaml> --output <blueprint.yaml>`

Compiles accepted identity fields into a standard `StoryBlueprint` skeleton. Recommendation rationale is preserved in `story_identity.yaml` and does not silently mutate blueprint structure.

`auteur identity compile <story_identity.yaml> --output <blueprint.yaml>`

Alias for `blueprint seed`.

### 2. Whole-Story Structure Audits

`auteur structure diagnose <blueprint.yaml>`

Runs deterministic coherence diagnostics (e.g., matching wants/change, verifying subplot budgets) and outputs finding logs.

`auteur structure propose-repairs <blueprint.yaml>`

Generates actionable repair proposals in `structure/proposals/` for any diagnostic errors or warnings found.

`auteur structure apply <proposal.yaml> <blueprint.yaml> [--in-place]`

Applies a selected proposal option cleanly to the target blueprint file.

### 3. Project Initialization & TDD Chapter Drafting

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

### 4. Cartographer Outlines

`auteur cartographer compile <blueprint.yaml> --output <cartographer_outline.yaml>`

Compiles a blueprint into a unified Cartographer outline and can split chapter outlines into a project chapter tree.

`auteur cartographer validate <cartographer_outline.yaml> [--blueprint <blueprint.yaml>]`

Runs deterministic local validation for compiled Cartographer outlines. Dedicated Pydantic outline models are still incomplete.

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
- [Opinionated Narrative Engine](docs/opinionated-narrative-engine.md)

The files under `docs/superpowers/` are implementation design and planning notes for development work. The user-facing docs above describe the current repository behavior.

## Tests

Run the full test suite with:

```powershell
python -m pytest
```

### Local verification

```powershell
python scripts/check.py
```

CI runs the same verification entrypoint: `python scripts/check.py`.

The manual real-LLM smoke script is not part of pytest because it spends real tokens:

```powershell
python .\scripts\smoke_real_llm.py
```

## Experimental

Open-ended candidate workflows (`--recommend-mode open-ended`, `auteur identity accept-candidate`) exist for internal and advanced use. They are not part of the default public workflow.
