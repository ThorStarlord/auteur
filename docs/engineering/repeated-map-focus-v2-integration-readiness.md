# Repeated Map/Focus V2 — Integration Readiness Note

Status: ready-for-integration-analysis; integration is separately authorized.

This note records the repository facts that establish that integrating the
qualified `feat/repeated-map-focus-v2` branch into `main` is safe, in the
specific sense that it can be performed with a Git-safe procedure that
provably leaves the user's dirty tracked and untracked files untouched.

It does not authorize the integration. The actual integration remains a
separately authorized action.

## Exact identities

```text
branch                    main
exact HEAD (this session) bcd8db2caeed94794969b96ffb12769208680080

feature branch            feat/repeated-map-focus-v2
feature closure HEAD      e29bf2c601e851bc084ed7bc0bfead3275f9d6ca

qualified product candidate
                          2e066108db51ff4b42b41316d5ea5e8d627eef71
```

## Strict fast-forward relationship

`main` is a strict ancestor of the feature branch:

```text
bcd8db2  (main) is an ancestor of e29bf2c (feat/repeated-map-focus-v2)
```

`main..feat/repeated-map-focus-v2` contains exactly 16 commits. Because the
relationship is an ancestor relationship, the feature branch is strictly
fast-forwardable onto `main` with no merges and no history rewriting.

Verified read-only:

```text
git merge-base --is-ancestor main feat/repeated-map-focus-v2
```

## Qualified candidate ancestry

The qualified product candidate `2e06610` is an ancestor of the feature
branch's closure HEAD:

```text
2e066108db51ff4b42b41316d5ea5e8d627eef71 is an ancestor of
e29bf2c601e851bc084ed7bc0bfead3275f9d6ca
```

Verified read-only with `git merge-base --is-ancestor`.

## No overlap with user-dirty tracked files

The feature branch's changed files do not touch any user-dirty tracked file in
the `main` working copy. The user-dirty tracked files are:

```text
.claude/settings.json
CONTEXT.md
README.md
docs/narrative-architecture.md
docs/opinionated-narrative-engine.md
```

The feature branch's complete changed path set is:

```text
docs/acceptance/series-repeated-map-focus-capability-contract-v1.md
docs/engineering/series-repeated-map-focus-qualification-v2.md
docs/handoffs/2026-08-25-repeated-map-focus-v2-closure.md
docs/qualification-evidence/2e066108db51ff4b42b41316d5ea5e8d627eef71.json
src/auteur/series/cli.py
src/auteur/series/repeated_map_focus.py
src/auteur/series/vertical_slice_formatters.py
src/auteur/series/vertical_slice_models.py
src/auteur/series/vertical_slice_service.py
src/auteur/series/vertical_slice_store.py
tests/fixtures/repeated_map_focus_v2/…        (11 fixture files)
tests/test_series_repeated_map_focus.py
tests/test_series_vertical_slice_models.py
tests/test_series_vertical_slice_service.py
```

The two path sets are disjoint. Verified by comparing the feature branch's
`git diff --name-only main feat/repeated-map-focus-v2` output against the
`main` worktree's dirty tracked set.

## No untracked-file collision from the feature branch

The user's existing untracked files (including `.claude/`, `.local/`,
`.reasonix/`, `demo/archive-of-lies-prototype/`, `docs/acceptance/…`,
`docs/adr/019–070`, `docs/design/series-vertical-slice-implementation-boundary-v1.md`,
`docs/domain-model.md`, `reasonix.toml`, and related tool directories) do not
collide with any path the feature branch adds or modifies. No feature-branch
path is currently untracked in the `main` worktree, so no checkout would be
blocked by, or would silently absorb, a pre-existing untracked user file.

## Qualification evidence remains attached to the exact candidate

The qualification evidence file
`docs/qualification-evidence/2e066108db51ff4b42b41316d5ea5e8d627eef71.json`
records `candidate.sha = 2e066108db51ff4b42b41316d5ea5e8d627eef71` and names
itself as the only permitted non-candidate working-change. The file lives on
the feature branch and the candidate is an ancestor of the branch head, so the
evidence remains attached to the exact qualified candidate. The complete source
gate is recorded as 4,477 collected, 4,449 passed, 1 skipped, 27 xfailed,
0 xpassed, 0 failed, 0 errors, with no added or removed failure nodes versus
baseline `d3bb1eb`.

Because the strict fast-forward is the integration path, the candidate bytes
and the evidence bytes are preserved byte-for-byte; no rebuild or re-run is
needed for the integration itself.

## Git-safe integration procedure that proves user files remain untouched

Recommended procedure (not yet authorized to run):

1. Work from the existing `feat/repeated-map-focus-v2` branch (or a fresh
   worktree checked out from that branch) so the dirty `main` working copy is
   never modified in place.
2. Record a pre-integration manifest of every user-dirty tracked file and every
   untracked user file (path + content hash) in the `main` checkout.
3. Fast-forward the branch: since `main` is a strict ancestor, integrate by
   advancing `main` to `e29bf2c` (fresh `git merge --ff-only` on a clean branch
   ref, or equivalent), never by merging into the dirty working copy.
4. Re-run the manifest check against the `main` checkout and confirm every
   user-dirty tracked and untracked file is byte-identical to the pre-integration
   manifest.

This is a Git-safe mechanism: it proves the user's files remain untouched by
comparing content hashes before and after, and it isolates the source mutation
away from the dirty worktree.

## Non-assumption about a second linked worktree

This note does **not** assume that `main` can necessarily be checked out
simultaneously in another linked worktree. If `main` is already checked out in
this dirty working copy, a fresh worktree intent on `main` may be blocked by the
existing checkout. The safe procedure above therefore operates from the feature
branch / a feature worktree and does not require a second `main` checkout.

## Authorization boundary

Actual integration remains separately authorized. Nothing in this note is an
instruction to run the integration. The next separately authorizable action is:

> Boundary 0 — integrate the completed and qualified Repeated Map/Focus V2
> branch into `main` safely.
