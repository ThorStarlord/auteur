# Auteur Repository-Wide Architecture and Feature Completeness Audit

**Audit date:** 2026-07-18  
**Repository:** `ThorStarlord/auteur`  
**Default-branch commit inspected:** `68351194a30d126b74d0fd4485fb0f10753b50df`  
**Released commit used for comparison:** `10fbbd1cd74a3acefe9065d413c37be350b7882e` (`v0.2.0`)  
**Audit mode:** source, tests, documentation, packaging configuration, and Git history inspected through the GitHub integration. The full suite, wheel build, and fresh-environment install were **not re-executed** in this connector-only audit. Historical test claims are identified as such.

## 1. Executive conclusion

Auteur is a real, usable, opinionated narrative-authoring system with a particularly deep Expression and reconciliation implementation. It is not merely an architecture prototype. The supported path from Story Identity and Blueprint through drafting, accepted Chapter/Book expressions, reconciliation, and HTML/EPUB export is substantially implemented.

However, the repository is **not complete in every sense**:

- Not all five semantic layers are complete or equally integrated.
- Not every narrative concept has one unified, typed, provenance-aware artifact.
- Not every public command is release-ready.
- Several release guarantees are stronger in documentation than in code.
- The current default branch differs materially from the `v0.2.0` release commit and contains tracked generated/scratch artifacts.

The correct overall verdict is:

```text
Architectural model: coherent and operational
Supported opinionated product path: substantially complete
All semantic layers: not complete
All narrative artifacts: not complete or unified
All public/documented features: not fully complete
Long-term product vision: not complete
```

The highest-leverage next phase is **v0.2.1 Release Integrity and Product Invariants Hardening**, not another narrative subsystem.

---

## 2. Audit scope and evidence standard

This audit distinguishes:

- **architectural layer** — a semantic kind of narrative knowledge;
- **supporting subsystem** — an implementation used by one or more layers;
- **cross-cutting infrastructure** — provenance, reasoning, validation, transformation, import/export;
- **workflow** — an ordered user or system process;
- **artifact type** — a persisted narrative, derived, decision, or pointer record;
- **CLI surface** — user-facing invocation, not proof of backend completeness;
- **experimental package** — code that performs some real work but is not yet a stable, unified product path.

Statuses used:

- `COMPLETE`
- `FUNCTIONAL_BUT_PARTIAL`
- `SCAFFOLDED`
- `STUB_ONLY`
- `DEPRECATED`
- `ARCHIVED`
- `MISSING`

A command, file, model, or test name was not treated as proof. Statuses are based on production behavior, persistence, validation, call sites, tests, and integration.

---

## 3. Repository and release reality

### 3.1 Release and default branch are different audit targets

The released version is `v0.2.0` at `10fbbd1`. The current default branch is `6835119`, eight commits ahead.

The post-release default branch adds primarily generated or local-development artifacts, including:

- `.superpowers/sdd/task-a13-report.md`;
- a Windows scratch-output filename at repository root;
- a tracked `examples/canonical_story/temp_lantern_phase_a/...` dogfood tree;
- `uv.lock`.

This is a repository-hygiene regression. It does not invalidate the released feature set, but it means current `main` is not a clean synonym for the release tag.

### 3.2 CI evidence

A validation workflow exists and runs Python 3.11 with `python scripts/check.py`. That script runs validator checks, repository validation, and `pytest tests -q`. No GitHub Actions run was available through the connector for the inspected default-branch commit, so this audit does not inherit a fresh CI result.

### 3.3 Packaging configuration

`pyproject.toml` declares version `0.2.0`, exposes the `auteur` console script, packages `src/auteur`, and includes data under `src/auteur/data`.

The packaged `sample_blueprint.yaml` is present. Ontology YAML is stored under repository-root `data/ontology`, while `OntologyLoader` resolves that repository-relative path. No corresponding `src/auteur/data/ontology/base_ontology.yaml` is present. Therefore Ontology can work from a source checkout while failing in an installed wheel.

---

## 4. Canonical architecture map

The canonical semantic architecture is:

```text
Layer 0 — Ontology: concepts and relationships
Layer 1 — Identity: narrative commitments
Layer 2 — Structure: plans, arcs, beats, sequencing
Layer 3 — Realization: concrete events and state changes
Layer 4 — Expression: rendered language and prose
```

Scopes such as Universe, Series, Book, Chapter, and Scene are containers across the semantic layers, not extra semantic layers.

Cross-cutting systems include Provenance, Transformation, Reasoning, Validation, Editing, Orchestration, Import/Export, and Diagnostics.

---

## 5. Layer implementation matrix

