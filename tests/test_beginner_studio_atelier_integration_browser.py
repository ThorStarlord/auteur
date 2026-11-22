"""Served Studio: from the Atelier into the Studio's own coding-agent workflow and back.

A concept selected in the atlas carries its own recorded source (one contract trope function is one
entry, not the whole list) into the existing inquiry and revision panel. Preparing a request changes
nothing, so the atlas keeps its place. A revision the author applies returns to the same concept,
marks what the records changed, and keeps every position when the same concepts are recorded.
"""
import copy
import json
import os
import time
from pathlib import Path
from urllib.request import urlopen

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture, project_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
DENSE = json.loads((REPO / "qualification/studio-trace/artifacts/candidate-2.json").read_text(encoding="utf-8"))
VISION = (REPO / "qualification/studio-trace/artifacts/story_vision.txt").read_text(encoding="utf-8").strip()
TROPE = "tropes|trope-node:trope-first-crosser"
CRAFT_FN = "tropes|trope:genre-craft-thriller:0"
ENGINE = "structure|structure-node:engine-risk-transfer"
SNAP = "document.getElementById('studio-atelier').atelierStudy.snapshot()"
FOLIO = "document.querySelector('#studio-atelier .atl-folio').innerText"
LIVE = "document.querySelector('#studio-atelier [aria-live]').textContent"
ARM = """() => { const r = document.getElementById('studio-atelier');
  window.__settled = new Promise(res => r.addEventListener('atelier:settled', e => res(e.detail), {once: true})); }"""
WAIT = "Promise.race([window.__settled, new Promise(r => setTimeout(() => r(null), 8000))])"
CLICK = """(id) => document.querySelector('#studio-atelier .atl-star[data-id="' + id + '"]').click()"""
PANEL = "#architecture-creative-agent-panel"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


@pytest.fixture()
def served(tmp_path):
    store = CanvasStore(tmp_path, "dense")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={"item": {
        "id": "story-vision", "kind": "note", "title": "Story Vision", "content": VISION}, "position": {"x": 20, "y": 50}})
    waiting = prepare_architecture(store)
    complete_architecture(store, build_host_agent_response(
        HostAgentRequest(**waiting["request"]), json.dumps(DENSE), runtime="integration-test").model_dump())
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    yield f"http://127.0.0.1:{server.port}", store
    server.stop()
    thread.join(timeout=5)


def open_atelier(browser, base, width=1440, height=900, atelier=True):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{base}/studio.html?canvas=dense" + ("&atelier" if atelier else ""), wait_until="networkidle")
    if atelier:
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        time.sleep(0.6)
    return page, errors


def act(page, fn):
    page.evaluate(ARM)
    fn()
    page.evaluate(WAIT)
    time.sleep(0.2)


def develop(page, concept, operation, text):
    act(page, lambda: page.evaluate(CLICK, concept))
    act(page, lambda: page.locator(f'#studio-atelier .atl-develop button[data-operation="{operation}"]').click())
    page.keyboard.type(text)  # the question field has focus after the hand-off
    page.locator(f"{PANEL} [data-creative-submit]").click()


def agent_revises(store, edit):
    """The author's coding agent answers the pending revision request (the Studio's host-agent path)."""
    projection = project_architecture(store)
    assert projection["status"] == "awaiting_host_agent"
    candidate = edit(copy.deepcopy(projection["candidate"]))
    complete_architecture(store, build_host_agent_response(
        HostAgentRequest(**projection["request"]), json.dumps(candidate), runtime="integration-test").model_dump())


def record_first_crosser(c):
    for owner in c["genre_contracts"] + [a for p in c["phases"] for a in p.get("genre_activations", [])]:
        refs = [{"function_index": i, "trope_node_id": "trope-first-crosser"}
                for i, t in enumerate(owner.get("trope_functions", [])) if t == "the first crosser"]
        if refs:
            owner["trope_function_refs"] = refs
    return c


def remove_first_crosser(c):
    c["nodes"] = [n for n in c["nodes"] if n["id"] != "trope-first-crosser"]
    c["links"] = [x for x in c["links"] if "trope-first-crosser" not in (x["source"], x["target"])]
    return c


def apply_review(page):
    page.locator("#architecture-refresh").click()
    page.wait_for_selector("#architecture-review:not([hidden])", timeout=10000)
    act(page, lambda: page.locator("#architecture-apply").click())
    page.wait_for_function("document.getElementById('architecture-review').hidden", timeout=10000)
    time.sleep(0.8)


def test_one_function_carries_its_own_entry_and_preparing_a_request_keeps_the_atlas(served, browser):
    base, store = served
    page, errors = open_atelier(browser, base)
    try:
        act(page, lambda: page.evaluate(CLICK, CRAFT_FN))
        about = page.locator("#studio-atelier .atl-develop .atl-develop-about").inner_text()
        assert "Trope function 1 of the Craft and structural thriller contract" in about
        assert "genre_contracts/genre-craft-thriller/trope_functions/0" in about
        develop(page, CRAFT_FN, "revise", "Make only this function the craftsman's apprentice.")
        chips = page.locator(f'{PANEL} [aria-label="Selected source anchors"]').inner_text()
        assert chips.strip() == "genre_contract · genre-craft-thriller / trope_functions · entry 1"
        page.wait_for_function("document.getElementById('architecture-status').textContent.includes('Awaiting')", timeout=10000)
        time.sleep(0.5)
        # The request names exactly that entry; the other uses of the same words are not its anchor.
        user = project_architecture(store)["request"]["user"]
        intent = json.loads(user)["graph_intent"] if user.lstrip().startswith("{") else None
        text = user if intent is None else json.dumps(intent)
        assert '"entryValue": "the first crosser"' in text and '"index": 0' in text
        # Preparing changes nothing, so the atlas keeps its place and says nothing changed.
        assert page.evaluate(SNAP)["focus"] == CRAFT_FN
        assert "changed" not in page.evaluate(LIVE)
        assert "waiting for your coding agent" in page.locator("#studio-atelier .atl-working").inner_text()
        back = page.locator("#architecture-creative-graph .atelier-return")
        assert back.is_visible() and "the first crosser" in back.inner_text()
        back.focus()
        page.keyboard.press("Enter")
        time.sleep(0.4)
        assert page.evaluate("document.activeElement.dataset.id") == CRAFT_FN
        assert not errors
    finally:
        page.close()


