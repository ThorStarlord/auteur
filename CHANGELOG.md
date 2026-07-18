# Changelog

## v0.2.0 (2026-07-18) — Auteur v1.1 Product Readiness

### Major features

- **auteur publish** — Immutable HTML/EPUB rendering pipeline. Accepts a
  canonical Book expression and produces distributable artifacts with zero
  Auteur internal markers, no new dependencies (stdlib EPUB3 via zipfile +
  ElementTree), deterministic output bytes, and an immutable publishing
  snapshot model.
  - `PublishingSnapshot` captures accepted Book state (content-addressed,
    written-once snapshot ID)
  - HTML renderer: title page, table of contents, default CSS, custom CSS
    support
  - EPUB3 renderer: valid EPUB archive (XHTML chapters, OPF manifest, nav
    document, stylesheet, mimetype-first ordering, forward-slash paths)
  - Snapshot model separates publication identity (`pub_<id>.yaml`, immutable)
    from run records (`runs/run_<ts>.yaml`, each invocation) with a
    `latest.yaml` convenience pointer
  - CLI: `auteur publish --format html|epub --output <path>`

- **auteur status** — Author workspace primitive (like `git status` for a
  novel). Aggregates identity, blueprint, structure, chapter, book, and
  reconciliation health into a single view with stale-item detection,
  blockers, and recommended next command. Supports `--json` and `--verbose`.

- **Book reconciliation (Phases A–C4, 300+ tests)** — Complete provenance-rich
  workflow: candidate publication, decisions (accept/reject/defer), pointer-based
  recomposition, deterministic comparison, 20-point acceptance gate, and
  reconciliation completion. Source-of-truth authority model with three
  decoupled tiers.

### Infrastructure

- **Schema versioning** — `Project.init()` writes `.auteur/project.yaml` with
  `schema_version`; `Project.load()` validates and warns on mismatch.
- **Dead code removal** — 3 stale genre CLI adapters removed, ~107 lines of
  legacy handler branches removed, 2 dead test files deleted, 5 misplaced test
  files moved from `src/` to `tests/`.
- **Quality infrastructure** — Ruff config (E/F/W selects), coverage config,
  pytest `--tb=short`, `.pre-commit-config.yaml` (ruff auto-fix + format).
- **Shared bootstrap cache** — Session-scoped `CanonicalStoryBootstrap` cache
  with `pytest-xdist` support, reducing per-test-file setup from ~6s to
  sub-second.

### Test verification

- 52 publishing pipeline tests (30 unit + 22 release qualification)
- Deterministic HTML/EPUB byte verification
- EPUB3 conformance (mimetype ordering, forward slashes, OPF metadata, spine,
  navigation)
- Unicode handling, output-path collision, stale/missing book handling
- Manuscript tampering detection, cross-format consistency
- CLI parser and module packaging verification

### Key metrics

- 3 commits in this release stage (7413af6, 85a6593, 3b4a0a6)
- +1,290 lines, -457 lines across all v1.1 work
- 0 new runtime dependencies added
