"""Architecture and Realization freshness follow governing dependencies, not downstream writing (#612)."""
from __future__ import annotations

import json

import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_architecture import (
    _author_source_fingerprint, _digest, apply_architecture_review, complete_architecture, prepare_architecture,
    project_architecture,
)
from auteur.beginner.studio_realization import complete_realization, prepare_realization, project_realization
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import (
    HostAgentRequest, build_host_agent_request, build_host_agent_response, write_host_agent_request,
)

ARCHITECTURE = {
    "schema_version": 2, "summary": "Copying debts binds the keeper to the island.",
    "nodes": [
        {"id": "copying_engine", "title": "Nightly copying", "category": "engine",
         "summary": "Each night of copying deepens complicity."},
        {"id": "sacred_ledger", "title": "The sacred ledger", "category": "theme",
         "summary": "What is written is owed."},
    ],
    "links": [{"id": "binds", "source": "copying_engine", "target": "sacred_ledger", "function": "binds"}],
}
REALIZATION = {
    "schema_version": 1, "summary": "A keeper and a page.",
    "elements": [
        {"id": "ines", "kind": "character", "title": "Ines", "description": "The ledger keeper.",
         "architecture_refs": ["copying_engine"]},
        {"id": "scene-copying", "kind": "scene", "title": "The page with his name",
         "description": "Ines reaches her brother's entry.", "architecture_refs": ["sacred_ledger"]},
    ],
    "links": [{"id": "pov", "source": "scene-copying", "target": "ines", "function": "point of view"}],
    "architecture_feedback": [], "open_questions": [],
}