def test_an_applied_revision_returns_to_the_concept_marks_the_change_and_keeps_every_place(served, browser):
    base, store = served
    items = json.loads(urlopen(f"{base}/api/beginner/studio/canvases/dense").read())["items"]
    page, errors = open_atelier(browser, base)
    try:
        act(page, lambda: page.evaluate(CLICK, TROPE))
        folio = page.evaluate(FOLIO)
        assert "None recorded" in folio and "repeat its words" in folio  # equal wording is not a link
        home = page.evaluate(SNAP)["home"]
        develop(page, TROPE, "revise", "Record which functions realise The First Crosser. Change nothing else.")
        page.wait_for_function("document.getElementById('architecture-status').textContent.includes('Awaiting')", timeout=10000)
        agent_revises(store, record_first_crosser)
        page.locator("#architecture-refresh").click()
        page.wait_for_selector("#architecture-review:not([hidden])", timeout=10000)
        time.sleep(0.4)
        assert "ready for your review" in page.locator("#studio-atelier .atl-working").inner_text()
        assert page.evaluate(SNAP)["focus"] == TROPE  # a proposal under review changes nothing yet
        act(page, lambda: page.locator("#architecture-apply").click())
        page.wait_for_function("document.getElementById('architecture-review').hidden", timeout=10000)
        time.sleep(0.8)
        snap = page.evaluate(SNAP)
        assert snap["focus"] == TROPE
        assert snap["revision"]["keptLayout"] is True and snap["home"] == home
        assert snap["revision"]["reworded"] == [] and len(snap["revision"]["relationsAdded"]) == 9
        assert CRAFT_FN in snap["revision"]["touched"]
        assert "is-revised" in page.locator(f'#studio-atelier .atl-star[data-id="{CRAFT_FN}"]').get_attribute("class")
        folio = page.evaluate(FOLIO)
        assert "9 functions recorded as realising this trope" in folio
        assert "Changed by the revision you applied".upper() in folio.upper()
        assert "genre_contracts/genre-craft-thriller/trope_function_refs/0" in folio
        assert "still selected" in page.evaluate(LIVE) and "kept its place" in page.evaluate(LIVE)
        # The author's story items are untouched; only the working Architecture was revised.
        assert json.loads(urlopen(f"{base}/api/beginner/studio/canvases/dense").read())["items"] == items
        act(page, lambda: page.evaluate(CLICK, TROPE))  # reselecting keeps the marks until cleared
        act(page, lambda: page.keyboard.press("Escape"))
        act(page, lambda: page.locator('#studio-atelier .atl-folio button[data-key="clear-revision"]').click())
        assert page.locator("#studio-atelier .atl-star.is-revised").count() == 0
        assert not errors
    finally:
        page.close()


def test_a_revision_that_removes_the_selected_concept_says_so_and_lays_the_atlas_out_again(served, browser):
    base, store = served
    page, errors = open_atelier(browser, base)
    try:
        develop(page, TROPE, "revise", "Remove The First Crosser trope node.")
        page.wait_for_function("document.getElementById('architecture-status').textContent.includes('Awaiting')", timeout=10000)
        agent_revises(store, remove_first_crosser)
        apply_review(page)
        snap = page.evaluate(SNAP)
        assert snap["focus"] is None and snap["revision"]["keptLayout"] is False
        assert TROPE in snap["revision"]["removed"]
        live = page.evaluate(LIVE)
        assert "no longer recorded" in live and "laid out again" in live
        assert not errors
    finally:
        page.close()


def test_interpretations_are_shown_and_the_engine_has_its_own_address(served, browser):
    base, _ = served
    page, errors = open_atelier(browser, base, width=390, height=844)
    try:
        act(page, lambda: page.evaluate(CLICK, ENGINE))
        folio = page.evaluate(FOLIO)
        assert "AGENT INTERPRETATIONS NAMING IT" in folio.upper()  # without the Story structure switch
        develop_box = page.locator("#studio-atelier .atl-develop")
        develop_box.scroll_into_view_if_needed()
        assert "Source · nodes/engine-risk-transfer" in develop_box.inner_text()
        assert page.evaluate("document.scrollingElement.scrollWidth") <= 390
        box = develop_box.bounding_box()
        assert box["x"] >= 0 and box["x"] + box["width"] <= 390
        assert not errors
    finally:
        page.close()


def test_the_ordinary_studio_gains_no_atelier_controls(served, browser):
    base, _ = served
    page, errors = open_atelier(browser, base, atelier=False)
    try:
        time.sleep(0.8)
        assert page.locator(".atelier-return").count() == 0
        assert page.locator("#studio-mode-atelier").is_hidden()
        assert not errors
    finally:
        page.close()
