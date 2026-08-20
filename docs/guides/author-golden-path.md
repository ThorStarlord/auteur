# Author Golden Path — Guided Journeys

This guide shows the canonical author journeys that prove Auteur's capabilities
form a coherent product. Each journey starts with a narrative problem and reaches
a justified, current, publishable result without requiring knowledge of Auteur's
internal architecture.

## Starting point

```bash
auteur dashboard --project .
```

Shows project overview, current stage, and primary next action.

For an established project, continue with:

```bash
auteur workflow next .
```

For a fresh project with no accepted `story_identity.yaml`, the same workflow
surface now routes into Story Discovery rather than directly generating one
canonical identity.

## New project — discover and choose the story direction

**Problem**: You have a premise or brain dump, but the story's narrative engine
has not been accepted yet.

```bash
# 1. Ask Auteur what to do next
auteur workflow next .

# 2. Tell Auteur what story you are trying to write. This creates/resumes
#    story_discovery/brief.yaml; it does not create canonical story state.
auteur story-discovery start --project .

# 3. Ask again. Once the brief has genre/reader promise, audience, and a
#    governing target experience, workflow routes to intent-aware discovery.
auteur workflow next .

# 4. Run the recommended intent-aware Story Discovery search.
auteur story-discovery run --brief story_discovery/brief.yaml --recommend --output story_discovery --project .

# 5. Review the comparison before deciding
#    story_discovery/comparison.md

# 6. Explicitly accept the direction you choose
auteur story-discovery accept story_discovery/candidate_X.yaml --output story_identity.yaml

# 7. Verify the workflow advances to Structure
auteur workflow next .
```

Authority invariant:

- Guided brief capture is non-canonical and never requires an LLM provider.
- `workflow next --execute` must not answer guided author-intent questions.
- Story Discovery search and recommendation are advisory and non-canonical.
- `workflow next --execute` must not auto-accept a Story Discovery candidate.
- `story_identity.yaml` becomes canonical only when the author explicitly runs
  `story-discovery accept` for the chosen candidate.

### Optional refinement — say more only when you know more

The minimum brief is intentionally small. If you already know more about the
reader experience or narrative architecture you want, refine the same working
brief without creating a second schema:

```bash
auteur story-discovery start --project . --refine
```

Refinement can add secondary/avoided reader experiences, a complete emotional
trajectory, medium or mode, literal hard constraints, and the existing
architecture-preference dimensions. `not sure` leaves an optional preference
UNKNOWN rather than inventing a default.

Writer-facing architecture choices map to the existing canonical vocabulary:

| Writer-facing choice | Canonical value |
| --- | --- |
| focused | `complexity=focused` |
| layered | `complexity=layered` |
| richly interconnected | `complexity=maximalist` |
| one strong cause | `causal_distribution=concentrated` |
| one main cause with meaningful contributors | `causal_distribution=layered` |
| several interacting causes | `causal_distribution=mixed` |
| one clearly dominant engine | `engine_hierarchy=single_center` |
| one main engine with substantial supporting layers | `engine_hierarchy=primary_with_layers` |
| several engines carrying comparable weight | `engine_hierarchy=ensemble` |

To change something you already declared, use the explicit edit mode:

```bash
auteur story-discovery start --project . --edit
```

Edits are saved atomically after each complete answer. Clearing genre, audience,
or the primary reader experience may intentionally make the brief incomplete
again. Because intent-aware Story Discovery compares persisted declared intent
by content, a real edit also makes an older structured recommendation stale.
Nothing becomes canonical until explicit `story-discovery accept`.

## Journey A — Repair a chapter-level structural problem

**Problem**: Your story's structure has a weakness detected by diagnostics.

```bash
# 1. Check what to do next
auteur workflow next --project .

# 2. Run structural diagnostics
auteur structure diagnose blueprint.yaml --project .

# 3. Generate repair proposals
auteur structure propose-repairs blueprint.yaml --project .

# 4. Review proposals (listed in structure/proposals/)
auteur structure propose --list --project .

# 5. Apply a proposal with explicit authority
auteur structure apply <proposal.yaml> blueprint.yaml --in-place

# 6. Verify freshness propagated
auteur workflow next --project .

# 7. Publish current structure
auteur structure publish --project .
```

## Journey B — Resolve interacting narrative decisions

**Problem**: Multiple open decisions interact in ways that affect project planning.

```bash
# 1. Check what to do next
auteur workflow next --project .

# 2. Run simulation to project consequences
auteur simulate create --project .

# 3. Build a portfolio of candidate combinations
auteur portfolio generate --project .

# 4. Compare portfolio options
auteur portfolio combine --project .

# 5. Commit to a direction
auteur commit create --project .

# 6. Accept the commitment with explicit confirmation
auteur commit accept <id> --confirm --project .

# 7. Verify lifecycle advanced
auteur workflow next --project .
```

## Journey C — Improve and publish a scene

**Problem**: A scene exists but has identified weaknesses.

```bash
# 1. Check what to do next
auteur workflow next --project .

# 2. Run book-level scene analysis
auteur reasoning book --project .

# 3. Review reasoning findings
auteur workflow explain --project .

# 4. Revise the scene through the authorized path
# (revision commands depend on the finding type)

# 5. Verify freshness
auteur workflow next --project .

# 6. Publish current scene
auteur scene publish --project .
```

## Quick reference

| Command | Purpose |
|---------|---------|
| `auteur dashboard` | Broad project overview |
| `auteur workflow next` | One authoritative next action |
| `auteur workflow explain` | Why that action is recommended |
| `auteur story-discovery start` | Create or resume the minimum non-canonical guided Discovery Brief |
| `auteur story-discovery start --refine` | Optionally add richer declared intent without inventing unknowns |
| `auteur story-discovery start --edit` | Edit or clear previously declared Story Discovery intent |
| `auteur story-discovery run ... --recommend` | Explore narrative engines and receive an advisory recommendation |
| `auteur story-discovery accept` | Explicitly promote the chosen Story Discovery candidate to canonical identity |
| `auteur structure diagnose` | Detect structural weaknesses |
| `auteur structure propose-repairs` | Generate repair proposals |
| `auteur structure apply` | Apply a proposal with authority |
| `auteur structure publish` | Publish current structure |
| `auteur reasoning book` | Book-level reasoning analysis |
| `auteur scene publish` | Publish current scene state |
| `auteur commit create` | Commit to a decision portfolio |
| `auteur commit accept` | Accept with explicit confirmation |
