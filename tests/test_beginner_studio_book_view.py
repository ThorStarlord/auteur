"""Read-only Book view consumes existing orientation with visible limitations."""
from pathlib import Path

BROWSER = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"


def test_book_projection_is_not_a_second_book_owner():
    html = (BROWSER / "studio.html").read_text(encoding="utf-8")
    js = (BROWSER / "studio.js").read_text(encoding="utf-8")
    assert "/api/beginner/book/progress" in js
    assert "book.current_chapter_state" in js
    assert "book.pending_updates" in js and "book.needs_attention" in js
    assert "book.next_story_action" in js
    assert "Chapter-order orientation only" in js
    assert 'id="book-orientation"' in html
    assert "read-only" in js.lower()
