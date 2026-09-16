"""Task 7: Beginner Workspace browser vertical slice tests (TDD failing first).

File-read smoke tests only: the browser is presentation-only over the Task 6
local JSON API, so these tests assert static structure/wiring without a server.
"""

from __future__ import annotations

from pathlib import Path

BROWSER_DIR = Path(__file__).resolve().parent.parent / "src" / "auteur" / "beginner" / "browser"
INDEX = BROWSER_DIR / "index.html"
APP = BROWSER_DIR / "app.js"
STYLES = BROWSER_DIR / "styles.css"

FORBIDDEN_SEALED_STRINGS = ("six strangers", "killer never leaves")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_browser_files_exist_and_nonempty():
    for path in (INDEX, APP, STYLES):
        assert path.is_file(), f"missing browser file: {path}"
        assert path.stat().st_size > 0, f"browser file is empty: {path}"


def test_browser_has_navigator_card_continue():
    html = _read(INDEX).lower()
    assert 'aria-label="story navigator"' in html
    assert 'data-testid="decision-card"' in html
    assert 'data-testid="continue"' in html


def test_browser_select_autosaves_and_continue_advances():
    js = _read(APP)
    assert "/api/beginner/workspaces" in js
    assert "commands/select" in js
    assert "commands/continue" in js
    assert "expected_session_version" in js
    assert "command_id" in js
    lowered = js.lower()
    assert "saved" in lowered
    # Selecting an option autosaves without advancing: the select path must not
    # trigger the continue command.
    select_idx = js.find("commands/select")
    continue_idx = js.find("commands/continue")
    assert select_idx != -1 and continue_idx != -1 and select_idx != continue_idx


def test_browser_tutor_collapsed_and_warnings_inline():
    html = _read(INDEX)
    js = _read(APP)
    combined = html + js
    assert "<details" in combined
    # Tutor teaching/rationale/impact/evidence collapsed by default: no details
    # element may carry the open attribute in the static shell or templates.
    assert "<details open" not in combined
    for token in ("why_this_matters", "narrative_principle", "downstream_consequences", "evidence"):
        assert token in js, f"browser must render tutor field: {token}"
    assert "blocking" in combined.lower()
    assert "stale" in combined.lower()
    assert "story map" in combined.lower()


def test_browser_narrow_screens_collapse_navigator_into_drawer():
    css = _read(STYLES)
    html = _read(INDEX)
    js = _read(APP)
    assert "@media" in css
    assert "drawer" in (css + html + js).lower() or "nav-open" in (css + html + js)


def test_browser_contains_no_sealed_logic():
    for path in (INDEX, APP):
        lowered = _read(path).lower()
        for forbidden in FORBIDDEN_SEALED_STRINGS:
            assert forbidden not in lowered, f"{path.name} leaks sealed fixture logic: {forbidden!r}"


def test_browser_render_smoke_via_file_reads():
    html = _read(INDEX)
    js = _read(APP)
    assert "app.js" in html
    assert "styles.css" in html
    assert "decision_card" in js
    assert "navigator" in js
    assert "session_version" in js
    assert "selected_option" in js


def test_browser_exposes_review_and_acceptance_commands():
    js = _read(APP)
    for token in ("available_actions", "open-review", "accept-direction", "accept-identity", "accept-structure"):
        assert token in js
    assert "What this choice changes" in js


def test_browser_uses_tri_state_guidance_alignment_and_clear_review_language():
    js = _read(APP)
    assert "guidance_alignment" in js
    assert "unanswered" in js.lower()
    assert "differs from guidance" in js
    assert "ready for review" in js.lower()
    assert "not yet accepted" in js.lower()
    assert "Review " in js
    assert "guidance-note" in js


def test_browser_exposes_revision_controls_without_domain_rules():
    js = _read(APP)
    for token in (
        "open-revision",
        "cancel-revision",
        "accept-revised-direction",
        "accept-revised-identity",
        "accept-revised-structure",
        "at_risk_stages",
        "target_stage",
    ):
        assert token in js
    assert "revision_id" in js
