---
name: audit
description: "Run Bible Audit diagnostics to detect carrier-state lore drift across drafted chapters (Layer 6)."
---

# Audit Skill

Detects Narrative Drift between the StoryBible event log and current carrier state — location teleportation, missing transitions, and other carrier-state inconsistencies across already-accepted chapters.

## Artifact Contract

| Direction | Path | Schema |
|---|---|---|
| **Consumes** | `blueprint.yaml`, `bible.json` in project | `StoryBlueprint` + `StoryBible` |
| **Produces** | `structure/diagnostics/audit_report.json` | `{"diagnostics": [{severity, layer, rule, message, evidence}]}` |

## Invocation

```bash
auteur audit <project_path> [--repair] [--layers <range>]
auteur audit --accept <proposal_id> --option <option_id> <project_path>
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | No unresolved errors found |
| `1` | One or more unresolved ERROR diagnostics present |

## Subcommands

| Flag | Purpose |
|---|---|
| *(none)* | Run audit, print human-readable report, write artifact |
| `--repair` | Also write `StructureProposal` YAML files to `structure/proposals/` |
| `--accept <id> --option <id>` | Resolve a specific proposal by selecting an option |
| `--layers <range>` | Filter output to specific layers (e.g. `"6"`, `"1-5"`, default `"all"`) |

## Artifact Format

The artifact `structure/diagnostics/audit_report.json` contains all unresolved diagnostics with full detail — severity, layer, rule, message, and evidence. It is always written, regardless of the `--repair` flag.

Proposal artifacts (written only with `--repair`) live in `structure/proposals/` as individual `StructureProposal` YAML files, one per diagnostic rule.

## Agent Usage

1. Ensure the project directory has `blueprint.yaml` and `bible.json`.
2. Run `auteur audit <project>`.
3. Read `structure/diagnostics/audit_report.json` for structured findings.
4. If lore drift is found, optionally run `auteur audit --repair <project>` to generate proposal artifacts.
5. Resolve proposals individually via `auteur audit --accept <id> --option <id> <project>`.
6. Re-run audit to confirm the resolution is filtered out.

## Example

```bash
auteur audit project/ --repair
# Exit: 1
# Artifact: project/structure/diagnostics/audit_report.json
# Stdout: Layer 6 — Carriers (1 finding)
#         [ERROR] carriers.location_teleportation: ...
#         Found 1 unresolved error(s), 0 unresolved warning(s).
# Proposals written to project/structure/proposals/
```
