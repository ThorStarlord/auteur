---
id: 0002
title: Write story_identity.yaml atomically on accept
state: accepted
priority: high
area: Opinionated Story Identity
filed-by: harness-build
opened: 2026-09-05
---

## What happens

`serialize_identity_promote` in `src/auteur/cli_serializers.py` writes the
promoted identity with a single in-place call:

```python
output_path.parent.mkdir(parents=True, exist_ok=True)
identity.to_yaml(output_path)
```

Steps someone can follow:

1. Start an accept of any valid candidate (`story-discovery accept <file>
   --output story_identity.yaml`) in a project that already has a
   `story_identity.yaml` from an earlier acceptance.
2. Kill the process mid-write (or observe: there is no temp file + rename,
   only a direct write).
3. Observe the previous `story_identity.yaml` is truncated or half-written.

The canonical store - the file MISSION.md calls the Layer 1 authority - can
be destroyed by an interrupted write. Every other persistence path in the
repo (`author_decisions/persistence.py`, `simulation/persistence.py`,
`reasoning/draft_review.py`) writes temp-file + `os.replace`. This one does
not.

## What should happen

The promote write is atomic: write to a temp file in the same directory,
`os.replace` into place. A failed or interrupted accept leaves the prior
`story_identity.yaml` byte-identical. Observable: kill the process mid-write
(or inspect the code path) and the previous file survives intact.

## Why it matters

MISSION.md hard invariant 2 ("No author data loss - a failed write never
corrupts or half-destroys the prior state") is unenforced at the single most
important write site in the product.

## Out of scope for this issue

Changing any other persistence path; adding backups or versioning of
story_identity.yaml; touching the validation logic in
`handle_identity_promote` (it correctly gates what gets written - this issue
is only about *how* the accepted bytes land).
