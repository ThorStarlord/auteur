"""Served Studio: from an Atelier concept into its Book and Series plans, read-only, and back.

A concept shows a Book plan only when that Book records a reference to the concept's node id. The
project's Series plan and Directions are offered as context, never as related plans. Opening the view
changes nothing, and Back (or Escape) returns to the same concept, trail and camera.
"""
import copy
import json
import os
import shutil
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, project_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import seed_series_context_study as seed  # noqa: E402
from seed_atelier_study import SPECIMENS, seed as seed_atelier  # noqa: E402

LEDGER = "structure|structure-node:eng_ledger"
SOURCE = "structure|structure-node:eng_source"
SNAP = "document.getElementById('studio-atelier').atelierStudy.snapshot()"
FOLIO = "document.querySelector('#studio-atelier .atl-folio').innerText"
SECTION = "(document.querySelector('#studio-atelier .atl-series')||{}).innerText||''"
LIVE = "document.querySelector('#studio-atelier [aria-live]').textContent"
ACTIVE_KEY = "document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.key || null : null"
CLICK = """(id) => document.querySelector('#studio-atelier .atl-star[data-id="' + id + '"]').click()"""
ARM = """() => { const r = document.getElementById('studio-atelier');
  window.__settled = new Promise(res => r.addEventListener('atelier:settled', e => res(e.detail), {once: true})); }"""
WAIT = "Promise.race([window.__settled, new Promise(r => setTimeout(() => r(null), 8000))])"
PANEL = "#architecture-creative-agent-panel"
FIELD = "#architecture-creative-agent-panel textarea"


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
def projects(tmp_path_factory):
    root = tmp_path_factory.mktemp("series-context")
    seed.seed_spring(root / "linked")
    context = root / "context"
    seed_atelier(context, "atelier-small", SPECIMENS["atelier-small"])
    shutil.copyfile(seed.FULL_PLAN, context / "series_identity.yaml")
    seed.seed_sparse(context)
    seed_atelier(root / "none", "atelier-small", SPECIMENS["atelier-small"])
    damaged = root / "damaged"
    seed.remove_node(seed.seed_spring(damaged), seed.REMOVED_NODE)
    (damaged / "series_identity.yaml").write_text("title: Unfinished\nbook_plans: [\n", encoding="utf-8")
    seed.seed_sparse(damaged)
    accepted = damaged / ".auteur/series/vertical-slice/accepted/series-direction.yaml"
    accepted.write_text(accepted.read_text(encoding="utf-8").replace("Archive of Lies", "Archive of Truths"),
                        encoding="utf-8")
    servers = {}
    for name in ("linked", "context", "none", "damaged"):
        server = BeginnerWorkspaceServer(root / name, port=0)
        servers[name] = (server, server.start_in_thread())
    yield {name: f"http://127.0.0.1:{server.port}" for name, (server, _thread) in servers.items()} | {"root": root}
    for server, thread in servers.values():
        server.stop()
        thread.join(timeout=5)


def open_atelier(browser, base, canvas, width=1440, height=900, atelier=True):
    page = browser.new_page(viewport={"width": width, "height": height})
    errors, writes, series = [], [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda r: (writes.append(r.url) if r.method != "GET" else None,
                                  series.append(r.url) if "series-context" in r.url else None))
    page.goto(f"{base}/studio.html?canvas={canvas}" + ("&atelier" if atelier else ""), wait_until="networkidle")
    if atelier:
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        time.sleep(0.6)
    writes.clear()  # opening the Studio ensures its canvas exists; only what follows is the journey's
    return page, errors, writes, series


def choose(page, concept):
    page.evaluate(CLICK, concept)
    page.wait_for_function("document.querySelector('#studio-atelier .atl-series .atl-series-status')", timeout=10000)
    time.sleep(0.4)


def place(snapshot):
    return {key: snapshot[key] for key in ("focus", "trail", "mode", "depth", "camera", "positions")}


def test_a_concept_opens_the_book_that_records_it_and_returns(browser, projects):
    page, errors, writes, _ = open_atelier(browser, projects["linked"], seed.SPRING)
    choose(page, LEDGER)
    section = page.evaluate(SECTION)
    assert "Book 24 · The Uncounted Crew" in section and "Records a reference to this concept in 4 elements" in section
    assert "not accepted" in section and "Read at " in section
    before = place(page.evaluate(SNAP))
    opener = page.locator('#studio-atelier [data-key="series-open:24"]')
    opener.focus()
    page.keyboard.press("Enter")
    page.wait_for_function(f"({SNAP}).series.leaf && ({SNAP}).series.status === 'ready'", timeout=10000)
    time.sleep(0.3)
    folio = page.evaluate(FOLIO)
    assert "What Book 24 records about “Ledger engine”" in folio
    assert "The craft-mark answers all three." in folio and "Unchanged since the Book was written." in folio
    assert "Written against the current working Architecture." in folio
    assert page.evaluate("document.activeElement.classList.contains('atl-folio-title')")
    assert "Back returns to “Ledger engine”" in page.evaluate(LIVE)  # opening orients; it is not a re-read
    assert place(page.evaluate(SNAP)) == before  # the atlas did not move while the plans are read
    page.keyboard.press("Escape")
    time.sleep(0.4)
    after = page.evaluate(SNAP)
    assert after["series"]["leaf"] is None and place(after) == before
    assert page.evaluate(ACTIVE_KEY) == "series-open:24"
    assert "Your place in the atlas is unchanged" in page.evaluate(LIVE)
    assert not writes and not errors


