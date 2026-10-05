from pathlib import Path


BROWSER = Path("src/auteur/beginner/browser")


def test_book_orientation_is_primary_and_technical_details_are_progressive() -> None:
    html = (BROWSER / "index.html").read_text(encoding="utf-8")
    app = (BROWSER / "app.js").read_text(encoding="utf-8")

    assert '<section aria-label="Book orientation"' in html
    for token in (
        'id="book-current-position"',
        'id="book-recent-changes"',
        'id="book-pending-updates"',
        'id="book-needs-attention"',
        'id="book-next-story-action"',
        'id="book-open-current-chapter"',
    ):
        assert token in html

    assert '<details aria-label="Technical Book details"' in html
    assert "<summary>Show details</summary>" in html
    assert "Next technical action:" in html

    for token in (
        "progress.current_chapter",
        "progress.current_chapter_state",
        "progress.recent_changes",
        "progress.pending_updates",
        "progress.needs_attention",
        "progress.next_story_action",
        "progress.next_action_chapter",
    ):
        assert token in app

    assert "renderBookNoticeList" in app
    assert "Open Chapter " in app
    assert "Advanced: whole-book details" not in html


def test_post_draft_chapter_presentation_is_dynamic() -> None:
    html = (BROWSER / "index.html").read_text(encoding="utf-8")
    app = (BROWSER / "app.js").read_text(encoding="utf-8")

    assert 'id="post-draft-heading">Chapter</h3>' in html
    assert '$("post-draft-heading").textContent = "Chapter " + chapter' in app
    assert "chapter + ' draft</h4>'" in app
    assert "No Chapter 1 draft exists yet." not in app
