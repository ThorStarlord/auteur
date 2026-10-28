"""Mechanical S2 exercise-driver contracts; fake candidates are NOT host-agent evidence."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    complete_architecture, project_architecture,
)
from auteur.beginner.studio_realization import (
    complete_realization, project_realization,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

PROBE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "probe_s2_manuscript_host_agent.py"
)
MODULE_SPEC = importlib.util.spec_from_file_location("s2_fixture_driver", PROBE_PATH)
assert MODULE_SPEC and MODULE_SPEC.loader
probe = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(probe)


def _respond(pending, candidate: dict) -> dict:
    """A deterministic structural fake. Never count this as a real coding-agent run."""
    request = HostAgentRequest(**pending["request"])
    return build_host_agent_response(
        request, json.dumps(candidate),
        runtime="mechanical-fixture-test", model="UNAVAILABLE",
    ).model_dump()


def _architecture_candidate() -> dict:
    return {
        "schema_version": 2,
        "summary": "A provisional engine of conflicting testimony, not accepted fact.",
        "nodes": [
            {
                "id": "evidence_pressure", "title": "Competing testimony",
                "category": "engine",
                "summary": "Unverified accounts create pressure to investigate.",
            }
        ],
        "links": [], "phases": [], "open_questions": [
            "Whose first-bell account can be trusted?"
        ],
    }


def _realization_candidate() -> dict:
    return {
        "schema_version": 1,
        "summary": "A working scene choice, not canon.",
        "elements": [
            {
                "id": "witness_scene", "kind": "scene",
                "title": "Evidence remains unsettled",
                "description": "A provisional scene tests conflicting bell testimony.",
                "architecture_refs": ["evidence_pressure"],
            }
        ],
        "links": [], "architecture_feedback": [], "open_questions": [],
    }


def test_s2_fixture_stages_exact_frozen_manuscript_without_correction(tmp_path):
    root = tmp_path / "scratch-manuscript"
    staged = probe.stage(root, "manuscript-one", mode="manuscript")
    store = CanvasStore(root, "manuscript-one")
    request = project_architecture(store)["request"]
    user = json.loads(request["user"])
    context = user["working_context"]

    assert staged["stage"] == "architecture_request_staged_not_executed"
    assert staged["original_prose_unchanged"] is True
    assert staged["unexpected_accepted_story_artifacts"] == []
    assert staged["correction_visible_to_agent"] is False
    assert not (root / probe.CORRECTION_RELATIVE).exists()
    assert staged["request_sha256"] == request["request_sha256"]
    assert Path(staged["request_path"]).is_file()
    assert context["working_source_format"] == 2
    assert context["vision"] == ""
    assert context["omitted_working_item_count"] == 0
    assert [item["id"] for item in context["working_items"]] == [
        "s2-p1", "s2-p2", "s2-p3", "s2-p4"
    ]
    assert all(item["content_is_excerpt"] is False for item in context["working_items"])
    assert all(item["content_characters"] == len(item["content"])
               for item in context["working_items"])
    assert "Mara did not start or arrange the fire" not in request["user"]
    assert all(entry["unchanged"] for entry in probe.audit(root, "manuscript-one")["source_items"])
    assert not (root / "story_identity.yaml").exists()

    with pytest.raises(ValueError, match="NEW or EMPTY disposable"):
        probe.stage(root, "another-canvas", mode="manuscript")


def test_stress_packet_marks_hidden_tail_and_item_25(tmp_path):
    root = tmp_path / "scratch-stress"
    stage = probe.stage(root, "stress-one", mode="stress")
    store = CanvasStore(root, "stress-one")
    req = project_architecture(store)["request"]
    source = json.loads(req["user"])["working_context"]

    assert stage["visible_item_count"] == 24
    assert stage["omitted_working_item_count"] == 1
    assert len(source["omitted_working_items_sha256"]) == 64
    assert source["working_items"][0]["content_is_excerpt"] is True
    assert source["working_items"][0]["content_characters"] > 1000
    assert len(source["working_items"][0]["content"]) == 1000
    assert len(source["working_items"][0]["full_content_sha256"]) == 64
    assert "s2-stress-25" not in req["user"]

    # Same-length changes outside the visible excerpt must invalidate the request.
    before = store.load()
    first = next(item for item in before.items if item.id == "s2-stress-01")
    new_text = first.content[:-1] + ("X" if first.content[-1] != "X" else "Y")
    store.apply(
        "update-item", expected_revision=before.revision,
        command_id="mutate-hidden-tail", payload={
            "item": first.model_copy(update={"content": new_text}).model_dump(mode="json")
        },
    )
    with pytest.raises(BeginnerConcurrencyError, match="source vision or working story changed"):
        complete_architecture(
            store, _respond({"request": req}, _architecture_candidate()),
        )
    assert project_architecture(store)["candidate"] is None


def test_c1_is_delayed_and_working_review_can_reach_realization(tmp_path):
    root = tmp_path / "scratch-correction"
    probe.stage(root, "correct-one", mode="manuscript")
    store = CanvasStore(root, "correct-one")
    first = project_architecture(store)
    with pytest.raises(ValueError, match="complete the first Architecture"):
        probe.correct(root, "correct-one")
    assert all(item.id != probe.CORRECTION_ID for item in store.load().items)

    # Mechanical candidate only; this does not simulate real literary reasoning.
    ready = complete_architecture(store, _respond(first, _architecture_candidate()))
    assert ready["status"] == "ready"

    correction = probe.correct(root, "correct-one")
    pending = project_architecture(store)
    assert correction["stage"] == "architecture_revision_staged_not_executed"
    assert pending["status"] == "awaiting_host_agent"
    assert correction["correction_visible_to_agent"] is True
    assert correction["original_prose_unchanged"] is True
    correction_file = Path(correction["correction_file"])
    assert correction_file.is_file()
    frozen = json.loads(correction_file.read_text(encoding="utf-8"))
    assert frozen["item_id"] == probe.CORRECTION_ID
    assert frozen["content"] == probe.CORRECTION
    assert frozen["sha256"] == correction["correction_sha256"]
    revised = json.loads(pending["request"]["user"])
    assert revised["working_context"]["working_source_format"] == 2
    assert probe.CORRECTION_ID in [
        item["id"] for item in revised["working_context"]["working_items"]
    ]
    assert probe.CORRECTION_INSTRUCTION == revised["revision_instruction"]
    assert "temporary shelter" in pending["request"]["user"]

    finished = complete_architecture(store, _respond(pending, _architecture_candidate()))
    assert finished["status"] == "review_ready"
    assert project_architecture(store)["review"] is not None
    reviewed = probe.apply_working_review(root, "correct-one")
    assert reviewed["architecture_status"] == "ready"
    assert reviewed["original_prose_unchanged"] is True

    stage = probe.prepare_concrete(root, "correct-one", "evidence_pressure")
    assert stage["stage"] == "realization_request_staged_not_executed"
    assert stage["focus_id"] == "evidence_pressure"
    prepared_realization = project_realization(store)
    assert prepared_realization["status"] == "awaiting_host_agent"
    assert json.loads(prepared_realization["request"]["user"])["source"]["focus_ids"] == [
        "evidence_pressure"
    ]
    concrete = complete_realization(
        store, _respond(prepared_realization, _realization_candidate())
    )
    assert concrete["status"] == "ready"
    audit = probe.audit(root, "correct-one")
    assert audit["original_prose_unchanged"] is True
    assert audit["unexpected_accepted_story_artifacts"] == []
    assert audit["correction_matches_fixture"] is True
    assert audit["correction_file_present"] is True
    assert audit["realization_status"] == "ready"
    assert audit["host_model_execution"] == "not_attested_by_fixture_driver"


def test_correction_never_mutates_original_source_and_rejects_bad_mode(tmp_path):
    stress_root = tmp_path / "stress"
    probe.stage(stress_root, "stress", mode="stress")
    with pytest.raises(ValueError, match="four-paragraph fixture"):
        probe.correct(stress_root, "stress")

    root = tmp_path / "original"
    probe.stage(root, "original", mode="manuscript")
    store = CanvasStore(root, "original")
    before = store.load()
    original = next(item for item in before.items if item.id == "s2-p3")
    store.apply(
        "update-item", expected_revision=before.revision, command_id="rewrite-source",
        payload={
            "item": original.model_copy(
                update={"content": original.content + " Extra story."}
            ).model_dump(mode="json"),
        },
    )
    with pytest.raises(ValueError, match="source or accepted-story invariant"):
        probe.correct(root, "original")
    result = probe.audit(root, "original")
    assert result["original_prose_unchanged"] is False


def test_staged_correction_hash_mismatch_rejects_before_working_mutation(tmp_path):
    root = tmp_path / "correction-version-drift"
    probe.stage(root, "drift-one", mode="manuscript")
    manifest_path = root / probe.MANIFEST_RELATIVE
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["correction_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="correction source changed"):
        probe.correct(root, "drift-one")
    assert all(
        item.id != probe.CORRECTION_ID
        for item in CanvasStore(root, "drift-one").load().items
    )
    assert not (root / probe.CORRECTION_RELATIVE).exists()


def test_frozen_correction_tampering_blocks_working_review(tmp_path):
    root = tmp_path / "correction-evidence"
    probe.stage(root, "evidence-one", mode="manuscript")
    store = CanvasStore(root, "evidence-one")
    first = project_architecture(store)
    complete_architecture(store, _respond(first, _architecture_candidate()))
    correction = probe.correct(root, "evidence-one")
    revision = project_architecture(store)
    assert complete_architecture(
        store, _respond(revision, _architecture_candidate())
    )["status"] == "review_ready"

    # The working note alone is not sufficient: the delayed frozen C1 receipt
    # is an independent input integrity boundary, not a source of new canon.
    path = Path(correction["correction_file"])
    frozen = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(
        json.dumps({**frozen, "content": "a substituted author direction"}),
        encoding="utf-8",
    )
    audit = probe.audit(root, "evidence-one")
    assert audit["original_prose_unchanged"] is True
    assert audit["correction_matches_fixture"] is False
    with pytest.raises(ValueError, match="frozen author correction"):
        probe.apply_working_review(root, "evidence-one")
    assert project_architecture(store)["status"] == "review_ready"
    assert not (root / "story_identity.yaml").exists()

    # Restore only the scratch correction record, then apply WORKING review.
    path.write_text(json.dumps(frozen), encoding="utf-8")
    applied = probe.apply_working_review(root, "evidence-one")
    assert applied["architecture_status"] == "ready"
    assert probe.audit(root, "evidence-one")["correction_matches_fixture"] is True
