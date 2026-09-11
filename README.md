# Auteur

Auteur is a **local-first literary compiler and guided narrative-decision system for long-form fiction**. It helps an author turn raw creative input into a coherent story direction, preserve accepted narrative state over long horizons, diagnose structural problems, and make bounded creative decisions without silently surrendering story authority to a model.

The intended beginner experience is guided authoring with progressive disclosure. The CLI and transparent YAML/JSON/Markdown artifacts remain the advanced-author and engineering surface.

> **Current repository state:** [STATUS.md](STATUS.md)  
> **V1.0 support contract:** [docs/v1/v1-product-contract.md](docs/v1/v1-product-contract.md)  
> **V1.0 closure/qualification plan:** [docs/v1/v1-closure-plan.md](docs/v1/v1-closure-plan.md)  
> **Future product directions:** [docs/product-evolution-roadmap.md](docs/product-evolution-roadmap.md)  
> **Mission/invariants:** [MISSION.md](MISSION.md)  
> **Canonical architecture:** [docs/narrative-architecture.md](docs/narrative-architecture.md)

## Current Development Posture

The repository is in a **V1.0 closure program**, not an architecture-expansion program. The five-layer narrative architecture and the guided author decision loop already exist; current work closes their support, authority, recovery, beginner-control, provider, and release-evidence seams.

Package metadata remains `0.37.1`. The presence of V1 closure code does **not** mean `1.0.0` has been released. The final version/tag is blocked on the exact-candidate qualification gates in `docs/v1/v1-qualification-matrix.md`.

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
accepted StoryIdentity
  ↓
Blueprint / Structure planning
  ↓
deterministic diagnostics + bounded decision support
  ↓
explicit author decisions
  ↓
optional Realization / drafting / reconciliation / publication
```

For long-running work, Auteur externalizes accepted history and current narrative state so later decisions do not require reconstructing the entire story from scratch.

## Product Model

```text
AUTHOR-FACING PRODUCT
  guided authoring
  bounded creative decisions
  explanations / trade-offs / Tutor guidance
  local Guided Author Workspace

NARRATIVE COMPILER
  Ontology → Identity → Structure → Realization → Expression

SUPPORTING INTELLIGENCE
  diagnostics / provenance / impact / planning
  Series continuity / Global Map / Focus
  simulation / portfolio comparison / craft knowledge
```

The supporting systems remain subordinate to author authority. A result can be deterministic, reproducible, persisted, and selected without becoming canon.

## Canonical Architecture

Auteur uses five semantic layers:

1. **Ontology** — concepts, relationships, vocabulary, domain rules.
2. **Identity** — commitments such as genre, medium, target experience, theme, and core engine.
3. **Structure** — plans: arcs, beats, threads, chapter plans, setup/payoff intentions, thematic progression.
4. **Realization** — events and state changes: scenes, chronology, knowledge, location, inventory, relationships, character deltas.
5. **Expression** — language: prose, dialogue, voice, diction, imagery, pacing, revision.

The independent scope axis is:

```text
Universe → Series → Book → Chapter → Scene
```

Scopes are containers across semantic layers, not extra semantic layers. Validation, orchestration, provenance, diagnostics, editing, versioning, maps, Tutor guidance, and Workspace presentation/actions are cross-cutting systems.

### Realization ↔ Expression

For the bounded V1 Scene path, Expression may render or elaborate accepted Realization but may not silently redefine participants, event/state facts, knowledge, location, outcome, or other upstream authority. Structured contradictions can block prose acceptance and may create a **noncanonical upstream proposal**; the accepted Scene changes only through its own explicit authority workflow.

See [docs/expression-boundary.md](docs/expression-boundary.md).

## Author Authority

Auteur's central product rule is simple:

**Advice is not authority.**

- Story Discovery candidates are advisory until explicit StoryIdentity acceptance.
- Diagnostics do not apply their own repairs.
- Maps and projections are derived/rebuildable views, not second canon.
- Story Design Packs and Genre Packs are reusable knowledge, not story-instance canon.
- Decision Cards and Decision Handoffs are derived/noncanonical.
- Persisted Tutor sessions are local/noncanonical and source-currentness-bound.
- Structure proposal selection and revision planning are not acceptance.
- Narrative Change Preview and reassessment are derived/read-only.
- The supported Structure path changes accepted Structure only through explicit confirmed application.
- Workspace actions call the same application services as CLI adapters; the browser is not a second acceptance system.
- Failed authority-bearing operations must fail closed or explicitly record durable partial application; they never pretend success.

## Guided Author Decision Loop

```text
accepted story direction
→ bounded Tutor decision
→ advisory choice
→ derived authority handoff
→ concrete noncanonical proposal
→ explicit proposal selection
→ revision plan + validation
→ derived change preview
→ explicit confirmed Structure application
→ bounded reassessment
→ dashboard / Guided Author Workspace orientation
```

Core CLI route:

```powershell
auteur tutor next --pack <pack_id> --decision "next creative decision" --premise "your story" --project . --source identity=story_identity.yaml --source blueprint=blueprint.yaml
auteur tutor choose <session_id> choose --value "<choice>" --project .
auteur tutor handoff <session_id> --project .
auteur tutor propose <session_id> --project .
auteur structure proposal inspect <proposal.yaml> --project .
auteur structure proposal select <proposal.yaml> --option <option_id> --project .
auteur structure revision plan --proposal <proposal.yaml> --project .
auteur structure revision validate <plan_id> --project .
auteur structure revision preview <plan_id> --project .
auteur structure revision apply <plan_id> --project . --confirm
auteur structure revision reassess <application_id> --project .
```

If a process was interrupted while a Structure plan was in `applying`:

```powershell
auteur structure revision recover --project .
```

Recovery never replays an authority-bearing revision automatically. It returns a stranded plan to `ready` only when current target hashes prove the authority targets are unchanged; otherwise it fails closed for inspection.

## Guided Author Workspace

Start the local browser surface:

```powershell
auteur workspace --project . --port 8765
```

Open `http://127.0.0.1:8765` locally.

