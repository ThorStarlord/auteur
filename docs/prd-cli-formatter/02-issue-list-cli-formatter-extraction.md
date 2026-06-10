# Issue List: CLI Formatter/Serializer Extraction

## 1. PRD Consumed

- **PRD**: `docs/prd-cli-formatter/01-prd-cli-formatter-extraction.md`
- **Intents**: `docs/prd-cli-formatter/00-user-intent.md`
- **user_goal_preserved_as**: `core_with_expansion`
- **scope_expansion_proposed**: true
- **scope_expansion_status**: `pending_user_approval`

## 2. Scope Status

**Core + Expansion (expansions pending)**

Issues generated for **core features only** (F1-F4: handler extraction, formatter layer, serializer layer, thin dispatch CLI). The two proposed expansions (E1: structure analyzer rule registry, E2: shared test fixtures) remain `pending_user_approval` and are not included in this issue list.

## 3. Issues Generated

### Story 1: Define Handler Interface and Result Types

**ID**: TASK-001
**Type**: Tech Debt
**Title**: Define handler interface and result types

**Acceptance Criteria**:
- `src/auteur/cli_handlers.py` created with a handler protocol or abstract base class
- `CommandResult` dataclass defined with `success: bool`, `data: Any`, and per-command typed result variants
- `CommandError` or error variant defined with `message: str`, `exit_code: int`, optional `details: dict`
- All result types are serializable (JSON/YAML dumpable) for the serializer layer
- Module is importable without side effects — no module-level I/O, no argparse imports

**Effort**: 1 day
**Priority**: P0 (unblocks all handler migration)
**Dependencies**: None

---

### Story 2: Migrate Structure Command Handlers

**ID**: TASK-002
**Type**: Tech Debt
**Title**: Migrate structure command handlers (diagnose, propose-repairs, apply, generate)

**Acceptance Criteria**:
- `handle_structure_diagnose(blueprint: StoryBlueprint, output: Path | None) -> CommandResult` exists and returns structured diagnostic data (not printed text)
- `handle_structure_propose_repairs(blueprint: StoryBlueprint) -> CommandResult` exists
- `handle_structure_apply(proposal: StructureProposal, blueprint: StoryBlueprint, ...) -> CommandResult` exists
- `handle_structure_generate(blueprint: StoryBlueprint, symptom: str | None, ...) -> CommandResult` exists
- Zero `print()` calls or filesystem writes in any handler — pure orchestration only
- All handlers accept typed domain objects (not argparse Namespace)
- All handler logic matches existing `_cmd_structure_*` behavior (verified by running existing tests)

**Effort**: 2 days
**Priority**: P0
**Dependencies**: TASK-001 (needs CommandResult types)

---

### Story 3: Migrate Identity and Project Command Handlers

**ID**: TASK-003
**Type**: Tech Debt
**Title**: Migrate identity and project command handlers (validate, compile, recommend, promote, init, blueprint seed, cartographer)

**Acceptance Criteria**:
- `handle_identity_validate(identity: StoryIdentity) -> CommandResult` exists
- `handle_identity_compile(identity: StoryIdentity, output: Path) -> CommandResult` exists
- `handle_identity_recommend(premise: str, genre: str | None, medium: str | None, ...) -> CommandResult` exists
- `handle_identity_promote(candidate_path: Path, output_path: Path) -> CommandResult` exists
- `handle_init(path: Path, blueprint: StoryBlueprint, force: bool) -> CommandResult` exists
- `handle_blueprint_seed(identity: StoryIdentity, output: Path) -> CommandResult` exists
- `handle_cartographer_compile(blueprint: StoryBlueprint, output: Path) -> CommandResult` exists
- `handle_cartographer_validate(outline_path: Path, blueprint_path: Path) -> CommandResult` exists
- Zero `print()` calls or filesystem writes in any handler
- LLM recommendation logic (identity recommend) delegates to LLM client but handler returns structured result, not printed output
- Existing `_cmd_identity_recommend` validation-feedback and retry loop logic is preserved

**Effort**: 2 days
**Priority**: P0
**Dependencies**: TASK-001

---

### Story 4: Migrate Draft/Accept/Retry/Audit/State Command Handlers

**ID**: TASK-004
**Type**: Tech Debt
**Title**: Migrate draft/accept/retry/audit/state handlers

