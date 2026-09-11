# Decision-Oriented Tutor

## Purpose

The Decision-Oriented Tutor helps an author work through **one bounded creative decision at a time**. It can orient the author, explain a craft principle, recommend a direction, expose alternatives and trade-offs, remember an explicit advisory response, and route that response toward an existing story-authority workflow when evidence supports the route.

It does **not** own story canon.

The current boundary is:

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
derived Decision Handoff
        ↓
optional concrete noncanonical proposal
        ↓
existing explicit story-authority workflow
```

Nothing canonical changes until the author explicitly changes the story through the workflow that owns the affected artifact.

## Authority model

Exact authority labels matter:

- A Decision Card is **`DERIVED / NOT CANON`**.
- A persisted Tutor session is **`LOCAL / NONCANONICAL`**.
- A Decision Handoff is **`DERIVED / NOT CANON`**.
- A Tutor-generated Structure proposal is **`NONCANONICAL PROPOSAL / NOT APPLIED`**.

Determinism, persistence, current source fingerprints, proposal generation, or an author selecting an option do not grant narrative authority.

`tutor choose`, `tutor handoff`, and `tutor propose` do **not**:

- accept or promote `StoryIdentity`;
- update `blueprint.yaml`;
- rewrite accepted canon;
- apply a Structure repair or revision;
- turn a recommendation into an accepted story change.

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
| `authority_status` | `DERIVED / NOT CANON`. |

### Stable identity

Decision Cards have deterministic semantic IDs. Recreating the same semantic decision produces the same card identity. Changing only Tutor presentation depth does not create a different semantic decision.

A semantic input change can change the card ID. Source fingerprints independently identify the source snapshot on which persisted advice depended, allowing old sessions to become stale when the story changes.

Neither mechanism means that the recommendation is objectively correct, narratively causal, or authoritative. They provide identity and currentness, not canon.

## Tutor depth

The Tutor supports five presentation depths:

- `recommend` — concise recommendation and rationale;
- `explain` — deeper explanation of the same decision;
- `teach` — more instructional craft framing;
- `challenge` — more pressure-testing of the same decision;
- `quiz` — comprehension-oriented presentation.

Depth is presentation-only. It does not change the semantic card ID, story authority, writer skill state, or canonical narrative state. The Tutor does not infer proficiency or run an adaptive curriculum.

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

Supported response actions are:

- `choose`;
- `keep_unresolved`;
- `reject_finding`;
- `request_alternatives`.

`choose`, `keep_unresolved`, and `reject_finding` resolve the advisory session. `request_alternatives` records the request while leaving the session active. It does not synthesize or apply new story content by itself.

### Staleness

When a persisted session is created, Auteur records fingerprints for the project-local source files supplied to that session. Later actionable Tutor operations recompute current file content from the stored source identities.

If relevant source content changes, the session becomes stale.

A stale session remains inspectable, but it cannot yield a new substantive response, actionable authority handoff, or concrete Tutor-to-Structure proposal. Regenerate fresh advice instead of reviving stale advice.

Auteur fails closed when currentness cannot be established. File timestamps are not treated as freshness proof.

## CLI walkthrough

### One-off advice

```powershell
auteur tutor next --pack superhero --decision "power origin"
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

### Inspect and respond

```powershell
auteur tutor show <session_id> --project .
auteur tutor choose <session_id> choose --value "Keep the origin costly" --project .
```

`show` may mark the session stale if stored source fingerprints no longer match current project files. A choice records the advisory response only; it does not edit accepted story artifacts.

### Route a resolved choice

```powershell
auteur tutor handoff <session_id> --project .
```

A handoff is an on-demand derived projection. It names the owning layer/artifact and an existing authority workflow only when the evidence supports that route. It never executes the authority-bearing step, and stale or unsupported contexts fail closed.

### Prepare a concrete Structure proposal

For the currently supported Tutor-to-Structure route:

```powershell
auteur tutor propose <session_id> --project .
```

The model's responsibility is bounded to creative proposal content. Deterministic code owns currentness, allowed fields, schema validation, no-op rejection, IDs, paths, persistence, and authority classification.

The generated `StructureProposal` is intentionally **unselected and noncanonical**. The author must inspect and select the concrete realization explicitly:

```powershell
auteur structure proposal inspect <proposal.yaml> --project .
auteur structure proposal select <proposal.yaml> --option <option_id> --project .
```

Selection changes only proposal decision metadata. It does not update the blueprint or automatically create a revision plan.

### Continue through Structure authority

```powershell
auteur structure revision plan --proposal <proposal.yaml> --project .
auteur structure revision validate <plan_id> --project .
auteur structure revision preview <plan_id> --project .
auteur structure revision apply <plan_id> --project . --confirm
auteur structure revision reassess <application_id> --project .
```

Planning/validation are non-applying. Narrative Change Preview is `DERIVED PREVIEW / NOT APPLIED`. Only the explicit confirmed revision application changes Structure authority. Reassessment is `DERIVED REASSESSMENT / READ ONLY` and reports only what deterministic evidence can support.

For a complete walkthrough, see [../guides/guided-author-decision-loop.md](../guides/guided-author-decision-loop.md).

## Relationship to existing systems

### Story Design Packs

Story Design Packs remain reusable craft/design knowledge. The existing `auteur design pack ...` and legacy `auteur design tutor ...` surfaces remain available. A pack can inform a Decision Card without becoming story-instance canon.

### Structure diagnostics and revision

A deterministic Structure diagnostic can be adapted into a Decision Card so the author can understand the finding and its repair options. Conversion does not apply the repair. Structure remains responsible for proposal selection, revision planning, validation, preview, confirmed application, and any deterministic post-application reassessment.

Tutor-generated craft proposals deliberately reuse that existing Structure lifecycle rather than creating a second mutation system.

### Story Discovery and StoryIdentity

Story Discovery candidates and recommendations remain advisory until the author uses the existing explicit `story-discovery accept` path. The Tutor does not wrap, replace, or silently call StoryIdentity acceptance.

### Dashboard and Guided Author Workspace

The dashboard's Author Attention projection and Guided Author Workspace V1 can surface stale Tutor sessions, unresolved advice, proposal review, revision planning, blocked/current plans, and the next safe command. They are read-only orientation surfaces and do not perform the actions they recommend.

## Executable guarantees

The current regression/integration suite makes the following boundaries executable:

- Decision Cards cannot become canon automatically.
- Tutor session persistence changes local Tutor state, not accepted story state.
- Root Tutor advice/choice/handoff/proposal preparation cannot silently mutate StoryIdentity or Structure.
- Stale sessions fail closed before actionable continuation.
- Tutor-generated Structure proposals require explicit review/selection.
- Proposal-backed revision planning fails closed on unselected or zero-operation proposals.
- Invalid blueprint replacement fails before destructive write.
- Narrative Change Preview and Decision Reassessment are read-only.
- Tutor/craft reassessment reports `not_assessable` when exact deterministic diagnostic identity is unavailable.
- The full Beginner Decision Golden Path keeps StoryIdentity byte-identical and keeps the blueprint unchanged until the explicit confirmed Structure application step.
- Existing Story Design Pack, Genre Pack, Story Discovery, Structure, and other authority paths remain separate.

## Current product posture

The original M1 advisory Tutor milestone is complete, and the evidence-led continuation through authority handoff, proposal formation/selection, revision preview/application, reassessment, project orientation, and Guided Author Workspace V1 is now integrated.

Further work should be selected from observed product friction rather than automatically extending Tutor authority or adding new ontology. The long-horizon campaign remains separately evidence-gated.