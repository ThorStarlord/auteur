"""Served Chromium checks of author-directed intention management and review critique.

The host-agent answer is an admitted fixture. These are UI/persistence checks, not
human usability observations or independent creative generation.
"""
from __future__ import annotations

import json

from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import (
    complete_architecture, prepare_architecture, project_architecture,
    project_architecture_resume,
)
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from test_beginner_studio_architecture_interactive_browser import _seeded_thread


def _open_page(server, canvas):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas={canvas}")
    page.locator("#architecture-develop").wait_for()
    return playwright, browser, page


def test_browser_can_keep_withdraw_and_supersede_author_intentions(tmp_path):
    store = _seeded_thread(tmp_path)
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    server.start_in_thread()
    playwright = browser = page = None
    try:
        playwright, browser, page = _open_page(server, "creative-thread")
        page.locator("#studio-creative-intentions > summary").click()
        page.locator("#studio-intention-title").fill("Restorative discovery")
        page.locator("#studio-intention-directive").fill(
            "Preserve costly discovery as a possible route to mutual care."
        )
        page.locator("#studio-intention-add").click()
        page.wait_for_function(
            "() => document.querySelector('#studio-intention-statusline').textContent"
            ".includes('Intention recorded')"
        )
        page.locator("#studio-intentions-list button").filter(
            has_text="Replace with successor"
        ).click()
        page.locator('[aria-label="Successor title for Restorative discovery"]').fill(
            "Restoration through reconciliation"
        )
        page.locator('[aria-label="Successor directive for Restorative discovery"]').fill(
            "Make restoration depend on a voluntary act of reconciliation."
        )
        page.get_by_role("button", name="Confirm replacement").click()
        page.wait_for_function(
            "() => document.querySelector('#studio-intention-statusline').textContent"
            ".includes('New active direction replaces')"
        )
        page.reload()
        page.locator("#studio-intentions-list").get_by_text(
            "Restorative discovery · superseded"
        ).wait_for()
        page.locator("#studio-intentions-list").get_by_text(
            "Restoration through reconciliation · active"
        ).wait_for()
        current = project_architecture_resume(store)["creative_intentions"]
        old = next(row for row in current if row["title"] == "Restorative discovery")
        new = next(row for row in current if row["title"] == "Restoration through reconciliation")
        assert old["superseded_by"] == new["id"]
        assert new["status"] == "active"
        assert project_architecture(store)["status"] == "ready"
    finally:
        if page:
            page.close()
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
        server.stop()


def test_browser_prepares_and_validates_read_only_pending_review_critique(tmp_path):
    store = _seeded_thread(tmp_path)
    first = project_architecture(store)["candidate"]
    pending = prepare_architecture(store, "Make the inherited obligation more consequential.")
    candidate = json.loads(json.dumps(first))
    candidate["summary"] = "Unresolved obligations sharpen the emotional consequences."
    complete_architecture(store, build_host_agent_response(
        HostAgentRequest(**pending["request"]), json.dumps(candidate),
        runtime="browser-test", model="fixture",
    ).model_dump())
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    server.start_in_thread()
    playwright = browser = page = None
    try:
        playwright, browser, page = _open_page(server, "creative-thread")
        page.locator("#architecture-review").wait_for(state="visible")
        page.locator("#architecture-impact-inquiry > summary").click()
        page.locator("#architecture-impact-prepare").click()
        page.wait_for_function(
            "() => document.querySelector('#architecture-impact-request').value.length > 0"
        )
        request = HostAgentRequest(**json.loads(page.locator(
            "#architecture-impact-request"
        ).input_value()))
        answer = {
            "schema_version": 1,
            "analysis": "recorded_change: the summary now emphasizes emotional cost.",
            "recorded_observations": [],
            "hypotheses": [],
            "uncertainties": ["reasoned_consequence: the reader's response remains untested."],
        }
        signed = build_host_agent_response(
            request, json.dumps(answer), runtime="browser-test", model="fixture",
        )
        page.locator("#architecture-impact-response").fill(
            json.dumps(signed.model_dump(mode="json"))
        )
        page.locator("#architecture-impact-complete").click()
        page.locator("#architecture-impact-result").get_by_text(
            "recorded_change", exact=False
        ).wait_for()
        assert project_architecture(store)["status"] == "review_ready"
        assert project_architecture(store)["candidate"]["summary"] == first["summary"]
    finally:
        if page:
            page.close()
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
        server.stop()