def test_another_concept_the_book_refers_to_is_shown_in_the_atlas(browser, projects):
    page, errors, writes, _ = open_atelier(browser, projects["linked"], seed.SPRING)
    choose(page, LEDGER)
    page.locator('#studio-atelier [data-key="series-open:24"]').click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    page.locator('#studio-atelier [data-key="series-node:24:eng_source"]').click()
    time.sleep(0.5)
    snap = page.evaluate(SNAP)
    assert snap["focus"] == SOURCE and snap["trail"] == [LEDGER, SOURCE] and snap["series"]["leaf"] is None
    assert "Book 24 · The Uncounted Crew" in page.evaluate(SECTION)
    assert not writes and not errors


def test_project_plans_are_context_not_links_and_a_hypothesis_is_only_drafted(browser, projects):
    page, errors, writes, _ = open_atelier(browser, projects["context"], "atelier-small")
    genre = next(c["id"] for c in page.evaluate(SNAP)["concepts"] if c["facet"] == "genres" and c["tier"] == 1)
    choose(page, genre)
    section = page.evaluate(SECTION)
    assert "Recorded in Book plans" not in section
    assert "Not linked to this concept" in section and "The Ash Empire Trilogy" in section
    page.locator('#studio-atelier [data-key="series-open"]').click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    folio = page.evaluate(FOLIO)
    for text in ("Author-declared plan · no acceptance record", "series_identity.yaml · narrative_setups[0]",
                 "The plan records its payoff in Book 3", "Accepted · revision 2",
                 "Accepted against Series Direction revision 1; the Series Direction is now revision 2",
                 "nothing records that they describe the same Series", "Equal words are not a link"):
        assert text in folio, text
    page.locator('#studio-atelier [data-key="series-ask:series_identity.yaml#narrative_setups[0]"]').click()
    time.sleep(0.5)
    field = page.locator("#architecture-creative-agent-panel textarea").first
    assert "not a recorded link" in field.input_value() and "narrative_setups[0]" in field.input_value()
    assert page.evaluate("document.activeElement === document.querySelector('#architecture-creative-agent-panel textarea')")
    assert page.evaluate(SNAP)["series"]["leaf"]["from"] == genre  # the view the author left is still open
    assert not writes and not errors  # a drafted question is not a sent one


def test_damaged_and_stale_records_are_reported_and_withheld(browser, projects):
    page, errors, writes, _ = open_atelier(browser, projects["damaged"], seed.SPRING)
    choose(page, LEDGER)
    section = page.evaluate(SECTION)
    assert "A concept it refers to is no longer in the working Architecture." in section
    assert "series_identity.yaml could not be read as a Series plan." in section
    page.locator('#studio-atelier [data-key="series-open:24"]').click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    folio = page.evaluate(FOLIO)
    assert "Written against an earlier working Architecture request" in folio
    assert "inst_gate_table · no longer recorded" in folio
    assert "does not match its acceptance record" in folio and "Archive of Truths" not in folio
    assert "the current Series Direction does not verify" in folio
    assert not writes and not errors


def test_no_plans_is_said_plainly_and_the_ordinary_studio_never_asks(browser, projects):
    page, errors, _, _ = open_atelier(browser, projects["none"], "atelier-small")
    choose(page, next(c["id"] for c in page.evaluate(SNAP)["concepts"] if c["facet"] == "genres"))
    assert "No Book or Series plan is kept for this canvas or project" in page.evaluate(SECTION)
    assert page.locator('#studio-atelier [data-key="series-open"]').count() == 0
    plain, plain_errors, _, series = open_atelier(browser, projects["linked"], seed.SPRING, atelier=False)
    time.sleep(1.0)
    assert not series and not plain_errors and not errors
    assert plain.locator(".atl-series").count() == 0


def test_phone_width_reads_the_plans_and_returns(browser, projects):
    page, errors, _, _ = open_atelier(browser, projects["linked"], seed.SPRING, width=390, height=844)
    choose(page, LEDGER)
    page.locator('#studio-atelier [data-key="series-open:24"]').click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.locator('#studio-atelier [data-key="series-back-end"]').click()
    time.sleep(0.4)
    snap = page.evaluate(SNAP)
    assert snap["series"]["leaf"] is None and snap["focus"] == LEDGER
    assert page.evaluate(ACTIVE_KEY) == "series-open:24"
    assert not errors


