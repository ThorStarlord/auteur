# Guided Author Decision Loop

This guide describes the current bounded path from advisory guidance to an explicit story change. It is a product workflow over existing authority services, not a new narrative layer.

## Authority at a glance

| Surface | Authority |
| --- | --- |
| Decision Card | `DERIVED / NOT CANON` |
| Tutor session | `LOCAL / NONCANONICAL` |
| Decision Handoff | `DERIVED / NOT CANON` |
| Tutor-generated Structure proposal | `NONCANONICAL PROPOSAL / NOT APPLIED` |
| Structure revision plan | `REVISION PLAN / NOT APPLIED` |
| Narrative Change Preview | `DERIVED PREVIEW / NOT APPLIED` |
| confirmed Structure revision application | explicit Structure authority action |
| Decision Reassessment | `DERIVED REASSESSMENT / READ ONLY` |
| Dashboard / Author Attention | derived read-only orientation |
| Guided Author Workspace V2 | local adapter over the same application services; actions retain their native authority status |

Selection, persistence, deterministic IDs, source currentness, or clicking a browser control do not turn advice into canon. The story changes only at an owning authority workflow with explicit author confirmation.

## 1. Establish accepted story direction

```powershell
auteur story-discovery run "<premise>" --recommend --output story_discovery --project .
auteur story-discovery accept story_discovery\candidate_1.yaml --output story_identity.yaml
auteur blueprint seed story_identity.yaml --output blueprint.yaml
```

Story Discovery candidates remain advisory until `story-discovery accept`.

## 2. Ask Tutor for one bounded decision

Bind persisted advice to current project sources:

```powershell
auteur tutor next `
  --pack superhero `
  --decision "power origin" `
  --premise "<premise>" `
  --project . `
  --source identity=story_identity.yaml `
  --source blueprint=blueprint.yaml
```

Use `auteur tutor explain ...` for deeper presentation and `auteur tutor show <session_id> --project .` to inspect a stored session.

Record an advisory choice:

```powershell
auteur tutor choose <session_id> choose --value "<choice>" --project .
```

This resolves local Tutor state only. It does not edit StoryIdentity or the blueprint.

## 3. Route the decision to its owning authority workflow

```powershell
auteur tutor handoff <session_id> --project .
```

The handoff identifies an existing authority route when evidence is sufficient. It does not execute that route. Stale or ambiguous advice fails closed.

For the currently supported Tutor-to-Structure route:

```powershell
auteur tutor propose <session_id> --project .
```

Proposal generation may use an LLM for bounded creative content, but deterministic code owns currentness, schema validation, allowed fields, IDs, paths, and persistence.

## 4. Inspect and explicitly select the proposal

```powershell
auteur structure proposal inspect <proposal.yaml> --project .
auteur structure proposal select <proposal.yaml> --option <option_id> --author "<name>" --project .
```

Selection changes proposal decision metadata only. The blueprint remains unchanged.

## 5. Plan and validate the revision

```powershell
auteur structure revision plan --proposal <proposal.yaml> --project .
auteur structure revision validate <plan_id> --project .
```

Planning and validation remain non-applying. Unselected proposals, zero-operation plans, stale preconditions, and invalid replacement content fail closed.

## 6. Preview consequences

```powershell
auteur structure revision preview <plan_id> --project .
```

Narrative Change Preview is derived/read-only. It reports intended direct changes, currentness, and downstream artifacts already evidenced by Auteur's dependency/impact machinery. It does not invent speculative story-quality effects.

## 7. Cross the Structure authority boundary

CLI:

```powershell
auteur structure revision apply <plan_id> --project . --confirm
```

Application validates preconditions and scope. Without explicit confirmation no accepted Structure change is allowed.

If the process was interrupted while an application was in progress:

```powershell
auteur structure revision recover --project .
```

Recovery is fail-closed. A stranded plan returns to `ready` only when current target hashes prove every authority target is unchanged. If target state changed and no durable application record proves what happened, the plan becomes `failed` for inspection. Recovery never automatically replays an authority-bearing revision.

## 8. Reassess only what evidence can establish

```powershell
auteur structure revision reassess <application_id> --project .
```

For proposals tied to an exact native Structure diagnostic rule, Auteur can rerun that rule and report `resolved` or `remaining`. Tutor/craft-originated changes without an exact deterministic diagnostic identity remain `not_assessable`; Auteur does not manufacture a creative-quality score.

## 9. Ask what needs attention now

```powershell
auteur dashboard --project .
```

Author Attention prioritizes stale Tutor sessions, unresolved decisions, proposal review, revision planning, blocked/draft/ready plans, and the next safe action.

## 10. Use Guided Author Workspace V2 instead of typing the core loop

```powershell
auteur workspace --project . --port 8765
```

Open `http://127.0.0.1:8765` locally.

The V1 closure Workspace is a browser adapter over the same application services used by the CLI path. For the bounded supported Structure loop it can:

```text
view Author Attention
→ record a Tutor choice
→ review/select a Structure proposal
→ create and validate a revision plan
→ preview consequences
→ separately confirm the authority-bearing Structure application
→ return to refreshed project orientation
```

The browser does not shell out to CLI commands and does not maintain a second story-state database.

### Workspace safety boundaries

- server binds only to `127.0.0.1`;
- mutation uses POST routes only;
- Host and same-origin Origin are validated;
- each Workspace process uses a session-specific CSRF token;
- action payload size is bounded;
- project-relative proposal paths cannot escape the selected project;
- the Structure authority action still requires a separate explicit confirmation;
- a blocked/malformed request does not become a story mutation.

## Realization ↔ Expression boundary

The bounded V1 Scene path applies the same authority rule downstream. Expression may freely render wording, dialogue, imagery, rhythm, interiority, and local pacing, but it cannot silently redefine accepted Realization facts.

When structured prose evidence contradicts accepted Scene Realization:

```text
prose candidate
→ blocking/review-required Expression finding
→ optional noncanonical upstream Realization proposal
→ explicit owning Realization action if the author wants to change the fact
→ Expression revalidation
```

The prose finding/proposal never edits the accepted Scene automatically. See [../expression-boundary.md](../expression-boundary.md).

## Complete bounded loop

```text
accepted story direction
→ bounded Tutor decision
→ advisory choice
→ derived authority handoff
→ concrete noncanonical proposal
→ explicit proposal selection
→ revision plan
→ validation
→ derived change preview
→ explicit confirmed Structure authority action
→ bounded reassessment
→ project orientation
```

The important boundary is **derived guidance versus explicit narrative authority**. Auteur can recommend, explain, prepare, preview, detect staleness, recover safely, and reassess; accepted story change remains an explicit action in the workflow that owns the artifact.
