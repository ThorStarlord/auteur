"""Return to Writing: inspecting a working item or Architecture pauses, never replaces, writing (#603, #604)."""
import json
import os
import re

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

CANVAS = "ferry-story"
OPENING = "Mara pushed off before the bell finished ringing. The fog took the bank behind her."
INSERT = " She did not look back"
GENRE = "Gothic mystery"
TROPE = "The keeper who cannot leave her post"
TROPE_REF = "genre_contracts/gothic_mystery/trope_functions/0"


def architecture_candidate(trope):
    return {
        "schema_version": 2,
        "summary": "A ferry crossing where an inherited post and fear of the far shore pull against each other.",
        "nodes": [
            {"id": "gothic_mystery", "title": GENRE, "category": "genre",
             "summary": "Dread gathers around a shore nobody explains."},
            {"id": "inherited_post", "title": "Inherited post", "category": "theme",
             "summary": "Keeping a dead parent's duty."},
        ],
        "links": [{"id": "shore-tests-duty", "source": "gothic_mystery", "target": "inherited_post",
                   "function": "turns duty into risk"}],
        "emotion_targets": [{"id": "dread", "emotion": "fear", "role": "primary",
                             "intended_effect": "Unease about the far landing.",
                             "eliciting_condition": "Each crossing withholds more.",
                             "aesthetic_strategy": "Fog, bells and unanswered lights.",
                             "provenance": "agent_proposed"}],
        "genre_contracts": [{"genre_node_id": "gothic_mystery", "role": "governing",
                             "emotion_target_ids": ["dread"], "trope_functions": [trope],
                             "narrative_engine": "Each crossing reveals what the shore withholds.",
                             "structural_pattern": "Crossings escalate toward the landing no one returns from.",
                             "payoff_expectations": ["The shore's secret is named"]}],
    }


def complete_working_architecture(store, trope, instruction=""):
    """A host agent answers a source-bound request; a revision is applied as another session would."""
    pending = prepare_architecture(store, instruction)
    request = HostAgentRequest(**pending["request"])
    response = build_host_agent_response(request, json.dumps(architecture_candidate(trope)),
                                         runtime="browser-test", model="fixture")
    complete_architecture(store, response.model_dump())
    sha = pending["request"]["request_sha256"]
    if instruction:
        apply_architecture_review(store, sha)
    return sha


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


def seeded_store(root):
    store = CanvasStore(root, CANVAS)
    store.create()
    items = [
        ("scene-crossing", "scene", "The night crossing", OPENING, (60, 60)),
        ("char-mara", "character", "Mara, the pilot", "Keeps the lantern because her mother did.", (300, 60)),
        ("scene-landing", "scene", "Arrival at the far landing", "No one has stepped off here.", (60, 260)),
    ]
    for index, (item_id, kind, title, content, (x, y)) in enumerate(items):
        store.apply(
            "create-item", expected_revision=index, command_id=f"seed-{item_id}",
            payload={"item": {"id": item_id, "kind": kind, "title": title, "content": content},
                     "position": {"x": x, "y": y}},
        )
    doc = store.load()
    store.apply(
        "replace-working-document", expected_revision=doc.revision, command_id="seed-links",
        payload={
            "items": [item.model_dump(exclude_none=True) for item in doc.items],
            "connections": [{"id": "edge-pov", "source": "scene-crossing", "target": "char-mara",
                             "label": "point of view"}],
            "positions": {key: value.model_dump() for key, value in doc.positions.items()},
            "viewport": doc.viewport.model_dump(),
        },
    )
    return store


def scene_text(store, item_id="scene-crossing"):
    return next(item.content for item in store.load().items if item.id == item_id)


def wait_for_saved(page, store, expected):
    # The store is the evidence; a pause announcement may replace an earlier "saved locally" status.
    for _ in range(80):
        if scene_text(store) == expected:
            break
        page.wait_for_timeout(100)
    assert scene_text(store) == expected
    assert "SAVE FAILED" not in page.locator("#status").inner_text()