| Layer | Status | Evidence | Incomplete or divergent behavior | Released product role |
|---|---|---|---|---|
| Layer 0 — Ontology | **FUNCTIONAL_BUT_PARTIAL** | Typed concept/relationship models; core concepts; YAML loader/merge/cache; CLI; validation and integration tests | Package data is outside the wheel package; validation is shallow for unresolved targets; built-in genre list is hard-coded to three; not a required source of truth for the main product path | Experimental/optional analysis and vocabulary layer |
| Layer 1 — Identity | **COMPLETE** | `StoryIdentity`, genre/medium contracts, validation, recommendation, Story Discovery, genre pipelines, compilation to `StoryBlueprint`, CLI and tests | LLM recommendation quality remains provider-dependent; hidden open-ended mode is not a default product path | Production foundation |
| Layer 2 — Structure | **COMPLETE** for the primary model; supporting outline system **FUNCTIONAL_BUT_PARTIAL** | `StoryBlueprint`, deterministic diagnostics, proposal generation/application, Cartographer audits, `narrative_blueprint` schemas/loaders/validators, orchestration seed/validate/graph/status | Two parallel structural representations (`StoryBlueprint` and `narrative_blueprint` outline artifacts); orchestration is genre-path-specific; some CLI logic is brittle; provenance/authority is not uniform across both representations | Production foundation plus advanced outline subsystem |
| Layer 3 — Realization | **FUNCTIONAL_BUT_PARTIAL** | Rich `SceneOutline` schema, loader, knowledge/temporal/realization validators, seed/validate/inspect/graph CLI, accepted Scene Realizations used by Expression and canonical dogfood | Seeded scenes are placeholders; fixed heuristics and three hard-coded genres; rich SceneOutline is not the universal input of the legacy drafting pipeline; graph/rendering path has naming inconsistencies; state ownership overlaps Bible/relations | Real production data for Expression, but not one unified product layer |
| Layer 4 — Expression | **COMPLETE** for the supported Chapter/Book workflow | Scene candidates, lifecycle, Chapter composition, Book composition, Chapter and Book reconciliation, planning, atomic publication, decisions, accepted-source pointers, recomposition, comparison, acceptance, completion, publishing | Older Scene and direct Book acceptance paths are less atomic than the newer reconciliation paths; `status()` can mutate candidate review metadata; legacy `final.md` drafting coexists with accepted Expression artifacts | Deepest and most complete production layer |

### 5.1 Direct answers about the five layers

- **Ontology:** implemented, but partial and not install-safe.
- **Identity:** implemented and complete for the supported product.
- **Structure:** implemented and complete in the primary engine; parallel outline/orchestration path remains partially unified.
- **Realization:** implemented and useful, but partial and unevenly integrated.
- **Expression:** implemented and complete for the supported Chapter/Book path, with legacy-path hardening debt.

Therefore: **not all architectural layers are fully implemented**.

---

## 6. Cross-cutting subsystem matrix

| Subsystem | Status | Key evidence | Main limitation |
|---|---|---|---|
| Provenance | **FUNCTIONAL_BUT_PARTIAL** | Typed lifecycle/review/dependency records; normalized hashes; immutable snapshots; direct dependency projections; freshness and impact analysis | `ArtifactStore` still describes a pilot chain and does not own every artifact family; newer Expression workflows implement parallel provenance conventions; broad exception handling can hide validation failures |
| Transformation | **COMPLETE** for Chapter/Book Expression | Candidate → proposal → plan → publication → decision → accepted source → recomposition → comparison → acceptance → completion | Not uniformly adopted by Identity, Structure, Universe, Series, Relations, and legacy drafting paths |
| Reasoning runtime | **FUNCTIONAL_BUT_PARTIAL** | In-process registry, dependency DAG, outcomes, persisted reports, freshness snapshots, two deterministic critics, synthesis and review CLI | Version selection is lexical rather than semantic; freshness depends heavily on caller-supplied snapshots; reasoning sections are mechanically derived from findings; only a small number of deterministic adapters |
| LLM critics | **FUNCTIONAL** | Five critics, typed findings, parallel execution, explicit parse failures | Provider-dependent; separate from the deterministic reasoning registry; not clean-install/real-provider verified here |
| Pipeline | **FUNCTIONAL_BUT_PARTIAL** | Cartographer → Bard → critics → iteration → final/Bible update | Successful critic pass automatically writes `final.md` and mutates Bible, crossing authority without the newer explicit Expression acceptance protocol; malformed duplicated header/imports indicate maintenance debt |
| Chapter reconciliation | **COMPLETE** | Inspection, proposals, plan, publication, candidate lifecycle, recomposition, acceptance, completion | Advanced markerless mapping and Scene merge/split intentionally deferred |
| Book reconciliation | **COMPLETE** | Ownership routing through C1–C4, accepted-source pointers, exact comparison, atomic acceptance, administrative completion | Extremely large implementation module; needs continued regression/maintainability attention |
| Publishing | **FUNCTIONAL_BUT_PARTIAL** | Immutable source snapshot, run history, HTML and EPUB renderers, CLI, tests | EPUB `mimetype` is compressed instead of stored; claimed byte determinism is undermined by current timestamps and ZIP metadata; accepted-manuscript tampering is not rejected; version metadata is hard-coded to `0.1.0`; optional Markdown renderer is undeclared |
| Schema version guard | **FUNCTIONAL** | `.auteur/project.yaml`, supported version check, warning/rejection | No migration registry, migration command, or artifact-family migration framework; “schema migration” is not implemented |
| Author status | **FUNCTIONAL_BUT_PARTIAL** | Aggregates identity/blueprint/chapter/book/reconciliation and suggests next command | Reads Identity fields through paths that do not match current schema; recommends `init --from story_identity` though `init` expects Blueprint; empty chapter list can cause indexing failure; some freshness is read from stored payload rather than live stores |
| Genre pipeline | **COMPLETE** for three built-ins | Generic shared runtime, sessions, validation, browser workflow, identity compilation, CLI | Built-in coverage remains three genres; external plugin distribution is not implemented |
| Genre Builder | **FUNCTIONAL** | Build, validate, explain, install, list project-local contracts | Does not itself create a new interactive core pipeline or plugin distribution package |
| Series | **FUNCTIONAL_BUT_PARTIAL** | Validate, compile, diagnose, graph, Bible; continuity validators; Universe integration | No uniform accepted-artifact/provenance lifecycle; relative Universe paths can depend on current working directory; limited end-to-end authored dogfood |
| Universe | **FUNCTIONAL_BUT_PARTIAL** | Typed model, validation, diagnostics, canonical write command | Directly writes “canonical” YAML without the main acceptance/provenance protocol |
| Character | **FUNCTIONAL** | Categorize, diagnose, show | Mostly derived output; no independent accepted Character artifact lifecycle |
| Relations | **FUNCTIONAL** | Validate, diagnose, graph, apply declared changes | Separate state authority model; not normalized into the main transformation lifecycle |
| Editing | **FUNCTIONAL** | Review, accept/reject patch, apply accepted patch | Chapter/draft-oriented and separate from newer Expression reconciliation |
| Markdown round-trip | **FUNCTIONAL** | Export, import, drift/proposals, confirm, promote draft | Chapter Markdown only; separate from full Book reconciliation and publishing formats |

