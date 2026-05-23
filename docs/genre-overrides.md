# Genre Overrides

Genre overrides let you deliberately break a genre contract expectation while keeping Auteur's diagnostics honest about the consequence.

## When to Use an Override

Auteur's genre contracts enforce load-bearing expectations: required tropes, ending tones, emotional runways, and psychology budgets. When `auteur structure diagnose` flags a contract violation, you have two options:

- **Fix the underlying element** to satisfy the contract.
- **Declare a GenreOverride** to document the intentional deviation.

Overrides are **author-only** decisions. The LLM is forbidden from injecting them during identity recommendation.

## Override Types

| Type | Meaning | Diagnostic Effect |
|---|---|---|
| `safe_variation` | Minor deviation within genre tolerance | ERROR → WARNING |
| `compression` | Shortening a required mechanism (e.g., emotional runway) with high-density execution | ERROR → WARNING |
| `subversion` | Intentionally inverting a trope or expectation to make the violation felt | ERROR → WARNING |
| `reclassification` | Deleting a load-bearing requirement, effectively changing the genre contract | ERROR → WARNING |

## Syntax

Add a `genre_overrides` mapping to `ProjectIdentity` in your `blueprint.yaml`:

```yaml
identity:
  genre: mystery
  genre_overrides:
    ending_tone:
      load_bearing_expectation: "A mystery contract forbids a purely tragic ending."
      user_override: "The detective dies in the final confrontation to underscore systemic corruption."
      override_type: subversion
      rationale: "The tragic ending is the point — it completes the hardboiled transformation."
    trope.clue_fair_puzzle:
      load_bearing_expectation: "locked_room subgenre requires fair-play clue logic."
      user_override: "The method is supernatural; clues are irrelevant."
      override_type: reclassification
      rationale: "This is a supernatural horror story wearing a mystery coat."
```

The override key must match the expectation being bypassed. Current recognized keys:

| Key | What it overrides |
|---|---|
| `ending_tone` | Genre contract's forbidden ending tone |
| `emotional_runway` | Genre contract's minimum setup/runway requirement |
| `trope.<name>` | A specific required trope that is being forbidden (e.g., `trope.clue_fair_puzzle`) |

## How Diagnostics React

When an override is present:

- The diagnostic severity drops from `ERROR` to `WARNING`.
- The rule ID appends the override type as a suffix (e.g., `genre.forbidden_mismatch.ending_tone.subversion`).
- The evidence lists the override type and user description.
- Repair options shift from "fix the problem" to "handle the consequence."

Without an override, the same violation remains an `ERROR` and blocks compilation.

## General Rule Categories

The CONTEXT.md glossary references two generic rule categories:

- `genre.forbidden_mismatch.override_bypassed` — covers ending-tone and required-trope overrides.
- `genre.runway.override_bypassed` — covers emotional-runway overrides.

The actual emitted rule IDs carry the specific override type as a suffix (e.g., `genre.setup_contract.insufficient_runway.compressed`).