class Studio:
    def __init__(self, browser, root, width, height, architecture=False):
        self.store = seeded_store(root)
        self.architecture_sha = complete_working_architecture(self.store, TROPE) if architecture else None
        self.root = root
        self.server = BeginnerWorkspaceServer(root, port=0)
        self.thread = self.server.start_in_thread()
        self.page = browser.new_page(viewport={"width": width, "height": height})
        self.errors, self.requests = [], []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("request", lambda request: self.requests.append((request.method, request.url)))
        self.page.goto(f"http://127.0.0.1:{self.server.port}/studio.html?canvas={CANVAS}")
        self.wait_loaded()

    def wait_loaded(self):
        self.page.wait_for_function(
            "document.querySelector('#status').textContent.includes('Working canvas loaded')"
        )

    def close(self):
        self.page.close()
        self.server.stop()
        self.thread.join(timeout=2)
        assert not self.thread.is_alive()

    def selection(self):
        return self.page.evaluate(
            "() => { const t = document.querySelector('#scene-text');"
            " return [t.selectionStart, t.selectionEnd, document.activeElement.id]; }"
        )

    def assert_no_authority_or_generation(self):
        # Only the existing canvas open-on-load call and versioned working-document saves may write.
        opened = f"http://127.0.0.1:{self.server.port}/api/beginner/studio/canvases"
        mutations = [url for method, url in self.requests if method != "GET" and url != opened]
        assert mutations and all(url.endswith(f"/canvases/{CANVAS}/commands/replace-working-document")
                                 for url in mutations), mutations
        assert not any(name in url for _, url in self.requests
                       for name in ("quick-draft", "/architecture/prepare", "/realization/prepare", "accept"))
        assert not (self.root / "story_identity.yaml").exists()
        assert not (self.root / "blueprint.yaml").exists()
        assert self.errors == []


def test_inspecting_a_connected_item_pauses_writing_and_return_restores_exact_position(tmp_path, browser):
    studio = Studio(browser, tmp_path, 1440, 900)
    page = studio.page
    try:
        page.get_by_role("button", name="Story Realization").click()
        page.locator('#nodes .node[data-item-id="scene-crossing"]').click()
        page.get_by_role("button", name="Open scene editor").click()
        editor = page.locator("#scene-text")
        editor.wait_for()
        assert page.locator("#scene-heading").inner_text() == "The night crossing"
        editor.evaluate("(t, n) => { t.focus(); t.setSelectionRange(n, n); }", OPENING.index("."))
        page.keyboard.type(INSERT)
        page.keyboard.press("Shift+ArrowLeft")
        page.keyboard.press("Shift+ArrowLeft")
        written = OPENING.replace(".", INSERT + ".", 1)
        start, end, _ = studio.selection()
        assert (start, end) == (OPENING.index(".") + len(INSERT) - 2, OPENING.index(".") + len(INSERT))

        page.locator('#nodes .node[data-item-id="char-mara"]').click()
        assert page.locator("#scene-panel").is_hidden()
        assert page.locator("#title").input_value() == "Mara, the pilot"
        bar = page.locator("#writing-return")
        assert bar.is_visible()
        assert "The night crossing" in bar.inner_text()
        assert page.locator('#nodes .node[data-item-id="char-mara"]').get_attribute("aria-pressed") == "true"
        wait_for_saved(page, studio.store, written)

        # The paused position is an explicit contract, not the hidden textarea's leftover selection.
        editor.evaluate("t => { t.value = 'stale buffer'; t.setSelectionRange(0, 0); }")
        page.get_by_role("button", name="Return to Writing").click()
        assert page.locator("#scene-panel").is_visible()
        assert page.locator("#scene-heading").inner_text() == "The night crossing"
        assert editor.input_value() == written
        assert studio.selection() == [start, end, "scene-text"]
        assert bar.is_hidden()
        assert page.locator('#nodes .node[data-item-id="scene-crossing"]').get_attribute("aria-pressed") == "true"

        # Return to canvas still ends writing explicitly and offers no return.
        page.get_by_role("button", name="Return to canvas").click()
        assert page.locator("#scene-panel").is_hidden()
        assert bar.is_hidden()
        assert scene_text(studio.store) == written
        studio.assert_no_authority_or_generation()
    finally:
        studio.close()


