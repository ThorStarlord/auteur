# Product Requirements Document: CLI Formatter/Serializer Extraction

## 1. Executive Summary

Extract a three-layer architecture from the current CLI monolith (`src/auteur/cli.py`, 1812 lines) that separates argument dispatch → domain orchestration → output formatting. This reconciles Auteur's documented "core separation" architecture (which declares domain logic should return structured objects that a formatter renders and a serializer persists) with the current implementation (where all three concerns are interleaved with inline `print()` calls on ~140 lines).

The result is a thin dispatch CLI (~200-300 lines), pure handler functions (one per command, returning structured result objects), and a formatter/serializer layer that makes the artifact-based agentic API first-class instead of a secondary output channel.

## 2. User Goal (As Stated)

> "Analyze my current project and propose a P0 task to improve the code structure."

The user asked for the single highest-impact code structure improvement. The architecture analysis identified the CLI monolith as the P0 candidate. This PRD formalizes the scope, acceptance criteria, and boundaries for that work.

## 3. Goal Preservation & Expansion

**user_goal_preserved_as**: core_with_expansion

The core deliverable is the CLI formatter/serializer extraction — the P0 task the user asked for.

Two expansion features are proposed based on discovery: decomposing the structure analyzer monolith and introducing shared test fixtures. These are adjacent improvements that share the same engineering rhythm (extract seams, improve testability, deepen modules) and naturally follow from the same architecture analysis.

**scope_expansion_proposed**: true
**scope_expansion_requires_approval**: true
**scope_expansion_status**: pending_user_approval

## 4. Features

### Core Features (Goal-Preserving)

#### F1: Handler Extraction — Separate Domain Orchestration from Argument Parsing

Extract every `_cmd_*` function in `cli.py` into standalone handler functions that accept only domain objects (not argparse Namespace) and return structured result objects.

**What changes**:
- New file `src/auteur/cli_handlers.py` (or per-domain handler modules)
- Each handler is a pure function: `(domain_inputs) -> CommandResult` — no `print()`, no filesystem side effects, no argparse dependency
- Handler receives pre-parsed, validated inputs (Path, int, enum, etc.) — no `args.blueprint` stringly-typed access
- Error cases return structured `CommandResult.failure(...)` instead of `print(file=sys.stderr); return 1`

**Does NOT change**:
- Domain logic in `blueprint.py`, `identity.py`, `structure/`, etc. — handlers call existing APIs, they don't rewrite them
- CLI's public interface (flags, subcommand names, argument names) — no breaking changes

**Key requirements**:
- Every existing `_cmd_*` must have a corresponding handler
- Handler return types are lightweight dataclasses or TypedDicts — not Pydantic unless reuse justifies it
- Handlers do NOT open files — they accept already-loaded data (`StoryBlueprint`, `StoryBible`, etc.)
- Handlers do NOT define argparse parsers

#### F2: Formatter Layer — Separate stdout Rendering from Computation

Extract every `print()` call in `cli.py` into named formatter functions that take handler result objects and return/formatted text strings.

**What changes**:
- New file `src/auteur/cli_formatters.py`
- One `format_<command>(result: CommandResult) -> str | None` per command
- Formatters own all `print()` calls — they are the ONLY module that calls `print()`
- Formatters handle both stdout (human-readable) and stderr (errors/warnings) output formatting
- Color, indentation, and layout logic lives here — nowhere else

**Key requirements**:
- Zero `print()` calls remain in `cli.py` after extraction
- Formatters are stateless — pure `(result) -> str` functions
- Error message formatting is centralized (no more 25 copies of `print(f"Error: ...", file=sys.stderr)`)

#### F3: Serializer Layer — Make Artifact Writing First-Class

Extract artifact/side-effect writing into a serializer layer that writes structured output (JSON reports, YAML proposals, audit reports) to deterministic paths.

**What changes**:
- New file `src/auteur/cli_serializers.py`
- One `serialize_<command>(result, output_path)` per command that produces artifacts
- Serializers own all filesystem writes — they are the ONLY module that calls `path.write_text()` / `yaml.dump()` / `json.dump()`

**Key requirements**:
- Serializers are the agent-facing API — agents can call `serialize_<command>(result)` to produce standard artifact files without invoking the CLI
- Every command that writes artifact files today must have a serializer
- Serializers do NOT format human-readable text and do NOT print to stdout

