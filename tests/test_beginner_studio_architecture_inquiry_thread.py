"""Creative deliberation continuity for read-only architecture inquiries.

Inquiries remain noncanonical and never write a working ArchitectureCandidate. These tests cover
explore differentiation (distinct titles and distinct declared divergence axes), stable alternative IDs,
same-baseline prior exchanges, history projection, lineage across a changed baseline, operation-specific
instructions and the host-agent CLI bridge.
"""
from __future__ import annotations

import json

import pytest

from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture, project_architecture,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry,
    project_architecture_inquiry,
)

from test_beginner_studio_architecture_inquiry import intent, packet, seeded_store
from test_beginner_studio_architecture_review import valid_candidate, response


def _result(hypotheses, analysis="Analysis of the engine.", observations=None):
    return {
        "schema_version": 1,
        "analysis": analysis,
        "recorded_observations": observations or [],
        "hypotheses": hypotheses,
        "uncertainties": ["The candidate does not establish either effect."],
    }


def _hypothesis(title, axis, description="A distinct causal mechanism."):
    return {"title": title, "description": description, "divergence_axis": axis}


def _pair():
    return [
        _hypothesis("Restorative knowledge", "causal_engine"),
        _hypothesis("Consolation without knowledge", "reader_emotion"),
    ]


def _supersede_baseline(store):
    canvas = store.load()
    vision = next(item for item in canvas.items if item.id == "story-vision").model_dump(mode="json")
    vision["content"] += " The author now wants the cost to fall on a community."
    store.apply("update-item", expected_revision=canvas.revision,
                command_id="supersede-vision", payload={"item": vision})
    replacement = prepare_architecture(store)
    changed = valid_candidate()
    changed["summary"] = "A different governing summary."
    complete_architecture(store, response(replacement, changed))


