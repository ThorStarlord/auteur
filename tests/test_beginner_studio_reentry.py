"""Studio re-entry preserves existing working canvases, not a blank replacement."""
from __future__ import annotations

import json
from urllib.request import Request, urlopen

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_store import CanvasStore, list_canvas_summaries


def test_local_recent_canvases_recoverable_after_restart(tmp_path):
    store = CanvasStore(tmp_path, "story-one")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="create-first",
                payload={"item": {"id": "note-one", "title": "Saved plan", "content": "A hidden clue"},
                         "position": {"x": 50, "y": 60}})
    summaries = list_canvas_summaries(tmp_path)
    assert summaries[0]["canvas_id"] == "story-one"
    assert summaries[0]["title"] == "Saved plan"
    assert summaries[0]["item_count"] == 1
    assert list_canvas_summaries(tmp_path)[0]["state"] == "ready"


def test_unavailable_canvas_is_not_silently_discarded(tmp_path):
    store = CanvasStore(tmp_path, "broken")
    store.create()
    store._path("canvas.json").write_text("bad-json", encoding="utf-8")
    summaries = list_canvas_summaries(tmp_path)
    assert summaries[0]["canvas_id"] == "broken"
    assert summaries[0]["state"] == "unavailable"


def test_canvas_list_route_does_not_create_new_canvas(tmp_path):
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    try:
        with urlopen(f"http://127.0.0.1:{server.port}/api/beginner/studio/canvases") as response:
            assert response.status == 200
            assert json.loads(response.read()) == {"canvases": []}
        assert list_canvas_summaries(tmp_path) == []
    finally:
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()


def test_studio_reentry_has_recent_picker_and_new_canvas_action():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"
    js = (root / "studio.js").read_text(encoding="utf-8")
    html = (root / "studio.html").read_text(encoding="utf-8")
    assert 'id="canvas-picker"' in html and 'id="new-canvas"' in html
    assert "listCanvasChoices()" in js and "recent.canvas_id" in js
    assert "No new canvas was created" in js