---

## 7. Narrative Artifact Registry

The table below records the material artifact families needed to understand the current product. Several families use dictionaries and YAML conventions rather than one central typed schema.

| Artifact | Owner | Authority/lifecycle | Persistence | Creator / consumer | Validation, provenance, freshness | Status |
|---|---|---|---|---|---|---|
| Project metadata | Infrastructure | mutable project metadata | `.auteur/project.yaml` | `Project.init/load` | schema-version check only | Implemented; no migrations |
| Genre session | Identity workflow | mutable session, then completed | `.auteur/genre_sessions/<genre>/session.json` | Genre pipeline runtime | typed session model and validation | Implemented |
| Story Identity | Identity | author/canonical by workflow | `story_identity.yaml` | recommend, Story Discovery, genre pipeline, compile | Pydantic validation; optional provenance sidecar | Implemented |
| Story Identity candidate/set | Identity | candidate/derived | recommendation/discovery output directories | recommendation and discovery workflows | validation before promotion | Implemented |
| Genre Contract | Ontology/Identity | contract; built-in or project-local | package/project YAML | Genre Builder and registry | typed contract validation | Implemented |
| Genre guide | Identity support | derived | user-selected Markdown output | `genre explain` | source contract linkage is informal | Implemented |
| Story Blueprint | Structure | canonical file by convention | `blueprint.yaml` | identity compile, structure commands, project init | Pydantic model/validators; optional provenance sidecar | Implemented |
| Narrative outline artifacts | Structure | planned/canonical by workflow | `.auteur/outlines/<genre>/*.yaml` | orchestration/blueprint CLI | typed schemas, references, chronology, contradiction validators | Implemented; parallel model |
| Structure diagnostic | Structure/Validation | derived | CLI output / JSON | analyzer/audits | typed diagnostic | Implemented |
| Structure proposal | Structure/Transformation | proposal | `structure/proposals/...` | diagnostics and critic repair writer | target/source-domain checks vary by producer | Implemented |
| Story Bible | Realization/state | operational state | `bible.json` | drafting pipeline, state/audit | typed wrapper but mutable operational model | Implemented; overlapping authority |
| Scene Realization | Realization | accepted or draft | `.auteur/scenes/...` and/or `chapters/*/scenes/*.yaml` | realization CLI, bootstrap, ArtifactStore | rich schema and validators; multiple path conventions | Implemented, partial integration |
| Scene prose candidate | Expression | candidate → accepted/rejected/replaced | `chapters/<n>/scenes/<scene>/prose_vNNN.{md,yaml}` | `ExpressionStore` | source Scene revision/hash, validation findings, review state | Implemented |
| Scene accepted pointer/copy | Expression | accepted convenience record | `.../<scene>/accepted.yaml` | Scene acceptance and Chapter composition | full metadata copy rather than minimal pointer | Implemented |
| Chapter Expression | Expression | derived/proposed → accepted | `chapters/<n>/expression/chapter_vNNN.{md,yaml}` | Chapter composer/reconciliation | source Structure/Scene/transition snapshots and freshness | Implemented |
| Chapter transition manifest | Expression | Chapter-owned content | `chapters/<n>/expression/transitions.yaml` | Chapter composition/reconciliation | boundary and content checks | Implemented |
| Chapter accepted record | Expression | accepted convenience record | `chapters/<n>/expression/accepted.yaml` | Chapter acceptance/Book composition | metadata copy; direct acceptance path is less atomic | Implemented |
| Book Expression | Expression | derived/proposed → accepted | `book/expression/book_vNNN.{md,yaml}` | Book composer/reconciliation | Chapter revision/hash/order checks | Implemented |
| Book structure/order | Expression/Structure boundary | mutable Book assembly order | `book/structure.yaml` | Book composer and reconciliation | order checks; not a full provenance pointer | Implemented |
| Book accepted record | Expression | accepted pointer/copy | `book/expression/accepted.yaml` | Book acceptance/publishing | direct Book acceptance path differs from reconciliation acceptance | Implemented |
| Artifact provenance sidecar | Provenance | canonical metadata snapshot | `.auteur/state/artifacts/*.yaml` | `ArtifactStore` | normalized hash, dependency projection, revisions | Implemented for selected families |
| Artifact metadata revision | Provenance | immutable history | `.auteur/state/artifacts/revisions/<id>/NNNNNN.yaml` | `ArtifactStore` | immutable-if-new | Implemented |
| Reasoning report | Reasoning | derived | caller-supplied report directory, JSON | Reasoning runtime | critic/version/source snapshot | Implemented |
| Reasoning synthesis review | Reasoning | derived | report directory, JSON | synthesis | source report references and freshness | Implemented |
| Editing review/patch proposal | Editing | derived/proposed/accepted/rejected | chapter editing artifact directory | editing handlers/serializers | patch staleness and target state | Implemented |
| Round-trip export/import run | Import/export | external/derived history | chapter export/import directories | roundtrip workflow | manifests, drift reports, proposals | Implemented |
| Chapter reconciliation inspection/run/proposal | Expression | derived/proposed | `chapters/*/expression/reconciliation/{runs,inspections,proposals,...}` | reconciliation store | source assembly/manuscript hashes | Implemented |
| Chapter reconciliation plan/publication | Transformation | derived/published | reconciliation plan/publication paths | plan/publish | live freshness, atomic publication | Implemented |
| Chapter candidate decision | Decision | append-only decision | publication decision paths | reconciliation decisions | candidate snapshot and provenance | Implemented |
| Chapter recomposition/comparison/acceptance/completion | Expression/Decision/Admin | derived/evaluated/accepted/completed | reconciliation paths | C1–C4 workflow | accepted-source snapshots and gates | Implemented |
| Book reconciliation inspection/routing/proposal | Expression | derived/proposed | `book/expression/reconciliation/...` | Book routing | marker ownership and freshness | Implemented |
| Book plan/publication/candidate | Transformation | derived/published/candidate | Book reconciliation paths | plan/publish | live freshness and atomic transaction | Implemented |
| Book-owned accepted revision | Expression | immutable accepted source | Book reconciliation `accepted-sources/...` | candidate approval | decision and source snapshots | Implemented |
| Book-owned current pointer | Pointer | mutable pointer only | Book reconciliation pointer paths | approval/recomposition | pointer history and freshness | Implemented |
| Book recomposition/comparison | Expression/Evaluation | derived/proposed/evaluated | reconciliation recomposition/comparison paths | C1/C2 | pointer snapshots, exact residual classification | Implemented |
| Book acceptance record/revision | Decision/Expression | immutable decision + accepted revision | acceptance paths plus accepted Book pointer | C3 | exact-match gate, pointer-last atomicity | Implemented |
| Book reconciliation completion | Administration | derived/completed | completion paths | C4 | full provenance chain; no authority move | Implemented |
| Publishing snapshot | Publishing | immutable derived snapshot | `.auteur/publishing/pub_<id>.yaml` | `PublishingSnapshot.save_snapshot` | source Book manifest/text hash | Implemented; version metadata defect |
| Publishing run | Publishing | append-only run history | `.auteur/publishing/runs/run_<timestamp>_<uid>.yaml` | each publish invocation | renderer options and output hash | Implemented |
| Publishing latest | Pointer | mutable convenience pointer | `.auteur/publishing/latest.yaml` | publishing | points to most recent run | Implemented |
| HTML output | Output | replace-protected output | user-selected `.html` | publisher | output hash, no internal markers | Implemented |
| EPUB output | Output | replace-protected output | user-selected `.epub` | publisher | ZIP structure tests; conformance/determinism gaps | Implemented but partial |
| Series Identity/BookPlan | Series scope | source contract | `series_identity.yaml` | Series CLI | typed model validation | Implemented |
| Series Book identities | Identity/Series | generated identities | output directory | series compile | StoryIdentity validation | Implemented |
| Series diagnostics/graph/Bible | Derived | derived | JSON/YAML/Mermaid outputs | Series workflow | deterministic validators | Implemented |
| Universe Identity/diagnostics | Universe scope | source/canonical by command | user YAML / diagnostics text | Universe CLI | typed model validation | Implemented; no acceptance lifecycle |
| Character categorization | Character | derived | stdout or JSON | Character CLI | Blueprint-based deterministic analysis | Implemented |
| Relations map/changes/diagnostics/graph | Realization/state | state + derived outputs | project YAML/JSON | Relations CLI | handler validation | Implemented |

