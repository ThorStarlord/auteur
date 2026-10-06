# Architecture

> The semantic architecture is defined by [Narrative Architecture](narrative-architecture.md). This document describes interfaces and engine plumbing.

Auteur separates invocation, deterministic authority, and nondeterministic generation.

## Host-Agent-First Execution Target

ADR 022 establishes the target execution model:

```text
AUTHOR / CALLER
  CLI, Python library, coding agent, future API
        |
        v
AUTEUR DETERMINISTIC CORE
  state, artifacts, validation, authority, orchestration
        |
        v
GENERATION CAPABILITY BOUNDARY
        |
        +--> active host coding agent (preferred when available)
        |
        +--> direct LLM provider adapter (standalone / compatibility)
        |
        +--> deterministic fake/replay backend (tests)
```

"Use the current coding agent" does not mean that Auteur imports or launches a
specific agent product. A parent coding agent may not expose a callable SDK to a
child process. The portable contract is therefore a bounded request/response
handoff: Auteur emits the exact generation/reasoning request, the active host
agent fulfills it using its current model/session, and Auteur consumes the
structured response through existing validation and authority boundaries.

The host integration must be coding-agent agnostic. Auteur must not require
Claude Code, Codex, ChatGPT, Cursor, OpenCode, or any other vendor-specific
session protocol for core product behavior. Runtime/model identity should be
recorded when observable; unavailable identity is evidence metadata, not a
reason to fabricate one.

Current Engine v1 still routes most generated work through `LLMClient` direct
provider adapters. That is the present implementation state, not the long-term
product boundary. Migration should preserve `LLMClient` as a standalone backend
rather than deleting provider support.

## Engine Shape

Engine v1 is a deterministic orchestration layer around non-deterministic LLM generation.

Deterministic code owns:

- Pydantic blueprint schema and cross-field validation.
- Optional whole-story structure schema.
- Deterministic structure completeness/coherence diagnostics.
- Human-editable repair proposal artifact construction from diagnostics.
- Default expansion based on length class.
- Project directory creation and artifact writing.
- Story Bible persistence.
- YAML/JSON parsing.
- Critic finding and validation report models.
- Draft retry and resume behavior.
- Story Discovery artifact boundaries, workflow routing, and explicit author-acceptance authority.

LLMs own:

- Story Discovery candidate generation and comparative advisory judgment (`auteur story-discovery run ... --recommend`).
- Direct single-engine story identity recommendation for advanced/scripted use (`auteur identity recommend`).
- Cartographer chapter outline generation.
- Bard prose drafting and rewriting.
- Critic judgment for contract, arc, tension, slop, and theme.

The purpose is not to remove LLM non-determinism. The purpose is to bound it: every creative output is routed through structured prompts, parsed artifacts, validation reports, and iteration state. In Story Discovery specifically, generated alternatives and the advisory winner remain non-canonical until the author explicitly accepts a candidate.

Structure analysis is intentionally split from generation. Pydantic models say whether a blueprint is parseable; `auteur.structure` says whether the declared whole-story structure is complete and coherent enough for downstream work.

## Core Components

`src/auteur/blueprint.py`

Defines the story specification. `StoryBlueprint.from_yaml()` loads a blueprint, validates types/enums/ranges, fills structural defaults, and rejects inconsistent combinations such as incompatible audience/content rules. It also carries optional whole-story structure fields: target experience, mode, medium, subgenre hierarchy, subplot budget, and `story_engine`.

`src/auteur/structure/`

Contains deterministic structure diagnostics. The analyzer checks narrow completeness and coherence rules, such as missing `story_engine`, thread count exceeding subplot budget, duplicated main-thread want/change, and theme thesis not represented by thread thematic functions. It does not call LLMs and does not judge story quality.

`auteur structure diagnose`

Runs the deterministic structure analyzer from the CLI. It emits a JSON report to stdout, can also write that report to an explicit output path, returns `4` when error diagnostics are present, and does not mutate the blueprint.

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

`src/auteur/pipeline/`

Coordinates the chapter workflow: plan, draft, critique, write artifacts, retry, accept on pass, and record token usage.

`src/auteur/project.py`

Wraps a project directory containing `blueprint.yaml`, `bible.json`, and chapter artifacts.

`src/auteur/llm/`

Defines the current provider-agnostic `LLMClient` protocol and concrete
Anthropic/OpenAI clients. Under ADR 022 these become one implementation family
behind the broader generation-capability boundary. They remain useful for
standalone/headless execution and compatibility testing.

## Current Limitations

- Current `main` has not yet integrated the host coding-agent request/response
  adapter across production generation paths; direct `LLMClient` adapters remain
  the integrated production path. Draft PR #327 contains a bounded Quick Draft
  host-agent candidate, but that candidate is not yet part of `main`.
- Structure generation remains early/helper-level.
- Critic logic is still mostly LLM-based.
- Cost accounting records tokens, not currency.
- Genre override rules exist but need clearer documentation.

## Current Engine Reality

Deterministic code owns schemas, diagnostics, artifacts, Story Discovery authority boundaries, and workflow routing. LLMs own Story Discovery candidate generation/advisory judgment, direct identity recommendation, outlining, drafting, and critic judgment. Per-agent model routing now exists.

The current CLI also includes Story Discovery orchestration, deterministic Series and Universe
contracts, Genre Builder guides, round-trip import/export, controlled editing,
and the genre-neutral interactive pipeline runtime. These packages produce
working or derivative reports and artifacts without replacing canonical author contracts; Story Discovery becomes canonical only through explicit candidate acceptance.
