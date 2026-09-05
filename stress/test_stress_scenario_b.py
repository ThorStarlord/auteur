"""Stress scenario B - pipeline at scale.

Drives the real ``PipelineRunner`` end-to-end (plan -> draft -> critique) over
a multi-chapter book with a ``FakeClient`` carrying a fully scripted, valid
response sequence. Verifies token accounting integrity: the sum of scripted
input/output tokens must equal what the pipeline's counting wrapper reports.

No deviation: the full plan -> draft -> critique loop is scripted and executed.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from _stress_common import get_scale, run_scenario_b


@pytest.fixture(scope="module")
def scenario_b(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    base = tmp_path_factory.mktemp("stress_b")
    return run_scenario_b(base, get_scale())


@pytest.mark.stress
def test_scenario_b_all_chapters_accepted(scenario_b: dict[str, Any]) -> None:
    metrics = scenario_b["metrics"]
    assert metrics["chapters"] >= 2
    assert all(entry["accepted"] for entry in metrics["per_chapter"])
    assert scenario_b["checks"]["finals_written_for_every_chapter"]


@pytest.mark.stress
def test_scenario_b_token_accounting_integrity(
    scenario_b: dict[str, Any],
) -> None:
    metrics = scenario_b["metrics"]
    assert scenario_b["checks"]["call_count_matches_script"], (
        f"consumed {metrics['client_calls']} responses, "
        f"scripted {metrics['scripted_responses']}"
    )
    assert scenario_b["checks"]["input_tokens_match_script"], (
        f"counted {metrics['counted_input_tokens']} input tokens, "
        f"scripted {metrics['expected_input_tokens']}"
    )
    assert scenario_b["checks"]["output_tokens_match_script"], (
        f"counted {metrics['counted_output_tokens']} output tokens, "
        f"scripted {metrics['expected_output_tokens']}"
    )


@pytest.mark.stress
def test_scenario_b_per_chapter_times_reported(
    scenario_b: dict[str, Any],
) -> None:
    per_chapter = scenario_b["metrics"]["per_chapter"]
    assert per_chapter
    for entry in per_chapter:
        assert entry["wall_s"] >= 0.0
        assert entry["iterations"] >= 1
        assert entry["input_tokens"] >= 0
        assert entry["output_tokens"] >= 0


@pytest.mark.stress
def test_scenario_b_report_dumped(
    scenario_b: dict[str, Any], tmp_path_factory: pytest.TempPathFactory
) -> None:
    """The metrics dict must be JSON-serializable for the stress report."""
    payload = json.dumps(scenario_b["metrics"], default=str)
    assert isinstance(payload, str)
