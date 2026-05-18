# ADR 004: Story Identity Schema and Compilation Workflow

## Status

Accepted

## Context

Auteur operates as a literary compiler. Its main document, the `StoryBlueprint`, defines the story's granular structural contract, including exact character lists, chapter waveforms, thread supports, and word count constraints. 

However, authors and creative agents face a cold-start problem. Generating a highly structured blueprint from raw, messy creative intent in a single step leads to:
1. Significant validation failures when the agent tries to guess all granular details.
2. Silent mutation or corruption of the core story intent.
3. Vague, chat-like behavior that violates Auteur's deterministic design principles.

We need a structured, high-level creative contract—the **Story Identity**—that operates *before* the blueprint, allowing the author and agent to lock down high-level thematic and emotional promises without getting bogged down in character metrics.

## Decision

We will introduce a distinct **Story Identity** layer, structured via Pydantic and backed by a deterministic compilation engine that seeds a fully valid blueprint skeleton.

### Schema

The `StoryIdentity` schema (defined in `src/auteur/identity.py`) captures:
- `title` & `core_answer`: The singular creative compass of the project.
- `target_experience`: The emotional promise (primary, progression, avoided outcomes).
- `story_type`: Classification mapping to existing Auteur enums (medium, mode, genre, subgenres, target audience).
- `central_engine`: High-level structural forces (Want, Resistance, Conflict, Stakes, Change).
- `not_this`: Bounds defining creative drift.
- `open_questions`: Unresolved narrative and thematic questions.

### Workflow & CLI

1. **Design**: An agent or author uses the `story-identity-architect` skill playbook to iterate on a `story_identity.yaml` using a disciplined "grilling workflow."
2. **Validate**: `auteur identity validate <path>` checks the YAML file against the Pydantic schema to ensure all creative constraints are structurally sound.
3. **Seed/Compile**: `auteur blueprint seed <identity_path> --output <blueprint_path>` maps the high-level forces into a complete, valid `StoryBlueprint` skeleton populated with clean defaults (standard three-act structure, default protagonist/antagonist characters with aligned arcs, tension curves).

## Consequences

- **Separation of Concerns**: Creative alignment happens first in `story_identity.yaml`; structural mechanics are compiled into `blueprint.yaml`.
- **Deterministic Validation**: Protects Auteur from turning into a fuzzy LLM-driven chat assistant.
- **TDD Compliance**: The entire identity pipeline is covered by rigorous validation and compilation tests.
- **Traceability**: `story_identity.yaml` can be saved under version control, documenting the high-level decision-making process of the story.
