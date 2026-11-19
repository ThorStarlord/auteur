"""A copied Realization proposal keeps a small validated origin; legacy data is unchanged (#611)."""
import pytest

from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_store import CanvasItem, CanvasStore, WorkingCanvas

REALIZATION, ARCHITECTURE = "b" * 64, "c" * 64
LEGACY_FOOTER = (
    "Neighbors decide.\n\nArchitecture refs: allocation_engine\n"
    "Origin: working realization " + REALIZATION + "/assembly. Not accepted story."
)


def origin(**changes):
    return {
        "request_sha": REALIZATION, "source_ref": "realization/elements/assembly",
        "source_kind": "realization_element", "focus_id": "assembly",
        "architecture_request_sha": ARCHITECTURE, "architecture_refs": ["allocation_engine"],
        "stale_at_adoption": False, **changes,
    }


def scene(**changes):
    return {"id": "copied", "kind": "scene", "title": "Assembly", "group": "Story Realization",
            "content": "", "scene_intent": "Neighbors decide.", "proposal_origin": origin(), **changes}


def test_realization_origin_persists_through_the_working_document_command(tmp_path):
    store = CanvasStore(tmp_path, "origin")
    store.create()
    store.apply("replace-working-document", expected_revision=0, command_id="copy", payload={
        "items": [scene()], "connections": [], "positions": {"copied": {"x": 10, "y": 10}},
        "viewport": {"pan_x": 0, "pan_y": 0, "zoom": 1},
    })
    reloaded = CanvasStore(tmp_path, "origin").load().items[0]
    assert reloaded.content == ""
    assert reloaded.proposal_origin.model_dump(mode="json") == origin()


@pytest.mark.parametrize("bad", [
    {"architecture_refs": ["Not An Id"]},
    {"architecture_refs": []},
    {"architecture_request_sha": "short"},
    {"source_ref": "realization/elements/other"},
    {"stale_at_adoption": None},
    {"source_kind": "proposal_edge"},
])
def test_invalid_realization_origin_is_rejected(bad):
    with pytest.raises(ValueError):
        CanvasItem.model_validate(scene(proposal_origin=origin(**bad)), strict=True)


def test_the_same_proposal_cannot_be_adopted_twice(tmp_path):
    store = CanvasStore(tmp_path, "twice")
    store.create()
    with pytest.raises((ValueError, BeginnerConcurrencyError)):
        store.apply("replace-working-document", expected_revision=0, command_id="dup", payload={
            "items": [scene(), scene(id="again")], "connections": [],
            "positions": {"copied": {"x": 1, "y": 1}, "again": {"x": 2, "y": 2}},
            "viewport": {"pan_x": 0, "pan_y": 0, "zoom": 1},
        })


def test_legacy_origins_and_copied_footers_serialize_unchanged(tmp_path):
    legacy_origin = {"request_sha": "a" * 64, "source_ref": "links/0",
                     "source_kind": "proposal_edge", "focus_id": "allocation_engine"}
    document = WorkingCanvas.model_validate({
        "canvas_id": "legacy", "revision": 3,
        "items": [
            {"id": "kept", "title": "Kept edge", "architecture_role": "theme",
             "proposal_origin": legacy_origin},
            {"id": "old-copy", "kind": "scene", "title": "Assembly", "group": "Story Realization",
             "content": LEGACY_FOOTER},
        ],
        "positions": {"kept": {"x": 1, "y": 1}, "old-copy": {"x": 2, "y": 2}},
    })
    text = document.model_dump_json()
    assert '"proposal_origin":{"request_sha":"' + "a" * 64 + '","source_ref":"links/0",' \
        '"source_kind":"proposal_edge","focus_id":"allocation_engine"}' in text
    reloaded = WorkingCanvas.model_validate_json(text, strict=True)
    assert reloaded.model_dump_json() == text
    assert reloaded.items[1].content == LEGACY_FOOTER
    assert reloaded.items[1].proposal_origin is None