### 7.1 Artifact discrepancies

- **Described but not installable:** Ontology YAML package data.
- **Implemented but under-documented:** complete Book reconciliation C1–C4 details exceed several older roadmap documents.
- **Implemented without one typed schema:** many reconciliation and publishing manifests are dictionary-shaped YAML.
- **Duplicate representations:** `StoryBlueprint` versus `narrative_blueprint` outlines; Bible/relations versus Scene state; legacy `final.md` versus accepted Scene/Chapter/Book Expression.
- **Authority inconsistency:** some older workflows mutate source artifacts directly while newer reconciliation workflows create immutable revisions and pointer transitions.

---

## 8. Workflow completeness matrix

| Workflow | Status | Entry point | Assessment |
|---|---|---|---|
| Genre pipeline | **RELEASE_READY** for source/wheel if assets present | `auteur <genre> init` | Shared runtime, session, validation, browser workflow, identity compilation; three built-ins |
| Story Identity creation | **RELEASE_READY** | `identity recommend`, Story Discovery, genre pipeline | Full validation/candidate promotion; LLM-dependent generation |
| Blueprint loading/validation | **RELEASE_READY** | `identity compile`, `blueprint seed`, structure commands | Typed model, diagnostics, proposals |
| Structure diagnosis | **RELEASE_READY** | `structure diagnose` | Rich deterministic analyzer and audits |
| Structure proposal generation/application | **FUNCTIONAL** | `structure propose-repairs/apply` | Real proposals; not fully normalized into general transformation/provenance architecture |
| Cartographer planning | **FUNCTIONAL** | `plan`, `cartographer` | Real prompt/outline compilation; LLM-dependent |
| Chapter drafting | **FUNCTIONAL_BUT_PARTIAL** | `draft` | End-to-end generation/critics/Bible update; auto-finalizes and mutates state without newer explicit acceptance protocol |
| Critic evaluation | **FUNCTIONAL** | drafting pipeline | Five LLM critics, typed findings and parse-failure handling |
| Chapter reconciliation | **RELEASE_READY** | `expression reconcile ...` | Deep, explicit lifecycle and authority boundaries |
| Book reconciliation | **RELEASE_READY** | Book expression reconciliation commands | Full routing through completion; high test depth |
| Editing | **FUNCTIONAL** | `edit review/accept/reject/apply` | Controlled patch workflow |
| Markdown round-trip | **FUNCTIONAL** | `export chapter`, `import chapter/confirm/promote-draft` | Chapter Markdown only |
| Series management | **FUNCTIONAL** | `series validate/compile/diagnose/graph/bible` | Real cross-book behavior; no unified accepted lifecycle |
| Universe management | **FUNCTIONAL** | `universe validate/diagnose/build` | Real models/validation; direct canonical write |
| Character analysis | **FUNCTIONAL** | `character categorize/diagnose/show` | Derived analysis only |
| Relations tracking | **FUNCTIONAL** | `relations validate/diagnose/graph/apply` | Real state workflow, separate authority model |
| `auteur status` | **PARTIAL** | `status` | Useful aggregation but schema/next-command bugs and incomplete live freshness |
| HTML publishing | **FUNCTIONAL_BUT_PARTIAL** | `publish --format html` | Good output/snapshot model; timestamp-dependent byte output despite deterministic claim |
| EPUB publishing | **FUNCTIONAL_BUT_PARTIAL** | `publish --format epub` | Real EPUB structure; compressed `mimetype`, timestamp/ZIP nondeterminism, no external validator evidence |
| Schema loading/version validation | **FUNCTIONAL** | `Project.init/load` | Version guard only |
| Schema migration | **NONFUNCTIONAL / MISSING** | none | No migration registry or command |

