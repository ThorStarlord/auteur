"""Source-focused W4-style creative continuity is working, not canon.

This is a deterministic, deliberately authored fixture derived from the public
W4 Vision, not a host-model quality or reliability evaluation.
"""
from __future__ import annotations

import json

import pytest

from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_realization import (
    complete_realization, prepare_realization, project_realization,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


def _respond(state: dict, candidate: dict) -> dict:
    request = HostAgentRequest(**state["request"])
    return build_host_agent_response(
        request, json.dumps(candidate), runtime="deterministic-test", model="fixture",
    ).model_dump()


def _architecture() -> dict:
    return {
        "schema_version": 2,
        "summary": "Recurring floods renew communal allocation pressures; records complicate fairness.",
        "nodes": [
            {"id": "flood_cycle", "title": "Recurring flood cycle", "category": "engine",
             "summary": "An indifferent flood renews physical pressure without intending harm."},
            {"id": "allocation_process", "title": "Water allocation", "category": "engine",
             "summary": "Communities negotiate water distribution and canal repairs."},
            {"id": "ledger_evidence", "title": "Historical ledger", "category": "thread",
             "summary": "Records illuminate earlier choices but cannot settle their fairness."},
            {"id": "distribution_ritual", "title": "Public ritual", "category": "engine",
             "summary": "A recurring procedure translates claims into practical decisions."},
            {"id": "fairness_question", "title": "What counts as fair?", "category": "theme",
             "summary": "Inherited obligations remain contestable without one moral answer."},
        ],
        "links": [
            {"id": "flood_renews_allocation", "source": "flood_cycle",
             "target": "allocation_process", "function": "Recurring material need renews distribution pressure."},
            {"id": "ledger_reframes_claims", "source": "ledger_evidence",
             "target": "fairness_question", "function": "Precedent informs but cannot determine fairness."},
            {"id": "ritual_shapes_allocation", "source": "distribution_ritual",
             "target": "allocation_process", "function": "Public negotiation produces an actionable decision."},
            {"id": "allocation_creates_precedent", "source": "allocation_process",
             "target": "ledger_evidence", "function": "New decisions become part of future recorded history."},
        ],
        "open_questions": ["No cast, preferred hierarchy, or moral resolution has been accepted."],
    }


def _realization() -> dict:
    return {
        "schema_version": 1,
        "summary": "Possible concrete pressures demonstrate allocation, investigation and precedent; none is canon.",
        "elements": [
            {"id": "canal_records_custodian", "kind": "character", "title": "A possible records custodian",
             "description": "A proposed custodian must disclose competing ledger entries without declaring which claim deserves priority.",
             "architecture_refs": ["ledger_evidence", "fairness_question"]},
            {"id": "allocation_assembly", "kind": "scene", "title": "A possible allocation assembly",
             "description": "After a flood, a public procedure must weigh stored-water claims and repairs before interpretations agree.",
             "architecture_refs": ["flood_cycle", "allocation_process", "distribution_ritual"]},
            {"id": "competing_precedents", "kind": "event", "title": "Competing precedents discovered",
             "description": "Previously defensible allocations imply incompatible obligations; evidence informs the assembly but cannot dictate justice.",
             "architecture_refs": ["ledger_evidence", "fairness_question", "allocation_process"]},
            {"id": "carried_obligation", "kind": "plot_arc", "title": "A claim carried forward",
             "description": "A provisional distribution resolves immediate need but becomes a revisable precedent in a later cycle.",
             "architecture_refs": ["allocation_process", "flood_cycle", "fairness_question"]},
        ],
        "links": [
            {"id": "custodian_informs_assembly", "source": "canal_records_custodian",
             "target": "allocation_assembly", "function": "Shares evidence without resolving competing interpretations."},
            {"id": "precedents_complicate_assembly", "source": "competing_precedents",
             "target": "allocation_assembly", "function": "Historical evidence raises competing obligations."},
            {"id": "assembly_carries_forward", "source": "allocation_assembly",
             "target": "carried_obligation", "function": "A temporary practical choice becomes contestable future precedent."},
        ],
        "architecture_feedback": [],
        "open_questions": ["Whether any proposed character or particular outcome belongs in the story remains the author's choice."],
    }


def _store(tmp_path, canvas_id="w4-public-vision") -> CanvasStore:
    store = CanvasStore(tmp_path, canvas_id)
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="public-vision",
        payload={"item": {
            "id": "story-vision", "kind": "note", "title": "Story Vision",
            "content": "Each spring indifferent floods renew water and canal-repair claims; a ledger and annual ritual make justice disputable. No cast, hierarchy, or moral answer is accepted.",
        }, "position": {"x": 40, "y": 50}},
    )
    request = prepare_architecture(store)
    complete_architecture(store, _respond(request, _architecture()))
    return store


def test_focused_response_cannot_ignore_author_selected_architecture(tmp_path):
    store = _store(tmp_path)
    request = prepare_realization(store, ["allocation_process"])
    off_focus = _realization()
    for element in off_focus["elements"]:
        element["architecture_refs"] = ["fairness_question"]
    with pytest.raises(ValueError, match="selected architecture focus"):
        complete_realization(store, _respond(request, off_focus))
    assert project_realization(store)["status"] == "awaiting_host_agent"
    assert project_realization(store)["candidate"] is None
    assert complete_realization(store, _respond(request, _realization()))["status"] == "ready"


def test_realization_of_public_w4_style_architecture_remains_provisional(tmp_path):
    store = _store(tmp_path)
    revision = store.load().revision
    request = prepare_realization(store, ["allocation_process"])
    source = json.loads(request["request"]["user"])["source"]
    assert source["focus_ids"] == ["allocation_process"]
    assert source["architecture"]["links"][0]["id"] == "flood_renews_allocation"
    result = complete_realization(store, _respond(request, _realization()))
    assert result["status"] == "ready"
    assert {"allocation_process", "flood_cycle", "ledger_evidence"} <= {
        ref for element in result["candidate"]["elements"] for ref in element["architecture_refs"]
    }
    reopened = project_realization(CanvasStore(tmp_path, "w4-public-vision"))
    assert reopened["candidate"] == result["candidate"]
    assert reopened["status"] == "ready"
    assert store.load().revision == revision
    assert not (tmp_path / "story_identity.yaml").exists()
    assert not (tmp_path / "blueprint.yaml").exists()
    assert not (tmp_path / "chapters").exists()

    document = store.load()
    edited = document.items[0].model_copy(update={"content": "The author changed the governing premise."})
    store.apply("update-item", expected_revision=document.revision, command_id="new-vision",
                payload={"item": edited.model_dump(mode="json")})
    stale = project_realization(CanvasStore(tmp_path, "w4-public-vision"))
    assert stale["status"] == "stale"
    assert stale["candidate"] == result["candidate"]


def test_whole_story_realization_does_not_require_specific_focus(tmp_path):
    store = _store(tmp_path)
    request = prepare_realization(store, [])
    general = _realization()
    for element in general["elements"]:
        element["architecture_refs"] = ["fairness_question"]
    assert complete_realization(store, _respond(request, general))["status"] == "ready"


def test_multi_component_focus_is_not_partially_discarded(tmp_path):
    store = _store(tmp_path)
    request = prepare_realization(store, ["allocation_process", "ledger_evidence"])
    partial = _realization()
    for element in partial["elements"]:
        element["architecture_refs"] = ["allocation_process"]
    with pytest.raises(ValueError, match="selected architecture focus"):
        complete_realization(store, _respond(request, partial))
    assert complete_realization(store, _respond(request, _realization()))["status"] == "ready"
