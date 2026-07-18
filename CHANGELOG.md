# Changelog


## v0.2.1 (2026-07-18) — Release Integrity and Product Invariants Hardening

### Repository hygiene

- Removed tracked Windows temp/scratch files (Claude Code scratchpad artifacts)
- Removed `examples/canonical_story/temp_lantern_phase_a/` dogfood output
- Removed tracked `.superpowers/` development artifacts
- Updated `.gitignore` with narrow patterns to prevent recurrence
- `uv.lock` retained as intentional package-management lockfile

### Ontology install-safe packaging

- Moved runtime ontology resources into `src/auteur/data/ontology/` package namespace
- `OntologyLoader` uses `importlib.resources` instead of repository-root path traversal
- Ontology loading works from installed wheel, editable install, and source checkout
- Added `pyproject.toml` package-data declarations
- Clear missing-resource error messages

### Publishing integrity

- Accepted Book manuscript content hash verified before any output is produced
- Tampered manuscript blocks all publishing (HTML/EPUB) atomically
- No partial output, snapshot, or run record remains after integrity failure
- No `latest.yaml` pointer is moved on failure

### EPUB3 conformance

- `mimetype` is always the first ZIP entry
- `mimetype` uses `ZIP_STORED` (uncompressed) per EPUB3 spec
- Output hash computed over raw binary bytes (not decoded/re-encoded text)
- Fixed ZIP timestamps (`1980-01-01 00:00:00`) for deterministic archives

### Deterministic output

- Wall-clock dates removed from rendered content (replaced with stable Auteur version string)
- Fixed ZIP timestamps replace runtime `date_time` values
- Identical accepted source + config + version produces byte-identical output
- Tests verify across separate invocations and directories

### Version metadata

- Hardcoded `auteur_version: "0.1.0"` replaced with `importlib.metadata.version("auteur")`
- Package version, `auteur.__version__`, and publishing snapshots share one source
- Binary output hashed with `sha256_binary()` over raw bytes

### Markdown renderer

- `markdown-it-py` declared as a required dependency (no silent fallback to `<p>`-only renderer)

### Status correctness

- Identity display reads current `story_type.genre` schema (not obsolete `genre.primary` nesting)
- Suggested commands are syntactically valid CLI invocations
- No write operations during status collection (confirmed by audit)

### CI hardening

- Python version matrix: 3.11, 3.12, 3.13
- Wheel build + installed-wheel smoke test
- Installed CLI exercises: `--help`, `ontology list`

### Test verification

- 52 existing publishing tests preserved
- New tests: ontology packaging (4), publishing integrity (6), EPUB structure (5),
  determinism (4), version metadata (3), status correctness (8), output hashing (2),
  markdown renderer (1)
- Total: ~85 tests

### Key metrics

- Files changed: ~15 (modified + new)
- Runtime dependencies added: `markdown-it-py>=3.0`

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
