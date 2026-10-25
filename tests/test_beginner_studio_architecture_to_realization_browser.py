"""Architecture context leads into source-focused, explicitly requested realization."""
import json
import os

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_realization import (
    complete_realization, prepare_realization, project_realization,
)
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

def test_realization_scene_carries_editable_intent_to_quick_draft(tmp_path, browser):
    """A source-linked concrete scene becomes editable, but never automatically accepted."""
    story = "A recurring allocation changes what people owe one another."
    scene = "In the flood assembly, neighbors negotiate repairs before any claim is settled."
    store = store_with_architecture(tmp_path, "scene-bridge")
    pending = prepare_realization(store, ["allocation_engine"])
    request = HostAgentRequest(**pending["request"])
    proposal = {
        "schema_version": 1,
        "summary": "One proposed concrete scene, not accepted story.",
        "elements": [{
            "id": "assembly_scene", "kind": "scene", "title": "Assembly after the storm",
            "description": scene, "architecture_refs": ["allocation_engine"],
        }],
        "links": [], "architecture_feedback": [], "open_questions": [],
    }
    response = build_host_agent_response(
        request, json.dumps(proposal), runtime="browser-test", model="fixture",
    )
    assert complete_realization(store, response.model_dump())["status"] == "ready"

    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    quick_draft_requests = []
    def observe_request(request):
        if request.method == "POST" and request.url.endswith("/api/beginner/quick-draft"):
            quick_draft_requests.append(json.loads(request.post_data))
    page.on("request", observe_request)
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=scene-bridge")
        page.locator("#workspace-realization").click()
        page.locator("#layer-view").select_option("realization_candidates")
        page.locator('#nodes .node.realization[data-item-id="assembly_scene"]').click()
        page.locator("#realization-copy").click()
        page.locator("#write").click()

        # The model's concrete proposal stays editable and working only.
        # The generation intent must never contain appended provenance labels.
        assert page.locator("#scene-intent").input_value() == scene
        assert page.locator("#scene-premise").input_value() == ""
        assert "Architecture refs: allocation_engine" in page.locator("#scene-text").input_value()
        assert "Architecture refs:" not in page.locator("#scene-intent").input_value()
        # Reusing notes must not silently place machine provenance in a model prompt.
        page.locator("#use-scene-as-intent").click()
        assert "provenance footer" in page.locator("#generation-status").inner_text()
        assert page.locator("#scene-intent").input_value() == scene
        assert quick_draft_requests == []

        # Premise is NOT inferred from a Story Vision that might only describe mood.
        page.locator("#generate-scene").click()
        assert "premise and a scene intent" in page.locator("#generation-status").inner_text()
        assert quick_draft_requests == []
        page.locator("#use-vision-as-premise").click()
        assert page.locator("#scene-premise").input_value() == story
        assert quick_draft_requests == []

        # The explicit copy must not overwrite a user-edited premise.
        authored_premise = "A town decides how to share the water and repair the canal."
        authored_scene = "The assembly refuses a seemingly fair but harmful compromise."
        page.locator("#scene-premise").fill(authored_premise)
        page.locator("#use-vision-as-premise").click()
        assert page.locator("#scene-premise").input_value() == authored_premise
        page.locator("#scene-intent").fill(authored_scene)

        # Quick Draft is staged only through a fresh, explicit action.
        with page.expect_response(
            lambda res: res.url.endswith("/api/beginner/quick-draft")
            and res.request.method == "POST"
        ) as staging:
            page.locator("#generate-scene").click()
        assert staging.value.status == 202
        assert quick_draft_requests == [{
            "premise": authored_premise, "first_scene": authored_scene,
        }]
        page.locator("#save-scene").click()
        page.wait_for_function(
            'document.querySelector("#status").textContent.includes("Working canvas saved locally")'
        )
        saved = store.load()
        copied = [item for item in saved.items if item.title == "Assembly after the storm"]
        assert len(copied) == 1
        assert copied[0].scene_premise == authored_premise
        assert copied[0].scene_intent == authored_scene
        assert copied[0].quick_draft_session_id
        assert not (tmp_path / "story_identity.yaml").exists()
        assert not (tmp_path / "blueprint.yaml").exists()
        assert not (tmp_path / "chapters").exists()

        page.reload()
        page.locator("#write").click()
        assert page.locator("#scene-premise").input_value() == authored_premise
        assert page.locator("#scene-intent").input_value() == authored_scene
        assert page.locator("#refresh-draft").is_visible()
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
