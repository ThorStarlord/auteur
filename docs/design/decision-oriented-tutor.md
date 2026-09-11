# Decision-Oriented Tutor M1

## Purpose

The Decision-Oriented Tutor helps an author work through **one bounded creative decision at a time**. It can orient the author, explain a craft principle, recommend a direction, expose alternatives and trade-offs, and remember an explicit advisory response.

It does **not** own story canon.

The M1 boundary is:

```text
accepted story authority
        ↓
derived guidance / diagnostic evidence
        ↓
Decision Card
        ↓
local Tutor session
        ↓
author response
        ↓
existing explicit story-authority workflow, if the story should change
```

Nothing canonical changes until the author explicitly changes the story through an existing story-authority workflow.

## Authority model

Two exact statuses matter:

- A Decision Card is **`DERIVED / NOT CANON`**.
- A persisted Tutor session is **`LOCAL / NONCANONICAL`**.

Determinism, persistence, current source fingerprints, or an author selecting an option do not grant narrative authority.

`tutor choose` records what the author said about the advice. It does **not**:

- accept or promote `StoryIdentity`;
- update `blueprint.yaml`;
- rewrite accepted canon;
- apply a Structure repair;
- turn a diagnostic recommendation into an accepted change.

Use the existing Identity, Structure, Realization, or other documented authority-bearing workflow to make an actual story change.

## Decision Card

A Decision Card is the bounded, author-facing form of one derived decision. Important fields include:

| Field | Meaning |
| --- | --- |
| `decision` | The question or choice currently being presented. |
| `orientation` | Short framing for where the author is in the decision. |
| `why_it_matters` | Why the choice has narrative consequences. |
| `craft_concept` | The craft principle involved. |
| `recommendation` | Auteur's strongest advisory direction. |
| `alternatives` | Other plausible directions. |
| `tradeoffs` | Costs, benefits, and tensions around the choice. |
| `beginner_trap` | A common failure mode to avoid. |
| `downstream_consequences` | What later story work may be affected. |
| `evidence` / `pack_sources` | Where the guidance came from. |
| `author_actions` | Advisory responses the card permits. |
| `authority_status` | Always `DERIVED / NOT CANON` in M1. |

### Stable identity

Decision Cards have deterministic semantic IDs. Recreating the same semantic decision produces the same card identity. Changing only Tutor presentation depth does not create a different semantic decision.

A semantic input change can change the card ID. Source fingerprints independently identify the source snapshot on which persisted advice depended, allowing old sessions to become stale when the story changes.

Neither mechanism means that the recommendation is objectively correct, narratively causal, or authoritative. They provide identity and currentness, not canon.

## Tutor depth

M1 supports five presentation depths:

- `recommend` — concise recommendation and rationale;
- `explain` — deeper explanation of the same decision;
- `teach` — more instructional craft framing;
- `challenge` — more pressure-testing of the same decision;
- `quiz` — comprehension-oriented presentation.

Depth is **presentation-only in M1**. It does not change the semantic card ID, story authority, writer skill state, or canonical narrative state. M1 does not infer proficiency or run an adaptive curriculum.

## Local session lifecycle

Persisted sessions live beneath the selected project:

```text
.auteur/
  tutor/
    sessions/
      <session_id>.json
```

The persistence layer uses atomic replacement so a failed write does not replace an already-valid session file with a partial one.

A session has three relevant lifecycle states:

- `active` — current advice that may receive an allowed advisory response;
- `stale` — source content has changed or currentness no longer matches the stored source snapshot;
- `resolved` — a resolving advisory response has been recorded.

The supported M1 response actions are:

- `choose`;
- `keep_unresolved`;
- `reject_finding`;
- `request_alternatives`.

`choose`, `keep_unresolved`, and `reject_finding` resolve the advisory session. `request_alternatives` records the request while leaving the session active. It does not synthesize or apply new story content by itself.

### Staleness

When a persisted session is created, Auteur records fingerprints for the project-local source files supplied to that session. Later `show` and `choose` operations recompute the current file content from the stored source identities.

If relevant source content changes, the session becomes stale.

