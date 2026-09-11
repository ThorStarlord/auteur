# Guided Author Decision Loop

This guide describes the current beginner-facing path from advisory guidance to an explicit story change. It is a product workflow, not a new narrative layer.

## Authority at a glance

| Surface | Authority |
| --- | --- |
| Decision Card | `DERIVED / NOT CANON` |
| Tutor session | `LOCAL / NONCANONICAL` |
| Decision Handoff | `DERIVED / NOT CANON` |
| Tutor-generated Structure proposal | `NONCANONICAL PROPOSAL / NOT APPLIED` |
| Structure revision plan | `REVISION PLAN / NOT APPLIED` |
| Narrative Change Preview | `DERIVED PREVIEW / NOT APPLIED` |
| `structure revision apply --confirm` | explicit Structure authority action |
| Decision Reassessment | `DERIVED REASSESSMENT / READ ONLY` |
| Dashboard / Guided Author Workspace | derived read-only orientation |

Selection, persistence, deterministic IDs, or source currentness do not turn advice into canon. The story changes only at an owning authority workflow with explicit author confirmation.

## 1. Establish accepted story direction

For a new project, explore Story Discovery candidates and explicitly accept the direction you want:

```powershell
auteur story-discovery run "<premise>" --recommend --output story_discovery --project .
auteur story-discovery accept story_discovery\candidate_1.yaml --output story_identity.yaml
auteur blueprint seed story_identity.yaml --output blueprint.yaml
```

Story Discovery candidates remain advisory until `story-discovery accept`.

## 2. Ask Tutor for one bounded decision

Bind persisted advice to real project sources so Auteur can later detect staleness:

```powershell
auteur tutor next `
  --pack superhero `
  --decision "power origin" `
  --premise "<premise>" `
  --project . `
  --source identity=story_identity.yaml `
  --source blueprint=blueprint.yaml
```

Use `auteur tutor explain ...` for deeper presentation of the same semantic decision and `auteur tutor show <session_id> --project .` to inspect the stored session.

Record an advisory choice:

```powershell
auteur tutor choose <session_id> choose --value "<choice>" --project .
```

This resolves local Tutor state only. It does not edit StoryIdentity or the blueprint.

## 3. Route the decision to its owning authority workflow

Ask for a derived handoff:

```powershell
auteur tutor handoff <session_id> --project .
```

The handoff identifies an existing authority route when evidence is sufficient. It does not execute the route. Stale or ambiguous advice must fail closed rather than guess.

For the currently supported Tutor-to-Structure route, create a concrete noncanonical proposal:

```powershell
auteur tutor propose <session_id> --project .
```

Proposal generation may use an LLM for bounded creative patch content, but deterministic code owns schema validation, source currentness, artifact paths, IDs, and authority rails.

## 4. Inspect and explicitly select the concrete proposal

```powershell
auteur structure proposal inspect <proposal.yaml> --project .
auteur structure proposal select <proposal.yaml> --option <option_id> --author "<name>" --project .
```

Selection records proposal decision metadata only. The blueprint is still unchanged.

## 5. Plan and validate the revision

```powershell
auteur structure revision plan --proposal <proposal.yaml> --project .
auteur structure revision validate <plan_id> --project .
```

Planning and validation remain non-applying. Unselected proposals, zero-operation proposal plans, and stale preconditions fail closed.

## 6. Preview consequences before authority changes

```powershell
auteur structure revision preview <plan_id> --project .
```

Narrative Change Preview is derived/read-only. It reports the direct target, intended changed fields, currentness, and downstream artifacts evidenced by Auteur's existing dependency graph. It does not claim speculative story-quality effects.

If the plan is stale, preview remains inspectable but does not present the revision as ready to apply.

## 7. Cross the explicit Structure authority boundary

Only this step changes the blueprint:

```powershell
auteur structure revision apply <plan_id> --project . --confirm
```

Application validates preconditions and scope and fails closed on invalid blueprint content. The explicit `--confirm` is the authority gate.

## 8. Reassess what deterministic evidence can actually say

```powershell
auteur structure revision reassess <application_id> --project .
```

For a proposal derived from an exact native Structure diagnostic rule, Auteur reruns the canonical analyzer and reports whether that same rule is `resolved` or `remaining`.

For Tutor/craft-originated changes without an exact diagnostic identity, the correct result is `not_assessable`. Auteur does not manufacture a quality score or pretend a subjective craft choice was deterministically proven successful.

## 9. Ask Auteur what needs attention now

The existing dashboard composes current project orientation:

```powershell
auteur dashboard --project .
```

Its **Author Attention** section prioritizes stale Tutor sessions, unresolved decisions, proposal review, revision planning, blocked/draft/ready plans, and the next safe command.

For a beginner-oriented local browser presentation:

```powershell
auteur workspace --project . --port 8765
```

Open `http://127.0.0.1:8765` locally. Guided Author Workspace V1 is loopback-only and read-only. It exposes no mutation endpoints; it shows the same derived orientation and existing safe command rather than creating another acceptance path.

## The complete loop

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
→ explicit revision apply --confirm
→ bounded reassessment
→ dashboard / Guided Author Workspace orientation
```

The important boundary is not "AI versus human." It is **derived guidance versus explicit narrative authority**. Auteur can recommend, explain, prepare, preview, and reassess; accepted story change remains an explicit action in the workflow that owns that artifact.