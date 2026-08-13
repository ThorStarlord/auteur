# Reasoning Report Output Contract

**Status:** Accepted (2026-08-13, docs-contract-reconciliation)

## Canonical location

Reasoning reports (the JSON artifacts written by `ReasoningRuntime`) are stored
under the **project directory**, never the repository root:

```
<project>/.auteur/reasoning/<report_id>.json
```

The CLI already uses this path (`src/auteur/cli_dispatch.py`, `_handle_reasoning_book`),
and the draft pipeline (`src/auteur/pipeline/runner.py`) resolves it from the
`Project` instance (`project.path / ".auteur" / "reasoning"`).

## Rules

1. **The repo root is never a report target.** No `*.json` derived artifacts may be
   written to the repository root. Root-level JSON files are gitignored by
   `/*.json` only as a *safety net* — not as an approved location. `scripts/validate-repo.py`
   errors if any root-level `*.json` exists.
2. **Callers that know their project pass a project-relative `report_dir`.**
   `_get_reasoning_runtime(..., report_dir=<project>/.auteur/reasoning)`.
3. **Callers without project context default to `.auteur/reasoning` under the
   current working directory** — never `Path()` (the previous default, which wrote
   reports into the repo root during dogfood/test runs and accumulated ~9,576 files).
4. `ReasoningRuntime` creates the directory with `mkdir(parents=True, exist_ok=True)`
   and writes one `<report_id>.json` per execution outcome.

## Rationale

The probe that diagnosed repository drift (`docs/reviews/2026-08-13-auteur-repo-sensemaking-brief.md`)
counted ~9,576 root-level report JSONs. The root cause was a single default:
`report_dir=Path()` in `runner.py` resolves to the process working directory.
`/*.json` in `.gitignore` hid the sprawl instead of preventing it. This contract
closes the gap with a deterministic validator rule.