def serve(project):
    server = BeginnerWorkspaceServer(project, port=0)
    return server, server.start_in_thread(), f"http://127.0.0.1:{server.port}"


def test_an_applied_revision_reads_the_open_plans_again(browser, projects, tmp_path):
    project = tmp_path / "linked"
    shutil.copytree(projects["root"] / "linked", project)
    store = CanvasStore(project, seed.SPRING)
    server, thread, base = serve(project)
    try:
        page, errors, _, _ = open_atelier(browser, base, seed.SPRING)
        choose(page, LEDGER)
        page.evaluate(ARM)
        page.locator('#studio-atelier .atl-develop button[data-operation="revise"]').click()
        page.evaluate(WAIT)
        page.keyboard.type("Reword only the Ledger engine summary.")
        page.locator(f"{PANEL} [data-creative-submit]").click()
        time.sleep(1.5)
        waiting = project_architecture(store)
        revised = copy.deepcopy(waiting["candidate"])
        node = next(n for n in revised["nodes"] if n["id"] == "eng_ledger")
        node["summary"] += " Reworded for the test."
        complete_architecture(store, build_host_agent_response(
            HostAgentRequest(**waiting["request"]), json.dumps(revised), runtime="series-test").model_dump())
        page.locator(".atelier-return").first.click()
        time.sleep(0.6)
        page.locator('#studio-atelier [data-key="series-open:24"]').click()
        page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
        assert "Written against the current working Architecture." in page.evaluate(FOLIO)
        page.locator("#architecture-refresh").click()
        page.wait_for_selector("#architecture-review:not([hidden])", timeout=10000)
        page.evaluate(ARM)
        page.locator("#architecture-apply").click()
        page.evaluate(WAIT)
        page.wait_for_function(f"({SNAP}).series.status === 'ready' && ({SNAP}).series.changed", timeout=10000)
        time.sleep(0.4)
        snap = page.evaluate(SNAP)
        assert snap["focus"] == LEDGER and snap["series"]["leaf"]["from"] == LEDGER
        folio = page.evaluate(FOLIO)
        assert "Written against an earlier working Architecture request" in folio
        assert "This concept changed after the Book was written." in folio
        assert "Written against the current working Architecture." not in folio
        assert not errors
    finally:
        server.stop()
        thread.join(timeout=5)


def test_an_unreadable_book_is_never_reported_as_no_plan(browser, projects, tmp_path):
    project = tmp_path / "linked"
    shutil.copytree(projects["root"] / "linked", project)
    record = project / ".auteur/beginner/studio/canvases" / seed.SPRING / "architecture/books/24/current.json"
    record.write_text(record.read_text(encoding="utf-8")[:200], encoding="utf-8")
    server, thread, base = serve(project)
    try:
        page, errors, _, _ = open_atelier(browser, base, seed.SPRING)
        choose(page, LEDGER)
        section = page.evaluate(SECTION)
        assert "No Book or Series plan is kept" not in section
        assert "Book 24’s working architecture could not be read" in section
        page.locator('#studio-atelier [data-key="series-open"]').click()
        page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
        folio = page.evaluate(FOLIO)
        assert "a Book that could not be read might" in folio and "Plans that record" not in folio
        assert not errors
    finally:
        server.stop()
        thread.join(timeout=5)


def test_a_new_hypothesis_replaces_an_untouched_suggestion_but_keeps_the_authors_words(browser, projects):
    page, errors, writes, _ = open_atelier(browser, projects["context"], "atelier-small")
    genres = [c for c in page.evaluate(SNAP)["concepts"] if c["facet"] == "genres" and c["tier"] == 1]
    first, second = genres[0], genres[1]
    for concept, key in ((first, "series_identity.yaml#narrative_setups[0]"), (second, "series_identity.yaml#narrative_setups[1]")):
        choose(page, concept["id"])
        page.locator('#studio-atelier [data-key="series-open"]').click()
        page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
        page.locator(f'#studio-atelier [data-key="series-ask:{key}"]').click()
        time.sleep(0.5)
        page.locator(".atelier-return").first.click()
        time.sleep(0.4)
        page.keyboard.press("Escape")
        time.sleep(0.3)
    text = page.locator(FIELD).first.input_value()
    assert second["title"] in text and first["title"] not in text and "narrative_setups[1]" in text
    page.locator(FIELD).first.fill("My own question.")
    choose(page, first["id"])
    page.locator('#studio-atelier [data-key="series-open"]').click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    page.locator('#studio-atelier [data-key="series-ask:series_identity.yaml#narrative_setups[0]"]').click()
    time.sleep(0.5)
    assert page.locator(FIELD).first.input_value() == "My own question."
    assert not writes and not errors
