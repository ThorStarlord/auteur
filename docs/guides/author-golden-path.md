# Author Golden Path — Guided Journeys

This guide shows three canonical end-to-end author journeys that prove
Auteur's capabilities form a coherent product. Each journey starts with
a narrative problem and reaches a justified, current, publishable result
without requiring knowledge of Auteur's internal architecture.

## Starting point

```bash
auteur dashboard --project .
```

Shows project overview, current stage, and primary next action.

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
| `auteur structure diagnose` | Detect structural weaknesses |
| `auteur structure propose-repairs` | Generate repair proposals |
| `auteur structure apply` | Apply a proposal with authority |
| `auteur structure publish` | Publish current structure |
| `auteur reasoning book` | Book-level reasoning analysis |
| `auteur scene publish` | Publish current scene state |
| `auteur commit create` | Commit to a decision portfolio |
| `auteur commit accept` | Accept with explicit confirmation |
