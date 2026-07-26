# Genre Packs Erotic Fiction MVP Acceptance Report

## 1. Executive Summary & Candidate Provenance Lineage

This report documents the verification, qualification, and acceptance of the **Genre Packs MVP — Erotic Fiction Vertical Slice** for Auteur.

* **Base Release**: `v0.35.0`
* **Base Release Commit**: `ef92184727e75b493d920da3c0b1940752713500`
* **Feature Branch**: `feature/genre-packs-erotic-fiction-mvp`
* **Initial Implementation Candidate**: `14f3610f9c61686347e152bdf0baeb607ac14721` (Core domain, CLI, and test suite)
* **Pre-Audit Qualified Candidate**: `311e5b7062c09d2dc3f71fb3af4be788b25c36bb` (Initial audit submission)
* **Audit Repair Commits**:
  - `bad0a453374c052f9cbeaab1e82ffeecb67fa9d8` (In-memory cache eviction & relocation rebind)
  - `fcea3fd2b04ee1f33a8856de09e8996248e0f93c` (CLI subparser collision resolution & custom contract validation routing)
* **Final Merge Candidate**: The descendant commit containing this finalized evidence
* **Pack Schema Version**: `1`
* **Erotic Fiction Pack Version**: `0.1.0`
* **Erotic Fiction Pack Content Hash**: `3b4e6730ef3381df4cf13bc20d7718aa6a7e089aaae3fa492ed656cbdf9c6e39`
* **Qualification Package Version**: `0.36.0` (prevents collision with released `v0.35.0`)
* **Proposed Release**: `v0.36.0` (Genre Packs MVP — Erotic Fiction vertical slice product expansion)

---

## 2. Test Suite & Arithmetic Reconciliation

The test inventory reconciles completely against the v0.35 baseline (3679 tests):

| Suite / Metric | Collected | Passed | Skipped | Xfailed | Xpassed | Failed | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| **v0.35 Baseline Collected** | 3679 | 3651 | 1 | 27 | 0 | 0 | 0 |
| **Genre Pack Domain Tests** (`tests/test_genre_packs_erotic_fiction.py`) | 29 | 29 | 0 | 0 | 0 | 0 | 0 |
| **CLI Genre Pack Tests** (`tests/test_cli_genre_packs.py`) | 5 | 5 | 0 | 0 | 0 | 0 | 0 |
| **Net Test Delta** | +34 | +34 | 0 | 0 | 0 | 0 | 0 |
| **Current Complete Suite Collected** | **3713** | **3685** | **1** | **27** | **0** | **0** | **0** |

* **Arithmetic Verification**: \(3685 + 1 + 27 = 3713\). Net delta is exactly +34 tests (29 in `test_genre_packs_erotic_fiction.py` + 5 in `test_cli_genre_packs.py`). Zero tests were silently deleted or replaced.

---

## 3. Persistence Authority, Isolation & Privacy Contract

1. **Single Project-Local Authority**: When `--project` / `project_dir` is supplied, `load_recommendation` resolves ONLY `<project>/.auteur/genre_recommendations/<rec_id>.json`.
2. **Zero Silent Global Fallback**: If the project-local recommendation artifact is missing or deleted, `load_recommendation` returns `RECOMMENDATION_NOT_FOUND`. It NEVER silently restores, loads, or substitutes recommendation bodies from user-global storage (`~/.auteur/...`).
3. **Corruption Detection**: If the project-local recommendation file is malformed, `load_recommendation` returns `RECOMMENDATION_NOT_FOUND` with explicit corruption error details instead of hiding failure via global cache fallback.
4. **Privacy & Retention Policy**:
   - Recommendation bodies and raw premises live strictly within the project directory (`<project>/.auteur/genre_recommendations/`).
   - Deleting the project folder automatically purges all contained recommendation artifacts.
   - Atomic writes (`_atomic_write_json`) use temporary files unlinked during failure so no abandoned readable recommendation fragments remain.
5. **Relocation & Isolation Compatibility**: Moving or renaming the project directory preserves inspectability because recommendation artifacts reside inside the project root (`<project>/.auteur/genre_recommendations/`).

---

## 4. Installed Wheel Qualification Matrix

Executed outside the source repository using an isolated Python 3.14 virtual environment:

| Requirement / Scenario | Test Execution & Verification | Result |
|---|---|---|
| Package version identity | `auteur.__version__ == "0.36.0"` (Wheel filename `auteur-0.36.0-py3-none-any.whl`) | **PASS** |
| Fresh external installation | `pip install dist/auteur-0.36.0-py3-none-any.whl` into temp venv | **PASS** |
| Import from site-packages | `python -c "import auteur; print(auteur.__file__)"` resolves to `site-packages/auteur` | **PASS** |
| Pack list and inspect | `auteur genre pack list --json` and `auteur genre pack inspect erotic_fiction` | **PASS** |
| Opinionated recommendation | `auteur genre recommend --premise "..." --json` | **PASS** |
| Recommendation durability | Project-local `.auteur/genre_recommendations/<rec_id>.json` written atomically; inspectable across process restarts | **PASS** |
| Single project-local authority | Storage is strictly authoritative; missing local artifact returns NOT_FOUND with zero silent fallback | **PASS** |
| Zero pre-acceptance mutation | `story_identity.yaml` byte-for-byte identical after recommendation | **PASS** |
| Explicit acceptance | `auteur genre recommendation accept <id> --confirm` reconciles Layer 1 Identity | **PASS** |
| Restart persistence | Reload project and verify `StoryIdentity.genre_profile` retains commitment | **PASS** |
| Author override persistence | `auteur genre recommendation override <id> --target ... --replacement ...` | **PASS** |
| Pack version and hash persistence | `primary_pack_version` ("0.1.0") and `pack_content_hash` recorded in `genre_profile` | **PASS** |
| Stale-recommendation refusal | Reconcile with altered content hash raises `RECOMMENDATION_STALE` | **PASS** |
| Genre-aware validation | `auteur genre validate --project ...` | **PASS** |
| Genre-aware diagnosis | `auteur genre diagnose --project ...` | **PASS** |
| Human / JSON semantic parity | Exact semantic parity across recommendation ID, profile, confidence, state, and warnings | **PASS** |

---

## 5. Diagnostic Rule Verification & MVP Limitations

For each of the 4 genre-aware diagnostic rules implemented in `src/auteur/genre_packs/diagnostics.py`:

1. **`genre.erotic_fiction.desire_affects_decisions`**: Lexical proxy evaluating `central_engine.want`. Emits `ERROR`.
2. **`genre.erotic_fiction.intimate_scenes_change_state`**: Structural proxy evaluating scene `state_change` and summary. Emits `WARNING`.
3. **`genre.erotic_fiction.scene_function_diversity`**: Exact matching detecting consecutive repeated `scene_function`. Emits `WARNING`.
4. **`genre.erotic_fiction.resolution_addresses_erotic_arc`**: Structural heuristic evaluating Act 3 resolution scenes. Emits `ERROR`.