### 8.1 Supported author workflow

A supported opinionated author can, in source checkout conditions:

```text
Identity → Blueprint → Structure → drafting/Expression
→ Chapter/Book acceptance and reconciliation
→ accepted Book → HTML/EPUB output
```

That path is substantially complete. It is not uniformly governed by the same authority model at every legacy step, and installed-wheel coverage is not complete for all advertised subsystems.

---

## 9. CLI completeness matrix

| Top-level command | Backend status | Test/product status | Recommended action |
|---|---|---|---|
| `status` | partial | useful but schema/next-command bugs | harden in v0.2.1 |
| `publish` | partial | real HTML/EPUB output; invariant gaps | harden in v0.2.1 |
| `init` | complete | Blueprint-based project init | clarify `--from` help and status suggestion |
| `plan` | functional | prompt only | keep |
| `draft` | functional/legacy | auto-authority crossing | align with Expression acceptance |
| `accept` | functional/legacy | final.md promotion | document relation to Expression acceptance |
| `retry` | functional | LLM-dependent | keep |
| `audit` | functional | Bible/state audit | keep; terminology is legacy “layers” |
| `structure` | complete | diagnose/propose/apply/generate | keep |
| `reasoning` | functional | review/inspect only | add registry/runtime execution UX later |
| `identity` | complete | validate/compile/recommend plus hidden candidate flow | keep |
| `story-discovery` | complete | run/accept | keep |
| `blueprint` | mixed | primary seed plus parallel outline commands | clarify names/models |
| `character` | functional | categorize/diagnose/show | keep |
| `series` | functional | all five commands real | add lifecycle/provenance later |
| `edit` | functional | four patch commands | keep |
| `relations` | functional | four state commands | keep |
| `export` / `import` | functional | Chapter Markdown round-trip | keep; distinguish from publishing |
| `genre` | functional | build/validate/explain/install/list | keep |
| `universe` | functional | validate/diagnose/build | add explicit acceptance semantics later |
| `book` | functional | BookPlan → StoryIdentity | keep |
| `state` | functional | check/update/prepare/canon/confirm plus provenance commands | high cognitive load; improve help grouping |
| `expression` | complete but very large | full Scene/Chapter/Book workflow | improve guided UX; preserve backend |
| `cartographer` | functional | compile/validate | keep |
| `ontology` | source-functional, wheel-risk | inspect/list/validate/themes | package resources before advertising as installed feature |
| `netorare`, `mystery`, `gentlefemdom` | complete built-in pipelines | interactive browser workflows | keep |

