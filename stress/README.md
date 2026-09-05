# Auteur offline stress harness (stress/)

A simulated, fully **offline, deterministic, zero-API-cost** stress harness for
the Auteur CLI/library. No network, no real API calls, no API keys: every LLM
interaction is scripted through `auteur.llm.fake.FakeClient`, randomness is
seeded, and measurements use only the stdlib (`time.perf_counter`,
`tracemalloc`, `subprocess`, `concurrent.futures`).

Stress tests are **opt-in**: a default `pytest` session never runs them.

## Running via pytest

```powershell
# opt in, default scale (full)
$env:AUTEUR_STRESS = "1"
.venv\Scripts\python.exe -m pytest stress -q -p no:cacheprovider

# tiny smoke scale (finishes in seconds)
$env:AUTEUR_STRESS = "1"
$env:AUTEUR_STRESS_SCALE = "smoke"
.venv\Scripts\python.exe -m pytest stress -q -p no:cacheprovider

# default run: everything collected is skipped (or collected none)
.venv\Scripts\python.exe -m pytest stress -q -p no:cacheprovider
```

Environment knobs:

- `AUTEUR_STRESS=1` - execute stress tests (otherwise they are all skipped).
- `AUTEUR_STRESS_SCALE=smoke|full` - workload size (default `full`).

Note: the harness lives in the top-level `stress/` directory, deliberately
outside `tests/`. pytest's default prepend import mode puts a conftest's
directory on `sys.path`, so a `conftest.py` under `tests/` would shadow
`tests/conftest.py` for the plain `import conftest` statements used across the
existing suite (observed as 431 ImportErrors in a full-suite run). Because
`pyproject.toml` sets `testpaths = ["tests"]`, a default `pytest` run never
collects `stress/`. A dedicated `pytest stress` session does not load
`tests/conftest.py` (nor its autouse session-scoped bootstrap fixture), so it
pays no canonical bootstrap cost; the standalone runner below does not use
pytest either.

## Running via the standalone runner

```powershell
.venv\Scripts\python.exe scripts/stress/run_stress.py --scale smoke
```

`--scale` defaults to `AUTEUR_STRESS_SCALE`, then `full`. Exit code is `0` when
every scenario passes. Outputs (also `.json`), plus per-run working directories
with every generated artifact, land under `artifacts/stress/`:

```
artifacts/stress/
  <timestamp>-stress-report.json   # machine-readable report
  <timestamp>-stress-report.md     # human-readable report
  <timestamp>-stress-run/          # generated projects/artifacts per scenario
  pytest/                          # best-effort metrics dumps from pytest runs
```

`artifacts/` is already git-ignored (`.gitignore` line `/artifacts/`), so
reports never need to be committed.

## What each scenario measures

| Scenario | What it does | Recorded metrics |
|---|---|---|
| A - artifact scale | Generates a giant valid blueprint (hundreds of chapters), runs whole-story `structure diagnose` on it, compiles a full cartographer outline with one scripted planning response per chapter, builds a large-prose book (accepted chapter expressions, hundreds of KB/chapter) plus several small extra projects (one with a large `draft_v1.md`/`final.md`), then runs `status --json` and `publish` to HTML. | Wall time + peak `tracemalloc` per operation; file sizes; LLM-call counts. Sanity-only assertions: no hard timing thresholds. |
| B - pipeline at scale | Drives the real `PipelineRunner` end-to-end (plan -> draft -> critique) over a multi-chapter book with a fully scripted `FakeClient` sequence (cartographer + bard + 5 critics per chapter). | Per-chapter wall time, iterations, accepted flags; token-accounting integrity: scripted input/output token sums must equal what the pipeline's counting wrapper reports. |
| C - LLM failure simulation | Scripts `RetriableError` storms - the exact error type `RetryingClient` (src/auteur/llm/retrying.py) catches. `base_delay=0.0` makes backoff instant and deterministic (real sleep cost 0s). Covers: transient failures then success (retries-to-success matches the script), transient failures mid-drafting through the pipeline, and exhaustion (raises, no partial artifacts). | Retries-to-success, attempts vs script, artifact parse checks, total wall time (asserted < 60s as a harness budget, not a flaky threshold). |
| D - concurrency | Launches parallel **real CLI subprocesses** (`.venv\Scripts\auteur.exe`) against one shared project and against distinct projects, plus a serial control pass. | Exit codes, traceback-free stderr, post-run YAML/JSON parse checks on all project artifacts, and serial-vs-parallel `status --json` state consistency. |

## Scenario D command choices and why

- `status --json` - `src/auteur/status.py` is documented read-only ("Read-only,
  never mutates any artifact"), so concurrent invocations against the same
  project cannot race on writes.
- `structure diagnose <blueprint> --output <unique path>` - deterministic
  whole-story diagnostics. A unique `--output` per invocation is required:
  without one the CLI writes `structure/diagnostics/structure_report.json`
  next to the blueprint, which would be a shared concurrent write target.

`status` is therefore used for the read-heavy same-project burst, and both
commands run against the distinct projects with exclusive report paths.

## Reading the report

- `status` per scenario: `passed`, `failed` (some boolean check was false), or
  `error` (unexpected exception; traceback is included).
- `checks` - named boolean assertions, e.g. `input_tokens_match_script`,
  `same_project_no_tracebacks`, `state_consistent_with_serial_control`.
- `metrics` - scenario-specific numbers (retries-to-success, per-chapter rows,
  token sums, concurrency task counts, byte sizes).
- `timings` - `wall_s` and `peak_traced_bytes` per measured operation.
- `machine` - Python version, platform, processor, CPU count, scale, timestamp.

Peak memory is traced with `tracemalloc` for in-process operations (everything
in scenarios A-C); Scenario D spawns subprocesses, whose memory is not
traced in-process (exit codes and artifact integrity are the assertions there).

## Additivity

This directory and `scripts/stress/run_stress.py` are purely additive. The only
shared-config file touched is `.gitignore`, which already ignores `/artifacts/`,
so no change was required for the stress report output.
