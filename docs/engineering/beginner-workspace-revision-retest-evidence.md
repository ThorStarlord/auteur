# Beginner Workspace revision retest evidence

- Candidate: `33a1402731ae271cf1dffe57cc48092e828ba43`
- Workspace: `sealed-elevator-human-02243`
- Scope: revision-only browser retest
- Human usability status: **pending**

## Checkpoints

1. **Open revision** — passed. The workspace entered Discover and identified the active revision target.
2. **Exploratory change** — passed. The selected option was labeled exploratory; canonical state remained unchanged; downstream stages were shown at risk.
3. **Cancel revision** — passed. The overlay disappeared and the original accepted choice remained selected.
4. **Initial accept-revised attempt** — blocked. The reused workspace contained materially stale assumptions, so acceptance was correctly blocked pending guidance reassessment.
5. **Accept revised Story Direction after reassessment** — passed. The revised direction became accepted, the revision ended, and downstream Story Identity / Structure became stale and required reassessment.

## Narrow usability finding

The Story Map previously rendered both historical Story Direction references as
current milestones. The projection now exposes only the latest accepted
revision per milestone, while the session envelope continues to preserve the
append-only acceptance history for provenance.

Expected invariant:

- persistent `accepted_milestones`: both Story Direction revisions remain;
- `WorkspaceProjection.canonical_refs`: only the latest Story Direction revision;
- browser Story Map: Story Direction appears once.

The corresponding browser captures were displayed inline during the retest and
the browser tab was marked deliverable. No PNG files were persisted because the
browser capture surface exposes images to the task UI but does not provide a
filesystem export operation.
