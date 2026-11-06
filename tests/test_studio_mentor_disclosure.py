"""Bounded relevance-first working-source disclosure for the Mentor.

The packet must disclose the focused source, recorded relationships, explicitly referenced material and
recent kept ideas before unrelated filler, and it must report what it omitted. Undisclosed material is
never citable, so the agent cannot claim to have read it.
"""
from __future__ import annotations

from auteur.beginner.studio_store import CanvasStore
from auteur.beginner.studio_mentor import _context


def _canvas(tmp_path, *, total_extra: int = 16):
    store = CanvasStore(tmp_path, "disclosure")
    store.create()
    revision = 0

    def add(item, x):
        nonlocal revision
        store.apply("create-item", expected_revision=revision, command_id=f"add-{item['id']}",
                    payload={"item": item, "position": {"x": x, "y": 20 + (x % 400)}})
        revision += 1

    add({"id": "story-vision", "kind": "note", "title": "Story Vision",
         "content": "A city pays for knowledge with memory."}, 10)
    add({"id": "hero", "kind": "note", "title": "Surveyor", "content": "The surveyor's own past."}, 20)
    # Old, unrelated filler.
    add({"id": "filler-old", "kind": "note", "title": "Old unrelated note",
         "content": "An early idea that later became irrelevant."}, 30)
    # Older but relevant: recorded canvas relationship to the focus.
    add({"id": "ledger-old", "kind": "note", "title": "Ledger precedent",
         "content": "Historical precedent gives the ledger growing decision power."}, 40)
    store.apply("connect", expected_revision=revision, command_id="link-hero-ledger",
                payload={"connection": {"id": "hero-ledger", "source": "hero", "target": "ledger-old",
                                        "label": "the surveyor is bound by precedent"}})
    revision += 1
    # Newer relevant: a kept idea whose recorded origin is this focus.
    add({"id": "kept-new", "kind": "note", "title": "Kept restorative reading",
         "content": "Discovery restores shared understanding if the cost is returned.",
         "proposal_origin": {"request_sha": "a" * 64, "source_ref": "directions/restorative",
                             "source_kind": "host_agent_suggestion", "focus_id": "hero"}}, 50)
    # Newer unrelated filler.
    for index in range(total_extra):
        add({"id": f"filler-{index:02d}", "kind": "note", "title": f"Filler idea {index}",
             "content": f"Unrelated working note {index}."}, 60 + index)
    return store


def test_relevance_beats_insertion_order_and_reports_what_is_omitted(tmp_path):
    store = _canvas(tmp_path)
    snapshot = _context(store, "hero", "working")
    ctx = snapshot["context"]
    disclosed = [row["id"] for row in ctx["working_ideas"]]
    reasons = {row["id"]: row["selection_reason"] for row in ctx["working_ideas"]}
    assert disclosed[0] == "hero"
    assert reasons["hero"] == "focus"
    assert "kept-new" in disclosed and reasons["kept-new"] == "kept_for_focus"
    assert "ledger-old" in disclosed and reasons["ledger-old"] == "recorded_relationship"
    # Newest relevant material precedes older relevant material within the same priority.
    assert disclosed.index("kept-new") < disclosed.index("ledger-old")
    assert ctx["omitted_working_item_count"] > 0
    omitted_ids = {f"filler-{i:02d}" for i in range(16)} - set(disclosed)
    assert omitted_ids
    for omitted in omitted_ids:
        assert "canvas/items/" + omitted not in snapshot["allowed_refs"]


def test_explicitly_referenced_material_is_disclosed_even_when_it_is_old(tmp_path):
    store = _canvas(tmp_path, total_extra=0)
    snapshot = _context(store, "hero", "working",
                        author_reply="Compare this with the Old unrelated note from earlier.")
    reasons = {row["id"]: row["selection_reason"] for row in snapshot["context"]["working_ideas"]}
    assert reasons["filler-old"] == "explicit_reference"


def test_disclosure_is_deterministic_and_bounded(tmp_path):
    store = _canvas(tmp_path)
    first = _context(store, "hero", "working")
    second = _context(store, "hero", "working")
    assert first["source_sha256"] == second["source_sha256"]
    assert len(first["context"]["working_ideas"]) <= 10
    assert sum(len(row["content"]) for row in first["context"]["working_ideas"]) <= 6000


def test_long_content_is_marked_as_an_excerpt_and_fingerprinted(tmp_path):
    store = _canvas(tmp_path, total_extra=0)
    canvas = store.load()
    hero = next(item for item in canvas.items if item.id == "hero").model_dump(mode="json")
    hero["content"] = "The surveyor's past, in detail. " * 120
    store.apply("update-item", expected_revision=canvas.revision, command_id="long-hero",
                payload={"item": hero})
    disclosure = _context(store, "hero", "working")["context"]["working_ideas"][0]
    assert disclosure["content_is_excerpt"] is True
    assert disclosure["content_characters"] > len(disclosure["content"])


def test_intentions_are_disclosed_separately_from_working_ideas(tmp_path):
    store = _canvas(tmp_path, total_extra=0)
    canvas = store.load()
    store.apply("create-item", expected_revision=canvas.revision, command_id="add-intention",
                payload={"item": {"id": "restorative", "kind": "note", "title": "Restorative discovery",
                                  "content": "Discovery should become more restorative.",
                                  "intention_status": "active"},
                         "position": {"x": 300, "y": 300}})
    ctx = _context(store, "hero", "working")["context"]
    assert [row["id"] for row in ctx["working_ideas"]].count("restorative") == 0
    assert [(row["id"], row["status"]) for row in ctx["creative_intentions"]] == [
        ("restorative", "active"),
    ]
