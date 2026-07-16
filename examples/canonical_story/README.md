# The Lantern at Low Water

Auteur's canonical demonstration project is a small authored story and living
reference program used to show how narrative artifacts relate to governing
capabilities.

Mara, a ferry keeper, must decide whether to light the river beacon for a boat
carrying the magistrate who condemned her brother.

```text
Story Identity → Blueprint → Chapter Structure → Scene Realization
→ Scene Expression → Chapter Expression → external edit
→ reasoning review → reconciliation → Book Manuscript
```

Derived reports belong under `reasoning/`; proposed transformations belong
under `proposals/`; neither is canonical story content.

Future capability work should answer both “does it work?” and “how does it
behave on The Lantern at Low Water?”

Bootstrap mappings:

- `story_identity.yaml` → native accepted Story Identity;
- `blueprint.md` → native Blueprint adapter in the temporary workspace;
- five `realization.yaml` files → native accepted Scene Realizations under
  `chapters/01/scenes`;
- the five-scene order → native accepted Chapter Structure.

The human-readable Blueprint is not lossless native YAML; the bootstrap keeps
it unchanged and reports that adapter boundary. The bootstrap now creates five
accepted Scene Expressions, one accepted Chapter-owned transition, and an
accepted derived Chapter Expression. The dogfood then runs the marker-preserving
external edit through inspection, proposal, planning, publication, mixed
candidate decisions, accepted-source recomposition, Chapter acceptance, and
`partially_reconciled` completion.

Run the bounded dogfood from the repository root:

```powershell
$env:PYTHONPATH = "."
python scripts/dogfood-canonical-story.py
```

The runner copies this reference into a temporary workspace and reports which
public workflow stages are exercised or still require project-specific
adapters. It also bootstraps a coherent second Chapter in the temporary copy,
composes and accepts a Book Manuscript, verifies Chapter-revision staleness and
recomposition, and exports clean Markdown. It never writes derived artifacts
into this committed directory.

Book external-edit routing is read-only and specified in
`docs/book-reconciliation.md`. Book-owned proposals from routing can then be
planned and published transactionally into durable, unaccepted Book candidates
(with a noncanonical preview and manifest) as specified in
`docs/book-reconciliation-application.md`. Publication is not acceptance: it
creates no accepted Book, Chapter, or upstream mutation, a stale plan publishes
nothing, and a duplicate publication is rejected. Book candidate acceptance and
Book recomposition are not implemented.
