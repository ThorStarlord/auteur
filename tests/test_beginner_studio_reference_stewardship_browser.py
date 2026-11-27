"""The served Atelier adopts a positional observation through the reviewed Working Book workflow.

The author meets Book 25's prose from the question it names (a lead, not a reference). The Book's own development panel shows
the observation with its historical reading and the choices the owner allows. The author chooses the current question; the
owner prepares a request; a coding agent's unedited answer is checked and reviewed by the owner; the author applies it through the
served control. The question reading then lists both Books as engaging the question.

The coding agent's answer and the request it answers are the evidence in
docs/qualification-evidence/narrative-reference-stewardship-20261127/reproduce/exercise-a. The request must match the one the
served page prepares, so a change that alters the packet fails here rather than passing an answer written for another request.
"""
import contextlib
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_store import CanvasStore
from auteur.series.working_book_architecture import book_complete, book_project
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "docs/qualification-evidence/narrative-reference-stewardship-20261127/reproduce/exercise-a"
sys.path.insert(0, str(REPO / "tests"))
_spec = importlib.util.spec_from_file_location("exercise_a", EVIDENCE.parent / "exercise_a.py")
exercise_a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exercise_a)

CANVAS = exercise_a.discovery.SPRING
BLIND_SPOT = exercise_a.BLIND_SPOT
CONVERSION = exercise_a.CONVERSION
BOOK = exercise_a.BOOK  # Book 25: the one that gains the association in this journey
BOOK_ASSOCIATED = exercise_a.BOOK_ASSOCIATED  # Book 24: its association was applied from PR #648's evidence


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        yield instance
        instance.close()


@pytest.fixture(scope="module")
def seeded(tmp_path_factory):
    """Identities, Book 24's applied association, and Book 25 up to date with the Architecture (the exercise's own seed)."""
    root = tmp_path_factory.mktemp("stewardship") / "root"
    exercise_a.seed(root, root.parent / "seed-out")
    return root


def store_of(project: Path) -> CanvasStore:
    """The study's own canvas store: `project` is the discovery folder itself."""
    return CanvasStore(project, CANVAS)


def project_record(project: Path, number: int) -> Path:
    return project / ".auteur/beginner/studio/canvases" / CANVAS / f"architecture/books/{number}/current.json"


