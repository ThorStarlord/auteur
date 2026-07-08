---
name: state-check
description: "Run Structure Diagnostic (Layers 1-5, 9) and Bible Audit (Layer 6) in one pass, optionally validate Scene Representation (Layer 7) against an outline."
---

# State Check Skill

Unified diagnostic pass across all structural layers. Combines within-blueprint coherence checks, carrier-state lore drift, and scene-outline consistency into a single report.

## Artifact Contract

| Direction | Path | Schema |
|---|---|---|
| **Consumes** | `blueprint.yaml`, `bible.json` in project | `StoryBlueprint` + `StoryBible` |
| **Consumes (optional)** | `outline.yaml` via `--outline` | Cartographer outline dict |
| **Produces** | `structure/diagnostics/state_report.json` | `{"diagnostics": [{severity, layer, rule, message, evidence}]}` |

## Invocation

```bash
auteur state check <project_path> [--outline <outline.yaml>]
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | No structural or lore errors found |
| `4` | One or more ERROR-severity diagnostics present |
| `1` | Project files missing or invalid |

## Layer Coverage

| Layer | Coverage | Source |
|---|---|---|
| 1-5 | Blueprint coherence | `StructureDiagnostic` |
| 6 | Carrier-state lore drift | `BibleAudit` |
| 7 | Scene representation (with `--outline`) | `OutlineAudit` |
| 9 | Thematic resonance | `StructureDiagnostic` |

When `--outline` is omitted, Layer 7 emits a WARNING noting it was skipped.

## Agent Usage

1. Ensure project has `blueprint.yaml` and `bible.json`.
2. Optionally prepare an `outline.yaml` for Layer 7 validation.
3. Run `auteur state check <project> [--outline <path>]`.
4. Read `structure/diagnostics/state_report.json` for full structured results.
5. Resolve findings by editing blueprint/bible or via proposal workflow.

## Example

```bash
auteur state check project/ --outline chapters/01/outline.yaml
# Exit: 0
# Artifact: project/structure/diagnostics/state_report.json
# Stdout: ╔═══ Story State Report ═══════════════════════════════════╗
#         ║ Project: project                         ║
#         ...
```
