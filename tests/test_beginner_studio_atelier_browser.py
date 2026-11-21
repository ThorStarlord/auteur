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


def test_living_atlas_reveals_in_place_and_constellation_returns_without_writing(served, browser):
    before = revision(served)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"{served}/studio.html?canvas=atelier&atelier", wait_until="networkidle")
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        assert page.locator("#studio-mode-atelier").get_attribute("aria-pressed") == "true"
        assert page.locator("#viewport").is_hidden()
        # The living atlas is the default way of looking; research treatment C is not offered.
        assert page.locator('#studio-atelier .atl-mode[data-mode="atlas"]').get_attribute("aria-pressed") == "true"
        assert page.locator('#studio-atelier .atl-mode[data-mode="constellation"]').is_disabled()
        assert page.locator('#studio-atelier .atl-mode[data-mode="research"]').count() == 0
        rest = page.evaluate("document.getElementById('studio-atelier').atelierStudy.snapshot()")
        resting = page.evaluate("document.getElementById('studio-atelier').atelierStudy.metrics()")
        assert resting["labels"]["restNamed"] > resting["labels"]["restLandmarks"] / 2
        assert resting["renderedLabelOverlaps"]["count"] == 0
        focus = '.atl-star[data-id="genres|genre:literary_mystery"]'
        selected = page.evaluate(SETTLE, [focus])
        assert selected["focus"] == "genres|genre:literary_mystery" and selected["mode"] == "atlas"
        assert selected["composition"]["first"] > 5 and selected["composition"]["moved"] == 0
        assert selected["renderedLabelOverlaps"]["count"] == 0
        revealed = page.evaluate("document.getElementById('studio-atelier').atelierStudy.snapshot()")
        # Progressive revelation moves nothing and never zooms out to contain the neighbourhood.
        assert revealed["positions"] == rest["positions"]
        assert revealed["camera"]["z"] == rest["camera"]["z"]
        assert page.locator("#studio-atelier .atl-folio-title").inner_text() == "Literary mystery"
        # The folio lists every documented relationship (a neighbour may be related more than once).
        assert page.locator("#studio-atelier .atl-rel").count() >= selected["composition"]["first"]
        examined = page.evaluate(SETTLE, [".atl-look [data-key=look]"])
        assert examined["mode"] == "constellation" and examined["composition"]["moved"] > 0
        assert page.locator("#studio-atelier .atl-mode-chip").is_visible()
        back = page.evaluate(SETTLE, [".atl-look [data-key=look]"])
        assert back["mode"] == "atlas" and back["focus"] == "genres|genre:literary_mystery"
        assert page.evaluate("document.getElementById('studio-atelier').atelierStudy.snapshot()")["positions"] == rest["positions"]
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


