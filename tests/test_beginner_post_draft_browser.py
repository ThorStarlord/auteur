from pathlib import Path


def test_browser_exposes_post_draft_actions_without_direct_canonical_write() -> None:
    html = Path("src/auteur/beginner/browser/index.html").read_text(encoding="utf-8")
    app = Path("src/auteur/beginner/browser/app.js").read_text(encoding="utf-8")
    server = Path("src/auteur/beginner/server.py").read_text(encoding="utf-8")

    assert 'id="post-draft-review"' in html
    assert "Recommended next step" in html
    assert "accept-latest-draft" in app
    assert "revision-handoff" in app
    assert "draft-chapter-1" in app
    assert '"draft-chapter-1": "draft_chapter_one"' in server
    assert "auteur draft <project> 1" not in app
    assert "Revising Chapter" in app
    assert "window.confirm" in app
    assert "write_final" not in app