def reply(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(request, json.dumps(data), runtime="test", model="fixture").model_dump()


def apply(store, action, **payload):
    return store.apply(action, expected_revision=store.load().revision,
                       command_id=f"{action}-{store.load().revision}", payload=payload)


def item(store, item_id):
    return next(entry for entry in store.load().items if entry.id == item_id)


def edit(store, item_id, **changes):
    apply(store, "update-item", item=item(store, item_id).model_copy(update=changes).model_dump(mode="json"))


def story(tmp_path, *, with_scene=True):
    store = CanvasStore(tmp_path, "tide")
    store.create()
    apply(store, "create-item", item={"id": "story-vision", "title": "Story Vision",
                                      "content": "A keeper copies the island's debts."},
          position={"x": 10, "y": 10})
    apply(store, "create-item", item={"id": "salt-note", "title": "Salt", "content": "Salt is memory."},
          position={"x": 30, "y": 30})
    if with_scene:
        apply(store, "create-item", item={"id": "opening", "kind": "scene", "title": "Opening",
                                          "content": "Low tide."}, position={"x": 50, "y": 50})
    complete_architecture(store, reply(prepare_architecture(store), ARCHITECTURE))
    pending = prepare_realization(store, [])
    complete_realization(store, reply(pending, REALIZATION))
    return store, pending["request"]["request_sha256"]


def copy(store, realization_sha, element):
    """The Studio copy: structured origin, empty scene manuscript (#611)."""
    architecture_sha = project_architecture(store)["candidate_request_sha256"]
    source = next(entry for entry in REALIZATION["elements"] if entry["id"] == element)
    apply(store, "create-item", item={
        "id": "copy-" + element, "kind": source["kind"], "title": source["title"],
        "group": "Story Realization", "content": "" if source["kind"] == "scene" else source["description"],
        **({"scene_intent": source["description"]} if source["kind"] == "scene" else {}),
        "proposal_origin": {"request_sha": realization_sha, "source_ref": "realization/elements/" + element,
                            "source_kind": "realization_element", "focus_id": element,
                            "architecture_request_sha": architecture_sha,
                            "architecture_refs": source["architecture_refs"], "stale_at_adoption": False},
    }, position={"x": 200, "y": 200})


def test_copying_and_writing_do_not_stale_the_architecture_or_block_realization(tmp_path):
    store, realization_sha = story(tmp_path)
    copy(store, realization_sha, "scene-copying")
    copy(store, realization_sha, "ines")
    apply(store, "connect", connection={"id": "kept", "source": "copy-scene-copying", "target": "copy-ines",
                                        "label": "point of view"})
    edit(store, "copy-scene-copying", content="She copied it. The nib split on the full stop.")
    # Writing in the author's own scene, including one the architecture was built from, is manuscript drafting.
    edit(store, "opening", content="Low tide. Ines found her place.", scene_premise="A keeper doubts.",
         scene_intent="She reaches the entry.")
    apply(store, "create-item", item={"id": "later", "kind": "scene", "title": "Second tide",
                                      "content": "A new scene written afterwards."}, position={"x": 90, "y": 90})
    projection = project_architecture(store)
    assert projection["status"] == "ready"
    assert projection["downstream_changed"] is True
    assert projection["changed_sources"] == []
    assert project_realization(store)["status"] == "ready"
    # Further Realization proceeds from the unchanged governing Architecture.
    assert prepare_realization(store, ["copying_engine"])["status"] == "awaiting_host_agent"


@pytest.mark.parametrize(("change", "expected"), [
    (lambda store: edit(store, "story-vision", content="The keeper refuses."), ["story_vision"]),
    (lambda store: edit(store, "salt-note", content="Salt is forgetting."), ["working_sources"]),
    (lambda store: edit(store, "opening", title="Opening at high tide"), ["scene:opening"]),
    (lambda store: apply(store, "delete-item", item_id="opening"), ["scene:opening"]),
    (lambda store: (store.project_root / "story_identity.yaml").write_text(
        json.dumps({"title": "Tide", "core_answer": "Debts are owed to the sea.", "central_engine": {
        "want": "Keep faith", "resistance": "Kin", "conflict": "Duty and love", "stakes": "The island",
        "change": "Refusal"}}), encoding="utf-8"), ["accepted_identity"]),
])
def test_a_governing_change_stales_and_names_its_dependency(tmp_path, change, expected):
    store, _ = story(tmp_path)
    change(store)
    projection = project_architecture(store)
    assert projection["status"] == "stale"
    assert projection["changed_sources"] == expected
    realization = project_realization(store)
    assert realization["status"] == "stale"
    assert realization["changed_sources"] == expected
    with pytest.raises(ValueError, match="narrative architecture is stale"):
        prepare_realization(store, [])


def test_in_flight_architecture_rejects_governing_change_but_not_downstream_writing(tmp_path):
    store, realization_sha = story(tmp_path)
    pending = prepare_architecture(store, "Deepen the ledger.")
    copy(store, realization_sha, "scene-copying")
    edit(store, "copy-scene-copying", content="Written while the agent worked.")
    assert complete_architecture(store, reply(pending, ARCHITECTURE))["status"] == "review_ready"

    revised = prepare_architecture(store, "Deepen the ledger again.")
    edit(store, "story-vision", content="The keeper burns the ledger.")
    with pytest.raises(BeginnerConcurrencyError, match=r"source vision or working story changed \(Story Vision\)"):
        complete_architecture(store, reply(revised, ARCHITECTURE))


def test_a_reviewed_revision_applies_after_writing_but_not_after_a_governing_change(tmp_path):
    store, realization_sha = story(tmp_path)
    revised = {**ARCHITECTURE, "summary": "The ledger is alive."}
    pending = prepare_architecture(store, "Make the ledger alive.")
    complete_architecture(store, reply(pending, revised))
    copy(store, realization_sha, "scene-copying")
    edit(store, "copy-scene-copying", content="Written while reviewing.")
    applied = apply_architecture_review(store, pending["request"]["request_sha256"])
    assert applied["candidate"]["summary"] == "The ledger is alive."

    pending = prepare_architecture(store, "Make the ledger patient.")
    complete_architecture(store, reply(pending, {**ARCHITECTURE, "summary": "The ledger waits."}))
    edit(store, "salt-note", content="Salt is a warning.")
    with pytest.raises(BeginnerConcurrencyError, match=r"working ideas that guide the architecture\); review again"):
        apply_architecture_review(store, pending["request"]["request_sha256"])
    assert project_architecture(store)["candidate"]["summary"] == "The ledger is alive."


def test_in_flight_realization_rejects_governing_change_but_not_a_copy(tmp_path):
    store, realization_sha = story(tmp_path)
    pending = prepare_realization(store, ["copying_engine"])
    copy(store, realization_sha, "ines")
    assert complete_realization(store, reply(pending, REALIZATION))["status"] == "ready"

    pending = prepare_realization(store, ["sacred_ledger"])
    edit(store, "salt-note", content="Salt is a lie.")
    with pytest.raises(BeginnerConcurrencyError, match="stale realization retained"):
        complete_realization(store, reply(pending, REALIZATION))


def test_a_format_2_architecture_keeps_its_recorded_freshness(tmp_path):
    """An existing request is never reinterpreted under the new dependency contract."""
    store, realization_sha = story(tmp_path, with_scene=False)
    current = project_architecture(store)
    format_3 = HostAgentRequest(**json.loads(
        (store.directory / "architecture" / "requests" / current["candidate_request_sha256"] / "request.json")
        .read_text(encoding="utf-8")))
    user = json.loads(format_3.user)
    user["freshness_format"] = 2
    settings = {"canvas_id": store.canvas_id, "source_sha256": _author_source_fingerprint(store, user),
                "design_guidance_sha256": format_3.settings["design_guidance_sha256"],
                "intention_sha256": format_3.settings["intention_sha256"], "freshness_format": 2,
                "operation": "develop"}
    legacy = build_host_agent_request(
        candidate_id="studio-legacy", role="studio_architecture", system=format_3.system,
        user=json.dumps(user, sort_keys=True), settings=settings, output_contract=format_3.output_contract)
    base = store.directory / "architecture"
    write_host_agent_request(base / "requests" / legacy.request_sha256 / "request.json", legacy)
    record = json.loads((base / "current.json").read_text(encoding="utf-8"))
    record.update(request_sha256=legacy.request_sha256, source_sha256=settings["source_sha256"])
    (base / "current.json").write_text(json.dumps(record), encoding="utf-8")
    (base / "latest_request.json").write_text(json.dumps({"request_sha256": legacy.request_sha256}),
                                              encoding="utf-8")
    assert project_architecture(store)["status"] == "ready"
    copy(store, realization_sha, "ines")
    assert project_architecture(store)["status"] == "stale"
    assert project_architecture(store)["changed_sources"] == ["working_story"]
    assert _digest(settings) == _digest(legacy.settings)
