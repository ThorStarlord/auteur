# Auteur

Auteur is a **local-first literary compiler and guided narrative-decision system for long-form fiction**. It helps an author turn raw creative input into a coherent story direction, preserve accepted narrative state over long horizons, diagnose structural problems, and make bounded creative decisions without silently surrendering story authority to the model.

The intended beginner experience is guided authoring with progressive disclosure. The Python CLI and YAML/JSON/Markdown artifacts remain the transparent engineering and advanced-author surface.

> **Current repository state:** see [STATUS.md](STATUS.md).  
> **Future product/repository directions:** see [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md).  
> **Mission and invariants:** see [MISSION.md](MISSION.md).  
> **Canonical architecture:** see [docs/narrative-architecture.md](docs/narrative-architecture.md).

## What Auteur Optimizes For

Auteur's first valuable outcome is not maximum prose volume. It is a story direction the author can understand, inspect, and explicitly accept.

```text
raw idea
  ↓
narrative search (multiple plausible story engines)
  ↓
advisory recommendation + trade-offs
  ↓
explicit author choice
  ↓
story_identity.yaml (accepted story engine)
  ↓
blueprint / structure planning
  ↓
deterministic diagnostics + derived decision support
  ↓
explicit author decisions
  ↓
optional outline / drafting / critique / publication workflows
```

For long-running projects, Auteur also externalizes accepted history and current narrative state so future decisions can be made without reconstructing the entire story from scratch.

## Product Model

Auteur increasingly separates the author-facing product from the underlying compiler machinery:

```text
AUTHOR-FACING PRODUCT
  guided authoring
  bounded creative decisions
  explanations / trade-offs / Tutor guidance

NARRATIVE COMPILER
  Ontology → Identity → Structure → Realization → Expression

SUPPORTING INTELLIGENCE
  diagnostics / provenance / impact / planning
  Series continuity / Global Map / Focus
  simulation / portfolio comparison / craft knowledge
```

The supporting systems remain subordinate to author authority. A deterministic result can be useful, reproducible, and well-evidenced without becoming canon.

## Canonical Architecture

Auteur uses five semantic layers:

1. **Ontology** — concepts, relationships, vocabulary, and domain rules.
2. **Identity** — commitments such as genre, medium, target experience, theme, and core story engine.
3. **Structure** — plans: arcs, beats, threads, chapter plans, setup/payoff intentions, thematic progression.
4. **Realization** — events and state changes: scenes, chronology, knowledge, location, inventory, relationships, and character deltas.
5. **Expression** — language: prose, dialogue, voice, diction, imagery, pacing, and revision.

The independent scope axis is:

```text
Universe → Series → Book → Chapter → Scene
```

Scopes are containers across semantic layers, not semantic layers themselves. Validation, orchestration, diagnostics, versioning, editing, maps, Tutor guidance, and other workflow systems are cross-cutting capabilities.

See [docs/narrative-architecture.md](docs/narrative-architecture.md) for the canonical model.

## Author Authority

Auteur's central safety and product rule is simple:

**Advice is not authority.**

- Story Discovery candidates do not become `StoryIdentity` until explicit acceptance.
- Diagnostics do not apply their own repairs.
- Maps and projections are derived/rebuildable views, not second canon.
- Story Design Packs and Genre Packs are reusable knowledge, not story-instance canon.
- Decision Cards are `DERIVED / NOT CANON`.
- Persisted Tutor sessions are `LOCAL / NONCANONICAL` and record advisory interaction only.
- Existing explicit story-authority/acceptance/revision workflows remain the routes that can change accepted narrative state.

## Current Capability Families on `main`

The current production baseline includes:

