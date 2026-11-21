# Auteur operations and candidate contract

These describe the Studio architecture bridge on the current main branch. They are the contract for every operation you may use.

## Running the bridge

    PYTHONPATH=<repo>/src PYTHONUTF8=1 python -m auteur.beginner.studio_architecture --project <project> --canvas <canvas> <action> [options]

The repository path, the project and the canvas are given in 04-access.md.

## Read-only actions

- `resume`: a read-only re-entry packet. It contains the story vision (`story_vision`), the current working candidate (`architecture`), the open questions, the provisional concepts, the author's intentions (`creative_intentions`), any pending request, and the adoption lineage. It also contains a block of generic ontology guidance (`ontology_guidance`). That block is product output. Judge it on its merits.
- `show`: the current proposal, or the pending host-agent request.
- `intentions`: the author-directed creative intentions and their status.

## Write actions

- `prepare [--instruction TEXT]`: opens a host-agent request. Without an instruction it asks for a new architecture. With an instruction it asks for a revision of the current candidate.
- `complete-file --candidate FILE`: validates a candidate JSON file you wrote against the pending request, using the schema below. On success the candidate becomes the proposal. If the request carried a revision instruction, the candidate is stored as a reviewed revision and waits for application. The bridge has no command to apply a reviewed revision.
- `record-concept --concept FILE`: records one provisional concept. The file must hold these fields: `name` (up to 120 characters), `definition` (up to 1200), `motivating_story_use` (up to 1200), `why_existing_concepts_insufficient` (up to 1200), `related_concepts` (up to 16), `proposed_relations` (up to 16), `compatibility_concerns` (up to 16), and `status`, which must be `"provisional"`.
- `keep-intention --title TEXT --directive-file FILE [--status provisional|active]`: records an author-directed intention. Use it only for directives the author has given. Do not invent author intentions.
- `set-intention-status --id ID --status STATUS`: an author action. Do not use it.

## The candidate schema (schema version 2, JSON)

- `schema_version`: 2.
- `summary`: up to 3000 characters.
- `nodes` (up to 80): each has `id`, `title` (up to 120), `category`, `summary` (up to 2000), `scope`, `parent_id`. Allowed categories: `reader_experience`, `aesthetic`, `genre`, `trope`, `engine`, `thread`, `structure`, `theme`, `character`, `relationship`, `other`.
- `links` (up to 180): each has `id`, `source`, `target` and `function`. The function is a short label of up to 120 characters. Links carry no provenance field.
- `phases` (up to 32): each has `id`, `title`, `order`, `scope`, `genres` (up to 8, roles `governing`, `locally_dominant`, `supporting` or `background`), `genre_activations` (up to 8), `narrative_function` (up to 1000 characters), `transition` (up to 700 characters) and `parallel_with`.
- `genre_contracts` (up to 14): roles are `governing`, `supporting`, `tertiary` or `local`. `background` is not a contract role.
- `emotion_targets` (up to 30): each has a `provenance`, which is `author_declared` or `agent_proposed`. Agents must set `agent_proposed`. Do not set `author_declared`.
- `complex_emotions` (up to 16), and `genre_interactions` (up to 40, each with `kind` one of `reinforces`, `enables`, `constrains`, `contrasts`, `creates_tension`, `converges`).
- `open_questions` (up to 16 strings).

## What the schema does not hold

- There is no Book node. A Book's function must be expressed in a phase narrative, a node summary or an open question.
- There is no institution category. Institutions use `other`.
- Phase narratives are capped at 1000 characters, so a phase covering several Books cannot describe each Book in full.
- Provenance exists only for emotion targets.

A validation error from `complete-file` is the product's answer, not a fault in your reasoning. Quote it in `product-use.md`.
