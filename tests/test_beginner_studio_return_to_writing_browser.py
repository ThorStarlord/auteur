"""Return to Writing: inspecting a working item pauses, never replaces, the writing task (#603)."""
import os

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_store import CanvasStore

CANVAS = "ferry-story"
OPENING = "Mara pushed off before the bell finished ringing. The fog took the bank behind her."
INSERT = " She did not look back"


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
    page.wait_for_function(
        "document.querySelector('#status').textContent.includes('saved locally')"
    )
    for _ in range(40):
        if scene_text(store) == expected:
            return
        page.wait_for_timeout(100)
    assert scene_text(store) == expected


class Studio:
    def __init__(self, browser, root, width, height):
        self.store = seeded_store(root)
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
