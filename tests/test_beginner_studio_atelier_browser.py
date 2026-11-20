"""Served Studio: the Atelier study is absent by default and, when opted in, explores the real
working Architecture without moving the atlas for good or writing the canvas."""
import json
import os
from pathlib import Path
from urllib.request import urlopen

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

CANDIDATE = (Path(__file__).resolve().parents[1] /
             "docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json")


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


@pytest.fixture
def served(tmp_path):
    store = CanvasStore(tmp_path, "atelier")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={"item": {
        "id": "story-vision", "kind": "note", "title": "Story Vision",
        "content": "A coastal mystery about maps that erase memory. Wonder, dread, and earned hope."},
        "position": {"x": 20, "y": 50}})
    waiting = prepare_architecture(store)
    reply = build_host_agent_response(HostAgentRequest(**waiting["request"]),
                                      CANDIDATE.read_text(encoding="utf-8"), runtime="integration-test").model_dump()
    complete_architecture(store, reply)
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    yield f"http://127.0.0.1:{server.port}"
    server.stop()
    thread.join(timeout=5)


def revision(base):
    with urlopen(f"{base}/api/beginner/studio/canvases/atelier") as response:
        return json.load(response)["revision"]


SETTLE = """async ([selector]) => {
  const root = document.getElementById('studio-atelier');
  const done = new Promise(r => root.addEventListener('atelier:settled', e => r(e.detail), {once: true}));
  root.querySelector(selector).click();
  return await done;
}"""


def test_default_studio_has_no_study(served, browser):
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"{served}/studio.html?canvas=atelier", wait_until="networkidle")
        page.wait_for_selector("#nodes .node.candidate", timeout=20000)
        assert page.locator("#studio-mode-atelier").is_hidden()
        assert page.locator("#studio-atelier").is_hidden()
        assert page.locator("#viewport").is_visible()
        assert page.locator("#studio-mode-focus").get_attribute("aria-pressed") == "true"
        assert errors == []
    finally:
        page.close()


def test_opted_in_study_explores_and_returns_without_writing(served, browser):
    before = revision(served)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"{served}/studio.html?canvas=atelier&atelier=C", wait_until="networkidle")
        page.wait_for_selector("#studio-atelier .atl-star", timeout=20000)
        assert page.locator("#studio-mode-atelier").get_attribute("aria-pressed") == "true"
        assert page.locator("#viewport").is_hidden()
        rest = page.evaluate("document.getElementById('studio-atelier').atelierStudy.snapshot()")
        focus = '.atl-star[data-id="genres|genre:literary_mystery"]'
        selected = page.evaluate(SETTLE, [focus])
        assert selected["focus"] == "genres|genre:literary_mystery"
        assert selected["composition"]["first"] > 5
        assert page.locator("#studio-atelier .atl-folio-title").inner_text() == "Literary mystery"
        # The folio lists every documented relationship (a neighbour may be related more than once).
        assert page.locator("#studio-atelier .atl-rel").count() >= selected["composition"]["first"]
        for treatment in "AB":
            page.locator(f'#studio-atelier .atl-treatment[data-treatment="{treatment}"]').click()
        page.evaluate(SETTLE, [".atl-folio .atl-return"])
        after = page.evaluate("document.getElementById('studio-atelier').atelierStudy.snapshot()")
        assert after["focus"] is None
        assert after["positions"] == rest["positions"]
        assert after["camera"] == rest["camera"]
        page.locator("#studio-mode-focus").click()
        assert page.locator("#viewport").is_visible() and page.locator("#studio-atelier").is_hidden()
        assert errors == []
    finally:
        page.close()
    assert revision(served) == before