The V1 closure implementation upgrades the Workspace from read-only V1 orientation to a bounded **Workspace V2** control plane over the existing decision-loop services. It can record supported Tutor choices, review/select Structure proposals, create/validate/preview plans, and explicitly confirm the supported Structure authority action. It then reloads the same Author Attention projection.

Security/authority boundaries:

- binds only to `127.0.0.1`;
- validates Host and same-origin POST Origin;
- uses a session-specific CSRF token;
- mutation is POST-only;
- action payloads are bounded;
- project paths are confined to the selected project;
- canonical Structure application has its own explicit confirmation;
- no endpoint creates an alternate story-state database.

## Story Discovery Quick Start

```powershell
New-Item -ItemType Directory -Force .\tmp\shattered_crown | Out-Null
Push-Location .\tmp\shattered_crown

auteur workflow next .
auteur story-discovery run "A detective investigates a locked manor murder" --recommend --output story_discovery --project .
auteur story-discovery accept story_discovery\candidate_X.yaml --output story_identity.yaml
auteur blueprint seed story_identity.yaml --output blueprint.yaml
auteur structure diagnose blueprint.yaml

Pop-Location
```

Story Discovery recommendation remains advisory. `auteur workflow next . --execute` does not auto-accept a Story Discovery candidate.

## Story Design Packs and Tutor

```powershell
auteur design pack list
auteur design pack inspect <pack_id>
auteur tutor next --pack <pack_id> --decision "next creative decision" --premise "your story"
auteur tutor explain --pack <pack_id> --decision "next creative decision" --premise "your story"
```

The earlier `auteur design tutor ...` surface remains available for compatibility. Tutor guidance never silently accepts narrative authority.

## Outline, Drafting, and Publishing

```powershell
auteur init .\tmp\project --from .\tmp\story\blueprint.yaml
auteur cartographer compile .\tmp\story\blueprint.yaml --output .\tmp\story\cartographer_outline.yaml
auteur draft .\tmp\project 1 --provider anthropic --max-iterations 3
```

If drafting exhausts its iteration cap:

```powershell
auteur accept .\tmp\project 1
auteur retry .\tmp\project 1 --max-iterations 2
```

Accepted Book output can be published as HTML or EPUB through the documented `auteur publish` workflow. External-platform auto-publishing remains out of scope.

## Providers

Install Anthropic support:

```powershell
python -m pip install -e ".[dev,anthropic]"
$env:ANTHROPIC_API_KEY = "..."
```

Install OpenAI support:

```powershell
python -m pip install -e ".[dev,openai]"
$env:OPENAI_API_KEY = "..."
```