**Acceptance Criteria**:
- `handle_draft(project: Project, chapter: int, max_iterations: int, ...) -> DraftResult` exists
- `handle_accept(project: Project, chapter: int) -> CommandResult` exists
- `handle_retry(project: Project, chapter: int, max_iterations: int, ...) -> CommandResult` exists
- `handle_audit(project: Project, repair: bool, accept: str | None, option: str | None, layers: str) -> CommandResult` exists
- `handle_state_check(project: Project, outline: dict | None) -> CommandResult` exists
- `handle_state_update(...)`, `handle_state_prepare(...)`, `handle_state_canon(...)`, `handle_state_confirm(...)` exist
- Zero `print()` calls or filesystem writes in any handler
- Draft iteration loop, LLM retry logic, critic fan-out, and bible update logic are preserved
- Conflict report handling and iteration status tracking return structured data, not printed lines

**Effort**: 3 days (most complex — draft/retry have iteration loops, retry needs to load previous state)
**Priority**: P0
**Dependencies**: TASK-001

---

### Story 5: Create Formatter and Serializer Layers

**ID**: TASK-005
**Type**: Tech Debt
**Title**: Create formatter and serializer layers

**Acceptance Criteria**:
- `src/auteur/cli_formatters.py` created
- One `format_<command>(result: CommandResult) -> str | None` per command
- Formatters own ALL `print()` calls — they are the only module that prints to stdout/stderr
- Error messages centralized — a single `format_error(message, exit_code)` replaces 25+ copies of `print(f"Error: ...", file=sys.stderr)`
- Human-readable summaries (diagnostic counts, iteration status, token usage) are formatted here
- `src/auteur/cli_serializers.py` created
- One `serialize_<command>(result, output_path) -> Path` per command that writes artifacts
- Serializers own ALL `path.write_text()`, `yaml.dump()`, `json.dump()` calls
- Serializers can be called from an agent context without invoking the CLI — they take a result + output path and produce the file
- Both modules are importable without side effects
- No module exceeds 500 lines (split into subdirectories if needed, e.g., `cli_formatters/structure.py`)

**Effort**: 2 days
**Priority**: P0
**Dependencies**: TASK-002, TASK-003, TASK-004 (needs handlers to exist to write formatters/serializers for them)

---

### Story 6: Rewrite cli.py as Thin Dispatch

**ID**: TASK-006
**Type**: Tech Debt
**Title**: Rewrite cli.py as thin dispatch layer

**Acceptance Criteria**:
- `cli.py` reduced to ≤300 lines (argument parser definitions + dispatch wiring only)
- Every command is wired as: `result = handler(args); serializer(result, output_path); output = formatter(result); if output: print(output)`
- Zero domain logic lives in `cli.py` — it only imports and dispatches
- Error handling unified through a `_run_command(handler_fn, ...)` wrapper that catches structured failures from handlers
- Existing `_cmd_*` functions are deleted — no dead code remains
- All three layers (handler, serializer, formatter) are importable and testable in isolation
- Every existing CLI command produces identical stdout/stderr output (verified by running the full test suite)
- Every existing CLI command writes identical artifact files as before
- All existing tests pass without modification
- No public CLI interface changes (no renamed flags, no removed subcommands, no changed argument defaults)
- No internal `_cmd_*` functions remain importable from the module

**Effort**: 1 day
**Priority**: P0
**Dependencies**: TASK-005 (needs formatters and serializers to exist before wiring)

## 4. Release Scope

| Metric | Value |
|---|---|
| **Total issues** | 6 |
| **Core issues** | 6 |
| **Expansion issues** | 0 (pending approval) |
| **Feature type** | 0 |
| **Tech Debt type** | 6 |
| **Bug type** | 0 |
| **Total effort (core)** | 11 days |
| **Total effort (expansions)** | 2.5-3.5 days (if approved) |
| **Estimated timeline** | 2-3 weeks (single developer) |

## 5. Phasing Strategy

### Phase 1 (MVP): Core Features