The CLI is broad, but discoverability remains weak: many commands, overlapping vocabulary, mixed error formats, hidden commands, no guided workflow, and experimental subsystems exposed alongside release-ready ones.

---

## 10. Incomplete implementation signals and dead paths

### Production-relevant findings

- Ontology data is repository-relative rather than package-relative.
- Realization SceneBuilder deliberately emits placeholder/draft scenes and uses fixed heuristics.
- Orchestration and Realization are hard-coded to three genres in several places.
- Provenance Scene validation swallows broad exceptions and treats the result as no additional invalidity.
- Reasoning runtime freshness is caller-snapshot-driven and does not independently inspect live files.
- `PipelineRunner` has duplicated imports/malformed module-header ordering and auto-finalizes a passing draft.
- `ExpressionStore.status()` may write review metadata while being called as a status query.
- Direct Scene and Book acceptance update multiple authority-bearing files without the pointer-last transaction model used in reconciliation.
- Current `main` tracks generated dogfood/scratch files.

### Signals that are not product stubs

Most `pass` occurrences are exception classes or test helpers. Repository TODO/FIXME/NotImplemented searches primarily return scripts, archived plans, and controlled-failure fixtures rather than active product placeholders.

---

## 11. Documentation-versus-code discrepancies

| Documentation claim | Code reality | Classification |
|---|---|---|
| Ontology is merely experimental/core stubs | Substantial models, loader, CLI, and tests exist | Docs understate implementation, but omit wheel packaging failure |
| Narrative Realization backends are stubs | Rich schemas, loader, validators, CLI, builder, and tests exist | Docs understate implementation; product integration is still partial |
| Book-level publishing formats remain deferred | HTML and EPUB are implemented | Older completion review is stale |
| Publishing produces deterministic output bytes | HTML includes current date; EPUB metadata and ZIP timestamps vary | Documentation overstates guarantee |
| EPUB3 conformance is verified | Structure is tested, but `mimetype` is written compressed and no external conformance run is available | Documentation overstates conformance |
| Accepted manuscript tampering is detected | Publishing hashes current Book Markdown and can create a new snapshot after tampering without validating against accepted metadata | Documentation overstates integrity protection |
| Schema migration is complete | Only project schema version detection/warnings exist | “Migration” is unimplemented |
| Provenance is complete | Strong pilot chain and reconciliation provenance exist, but not one universal store/lifecycle for every scope | Documentation overstates uniformity |
| Critics are complete | Five LLM critics exist; deterministic reasoning has two adapters; no universal critic plugin/runtime coverage | Complete for current drafting, not vision-complete |
| Book reconciliation is complete | Code supports full C1–C4 flow | Supported claim confirmed |

---

## 12. Publishing and release audit

### Confirmed strengths

- Immutable publication snapshot is separated from mutable `latest.yaml` and append-only run records.
- HTML and EPUB output remove Auteur markers.
- EPUB contains OPF, nav, stylesheet, chapters, and container metadata.
- Output collision is blocked.
- Package version and `__version__` agree at `0.2.0`.
- Packaged sample blueprint exists under `src/auteur/data`.

### High-priority defects

