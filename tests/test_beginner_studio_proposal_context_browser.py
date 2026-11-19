"""A copied scene shows its proposal's relationships and Architecture sources without accepting them (#613)."""
import json
import os
import re

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import (
    apply_architecture_review, complete_architecture, prepare_architecture,
)
from auteur.beginner.studio_realization import complete_realization, prepare_realization
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

ARCHITECTURE = {
    "schema_version": 2, "summary": "Copying debts binds the keeper to the island.",
    "nodes": [
        {"id": "copying_engine", "title": "Nightly copying", "category": "engine",
         "summary": "Each night of copying deepens complicity."},
        {"id": "sacred_ledger", "title": "The sacred ledger", "category": "theme",
         "summary": "What is written is owed."},
    ],
    "links": [{"id": "binds", "source": "copying_engine", "target": "sacred_ledger", "function": "binds"}],
}
REALIZATION = {
    "schema_version": 1, "summary": "A keeper, her brother and a page.",
    "elements": [
        {"id": "scene-copying", "kind": "scene", "title": "The page with his name",
         "description": "Ines reaches her brother's entry.", "architecture_refs": ["copying_engine", "sacred_ledger"]},
        {"id": "ines", "kind": "character", "title": "Ines Varga", "description": "The ledger keeper.",
         "architecture_refs": ["copying_engine"]},
        {"id": "tomas", "kind": "character", "title": "Tomas Varga", "description": "Her brother, gone.",
         "architecture_refs": ["sacred_ledger"]},
    ],
    "links": [
        {"id": "pov", "source": "scene-copying", "target": "ines", "function": "point of view"},
        {"id": "named", "source": "scene-copying", "target": "tomas", "function": "names"},
        {"id": "siblings", "source": "ines", "target": "tomas", "function": "sister of"},
    ],
    "architecture_feedback": [], "open_questions": [],
}


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


def reply(status, data):
    request = HostAgentRequest(**status["request"])
    return build_host_agent_response(request, json.dumps(data), runtime="browser-test", model="fixture").model_dump()


def story(root):
    store = CanvasStore(root, "tide")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={
        "item": {"id": "story-vision", "title": "Story Vision", "content": "A keeper copies the island's debts."},
        "position": {"x": 20, "y": 20}})
    complete_architecture(store, reply(prepare_architecture(store), ARCHITECTURE))
    pending = prepare_realization(store, [])
    complete_realization(store, reply(pending, REALIZATION))
    return store, pending["request"]["request_sha256"]


