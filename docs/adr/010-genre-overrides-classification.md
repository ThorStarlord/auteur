# ADR 010: First-Class Genre Overrides and Consequence Classification

## Status

Accepted

## Context

Auteur's whole-story structure engine provides highly opinionated genre recommendations and expectations (e.g., emotional runways, required tropes, and ending tones). While this ensures high genre fidelity, forcing absolute adherence turns the system into a "genre prison" that limits authorial freedom. Writers often need to:
- Establish relationships in highly compressed formats.
- Intentionally subvert genre conventions for artistic effect.
- Reclassify their work when it morphs from one primary genre contract to a related hybrid/sub-genre format (e.g., Netorare to transgressive vignette).

We need an explicit, parseable system where the user can override any genre recommendation. At the same time, Auteur must remain honest and prevent authors from assuming their original genre contract is intact when they violate load-bearing expectations. It should classify overrides, raise helpful advice diagnostics, and provide a structured decision-tree option-flow to guide the author.

## Decision

Introduce first-class **Genre Overrides** into the Auteur story blueprint and structure diagnostics engine.

### 1. Blueprint Schema Changes (`src/auteur/blueprint.py`)
Add a `genre_overrides` mapping field to `ProjectIdentity` (Layer 1). This mapping has keys corresponding to the expectation being bypassed (e.g. `"emotional_runway"`, `"required_tropes"`, `"ending_tone"`) and links to a `GenreOverride` model:
- `load_bearing_expectation`: The specific genre contract field being bypassed.
- `user_override`: A short textual description of the author's alternative choice.
- `override_type`: An enum defining the classification of the consequence:
  - `safe_variation`: The user changes something non-essential. Genre remains fully intact.
  - `compression`: The user shortens a required mechanism (e.g., relation runway setup). Genre remains intact if setup is high-density and efficient.
  - `subversion`: The expectation is intentionally violated to make the audience feel the violation.
  - `reclassification`: A load-bearing requirement is deleted, changing the primary genre contract of the story.
- `rationale`: Optional free-text explaining the author's intention.

### 2. Diagnostics Modeling (`src/auteur/structure/diagnostics.py`)
Add a `genre_recommendation_flow` dictionary to the `StructureDiagnostic` schema. This represents the diagnostic flow outlining options:
- `selected_genre`: The chosen genre contract.
- `load_bearing_expectation`: The expectation violated.
- `user_override`: The bypass description.
- `auteur_diagnosis`: The risk type (e.g., `genre_contract_risk`).
- `consequence`: The primary impact on audience reception.
- `options`: A dictionary of recommendations for the user:
  - `preserve_genre`: Recommendation on how to keep the genre using compression/alternative techniques.
  - `subvert_genre`: Recommendation on how to make the suddenness or subversion itself a successful artistic product.
  - `reclassify`: Recommendation on what the new genre contract should be renamed to.
  - `override_anyway`: Recommendation/note on proceeding anyway with reduced confidence.

### 3. Diagnostic Analyzer Changes (`src/auteur/structure/analyzer.py`)
Update the structure diagnostics engine:
- If a genre expectation is violated (e.g., a short story container is used for Netorare requiring a long emotional runway) and **no override** is declared, raise a standard warning/error but attach the rich `genre_recommendation_flow` payload to the diagnostic.
- If a valid override **is** declared:
  - **`safe_variation` or `compression`**: Suppress the error and output a low-priority advice warning highlighting the required compression strategies.
  - **`subversion`**: Suppress the error/warning and output an advice warning prompting the author to ensure the violation is intentional and replaced with another product (e.g. shock, absurdity).
  - **`reclassification`**: Warn the user of the primary contract change, advising them to reclassify their story.

## Consequences

- Authors remain in full control of their stories while the engine maintains strict, objective genre logic honesty.
- The structure engine transitions from a "genre police" system into a high-value narrative consulting partner.
- The downstream LLM agents (Cartographer, Critic) can parse overrides and tailor their chapter outlines/critiques accordingly.
