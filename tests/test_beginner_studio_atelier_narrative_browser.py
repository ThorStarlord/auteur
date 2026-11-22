"""Served Studio: the Atelier's story-structure comparison and its story-time trace.

The comparison is opt-in inside the opt-in study. It sizes genre marks by the role their contract
records (never by relationship count), frames recorded structural parents without making them look
more important, and can trace a concept through the phases whose records name it. Nothing moves, no
path joins separated phases, every marked phase resolves to a recorded source, and nothing is written.
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
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
DENSE = REPO / "qualification/studio-trace/artifacts/candidate-2.json"
SMALL = REPO / "docs/qualification-evidence/agent-first-ontology-20261103/rich-vision-candidate.json"
CIVIC = "genres|genre:genre-civic-life"
ENGINE = "structure|structure-node:engine-risk-transfer"


def counterexample():
    """The small specimen with only its governing and supporting contract roles exchanged."""
    candidate = json.loads(SMALL.read_text(encoding="utf-8"))
    for contract in candidate["genre_contracts"]:
        contract["role"] = {"governing": "supporting", "supporting": "governing"}.get(contract["role"], contract["role"])
    return candidate


def seed(root, canvas, candidate, vision):
    store = CanvasStore(root, canvas)
    store.create()
    store.apply("create-item", expected_revision=0, command_id=f"{canvas}-vision", payload={"item": {
        "id": "story-vision", "kind": "note", "title": "Story Vision", "content": vision}, "position": {"x": 20, "y": 50}})
    waiting = prepare_architecture(store)
    reply = build_host_agent_response(HostAgentRequest(**waiting["request"]), json.dumps(candidate),
                                      runtime="integration-test").model_dump()
    complete_architecture(store, reply)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


@pytest.fixture(scope="module")
def served(tmp_path_factory):
    root = tmp_path_factory.mktemp("atelier-narrative")
    seed(root, "dense", json.loads(DENSE.read_text(encoding="utf-8")),
         (REPO / "qualification/studio-trace/artifacts/story_vision.txt").read_text(encoding="utf-8").strip())
    seed(root, "counter", counterexample(),
         "A coastal mystery about maps that erase memory. Wonder, dread, and earned hope. (Test fixture.)")
    server = BeginnerWorkspaceServer(root, port=0)
    thread = server.start_in_thread()
    yield f"http://127.0.0.1:{server.port}"
    server.stop()
    thread.join(timeout=5)


def revision(base, canvas):
    with urlopen(f"{base}/api/beginner/studio/canvases/{canvas}") as response:
        return json.load(response)["revision"]


ARM = """() => { const r = document.getElementById('studio-atelier');
  window.__settled = new Promise(res => r.addEventListener('atelier:settled', e => res(e.detail), {once: true})); }"""
WAIT = "Promise.race([window.__settled, new Promise(r => setTimeout(() => r(null), 8000))])"
SNAP = "document.getElementById('studio-atelier').atelierStudy.snapshot()"
SCALE = """(id) => parseFloat(getComputedStyle(document.querySelector('#studio-atelier .atl-star[data-id="' + id + '"]')).getPropertyValue('--gs'))"""
KICKER = """(id) => { const s = document.querySelector('#studio-atelier .atl-star[data-id="' + id + '"]');
  return {style: s.querySelector('.atl-text').dataset.style, kicker: s.querySelector('.atl-kicker').textContent,
    shown: getComputedStyle(s.querySelector('.atl-kicker')).display !== 'none'}; }"""
CLICK = """(id) => document.querySelector('#studio-atelier .atl-star[data-id="' + id + '"]').click()"""
GLYPH = """(id) => { const b = document.querySelector('#studio-atelier .atl-star[data-id="' + id + '"] .atl-glyph').getBoundingClientRect();
  return {x: b.left + b.width / 2, y: b.top + b.height / 2}; }"""


def open_atelier(browser, base, canvas, query="", width=1440, height=900):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{base}/studio.html?canvas={canvas}&atelier{query}", wait_until="networkidle")
    page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
    page.wait_for_function("document.getElementById('studio-atelier').atelierStudy.metrics()", timeout=10000)
    return page, errors


def act(page, fn):
    page.evaluate(ARM)
    fn()
    page.evaluate(WAIT)
    time.sleep(0.2)


def select(page, concept):
    point = page.evaluate(GLYPH, concept)
    act(page, lambda: page.mouse.click(point["x"], point["y"]))


def resolve(candidate, ref):
    """Follow a recorded source reference such as phases/<id>/genres/2 into the candidate."""
    here = candidate
    for part in ref.split("#")[0].split("/"):
        if isinstance(here, list):
            here = here[int(part)] if part.isdigit() else next(
                item for item in here if part in (item.get("id"), item.get("genre_node_id")))
        else:
            here = here[part]
    return here


def folio(page):
    """The folio as read, in lower case (section titles are set in capitals by CSS)."""
    return page.locator("#studio-atelier .atl-folio").inner_text().lower()


def view(snapshot):
    return {"camera": snapshot["camera"], "positions": snapshot["positions"]}


def test_story_structure_is_opt_in_sizes_by_recorded_role_and_moves_nothing(browser, served):
    before = revision(served, "dense")
    page, errors = open_atelier(browser, served, "dense")
    tool = page.locator("#studio-atelier .atl-tool-structure")
    # Off by default: the baseline atlas still sizes marks by documented relationships.
    assert tool.get_attribute("aria-pressed") == "false"
    disaster, apprentice = "genres|genre:genre-disaster", "genres|genre:genre-apprenticeship"
    assert page.evaluate(SCALE, disaster) > page.evaluate(SCALE, apprentice)  # 18 > 16 relationships
    rest = view(page.evaluate(SNAP))

    act(page, lambda: tool.click())
    assert tool.get_attribute("aria-pressed") == "true"
    on = page.evaluate(SNAP)
    assert on["narrative"] is True and view(on) == rest, "the comparison must not move anything"
    # Recorded role, not connectivity: the tertiary genre (18 relationships) is now smaller than a
    # supporting one (16), and the governing genre is the largest.
    assert page.evaluate(SCALE, "genres|genre:genre-procedural") == pytest.approx(1.6)
    assert page.evaluate(SCALE, apprentice) == pytest.approx(1.12)
    assert page.evaluate(SCALE, disaster) == pytest.approx(0.9)
    # Parenthood is a frame and a stated count, not extra size.
    engine = page.locator(f'#studio-atelier .atl-star[data-id="{ENGINE}"]')
    assert "is-parent" in engine.get_attribute("class") and page.evaluate(SCALE, ENGINE) == pytest.approx(1)
    assert page.evaluate(KICKER, ENGINE) == {"style": "restRole", "kicker": "CONTAINS 8", "shown": True}
    assert "recorded story structure" in folio(page) and "measures connectivity, not importance" in folio(page)

    act(page, lambda: tool.click())
    assert page.evaluate(SCALE, disaster) > page.evaluate(SCALE, apprentice), "switching off restores the baseline"
    assert view(page.evaluate(SNAP)) == rest
    assert errors == [] and revision(served, "dense") == before


def test_counterexample_governing_genre_with_fewer_relationships_is_still_the_governing_mark(browser, served):
    before = revision(served, "counter")
    page, errors = open_atelier(browser, served, "counter", "&narrative")
    governing, supporting = "genres|genre:fantasy", "genres|genre:literary_mystery"
    concepts = {c["id"]: c for c in page.evaluate(SNAP)["concepts"]}
    assert concepts[governing]["relations"] < concepts[supporting]["relations"]
    assert page.evaluate(SCALE, governing) > page.evaluate(SCALE, supporting)
    assert page.evaluate(KICKER, governing) == {"style": "landmark", "kicker": "GOVERNING · PROPOSED", "shown": True}
    text = folio(page)
    assert "governing genre\nfantasy" in text and "not author decisions" in text
    assert errors == [] and revision(served, "counter") == before


def test_trace_marks_only_recorded_phases_draws_no_new_path_and_restores_the_view(browser, served):
    before = revision(served, "dense")
    candidate = json.loads(DENSE.read_text(encoding="utf-8"))
    page, errors = open_atelier(browser, served, "dense", "&narrative")
    select(page, CIVIC)
    selected = page.evaluate(SNAP)
    paths = page.locator("#studio-atelier svg path").count()
    act(page, lambda: page.click('#studio-atelier [data-key="trace"]'))
    traced = page.evaluate(SNAP)
    assert view(traced) == view(selected) and traced["focus"] == CIVIC
    phases = traced["trace"]["phases"]
    assert [p["status"] for p in phases] == ["recorded", "recorded", "none", "recorded", "recorded",
                                             "none", "none", "recorded", "recorded"]
    assert [p["role"] for p in phases] == ["background", "background", None, "background", "locally_dominant",
                                           None, None, "supporting", "governing"]
    for phase in phases:
        assert (phase["status"] == "recorded") == bool(phase["sources"])
        for ref in phase["sources"]:
            assert resolve(candidate, ref) is not None, ref
        # A thread is kept only where the phase records an activation of the genre.
        assert bool(phase["relations"]) == any("/genre_activations/" in ref for ref in phase["sources"])
    # Nothing is drawn between phases: no new path, and only the four recorded activations stay lit.
    assert page.locator("#studio-atelier svg path").count() == paths
    assert page.locator("#studio-atelier .atl-edge.is-traced").count() == 4
    kickers = [page.evaluate(KICKER, p["phase"])["kicker"] for p in phases]
    assert kickers == ["BACKGROUND", "BACKGROUND", "NOT RECORDED", "BACKGROUND", "LOCALLY DOMINANT",
                       "NOT RECORDED", "NOT RECORDED", "SUPPORTING", "GOVERNING"]
    text = folio(page)
    assert "6 of 9 phases record it" in text and "story order is not recorded causation" in text
    assert "phases/phase-bought-seal/genres/2" in text

    # Escape steps back one level: the trace ends, the selection and view are exactly as before.
    act(page, lambda: page.keyboard.press("Escape"))
    after = page.evaluate(SNAP)
    assert after["trace"] is None and after["focus"] == CIVIC and view(after) == view(selected)
    assert page.locator("#studio-atelier.atl-tracing").count() == 0
    assert page.locator("#studio-atelier .atl-star.is-occurs, #studio-atelier .atl-star.is-unrecorded").count() == 0
    act(page, lambda: page.keyboard.press("Escape"))
    assert page.evaluate(SNAP)["focus"] is None
    assert errors == [] and revision(served, "dense") == before


def test_no_trace_is_offered_without_direct_phase_records(browser, served):
    page, errors = open_atelier(browser, served, "dense", "&narrative")
    select(page, ENGINE)
    assert page.locator('#studio-atelier [data-key="trace"]').count() == 0
    text = folio(page)
    assert "0 of 9 phases record it" in text and "not evidence that it is absent from the story" in text
    assert "recorded as the parent of\n8:" in text and "containment, not importance" in text
    # A function recorded inside a single phase occurs there only: no trace across story time.
    local = next(c["id"] for c in page.evaluate(SNAP)["concepts"] if c["id"].startswith("structure|phase-structure:"))
    act(page, lambda: page.evaluate(CLICK, local))
    assert page.locator('#studio-atelier [data-key="trace"]').count() == 0
    assert "1 of 9 phases record it" in folio(page)
    # The baseline never offers a trace at all.
    base, base_errors = open_atelier(browser, served, "dense")
    select(base, CIVIC)
    assert base.locator('#studio-atelier [data-key="trace"]').count() == 0
    assert "in story time" not in folio(base)
    assert errors == [] and base_errors == []


def test_trace_by_keyboard_and_at_phone_width(browser, served):
    page, errors = open_atelier(browser, served, "dense", "&narrative")
    select(page, CIVIC)
    button = page.locator('#studio-atelier [data-key="trace"]')
    button.focus()
    act(page, lambda: page.keyboard.press("Enter"))
    assert page.evaluate(SNAP)["trace"]["id"] == CIVIC
    again = page.locator('#studio-atelier [data-key="trace"]')
    assert again.get_attribute("aria-pressed") == "true" and page.evaluate("document.activeElement.dataset.key") == "trace"
    act(page, lambda: page.keyboard.press("Escape"))
    assert page.evaluate(SNAP)["trace"] is None and page.evaluate("document.activeElement.dataset.key") == "trace"

    phone, phone_errors = open_atelier(browser, served, "dense", "&narrative", 390, 844)
    # A phone selection pans the camera to keep the focus readable; the trace starts from the settled view.
    act(phone, lambda: phone.evaluate(CLICK, CIVIC))
    selected = view(phone.evaluate(SNAP))
    act(phone, lambda: phone.locator('#studio-atelier [data-key="trace"]').click())
    assert view(phone.evaluate(SNAP)) == selected
    assert phone.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    # A phase name that does not fit stays quiet; none is shown cut by the stage edge.
    assert phone.evaluate("""() => { const s = document.querySelector('#studio-atelier .atl-stage').getBoundingClientRect();
      return [...document.querySelectorAll('#studio-atelier .atl-star .atl-text')]
        .filter(t => parseFloat(getComputedStyle(t).opacity) > 0.3 && t.getBoundingClientRect().width > 0)
        .filter(t => { const r = t.getBoundingClientRect(); return r.left < s.left - 1 || r.right > s.right + 1; }).length; }""") == 0
    assert phone.evaluate("document.getElementById('studio-atelier').atelierStudy.metrics().renderedLabelOverlaps.count") == 0
    assert errors == [] and phone_errors == []