def test_copied_scene_offers_suggested_relationships_and_its_architecture(tmp_path, browser):
    store, realization_sha = story(tmp_path)
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    saved = 'document.querySelector("#status").textContent.includes("saved locally")'
    base = f"http://127.0.0.1:{server.port}/studio.html?canvas=tide"

    def open_scene():
        if page.locator("#scene-panel").is_visible():  # re-entry restores the open editor (#605)
            assert page.locator("#scene-heading").inner_text() == "The page with his name"
            page.locator("#scene-proposal").wait_for()
            return
        page.locator("#workspace-realization").click()
        page.locator("#layer-view").select_option("create")
        page.locator(f'#nodes .node[data-item-id="{scene_id}"]').click()
        page.locator("#write").click()
        page.locator("#scene-proposal").wait_for()

    try:
        page.goto(base)
        page.wait_for_function('!document.querySelector("#canvas-picker").disabled')
        page.locator("#workspace-realization").click()
        for element in ("scene-copying", "ines"):
            page.locator("#layer-view").select_option("realization_candidates")
            page.locator(f'#nodes .node.realization[data-item-id="{element}"]').click()
            page.locator("#realization-copy").click()
            page.wait_for_function(saved)
        canvas = store.load()
        scene_id = next(i.id for i in canvas.items if i.proposal_origin and i.proposal_origin.focus_id == "scene-copying")
        ines_id = next(i.id for i in canvas.items if i.proposal_origin and i.proposal_origin.focus_id == "ines")
        assert canvas.connections == []

        open_scene()
        refs = page.locator("#scene-architecture-refs button")
        assert refs.all_inner_texts() == ["Nightly copying", "The sacred ledger"]
        page.wait_for_function('document.querySelectorAll("#scene-suggested-relationships li").length === 2')
        suggestions = page.locator("#scene-suggested-relationships li").all_inner_texts()
        assert any("point of view · Ines Varga" in s and "Keep as working connection" in s for s in suggestions)
        assert any("names · Tomas Varga (still only a proposal)" in s and "Keep" not in s for s in suggestions)
        # A suggestion is visible but is not the author's connection until kept.
        assert store.load().connections == []
        assert page.locator("#scene-connections").is_hidden()

        page.get_by_role("button", name="Keep as working connection: “point of view” with Ines Varga").click()
        page.wait_for_function(saved)
        kept = store.load().connections
        assert [(e.source, e.target, e.label) for e in kept] == [(scene_id, ines_id, "point of view")]
        assert re.fullmatch(r"kept-[a-f0-9]{12}-[a-f0-9]+-pov", kept[0].id)
        # Keyboard focus stays on the outcome of the action, not the page body.
        assert page.evaluate("document.activeElement.dataset.kept") == "pov"
        assert page.get_by_role("button", name="Keep as working connection: “point of view” with Ines Varga").count() == 0
        assert "Connected on your canvas" in page.locator("#scene-suggested-relationships").inner_text()
        assert page.locator("#scene-connection-list").inner_text().split() == [
            "Inspect", "Ines", "Varga", "point", "of", "view"]

        # Write, inspect a source from the scene, and return to the same place.
        text = page.locator("#scene-text")
        text.fill("Low tide. She found her place.")
        text.evaluate("t => { t.focus(); t.setSelectionRange(9, 9); }")
        page.wait_for_function(saved)
        refs.first.click()
        assert page.locator("#workspace-architecture").get_attribute("aria-pressed") == "true"
        assert "Nightly copying" in page.locator("main").inner_text()
        page.get_by_role("button", name="Return to Writing").click()
        assert page.locator("#scene-heading").inner_text() == "The page with his name"
        assert text.evaluate("t => [document.activeElement === t, t.selectionStart]") == [True, 9]
        assert store.load().items[[i.id for i in store.load().items].index(scene_id)].content == (
            "Low tide. She found her place.")

        # Re-entry keeps the source identity; no duplicate connection can be created.
        page.reload()
        page.wait_for_function('!document.querySelector("#canvas-picker").disabled')
        open_scene()
        page.wait_for_function('document.querySelectorAll("#scene-suggested-relationships li").length === 2')
        assert "Connected on your canvas" in page.locator("#scene-suggested-relationships").inner_text()
        assert len(store.load().connections) == 1

        # Narrow screen: the context stays reachable without horizontal overflow.
        page.set_viewport_size({"width": 375, "height": 812})
        assert page.evaluate("document.querySelector('#scene-proposal').getBoundingClientRect().right") <= 375
        page.set_viewport_size({"width": 1440, "height": 900})

        # A revised Architecture is reported, never silently substituted.
        revision = prepare_architecture(store, "Make the ledger a living debt.")
        complete_architecture(store, reply(revision, {**ARCHITECTURE, "summary": "The ledger is alive."}))
        apply_architecture_review(store, revision["request"]["request_sha256"])
        page.reload()
        page.wait_for_function('!document.querySelector("#canvas-picker").disabled')
        open_scene()
        assert "revised since this proposal was made" in page.locator("#scene-proposal-notice").inner_text()
        assert refs.first.inner_text() == "Nightly copying (current version)"

        # A missing proposal source is reported honestly.
        (store.directory / "realization" / "requests" / realization_sha / "response.json").unlink()
        page.reload()
        page.wait_for_function('!document.querySelector("#canvas-picker").disabled')
        open_scene()
        page.wait_for_function(
            'document.querySelector("#scene-proposal-notice").textContent.includes("unavailable")')
        assert page.locator("#scene-suggested-relationships li").count() == 0
        assert not (tmp_path / "story_identity.yaml").exists()
        assert errors == []
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
