# Read-only reconciliation application planning

Planning validates selected reconciliation proposals and persists only a
derived application-set plan. It never changes proposal status or creates,
publishes, accepts, recomposes, or mutates any narrative artifact.

Supported types are Scene Expression patches, Scene Expression replacement
candidates, and Chapter transition patches. Freshness checks cover target
existence/revision/hash, source Chapter assembly revision/hash, imported
manuscript hash, transition revision/hash, applicable proposal status, and the
supported transformation contract. Conflicts include duplicate selection,
overlapping Scene targets, Scene patch/replacement collisions, duplicate
transition targets, and mismatched assemblies or manuscripts.

Plans are stored at `chapters/<chapter>/expression/reconciliation/plans/` and
contain `application_set_id`, source inspection/assembly, proposal IDs,
`planned` status, readiness, targets, conflicts, freshness results, planned
outputs, and a noncanonical `application_preview`.

Scene and transition outputs are symmetric planned candidates requiring later
explicit acceptance. Canonical Chapter composition uses accepted sources only.

```bash
auteur expression reconcile plan --inspection <inspection-id> \
  --select <proposal-id>,<proposal-id> --project PROJECT
auteur expression reconcile show-plan <application-set-id> --project PROJECT
```

There is intentionally no `apply` command in this slice.