- **Story Discovery & StoryIdentity** — explore multiple plausible engines, compare them, receive a bounded recommendation, and explicitly accept the chosen direction.
- **Genre Packs & overrides** — versioned genre knowledge, applicability/recommendation support, subgenre validation, and explicit authority-bearing acceptance/override paths.
- **Interactive genre pipelines** — neutral session/runtime infrastructure for built-in genre-specific StoryIdentity authoring.
- **Story Design Packs** — reusable craft/design knowledge with deterministic composition.
- **Creative Writing Tutor V1** — existing `auteur design tutor ...` guidance over Story Design Packs.
- **Decision-Oriented Tutor** — root `auteur tutor next/explain/show/choose/handoff/propose`, deterministic Decision Cards, source-bound local advisory sessions, stale-source blocking, and explicit routing into existing authority workflows.
- **Structure revision continuation** — explicit proposal inspect/select, fail-closed revision planning/validation, derived Narrative Change Preview, explicit confirmed application, and deterministic/read-only reassessment.
- **Project orientation** — dashboard Author Attention plus a loopback-only, read-only Guided Author Workspace V1.
- **Realization/state/provenance** — state coordination plus accumulated impact, convergence, decision, review, planning, simulation, and portfolio support.
- **Series / long-horizon support** — bounded accepted-history/current-state reconstruction, continuity machinery, derived Global Map/Focus support, and Guided Series Continuity Review V1.
- **Outline & drafting** — Cartographer outlines, chapter contracts, Bard/Critics drafting, retry, and explicit acceptance.

For exact current/pending boundaries, including open work, use [STATUS.md](STATUS.md).

## Guided Author Decision Loop

The Tutor now has a bounded continuation path from advice to the existing Structure authority workflow:

```text
Decision Card — DERIVED / NOT CANON
        ↓
Tutor session — LOCAL / NONCANONICAL
        ↓
author choice
        ↓
derived authority handoff
        ↓
noncanonical Structure proposal
        ↓
explicit proposal selection
        ↓
revision plan + validation
        ↓
derived Narrative Change Preview
        ↓
explicit revision apply --confirm
        ↓
read-only Decision Reassessment
        ↓
dashboard / Guided Author Workspace orientation
```

Important boundary: `tutor choose`, `tutor handoff`, `tutor propose`, proposal selection, revision planning, preview, and reassessment do **not** themselves modify accepted story state. For the supported Structure route, `auteur structure revision apply <plan_id> --project . --confirm` is the explicit authority-bearing step.

Core commands:

```powershell
auteur tutor next --pack superhero --decision "power origin"
auteur tutor explain --pack superhero --decision "power origin"
auteur tutor show <session_id> --project .
auteur tutor choose <session_id> choose --value "Keep the origin costly" --project .
auteur tutor handoff <session_id> --project .
auteur tutor propose <session_id> --project .
```

Persisted sessions require project-local source binding when they are created, for example `--project . --source identity=story_identity.yaml --source blueprint=blueprint.yaml`. Auteur fingerprints the actual file bytes and later blocks substantive responses or actionable continuation when the source no longer matches.

See [docs/guides/guided-author-decision-loop.md](docs/guides/guided-author-decision-loop.md) for the complete beginner-facing walkthrough and [docs/design/decision-oriented-tutor.md](docs/design/decision-oriented-tutor.md) for the Tutor authority/staleness model.

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

## Quick Start — Story Direction First

For a fresh project, the default Identity-stage path is Story Discovery: explore multiple narrative engines, review the advisory recommendation, and explicitly accept the direction you choose.

```powershell
# 1. Create a fresh working directory and ask Auteur for the next step
New-Item -ItemType Directory -Force .\tmp\shattered_crown | Out-Null
Push-Location .\tmp\shattered_crown
auteur workflow next .

# 2. Explore multiple story engines and receive an advisory recommendation
auteur story-discovery run "A detective investigates a locked manor murder" --recommend --output story_discovery --project .

# 3. Ask again: Auteur points to the recommended candidate
auteur workflow next .

# 4. Review the comparison, then explicitly accept the candidate you choose
# Replace candidate_X with the candidate you want to make authoritative.
auteur story-discovery accept story_discovery\candidate_X.yaml --output story_identity.yaml

# 5. Seed structural design from the accepted identity
auteur blueprint seed story_identity.yaml --output blueprint.yaml

# 6. Run whole-story structure diagnostics
auteur structure diagnose blueprint.yaml
Pop-Location
```

Story Discovery is advisory: search/recommendation writes candidate/comparison artifacts, not canonical `story_identity.yaml`. `auteur workflow next . --execute` will not auto-accept a Story Discovery candidate.

