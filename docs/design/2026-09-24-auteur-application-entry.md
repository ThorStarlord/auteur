# Auteur Application Entry

**Status:** implemented product contract  
**Selected:** 2026-09-24  
**Scope:** local application launch + Home + story reopening

## Decision

Auteur uses the existing local Python server and browser UI as the product runtime,
but the author no longer needs to understand that architecture.

The selected entry model is:

```text
auteur
  -> detect an already-running Auteur instance
  -> otherwise start the local server
  -> open the browser
  -> Auteur Home
       -> New Story
       -> Recent Stories
       -> Advanced workspace-ID opening
```

On Windows, `Auteur.cmd` delegates to the same launcher. The optional
`scripts/install-auteur-shortcut.ps1` creates a Desktop shortcut to that
launcher.

## Product / infrastructure boundary

Author-facing concepts:

- Auteur
- New Story
- Your Stories
- premise
- Story Architecture
- Continue

Infrastructure concepts remain advanced/developer surfaces:

- workspace ID
- localhost port
- Python server
- npm supervisor
- persistence paths

`workspace_id` remains a durable internal identifier, not the primary product
metaphor.

## Home contracts

### Recent stories

`GET /api/beginner/workspaces` returns a read-only newest-first index over
existing `.auteur/beginner/workspaces/*/session.json` state.

A damaged workspace is skipped rather than repaired or allowed to block Home.
The index never mutates story state.

### New story

`POST /api/beginner/workspaces` may omit both `workspace_id` and
`project_id`.

The server generates the workspace ID and uses it as the project ID when no
explicit project ID is supplied. Existing explicit-ID automation remains
compatible.

The browser therefore sends only the premise and an idempotency command ID.
The returned projection opens directly on Story Architecture.

## Launcher contracts

Both of these open the application:

```text
auteur
auteur open
```

Options:

```text
--project PATH
--port PORT
--provider openai|anthropic
--model MODEL
--no-browser
```

If the configured port already serves Auteur's health contract, the launcher
reuses that process and only opens Home. If the port belongs to another
application, startup fails clearly rather than pretending Auteur is running.

Health contract:

```json
{"app":"auteur","surface":"beginner","status":"ok"}
```

## Developer path

`npm start` and `npm run dev` remain developer mechanisms. They are not the
primary author-facing way to open Auteur.

## Desktop packaging boundary

A native packaged `.exe`, Electron/Tauri shell, or PWA is **not** required for
this package. The Windows shortcut is deliberately a thin launcher over the
same canonical local application.

That keeps desktop distribution replaceable until there is evidence that a
native shell adds value beyond launch convenience.
