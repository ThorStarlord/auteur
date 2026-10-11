"""Story Vision reuses the durable noncanonical working canvas, without a fabricated premise."""
from pathlib import Path

from auteur.beginner.studio_store import CanvasStore


BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_vision_is_no_premise_working_content_and_recovers(tmp_path):
    store = CanvasStore(tmp_path, "vision-test")
    store.create()
    result = store.apply(
        "create-item", expected_revision=0, command_id="create-vision",
        payload={"item": {
            "id": "story-vision", "title": "Story Vision", "kind": "note",
            "group": "Story Vision",
            "content": "Awe and vindication; mystery and horror alternate; no premise selected.",
        }, "position": {"x": 40, "y": 50}},
    )
    assert result.items[0].content.startswith("Awe")
    assert CanvasStore(tmp_path, "vision-test").load().items[0].id == "story-vision"
    assert not (tmp_path / ".auteur" / "beginner" / "workspaces").exists()
    assert not (tmp_path / "story_identity.yaml").exists()


def test_story_vision_has_optional_prose_entry_and_no_shadow_authority():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    assert 'id="vision-text"' in html
    assert 'id="vision-write"' in html
    assert 'A premise is optional' in html
    assert 'id: "story-vision"' in js
    assert 'kind: "note"' in js
    assert "scheduleSave()" in js
