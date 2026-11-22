"""Served Studio: the Atelier's story-structure comparison.

The comparison is opt-in inside the opt-in study. It sizes genre marks by the role their contract
records (never by relationship count) and frames recorded structural parents without making them look
more important. With it on, selecting a concept also names, in place, the role each phase records for
it, and marks a phase that lists it without activating it; no thread is added and nothing moves. Every
marked phase resolves to a recorded source, and nothing is written.
"""
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
SMALL_VISION = "A coastal mystery about maps that erase memory. Wonder, dread, and earned hope."
CIVIC = "genres|genre:genre-civic-life"
ENGINE = "structure|structure-node:engine-risk-transfer"
PHASE = "timeline|phase:"


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
    seed(root, "small", json.loads(SMALL.read_text(encoding="utf-8")), SMALL_VISION)
    seed(root, "counter", counterexample(), SMALL_VISION + " (Test fixture.)")
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
METRICS = "document.getElementById('studio-atelier').atelierStudy.metrics()"
STAR = """'#studio-atelier .atl-star[data-id="' + id + '"]'"""
SCALE = "(id) => parseFloat(getComputedStyle(document.querySelector(" + STAR + ")).getPropertyValue('--gs'))"
LABEL = """(id) => { const s = document.querySelector(""" + STAR + """);
  return {style: s.querySelector('.atl-text').dataset.style, kicker: s.querySelector('.atl-kicker').textContent,
    shown: getComputedStyle(s.querySelector('.atl-kicker')).display !== 'none', classes: s.className}; }"""
CLICK = "(id) => document.querySelector(" + STAR + ").click()"
GLYPH = """(id) => { const b = document.querySelector(""" + STAR + """ + ' .atl-glyph').getBoundingClientRect();
  return {x: b.left + b.width / 2, y: b.top + b.height / 2}; }"""
CLIPPED = """() => { const s = document.querySelector('#studio-atelier .atl-stage').getBoundingClientRect();
  return [...document.querySelectorAll('#studio-atelier .atl-star .atl-text')]
    .filter(t => parseFloat(getComputedStyle(t).opacity) > 0.3 && t.getBoundingClientRect().width > 0)
    .filter(t => { const r = t.getBoundingClientRect(); return r.left < s.left - 1 || r.right > s.right + 1; }).length; }"""


def open_atelier(browser, base, canvas, query="", width=1440, height=900):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{base}/studio.html?canvas={canvas}&atelier{query}", wait_until="networkidle")
    page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
    page.wait_for_function(METRICS, timeout=10000)
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
    # Parenthood is a frame and a stated count, not extra size, for every recorded parent.
    parents = page.evaluate("[...document.querySelectorAll('#studio-atelier .atl-star.is-parent')].map(s => s.dataset.id).sort()")
    assert parents == sorted([ENGINE, "structure|structure-node:engine-unverifiable-certificate",
                              "structure|structure-node:engine-succession", "structure|structure-node:engine-crossing-public",
                              "structure|structure-node:structure-criterion-test"])
    assert all(page.evaluate(SCALE, p) == pytest.approx(1) for p in parents)
    assert page.evaluate(LABEL, ENGINE)["kicker"] == "CONTAINS 8"
    text = folio(page)
    assert "recorded story structure" in text and "measures connectivity, not importance" in text
    assert "does not size or rank it as governing" in text
    # The proposal's own interpretation about its genre roles is shown beside them.
    assert "agent interpretations about these roles · 1" in text and "every genre contract here is a working framing" in text

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
    label = page.evaluate(LABEL, governing)
    assert (label["style"], label["kicker"], label["shown"]) == ("landmark", "GOVERNING · PROPOSED", True)
    text = folio(page)
    assert "governing genre\nfantasy" in text and "not author decisions" in text
    assert errors == [] and revision(served, "counter") == before


