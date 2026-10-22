"""Bare Studio re-entry preserves the author's saved working perspective."""
import json
import os

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_store import CanvasStore


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


@pytest.mark.parametrize("saved_view", ["architecture", "book"])
def test_bare_studio_reentry_preserves_saved_book_or_architecture_view(
    tmp_path, browser, saved_view,
):
    canvas_id = "resume-canvas"
    store = CanvasStore(tmp_path, canvas_id)
    store.create()
    store.apply(
        "create-item",
        expected_revision=0,
        command_id="create-note",
        payload={
            "item": {"id": "working-note", "title": "Working architecture"},
            "position": {"x": 60, "y": 80},
        },
    )
    initial_revision = store.load().revision
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    focus = {
        "selected": "working-note",
        "view": saved_view,
        "workspace": "realization" if saved_view == "book" else "architecture",
        "group": "",
        "facet": "overview",
    }
    page.add_init_script(
        "localStorage.setItem('auteur:studio:focus:resume-canvas', "
        + json.dumps(json.dumps(focus))
        + ");"
    )
    page.route(
        "**/api/beginner/book/progress",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({
                "current_chapter": 2,
                "current_chapter_state": "Working",
                "discovered_chapters": 2,
                "accepted_chapters": 1,
                "planned_chapters": 2,
                "accepted_chapter_refs": ["chapters/01/final.md"],
                "next_story_action": "Continue Chapter 2",
                "recent_changes": [],
                "pending_updates": [],
                "needs_attention": [],
                "orientation_reason": "Chapter 2 is in progress.",
            }),
        ),
    )
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html")
        page.locator("#status").wait_for(state="attached")
        page.wait_for_function(
            "document.querySelector('#canvas-picker').value === 'resume-canvas'"
        )
        page.wait_for_function(
            "document.querySelector('#layer-view').value === "
            + json.dumps("book" if saved_view == "book" else "architecture")
        )
        assert page.locator("#book-orientation").is_visible() == (saved_view == "book")
        assert page.locator("#workspace-architecture").get_attribute("aria-pressed") == (
            "false" if saved_view == "book" else "true"
        )
        assert page.locator("#workspace-realization").get_attribute("aria-pressed") == (
            "true" if saved_view == "book" else "false"
        )
        assert errors == []
        assert store.load().revision == initial_revision
        assert [item.id for item in store.load().items] == ["working-note"]
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
