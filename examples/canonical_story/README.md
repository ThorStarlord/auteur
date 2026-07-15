# The Lantern at Low Water

Auteur's canonical demonstration project is a small authored story and living
reference program used to show how narrative artifacts relate to governing
capabilities.

Mara, a ferry keeper, must decide whether to light the river beacon for a boat
carrying the magistrate who condemned her brother.

```text
Story Identity → Blueprint → Chapter Structure → Scene Realization
→ Scene Expression → Chapter Expression → external edit
→ reasoning review → reconciliation
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
it unchanged and reports that adapter boundary. Scene Expressions, Chapter
Expression, transitions, reconciliation, publication, decisions, and Chapter
acceptance remain untraversed.

Run the bounded dogfood from the repository root:

```powershell
$env:PYTHONPATH = "."
python scripts/dogfood-canonical-story.py
```

The runner copies this reference into a temporary workspace and reports which
public workflow stages are exercised or still require project-specific
adapters. It never writes derived artifacts into this committed directory.
