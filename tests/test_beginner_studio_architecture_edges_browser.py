"""Real Studio rendering for directed narrative architecture links."""
import json
import os
import re

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
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


def test_architecture_link_direction_and_reciprocity_in_studio(tmp_path, browser):
    store = CanvasStore(tmp_path, "edge-probe")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision",
                payload={"item": {"id": "vision", "kind": "note", "title": "Story Vision",
                                  "content": "A story about how people make meaning."},
                          "position": {"x": 20, "y": 20}})
    waiting = prepare_architecture(store)
    candidate = {
        "schema_version": 2,
        "summary": "Three related mechanisms with declared direction.",
        "nodes": [
            {"id": "a", "title": "Inquiry engine", "category": "engine",
             "summary": "Inquiry changes the choices available."},
            {"id": "b", "title": "Shared ritual", "category": "trope",
             "summary": "Rituals make decisions visible."},
            {"id": "c", "title": "Trust theme", "category": "theme",
             "summary": "Trust depends on revisable knowledge."},
        ],
        "links": [
            {"id": "a-to-b", "source": "a", "target": "b", "function": "Inquiry shapes ritual."},
            {"id": "b-to-a", "source": "b", "target": "a", "function": "Ritual redirects inquiry."},
            {"id": "c-to-a", "source": "c", "target": "a", "function": "Trust constrains inquiry."},
        ],
        "phases": [], "open_questions": [],
    }
    request = HostAgentRequest(**waiting["request"])
    response = build_host_agent_response(request, json.dumps(candidate),
                                         runtime="browser-test", model="fixture")
    complete_architecture(store, response.model_dump())

    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=edge-probe")
        page.locator('[data-architecture-link-id="a-to-b"]').wait_for()
        paths = page.locator("#edges [data-architecture-link-id]")
        assert paths.count() == 3
        by_id = {
            edge_id: page.locator(f'[data-architecture-link-id="{edge_id}"]')
            for edge_id in ("a-to-b", "b-to-a", "c-to-a")
        }
        for path in by_id.values():
            assert path.get_attribute("marker-end") == "url(#architecture-link-arrow)"
        assert by_id["a-to-b"].get_attribute("d") != by_id["b-to-a"].get_attribute("d")

        # The path ends at the target card boundary, leaving its arrowhead visible.
        path_numbers = [float(number) for number in re.findall(
            r"-?\d+(?:\.\d+)?", by_id["c-to-a"].get_attribute("d"),
        )]
        end_x, end_y = path_numbers[-2:]
        target_box = page.locator('[data-item-id="a"]').evaluate(
            "node => ({left: parseFloat(node.style.left), top: parseFloat(node.style.top), "
            "width: node.offsetWidth, height: node.offsetHeight})",
        )
        on_boundary = (
            abs(end_x - target_box["left"]) < 2
            or abs(end_x - target_box["left"] - target_box["width"]) < 2
            or abs(end_y - target_box["top"]) < 2
            or abs(end_y - target_box["top"] - target_box["height"]) < 2
        )
        assert on_boundary

        page.locator('[data-item-id="a"]').click()
        labels = page.locator("#source-links .facet-link").all_text_contents()
        assert "Outgoing to Shared ritual: Inquiry shapes ritual." in labels
        assert "Incoming from Shared ritual: Ritual redirects inquiry." in labels
        assert "Incoming from Trust theme: Trust constrains inquiry." in labels
        assert errors == []
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
