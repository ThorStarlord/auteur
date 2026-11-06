"""Continuing creative intentions and adoption lineage across successive revisions.

An adopted alternative is a recorded creative decision. It must stay visible after later, unrelated
revisions, and it becomes a continuing intention only through an explicit author action whose status
(provisional, active, superseded, withdrawn) is readable by a fresh agent.
"""
from __future__ import annotations

import copy
import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, main as architecture_main,
    prepare_architecture, project_architecture, project_architecture_resume,
)
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry,
)

from test_beginner_studio_architecture_inquiry import intent, packet, seeded_store
from test_beginner_studio_architecture_review import response, valid_candidate


def _exploration(store):
    pending = prepare_architecture_inquiry(store, intent(store, operation="explore"))
    complete_architecture_inquiry(store, packet(pending, {
        "schema_version": 1,
        "analysis": "Two different causal engines.",
        "recorded_observations": [],
        "hypotheses": [
            {"title": "Restorative knowledge", "divergence_axis": "causal_engine",
             "description": "Discovery restores shared understanding for the district."},
            {"title": "Consolation without knowledge", "divergence_axis": "reader_emotion",
             "description": "The community keeps comfort instead of the record of the loss."},
        ],
        "uncertainties": [],
    }))
    return pending["request_sha256"]


def _adopt_and_apply(store, inquiry_sha, hypothesis_id, instruction, summary):
    pending = prepare_architecture(
        store, instruction,
        selected_alternative={"inquiry_request_sha256": inquiry_sha, "hypothesis_id": hypothesis_id},
    )
    candidate = copy.deepcopy(valid_candidate())
    candidate["summary"] = summary
    complete_architecture(store, response(pending, candidate))
    apply_architecture_review(store, pending["request"]["request_sha256"])
    return pending["request"]["request_sha256"]


def test_adopted_direction_survives_a_later_unrelated_revision(tmp_path):
    store = seeded_store(tmp_path)
    inquiry_sha = _exploration(store)
    first = _adopt_and_apply(store, inquiry_sha, "h2", "Adopt consolation.",
                             "Consolation keeps wonder alive.")
    assert project_architecture_resume(store)["adopted_creative_alternative"]["title"] == (
        "Consolation without knowledge"
    )

    later = prepare_architecture(store, "Make the dread engine quieter.")
    quieter = copy.deepcopy(valid_candidate())
    quieter["summary"] = "Consolation keeps wonder alive; dread is quieter."
    quieter["nodes"][1]["summary"] = "Quieter threat still turns discovery into danger."
    complete_architecture(store, response(later, quieter))
    apply_architecture_review(store, later["request"]["request_sha256"])

    resumed = project_architecture_resume(store)
    lineage = resumed["creative_adoption_lineage"]
    assert [entry["title"] for entry in lineage] == ["Consolation without knowledge"]
    assert lineage[0]["adopted_in_request_sha256"] == first
    assert lineage[0]["inquiry_request_sha256"] == inquiry_sha
    assert resumed["adopted_creative_alternative"]["title"] == "Consolation without knowledge"


def test_adoption_lineage_lists_every_decision_newest_first(tmp_path):
    store = seeded_store(tmp_path)
    first_inquiry = _exploration(store)
    first = _adopt_and_apply(store, first_inquiry, "h1", "Adopt restoration.",
                             "Discovery restores.")
    # The applied revision is a new baseline, so a second decision requires a fresh inquiry.
    second_inquiry = _exploration(store)
    second = _adopt_and_apply(store, second_inquiry, "h2", "Prefer consolation now.",
                              "Consolation outweighs restoration.")
    lineage = project_architecture_resume(store)["creative_adoption_lineage"]
    assert [(entry["adopted_in_request_sha256"], entry["hypothesis_id"]) for entry in lineage] == [
        (second, "h2"), (first, "h1"),
    ]
    assert [entry["inquiry_request_sha256"] for entry in lineage] == [second_inquiry, first_inquiry]


def test_intention_is_created_by_explicit_author_action_and_recovered_on_resume(tmp_path, capsys):
    store = seeded_store(tmp_path)
    inquiry_sha = _exploration(store)
    directive = tmp_path / "directive.txt"
    directive.write_text(
        "Discovery should become more restorative; keep the wonder-to-dread movement.",
        encoding="utf-8",
    )
    architecture_main([
        "--project", str(tmp_path), "--canvas", "story-one", "keep-intention",
        "--title", "Restorative discovery",
        "--directive-file", str(directive),
        "--status", "active",
        "--from-request", inquiry_sha,
        "--source-ref", "h1",
        "--focus-id", "wonder-engine",
    ])
    created = json.loads(capsys.readouterr().out)
    assert created["status"] == "recorded"
    assert created["intention"]["status"] == "active"
    assert created["intention"]["provenance"]["source_kind"] == "creative_alternative"

    resumed = project_architecture_resume(store)
    assert [(x["title"], x["status"]) for x in resumed["creative_intentions"]] == [
        ("Restorative discovery", "active"),
    ]
    assert resumed["creative_intentions"][0]["directive"].startswith("Discovery should become")


