"""Served Studio: considering a working Book element for the Architecture, from the Atelier.

The discovery card shows what the Book records and what is not established; keeping it in the Book writes
nothing; asking hands the element to the existing coding-agent panel as Book evidence, apart from the
question, and only the inquiry request is written. A Book that changed since it was read is refused by the
inquiry owner, and the way back from the panel returns to the discovery.
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as seed  # noqa: E402
from test_beginner_studio_book_discovery import edit_book_element  # noqa: E402

CANVAS = seed.SPRING
LEDGER = "structure|structure-node:eng_ledger"
SNAP = "document.getElementById('studio-atelier').atelierStudy.snapshot()"
LIVE = "document.querySelector('#studio-atelier .atl-live').textContent"
KEY = "document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.key || null : null"
PANEL = "#architecture-creative-agent-panel"


def q(key):
    return f'#studio-atelier [data-key="{key}"]'


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
def pristine(tmp_path_factory):
    root = tmp_path_factory.mktemp("discovery-browser") / "discovery"
    seed.seed_discovery(root)
    return root


@pytest.fixture
def served(pristine, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(pristine, project)
    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    yield project, f"http://127.0.0.1:{server.port}"
    server.stop()
    thread.join(timeout=5)


def open_discovery(browser, base, width=1440, height=900):
    page = browser.new_page(viewport={"width": width, "height": height})
    log = {"errors": [], "writes": []}
    page.on("pageerror", lambda error: log["errors"].append(str(error)))
    page.on("request", lambda r: log["writes"].append(r.url.split("/api/")[-1]) if r.method != "GET" else None)
    page.goto(f"{base}/studio.html?canvas={CANVAS}&atelier", wait_until="networkidle")
    page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
    time.sleep(0.6)
    log["writes"].clear()
    page.evaluate("(id) => document.querySelector('#studio-atelier .atl-star[data-id=\"' + id + '\"]').click()", LEDGER)
    page.wait_for_function("document.querySelector('#studio-atelier .atl-series .atl-series-status')", timeout=10000)
    page.locator(q("series-open:24")).click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    time.sleep(0.3)
    page.locator(q("book-discover:24:unk-tally-hours")).click()
    page.wait_for_selector(q("book-discovery-q:24"), timeout=10000)
    time.sleep(0.3)
    return page, log


def card(page):
    return page.locator("#studio-atelier .atl-discovery").inner_text()


def test_the_discovery_card_says_what_is_recorded_and_keeping_it_writes_nothing(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    text = card(page).upper()
    assert page.evaluate(KEY) == "book-discovery-h:24"
    assert "Established: Book 24 records this open question and a reference to “Ledger engine”.".upper() in text
    assert "Not established: whether it matters beyond Book 24".upper() in text
    assert "“Ledger engine” · recorded, unchanged since the Book was written".upper() in text
    assert "working revision 1 · element unk-tally-hours".upper() in text
    page.locator(q("book-keep:24")).click()
    time.sleep(0.4)
    assert page.locator("#studio-atelier .atl-discovery").count() == 0
    assert page.evaluate(KEY) == "book-discover:24:unk-tally-hours"
    assert "Kept in Book 24. Nothing was prepared or changed." in page.evaluate(LIVE)
    assert not log["writes"] and not log["errors"]


def test_asking_sends_the_element_as_book_evidence_and_writes_only_the_inquiry(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    page.locator(q("book-investigate:24")).click()
    time.sleep(0.8)
    evidence = page.locator(f"{PANEL} .creative-book-evidence").inner_text()
    assert "Book evidence · from working Book 24" in evidence and "not as your question" in evidence
    question = page.locator(f"{PANEL} textarea").first.input_value()
    assert question.startswith("Does Book 24’s open question about “Ledger engine” (attached as Book evidence)")
    assert "stewardship tally" not in question  # the Book's own words travel only as Book evidence
    page.locator(f"{PANEL} [data-creative-submit]").click()
    page.wait_for_function(f"document.querySelector('{PANEL} [role=status]').textContent.includes('prepared')", timeout=15000)
    request = json.loads(page.locator(f"{PANEL} textarea[aria-label='Prepared host-agent request']").input_value())
    packet = json.loads(request["user"])
    assert packet["author_question"] == question  # the Book's evidence is not folded into the question
    assert packet["book_evidence"]["element"]["id"] == "unk-tally-hours"
    assert packet["graph_intent"]["anchors"][0]["id"] == "eng_ledger"
    assert log["writes"] == [f"beginner/studio/canvases/{CANVAS}/architecture/inquiry/prepare"]
    assert "Request prepared for your coding agent, with Book 24’s element as Book evidence" in page.locator("#status").inner_text()
    # The way back from the panel returns to the discovery, and the atlas kept its place.
    page.locator("#studio-atelier .atl-desk-back").click()
    time.sleep(0.5)
    assert page.evaluate(KEY) == "book-discovery-h:24"
    assert "Asked: a request with this element is waiting for your coding agent." in card(page)
    assert not log["errors"]


def test_a_book_that_changed_since_it_was_read_is_refused_by_the_inquiry_owner(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    page.locator(q("book-investigate:24")).click()
    time.sleep(0.6)
    edit_book_element(project)  # the Book changes behind the author, through its own owner
    page.locator(f"{PANEL} [data-creative-submit]").click()
    time.sleep(1.5)
    assert "changed since you read it" in page.locator("#status").inner_text()
    assert not (project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture/inquiries/latest_request.json").exists()
    assert not log["errors"]


def test_escape_closes_the_discovery_and_typing_keeps_it(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    page.locator(q("book-discovery-q:24")).click()
    page.keyboard.type(" Mine.")
    page.keyboard.press("Escape")
    time.sleep(0.3)
    assert page.locator("#studio-atelier .atl-discovery").count() == 1  # Escape while typing never closes it
    page.locator(q("book-discovery-h:24")).focus()
    page.keyboard.press("Escape")
    time.sleep(0.3)
    assert page.locator("#studio-atelier .atl-discovery").count() == 0
    assert page.evaluate(SNAP)["series"]["leaf"] is not None  # one level only
    page.locator(q("book-discover:24:unk-tally-hours")).click()
    time.sleep(0.3)
    assert " Mine." in page.locator(q("book-discovery-q:24")).input_value()  # the author's words were kept
    assert not log["writes"] and not log["errors"]


def test_phone_width_keeps_the_discovery_inside_the_screen(browser, served):
    project, base = served
    page, log = open_discovery(browser, base, width=390, height=844)
    overflow = page.evaluate("""() => { const f = document.querySelector('#studio-atelier .atl-folio');
      return [document.documentElement.scrollWidth - document.documentElement.clientWidth, f.scrollWidth - f.clientWidth]; }""")
    assert overflow == [0, 0]
    assert page.locator(q("book-investigate:24")).count() == 1
    assert not log["errors"]


def test_an_open_discovery_reads_its_book_again_after_the_architecture_changes(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    from auteur.beginner.studio_store import CanvasStore
    seed.impact.reword_unrelated(CanvasStore(project, CANVAS))  # an Architecture revision applied elsewhere
    page.locator("#architecture-refresh").click()
    page.wait_for_function(f"({SNAP}).book.discovery !== null && document.querySelector('{q('book-discovery-q:24')}')",
                           timeout=15000)
    text = card(page)
    assert "Reading Book 24" not in text and "working revision 1 · element unk-tally-hours" in text
    assert not log["errors"]


def test_an_answer_is_brought_to_the_author_and_the_card_knows_it_was_asked(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    page.locator(q("book-investigate:24")).click()
    time.sleep(0.6)
    page.locator(f"{PANEL} [data-creative-submit]").click()
    page.wait_for_function(f"document.querySelector('{PANEL} [role=status]').textContent.includes('prepared')", timeout=15000)
    from auteur.beginner.studio_architecture_inquiry import complete_architecture_inquiry, project_architecture_inquiry
    from auteur.beginner.studio_store import CanvasStore
    from test_beginner_studio_book_discovery import answer
    store = CanvasStore(project, CANVAS)
    complete_architecture_inquiry(store, answer(project_architecture_inquiry(store)))  # the coding agent answers
    page.locator("#architecture-refresh").click()
    page.wait_for_function("document.activeElement && document.activeElement.dataset.inquiryAnswer === 'true'", timeout=15000)
    result = page.locator(f"{PANEL} section[aria-label='Inquiry result']").inner_text()
    assert "Answer to: “Does Book 24’s open question" in result and "asked with Book 24 evidence" in result
    assert "It is still the Book’s current record." in result
    assert "Developing none of these alternatives leaves the Architecture as it is" in result
    assert "Your coding agent’s answer arrived" in page.locator("#status").inner_text()
    page.locator("#studio-atelier .atl-desk-back").click()
    time.sleep(0.5)
    assert "Asked: your coding agent’s answer is in the coding-agent panel." in card(page)
    assert not log["errors"]


def test_check_reads_an_open_cards_book_again_and_a_damaged_book_is_named_unreadable(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    edit_book_element(project)  # Book 24 becomes revision 2 behind the author
    page.locator("#architecture-refresh").click()
    page.wait_for_function(f"document.querySelector('{q('book-discovery-h:24')}') && "
                           "document.querySelector('#studio-atelier .atl-discovery').innerText.includes('working revision 2')",
                           timeout=15000)
    (project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture/books/24/current.json").write_text("{damaged", encoding="utf-8")
    page.locator(q("book-reread:24")).click()
    page.wait_for_function("document.querySelector('#studio-atelier .atl-discovery').innerText.includes('cannot be read')", timeout=15000)
    assert "no longer records this element" not in card(page)
    assert not log["errors"]
