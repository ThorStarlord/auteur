"""Stress scenario C - LLM failure simulation.

Scripts transient ``RetriableError`` storms (the error type ``RetryingClient``
actually catches) and verifies retries-to-success matches the script, the
operation eventually succeeds, and failed attempts leave no partial or corrupt
artifacts. ``RetryingClient`` takes a configurable ``base_delay``; the harness
uses ``base_delay=0.0`` for instant, deterministic backoff, so real sleep cost
is zero and the scenario stays far under the 60s budget.
"""

from __future__ import annotations

from typing import Any

import pytest

from _stress_common import get_scale, run_scenario_c


@pytest.fixture(scope="module")
def scenario_c(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    base = tmp_path_factory.mktemp("stress_c")
    return run_scenario_c(base, get_scale())


@pytest.mark.stress
def test_scenario_c_transient_failures_retried_to_success(
    scenario_c: dict[str, Any],
) -> None:
    checks = scenario_c["checks"]
    assert checks["unit_response_ok"]
    assert checks["unit_attempts_match_script"]


@pytest.mark.stress
def test_scenario_c_pipeline_survives_transient_failures(
    scenario_c: dict[str, Any],
) -> None:
    checks = scenario_c["checks"]
    assert checks["pipeline_accepted"]
    assert checks["pipeline_attempts_match_script"]
    assert checks["pipeline_tokens_match_successful_responses"]


@pytest.mark.stress
def test_scenario_c_failed_attempts_leave_no_corruption(
    scenario_c: dict[str, Any],
) -> None:
    checks = scenario_c["checks"]
    assert checks["draft_intact_not_partial"]
    assert checks["outline_still_parses"]
    assert checks["validation_still_parses"]


@pytest.mark.stress
def test_scenario_c_exhaustion_raises_and_preserves_state(
    scenario_c: dict[str, Any],
) -> None:
    checks = scenario_c["checks"]
    assert checks["exhaustion_raises_retriable"]
    assert checks["exhaustion_attempts_match_script"]
    assert checks["exhaustion_leaves_no_artifacts"]


@pytest.mark.stress
def test_scenario_c_runtime_under_60s(scenario_c: dict[str, Any]) -> None:
    assert scenario_c["checks"]["scenario_runtime_under_60s"]
    metrics = scenario_c["metrics"]
    assert metrics["real_sleep_cost_s"] == 0.0
    assert metrics["total_wall_s"] < 60.0
