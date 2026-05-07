# Architecture

Auteur has two distinct layers:

```text
How a user invokes Auteur
  CLI, Python library, coding agent, future API

How Auteur calls LLMs internally
  Cartographer, Bard, Critics through LLMClient adapters
```

The first layer is an interface choice. The second layer is engine plumbing. A coding agent can run the CLI, but the CLI still uses the same internal provider adapters as any other caller.

## Engine Shape

Engine v1 is a deterministic orchestration layer around non-deterministic LLM generation.

Deterministic code owns:

- Pydantic blueprint schema and cross-field validation.
- Default expansion based on length class.
- Project directory creation and artifact writing.
- Story Bible persistence.
- YAML/JSON parsing.
- Critic finding and validation report models.
- Draft retry and resume behavior.

LLMs own:

- Cartographer chapter outline generation.
- Bard prose drafting and rewriting.
- Critic judgment for contract, arc, tension, slop, and theme.

The purpose is not to remove LLM non-determinism. The purpose is to bound it: every creative output is routed through structured prompts, parsed artifacts, validation reports, and iteration state.

## Core Components

`src/auteur/blueprint.py`

Defines the story specification. `StoryBlueprint.from_yaml()` loads a blueprint, validates types/enums/ranges, fills structural defaults, and rejects inconsistent combinations such as incompatible audience/content rules.

`src/auteur/bible.py`

Stores live story state in JSON. Engine v1 records accepted chapter events and realized tension scores. Future work can expand this into richer state extraction.

`src/auteur/cartographer.py`

Renders a planning prompt from a `PlanningCall`. The Cartographer plans; it does not write prose.

`src/auteur/bard.py`

Renders the prose prompt. It supports initial draft mode and rewrite mode, where the prior draft and critic findings are included.

`src/auteur/critic/`

Contains the validation board:

- `contract`: content rules, forbidden tropes, expected elements, continuity, pacing.
- `arc`: character arc advancement.
- `tension`: felt tension versus target.
- `slop`: cliches, filler, AI tells, abstract emotion naming.
- `theme`: central question and motif presence.

`run_critics()` fans these out in parallel and returns one `ValidationReport`.

`src/auteur/pipeline.py`

Coordinates the chapter workflow: plan, draft, critique, write artifacts, retry, accept on pass, and record token usage.

`src/auteur/project.py`

Wraps a project directory containing `blueprint.yaml`, `bible.json`, and chapter artifacts.

`src/auteur/llm/`

Defines the provider-agnostic `LLMClient` protocol and concrete Anthropic/OpenAI clients.

## Current Limitations

- Cartographer outlines are parsed as raw YAML mappings, not yet validated against a dedicated outline model.
- Critic logic is mostly LLM-based; deterministic outline/prose checks are still limited.
- Provider choice is per CLI invocation, not yet per agent.
- Transient API failures are surfaced directly instead of retried with backoff.
- Cost accounting records tokens, not currency.

