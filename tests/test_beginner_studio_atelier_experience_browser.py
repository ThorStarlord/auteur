"""Served Studio, dense recorded Architecture: regressions for the Atelier acceptance review (PR #628).

A pointer left where it clicked leaves no preview behind; a very long name never moves the stage; the
Focused Constellation keeps recorded story order; on a phone a vertical swipe scrolls the page while a
horizontal drag travels the atlas. The study writes nothing.
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

ARTIFACTS = Path(__file__).resolve().parents[1] / "qualification/studio-trace/artifacts"
CANDIDATE = ARTIFACTS / "candidate-2.json"
GENRE = "genres|genre:genre-procedural"
LONG = ("Converts forty years of ordinary use into a fact with standing: the public has been the span's "
        "real underwriter")


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
    root = tmp_path_factory.mktemp("atelier-dense")
    store = CanvasStore(root, "dense")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={"item": {
        "id": "story-vision", "kind": "note", "title": "Story Vision",
        "content": (ARTIFACTS / "story_vision.txt").read_text(encoding="utf-8").strip()},
        "position": {"x": 20, "y": 50}})
    waiting = prepare_architecture(store)
    reply = build_host_agent_response(HostAgentRequest(**waiting["request"]),
                                      CANDIDATE.read_text(encoding="utf-8"), runtime="integration-test").model_dump()
    complete_architecture(store, reply)
    server = BeginnerWorkspaceServer(root, port=0)
    thread = server.start_in_thread()
    yield f"http://127.0.0.1:{server.port}"
    server.stop()
    thread.join(timeout=5)


def revision(base):
    with urlopen(f"{base}/api/beginner/studio/canvases/dense") as response:
        return json.load(response)["revision"]


ARM = """() => { const r = document.getElementById('studio-atelier');
  window.__settled = new Promise(res => r.addEventListener('atelier:settled', e => res(e.detail), {once: true})); }"""
WAIT = "Promise.race([window.__settled, new Promise(r => setTimeout(() => r(null), 8000))])"
SNAP = "document.getElementById('studio-atelier').atelierStudy.snapshot()"
# Rendered geometry, not a model estimate: visible label boxes against each other and against glyphs
# they do not own, plus any transient emphasis still standing.
GEOMETRY = """() => { const r = document.getElementById('studio-atelier');
  const shown = e => { let o = 1, x = e; while (x && x !== r) { o *= parseFloat(getComputedStyle(x).opacity); x = x.parentElement; } return o > 0.35; };
  const labels = [...r.querySelectorAll('.atl-star .atl-text')].filter(shown)
    .map(t => ({id: t.parentElement.dataset.id, b: t.getBoundingClientRect()})).filter(x => x.b.width > 0);
  // Glyphs a label may never cover: landmarks at rest and the neighbourhood (faded or local glyphs may be covered).
  const glyphs = [...r.querySelectorAll('.atl-star:not([data-tier="2"]):not(.is-dim) .atl-glyph')].filter(shown)
    .map(g => ({id: g.parentElement.dataset.id, b: g.getBoundingClientRect()}));
  const ov = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2;
  let onLabel = 0, onGlyph = 0;
  for (let i = 0; i < labels.length; i++) {
    for (let j = i + 1; j < labels.length; j++) if (ov(labels[i].b, labels[j].b)) onLabel++;
    for (const g of glyphs) if (g.id !== labels[i].id && ov(labels[i].b, g.b)) onGlyph++;
  }
  return {labels: labels.length, onLabel, onGlyph, callouts: r.querySelectorAll('.atl-star.is-callout').length,
    linked: r.querySelectorAll('.atl-star.is-linked').length, previews: r.querySelectorAll('.atl-edge.is-preview').length,
    named: labels.map(x => x.id).sort()}; }"""


def open_dense(browser, base, **context):
    ctx = browser.new_context(**({"viewport": {"width": 1440, "height": 900}} | context))
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{base}/studio.html?canvas=dense&atelier", wait_until="networkidle")
    page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
    time.sleep(0.8)
    return ctx, page, errors


def settle(page, act):
    page.evaluate(ARM)
    act()
    detail = page.evaluate(WAIT)
    time.sleep(0.3)
    return detail


def glyph_point(page, concept):
    return page.evaluate("""(id) => { const b = document.querySelector('.atl-star[data-id="' + id + '"] .atl-glyph')
      .getBoundingClientRect(); return {x: b.left + b.width / 2, y: b.top + b.height / 2}; }""", concept)


def test_atlas_is_first_and_a_still_pointer_leaves_no_preview(served, browser):
    before = revision(served)
    ctx, page, errors = open_dense(browser, served)
    try:
        # The atlas is the first surface: its stage starts within the first screen and fills most of it.
        stage = page.evaluate("(() => { const b = document.querySelector('#studio-atelier .atl-stage').getBoundingClientRect(); return {top: b.top, bottom: b.bottom}; })()")
        assert stage["top"] < 320 and stage["bottom"] <= 900
        rest = page.evaluate(GEOMETRY)
        assert rest["onLabel"] == 0 and rest["callouts"] == 0
        # Every genre is named at rest.
        assert {c["id"] for c in page.evaluate(SNAP)["concepts"] if c["facet"] == "genres"} <= set(rest["named"])
        point = glyph_point(page, GENRE)
        page.mouse.move(point["x"] + 40, point["y"] + 40)
        settle(page, lambda: page.mouse.click(point["x"], point["y"]))  # the pointer stays on the focus
        for state in (page.evaluate(GEOMETRY),
                      settle(page, lambda: page.keyboard.press("]")) and page.evaluate(GEOMETRY)):
            assert state["onLabel"] == 0 and state["onGlyph"] == 0, state
            assert state["callouts"] == 0 and state["linked"] == 0 and state["previews"] == 0, state
        settle(page, lambda: page.keyboard.press("Escape"))  # pointer still where it clicked
        back = page.evaluate(GEOMETRY)
        assert back["onLabel"] == 0 and back["callouts"] == 0 and back["linked"] == 0 and back["previews"] == 0, back
        assert back["named"] == rest["named"]
        # Hover still works once the pointer really moves: one call-out with the complete name.
        quiet = page.evaluate("[...document.querySelectorAll('#studio-atelier .atl-star.is-quiet:not([data-tier=\"2\"])')].map(s => s.dataset.id)[0]")
        if quiet:
            q = glyph_point(page, quiet)
            page.mouse.move(q["x"] + 30, q["y"] + 30)
            page.mouse.move(q["x"], q["y"], steps=4)
            time.sleep(0.3)
            hover = page.evaluate(GEOMETRY)
            assert hover["callouts"] == 1
            page.mouse.move(5, 5, steps=4)
            time.sleep(0.3)
            assert page.evaluate(GEOMETRY)["callouts"] == 0
        # Keyboard navigation still emphasises the concept it reaches, and keeps focus on a concept.
        page.keyboard.press("ArrowRight")
        time.sleep(0.6)
        assert page.evaluate("document.activeElement.classList.contains('atl-star')")
        assert page.evaluate(GEOMETRY)["callouts"] == 1
        assert errors == []
    finally:
        ctx.close()
    assert revision(served) == before


def test_a_very_long_name_never_moves_the_stage(served, browser):
    ctx, page, errors = open_dense(browser, served)
    try:
        concept = page.evaluate("(t) => " + SNAP + ".concepts.find(c => c.title.startsWith(t)).id", LONG)
        title = page.evaluate("(id) => " + SNAP + ".concepts.find(c => c.id === id).title", concept)
        assert len(title) >= 240
        box = "(() => { const b = document.querySelector('#studio-atelier .atl-stage').getBoundingClientRect(); return [b.top, b.height]; })()"
        ribbon = "document.querySelector('#studio-atelier .atl-ribbon').getBoundingClientRect().height"
        before, ribbon_before = page.evaluate(box), page.evaluate(ribbon)
        settle(page, lambda: page.evaluate("(id) => document.querySelector('.atl-star[data-id=\"' + id + '\"]').click()", concept))
        assert page.evaluate(box) == before and page.evaluate(ribbon) == ribbon_before
        # The focus card wears the whole name; the folio title is the complete recorded title.
        card = page.evaluate("(id) => document.querySelector('.atl-star[data-id=\"' + id + '\"] .atl-label').textContent", concept)
        assert " ".join(card.split()) == title
        assert page.locator("#studio-atelier .atl-folio-title").inner_text() == title
        assert errors == []
    finally:
        ctx.close()


def test_constellation_keeps_recorded_story_order(served, browser):
    order = [f"timeline|phase:{p['id']}" for p in sorted(json.loads(CANDIDATE.read_text(encoding="utf-8"))["phases"],
                                                         key=lambda p: p["order"])]
    ctx, page, errors = open_dense(browser, served)
    try:
        rest = page.evaluate(SNAP)
        settle(page, lambda: page.evaluate("(id) => document.querySelector('.atl-star[data-id=\"' + id + '\"]').click()", GENRE))
        examined = settle(page, lambda: page.evaluate("document.querySelector('.atl-look [data-key=look]').click()"))
        assert examined["mode"] == "constellation"
        phases = page.evaluate("""() => [...document.querySelectorAll('#studio-atelier .atl-star.is-near[data-facet="timeline"]')]
          .map(s => ({id: s.dataset.id, x: s.querySelector('.atl-glyph').getBoundingClientRect().left}))
          .sort((a, b) => a.x - b.x).map(p => p.id)""")
        assert len(phases) >= 6
        assert phases == [p for p in order if p in phases]
        assert page.evaluate(GEOMETRY)["onLabel"] == 0
        back = settle(page, lambda: page.evaluate("document.querySelector('.atl-lensbar-leave').click()"))
        assert back["mode"] == "atlas" and page.evaluate(SNAP)["positions"] == rest["positions"]
        settle(page, lambda: page.evaluate("document.querySelector('.atl-folio .atl-return').click()"))
        assert page.evaluate(SNAP)["camera"] == rest["camera"]
        assert errors == []
    finally:
        ctx.close()


def swipe(cdp, x0, y0, x1, y1, steps=12):
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [{"x": x0, "y": y0}]})
    for i in range(1, steps + 1):
        cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": [
            {"x": x0 + (x1 - x0) * i / steps, "y": y0 + (y1 - y0) * i / steps}]})
        time.sleep(0.016)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    time.sleep(0.6)


def test_phone_swipes_scroll_the_page_and_drags_travel_the_atlas(served, browser):
    """Emulated touch through Chrome's own input pipeline; not a real device."""
    ctx, page, errors = open_dense(browser, served, viewport={"width": 390, "height": 844},
                                   device_scale_factor=2, is_mobile=True, has_touch=True)
    try:
        cdp = ctx.new_cdp_session(page)
        stage = page.evaluate("(() => { const b = document.querySelector('.atl-stage').getBoundingClientRect(); return {x: b.left + b.width / 2, y: b.top + b.height * 0.6}; })()")
        camera = page.evaluate(SNAP)["camera"]
        swipe(cdp, stage["x"], stage["y"] + 80, stage["x"] + 4, stage["y"] - 200)
        assert page.evaluate("scrollY") > 100 and page.evaluate(SNAP)["camera"] == camera
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.4)
        swipe(cdp, stage["x"] + 120, stage["y"], stage["x"] - 140, stage["y"] + 4)
        moved = page.evaluate(SNAP)
        assert page.evaluate("scrollY") == 0 and moved["camera"]["cx"] > camera["cx"] and moved["focus"] is None
        # The phone constellation is one list in recorded story order, and leaving gives the stage back.
        ctx2, phone, errors2 = open_dense(browser, served, viewport={"width": 390, "height": 844},
                                          device_scale_factor=2, is_mobile=True, has_touch=True)
        try:
            height = phone.evaluate("document.querySelector('.atl-stage').getBoundingClientRect().height")
            settle(phone, lambda: phone.evaluate("(id) => document.querySelector('.atl-star[data-id=\"' + id + '\"]').click()", GENRE))
            settle(phone, lambda: phone.evaluate("document.querySelector('.atl-look [data-key=look]').click()"))
            rows = phone.evaluate("""() => [...document.querySelectorAll('#studio-atelier .atl-star.is-near')].map(s =>
              ({id: s.dataset.id, facet: s.dataset.facet, y: s.querySelector('.atl-glyph').getBoundingClientRect().top,
                named: !s.classList.contains('is-quiet')}))""")
            assert all(r["named"] for r in rows)
            ys = [r["y"] for r in sorted(rows, key=lambda r: r["y"])]
            assert all(b - a >= 40 for a, b in zip(ys, ys[1:]))
            phases = [r["id"] for r in sorted(rows, key=lambda r: r["y"]) if r["facet"] == "timeline"]
            order = [f"timeline|phase:{p['id']}" for p in sorted(json.loads(CANDIDATE.read_text(encoding="utf-8"))["phases"], key=lambda p: p["order"])]
            assert phases == [p for p in order if p in phases]
            grown = phone.evaluate("document.querySelector('.atl-stage').getBoundingClientRect().height")
            assert grown > height
            settle(phone, lambda: phone.evaluate("document.querySelector('.atl-lensbar-leave').click()"))
            assert phone.evaluate("document.querySelector('.atl-stage').getBoundingClientRect().height") == height
            assert errors2 == []
        finally:
            ctx2.close()
        assert errors == []
    finally:
        ctx.close()
