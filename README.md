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

This repository contains a working Engine v1 CLI and Python library covering the full narrative compilation lifecycle:

- **Opinionated Story Identity**: Recommended story-engine validation and seeding via Pydantic model contracts, including rationale, rejected directions, and author overrides.
- **Genre Overrides**: Declared author bypasses for genre contract expectations, classified into four consequence types (`safe_variation`, `compression`, `subversion`, `reclassification`).
- **Subgenre Modifier Validation**: Registered subgenre modifiers (`locked_room`, `hardboiled`, `cozy`) with scope, setup, and misuse diagnostics.
- **Structure Generation (top-down)**: Synthesizes a complete story engine from target experience, genre, and scope constraints.
- **Structure Diagnosis (bottom-up)**: Maps author-described symptoms (e.g. "midpoint feels flat") to likely structural root causes with recommendations.
- **Deterministic Diagnostics**: 20+ deterministic rules across layers 1-6 and 9, with repair proposals and full proposal lifecycle (diagnose → propose → select → apply).
- **State Management**: Multi-layer coordination across all 9 structure layers via `auteur state` commands (check, update, prepare, canon, confirm).
- **Outline Compiling**: Cartographer outline compilation from blueprint with deterministic validation.
- **TDD Drafting**: Multi-critic verification loops (contract, arc, tension, slop, theme) against structured chapter contracts, with automatic rewrite attempts and manual accept/retry flows.
- **Dual LLM Provider Support**: Anthropic Claude and OpenAI GPT adapters with per-agent model routing and exponential-backoff retry.

Transient API errors are handled by `RetryingClient` with exponential backoff. Per-agent model routing is configurable via blueprint-level `cartographer_model`, `bard_model`, and `critic_model` fields.

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

`auteur identity validate` also checks subgenre modifiers (known vs. unknown, primary genre compatibility, scope biases, setup requirements, and common misuses) when subgenres are declared.

### 2. Whole-Story Structure Audits & Generation

`auteur structure diagnose <blueprint.yaml>`

Runs deterministic coherence diagnostics (e.g., matching wants/change, verifying subplot budgets, genre contract constraints, subgenre modifier validation) and outputs finding logs.

`auteur structure propose-repairs <blueprint.yaml>`

Generates actionable repair proposals in `structure/proposals/` for any diagnostic errors or warnings found.

`auteur structure apply <proposal.yaml> <blueprint.yaml> [--in-place]`

Applies a selected proposal option cleanly to the target blueprint file.

`auteur structure generate <blueprint.yaml> [--symptom "text"]`

Two modes:

- **Top-down generation** (default): Synthesizes a full story engine from the blueprint's target experience, genre, and scope downward through structural forces and threads. Requires `target_experience` and at least one character. Outputs a `GenerationProposal` JSON.

- **Bottom-up symptom diagnosis** (`--symptom`): Maps an author-described symptom (e.g. "midpoint feels flat", "the ending doesn't land", "subplots go nowhere") to likely structural root causes with actionable recommendations. Returns one or more `SymptomDiagnosis` results ranked by relevance, each identifying the affected layer, root cause hypothesis, recommendation, and alternative hypotheses.

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

Runs deterministic local validation for compiled Cartographer outlines using the CartographerOutline Pydantic model.

### 5. Interactive Genre-Specific Pipelines

Auteur offers interactive browser-based story identity authoring for specific genres. Each genre pipeline provides a guided authoring experience with an opinionated emotional core system.

#### Netorare (NTR) Genre

`auteur netorare init <path> [--core classic_humiliation|horror|mystery] [--provider anthropic|openai] [--port 8765]`

Launches an interactive browser-based netorare story identity authoring session with three distinct emotional cores:

- **classic_humiliation**: Focus on emotional contrast and humiliation dynamics
- **horror**: Dread, body horror, and psychological terror elements
- **mystery**: Puzzle-like revelation and hidden truth discovery

```powershell
auteur netorare init ./my_netorare_story --core classic_humiliation
auteur netorare init ./my_netorare_story --core horror --provider openai
auteur netorare init ./my_netorare_story --core mystery --port 8765
```

The browser session reuses the same Session, Server, and interactive UI infrastructure to guide authoring from raw idea through identity validation.

#### Mystery (Detective) Genre

`auteur mystery init <path> [--core howdunit|paranoia|cozy] [--provider anthropic|openai] [--port 8766]`

Launches an interactive browser-based mystery story identity authoring session with three distinct emotional cores:

- **howdunit**: Puzzle-solving focus with intricate clue mechanics and red herrings
- **paranoia**: Dread and distrust, where reality itself becomes questionable
- **cozy**: Comfort-centered mystery with amateur detective charm and community focus

```powershell
auteur mystery init ./my_mystery_story --core howdunit
auteur mystery init ./my_mystery_story --core paranoia --provider openai
auteur mystery init ./my_mystery_story --core cozy --port 8766
```

Both Netorare and Mystery pipelines share the same Session/Server/UI infrastructure and deterministic validation layer, ensuring consistent identity curation across genres while allowing genre-specific emotional cores to guide authoring.

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

Auteur is a whole-story structure engine first. The structure layer owns:

- **9-layer model**: Target Experience → Promise/Form Contract → Scope/Scale → Structural Forces → Threads → Carriers → Representation → Modulation → Resonance/Coherence.
- **Deterministic diagnostics**: 20+ rules across layers 1-6 and 9 for within-blueprint coherence, genre contract validation, and subgenre modifier validation.
- **Proposal lifecycle**: Full diagnose → propose → select → apply cycle with `auteur structure` commands.
- **Top-down generation**: Synthesizes story engines from target experience downward via `auteur structure generate`.
- **Bottom-up symptom diagnosis**: Maps author-described symptoms to structural root causes via `auteur structure generate --symptom`.
- **Genre overrides**: Four-class override system (`safe_variation`, `compression`, `subversion`, `reclassification`) that downgrades contract violations to warnings with consequence guidance.
- **State management**: `auteur state` commands coordinate multi-layer check, update, prepare, canon, and confirm operations.

Chapter drafting is an optional downstream consumer of the structure engine. See [docs/structure-engine-v1.md](docs/structure-engine-v1.md) for the full design.

## Documentation

- [Architecture](docs/architecture.md)
- [Engine v1 Workflow](docs/engine-v1-workflow.md)
- [Project Format](docs/project-format.md)
- [Next Step Discovery](docs/next-step-discovery.md)
- [LLM Adapters](docs/llm-adapters.md)
- [Structure Engine v1](docs/structure-engine-v1.md)
- [Opinionated Narrative Engine](docs/opinionated-narrative-engine.md)
- [Genre Overrides](docs/genre-overrides.md)

The files under `docs/archived/superpowers/` are historical planning notes, not current user-facing documentation. The user-facing docs above describe the current repository behavior.

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