1. **EPUB mimetype storage** — the `mimetype` entry is written with archive-wide `ZIP_DEFLATED`; EPUB requires it first and uncompressed.
2. **False byte determinism** — current date/time is embedded in HTML/EPUB and default ZIP timestamps vary.
3. **Hard-coded wrong producer version** — publishing snapshot records `auteur_version: 0.1.0`.
4. **Accepted-source tamper gap** — published source text is not validated against the accepted Book manifest before snapshot creation.
5. **Optional undeclared Markdown renderer** — `markdown-it-py` changes output if installed but is not a declared runtime dependency.
6. **Binary hash encoding** — EPUB hash is computed through Latin-1 decode then UTF-8 re-encode instead of hashing raw bytes.
7. **No fresh installed-wheel audit in this run** — source inspection found Ontology resources missing from package configuration.

Publishing is functional, but it should not be described as fully qualified until these are corrected and a fresh wheel/external EPUB validation run passes.

---

## 13. Test confidence matrix

This audit did not execute tests. The table maps repository test presence and observed depth, not fresh pass counts.

| Capability | Direct tests | Integration/CLI | Failure/atomicity/freshness | Clean-install confidence |
|---|---|---|---|---|
| Ontology | high unit/integration presence | CLI tests exist | validation tests | **low** — package data missing |
| Identity/genre pipeline | high | CLI and browser/runtime tests | validation/session guards | medium-high |
| Structure | high | proposal/CLI/audit tests | error paths and proposals | high in checkout |
| Narrative Blueprint/Orchestration | high dedicated suites | CLI/integration tests | reference/chronology/contradiction | medium; parallel model |
| Realization | high dedicated suites | CLI and dogfood tests | knowledge/temporal/freshness | medium; product integration partial |
| Scene/Chapter Expression | very high | CLI/dogfood | lifecycle/staleness/reconciliation | high in checkout |
| Book reconciliation | very high (hundreds claimed and many files present) | complete CLI/dogfood | atomicity, pointer, freshness, duplicate handling | high in checkout |
| Reasoning | moderate | runtime/synthesis/review CLI | cycles/stale/failed outcomes | medium |
| Series/Universe/Character/Relations | moderate | CLI tests present | some error paths | medium |
| Status | limited direct evidence | CLI smoke implied | edge cases visibly unguarded | low-medium |
| Publishing | 52 historical release tests claimed; direct files present | CLI/module/package tests present | several specified invariants not actually asserted | medium-low until fixed and rerun |
| Schema migration | none | none | none | none |

### Test-confidence risks

- Some tests assert file presence or ZIP members without validating the specification-level invariant.
- Publishing “determinism” tests can pass within the same second despite timestamp-based output.
- EPUB tests check presence/order but do not assert `mimetype` compression type.
- Source-checkout tests cannot detect missing package resources unless run from an installed wheel outside the repository.
- Historical test totals are not fresh verification of current default branch.

---

## 14. Definitive gap register

| Gap | Category | Current state | Missing behavior / user impact | Severity / blocker | Effort | Recommendation / release |
|---|---|---|---|---|---|---|
| Release integrity and packaging invariants | infrastructure/product | v0.2.0 released; current main contaminated; ontology not packaged; publish claims exceed code | Installed feature failure and invalid reproducibility/conformance claims | **Critical; yes for next patch release** | medium | Implement v0.2.1 hardening |
| EPUB conformance and deterministic publishing | workflow/output | real renderer | uncompressed mimetype, stable metadata/ZIP timestamps, raw-byte hash, source tamper gate | **High; yes for publishing claims** | small-medium | fix in v0.2.1 |
| Ontology installed-wheel support | layer/packaging | real source-checkout subsystem | package YAML and use `importlib.resources`; remove repository-root dependency | **High; yes if command remains public** | small | fix in v0.2.1 or hide command |
| Legacy authority normalization | architecture/workflow | new reconciliation path is strong | align `PipelineRunner`, Scene acceptance, direct Book acceptance with explicit/atomic authority | high; no for existing narrow workflow, yes for uniform constitution | medium-large | v0.3 |
| Status correctness and guided workflow | CLI/UX | useful aggregate command | correct Identity paths, safe no-chapter behavior, valid next commands, live freshness | high user impact; not release blocker | small | v0.2.1 |
| Realization unification | layer | rich but parallel/partial | make Scene Realization the universal drafting input; unify Bible/relations/state ownership | high architecture impact; no immediate blocker | large | v0.3/v1.0 |
| Structure representation convergence | architecture/artifact | two substantial models | explicit adapter/authority relationship between StoryBlueprint and narrative outlines | medium-high | large | v0.3 |
| Schema migration framework | infrastructure | version guard only | migration registry, dry-run, backup, per-artifact versions | high long-term; not immediate | medium | v0.3 before schema changes |
| Universal provenance adoption | infrastructure | strong pilot + reconciliation stores | one policy for Identity/Structure/Series/Universe/Relations | medium-high | large | v0.3/v1.0 |
| Reasoning runtime maturity | subsystem | functional deterministic runtime/synthesis | semantic version handling, live source adapter, richer contracts/critics | medium | medium | v0.3 |
| Series/Universe lifecycle integration | workflow/scope | real functional commands | accepted revisions, provenance, project-relative dependency resolution | medium | medium-large | v1.0 |
| CLI discoverability/consistency | UX | very broad command surface | guided workflows, standardized errors, experimental labels, completion | medium-high | medium | v0.3 |
| CI/release matrix | infrastructure | Python 3.11 validation workflow | Python-version/OS matrix, coverage, wheel smoke, external EPUB validation | high risk reduction | medium | v0.2.1/v0.3 |
| Advanced markerless mapping, merge/split, grouped decisions | optional enhancement | intentionally deferred | advanced reconciliation UX | low for current product | large | v2 |
| Collaboration/database/performance | vision | non-goal/deferred | multi-user, scale, caching | low for v0.x | large | v2+

