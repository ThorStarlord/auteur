# ADR 001: Structure Proposal Artifact Format

## Status

Accepted

## Context

As defined in `docs/structure-engine-v1.md`, Auteur must treat structural choices as authorial. Instead of silently mutating the `StoryBlueprint`, Auteur should generate proposals that a human author can review, edit, and accept.

We need a format that:
1.  Is human-readable and easy to edit (YAML).
2.  Can present multiple distinct options for resolving a diagnostic error or generating a new structure.
3.  Explains the tradeoffs for each option.
4.  Contains the necessary data to update the blueprint if the option is selected.
5.  Provides a clear way for the author to record their choice.

## Decision

We will use a "Proposal and Selection" YAML format.

### Schema

```yaml
proposal_id: string
type: "generation" | "repair"
source_rule: string (optional, the diagnostic rule that triggered this)
summary: string

options:
  - id: string
    summary: string
    tradeoffs: string
    data:
      # A partial dictionary matching the StoryBlueprint structure.
      # Fields here will be merged into the existing blueprint.
      story_engine: ...
      identity: ...

selection:
  selected_option_id: string (empty by default)
  custom_data: {} (optional, for manual author overrides)
```

### Workflow

1.  **Generate**: Auteur runs an analyzer or generator and writes one or more proposal files to `structure/proposals/*.yaml`.
2.  **Review**: The author reviews the options and their tradeoffs.
3.  **Select**: The author sets `selected_option_id` to the ID of their chosen option.
4.  **Apply**: The author runs `auteur structure apply <path-to-proposal>`. Auteur reads the proposal, merges the data from the selected option (and any `custom_data`) into the project blueprint, and saves the updated blueprint.

## Consequences

- **Explicit Author Choice**: No changes happen to the core story spine without an explicit author action.
- **Traceability**: Proposals can be kept in version control to track why certain structural decisions were made.
- **Complexity**: We need a robust "deep merge" or "patch" utility to apply the `data` from an option to the Pydantic-based `StoryBlueprint`.
- **Validation**: The `apply` step must re-validate the resulting blueprint to ensure the author's selection or manual edits didn't break the schema.