## Story Design Packs and Tutor Surfaces

List or inspect reusable Story Design Packs:

```powershell
auteur design pack list
auteur design pack list --json
auteur design pack inspect <pack_id>
```

Use the root decision-oriented Tutor for one bounded author decision:

```powershell
auteur tutor next --pack <pack_id> --decision "next creative decision" --premise "your story"
auteur tutor explain --pack <pack_id> --decision "next creative decision" --premise "your story"
```

The earlier V1 Tutor surface remains available for backward compatibility:

```powershell
auteur design tutor recommend --pack <pack_id> --decision "next creative decision" --premise "your story"
auteur design tutor explain --pack <pack_id> --decision "next creative decision" --premise "your story"
auteur design tutor alternatives --pack <pack_id> --decision "next creative decision" --premise "your story"
```

All of this guidance is advisory. It does not silently accept StoryIdentity or mutate the story.

## Major CLI Surfaces

### Story Discovery & Identity

```text
auteur story-discovery run <premise> --recommend --output <directory> [--project <path>]
auteur story-discovery accept <candidate.yaml> --output <story_identity.yaml>
auteur identity recommend <premise> --output <path>
auteur identity validate <story_identity.yaml>
auteur blueprint seed <story_identity.yaml> --output <blueprint.yaml>
```

### Structure

```text
auteur structure diagnose <blueprint.yaml>
auteur structure propose-repairs <blueprint.yaml>
auteur structure apply <proposal.yaml> <blueprint.yaml> [--in-place]
auteur structure generate <blueprint.yaml> [--symptom "text"]
auteur structure proposal inspect <proposal.yaml> --project .
auteur structure proposal select <proposal.yaml> --option <option_id> --project .
auteur structure revision plan --proposal <proposal.yaml> --project .
auteur structure revision validate <plan_id> --project .
auteur structure revision preview <plan_id> --project .
auteur structure revision apply <plan_id> --project . --confirm
auteur structure revision reassess <application_id> --project .
```

### Project Orientation

```text
auteur dashboard --project .
auteur workspace --project . --port 8765
```

`dashboard` and Guided Author Workspace V1 are derived/read-only. The workspace binds only to `127.0.0.1` and exposes no mutation POST endpoints; it presents Author Attention and the exact existing safe next command.

### Project Planning and Counterfactual Support

```text
auteur plan status
auteur plan graph
auteur plan next
auteur plan critical-path
auteur plan milestones
auteur plan refresh
auteur plan explain <id>
auteur plan history

auteur simulate create --decision <id> --candidate <id>
auteur simulate compare <scenario-a> <scenario-b>
auteur simulate inspect <id> --evidence --uncertainty
auteur simulate promote <id> --confirm
```

Planning and simulation are noncanonical decision-support surfaces. Promotion routes a scenario into review; it is not automatic narrative acceptance.

### Interactive Genre Pipelines

```text
auteur netorare init <project>
auteur mystery init <project>
auteur gentlefemdom init <project>
auteur gentlefemdom resume <project>
```

Interactive genre working state lives under `.auteur/genre_sessions/<genre>/session.json` and remains noncanonical until the documented completion/compilation/acceptance boundary is crossed.

### Outline & Drafting

```powershell
auteur init .\tmp\shattered_crown_project --from .\tmp\shattered_crown\blueprint.yaml
auteur cartographer compile .\tmp\shattered_crown\blueprint.yaml --output .\tmp\shattered_crown\cartographer_outline.yaml
auteur draft .\tmp\shattered_crown_project 1 --provider anthropic --max-iterations 3
```

If drafting exhausts its iteration cap:

```powershell
auteur accept .\tmp\shattered_crown_project 1
auteur retry .\tmp\shattered_crown_project 1 --max-iterations 2
```

Drafting is a downstream consumer of accepted/planned narrative state; it is not Auteur's primary first-value surface.

## Series and Long-Horizon Narrative Intelligence

Auteur has a bounded long-horizon architecture for preserving accepted history, rebuilding current narrative state, and projecting decision-relevant context through derived Global Map/Focus machinery. The architecture deliberately separates:

