"""Bounded Stage 4G regression: detect an omitted mission-level comparison."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from auteur.reasoning.responsibility_frame import ResponsibilityFrame, review_responsibility_frame


OBJECTIVE = {
    "statement": "Develop generative and revisable twelve-Book Narrative Architecture",
    "source_ref": "docs/research/2026-11-07-generative-long-form-narrative-architecture-strategy.md",
    "source_revision": "375d42a2ff83757a05e4dfe2b9cabe5a541e2899",
}


def frame(*, boundary="mission_continuation"):
    return {
        "schema_version": 1,
        "governing_objective": OBJECTIVE,
        "current_question": "What should follow the Stage 4G contact-window stress test?",
        "decision_boundary": boundary,
        "options": [
            {"option_id": "a", "action": "Substantial Book 11 realization", "level": "local",
             "objective_contribution": "Test whether the Book 11 architectural contact is dramatic",
             "decision_value": "If the scene cannot sustain a consequential choice, reconsider its Book function"},
            {"option_id": "b", "action": "Author decision required", "level": "author_decision"},
            {"option_id": "c", "action": "One narrowly justified unresolved prerequisite", "level": "local"},
            {"option_id": "d", "action": "Research conclusion", "level": "close"},
        ],
        "selected_option_id": "a",
        "selection_rationale": "Further navigation micro-probes have diminishing returns versus lived fiction",
        "comparisons": [
            {"alternative_id": "c", "rationale": "Another micro-probe offers less local learning"},
            {"alternative_id": "d", "rationale": "Stopping would not test scene-level promise"},
        ],
    }


def codes(payload):
    result = review_responsibility_frame(ResponsibilityFrame.model_validate(payload))
    return result, {finding.code for finding in result.findings}


def test_stage_4g_local_choice_exposes_missing_mission_alternative():
    result, found = codes(frame())
    assert result.record_status == "decision_warrant_gaps"
    assert found == {"mission_alternative_unrepresented"}
    assert "twelve-Book" in result.mission_reentry_question
    assert result.authority == "derived_not_authorizing"


def test_adding_mission_option_without_comparing_it_is_not_adequate():
    payload = frame()
    payload["options"].append({
        "option_id": "e", "action": "Compare the Series' rival organizations and engine renewal",
        "level": "mission", "objective_contribution": "Directly tests whole-Series generativity",
        "decision_value": "May change the selected architecture",
    })
    result, found = codes(payload)
    assert found == {"mission_alternative_uncompared"}
    assert result.mission_reentry_question is None


def test_explicit_comparison_permits_warranted_local_choice_without_forcing_global():
    payload = frame()
    payload["options"].append({
        "option_id": "e", "action": "Compare whole-Series engines and the alternative organization",
        "level": "mission", "objective_contribution": "Tests cross-horizon narrative differentiation",
        "decision_value": "Could revise Book 7/10 separation",
    })
    payload["comparisons"].append({
        "alternative_id": "e",
        "rationale": "A short scene would discriminate the contact mechanism first; the Series comparison follows if it fails",
    })
    result, found = codes(payload)
    assert result.record_status == "no_declared_gaps"
    assert found == set()
    assert result.selected_option_id == "a"
    # Record completeness is deliberately not an empirical claim about the better choice.


def test_bounded_local_work_requires_no_global_comparison():
    result, found = codes(frame(boundary="bounded_task"))
    assert found == set()
    assert result.record_status == "bounded_task_not_reviewed"


def test_unexplained_selection_is_visible_even_with_mission_comparison():
    payload = frame()
    payload["options"].append({"option_id": "e", "action": "Revisit Series Architecture", "level": "mission"})
    payload["comparisons"].append({"alternative_id": "e", "rationale": "Prose first, then Series review"})
    payload["selection_rationale"] = None
    payload["options"][0]["decision_value"] = None
    _, found = codes(payload)
    assert found == {"selection_rationale_unstated", "selected_decision_value_unstated"}


@pytest.mark.parametrize("mutation", ["duplicate", "invalid_selected", "unknown_compared", "self_comparison"])
def test_frame_rejects_broken_option_references(mutation):
    payload = frame()
    if mutation == "duplicate":
        payload["options"].append({"option_id": "a", "action": "Duplicate", "level": "local"})
    elif mutation == "invalid_selected":
        payload["selected_option_id"] = "missing"
    elif mutation == "unknown_compared":
        payload["comparisons"].append({"alternative_id": "missing", "rationale": "Not listed"})
    else:
        payload["comparisons"].append({"alternative_id": "a", "rationale": "Compare against itself"})
    with pytest.raises(ValidationError):
        ResponsibilityFrame.model_validate(payload)


def test_module_cli_returns_derived_review_without_mutating_input(tmp_path: Path):
    source = tmp_path / "frame.json"
    data = frame()
    source.write_text(json.dumps(data), encoding="utf-8")
    before = source.read_bytes()
    result = subprocess.run(
        [sys.executable, "-m", "auteur.reasoning.responsibility_frame", str(source)],
        check=True, capture_output=True, text=True,
    )
    output = json.loads(result.stdout)
    assert output["record_status"] == "decision_warrant_gaps"
    assert output["findings"][0]["code"] == "mission_alternative_unrepresented"
    assert source.read_bytes() == before
