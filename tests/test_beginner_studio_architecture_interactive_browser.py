"""Served-browser journey for graph-grounded creative deliberation (Chromium through Playwright).

Evidence class: automated served Chromium with a SIMULATED host-agent answer. The inquiry response is a
labelled fixture submitted through the real HTTP route. This is not an independent coding-agent execution
and not human author evidence.
"""
from __future__ import annotations

import json
import os

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_architecture_inquiry import (
    complete_architecture_inquiry, prepare_architecture_inquiry,
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


def _seeded_thread(root):
    store = CanvasStore(root, "creative-thread")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision",
        payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision",
                          "content": "A recurring allocation changes what people owe one another."},
                 "position": {"x": 40, "y": 50}},
    )
    pending = prepare_architecture(store)
    candidate = {
        "schema_version": 2,
        "summary": "Recurring allocation turns shared constraints into contested choices.",
        "nodes": [
            {"id": "allocation_engine", "title": "Water allocation process", "category": "engine",
             "summary": "Communities negotiate distribution and repair priorities."},
            {"id": "inherited_obligation", "title": "Inherited obligations", "category": "theme",
             "summary": "Past decisions become present claims."},
        ],
        "links": [{"id": "allocation-carries-forward", "source": "allocation_engine",
                   "target": "inherited_obligation",
                   "function": "Decisions create claims that return in later cycles."}],
    }
    complete_architecture(store, build_host_agent_response(
        HostAgentRequest(**pending["request"]), json.dumps(candidate),
        runtime="browser-test", model="fixture",
    ).model_dump())
    return store


def _simulated_exploration(store):
    """Labelled fixture: a completed explore inquiry submitted through the real completion contract."""
    from auteur.beginner.studio_architecture import project_architecture

    baseline = project_architecture(store)["candidate_request_sha256"]
    pending = prepare_architecture_inquiry(store, {
        "version": 1, "canvas_id": store.canvas_id, "operation": "explore",
        "expected_candidate_request_sha256": baseline,
        "anchors": [{"kind": "node", "id": "allocation_engine"}],
        "author_text": "What other mechanisms could drive the allocation?",
    })
    answer = {
        "schema_version": 1,
        "analysis": "Two causal variables could change: who holds the allocation and whether claims expire.",
        "recorded_observations": [{"kind": "node", "id": "allocation_engine",
                                   "claim": "Communities negotiate distribution."}],
        "hypotheses": [
            {"title": "Rotating stewardship", "description": "Stewardship rotates so no household keeps the claim.",
             "divergence_axis": "character_agency"},
            {"title": "Expiring claims", "description": "Obligations lapse unless renewed by the community.",
             "divergence_axis": "structure"},
        ],
        "uncertainties": ["The candidate does not record who currently holds the allocation."],
    }
    request = HostAgentRequest(**pending["request"])
    complete_architecture_inquiry(store, build_host_agent_response(
        request, json.dumps(answer), runtime="browser-test", model="fixture",
    ).model_dump())
    return pending["request_sha256"]


def test_graph_selection_shows_earlier_exchanges_and_prepares_inquiry_without_revision(tmp_path, browser):
    store = _seeded_thread(tmp_path)
    _simulated_exploration(store)
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors, posts = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda message: errors.append(message.text)
            if message.type == "error" else None)
    page.on("request", lambda request: posts.append((request.method, request.url))
            if request.method == "POST" else None)
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=creative-thread")
        engine = page.locator('#nodes .node.candidate[data-item-id="allocation_engine"]')
        engine.wait_for()
        engine.click()
        disclosure = page.locator("#architecture-creative-graph")
        assert disclosure.evaluate("el => el.open") is True
        chips = page.locator('[aria-label="Selected source anchors"]')
        assert "node · allocation_engine" in chips.inner_text()
        history = page.locator('[aria-label="Earlier creative exchanges"]')
        history.wait_for()
        assert "What other mechanisms could drive the allocation?" in history.inner_text()
        assert "h1 Rotating stewardship" in history.inner_text()

        page.locator('[aria-label="Your creative intention"]').fill(
            "Develop the expiring-claims idea without changing the architecture yet.")
        page.locator('[data-operation="explore"]').first.click()
        page.locator('[data-creative-submit="true"]').click()
        page.wait_for_function(
            "() => document.querySelector('[aria-label=\"Prepared host-agent request\"]').value.length > 0")
        packet = page.locator('[aria-label="Prepared host-agent request"]').input_value()
        assert "studio_architecture_inquiry" in packet
        assert "prior_exchanges" in packet
        status = page.locator('#architecture-creative-agent-panel [role="status"]').inner_text()
        assert "not executed" in status
        assert not any("/architecture/prepare" in url for method, url in posts), posts
        assert not any("/architecture/inquiry/host-agent-response" in url for method, url in posts)
        assert not errors, errors
    finally:
        page.close()
        server.stop()


def test_selected_alternative_reaches_the_revision_request_and_nothing_is_applied(tmp_path, browser):
    store = _seeded_thread(tmp_path)
    _simulated_exploration(store)
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    revision_bodies = []
    page.on("request", lambda request: revision_bodies.append(request.post_data)
            if request.method == "POST" and request.url.endswith("/architecture/prepare") else None)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=creative-thread")
        page.locator('#nodes .node.candidate[data-item-id="allocation_engine"]').click()
        page.locator('[aria-label="Earlier creative exchanges"]').wait_for()
        button = page.locator('[data-alternative-id="h2"]')
        button.wait_for()
        button.click()
        panel_status = page.locator('#architecture-creative-agent-panel [role="status"]')
        assert "Write what you want to develop from h2 first" in panel_status.inner_text()
        assert not revision_bodies
        page.locator('[aria-label="Your creative intention"]').fill(
            "Adopt expiring claims and rebalance the cost of renewal.")
        button.click()
        page.wait_for_function("() => /Awaiting the active coding agent/.test("
                               "document.querySelector('#architecture-status').textContent)")
        assert len(revision_bodies) == 1
        body = json.loads(revision_bodies[0])
        assert body["selected_alternative"]["hypothesis_id"] == "h2"
        assert body["graph_intent"]["operation"] == "revise"
        assert body["instruction"].startswith("Adopt expiring claims")
        assert errors == []
    finally:
        page.close()
        server.stop()
    from auteur.beginner.studio_architecture import project_architecture
    projection = project_architecture(store)
    assert projection["status"] == "awaiting_host_agent"
    assert projection["candidate"]["summary"].startswith("Recurring allocation")
