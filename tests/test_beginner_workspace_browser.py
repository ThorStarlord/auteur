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


def test_browser_renders_review_labels_instead_of_internal_card_ids():
    js = _read(APP)
    assert "summary.label" in js
    assert '(summary.card_id || "card") + " — "' not in js


def test_browser_uses_tri_state_guidance_alignment_and_clear_review_language():
    js = _read(APP)
    assert "guidance_alignment" in js
    assert "unanswered" in js.lower()
    assert "differs from guidance" in js
    assert "ready for review" in js.lower()
    assert "working interpretation" in js.lower()
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
        "revision_id",
    ):
        assert token in js


def test_browser_exposes_composition_review_controls_and_author_inputs():
    js = _read(APP)
    for token in ('data-command="acknowledge"', "acknowledge-remainder", "data-composition-label", "data-composition-rationale"):
        assert token in js
    assert "Add a relationship lens" in js


def test_browser_uses_beginner_labels_and_completion_state():
    js = _read(APP)
    assert "function stageLabel" in js
    assert "function milestoneLabel" in js
    assert "Story foundation accepted" in js
    assert "revision workspace" in js
    assert "Open thread:" not in js
    assert 'class="nav-review"' not in js


def test_browser_has_decision_workspace_and_on_demand_inspector():
    html = _read(INDEX)
    js = _read(APP)
    css = _read(STYLES)
    assert 'id="decision-workspace"' in html
    assert 'id="guidance-inspector"' in html
    assert "Explore guidance" in html
    assert "guidance_inspector" in js
    assert "decision-workspace" in css


def test_browser_does_not_build_semantics_or_readiness():
    js = _read(APP)
    assert "narrative_consequences" not in js.replace("guidance_inspector", "")
    assert "ready_to_accept" not in js


def test_browser_inspector_and_navigator_are_accessible_drawers():
    html = _read(INDEX)
    js = _read(APP)
    css = _read(STYLES)
    assert 'aria-controls="guidance-inspector"' in html
    assert 'aria-expanded="false"' in html
    assert 'aria-live="polite"' in html
    assert ".guidance-inspector.is-open" in css
    assert "window.innerWidth <= 800" in js
    assert "Escape" in js
    assert "aria-hidden" in js


def test_browser_renders_contextual_inspector_without_internal_semantic_labels():
    js = _read(APP)
    assert "Story experience & craft context" in js
    assert "Reader experience" in js
    assert "Emotional promise" in js
    assert "Narrative promise" in js
    assert "Genre conventions" in js
    assert "Craft principle" in js
    assert "Common failure mode" in js
    assert "Mystery & reader contract" not in js
    assert "Mystery craft principle" not in js
    assert "option_comparisons" in js
    assert "Semantic Area:" not in js


def test_browser_renders_composition_dispositions_without_internal_state_labels():
    html = _read(INDEX)
    js = _read(APP)
    combined = html + js

    assert "Will remain context / provenance" in combined
    assert "Will become canonical" in combined
    assert "working_composition" in js
    assert "component.label" in js
    assert 'textContent = component.component_id' not in js
    assert "mapping_preview" in js


def test_browser_keeps_tradeoffs_out_of_center_warnings():
    js = _read(APP)
    assert "warnings = warnings.concat" not in js
    assert "card.warnings_or_tensions" not in js



def test_browser_makes_phase_transitions_and_primary_actions_explicit():
    js = _read(APP)
    css = _read(STYLES)

    assert "Next: outline your story" in js
    assert "primary-next-action" in js
    assert "projection.primary_action" in js
    assert "projectedPrimary.action_id" in js
    assert "primary-action-reason" in js
    assert "phase-complete-banner" in js
    assert ".review-action.primary-action" in css
    assert ".navigator-entry.is-accepted" in css
    assert "focus-visible" in css


def test_browser_exposes_integrated_story_composition_and_explicit_craft_dimensions():
    js = _read(APP)

    for token in (
        "How these parts work together",
        "Aesthetic framing",
        "Common tropes",
        "Narrative structure",
        "Relationship / thematic dynamics",
        "relationship_explanation",
        "expected_tropes",
        "narrative_structure",
    ):
        assert token in js