def test_selecting_another_scene_inspects_it_until_its_editor_is_opened_explicitly(tmp_path, browser):
    studio = Studio(browser, tmp_path, 1440, 900)
    page = studio.page
    try:
        page.get_by_role("button", name="Story Realization").click()
        page.locator('#nodes .node[data-item-id="scene-crossing"]').click()
        page.get_by_role("button", name="Open scene editor").click()
        page.locator("#scene-text").evaluate("t => { t.focus(); t.setSelectionRange(5, 5); }")

        page.locator('#nodes .node[data-item-id="scene-landing"]').click()
        assert page.locator("#scene-panel").is_hidden()
        assert page.locator("#title").input_value() == "Arrival at the far landing"
        assert "The night crossing" in page.locator("#writing-return").inner_text()

        page.reload()
        studio.wait_loaded()
        page.locator('#nodes .node[data-item-id="scene-landing"]').wait_for(state="attached")
        assert page.locator("#writing-return").is_visible()
        assert "The night crossing" in page.locator("#writing-return").inner_text()

        page.get_by_role("button", name="Open scene editor").click()
        assert page.locator("#scene-heading").inner_text() == "Arrival at the far landing"
        assert page.locator("#writing-return").is_hidden()

        # Creating a working item mid-scene also pauses, rather than abandons, the writing task.
        page.get_by_role("button", name="+ Character").click()
        assert page.locator("#scene-panel").is_hidden()
        assert "Arrival at the far landing" in page.locator("#writing-return").inner_text()
        page.get_by_role("button", name="Return to Writing").click()
        assert page.locator("#scene-heading").inner_text() == "Arrival at the far landing"
        page.get_by_role("button", name="Return to canvas").click()
        assert page.locator("#writing-return").is_hidden()
        assert scene_text(studio.store) == OPENING
        studio.assert_no_authority_or_generation()
    finally:
        studio.close()


def test_rejected_save_keeps_live_text_and_never_reports_success_across_return(tmp_path, browser):
    studio = Studio(browser, tmp_path, 1440, 900)
    page = studio.page
    try:
        page.get_by_role("button", name="Story Realization").click()
        page.locator('#nodes .node[data-item-id="scene-crossing"]').click()
        page.get_by_role("button", name="Open scene editor").click()
        page.locator("#scene-text").evaluate("t => { t.focus(); t.setSelectionRange(t.value.length, t.value.length); }")
        page.keyboard.type(" Saved line.")
        wait_for_saved(page, studio.store, OPENING + " Saved line.")

        # Another writer advances the working document, so the next versioned save is rejected for real.
        studio.store.apply(
            "create-item", expected_revision=studio.store.load().revision, command_id="other-tab",
            payload={"item": {"id": "other-tab-note", "title": "Written elsewhere"}, "position": {"x": 500, "y": 500}},
        )
        page.keyboard.type(" Unsaved line.")
        page.wait_for_function("document.querySelector('#status').textContent.includes('SAVE FAILED')")

        page.locator('#nodes .node[data-item-id="char-mara"]').click()
        assert "SAVE FAILED" in page.locator("#status").inner_text()
        page.get_by_role("button", name="Return to Writing").click()
        assert page.locator("#scene-text").input_value() == OPENING + " Saved line. Unsaved line."
        assert "SAVE FAILED" in page.locator("#status").inner_text()
        assert "saved locally" not in page.locator("#status").inner_text()
        assert scene_text(studio.store) == OPENING + " Saved line."
        assert any(item.id == "other-tab-note" for item in studio.store.load().items)
    finally:
        studio.close()


def test_text_changed_while_paused_is_not_given_a_stale_cursor(tmp_path, browser):
    studio = Studio(browser, tmp_path, 1440, 900)
    page = studio.page
    try:
        page.get_by_role("button", name="Story Realization").click()
        page.locator('#nodes .node[data-item-id="scene-crossing"]').click()
        page.get_by_role("button", name="Open scene editor").click()
        page.locator("#scene-text").evaluate("t => { t.focus(); t.setSelectionRange(4, 4); }")
        page.locator('#nodes .node[data-item-id="char-mara"]').click()
        page.locator('#nodes .node[data-item-id="scene-crossing"]').click()
        page.locator("#content").fill("Rewritten while paused.")
        page.get_by_role("button", name="Return to Writing").click()
        assert studio.selection() == [23, 23, "scene-text"]
        assert "changed while you were away" in page.locator("#status").inner_text()
    finally:
        studio.close()


