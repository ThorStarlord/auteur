# Guided Author Decision Loop

This guide describes the current beginner-facing path from a raw premise through
Narrative Architecture, explicit foundation acceptance, Chapter 1 planning,
candidate drafting, review/revision, and explicit Chapter 1 acceptance. It also
covers the later advisory decision loop. It is a product workflow, not a new
narrative layer.

For a creative beginner, the Browser Workspace is the preferred orientation
surface. The CLI route later in this guide remains useful for advanced authors
and for explicit lower-level workflow inspection.

## Authority at a glance

| Surface | Authority |
| --- | --- |
| Working interpretation / "What Auteur sees" | `DERIVED / NOT CANON` |
| Story Direction candidate / selected direction | `DERIVED / NOT CANON` until explicit Direction acceptance |
| Accepted Story Direction | accepted milestone; does not itself write canonical StoryIdentity |
| Story Identity candidate | `PROPOSED / NOT CANON` |
| Accepted Story Identity | canonical Identity |
| Structure working choices / review | working / derived until explicit Structure acceptance |
| Accepted Whole-Story Structure | canonical foundation milestone |
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

## Browser-first Beginner foundation path

Start with a fresh premise in the Beginner Workspace rather than pre-encoding the
correct architecture. The contemporary beginner route is:

```text
raw premise
→ What Auteur sees
→ How these parts work together
→ optional interpretation correction
→ Story Discovery
→ select a Story Direction
→ explicitly accept Story Direction
→ inspect Story Identity candidate
→ explicitly accept Story Identity
→ answer / review Structure decisions
→ explicitly accept Whole-Story Structure
→ highlighted next phase
→ whole-story outline → explicit outline acceptance
→ Chapter 1 plan → explicit plan acceptance
→ scene plans → explicit scene-plan acceptance
→ generate a noncanonical Chapter 1 candidate
→ review or revise the candidate
→ explicitly accept Chapter 1
```

### 1. Read the working interpretation

**What Auteur sees** is a derived working interpretation, not canon. It should
make clear which story dimensions are present and, when evidence supports it,
how they compose:

- main story machinery / narrative engine;
- genre and story traditions;
- aesthetic framing;
- common trope families;
- relationship or thematic dynamics;
- narrative structure status;
- intended reader experience.

The important beginner question is not merely "which labels were detected?" but
"how do these parts work together as this story?" If a material dimension such
as aesthetic framing is not established, Auteur should say so rather than
inventing one.

Interpretation refinement changes working guidance. It does not silently edit
accepted Story Identity or accepted Structure.

### 2. Explore and accept a Story Direction

Discovery should present genuinely different causal story directions rather than
surface-level paraphrases. Selecting a direction remains noncanonical. Explicit
Direction acceptance records the accepted direction milestone but still does not
make the Story Identity candidate canonical.

### 3. Inspect and accept Story Identity

The Story Identity candidate should read as the ratification of the direction
the author chose. The interface should distinguish what will become canonical,
what remains downstream guidance/provenance, and what is unresolved. Only the
explicit Identity acceptance crosses the Identity authority boundary.

### 4. Build and accept Whole-Story Structure

Structure guidance should feel downstream of the accepted Identity and active
Narrative Architecture rather than reverting to interchangeable generic advice.
Working Structure choices remain noncanonical until explicit Structure
acceptance.

After acceptance, the interface should clearly show that the foundation is
complete and make the **next safe action**—normally outlining—more prominent
than secondary exploration/help actions. It must not continue telling the author
to accept a milestone that is already accepted.

### 5. Continue through Chapter 1 planning

Once Story Direction, Story Identity, and Whole-Story Structure are accepted,
the foundation is canonical. The whole-story outline, Chapter 1 plan, and scene
plans remain derived working artifacts until their explicit continuation
acceptance actions are taken.

The Beginner browser should keep one forward action prominent at each boundary:
create/accept outline, create/accept Chapter 1 plan, create/accept scene plans,
then prepare and generate the Chapter 1 candidate.

### 6. Draft, review, revise, and explicitly accept Chapter 1

Chapter drafting creates `chapters/01/draft_vN.md` plus validation evidence.
Those artifacts are candidates, not canon. Review may route to another
noncanonical candidate or to explicit acceptance. Only the existing Chapter
acceptance owner may create `chapters/01/final.md` and update accepted Bible
state.

A prose candidate requires a provider-enabled runtime. No-provider mode can
still complete premise interpretation, Story Discovery, foundation acceptance,
and planning, but it must fail clearly at prose generation rather than invent a
silent fallback. Provider availability is an infrastructure prerequisite; it
does not weaken or replace the Chapter acceptance boundary.

Current local launch examples:

```powershell
auteur open --provider anthropic
auteur open --provider openai
```

API credentials remain external runtime configuration. The browser should make a
missing provider understandable; it must not turn provider configuration into a
second narrative authority or auto-accept generated prose.

---

## CLI / advanced route: establish accepted story direction

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
