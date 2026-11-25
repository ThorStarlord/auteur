"""Served Studio: develop a working Book element from an Atelier concept, through the Book's own owner.

Atlas concept → the Book that records it → one element → a request for the coding agent → its response
through the owner's own command → the owner's review → explicit Apply → back to the same place in the atlas.
Only prepare and apply write, and only the Book's own records change. A Book revision is never shown as a
change to the Architecture, and a refused operation never looks like a successful one.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_book_development import (
    apply_book_revision, complete_book_revision, prepare_book_revision, project_book_development,
)
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import seed_series_context_study as seed  # noqa: E402
from seed_atelier_study import SPECIMENS, seed as seed_atelier  # noqa: E402

CANVAS = seed.SPRING
LEDGER = "structure|structure-node:eng_ledger"
SOURCE = "structure|structure-node:eng_source"
TARGET = "eng-record-form"
ADDED = " Refusing the count costs the cohort its season's water credit, entered where the Council can see it."
SNAP = "document.getElementById('studio-atelier').atelierStudy.snapshot()"
FOLIO = "document.querySelector('#studio-atelier .atl-folio').innerText"
LIVE = "document.querySelector('#studio-atelier .atl-live').textContent"
KEY = "document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.key || null : null"
CLICK = """(id) => document.querySelector('#studio-atelier .atl-star[data-id="' + id + '"]').click()"""


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
    root = tmp_path_factory.mktemp("book-dev-served")
    seed.seed_spring(root / "linked")
    context = root / "context"
    seed_atelier(context, "atelier-small", SPECIMENS["atelier-small"])
    shutil.copyfile(seed.FULL_PLAN, context / "series_identity.yaml")
    seed.seed_sparse(context)
    return root


@pytest.fixture
def served(pristine, tmp_path):
    """A fresh copy of one seeded project, served for one test."""
    started = []

    def start(name="linked"):
        project = tmp_path / name
        shutil.copytree(pristine / name, project)
        server = BeginnerWorkspaceServer(project, port=0)
        started.append((server, server.start_in_thread()))
        return project, f"http://127.0.0.1:{server.port}"
    yield start
    for server, thread in started:
        server.stop()
        thread.join(timeout=5)


def open_atelier(browser, base, canvas=CANVAS, width=1440, height=900, atelier=True):
    page = browser.new_page(viewport={"width": width, "height": height})
    log = {"errors": [], "writes": [], "books": []}
    page.on("pageerror", lambda error: log["errors"].append(str(error)))
    page.on("request", lambda r: (log["writes"].append(r.url.split("/api/")[-1]) if r.method != "GET" else None,
                                  log["books"].append(r.url) if "/books/" in r.url else None))
    page.goto(f"{base}/studio.html?canvas={canvas}" + ("&atelier" if atelier else ""), wait_until="networkidle")
    if atelier:
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        time.sleep(0.6)
    log["writes"].clear()
    return page, log


def open_book(page, concept=LEDGER):
    page.evaluate(CLICK, concept)
    page.wait_for_function("document.querySelector('#studio-atelier .atl-series .atl-series-status')", timeout=10000)
    page.locator(q("series-open:24")).click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    time.sleep(0.3)


def develop(page, instruction="Make the cost of refusing the count visible inside this mechanism."):
    page.locator(q(f"book-dev:24:{TARGET}")).click()
    page.wait_for_selector(q("book-instruction:24"), timeout=10000)
    page.wait_for_function(f"({KEY}) === 'book-instruction:24'", timeout=5000)
    page.keyboard.type(instruction)


def wait_for(page, key, timeout=10000):
    page.wait_for_selector(q(key), timeout=timeout)
    time.sleep(0.3)


def book_dir(project):
    return project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture/books/24"


def current(project):
    return json.loads((book_dir(project) / "current.json").read_text(encoding="utf-8"))


def outside_book(project):
    book = book_dir(project)
    return {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(project.rglob("*"))
            if p.is_file() and book not in p.parents and not p.name.endswith(".lock")}


def candidate(project, *, beyond=False):
    artifact = json.loads(json.dumps(current(project)["artifact"]))
    for index, element in enumerate(artifact["engines"]):
        if element["id"] == TARGET or (beyond and index == 0):
            element.pop("provenance", None)
            element["attribution"], element["epistemic_status"] = "agent_proposed", "asserted"
            element["text"] += ADDED if element["id"] == TARGET else " (outside the request)"
    return artifact


def agent_cli(project, artifact):
    """The coding agent's side: the owner's own commands, in a fresh process."""
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"), PYTHONUTF8="1")
    base = [sys.executable, "-m", "auteur.series.working_book_architecture", "--project", str(project), "--canvas", CANVAS]
    shown = subprocess.run([*base, "book-show", "--book", "24"], capture_output=True, text=True, encoding="utf-8",
                           env=env, check=True)
    assert json.loads(shown.stdout)["status"] == "awaiting_host_agent"
    path = project.parent / "revised.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    done = subprocess.run([*base, "book-complete-file", "--book", "24", "--candidate", str(path)],
                          capture_output=True, text=True, encoding="utf-8", env=env, check=False)
    return json.loads(done.stdout)


def place(snapshot):
    return {key: snapshot[key] for key in ("focus", "trail", "mode", "depth", "camera", "positions")}


def test_develop_review_apply_and_return_changes_only_the_working_book(browser, served):
    project, base = served()
    outside = outside_book(project)
    page, log = open_atelier(browser, base)
    open_book(page)
    before = page.evaluate(SNAP)
    develop(page)
    folio = page.evaluate(FOLIO)
    assert "revise one element" in folio.lower() and "working revision 0" in folio
    assert "It records a reference to “Ledger engine”, the concept you came from." in folio
    assert "the 2 elements that refer to it" in folio  # the owner's dependent rule, before anything is prepared
    assert not log["writes"]  # opening the composer and checking the scope write nothing
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    assert page.evaluate(KEY) == "book-copy:24"  # the message for the coding agent is open, its Copy focused
    assert "Nothing in Book 24 has changed" in page.evaluate(LIVE)
    # Every word the author typed is in the request, exactly.
    assert project_book_development(project, CANVAS, 24)["pending"]["instruction"] ==         "Make the cost of refusing the count visible inside this mechanism."
    assert page.locator(q("book-agent:24")).get_attribute("open") is not None
    assert "book-show --book 24" in page.locator(f"{q('book-agent:24')} textarea").first.input_value()
    assert agent_cli(project, candidate(project))["status"] == "review_ready"
    assert current(project).get("revision_number", 0) == 0  # a stored review is not an applied one
    page.locator(q("book-check:24")).click()
    wait_for(page, "book-apply:24")
    assert page.evaluate(KEY) == "book-review:24"
    folio = page.evaluate(FOLIO)
    assert "Review · working revision 0 → 1" in folio and "Its wording or interpretation changed" in folio
    assert "The reference is recorded; whether it still holds is not." in folio
    assert "The Architecture is unchanged; check that the Book still fits each concept." in folio
    page.locator(q("book-apply:24")).click()
    wait_for(page, "book-note:24")
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    time.sleep(0.4)
    folio = page.evaluate(FOLIO)
    assert "now working revision 1" in folio and "Changed in working Book revision 1" in folio
    assert "Only this working Book changed" in folio
    assert "Only the working Book changed; the atlas is unchanged." in page.evaluate(LIVE)
    after_apply = page.evaluate(SNAP)
    assert after_apply["revision"] is None  # no Architecture concept is marked as changed
    assert place(after_apply) == place(before)
    page.keyboard.press("Escape")
    time.sleep(0.4)
    back = page.evaluate(SNAP)
    assert back["series"]["leaf"] is None and place(back) == place(before)
    assert page.evaluate(KEY) == "series-open:24"
    assert log["writes"] == [f"beginner/studio/canvases/{CANVAS}/books/24/prepare",
                             f"beginner/studio/canvases/{CANVAS}/books/24/apply"]
    assert not log["errors"]
    assert current(project)["revision_number"] == 1 and outside_book(project) == outside


def test_a_blocked_review_offers_no_apply_and_prepares_again_with_the_wider_scope(browser, served):
    project, base = served()
    page, log = open_atelier(browser, base)
    open_book(page)
    develop(page)
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    first = project_book_development(project, CANVAS, 24)["pending"]["request_sha256"]
    assert agent_cli(project, candidate(project, beyond=True))["status"] == "review_blocked"
    page.locator(q("book-check:24")).click()
    wait_for(page, "book-widen:24")
    assert page.locator(q("book-apply:24")).count() == 0
    assert "outside what you allowed — this blocks apply" in page.evaluate(FOLIO).lower()
    page.locator(q("book-widen:24")).click()
    wait_for(page, "book-instruction:24")
    snap = page.evaluate(SNAP)["book"]["dev"]
    first_engine = current(project)["artifact"]["engines"][0]["id"]
    assert first_engine in snap["targets"] and TARGET in snap["targets"] and not snap["holistic"]
    assert page.locator(q("book-instruction:24")).input_value().startswith("Make the cost")
    assert page.locator(q("book-replace:24")).is_checked()
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    pending = project_book_development(project, CANVAS, 24)["pending"]
    assert pending["request_sha256"] != first and first_engine in pending["targets"]
    assert current(project).get("revision_number", 0) == 0 and not log["errors"]


def test_apply_is_checked_again_at_the_write_and_a_refusal_changes_nothing(browser, served):
    project, base = served()
    page, log = open_atelier(browser, base)
    open_book(page)
    develop(page)
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    agent_cli(project, candidate(project))
    page.locator(q("book-check:24")).click()
    wait_for(page, "book-apply:24")
    # The working Architecture is revised elsewhere while the review is on screen.
    seed.remove_node(CanvasStore(project, CANVAS), seed.REMOVED_NODE)
    before = current(project)
    page.locator(q("book-apply:24")).click()
    wait_for(page, "book-note:24")
    folio = page.evaluate(FOLIO)
    assert "Not applied: working context changed" in folio and "Working Book 24 is unchanged." in folio
    assert "Not applied" in page.evaluate(LIVE)  # the refusal is announced, not only drawn
    assert current(project) == before
    page.wait_for_selector(q("book-redo:24"), timeout=10000)  # re-read: the request is now out of date
    assert "no longer matches the Book or its sources" in page.evaluate(FOLIO)
    page.locator(q("book-redo:24")).click()
    wait_for(page, "book-instruction:24")
    assert page.locator(q("book-replace:24")).is_checked()
    assert not log["errors"]


def test_a_refused_prepare_keeps_the_authors_words(browser, served):
    project, base = served()
    page, _ = open_atelier(browser, base)
    open_book(page)
    develop(page, "My own unsent words.")
    # Book 24 changes elsewhere after the author read it.
    view = project_book_development(project, CANVAS, 24)
    view = prepare_book_revision(project, CANVAS, 24, {"instruction": "elsewhere", "targets": [TARGET],
                                                       "expected_book_request_sha256": view["book"]["request_sha256"]})
    view = complete_book_revision(project, CANVAS, 24, build_host_agent_response(
        HostAgentRequest(**view["request"]), json.dumps(candidate(project)), runtime="elsewhere").model_dump())
    apply_book_revision(project, CANVAS, 24, {"request_sha256": view["pending"]["request_sha256"]})
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-note:24")
    folio = page.evaluate(FOLIO)
    assert "Not prepared: the working Book 24 changed since you read it" in folio and "Your words are kept." in folio
    assert page.locator(q("book-instruction:24")).input_value() == "My own unsent words."
    assert project_book_development(project, CANVAS, 24)["phase"] == "none"


def test_an_invalid_pasted_response_is_refused_and_the_request_stays_open(browser, served):
    project, base = served()
    page, _ = open_atelier(browser, base)
    open_book(page)
    develop(page)
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    request = project_book_development(project, CANVAS, 24)["request"]
    broken = candidate(project)
    broken["engines"][0]["attribution"] = "accepted"
    response = build_host_agent_response(HostAgentRequest(**request), json.dumps(broken), runtime="pasted").model_dump()
    page.locator(f"{q('book-agent:24')} details", has_text="Paste the coding agent").locator("summary").click()
    page.locator(q("book-response:24")).fill(json.dumps(response))
    page.locator(q("book-validate:24")).click()
    wait_for(page, "book-note:24")
    assert "The Working Book owner refused the response" in page.evaluate(FOLIO)
    assert project_book_development(project, CANVAS, 24)["phase"] == "awaiting_coding_agent"


def test_moving_on_while_apply_is_in_flight_keeps_the_new_place(browser, served):
    project, base = served()
    page, log = open_atelier(browser, base)
    open_book(page)
    develop(page)
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    agent_cli(project, candidate(project))
    page.locator(q("book-check:24")).click()
    wait_for(page, "book-apply:24")
    held = []
    page.route("**/books/24/apply", lambda route: held.append(route))
    page.locator(q("book-apply:24")).click()
    page.wait_for_function("document.querySelector('[data-key=\"book-apply:24\"]').disabled", timeout=5000)
    page.keyboard.press("Escape")
    page.evaluate(CLICK, SOURCE)
    time.sleep(0.4)
    held[0].continue_()
    time.sleep(1.5)
    snap = page.evaluate(SNAP)
    assert snap["focus"] == SOURCE and snap["series"]["leaf"] is None and snap["revision"] is None
    assert current(project)["revision_number"] == 1 and not log["errors"]


def test_plans_without_a_working_book_offer_no_revision(browser, served):
    _, base = served("context")
    page, log = open_atelier(browser, base, "atelier-small")
    page.evaluate(CLICK, page.evaluate(f"({SNAP}).concepts[0].id"))
    page.wait_for_function("document.querySelector('#studio-atelier .atl-series .atl-series-status')", timeout=10000)
    page.locator(q("series-open")).click()
    page.wait_for_function(f"({SNAP}).series.status === 'ready'", timeout=10000)
    time.sleep(0.3)
    assert page.locator("#studio-atelier [data-key^='book-']").count() == 0
    assert "Develop" not in page.evaluate(FOLIO)
    assert not log["books"] and not log["writes"] and not log["errors"]


def test_the_ordinary_studio_never_asks_for_books(browser, served):
    _, base = served()
    page, log = open_atelier(browser, base, atelier=False)
    time.sleep(1.0)
    assert not log["books"] and not log["errors"]


def test_phone_width_keeps_the_composer_and_review_inside_the_screen(browser, served):
    project, base = served()
    page, log = open_atelier(browser, base, width=390, height=844)
    open_book(page)
    develop(page)
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    agent_cli(project, candidate(project))
    page.locator(q("book-check:24")).click()
    wait_for(page, "book-apply:24")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
    widths = page.evaluate("""[...document.querySelectorAll('#studio-atelier .atl-book-dev, #studio-atelier .atl-book-dev textarea')]
      .map(e => e.getBoundingClientRect().right)""")
    assert widths and max(widths) <= 391
    assert not log["errors"]


def test_unsent_words_stay_with_their_element_and_the_view_stays_open(browser, served):
    project, base = served()
    page, log = open_atelier(browser, base)
    open_book(page)
    develop(page, "Words for the record form.")
    # Escape inside the field leaves the view and the words where they are.
    page.keyboard.press("Escape")
    time.sleep(0.3)
    assert page.evaluate(SNAP)["series"]["leaf"] is not None
    assert page.locator(q("book-instruction:24")).input_value() == "Words for the record form."
    # An opened disclosure stays open when the scope changes and the composer is drawn again.
    page.locator(f"{q('book-ids:24')} summary").click()
    page.locator(q("book-scope:24:holistic")).check()
    time.sleep(0.4)
    assert page.locator(q("book-ids:24")).get_attribute("open") is not None
    assert page.locator(q("book-instruction:24")).input_value() == "Words for the record form."  # they moved with the author
    page.locator(q("book-scope:24:targeted")).check()
    time.sleep(0.3)
    page.locator(q("book-cancel:24")).click()
    time.sleep(0.3)
    # Another element starts with its own, empty draft; the first keeps its words.
    page.locator(q("book-dev:24:eng-old-hand-ledger")).click()
    page.wait_for_selector(q("book-instruction:24"), timeout=10000)
    time.sleep(0.3)
    assert page.locator(q("book-instruction:24")).input_value() == ""
    page.locator(q("book-cancel:24")).click()
    time.sleep(0.3)
    page.locator(q(f"book-dev:24:{TARGET}")).click()
    page.wait_for_selector(q("book-instruction:24"), timeout=10000)
    time.sleep(0.3)
    assert page.locator(q("book-instruction:24")).input_value() == "Words for the record form."
    page.locator(q("book-prepare:24")).click()
    wait_for(page, "book-check:24")
    assert project_book_development(project, CANVAS, 24)["pending"]["instruction"] == "Words for the record form."
    assert not log["errors"]
