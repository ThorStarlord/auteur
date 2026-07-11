# Genre Pipeline Architecture Context

This document defines the domain language and runtime ownership for Auteur's
built-in interactive genre pipelines.

## Genre Pipeline

A genre pipeline is a deterministic Narrative Engine workflow that turns an
author's nine-layer choices into a validated `StoryIdentity`. Netorare, mystery,
and gentlefemdom are built-in pipelines. A built-in pipeline is not an external
plugin and is separate from project-local contracts created by Genre Builder.

Each pipeline supplies genre-specific intent through a `GenrePipelineSpec`:

- genre and stable slug;
- supported emotional core IDs and their default core;
- template factory and deterministic choice validator;
- genre-contract loader and core identity profile;
- browser title, default port, and author-visible mode default.

The registry is operational: public genre commands resolve a specification and
execute through `auteur.genre_pipeline`. Runtime code does not dispatch on genre
names or import another genre's command, session, server, or identity generator.

## Nine Layers

1. Emotional core
2. Genre contract
3. Scope and scale
4. Structural forces: want, resistance, conflict, stakes, change
5. Threads or the core-specific fifth design dimension
6. Carriers or the core-specific sixth design dimension
7. Representation or the core-specific seventh design dimension
8. Modulation or the core-specific eighth design dimension
9. Resonance and ratification

Templates expose phase names, options, constraints, and a primary emotion. The
runtime normalizes existing mapping-shaped and flat option layouts into one
browser descriptor. A phase without options is derived context and requires no
stored author selection.

## Runtime Ownership

`auteur.genre_pipeline` owns:

- versioned interactive session state;
- normalization of template data for the browser;
- localhost HTTP endpoints and packaged browser assets;
- deterministic choice and completion validation;
- neutral compilation of completed choices into `StoryIdentity`;
- orchestration shared by all public built-in genre commands.

Genre packages own their templates and validation rules. The operational
registry owns core identity profiles, while `auteur.genres` owns genre contracts.
Project-local custom contracts do not become browser pipelines automatically.

## Canonical State

Browser session state is a non-canonical working artifact stored at:

```text
<project>/.auteur/genre_sessions/<genre-slug>/session.json
```

The author may change choices, working title, and story mode while the session is
incomplete. Browser completion is explicit ratification of those choices. The CLI
then compiles and validates a `StoryIdentity`; error diagnostics block the write,
while warnings are reported. Existing `story_identity.yaml` files are never
silently overwritten.

Legacy `<project>/netorare/session.json` files are detected but never silently
migrated. They remain non-canonical and require an explicit author decision.

## Public Commands

The public entry points remain:

```text
auteur netorare init <project>
auteur mystery init <project>
auteur gentlefemdom init <project>
```

Each is a thin adapter over the same runtime. Core choices and default ports come
from the registry. Story mode has a visible core-specific default and remains
author-overridable. `--provider` is compatibility-only because interactive genre
authoring performs no LLM call.

## Extension Rule

Adding a built-in genre requires templates, deterministic validation, core
identity profiles, a genre contract, one registry entry, and tests. It must not
require edits to session, server, browser, or identity compilation logic.

Last updated: 2026-07-10.
