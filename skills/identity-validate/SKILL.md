---
name: identity-validate
description: "Validate a story_identity.yaml against all contract rules — genre constraints, mode compatibility, central engine completeness."
---

# Identity Validate Skill

Runs deterministic validation on a `StoryIdentity` YAML file. Checks genre-endorsed modes, forbidden mismatches, central engine completeness (want != change), target experience vs ending tone, and subgenre consistency.

## Artifact Contract

| Direction | Path | Schema |
|---|---|---|
| **Consumes** | `story_identity.yaml` | `StoryIdentity` Pydantic model |
| **Produces** | `identity/validation_report.json` | `{"diagnostics": [{severity, layer, rule, message, evidence}]}` |

The artifact is always written to `identity/validation_report.json` next to the identity file.

## Invocation

```bash
auteur identity validate <story_identity.yaml>
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Identity is valid (warnings may exist) |
| `1` | Identity has ERROR-severity diagnostics or file is missing/invalid |

## Validation Rules

| Rule | Severity | Description |
|---|---|---|
| `genre.mode_compatibility` | ERROR | Chosen mode conflicts with genre contract |
| `genre.forbidden_mismatch.ending_tone` | ERROR | Ending tone is forbidden by genre contract |
| `main_thread.change_duplicates_want` | ERROR | change field repeats want instead of describing transformation |
| `target_experience.ending_tone_avoided` | ERROR | Ending tone appears in target_experience.avoid |
| `subgenre.unknown` | WARNING | Subgenre identifier not found in registry |
| `central_engine.missing_change` | WARNING | change field is empty or generic |

## Agent Usage

1. Write or receive a `story_identity.yaml`.
2. Run `auteur identity validate story_identity.yaml`.
3. Read `identity/validation_report.json` for structured diagnostics.
4. If exit code is `1`, fix the identity and re-validate before compiling to blueprint.

## Example

```bash
auteur identity validate story_identity.yaml
# Exit: 0
# Artifact: identity/validation_report.json
# Stdout: Success: StoryIdentity story_identity.yaml is valid (with warnings).
#         Validation report written to identity/validation_report.json
```