#### F4: Thin Dispatch CLI — Wire the Three Layers Together

Replace the current `_cmd_*` functions in `cli.py` with thin dispatch that: parse args → validate → call handler → call serializer → call formatter.

**What changes**:
- `cli.py` is reduced to argument parser definitions + a dispatch table mapping command to (handler, serializer, formatter) triple
- Each command's code path is ~5-10 lines: `result = handler(args); serializer(result, output_path); output = formatter(result); if output: print(output)`
- Error handling is unified through a `_run_command(handler_fn, ...)` wrapper that catches structured failures and delegates to the error formatter

**Key requirements**:
- `cli.py` target: ~200-300 lines (down from 1812)
- Zero domain logic in cli.py — it imports and dispatches, never computes
- All three layers (handler, serializer, formatter) are independently testable

### Expansion Features (Proposed, Requires Approval)

#### E1: Structure Analyzer Rule Registry

**Rationale**: The structure analyzer (`src/auteur/structure/analyzer.py`, 1647 lines) has ~41 diagnostic rules as sequential if-blocks with no registry, no plugin mechanism, and no code-enforced rule naming convention. The same extraction pattern (monolith → thin dispatch + registered modules) applies.

**What changes**:
- Introduce a rule registry (`RULE_REGISTRY: list[Rule]`) that rules register into via a decorator or explicit registration
- `analyze_structure()` becomes a loop over registered rules instead of 41 sequential if-blocks
- Each rule becomes an isolated function/module with its own test file
- Rule naming (`genre.forbidden_mismatch.ending_tone`) is enforced by the registry, not convention

**Effort estimate**: Medium (2-3 days) — less than CLI extraction but non-trivial because rules share state and ordering may matter.

**Risk assessment**: Low — rules are already pure functions returning lists of `StructureDiagnostic`. The extraction is mechanical. Main risk is missing an ordering dependency that was implicit in the if-block sequence.

**Status**: REQUIRES USER APPROVAL

#### E2: Shared Test Fixtures and conftest.py

**Rationale**: No `conftest.py` exists. ~10 copies of `SAMPLE_YAML = Path(...)` and similar fixture code are duplicated across test files. This violates DRY and makes adding new tests more work than it should be.

**What changes**:
- Create `tests/conftest.py` with shared fixture functions: `sample_blueprint()`, `sample_identity()`, `tmp_project(tmp_path)`, etc.
- Replace inline fixture definitions across all test files with imports from conftest
- Deduplicate the SAMPLE_YAML path definitions

**Effort estimate**: Low (half a day) — mechanical work, no behavioral change.

**Risk assessment**: Minimal — test fixtures are pure data. Main risk is a fixture change breaking tests in unexpected files, mitigated by running the full suite after changes.

**Status**: REQUIRES USER APPROVAL

## 5. Out of Scope

- **CLI argument parser restyling**: The argparse definitions themselves stay in `cli.py`. Only the command handler bodies move. No flag renames, no subcommand restructuring.
- **Domain logic refactoring**: The `blueprint.py`, `identity.py`, `structure/` modules are NOT being decomposed as part of this PRD. They are called through their existing APIs. Only the CLI wiring changes.
- **LLM adapter changes**: No changes to `src/auteur/llm/`.
- **Test coverage expansion**: Existing tests must keep passing. Adding new tests for untested code paths is encouraged but not required for completion.
- **Documentation updates**: Updating architecture diagrams or CONTEXT.md is in scope; writing new user-facing docs is not.

## 6. Acceptance Criteria

### Core Features (Must-Have)

- [ ] F1: Every `_cmd_*` function in `cli.py` has a corresponding handler function in `cli_handlers.py`
- [ ] F1: Every handler accepts only typed domain objects (not argparse Namespace) and returns a structured result object (dataclass/TypedDict)
- [ ] F1: Zero `print()` calls or filesystem writes live in any handler
- [ ] F2: Zero `print()` calls remain in `cli.py` — all output is delegated to formatters
- [ ] F2: Error message formatting is centralized — no duplicate `print(f"Error: ...", file=sys.stderr)` patterns
- [ ] F3: Every command that writes artifacts today has a serializer function in `cli_serializers.py`
- [ ] F3: Serializers are the only code that calls `path.write_text()`, `yaml.dump()`, or `json.dump()`
- [ ] F3: Serializers can be called directly from an agent context (no CLI invocation required) to produce standard artifact files
- [ ] F4: `cli.py` is reduced to ≤300 lines (argument parser definitions + dispatch wiring only)
- [ ] F4: Zero domain logic lives in `cli.py` — it only imports and dispatches
- [ ] F4: All three layers (handler, serializer, formatter) are importable and testable in isolation
- [ ] F4: Every existing CLI command produces identical stdout/stderr output as before (verified by running the test suite)
- [ ] F4: Every existing CLI command writes identical artifact files as before
- [ ] All existing tests pass without modification
- [ ] No public CLI interface changes (no renamed flags, no removed subcommands, no changed argument defaults)