def test_withdrawing_an_intention_keeps_it_visible_as_history(tmp_path, capsys):
    store = seeded_store(tmp_path)
    directive = tmp_path / "directive.txt"
    directive.write_text("Make discovery restorative.", encoding="utf-8")
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "keep-intention",
                       "--id", "restorative", "--title", "Restorative discovery",
                       "--directive-file", str(directive)])
    capsys.readouterr()
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "set-intention-status",
                       "--id", "restorative", "--status", "withdrawn"])
    withdrawn = json.loads(capsys.readouterr().out)
    assert withdrawn["status"] == "withdrawn"

    resumed = project_architecture_resume(store)
    entry = resumed["creative_intentions"][0]
    assert entry["status"] == "withdrawn"
    assert entry["directive"] == "Make discovery restorative."
    assert entry["authority"] == "author_directed_working_intention"


def test_intention_requires_an_author_written_directive(tmp_path):
    store = seeded_store(tmp_path)
    canvas = store.load()
    with pytest.raises(ValueError, match="author-directed directive"):
        store.apply("create-item", expected_revision=canvas.revision, command_id="empty-intention",
                    payload={"item": {"id": "blank", "title": "Blank", "content": "",
                                      "intention_status": "active"},
                             "position": {"x": 10, "y": 10}})


def test_revision_packet_discloses_intentions_and_their_status(tmp_path, capsys):
    store = seeded_store(tmp_path)
    active = tmp_path / "active.txt"
    active.write_text("Discovery should become more restorative.", encoding="utf-8")
    retired = tmp_path / "retired.txt"
    retired.write_text("Discovery should stay purely destructive.", encoding="utf-8")
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "keep-intention",
                       "--id", "restorative", "--title", "Restorative discovery",
                       "--directive-file", str(active)])
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "keep-intention",
                       "--id", "destructive", "--title", "Destructive discovery",
                       "--directive-file", str(retired)])
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "set-intention-status",
                       "--id", "destructive", "--status", "superseded"])
    capsys.readouterr()

    pending = prepare_architecture(store, "Preserve restorative discovery while sharpening the mystery.")
    user = json.loads(pending["request"]["user"])
    intentions = user["working_context"]["creative_intentions"]
    assert {entry["id"]: entry["status"] for entry in intentions} == {
        "restorative": "active", "destructive": "superseded",
    }
    assert all(entry["source_ref"].startswith("canvas/items/") for entry in intentions)
    assert "creative_intentions" in pending["request"]["system"]
    assert "superseded" in pending["request"]["system"]


def test_changing_intention_status_invalidates_a_pending_revision(tmp_path, capsys):
    store = seeded_store(tmp_path)
    directive = tmp_path / "directive.txt"
    directive.write_text("Discovery should become more restorative.", encoding="utf-8")
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "keep-intention",
                       "--id", "restorative", "--title", "Restorative discovery",
                       "--directive-file", str(directive)])
    capsys.readouterr()
    pending = prepare_architecture(store, "Preserve restorative discovery.")
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "set-intention-status",
                       "--id", "restorative", "--status", "withdrawn"])
    capsys.readouterr()
    with pytest.raises(BeginnerConcurrencyError, match="creative intentions changed"):
        complete_architecture(store, response(pending, valid_candidate()))
    assert project_architecture(store)["status"] == "awaiting_host_agent"


def test_intentions_reach_the_mentor_context_with_status(tmp_path, capsys):
    from auteur.beginner.studio_mentor import _context
    from test_beginner_studio_architecture_review import working_store

    store = working_store(tmp_path)
    directive = tmp_path / "directive.txt"
    directive.write_text("Discovery should become more restorative.", encoding="utf-8")
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "keep-intention",
                       "--id", "restorative", "--title", "Restorative discovery",
                       "--directive-file", str(directive)])
    capsys.readouterr()
    # The intention is author source, so the architecture is developed after it to stay current.
    pending = prepare_architecture(store)
    complete_architecture(store, response(pending, valid_candidate()))
    context = _context(store, "wonder-engine", "candidate")["context"]
    assert [(x["id"], x["status"]) for x in context["creative_intentions"]] == [
        ("restorative", "active"),
    ]


def test_recording_an_intention_does_not_invalidate_the_applied_architecture(tmp_path, capsys):
    from auteur.beginner.studio_realization import prepare_realization

    store = seeded_store(tmp_path)
    inquiry_sha = _exploration(store)
    _adopt_and_apply(store, inquiry_sha, "h2", "Adopt consolation.", "Consolation keeps wonder alive.")
    directive = tmp_path / "directive.txt"
    directive.write_text("Keep consolation active while the mystery sharpens.", encoding="utf-8")
    architecture_main(["--project", str(tmp_path), "--canvas", "story-one", "keep-intention",
                       "--id", "consolation", "--title", "Consolation continues",
                       "--directive-file", str(directive)])
    capsys.readouterr()
    assert project_architecture(store)["status"] == "ready"
    realization = prepare_realization(store, ["wonder-engine"])
    assert realization["status"] == "awaiting_host_agent"