def digest_tree(project: Path) -> dict[str, str]:
    return {str(path.relative_to(project)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(project.rglob("*")) if path.is_file() and not path.name.endswith(".lock")}


@contextlib.contextmanager
def served(browser, project: Path, width: int = 1440, height: int = 900):
    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas={CANVAS}&atelier", wait_until="networkidle")
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        page.wait_for_selector('#studio-atelier [data-key="questions-all"]', state="attached", timeout=20000)
        yield server, page, errors
        assert not errors, errors
    finally:
        page.close()
        server.stop()
        thread.join(timeout=5)


def open_question(page, identifier: str) -> None:
    page.locator('#studio-atelier [data-key="questions-all"]').click()
    page.locator(f'#studio-atelier .atl-question-item[data-key="question:{identifier}"]').click()
    page.wait_for_selector("#studio-atelier .atl-folio", timeout=10000)


def folio_text(page) -> str:
    return page.locator("#studio-atelier .atl-folio").text_content()


def test_the_question_names_a_lead_in_book_25_and_records_nothing_until_it_is_applied(browser, seeded, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(seeded / "discovery", project)
    before = digest_tree(project)
    with served(browser, project) as (server, page, errors):
        open_question(page, CONVERSION)
        text = folio_text(page)
        # Book 24's association is applied: it is an engagement. Book 25's blind spot names the question by position only: a lead.
        assert "Book elements that engage it · 1" in text
        assert "Book prose that names it by position" in text
        assert "a lead to review, not an identity" in text
        assert page.locator(f'#studio-atelier [data-key="question-lead:{BOOK}:{BLIND_SPOT}"]').count() == 1
        assert page.locator(f'#studio-atelier [data-key="question-lead:{BOOK_ASSOCIATED}:{BLIND_SPOT}"]').count() == 0
    assert digest_tree(project) == before, "reading the question writes nothing"


def test_book_25_observation_is_adopted_through_review_and_applied_by_the_served_control(browser, seeded, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(seeded / "discovery", project)
    request = json.loads((EVIDENCE / "request-book25.json").read_text(encoding="utf-8"))
    answer = (EVIDENCE / "candidate-book25-unedited.json").read_text(encoding="utf-8")
    with served(browser, project) as (server, page, errors):
        open_question(page, CONVERSION)
        page.locator(f'#studio-atelier [data-key="question-lead:{BOOK}:{BLIND_SPOT}"]').click()
        page.wait_for_selector(f'#studio-atelier [data-key="observation-prepare:{BOOK}:{BLIND_SPOT}"]', timeout=30000)
        select = page.locator(f'#studio-atelier [data-key="observation-question:{BOOK}:{BLIND_SPOT}"]')
        select.select_option(CONVERSION)
        page.locator(f'#studio-atelier [data-key="observation-prepare:{BOOK}:{BLIND_SPOT}"]').click()
        page.wait_for_function(
            "() => /Prepared for your coding agent/.test(document.querySelector('#studio-atelier').textContent)", timeout=30000)
    # The owner prepared exactly the request the committed answer was written against, and nothing in Book 25 changed.
    pending = book_project(store_of(project), BOOK)
    assert pending["request"] is not None
    assert pending["request"]["request_sha256"] == request["request_sha256"]

    store = store_of(project)
    book_complete(store, BOOK, build_host_agent_response(HostAgentRequest(**request), answer,
                                                         runtime="fresh-sub-agent").model_dump())
    review = book_project(store, BOOK)["review"]
    assert review["applicable"], review["unexpected_changes"]
    assert [(row["element_id"], row["question_id"], row["established"]) for row in review["requested_question_associations"]] == [
        (BLIND_SPOT, CONVERSION, True)]

    with served(browser, project) as (server, page, errors):
        open_question(page, CONVERSION)
        page.locator(f'#studio-atelier [data-key="question-lead:{BOOK}:{BLIND_SPOT}"]').click()
        page.wait_for_function(
            """() => { const p = document.querySelector('#studio-atelier [aria-label="Developing Book 25"]');
                       return !!p && p.textContent.indexOf('Association you asked for') >= 0; }""", timeout=30000)
        developing = page.locator('#studio-atelier [aria-label="Developing Book 25"]').text_content()
        assert "Association you asked for · 1" in developing and "recorded in this revision" in developing
        page.locator(f'#studio-atelier [data-key="book-apply:{BOOK}"]').click()
        page.wait_for_function(
            """() => /Applied to working Book 25|applied/.test(document.querySelector('#studio-atelier').textContent)""",
            timeout=30000)

    recorded = json.loads(project_record(project, BOOK).read_text(encoding="utf-8"))
    applied = [row for row in recorded["artifact"]["series_consequences"] if row["id"] == BLIND_SPOT]
    # The owner recorded the binding (index, digest, version) beside the identity the author chose.
    assert applied and any(ref["kind"] == "series_question" and ref["id"] == CONVERSION and ref["series_question_index"] == 5
                           for ref in applied[0]["refs"])

    with served(browser, project) as (server, page, errors):
        open_question(page, CONVERSION)
        text = folio_text(page)
        assert "Book elements that engage it · 2" in text
        assert page.locator(f'#studio-atelier [data-element="{BLIND_SPOT}"][data-book="25"]').count() == 1
        assert page.locator(f'#studio-atelier [data-key="question-lead:{BOOK_ASSOCIATED}:{BLIND_SPOT}"]').count() == 0,             "the applied association leaves no lead behind"


def test_the_question_reading_fits_a_narrow_screen_without_horizontal_scroll(browser, seeded, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(seeded / "discovery", project)
    with served(browser, project, width=390, height=844) as (server, page, errors):
        open_question(page, CONVERSION)
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow <= 0, overflow


def test_declining_the_lead_changes_nothing(browser, seeded, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(seeded / "discovery", project)
    before = digest_tree(project)
    with served(browser, project) as (server, page, errors):
        open_question(page, CONVERSION)
        page.locator(f'#studio-atelier [data-key="question-lead:{BOOK}:{BLIND_SPOT}"]').click()
        page.wait_for_selector(f'#studio-atelier [data-key="observation-prepare:{BOOK}:{BLIND_SPOT}"]', timeout=30000)
        # The author looks, and leaves the lead as it is: no request is prepared and no record changes.
    assert digest_tree(project) == before