A stale session remains inspectable, but it cannot record `choose`, `keep_unresolved`, `reject_finding`, or `request_alternatives`. Regenerate a fresh card/session instead of reviving stale advice.

M1 fails closed when currentness cannot be established for an actionable persisted session. File timestamps are not treated as freshness proof.

## CLI walkthrough

### One-off advice

For an advisory card without persistence:

```powershell
auteur tutor next --pack superhero --decision "power origin"
```

For structured output:

```powershell
auteur tutor next --pack superhero --decision "power origin" --json
```

The card remains `DERIVED / NOT CANON`.

### Change presentation depth

```powershell
auteur tutor next --pack superhero --decision "power origin" --depth teach
auteur tutor explain --pack superhero --decision "power origin"
```

These commands present the same semantic decision differently; they do not make a canonical change.

### Persist a source-bound advisory session

Choose a project and bind the session to real project-local source files:

```powershell
auteur tutor next `
  --pack superhero `
  --decision "power origin" `
  --premise "A reluctant hero inherits a dangerous gift" `
  --project . `
  --source identity=story_identity.yaml `
  --source blueprint=blueprint.yaml `
  --json
```

`--source` uses `NAME=PATH`. The path must resolve to a real file inside the selected project. Auteur computes the source fingerprint from the file bytes; the caller does not provide a trusted hash.

The returned session ID identifies a local `.auteur/tutor/sessions/<session_id>.json` record whose authority remains `LOCAL / NONCANONICAL`.

### Explain a persisted decision

Use the same semantic decision and source bindings:

```powershell
auteur tutor explain `
  --pack superhero `
  --decision "power origin" `
  --premise "A reluctant hero inherits a dangerous gift" `
  --project . `
  --source identity=story_identity.yaml `
  --source blueprint=blueprint.yaml
```

### Inspect a session

```powershell
auteur tutor show <session_id> --project .
```

`show` may mark the session stale if stored source fingerprints no longer match current project files. Stale advice is still inspectable.

### Record an advisory response

```powershell
auteur tutor choose <session_id> choose `
  --value "Keep the origin costly" `
  --project .
```

Other supported actions are `keep_unresolved`, `reject_finding`, and `request_alternatives`.

`show` and `choose` do not require the caller to repeat `--source`; the persisted session already stores the normalized source identities needed to recompute current file fingerprints.

Again, this records a response only. It does not edit `story_identity.yaml`, `blueprint.yaml`, or any other accepted story artifact.

## Relationship to existing systems

### Story Design Packs

Story Design Packs remain reusable craft/design knowledge. The existing `auteur design pack ...` and legacy `auteur design tutor ...` surfaces remain available. A pack can inform a Decision Card without becoming story-instance canon.

### Structure diagnostics

A deterministic Structure diagnostic can be adapted into a Decision Card so the author can understand the finding and its repair options. Conversion does not apply the repair. The normal Structure lifecycle remains diagnose → propose → select → apply, with its own authority rules.

### Story Discovery and StoryIdentity

Story Discovery candidates and recommendations remain advisory until the author uses the existing explicit `story-discovery accept` path. The Tutor does not wrap, replace, or silently call StoryIdentity acceptance.

## M1 guarantees

The M1 regression suite makes the following boundaries executable:

- Decision Cards cannot become canon automatically.
- Tutor session persistence changes local Tutor state, not accepted story state.
- Root Tutor commands leave authoritative sentinel files byte-identical.
- A real Structure diagnostic can become a Decision Card without creating or applying a repair.
- Stale sessions reject every substantive M1 response action.
- Tutor depth does not change semantic decision identity or canon.
- Existing Story Design Pack, Genre Pack, Story Discovery, and Structure authority paths remain separate.

## What comes next

M1 deliberately stops at a safe advisory response. The next product-integration step is the **Beginner Decision Golden Path**: exercise the whole beginner journey and observe what happens after a user has understood and chosen advice.

If that workflow confirms the expected gap—“I chose this; how do I safely enact it in the story?”—the Product Evolution Roadmap identifies a **Decision-to-Authority Handoff** as a strong next candidate. That future handoff must still reuse existing story-authority workflows rather than turning Tutor into a second acceptance system.
