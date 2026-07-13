# Chapter Expression Reconciliation

`expression.reconcile_chapter` compares an external Chapter manuscript with a
known Chapter Expression assembly and creates derived inspection findings and
noncanonical proposals. It does not apply proposals.

```text
External manuscript → inspection report → classified changes → proposals
```

External edits never silently modify canonical Scene Expression, transitions,
Scene Realization, Structure, Identity, Bible/state, or accepted Chapter
assemblies.

## Artifacts

```text
chapters/<chapter>/expression/reconciliation/
├── runs/reconcile_<id>.yaml
├── inspections/inspection_<id>.yaml
├── proposals/proposal_<id>.yaml
├── mappings/mapping_<id>.yaml
└── divergences/divergence_<id>.yaml
```

Runs and reports record the `expression.reconcile_chapter` transformation,
source assembly revision/hash, external manuscript path/hash, marker state,
findings, and resulting proposal IDs. They are derived review artifacts and do
not replace Chapter or Scene manifests.

## Change policy

- Marked Scene wording edit → Scene Expression patch proposal.
- Substantial Scene rewrite → replacement-candidate proposal.
- Marked transition edit → Chapter transition patch proposal.
- Structural or event-changing prose → review-required Realization suggestion.
- Cross-boundary movement → unresolved finding; no automatic patch.
- Unsourced prose → Chapter-local divergence or manual mapping request.
- Marker mutation → strict marker finding or repair proposal.
- Markerless manuscript → unresolved import artifact.
- Section reorder → Structure/order-divergence proposal.
- Section deletion → review-required omission.
- Section duplication → deterministic reconciliation error.

Proposal artifacts record target revision/hash, target section, source assembly,
imported manuscript hash, original/replacement text, transformation version,
and status. Proposal status becomes stale when target, assembly, manuscript, or
ownership dependencies change.

No proposal application or canonical authority change is implemented in this
pilot.

## CLI

```bash
auteur expression reconcile inspect edited.md \
  --against chapter_07:expression_v003 --project PROJECT
auteur expression reconcile propose inspection_<id> --project PROJECT
auteur expression reconcile show inspection_<id> --project PROJECT
auteur expression reconcile show proposal_<id> --project PROJECT
```

Default output emphasizes ownership, change, and recommended actions. `--json`
retains hashes and technical provenance.

## Safety boundaries

Markerless manuscripts preserve the complete external text as unresolved
divergence. The author may restore markers, map sections manually, retain
Chapter-local divergence, create Scene candidates, or discard the import.

Cross-boundary edits preserve every affected section ID and offer manual
mapping, Chapter divergence, replacement candidates, Structure proposals,
Realization proposals, or discard. Automatic Scene merge, split, patch
application, and upstream mutation are excluded.