### Expansion Features (If Approved)

- [ ] E1: Every rule in `analyze_structure()` is extracted into a registered rule module
- [ ] E1: Registry enforces the dotted rule naming convention at registration time
- [ ] E1: `analyze_structure()` delegates to the registry (no sequential if-blocks for rule dispatch)
- [ ] E1: All existing diagnostics output is identical to pre-refactor output
- [ ] E1: All existing structure analyzer tests pass without modification
- [ ] E2: `tests/conftest.py` exists with shared fixture functions
- [ ] E2: No duplicated `SAMPLE_YAML = Path(...)` or equivalent fixture code remains across test files
- [ ] E2: All existing tests pass without modification

## 7. Non-Functional Requirements

- **Test parity**: Zero behavioral changes. The test suite is the ground truth — every test must pass with zero modifications after the refactor. If a test relied on internal CLI structure (e.g., importing a private `_cmd_*` function), that import path may need updating, but the test's observable assertions must remain valid.
- **No public API breakage**: The CLI's stdout/stderr output for every command must be byte-identical (where non-volatile) or semantically identical (where output contains timestamps/paths). Artifact file output must be byte-identical.
- **Importability**: Every new module (`cli_handlers`, `cli_formatters`, `cli_serializers`) must be importable without side effects. No module-level I/O, no argparse parsing at import time.
- **Module size**: No single new file should exceed 500 lines. If a concern is large enough to warrant more, it should be split into sub-modules (e.g., `cli_formatters/diagnose.py`).
- **Python 3.11+**: Must work on Python 3.11+ (project's existing floor). No dependencies beyond the project's existing `pyproject.toml`.

## 8. Approval Gate

[APPROVAL REQUIRED]

Two expansions were identified beyond the core CLI formatter extraction:

1. **Structure Analyzer Rule Registry** (medium effort, low risk)
   - Extract ~41 inline rules into a registered plugin system
   - Effort: 2-3 days
   - Risk: Low — rules are already pure functions
   - Accept: YES / NO

2. **Shared Test Fixtures / conftest.py** (low effort, minimal risk)
   - Create `tests/conftest.py` to eliminate ~10 copies of duplicate fixture code
   - Effort: Half a day
   - Risk: Minimal — purely mechanical deduplication
   - Accept: YES / NO

## 9. Machine-Readable Handoff

```yaml
artifact_id: prd
schema_version: 1
source_intent_ref: ../../docs/prd-cli-formatter/00-user-intent.md
user_goal_preserved_as: core_with_expansion
scope_expansion_proposed: true
scope_expansion_requires_approval: true
scope_expansion_status: pending_user_approval
created_at: 2026-06-10

scope_expansion_details:
  - feature: Structure Analyzer Rule Registry
    rationale: The analyzer.py monolith (1647 lines, ~41 rules as sequential if-blocks) is the second-largest structural debt. Same extraction pattern as CLI core — monolith to thin dispatch with registered modules.
    effort_days: 2-3
    risk: Low. Rules already return pure StructureDiagnostic lists. Main risk is implicit ordering dependencies between sequential if-blocks.
    status: pending_user_approval
  - feature: Shared Test Fixtures / conftest.py
    rationale: No conftest.py exists. ~10 copies of SAMPLE_YAML = Path(...) across test files. Violates DRY and adds friction to writing new tests.
    effort_days: 0.5
    risk: Minimal. Purely mechanical deduplication of data fixtures.
    status: pending_user_approval

scope_expansion_approvals: []
```

## Next Steps

1. User approves/rejects expansion features in the Approval Gate.
2. After approval: convert features into issue stories via `to-issues` skill.
3. Begin TDD implementation of core features (F1-F4) first, then approved expansions (E1, E2).
