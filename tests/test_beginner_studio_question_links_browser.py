"""The served Atelier shows Book elements' question associations, from both sides, and says what they establish.

The fixture applies, through the Working Book owner, the coding agent's unedited Book 24 answer recorded in Exercise A
(`docs/qualification-evidence/question-linked-narrative-inheritance-20261127/reproduce/exercise-a`): the blind-spot element
gains an association with the conversion question. A second copy leaves a further association pending, so the review
can be read before Apply. Nothing calls a provider.
"""
import contextlib
import json
import shutil
import sys
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response
from auteur.series.working_book_architecture import (
    book_apply_review,
    book_complete,
    book_prepare,
    book_project,
)

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402

CANVAS = discovery.SPRING
BOOK = 24
BLIND_SPOT = "cons-conversion-blind-spot"
CONVERSION = identity_for(5)
COMPACT = identity_for(6)
EXERCISE_A = (REPO / "docs/qualification-evidence/question-linked-narrative-inheritance-20261127/reproduce/exercise-a")
UNEDITED_CANDIDATE = EXERCISE_A / "candidate-book24-unedited.json"
TARGETS = (BLIND_SPOT, "inh-gate-independence", "later-cohort-seat")


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        yield instance
        instance.close()


@pytest.fixture(scope="module")
def applied(tmp_path_factory):
    """Book 24 with its blind-spot association applied: the owner's record of Exercise A's authentic answer."""
    root = tmp_path_factory.mktemp("question-links") / "discovery"
    store = discovery.seed_discovery(root)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    prepared = book_prepare(store, BOOK, instruction="Check which open questions this element engages.", targets=(BLIND_SPOT,))
    book_complete(store, BOOK, build_host_agent_response(HostAgentRequest(**prepared["request"]),
                                                         UNEDITED_CANDIDATE.read_text(encoding="utf-8"),
                                                         runtime="exercise-a-replay").model_dump())
    assert book_apply_review(store, BOOK, prepared["pending_request_sha256"])["result"] == "applied"
    return root


@pytest.fixture(scope="module")
def pending(applied, tmp_path_factory):
    """A copy of the applied study in which Book 24 has a second association waiting for review, not yet applied."""
    root = tmp_path_factory.mktemp("question-links-pending") / "discovery"
    shutil.copytree(applied, root)
    store = CanvasStore(root, CANVAS)
    prepared = book_prepare(store, BOOK, instruction="Check which open questions the Mill Compact agent engages.",
                            targets=("agent-mill-compact",))
    artifact = json.loads(json.dumps(json.loads((root / ".auteur/beginner/studio/canvases" / CANVAS /
                                                 "architecture/books/24/current.json").read_text(encoding="utf-8"))["artifact"]))
    agent = next(item for item in artifact["agents"] if item["id"] == "agent-mill-compact")
    if agent.get("provenance") is not None:
        agent.pop("provenance")
        agent["attribution"], agent["epistemic_status"] = "agent_proposed", "asserted"
    agent.setdefault("refs", []).append({"kind": "series_question", "id": COMPACT})
    book_complete(store, BOOK, build_host_agent_response(HostAgentRequest(**prepared["request"]), json.dumps(artifact),
                                                         runtime="owner-fixture").model_dump())
    assert book_project(store, BOOK)["status"] == "review_ready"
    return root


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


def open_conversion_question(page):
    page.locator('#studio-atelier [data-key="questions-all"]').click()
    item = page.locator(f'#studio-atelier .atl-question-item[data-key="question:{CONVERSION}"]')
    item.click()
    page.wait_for_selector("#studio-atelier .atl-folio", timeout=10000)


def folio_text(page) -> str:
    return page.locator("#studio-atelier .atl-folio").text_content()


def test_the_question_reading_names_the_book_element_that_engages_it_and_what_that_establishes(browser, applied, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(applied, project)
    with served(browser, project) as (server, page, errors):
        open_conversion_question(page)
        text = folio_text(page)
        assert "Book elements that engage it · 1" in text
        assert "Book 24" in text and "Series consequence" in text
        assert "The Book records:" in text
        assert "does not say the element answers, settles, develops or inherits from the question" in text
        # Book 24's engagement. A lead from Book 25 names the same element id, so the Book is named too.
        assert page.locator('#studio-atelier [data-element="cons-conversion-blind-spot"][data-book="24"]').count() == 1


def test_the_question_reading_fits_a_narrow_screen_without_horizontal_scroll(browser, applied, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(applied, project)
    with served(browser, project, width=390, height=844) as (server, page, errors):
        open_conversion_question(page)
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow <= 0, overflow


def test_a_pending_association_is_reviewed_and_is_not_an_engagement_until_applied(browser, pending, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(pending, project)
    # The question reading first: the proposed association is waiting for review, so it is not yet a Book engagement.
    with served(browser, project) as (server, page, errors):
        page.locator('#studio-atelier [data-key="questions-all"]').click()
        page.locator(f'#studio-atelier .atl-question-item[data-key="question:{COMPACT}"]').click()
        page.wait_for_selector("#studio-atelier .atl-folio", timeout=10000)
        assert "Book elements that engage it" not in folio_text(page)
    # The applied conversion question: its engagement card is the route to Book 24's own development panel.
    with served(browser, project) as (server, page, errors):
        page.locator('#studio-atelier [data-key="questions-all"]').click()
        page.locator(f'#studio-atelier .atl-question-item[data-key="question:{CONVERSION}"]').click()
        page.wait_for_selector("#studio-atelier .atl-folio", timeout=10000)
        page.locator('#studio-atelier [data-key="question-engagement:24:cons-conversion-blind-spot"]').click()
        # The review arrives with the Book's own read, which the page makes after the click.
        page.wait_for_function(
            """() => { const p = document.querySelector('#studio-atelier [aria-label="Developing Book 24"]');
                       return !!p && p.textContent.indexOf('Question associations in this revision') >= 0; }""",
            timeout=30000)
        developing = page.locator('#studio-atelier [aria-label="Developing Book 24"]').text_content()
        assert "Question associations in this revision · 1" in developing
        assert "now engages" in developing
        assert "does not say the element answers, settles, develops or inherits" in developing