---

## 15. Separate completeness conclusions

### A. Architectural completeness

**No.** The architecture is coherent, but the five layers are not uniformly complete:

- Identity: complete.
- Structure: complete in the primary engine.
- Expression: complete for the supported workflow.
- Ontology: functional but partial and not install-safe.
- Realization: functional but partial and not universally integrated.

### B. Core product completeness

**Qualified yes.** A knowledgeable user can traverse the supported opinionated source-checkout workflow from Identity to accepted Book and publish HTML/EPUB. The product should not be considered fully release-hardened until publishing, package resources, status guidance, and current-branch hygiene are corrected.

### C. Artifact completeness

**Yes for the supported Chapter/Book workflow; no for the full architecture.** Every artifact needed by the current Expression/reconciliation/publishing path exists. Across the broader architecture, artifacts are duplicated, informal, or lack a unified lifecycle.

### D. Feature completeness

**No.** Most public commands perform real work, but public Ontology is not wheel-safe, Status has correctness gaps, Publishing violates some stated invariants, Schema migration is absent, and several experimental/parallel systems are only partially integrated.

### E. Vision completeness

**No.** Full Ontology/Realization integration, universal provenance, schema evolution, advanced author UX, collaboration, performance, and richer import/export remain future work.

---

## 16. Recommended next implementation phase

# v0.2.1 Release Integrity and Product Invariants Hardening

### Why this is highest leverage

It protects the released product, aligns claims with behavior, fixes installed-wheel failures, and improves the first user interaction without expanding architecture.

### Scope

1. Remove tracked scratch/dogfood artifacts from default branch and prevent recurrence.
2. Package Ontology data under `src/auteur/data/ontology` and load it with `importlib.resources`, or hide Ontology from installed help until fixed.
3. Harden publishing:
   - store EPUB `mimetype` first and uncompressed;
   - make deterministic output truly deterministic or narrow the claim;
   - hash raw EPUB bytes;
   - derive actual Auteur version;
   - validate accepted Book Markdown against accepted manifest before snapshot;
   - declare or vendor one Markdown implementation.
4. Fix `auteur status` schema paths, no-chapter behavior, suggested commands, and live freshness sourcing.
5. Add wheel-installed smoke tests for Ontology, Status, Publish HTML, and Publish EPUB.
6. Add CI matrix coverage for supported Python versions and at least Linux/Windows.
7. Correct documentation claims after tests prove the new behavior.

### Out of scope

- Completing Ontology semantics.
- Completing Realization integration.
- New critics or reconciliation phases.
- Collaboration or database storage.
- Major CLI redesign.

### Acceptance criteria

- Clean default branch with no generated workspaces/scratch output.
- Fresh wheel install can run `auteur --help`, `ontology list`, `status`, and HTML/EPUB publish.
- EPUB passes structural checks including uncompressed mimetype and an external validator when available.
- Repeated renders from identical semantic inputs are byte-identical if determinism remains claimed.
- Tampered accepted Book source blocks publication.
- Status never crashes on empty/partial projects and recommends valid commands.
- Full suite, wheel smoke, and CI matrix pass.

### Target

`v0.2.1` patch release.

---

## 17. Final product status

```text
Book reconciliation architecture: complete
Book reconciliation implementation: complete
Book reconciliation CLI workflow: complete
Identity and primary Structure: complete
Expression workflow: complete for supported use
Ontology: functional but partial and package-broken
Realization: functional but partial
Publishing: functional but release-hardening required
Schema migration: missing
Supported author workflow: substantially complete
All public features: not complete
Auteur product overall: useful and released, not vision-complete
```

## 18. Audit limitations

- The GitHub integration provided source, history, tests, workflow, and package configuration inspection.
- It did not provide an executable checkout in this session.
- The full suite, wheel build, fresh install, and command smoke tests were therefore not re-run.
- No workflow run was available for the inspected default-branch commit.
- Historical pass counts in changelog/reports were treated as claims, not current proof.
- No product code was modified by this audit.
