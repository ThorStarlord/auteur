"""Studio inspector edits cannot rely exclusively on a separate Save click.

The executable DOM-stub reproducer is in the adversarial UX review. This test
pins the corrected event capture contract in the opt-in prototype.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_inspector_edits_capture_to_working_model_on_input():
    js = (HERE / "studio.js").read_text(encoding="utf-8")
    html = (HERE / "index.html").read_text(encoding="utf-8")
    begin = js.index("function captureInspectorFields()")
    end = js.index("function saveCurrent()", begin)
    capture = js[begin:end]
    assert 'item.content = $("content").value' in capture
    assert 'item.title = $("title").value.trim()' in capture
    assert 'item.group = $("group").value.trim()' in capture
    assert 'scheduleSave()' in capture
    assert 'addEventListener("input", captureInspectorFields)' in js
    assert 'addEventListener("change", captureInspectorFields)' in js
    assert "export your notes to save them" not in html