def test_selection_names_each_phase_role_in_place_without_new_threads(browser, served):
    before = revision(served, "dense")
    candidate = json.loads(DENSE.read_text(encoding="utf-8"))
    base, base_errors = open_atelier(browser, served, "dense")
    select(base, CIVIC)
    baseline = base.evaluate(SNAP)
    base_threads = base.locator("#studio-atelier .atl-edge.lv-1").count()

    page, errors = open_atelier(browser, served, "dense", "&narrative")
    select(page, CIVIC)
    selected = page.evaluate(SNAP)
    assert view(selected) == view(baseline), "the same selection, the same view"
    assert page.locator("#studio-atelier .atl-edge.lv-1").count() == base_threads, "no thread is added"
    phases = selected["storyTime"]["phases"]
    assert [p["status"] for p in phases] == ["recorded", "recorded", "none", "recorded", "recorded",
                                             "none", "none", "recorded", "recorded"]
    assert [p["role"] for p in phases] == ["background", "background", None, "background", "locally_dominant",
                                           None, None, "supporting", "governing"]
    for phase in phases:
        assert (phase["status"] == "recorded") == bool(phase["sources"])
        for ref in phase["sources"]:
            assert resolve(candidate, ref) is not None, ref
        label = page.evaluate(LABEL, phase["phase"])
        if phase["relations"]:
            # Activated: the phase's existing pill names the role the phase records.
            assert label["style"] == "nearRole" and label["kicker"] == "PHASE ROLE · " + phase["role"].replace("_", " ").upper()
        elif phase["status"] == "recorded":
            # Listed without an activation: marked in place, with no thread to draw.
            assert "is-listed" in label["classes"] and label["style"] == "phaseListed"
        else:
            assert "is-listed" not in label["classes"] and "is-near" not in label["classes"]
    text = folio(page)
    assert "6 of 9 phases record it" in text and "order is not recorded causation" in text
    assert "phases/phase-bought-seal/genres/2" in text and "recorded as running parallel with phase 2" in text
    assert "the genre contract records supporting" in text
    # Revealing deeper connections reaches the listed phases through other concepts; they keep their own mark.
    act(page, lambda: page.locator('#studio-atelier [data-key="depth"]').click())
    for phase in phases:
        listed = phase["status"] == "recorded" and not phase["relations"]
        assert ("is-listed" in page.evaluate(LABEL, phase["phase"])["classes"]) == listed

    act(page, lambda: page.keyboard.press("Escape"))
    assert page.evaluate(SNAP)["focus"] is None and page.locator("#studio-atelier .atl-star.is-listed").count() == 0
    assert errors == [] and base_errors == [] and revision(served, "dense") == before


def test_no_story_time_cue_without_a_phase_record_that_refers_to_the_concept(browser, served):
    page, errors = open_atelier(browser, served, "dense", "&narrative")
    select(page, ENGINE)
    assert page.locator("#studio-atelier .atl-star.is-listed").count() == 0
    text = folio(page)
    assert "no phase record refers to it" in text and "not evidence that it is absent from the story" in text
    assert "recorded as the parent of\n8:" in text and "does not size or rank it as governing" in text
    # A function recorded inside one phase is shown in that phase only.
    local = "structure|phase-structure:phase-public-underwrites:genre-civic-life"
    act(page, lambda: page.evaluate(CLICK, local))
    assert "recorded in phase 5 of 9" in folio(page)
    assert page.locator("#studio-atelier .atl-storytime .atl-st-item").count() == 1
    # A contract function whose words recur in phase functions is not linked to them by equal wording.
    small, small_errors = open_atelier(browser, served, "small", "&narrative")
    act(small, lambda: small.evaluate(CLICK, "tropes|trope:literary_mystery:0"))
    text = folio(small)
    assert "no phase record refers to it" in text and "phases 1, 3, 4 use the same words" in text
    assert small.locator("#studio-atelier .atl-star.is-listed").count() == 0
    # The baseline says nothing about story time.
    base, base_errors = open_atelier(browser, served, "dense")
    select(base, CIVIC)
    assert "in story time" not in folio(base) and base.locator("#studio-atelier .atl-star.is-listed").count() == 0
    assert errors == [] and small_errors == [] and base_errors == []


def test_story_time_by_keyboard_and_at_phone_width(browser, served):
    page, errors = open_atelier(browser, served, "dense", "&narrative")
    select(page, CIVIC)
    page.locator('#studio-atelier [data-key="depth"]').focus()
    page.keyboard.press("Tab")
    first = PHASE + "phase-first-signature"
    assert page.evaluate("document.activeElement.dataset.key") == "st:" + first
    # Keyboard focus on a story-time row emphasises its phase in the atlas, as hover would.
    assert "is-linked" in page.evaluate(LABEL, first)["classes"]
    act(page, lambda: page.keyboard.press("Enter"))
    assert page.evaluate(SNAP)["focus"] == first

    base, base_errors = open_atelier(browser, served, "dense", "", 390, 844)
    act(base, lambda: base.evaluate(CLICK, CIVIC))
    phone, phone_errors = open_atelier(browser, served, "dense", "&narrative", 390, 844)
    act(phone, lambda: phone.evaluate(CLICK, CIVIC))
    assert view(phone.evaluate(SNAP)) == view(base.evaluate(SNAP))
    assert phone.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert phone.evaluate(METRICS)["renderedLabelOverlaps"]["count"] == 0
    # A phase name that does not fit stays quiet; none is shown cut by the stage edge.
    assert phone.evaluate(CLIPPED) == 0
    assert errors == [] and base_errors == [] and phone_errors == []