def test_keyboard_narrow_journey_inspects_from_editor_and_returns_focus(tmp_path, browser):
    studio = Studio(browser, tmp_path, 390, 844)
    page = studio.page
    try:
        page.get_by_role("button", name="Story Realization").focus()
        page.keyboard.press("Enter")
        page.locator('#nodes .node[data-item-id="scene-crossing"]').focus()
        page.keyboard.press("Enter")
        page.get_by_role("button", name="Open scene editor").focus()
        page.keyboard.press("Enter")
        editor = page.locator("#scene-text")
        assert studio.selection()[2] == "scene-text"
        page.keyboard.press("End")
        page.keyboard.type(" Night held.")
        written = OPENING + " Night held."
        start, end, _ = studio.selection()

        page.get_by_role("button", name="Return to canvas").focus()
        page.keyboard.press("Tab")
        connected = page.get_by_role("button", name="Inspect Mara, the pilot")
        assert connected.evaluate("b => b === document.activeElement")
        assert "point of view" in connected.inner_text()
        page.keyboard.press("Enter")
        assert page.locator("#scene-panel").is_hidden()
        assert page.locator("#title").input_value() == "Mara, the pilot"
        back = page.get_by_role("button", name="Return to Writing")
        assert back.evaluate("b => b === document.activeElement")
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        wait_for_saved(page, studio.store, written)

        page.keyboard.press("Enter")
        assert page.locator("#scene-panel").is_visible()
        assert editor.input_value() == written
        assert studio.selection() == [start, end, "scene-text"]
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        studio.assert_no_authority_or_generation()
    finally:
        studio.close()


def start_writing(studio):
    """Open the crossing scene, write mid-sentence and leave a two-character selection."""
    page = studio.page
    page.get_by_role("button", name="Story Realization").click()
    page.locator('#nodes .node[data-item-id="scene-crossing"]').click()
    page.get_by_role("button", name="Open scene editor").click()
    page.locator("#scene-text").evaluate("(t, n) => { t.focus(); t.setSelectionRange(n, n); }", OPENING.index("."))
    page.keyboard.type(INSERT)
    page.keyboard.press("Shift+ArrowLeft")
    page.keyboard.press("Shift+ArrowLeft")
    start, end, _ = studio.selection()
    return OPENING.replace(".", INSERT + ".", 1), start, end


def follow_trope_from_genre(page):
    page.locator('[data-architecture-facet="genres"]').click()
    assert page.locator(".studio-explanation-title").inner_text() == GENRE
    page.get_by_role("button", name=re.compile("^Explore " + TROPE)).click()
    assert page.locator(".studio-explanation-title").inner_text() == TROPE


def test_architecture_investigation_follows_a_source_link_and_returns_to_the_scene(tmp_path, browser):
    studio = Studio(browser, tmp_path, 1440, 900, architecture=True)
    page = studio.page
    try:
        written, start, end = start_writing(studio)
        page.get_by_role("button", name="Explore architecture").click()
        assert page.locator("#scene-panel").is_hidden()
        assert page.locator("#workspace-architecture").get_attribute("aria-pressed") == "true"
        bar = page.locator("#writing-return")
        assert bar.is_visible() and "The night crossing" in bar.inner_text()
        assert "Return to Writing resumes “The night crossing”" in page.locator("#status").inner_text()
        wait_for_saved(page, studio.store, written)

        follow_trope_from_genre(page)
        arrival = page.locator("#studio-semantic-arrival").inner_text()
        assert f"“{GENRE}” → lists trope function → “{TROPE}”" in arrival
        assert "not accepted story" in arrival and f"Source: {TROPE_REF}" in arrival
        assert bar.is_visible()

        # Previous context navigates the investigation's own trail; the writing origin is untouched.
        page.get_by_role("button", name="← Previous context").click()
        assert page.locator(".studio-explanation-title").inner_text() == GENRE
        assert page.locator("#studio-semantic-trail").is_hidden()
        assert bar.is_visible()
        follow_trope_from_genre(page)
        page.get_by_role("button", name=re.compile("^Inspect source")).focus()
        page.keyboard.press("Enter")
        assert "NOT ACCEPTED" in page.locator("#source-state").inner_text()
        assert f"Response {studio.architecture_sha}" in page.locator("#source-ref").inner_text()

        page.locator("#scene-text").evaluate("t => { t.value = 'stale buffer'; t.setSelectionRange(0, 0); }")
        page.get_by_role("button", name="Return to Writing").click()
        assert page.locator("#workspace-realization").get_attribute("aria-pressed") == "true"
        assert page.locator("#scene-heading").inner_text() == "The night crossing"
        assert page.locator("#scene-text").input_value() == written
        assert studio.selection() == [start, end, "scene-text"]
        assert bar.is_hidden()
        assert scene_text(studio.store) == written

        # Re-entering Architecture later finds its own local trail; no writing origin is left behind.
        page.get_by_role("button", name="Return to canvas").click()
        page.get_by_role("button", name="Narrative Architecture").click()
        assert page.locator("#studio-semantic-trail").is_visible()
        assert bar.is_hidden()
        studio.assert_no_authority_or_generation()
    finally:
        studio.close()


