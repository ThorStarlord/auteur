"""Stress scenario D - concurrency.

Launches parallel real CLI subprocesses (the editable-install launcher
``.venv\\Scripts\\auteur.exe``) in two bursts:

1. several concurrent invocations against the SAME project;
2. concurrent invocations against distinct projects.

Command choices (safe to repeat, see README):

- ``status --json`` - documented read-only in ``src/auteur/status.py``
  ("Read-only, never mutates any artifact"), so concurrent reads of one
  project cannot race on writes.
- ``structure diagnose <blueprint> --output <unique path>`` - deterministic
  diagnostics; a unique ``--output`` per invocation is required because the
  default report destination (``structure/diagnostics/structure_report.json``)
  would be a shared write target.

Assertions: sane exit codes, no unhandled tracebacks on stderr, all project
artifacts still parse afterwards, and a serial control run's ``status --json``
state matches the post-parallel state.
"""

from __future__ import annotations

from typing import Any

import pytest

from _stress_common import get_scale, run_scenario_d


@pytest.fixture(scope="module")
def scenario_d(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    base = tmp_path_factory.mktemp("stress_d")
    return run_scenario_d(base, get_scale())


@pytest.mark.stress
def test_scenario_d_parallel_same_project_sane(scenario_d: dict[str, Any]) -> None:
    checks = scenario_d["checks"]
    assert scenario_d["metrics"]["same_project_tasks"] >= 2
    assert checks["same_project_all_rc0"]
    assert checks["same_project_no_tracebacks"]
    assert checks["same_project_no_timeouts"]


@pytest.mark.stress
def test_scenario_d_parallel_distinct_projects_sane(
    scenario_d: dict[str, Any],
) -> None:
    checks = scenario_d["checks"]
    assert scenario_d["metrics"]["distinct_project_tasks"] >= 2
    assert checks["distinct_projects_all_rc0"]
    assert checks["distinct_projects_no_tracebacks"]
    assert checks["distinct_projects_no_timeouts"]


@pytest.mark.stress
def test_scenario_d_artifacts_intact_after_parallel(
    scenario_d: dict[str, Any],
) -> None:
    checks = scenario_d["checks"]
    assert checks["post_blueprint_yaml_parses"]
    assert checks["post_project_metadata_parses"]
    assert checks["post_bible_json_parses"]
    assert checks["post_chapter_outlines_parse"]


@pytest.mark.stress
def test_scenario_d_state_consistent_with_serial_control(
    scenario_d: dict[str, Any],
) -> None:
    checks = scenario_d["checks"]
    assert checks["serial_status_json_parses"]
    assert checks["state_consistent_with_serial_control"]


@pytest.mark.stress
def test_scenario_d_diagnose_reports_parse(scenario_d: dict[str, Any]) -> None:
    checks = scenario_d["checks"]
    assert checks["serial_diagnose_report_parses"]
    assert checks["same_project_reports_parse"]
