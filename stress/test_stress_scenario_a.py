"""Stress scenario A - artifact scale.

Builds large valid artifacts offline and exercises the CLI dispatch over them:
whole-story structure diagnostics on a giant blueprint, cartographer outline
compilation with fully scripted planning responses, ``status --json`` over a
large-prose book plus small extra projects, and ``publish`` to HTML.

All assertions are sanity-only (completes, output parses/validates); timing and
memory numbers are recorded, never thresholded.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from _stress_common import REPO_ROOT, get_scale, run_scenario_a


def _dump_metrics(name: str, result: dict[str, Any]) -> None:
    """Best-effort local metrics dump (never fails the test)."""
    try:
        out_dir = REPO_ROOT / "artifacts" / "stress" / "pytest"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    except OSError:
        pass


@pytest.fixture(scope="module")
def scenario_a(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    base = tmp_path_factory.mktemp("stress_a")
    result = run_scenario_a(base, get_scale())
    _dump_metrics("scenario_a", result)
    return result


@pytest.mark.stress
def test_scenario_a_all_checks_pass(scenario_a: dict[str, Any]) -> None:
    failed = {k: v for k, v in scenario_a["checks"].items() if not v}
    assert not failed, f"scenario A failed checks: {failed}"


@pytest.mark.stress
def test_scenario_a_giant_blueprint_diagnosed(
    scenario_a: dict[str, Any],
) -> None:
    checks = scenario_a["checks"]
    assert checks["diagnose_rc0"]
    assert checks["diagnose_report_parses"]
    assert scenario_a["metrics"]["giant_chapters"] >= 12


@pytest.mark.stress
def test_scenario_a_cartographer_compiled_all_chapters(
    scenario_a: dict[str, Any],
) -> None:
    checks = scenario_a["checks"]
    assert checks["compile_unified_parses_with_total"]
    assert checks["compile_split_outline_count"]
    assert checks["compile_consumed_exactly_scripted"]


@pytest.mark.stress
def test_scenario_a_publish_html_valid(scenario_a: dict[str, Any]) -> None:
    checks = scenario_a["checks"]
    assert checks["publish_rc0"]
    assert checks["publish_html_nonempty"]
    assert checks["publish_html_contains_title"]
    assert scenario_a["metrics"]["published_html_bytes"] > 0


@pytest.mark.stress
def test_scenario_a_status_json_valid(scenario_a: dict[str, Any]) -> None:
    checks = scenario_a["checks"]
    assert checks["status_big_book_rc0"]
    assert checks["status_big_book_json_parses"]
    assert checks["status_large_drafts_rc0"]
    assert checks["status_extra_projects_rc0"]


@pytest.mark.stress
def test_scenario_a_timings_recorded(scenario_a: dict[str, Any]) -> None:
    timings = scenario_a["timings"]
    for label in (
        "structure_diagnose",
        "cartographer_compile",
        "build_book_project",
        "publish_html",
        "status_big_book",
    ):
        assert label in timings, f"missing timing for {label}"
        assert timings[label]["wall_s"] >= 0.0
        assert timings[label]["peak_traced_bytes"] >= 0