| Issue | Effort | Priority |
|---|---|---|
| TASK-001: Handler interface + result types | 1 day | P0 |
| TASK-002: Structure command handlers | 2 days | P0 |
| TASK-003: Identity/project command handlers | 2 days | P0 |
| TASK-004: Draft/accept/retry/audit/state handlers | 3 days | P0 |
| TASK-005: Formatter + serializer layers | 2 days | P0 |
| TASK-006: Thin dispatch CLI | 1 day | P0 |
| **Phase 1 total** | **11 days** | |

**Execution order**: TASK-001 → TASK-002 + TASK-003 + TASK-004 (parallelizable) → TASK-005 → TASK-006

### Phase 2 (If Expansions Approved)

| Issue | Effort | Priority |
|---|---|---|
| E1: Structure analyzer rule registry | 2-3 days | P1 |
| E2: Shared test fixtures / conftest.py | 0.5 days | P2 |
| **Phase 2 total** | **2.5-3.5 days** | |

## 6. Out of Scope

- **Structure analyzer decomposition** (E1 — expansion, pending approval): Not included in issues. Would be a separate phase if approved.
- **Shared test fixtures / conftest.py** (E2 — expansion, pending approval): Not included.
- **CLI argument parser changes**: No flag renames, no subcommand restructuring.
- **Domain module refactoring**: `blueprint.py`, `identity.py`, `structure/` modules are NOT being decomposed.
- **LLM adapter changes**: No changes to `src/auteur/llm/`.
- **New test coverage**: Adding tests for untested code paths is encouraged but not required.
- **User-facing documentation**: Writing new docs is out of scope.

## 7. Testing Plan

**Strategy**: Zero behavioral change — the test suite is the ground truth.

| Layer | Test approach |
|---|---|
| **Handlers** | New unit tests import handler functions directly, pass typed inputs, assert on structured `CommandResult` objects. No mocking needed beyond existing FakeClient. |
| **Formatters** | Unit tests pass a `CommandResult` to `format_<command>()`, assert on returned string content. |
| **Serializers** | Unit tests pass a `CommandResult` + `tmp_path` to `serialize_<command>()`, assert on written file contents. |
| **CLI integration** | Existing tests call `main()` with `capsys` / `tmp_path` — unchanged. Verify output parity. |
| **Full regression** | `python scripts/check.py` must pass identically before and after. |

**Critical verification step** (TASK-006 completion gate): Run the full test suite (`python -m pytest`) and `python scripts/check.py` before TASK-006 can be marked done. Any test that broke due to internal import changes (e.g., importing a `_cmd_*` function that no longer exists) must be updated, but the test's observable assertions must remain valid.

## 8. Machine-Readable Handoff

```yaml
artifact_id: issue_list
schema_version: 1
source_intent_ref: ../../docs/prd-cli-formatter/00-user-intent.md
user_goal_preserved_as: core_with_expansion
scope_expansion_proposed: true
scope_expansion_status: pending_user_approval
issues_generated: 6
core_issues_count: 6
expansion_issues_count: 0
escalation_required: false
escalation_reason: null
issues:
  - id: TASK-001
    title: Define handler interface and result types
    type: Tech Debt
    effort_days: 1
    priority: P0
    scope: core
    dependencies: []
  - id: TASK-002
    title: Migrate structure command handlers
    type: Tech Debt
    effort_days: 2
    priority: P0
    scope: core
    dependencies: [TASK-001]
  - id: TASK-003
    title: Migrate identity and project command handlers
    type: Tech Debt
    effort_days: 2
    priority: P0
    scope: core
    dependencies: [TASK-001]
  - id: TASK-004
    title: Migrate draft/accept/retry/audit/state handlers
    type: Tech Debt
    effort_days: 3
    priority: P0
    scope: core
    dependencies: [TASK-001]
  - id: TASK-005
    title: Create formatter and serializer layers
    type: Tech Debt
    effort_days: 2
    priority: P0
    scope: core
    dependencies: [TASK-002, TASK-003, TASK-004]
  - id: TASK-006
    title: Rewrite cli.py as thin dispatch layer
    type: Tech Debt
    effort_days: 1
    priority: P0
    scope: core
    dependencies: [TASK-005]
created_at: 2026-06-10
```

## Next Steps

1. **User to approve/reject expansions** (E1, E2) from the PRD approval gate
2. **Triage** — If expansions approved, add E1/E2 to this issue list at P1/P2
3. **TDD** — Begin with TASK-001 (handler interface definition), writing tests first