def test_explore_requires_at_least_two_alternatives(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    single = _result([_hypothesis("Only alternative", "structure")])
    with pytest.raises(ValueError, match="at least two"):
        complete_architecture_inquiry(store, packet(pending, single))
    assert project_architecture_inquiry(store)["status"] == "awaiting_host_agent"


def test_explore_rejects_relabelled_duplicate_alternatives(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    duplicate = _result([
        _hypothesis("Restorative knowledge", "causal_engine"),
        _hypothesis("  restorative KNOWLEDGE  ", "causal_engine", "The same mechanism with different words."),
    ])
    with pytest.raises(ValueError, match="distinct"):
        complete_architecture_inquiry(store, packet(pending, duplicate))
    assert project_architecture_inquiry(store)["status"] == "awaiting_host_agent"


def test_explore_rejects_alternatives_that_change_the_same_causal_variable(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    same_dial = _result([
        _hypothesis("Communal ledger", "social_scale"),
        _hypothesis("Delegated cost", "social_scale"),
    ])
    with pytest.raises(ValueError, match="distinct divergence_axis"):
        complete_architecture_inquiry(store, packet(pending, same_dial))
    assert project_architecture_inquiry(store)["status"] == "awaiting_host_agent"


def test_explore_requires_each_alternative_to_declare_its_divergence_axis(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    undeclared = _result([
        {"title": "Restorative knowledge", "description": "A distinct causal mechanism."},
        _hypothesis("Consolation without knowledge", "reader_emotion"),
    ])
    with pytest.raises(ValueError, match="distinct divergence_axis"):
        complete_architecture_inquiry(store, packet(pending, undeclared))


def test_explain_still_completes_without_alternatives(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store, operation="explain"))
    completed = complete_architecture_inquiry(store, packet(pending, _result([])))
    assert completed["status"] == "ready"
    assert completed["result"]["hypotheses"] == []


def test_completed_alternatives_receive_stable_server_ids_and_keep_their_axis(tmp_path):
    store = seeded_store(tmp_path)
    pending = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    completed = complete_architecture_inquiry(store, packet(pending, _result(_pair())))
    assert [h["id"] for h in completed["result"]["hypotheses"]] == ["h1", "h2"]
    assert completed["result"]["hypotheses"][1]["divergence_axis"] == "reader_emotion"


def test_next_request_carries_prior_exchange_for_the_same_baseline(tmp_path):
    store = seeded_store(tmp_path)
    first = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    complete_architecture_inquiry(store, packet(first, _result(_pair())))
    follow = intent(store, operation="explore")
    follow["author_text"] = "Develop the second alternative against the wonder engine."
    second = prepare_architecture_inquiry(store, follow)
    user = json.loads(second["request"]["user"])
    prior = user["prior_exchanges"]
    assert len(prior) == 1
    assert prior[0]["author_question"] == "What other narratives could this engine support?"
    assert [h["id"] for h in prior[0]["hypotheses"]] == ["h1", "h2"]
    assert prior[0]["hypotheses"][1]["title"] == "Consolation without knowledge"
    assert user["author_question"] == follow["author_text"]


def test_prior_exchanges_do_not_leak_across_a_changed_baseline(tmp_path):
    store = seeded_store(tmp_path)
    first = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    complete_architecture_inquiry(store, packet(first, _result(_pair())))
    _supersede_baseline(store)
    follow = prepare_architecture_inquiry(store, intent(store, operation="explain"))
    assert json.loads(follow["request"]["user"])["prior_exchanges"] == []


def test_superseded_exchanges_remain_lineage_not_current_history(tmp_path):
    store = seeded_store(tmp_path)
    first = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    complete_architecture_inquiry(store, packet(first, _result(_pair())))
    _supersede_baseline(store)
    projection = project_architecture_inquiry(store)
    assert projection["history"] == []
    from auteur.beginner.studio_architecture_inquiry import superseded_history
    lineage = superseded_history(store, project_architecture(store)["candidate_request_sha256"])
    assert lineage[0]["hypotheses"][1]["id"] == "h2"
    assert lineage[0]["baseline_candidate_request_sha256"] != project_architecture(store)["candidate_request_sha256"]


def test_projection_lists_completed_exchanges_for_current_baseline_newest_first(tmp_path):
    store = seeded_store(tmp_path)
    first = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    complete_architecture_inquiry(store, packet(first, _result(_pair())))
    second_intent = intent(store, operation="challenge")
    second_intent["author_text"] = "Where is this engine weakest?"
    second = prepare_architecture_inquiry(store, second_intent)
    complete_architecture_inquiry(store, packet(second, _result([])))
    history = project_architecture_inquiry(store)["history"]
    assert [entry["operation"] for entry in history] == ["challenge", "explore"]
    assert history[0]["author_question"] == "Where is this engine weakest?"
    assert history[1]["hypotheses"][0]["id"] == "h1"


def test_operation_specific_instructions_differentiate_creative_operations(tmp_path):
    store = seeded_store(tmp_path)
    explain = prepare_architecture_inquiry(store, intent(store, operation="explain"))["request"]
    explore = prepare_architecture_inquiry(store, intent(store, operation="explore"))["request"]
    challenge = prepare_architecture_inquiry(store, intent(store, operation="challenge"))["request"]
    assert explain["system"] != explore["system"] != challenge["system"]
    assert "distinct" in explore["system"].lower() and "alternative" in explore["system"].lower()
    assert "divergence_axis" in explore["system"]
    assert "weakest" in challenge["system"].lower()


def test_inquiry_cli_prepares_shows_and_completes_without_http(tmp_path, capsys):
    from auteur.beginner.studio_architecture_inquiry import main as inquiry_main

    seeded_store(tmp_path)
    question = tmp_path / "question.txt"
    question.write_text("What other narratives could this engine support?", encoding="utf-8")
    inquiry_main([
        "--project", str(tmp_path), "--canvas", "story-one", "prepare",
        "--op", "explore", "--anchor", "node:wonder-engine", "--text-file", str(question),
    ])
    prepared = json.loads(capsys.readouterr().out)
    assert prepared["status"] == "awaiting_host_agent"
    answer = tmp_path / "answer.json"
    answer.write_text(json.dumps(_result(_pair())), encoding="utf-8")
    inquiry_main(["--project", str(tmp_path), "--canvas", "story-one", "complete-file",
                  "--response-file", str(answer)])
    completed = json.loads(capsys.readouterr().out)
    assert completed["status"] == "ready"
    assert completed["result"]["hypotheses"][0]["id"] == "h1"
    inquiry_main(["--project", str(tmp_path), "--canvas", "story-one", "show"])
    assert json.loads(capsys.readouterr().out)["status"] == "ready"
