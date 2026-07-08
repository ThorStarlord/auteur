---
name: structure-diagnose
description: "Run deterministic whole-story structure diagnostics on a blueprint.yaml and read the results from the artifact."
---

# Structure Diagnose Skill

Runs deterministic coherence/completeness checks across blueprint layers 1-5 and 9. Does not call an LLM. Does not mutate the blueprint.

## Artifact Contract

| Direction | Path | Schema |
|---|---|---|
| **Consumes** | `blueprint.yaml` | `StoryBlueprint` Pydantic model |
| **Produces** | `structure/diagnostics/structure_report.json` | `{"diagnostics": [{severity, layer, rule, message, evidence, repair_options}]}` |

The artifact is always written to `structure/diagnostics/structure_report.json` relative to the blueprint. Use `--output <path>` to override.

## Invocation

```bash
auteur structure diagnose <blueprint.yaml> [--output <path>]
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | No errors (warnings/info may exist) |
| `4` | One or more ERROR-severity diagnostics found |
| `1` | Blueprint file not found or invalid YAML |

## Diagnostic Severity

| Severity | Meaning |
|---|---|
| `error` | Must be resolved before drafting |
| `warning` | Should be reviewed, may indicate risk |
| `info` | Advisory observation, no action required |

## Agent Usage

1. Write or confirm `blueprint.yaml` exists.
2. Run `auteur structure diagnose blueprint.yaml`.
3. Read `structure/diagnostics/structure_report.json`.
4. If exit code is `4`, iterate on the blueprint and re-run.
5. If exit code is `0`, the blueprint is structurally coherent.

## Example

```bash
auteur structure diagnose project/blueprint.yaml
# Exit: 0
# Artifact: project/structure/diagnostics/structure_report.json
# Stdout: [WARNING] structure.subplot_budget.missing: ...
#         3 total: 0 error(s), 2 warning(s), 1 info
```