def test_keyboard_narrow_focus_writing_investigation_restores_range_scroll_and_mode(tmp_path, browser):
    studio = Studio(browser, tmp_path, 390, 844, architecture=True)
    page = studio.page
    try:
        page.get_by_role("button", name="Story Realization").focus()
        page.keyboard.press("Enter")
        page.locator('#nodes .node[data-item-id="scene-crossing"]').focus()
        page.keyboard.press("Enter")
        page.get_by_role("button", name="Open scene editor").focus()
        page.keyboard.press("Enter")
        page.get_by_role("button", name="Focus writing").focus()
        page.keyboard.press("Enter")
        editor = page.locator("#scene-text")
        editor.focus()
        page.keyboard.press("Control+End")
        page.keyboard.type("".join(f"\nThe bell rang {n}." for n in range(30)))
        page.keyboard.press("Shift+ArrowLeft")
        page.keyboard.press("Shift+ArrowLeft")
        start, end, _ = studio.selection()
        scroll = editor.evaluate("t => t.scrollTop")
        assert scroll > 0
        written = editor.input_value()

        page.get_by_role("button", name="Return to canvas").focus()
        page.keyboard.press("Shift+Tab")
        explore = page.get_by_role("button", name="Explore architecture")
        assert explore.evaluate("b => b === document.activeElement")
        page.keyboard.press("Enter")
        assert page.locator("#scene-panel").is_hidden()
        assert page.evaluate("document.activeElement.dataset.architectureFacet") == "overview"
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        wait_for_saved(page, studio.store, written)

        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.dataset.architectureFacet") == "genres"
        page.keyboard.press("Enter")
        page.get_by_role("button", name=re.compile("^Explore " + TROPE)).focus()
        page.keyboard.press("Enter")
        assert page.locator(".studio-explanation-title").inner_text() == TROPE
        back = page.get_by_role("button", name="Return to Writing")
        box = back.bounding_box()
        assert box and 0 <= box["y"] and box["y"] + box["height"] <= 844 and box["x"] + box["width"] <= 390
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")

        # Return to Writing is reachable in the keyboard order from the explanation itself.
        for _ in range(80):
            if back.evaluate("b => b === document.activeElement"):
                break
            page.keyboard.press("Shift+Tab")
        assert back.evaluate("b => b === document.activeElement")
        page.keyboard.press("Enter")
        assert page.locator("#scene-panel").is_visible()
        assert "expanded" in page.locator("#scene-panel").get_attribute("class")
        assert editor.input_value() == written
        assert studio.selection() == [start, end, "scene-text"]
        assert abs(editor.evaluate("t => t.scrollTop") - scroll) <= 1
        studio.assert_no_authority_or_generation()
    finally:
        studio.close()


def test_architecture_source_change_while_investigating_is_announced_and_writing_still_returns(tmp_path, browser):
    studio = Studio(browser, tmp_path, 1440, 900, architecture=True)
    page = studio.page
    try:
        written, start, end = start_writing(studio)
        page.get_by_role("button", name="Narrative Architecture").click()
        bar = page.locator("#writing-return")
        assert page.locator("#scene-panel").is_hidden() and bar.is_visible()
        wait_for_saved(page, studio.store, written)
        follow_trope_from_genre(page)

        # Another session applies a revised working architecture whose trope has a similar title.
        complete_working_architecture(studio.store, "The keeper who will not leave her post",
                                      "Sharpen the keeper's refusal.")
        page.get_by_role("button", name="Check agent result").click()
        page.wait_for_function(
            "document.querySelector('#status').textContent.includes('Previous semantic source changed')"
        )
        assert page.locator("#studio-semantic-arrival").is_hidden()
        assert page.locator("#studio-semantic-trail").is_hidden()
        assert TROPE not in page.locator("#studio-explanatory-hero").inner_text()
        assert bar.is_visible()

        page.reload()
        studio.wait_loaded()
        assert page.locator("#workspace-architecture").get_attribute("aria-pressed") == "true"
        assert bar.is_visible() and "The night crossing" in bar.inner_text()
        page.get_by_role("button", name="Return to Writing").click()
        assert page.locator("#scene-text").input_value() == written
        assert studio.selection() == [start, end, "scene-text"]
        assert scene_text(studio.store) == written
        studio.assert_no_authority_or_generation()
    finally:
        studio.close()
