"""Focused unfolding may add editable working ideas, never accepted story canon."""
from __future__ import annotations

import pytest
from pydantic import ValidationError
from auteur.beginner.persistence import BeginnerConcurrencyError
from auteur.beginner.studio_store import CanvasItem, CanvasStore, ProposalOrigin, WorkingCanvas

SHA = "a" * 64
ALT_SHA = "b" * 64

def candidate(item_id="adopted"):
    return {
        "id": item_id, "kind": "note", "title": "Earned breakthrough",
        "content": "Suggested function; editable and noncanonical",
        "group": "Narrative Architecture", "architecture_role": "trope",
        "proposal_origin": {
            "request_sha": SHA, "source_ref": "links/0",
            "source_kind": "proposal_edge", "focus_id": "emotion-1"
        },
    }

def payload(item_id="adopted"):
    return {"item": candidate(item_id), "position": {"x": 240, "y": 360}}

def test_old_canvas_without_architecture_metadata_remains_valid(tmp_path):
    s=CanvasStore(tmp_path,"legacy")
    s.create()
    old={"id": "legacy-note", "kind": "note", "title": "A scene", "content": "Text"}
    doc=s.apply("create-item",expected_revision=0,command_id="old-create",
                payload={"item":old,"position":{"x":20,"y":30}})
    restored=CanvasStore(tmp_path,"legacy").load()
    assert restored.items[0].architecture_role is None
    assert restored.items[0].proposal_origin is None
    assert restored.items[0].title=="A scene"
    assert doc.revision==restored.revision==1

def test_typed_provenance_and_invalid_roles_are_checked():
    item=CanvasItem.model_validate(candidate(),strict=True)
    assert item.architecture_role=="trope"
    assert item.proposal_origin.request_sha==SHA
    with pytest.raises(ValidationError):
        CanvasItem.model_validate({**candidate(),"architecture_role":"accepted_canon"},strict=True)
    with pytest.raises(ValidationError):
        CanvasItem.model_validate({**candidate(),"proposal_origin":
            {**candidate()["proposal_origin"],"request_sha":"bad"}},strict=True)
    with pytest.raises(ValidationError):
        CanvasItem.model_validate({**candidate(),"proposal_origin":
            {**candidate()["proposal_origin"],"source_ref":"../escape?token=secret"}},strict=True)

def test_adopt_is_atomic_and_idempotent_but_never_accepts_story(tmp_path):
    s=CanvasStore(tmp_path,"author")
    s.create()
    first=s.apply("adopt-suggestion",expected_revision=0,command_id="adopt-once",payload=payload())
    repeat=s.apply("adopt-suggestion",expected_revision=0,command_id="adopt-once",payload=payload())
    assert first.revision==repeat.revision==1
    assert len(repeat.items)==1
    assert repeat.items[0].proposal_origin.source_ref=="links/0"
    assert not (tmp_path/"story_identity.yaml").exists()
    assert not (tmp_path/".auteur"/"beginner"/"workspaces").exists()
    assert CanvasStore(tmp_path,"author").load().items[0].title=="Earned breakthrough"

def test_different_command_same_proposal_identity_cannot_duplicate(tmp_path):
    s=CanvasStore(tmp_path,"dupe")
    s.create()
    s.apply("adopt-suggestion",expected_revision=0,command_id="one",payload=payload())
    with pytest.raises(ValueError,match="already adopted|duplicate"):
        s.apply("adopt-suggestion",expected_revision=1,command_id="two",payload=payload("second"))
    assert len(s.load().items)==1 and s.load().revision==1

def test_revision_conflict_fails_without_working_mutation(tmp_path):
    s=CanvasStore(tmp_path,"race")
    s.create()
    s.apply("create-item",expected_revision=0,command_id="first",
        payload={"item":{"id":"other","title":"Already there"},"position":{"x":1,"y":2}})
    original=s._path("canvas.json").read_bytes()
    with pytest.raises(BeginnerConcurrencyError):
        s.apply("adopt-suggestion",expected_revision=0,command_id="stale",payload=payload())
    assert s._path("canvas.json").read_bytes()==original

def test_unattributed_automatic_canon_promotion_and_extra_payload_rejected(tmp_path):
    s=CanvasStore(tmp_path,"authority")
    s.create()
    with pytest.raises((ValueError,ValidationError)):
        s.apply("adopt-suggestion",expected_revision=0,command_id="no-origin",
            payload={"item":{"id":"x","title":"Unknown"},"position":{"x":1,"y":2}})
    with pytest.raises(ValueError):
        s.apply("adopt-suggestion",expected_revision=0,command_id="extra",
            payload={**payload(),"canonical":True})
    assert s.load().revision==0

def test_deleted_origin_cannot_be_readopted_under_new_identity(tmp_path):
    s=CanvasStore(tmp_path,"restore")
    s.create()
    a=s.apply("adopt-suggestion",expected_revision=0,command_id="adopt",payload=payload())
    b=s.apply("delete-item",expected_revision=a.revision,command_id="delete",
        payload={"item_id":"adopted"})
    with pytest.raises(ValueError,match="already adopted|duplicate"):
        s.apply("adopt-suggestion",expected_revision=b.revision,command_id="new-id",payload=payload("duplicate"))
    restored=s.apply("restore-item",expected_revision=b.revision,command_id="restore",
        payload={"item_id":"adopted"})
    assert restored.items[0].architecture_role=="trope"

def test_author_can_edit_adopted_node_without_losing_historical_origin(tmp_path):
    s=CanvasStore(tmp_path,"author-edit")
    s.create()
    first=s.apply("adopt-suggestion",expected_revision=0,command_id="adopt",payload=payload())
    changed=first.items[0].model_dump(mode="json")
    changed["title"]="Now I have a different purpose"
    changed["content"]="An author-owned interpretation"
    nxt=s.apply("update-item",expected_revision=1,command_id="edit",
        payload={"item":changed})
    assert nxt.items[0].title=="Now I have a different purpose"
    assert nxt.items[0].proposal_origin.request_sha==SHA
    assert nxt.items[0].proposal_origin.source_ref=="links/0"

def test_replace_document_cannot_bypass_adoption_uniqueness(tmp_path):
    s=CanvasStore(tmp_path,"replace")
    s.create()
    first=candidate("first")
    second=candidate("second")
    with pytest.raises(ValueError,match="duplicate"):
        s.apply("replace-working-document",expected_revision=0,command_id="two",
            payload={"items":[first,second],"connections":[],
                "positions":{"first":{"x":1,"y":1},"second":{"x":2,"y":2}},
                "viewport":{"pan_x":0,"pan_y":0,"zoom":1}})
    assert s.load().revision==0
