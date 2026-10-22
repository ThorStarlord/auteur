"""Architecture context leads into source-focused, explicitly requested realization."""
import json
import os

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_realization import project_realization
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


def store_with_architecture(root, canvas_id):
    store = CanvasStore(root, canvas_id)
    store.create()
    store.apply(
        "create-item",
        expected_revision=0,
        command_id="vision",
        payload={
            "item": {
                "id": "story-vision",
                "kind": "note",
                "title": "Story Vision",
                "content": "A recurring allocation changes what people owe one another.",
            },
            "position": {"x": 40, "y": 50},
        },
    )
    pending = prepare_architecture(store)
    request = HostAgentRequest(**pending["request"])
    candidate = {
        "schema_version": 2,
        "summary": "Recurring allocation turns shared constraints into contested choices.",
        "nodes": [
            {
                "id": "allocation_engine",
                "title": "Water allocation process",
                "category": "engine",
                "summary": "Communities negotiate distribution and repair priorities.",
            },
            {
                "id": "inherited_obligation",
                "title": "Inherited obligations",
                "category": "theme",
                "summary": "Past decisions become present claims.",
            },
        ],
        "links": [
            {
                "id": "allocation-carries-forward",
                "source": "allocation_engine",
                "target": "inherited_obligation",
                "function": "Decisions create claims that return in later cycles.",
            },
        ],
    }
    response = build_host_agent_response(
        request, json.dumps(candidate), runtime="browser-test", model="fixture",
    )
    complete_architecture(store, response.model_dump())
    return store


def realization_focus(store):
    projection = project_realization(store)
    assert projection["request"] is not None
    request_user = json.loads(projection["request"]["user"])
    return request_user["source"]["focus_ids"]


def test_component_continuation_preserves_focus_and_whole_story_remains_available(
    tmp_path, browser,
):
    focused = store_with_architecture(tmp_path, "focused-story")
    whole = store_with_architecture(tmp_path, "whole-story")
    focused_revision = focused.load().revision
    whole_revision = whole.load().revision
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    requests = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda request: requests.append((request.method, request.url)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=focused-story")
        engine = page.locator('#nodes .node.candidate[data-item-id="allocation_engine"]')
        engine.wait_for()
        engine.click()
        assert page.locator("#source-title").inner_text() == "Water allocation process"
        assert "Communities negotiate distribution" in page.locator("#source-description").inner_text()
        assert page.locator("#architecture-realization-continuation").is_visible()

        page.get_by_role("button", name="Develop this in Story Realization").click()
        assert page.locator("#realization-focus-label").inner_text() == (
            "Architecture focus: Water allocation process"
        )
        assert not any(method == "POST" and "/realization/prepare" in url
                       for method, url in requests)
        assert focused.load().revision == focused_revision
        assert project_realization(focused)["request"] is None

        page.get_by_role("button", name="Develop concrete story material").click()
        page.locator("#realization-handoff").wait_for(state="visible")
        assert realization_focus(focused) == ["allocation_engine"]
        assert page.locator("#realization-request").input_value()
        assert focused.load().revision == focused_revision
        assert not (tmp_path / "story_identity.yaml").exists()
        assert not (tmp_path / "blueprint.yaml").exists()

        page.get_by_role("button", name="Narrative Architecture").click()
        assert page.locator("#source-title").inner_text() == "Water allocation process"
        assert page.locator("#architecture-realization-continuation").is_visible()
        page.reload()
        page.locator('#nodes .node.candidate[data-item-id="allocation_engine"]').wait_for()
        assert page.locator("#source-title").inner_text() == "Water allocation process"
        assert page.locator('#nodes .node.candidate[data-item-id="allocation_engine"]')\
            .get_attribute("aria-pressed") == "true"
        assert focused.load().revision == focused_revision

        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=whole-story")
        page.locator('#nodes .node.candidate[data-item-id="allocation_engine"]').wait_for()
        assert page.locator("#architecture-realization-continuation").is_hidden()
        page.get_by_role("button", name="Story Realization").click()
        assert page.locator("#realization-focus-label").inner_text() == "Architecture focus: whole story"
        page.get_by_role("button", name="Develop concrete story material").click()
        page.locator("#realization-handoff").wait_for(state="visible")
        assert realization_focus(whole) == []
        assert whole.load().revision == whole_revision
        assert not (tmp_path / "story_identity.yaml").exists()
        assert not (tmp_path / "blueprint.yaml").exists()
        assert errors == []
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