def test_atelier_frontispiece_stable_ribbon_and_clear_preview(served, browser):
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"{served}/studio.html?canvas=atelier&atelier", wait_until="networkidle")
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        page.evaluate("window.scrollTo(0, 0)")
        assert page.evaluate("document.querySelector('.workspace').classList.contains('atelier-first')")
        assert page.evaluate(
            "document.querySelector('#studio-atelier').getBoundingClientRect().top + window.scrollY"
        ) < 500
        assert all("DURATION UNKNOWN" not in text.upper() for text in page.evaluate(
            "[...document.querySelectorAll('#studio-atelier .atl-book-label')].map(t => t.textContent)"))

        longest = page.evaluate("""() => {
          const root = document.getElementById('studio-atelier');
          let best = null, length = -1;
          for (const star of root.querySelectorAll('.atl-star')) {
            const title = star.title || '';
            if (title.length > length) { length = title.length; best = star.dataset.id; }
          }
          return best;
        }""")
        rest_ribbon = page.evaluate(
            "document.querySelector('#studio-atelier .atl-ribbon').getBoundingClientRect().height")
        rest_stage = page.evaluate(
            "document.querySelector('#studio-atelier .atl-stage').getBoundingClientRect().top")
        page.evaluate(SETTLE, ['.atl-star[data-id="' + longest.replace('"', '\\"') + '"]'])
        assert page.evaluate(
            "document.querySelector('#studio-atelier .atl-ribbon').getBoundingClientRect().height"
        ) == rest_ribbon
        assert page.evaluate(
            "document.querySelector('#studio-atelier .atl-stage').getBoundingClientRect().top"
        ) == rest_stage

        # A real pointer click commits attention; the hover preview must not linger.
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)
        glyph = page.evaluate("""() => {
          const star = document.querySelector('#studio-atelier .atl-star[data-facet="genres"]');
          const box = star.querySelector('.atl-glyph').getBoundingClientRect();
          return {x: box.x + box.width / 2, y: box.y + box.height / 2};
        }""")
        page.mouse.move(glyph["x"], glyph["y"])
        page.wait_for_timeout(200)
        assert page.locator("#studio-atelier .atl-edge.is-preview").count() > 0
        page.mouse.click(glyph["x"], glyph["y"])
        page.wait_for_timeout(1500)
        assert page.locator("#studio-atelier .atl-edge.is-preview").count() == 0
        assert page.locator("#studio-atelier .atl-star.is-linked").count() == 0

        # Escape at rest also releases a hover preview.
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)
        alternate = page.evaluate("""() => {
          const stars = document.querySelectorAll('#studio-atelier .atl-star[data-facet="genres"]');
          const star = stars[1] || stars[0];
          const box = star.querySelector('.atl-glyph').getBoundingClientRect();
          return {x: box.x + box.width / 2, y: box.y + box.height / 2};
        }""")
        page.mouse.move(alternate["x"], alternate["y"])
        page.wait_for_timeout(200)
        assert page.locator("#studio-atelier .atl-edge.is-preview").count() > 0
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        assert page.locator("#studio-atelier .atl-edge.is-preview").count() == 0
        assert errors == []
    finally:
        page.close()


def test_atelier_phone_scrolls_and_keeps_focus_clear(served, browser):
    context = browser.new_context(
        viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"{served}/studio.html?canvas=atelier&atelier", wait_until="networkidle")
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        page.evaluate("document.querySelector('#studio-atelier').scrollIntoView({block:'start'})")
        page.wait_for_timeout(300)
        assert page.evaluate(
            "getComputedStyle(document.querySelector('#studio-atelier .atl-stage')).touchAction"
        ) == "pan-y"
        before = page.evaluate("window.scrollY")
        point = page.evaluate("""() => {
          const box = document.querySelector('#studio-atelier .atl-stage').getBoundingClientRect();
          return {x: box.x + box.width / 2, y: box.y + 250};
        }""")
        cdp = context.new_cdp_session(page)
        cdp.send("Input.dispatchTouchEvent", {
            "type": "touchStart", "touchPoints": [{"x": point["x"], "y": point["y"]}]})
        for step in range(1, 6):
            cdp.send("Input.dispatchTouchEvent", {
                "type": "touchMove", "touchPoints": [{"x": point["x"], "y": point["y"] - step * 40}]})
            page.wait_for_timeout(30)
        cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        page.wait_for_timeout(600)
        assert page.evaluate("window.scrollY") > before + 20

        page.evaluate(SETTLE, ['.atl-star[data-id="genres|genre:literary_mystery"]'])
        layout = page.evaluate("""() => {
          const root = document.getElementById('studio-atelier');
          const focus = root.querySelector('.atl-star.is-focus .atl-text').getBoundingClientRect();
          const trail = root.querySelector('.atl-trail').getBoundingClientRect();
          const stage = root.querySelector('.atl-stage').getBoundingClientRect();
          return {
            focus: {top: focus.top, bottom: focus.bottom, left: focus.left, right: focus.right},
            trail: {top: trail.top, bottom: trail.bottom, left: trail.left, right: trail.right},
            stage: {top: stage.top, bottom: stage.bottom},
          };
        }""")
        assert layout["focus"]["top"] >= layout["stage"]["top"]
        assert layout["focus"]["bottom"] <= layout["stage"]["bottom"]
        assert not (layout["focus"]["top"] < layout["trail"]["bottom"]
                    and layout["focus"]["bottom"] > layout["trail"]["top"]
                    and layout["focus"]["left"] < layout["trail"]["right"]
                    and layout["focus"]["right"] > layout["trail"]["left"])
        assert errors == []
    finally:
        page.close()
        context.close()
