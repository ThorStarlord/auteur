# PRD: Story State Manager — Unified `auteur audit` for All 9 Diagnostic Layers

## Problem Statement

Auteur currently runs diagnostic passes on two separate tracks: `auteur structure diagnose` checks blueprint coherence (Layers 1–5), and `auteur audit` checks Bible/carrier consistency (Layer 6). The author must know which command to run for which kind of problem, and the diagnostic outputs use different types (`StructureDiagnostic` vs `BibleAuditDiagnostic`) that cannot be merged into a single Decision Packet flow. This makes the system harder to reason about, harder to extend to new layers (7–9), and forces the author to manually correlate findings across commands.

## Solution

A unified `auteur audit <project>` command that:
- Resolves both `blueprint.yaml` and `bible.json` from the project directory
- Runs all active diagnostic rules across all layers in one pass
- Produces a single grouped-by-layer report
- Emits unified Decision Packets with `--repair`
- Supports layer filtering via `--layers <range>` so authors can focus on specific concerns

The separate `auteur structure diagnose` command is preserved as an alias for `auteur audit --layers 1-5`. No existing workflows break — the old command still works.

## User Stories

1. As a fiction author, I want to run one command (`auteur audit my_novel`) to see all structural and lore issues at once, so that I don't need to know which layer my problem lives in before diagnosing it.

2. As a power user, I want to filter audits to specific layers (`--layers 6` for carrier state only), so that I can focus on one kind of problem at a time without noise from other layers.

3. As a returning author, I want unresolved diagnostics from previous runs to remain visible and new diagnostics to be appended, so that I can track my progress across sessions.

4. As an author, I want each finding to show its layer label in the report, so that I understand whether a problem is in the blueprint structure, the character state, or the prose representation.

5. As an author, I want to run `auteur audit --repair` and have all error-severity findings across all layers promoted to Decision Packet YAML files, so that I can review structured options for fixing each issue.