```text
accepted Direction / Realization
        ↓
accepted history + provenance
        ↓
deterministic current-state projection
        ↓
relationship/dependency index
        ↓
derived Global Map
        ↓
planning intent / question / horizon
        ↓
derived Focus / Decision Map
        ↓
advisory recommendation
        ↓
explicit author action
```

The current campaign is **not** authorizing speculative expansion. It is in `PROSPECTIVE_NATIVE_EVIDENCE_INCUBATION`: new ontology, extraction, V2 review, and scale work wait for a natural Auteur-native planning case that produces a concrete failure or opportunity.

See [docs/campaign/auteur-long-horizon-campaign-state.md](docs/campaign/auteur-long-horizon-campaign-state.md) and [docs/architecture/detailed-narrative-architecture-v1.md](docs/architecture/detailed-narrative-architecture-v1.md).

## Work That Is Not Shipped

Historical PR #167 for bounded Episode 1 Direction support is **closed / not merged / superseded**. Its ratified contract is preserved, and contemporary reconstruction is tracked separately; Episode 1 support must not be described as current production behavior.

Broader multi-episode/season expansion remains evidence-gated under the long-horizon campaign posture.

See [STATUS.md](STATUS.md) for current reconciliation details.

## Project Artifacts

A basic drafting project still uses transparent file artifacts such as:

```text
project/
  blueprint.yaml
  bible.json
  chapters/
    01/
      outline.yaml
      draft_v1.md
      validation_v1.json
      final.md
```

Additional subsystems persist their own derived, local, candidate, or authoritative artifacts under the documented project-local paths. See [docs/project-format.md](docs/project-format.md).

## Documentation Map

- [Current repository status](STATUS.md) — living operational state, open milestone work, next recommended action.
- [Guided Author Decision Loop](docs/guides/guided-author-decision-loop.md) — beginner-facing advice → proposal → revision → reassessment → orientation walkthrough.
- [Decision-Oriented Tutor](docs/design/decision-oriented-tutor.md) — root Tutor workflow, Decision Cards, session lifecycle, staleness, and authority boundaries.
- [Product Evolution Roadmap](docs/product-evolution-roadmap.md) — forward-looking product/repository candidates and evidence gates; advisory, not implementation authority.
- [Architecture Roadmap](docs/architecture-roadmap.md) — architecture integrity and architecture-specific extension history.
- [Mission](MISSION.md) — durable scope and invariants.
- [Product requirements](docs/PRD.md) — product contract and primary user.
- [Canonical narrative architecture](docs/narrative-architecture.md) — five semantic layers × scope axis.
- [Opinionated Narrative Engine](docs/opinionated-narrative-engine.md) — product design, first value, guided authoring, Map/Focus framing.
- [Detailed long-horizon architecture](docs/architecture/detailed-narrative-architecture-v1.md) — accepted-history/current-state/relevance architecture.
- [Long-horizon campaign state](docs/campaign/auteur-long-horizon-campaign-state.md) — evidence posture and authorization boundary.
- [Runtime/domain context](CONTEXT.md) — genre pipeline and compatibility terminology.
- [Project format](docs/project-format.md) — artifact contract.
- [Release qualification](docs/engineering/release-qualification.md) — candidate/release evidence rules.
- [Changelog](CHANGELOG.md) and [release records](docs/releases/README.md) — release history.

ADRs, qualification reports, research records, experiments, and product-validation documents are historical evidence. Do not rewrite them merely to make current status cleaner.

## Tests and Local Verification

Run the full test suite:

```powershell
python -m pytest
```

Run the repository verification stack:

```powershell
python scripts/check.py
```

CI runs the same verification entrypoint with `python scripts/check.py --skip-pytest`, alongside Linux Python 3.11/3.12/3.13 validation, a full Windows Python 3.13 test leg, and installed-wheel smoke according to `.github/workflows/validation.yml`. Real-provider smoke checks remain separate because they spend external API tokens.

## Versioning

`pyproject.toml` currently reports `0.37.1`. Current `main` also contains post-release development, so package metadata alone is not a complete development-status indicator.

Use [STATUS.md](STATUS.md) for the present-tense repository map and [docs/releases/](docs/releases/README.md) for release-specific claims.
