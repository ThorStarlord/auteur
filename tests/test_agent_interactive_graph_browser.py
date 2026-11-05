"""Served-browser checks for the isolated agent-interactive graph prototype.

These tests use the repository's real static files and, for the baseline check,
the real current Studio server. A skipped test means the browser dependency is
unavailable; it is not a passing result.
"""
from __future__ import annotations

import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

playwright_sync = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROTOTYPE = "/docs/prototypes/agent-interactive-graph/index.html"
EVIDENCE = ROOT / "docs" / "qualification-evidence" / "agent-first-ontology-20261103"


@pytest.fixture(scope="module")
def static_server():
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        try:
            chromium = playwright.chromium.launch()
        except Exception as exc:  # pragma: no cover - environment-dependent
            pytest.skip(f"Chromium/Playwright unavailable: {exc}")
        try:
            yield chromium
        finally:
            chromium.close()


def open_prototype(browser, base):
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("console", lambda message: errors.append(message.text)
            if message.type == "error" else None)
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base + PROTOTYPE, wait_until="networkidle")
    page.wait_for_selector("#source-status", timeout=20000)
    return page, errors


def select_anchor(page, kind, anchor_id):
    page.locator(
        f'[data-anchor-kind="{kind}"][data-anchor-id="{anchor_id}"]'
    ).first.click()


def test_b1_served_inspection_draft_stale_and_mobile(browser, static_server):
    page, errors = open_prototype(browser, static_server)
    try:
        page.evaluate(
            "() => { window.__requestCount = 0; window.__originalFetch = window.fetch; "
            "window.fetch = (...args) => { window.__requestCount += 1; "
            "return window.__originalFetch(...args); }; window.__storageBefore = localStorage.length; }"
        )
        source = page.locator("#source-status").inner_text()
        assert "c6269dc2e1953498ced08c1e32fa10b4d7bf05274e72c6214bd8b1f5074b5d66" in source
        assert "working proposal" in source.lower()

        select_anchor(page, "node", "memory_economy")
        assert page.locator("#focus-title").inner_text() == "Memory economy"
        assert "nodes/3" in page.locator("#focus-source").inner_text()
        page.locator('[data-relation-id="engine_drives_cost"]').first.click()
        detail = page.locator("#relation-detail").inner_text()
        assert "links/3" in detail
        assert "personal loss" in detail.lower()
        page.locator("#back-to-entity").click()
        assert page.locator("#focus-title").inner_text() == "Memory economy"

        select_anchor(page, "emotion_target", "wonder")
        assert "No recorded relation" in page.locator("#relation-empty").inner_text()
        page.locator("#author-intention").fill(
            "How might the memory economy shape wonder without asserting a link?"
        )
        page.locator("#prepare-draft").click()
        status = page.locator("#draft-status").inner_text()
        assert "prepared_not_executed" in status
        draft = page.locator("#draft-output").input_value()
        assert "How might the memory economy shape wonder" in draft
        assert "No recorded relation" in draft
        assert "memory_economy" in draft
        assert "emotion_targets/0" in draft
        assert page.evaluate("window.__requestCount") == 0
        assert page.evaluate("localStorage.length") == page.evaluate("window.__storageBefore")

        page.locator("#simulate-stale").click()
        assert "STALE SOURCE" in page.locator("#source-status").inner_text()
        assert page.locator("#prepare-draft").is_disabled()
        assert page.locator("#draft-output").count() == 0
        page.locator("#simulate-stale").click()
        assert not page.locator("#prepare-draft").is_disabled()

        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(250)
        overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 1

        page.locator('[aria-label="Remove emotion_target wonder from selection"]').click()
        page.locator('[data-relation-id="engine_drives_cost"]').first.focus()
        page.keyboard.press("Enter")
        page.locator("#back-to-entity").focus()
        page.keyboard.press("Enter")
        assert page.locator("#focus-title").inner_text() == "Memory economy"
        assert errors == []
    finally:
        page.close()


def test_b2_served_workbench_switch_and_dense_focus(browser, static_server):
    page, errors = open_prototype(browser, static_server)
    try:
        page.locator("#variant-b2").click()
        assert "B2" in page.locator("#variant-label").inner_text()
        select_anchor(page, "node", "memory_economy")
        select_anchor(page, "emotion_target", "wonder")
        assert page.locator("#component-grid .component-card").count() == 2
        grid = page.locator("#component-grid").inner_text()
        assert "Emotional" in grid
        assert "Causal" in grid

        page.locator("#variant-b1").click()
        assert page.locator("#component-grid").count() == 0
        assert "Memory economy" in page.locator("#selection-trail").inner_text()
        page.locator("#variant-b2").click()
        assert page.locator("#component-grid .component-card").count() == 2

        page.select_option("#fixture-select", "dense")
        page.wait_for_function(
            "() => document.querySelector('#fixture-label') && "
            "document.querySelector('#fixture-label').textContent.includes('SYNTHETIC')",
            timeout=20000,
        )
        assert "SYNTHETIC" in page.locator("#fixture-label").inner_text()
        select_anchor(page, "node", "engine_00")
        assert page.locator("#component-grid .component-card").count() == 1
        assert "Stress engine 0" in page.locator("#component-grid").inner_text()
        assert "anchors in this fixture" in page.locator("#anchor-count").inner_text()
        assert errors == []
    finally:
        page.close()


def test_current_studio_baseline_is_served_with_the_same_candidate(browser, tmp_path):
    from auteur.beginner.server import BeginnerWorkspaceServer
    from auteur.beginner.studio_architecture import (
        complete_architecture, prepare_architecture,
    )
    from auteur.beginner.studio_store import CanvasStore
    from auteur.host_agent import HostAgentRequest, build_host_agent_response

    candidate = json.loads(
        (EVIDENCE / "rich-vision-candidate.json").read_text(encoding="utf-8")
    )
    store = CanvasStore(tmp_path, "baseline")
    store.create()
    store.apply(
        "create-item", expected_revision=0, command_id="vision-created",
        payload={"item": {
            "id": "story-vision", "kind": "note", "title": "Story Vision",
            "content": "A coastal mystery about maps that erase memory. "
                       "Wonder, dread, and earned hope.",
        }, "position": {"x": 20, "y": 50}},
    )
    waiting = prepare_architecture(store)
    request = HostAgentRequest(**waiting["request"])
    reply = build_host_agent_response(
        request, json.dumps(candidate), runtime="integration-test",
    ).model_dump()
    complete_architecture(store, reply)

    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    try:
        page.goto(
            f"http://127.0.0.1:{server.port}/studio.html?canvas=baseline",
            wait_until="networkidle",
        )
        page.wait_for_selector("#architecture-reader:not([hidden])", timeout=20000)
        reader = page.locator("#architecture-reader").inner_text().lower()
        assert "memory economy" in reader
        assert "working proposal" in reader
        assert page.locator("#viewport").is_visible()
        assert page.locator("#architecture-status").inner_text()
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