6. As an author, I want resolved proposals (where I've already set `selected_option_id`) to be skipped in subsequent audit runs, so that I only see unresolved issues.

7. As a developer, I want `BibleAuditDiagnostic` to carry `repair_options` so that Bible-level findings can be promoted to Decision Packets through the same pipeline as structure-level findings.

8. As a developer, I want an adapter that converts `BibleAuditDiagnostic` to `StructureDiagnostic` so that the proposal generation pipeline (`propose_repairs_from_diagnostics`) can consume a single stream of diagnostics.

## Implementation Decisions

### Decision 1: CLI surface

```text
auteur audit <project>                     # all layers (default)
auteur audit <project> --layers 6          # Bible/carriers only
auteur audit <project> --layers 1-5        # structure only (backward compat)
auteur audit <project> --layers all        # explicit default
auteur audit <project> --repair            # write Decision Packets for all layers
auteur audit <project> --accept <id> --option <id>  # resolve proposal (existing)
auteur audit <project> --show              # print all proposals (existing)
```

The `--layers` flag accepts a comma-separated range or `all`. Single values (`--layers 6`) run one layer only. Dashed ranges (`--layers 1-5`) run a contiguous block. No `--layers` is equivalent to `--layers all`.

`_cmd_structure_diagnose` is preserved as-is but internally delegates to the unified audit runner with `--layers 1-5`. No callers break.

### Decision 2: Type bridge

`BibleAuditDiagnostic` gains a `repair_options: RepairOptions` field (defaulting to `RepairOptions()` with empty lists) so it carries the same data as `StructureDiagnostic`.

An adapter function converts `BibleAuditDiagnostic` → `StructureDiagnostic`:

```python
def as_structure_diagnostic(bible_diag: BibleAuditDiagnostic) -> StructureDiagnostic:
    return StructureDiagnostic(
        severity=bible_diag.severity,
        layer=DiagnosticLayer.CARRIERS,
        rule=bible_diag.rule,
        evidence=bible_diag.evidence,
        repair_options=bible_diag.repair_options or RepairOptions(),
        affected_blueprint_fields=[],
    )
```

This is a pure function with no side effects. It lives in `structure/bible_audit.py` alongside the audit logic.

### Decision 3: Unified runner

A new function `run_all_diagnostics(project: Project) -> list[StructureDiagnostic]` orchestrates both passes:

```
1. blueprint project.blueprint
2. bible project.bible
3. diagnostics = []
4. diagnostics += analyze_structure(blueprint)        # structure analyzer
5. bible_findings = audit_bible_locations(bible)       # Bible audit
6. diagnostics += [as_structure_diagnostic(f) for f in bible_findings]
7. diagnostics += ...future layer diagnostics...
8. return diagnostics
```

This function lives in `structure/analyzer.py` (or a new `structure/engine.py` — open to naming). The CLI calls this once, then passes the combined list to `propose_repairs_from_diagnostics()` when `--repair` is set.

### Decision 4: Layer filtering

The `--layers` flag is parsed and converted to a set of `DiagnosticLayer` enum values. After `run_all_diagnostics()` returns, the list is filtered to keep only diagnostics whose `.layer` is in the requested set. Filtering happens in the CLI layer, not the runner — the runner always runs everything; the CLI decides what to show.

### Decision 5: Report format

```
$ auteur audit my_novel

╔═══ Story State Report ═══════════════════════════════════╗
║ Project: my_novel                                       ║
║ Layers: 1-5, 6                                          ║
╚══════════════════════════════════════════════════════════╝

Layer 2 — Genre (1 finding)
  ERROR: Mixed genre signals — romance plot opens, but opening
         scene is thriller pacing. Add genre-establishing beats.

Layer 6 — Carriers (2 findings)
  ERROR: Location teleportation — Aldric moves from Throne Room
         to Dungeon with no intermediate event.
  WARNING: Emotional state gap — Kael's grief in chapter 5 is
           inconsistent with his relief in chapter 3.

3 findings total. Run with --repair to write Decision Packets.
```

Resolved proposals (where `selection.selected_option_id` is set) are not listed in findings. The report footer shows the count of skipped resolved proposals if any exist.

## Testing Decisions

### Testing philosophy

Tests verify behavior through public interfaces, not implementation details. A good test describes _what_ the system does — "unified audit produces a combined diagnostic list from both blueprint and Bible sources" — not _how_ it merges the two lists.

### Test modules

1. **`tests/test_structure_analyzer.py`** — Add tests for `run_all_diagnostics()` (the unified runner). Create a project fixture with both a blueprint (with a known structural gap) and a Bible (with a known carrier inconsistency), then assert both diagnostic types appear in the output.

2. **`tests/test_bible_audit.py`** — Add test for the `repair_options` field on `BibleAuditDiagnostic`. Verify default empty state.

3. **`tests/test_cli.py`** — Add tests for the `--layers` flag parsing and filtering behavior. Verify that `--layers 6` only returns carrier-layer diagnostics.

### Prior art

- `test_bible_audit.py::test_detects_location_teleportation_between_consecutive_events` — demonstrates the existing Bible audit unit test pattern with a constructed `StoryBible`.
- `test_proposal_accept_apply.py` — demonstrates the Decision Packet write/resolve flow.
- `test_critic_contract.py` — demonstrates the `FakeClient` pattern for LLM-free testing.

## Out of Scope

- **Critic Proposal unification** (Layer 7): The critic findings → Decision Packet pipeline was wired in a recent session but is not part of this PRD. Critic proposals live in `structure/proposals/critic_*.yaml` and are handled separately.
- **Per-agent model routing**: Still a known gap, tracked separately.
- **Interactive proposal resolution TUI**: Resolution remains YAML-editing or CLI `--accept` flags.
- **New Bible diagnostic rules**: Only the existing location-teleportation rule is carried forward. New rules (emotional state drift, relationship state drift) are future work.

## Further Notes

### Module impact matrix

| Module | Change |
|---|---|
| `src/auteur/structure/bible_audit.py` | Add `repair_options: RepairOptions` to `BibleAuditDiagnostic`; add `as_structure_diagnostic()` adapter |
| `src/auteur/structure/diagnostics.py` | No change (`StructureDiagnostic` is the target type) |
| `src/auteur/structure/analyzer.py` | Add `run_all_diagnostics(project)` orchestrator |
| `src/auteur/cli.py` | Add `--layers` flag to `_cmd_audit`; delegate `_cmd_structure_diagnose` to unified runner |
| `src/auteur/project.py` | No change (already exposes `.blueprint` and `.bible`) |

### Sequence (first vertical slice)

```
RED:   test_cli_unified_audit_merges_both_diagnostic_sources
GREEN: as_structure_diagnostic() + run_all_diagnostics() + CLI wiring + --layers
```

This tracer bullet proves the path exists. Subsequent slices add `--layers` filtering, the grouped report format, and resolved-proposal skipping.