Both:

```powershell
python -m pip install -e ".[dev,all]"
```

V1 defines stable provider-independent operational error categories for missing/invalid credentials, rate limiting, timeout, connection failures, provider 5xx responses, malformed responses, retry exhaustion, and related structured-output/user-interruption boundaries. These categories are operational guarantees, not literary-quality judgments.

The opt-in live release smoke is deliberately separate from ordinary CI because it uses external credentials/tokens:

```powershell
python scripts/qualify_v1_provider.py --provider anthropic --output .auteur/qualification/anthropic.json
python scripts/qualify_v1_provider.py --provider openai --output .auteur/qualification/openai.json
```

## Series and Long-Horizon Support

Auteur has bounded accepted-history/current-state reconstruction and derived Global Map/Focus/continuity support. This is a bounded V1 capability—not a claim that 50/100+ Book scale is qualified.

The long-horizon campaign remains prospective and evidence-gated. No generalized Episode 2+, universal extraction/relationship ontology, generic graph database, or very-large-scale program follows automatically from V1 closure.

Historical Episode 1 PR #167 remains closed/not merged/superseded. Contemporary reconstruction is preserved separately in issue #218 and is not a V1 blocker.

## V1 Support Boundary

The exact support contract is [docs/v1/v1-product-contract.md](docs/v1/v1-product-contract.md).

In short:

- Scene/Chapter/Book: supported.
- Series: bounded continuity/history support.
- Universe: experimental/optional supporting tooling, not a provenance-normalized V1 authoring vertical.
- Linux Python 3.11/3.12/3.13 and Windows Python 3.13: release-qualified only after the exact final candidate passes.
- macOS: best effort unless explicitly added to the final qualification matrix.
- HTML/EPUB: V1 publication outputs.
- PDF, cloud collaboration, external auto-publishing, generalized serial progression, and 50/100+ Book scale: not required for 1.0.

## Tests and Qualification

Full suite:

```powershell
python -m pytest
```

Repository verification:

```powershell
python scripts/check.py
```

Hermetic V1 closure bundle:

```powershell
python scripts/qualify_v1_author_journey.py
```

CI runs Linux Python 3.11/3.12/3.13, a full Windows Python 3.13 leg, installed-wheel smoke, repository verification, and the dedicated V1 closure evidence bundle. The V1 platform tests exercise semantic hashing across line endings/key order/Unicode normalization, Unicode artifact paths, project relocation, restart, and downstream staleness.

## Documentation Map

- [Repository status](STATUS.md) — current selected work and exact next gate.
- [V1 Product Contract](docs/v1/v1-product-contract.md) — exact support surface and claim ceiling.
- [V1 Closure Plan](docs/v1/v1-closure-plan.md) — implementation/qualification work packages.
- [V1 Authority Artifact Matrix](docs/v1/v1-authority-artifact-matrix.md) — authority/provenance classification.
- [V1 Qualification Matrix](docs/v1/v1-qualification-matrix.md) — evidence required before `1.0.0`.
- [V1 Completeness Audit](docs/v1/v1-completeness-audit.md) — implemented versus still-unqualified surfaces.
- [Guided Author Decision Loop](docs/guides/guided-author-decision-loop.md) — advice → proposal → explicit change → reassessment.
- [Product Evolution Roadmap](docs/product-evolution-roadmap.md) — post-closure candidates and evidence gates.
- [Mission](MISSION.md) — durable invariants/non-goals.
- [Product requirements](docs/PRD.md) — product requirements and primary user.
- [Canonical narrative architecture](docs/narrative-architecture.md) — five semantic layers × scope axis.
- [Expression boundary](docs/expression-boundary.md) — Realization/Expression ownership contract.
- [Long-horizon campaign](docs/campaign/auteur-long-horizon-campaign-state.md) — evidence posture.
- [Project format](docs/project-format.md) — artifact layout/compatibility.
- [Release qualification](docs/engineering/release-qualification.md) — exact candidate/release evidence rules.
- [Changelog](CHANGELOG.md) and [release records](docs/releases/README.md) — release history.

## Versioning

`pyproject.toml` currently reports `0.37.1`. The V1 closure program deliberately leaves that version unchanged until the final release candidate satisfies the exact release invariant. Use [STATUS.md](STATUS.md) for development state and [docs/releases/](docs/releases/README.md) for release claims.
