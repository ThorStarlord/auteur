"""The served Atelier's Narrative Question Workspace: an author discovers a continuing question, reads how it has been
recorded, sees the Working Books that refer to it, investigates it through the coding-agent desk, reviews a reworded
question, applies it explicitly, and returns to the question with its updated history.

The coding agent's answers are replayed fixtures: each is built from the request the page prepared, and then pasted into
the desk as the host agent's response. Nothing calls a provider. Each replayed answer is an answer, not new reasoning.
"""
import contextlib
import copy
import json
import shutil
import sys
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import _candidate, complete_architecture, prepare_architecture, project_architecture
from auteur.beginner.studio_architecture_inquiry import complete_architecture_inquiry, project_architecture_inquiry
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities, identity_for  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

CANVAS = discovery.SPRING
GATE = 14
GATE_ID = identity_for(GATE)
REWORDED = " Revised: whether the Council may pass through it."
ALTERNATIVE_TITLE = "A mechanism question"
REVISION_INSTRUCTION = "Reword the Gate Table question as the mechanism alternative reads."
INQUIRY_RESULT = {
    "schema_version": 1,
    "analysis": "The question asks whether the Gate Table is accepted, or how it decides who may pass.",
    "recorded_observations": [{"kind": "question", "id": GATE_ID,
                               "claim": "The Architecture records this question as open."}],
    "hypotheses": [
        {"title": "A standing question", "divergence_axis": "social_scale",
         "description": "The Gate Table stays open for the Council; the question is about standing."},
        {"title": ALTERNATIVE_TITLE, "divergence_axis": "causal_engine",
         "description": "The Gate Table is a mechanism whose acceptance decides which hands may pass."},
    ],
    "uncertainties": ["Whether any Book depends on the Gate Table being accepted."],
}


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        yield instance
        instance.close()


@pytest.fixture(scope="module")
def identified(tmp_path_factory):
    """Identities established, and Books 24 and 25 recorded against them. Each test works on its own copy."""
    root = tmp_path_factory.mktemp("question-workspace") / "discovery"
    store = discovery.seed_discovery(root)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, root, 24)
    reconcile(store, root, 25)
    return root


def copy_of(identified: Path, tmp_path: Path) -> Path:
    target = tmp_path / "discovery"
    shutil.copytree(identified, target)
    return target


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


def open_gate_question(page):
    """From the atlas or the list of all questions: the Gate Table question is read in the folio."""
    item = page.locator(f'#studio-atelier .atl-question-item[data-key="question:{GATE_ID}"]')
    if item.count() == 0:
        page.locator('#studio-atelier [data-key="questions-all"]').click()
        item = page.locator(f'#studio-atelier .atl-question-item[data-key="question:{GATE_ID}"]')
    item.click()
    page.wait_for_selector("#studio-atelier .atl-qhistory", timeout=10000)


def folio_text(page) -> str:
    # The DOM text, not the rendered text: the stylesheet sets section labels in capitals, which the words are not.
    return page.locator("#studio-atelier .atl-folio").text_content()


def store_for(project: Path) -> CanvasStore:
    return CanvasStore(project, CANVAS)


def book_records(project: Path) -> dict:
    root = project / ".auteur/beginner/studio/canvases" / CANVAS / "architecture/books"
    return {n: (root / str(n) / "current.json").read_bytes() for n in (24, 25)}


def replay(request: dict, payload) -> str:
    """The coding agent's answer to a prepared request, as the desk expects it pasted."""
    response = build_host_agent_response(HostAgentRequest(**request), json.dumps(payload), runtime="replay")
    return json.dumps(response.model_dump(), default=str)


def test_the_question_is_discovered_read_and_related_to_its_books(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    impact.revise_architecture(store_for(project), "Reword the Gate Table question.", _reword)
    with served(browser, project) as (server, page, errors):
        # Discovery: the Architecture's own question list, with no Book decision located first.
        page.locator('#studio-atelier [data-key="questions-all"]').click()
        assert page.locator("#studio-atelier .atl-question-item").count() >= 10
        assert "Continuing · identity recorded · 16" in folio_text(page)
        open_gate_question(page)

        # Current formulation and its standing, said in full.
        assert "Revised: whether the Council may pass through it." in page.locator(
            "#studio-atelier .atl-folio-title").inner_text()
        text = folio_text(page)
        assert "Continuing question. Its identity was first recorded in revision 3" in text
        # Earlier formulations and the reason each revision records, with the earlier wording visible.
        assert "Your revision request: “Give each open question a stable identity.”" in text
        assert "Your revision request: “Reword the Gate Table question.”" in text
        assert "Was · " in text and "Now · " in text
        assert "Wording only · revisions 1–2 · no identity recorded" in text

        # Working Books that record a decision about it, by identity; reconsideration without a verdict on the Book.
        assert "Working Books that record a decision about it · 2" in text
        assert text.count("this may warrant reconsideration") == 2
        assert text.count("The Book is not declared inconsistent.") == 2
        assert "Read Book 24" in text and "Read Book 25" in text

        # Investigation is offered after the history, and nothing has been asked yet.
        assert text.index("How it has changed") < text.index("Working Books that record") < text.index(
            "Investigate with your coding agent")

        # Cross-Book navigation returns to the question, not to the atlas.
        page.locator('#studio-atelier [data-key="question-book:24:dec-gate-table"]').click()
        page.wait_for_selector('#studio-atelier [data-key="series-back"]', timeout=10000)
        assert page.locator('#studio-atelier [data-key="series-back"]').inner_text() == "← Back to the open question"
        page.locator('#studio-atelier [data-key="series-back"]').click()
        page.wait_for_selector("#studio-atelier .atl-qhistory", timeout=10000)
        assert "Continuing question." in folio_text(page)

        # Source details are one disclosure away, with the recorded identity and version.
        page.locator('#studio-atelier details[data-key="question-source:' + GATE_ID + '"] summary').click()
        assert GATE_ID in folio_text(page)

        # Back returns to the list the question was opened from, which is where the author was.
        page.locator('#studio-atelier [data-key="question-back"]').first.click()
        assert "The questions this Architecture records" in folio_text(page)

        # A narrow screen reads the same reading without horizontal scrolling.
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(300)
        open_gate_question(page)
        overflow = page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 1, overflow
        page.screenshot(path=str(tmp_path / "question-reading-narrow.png"), full_page=False)
        page.set_viewport_size({"width": 1440, "height": 900})


def test_the_author_investigates_a_question_and_applies_a_reviewed_rewording(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    before_books = book_records(project)
    before_question = _candidate(store)["candidate"]["open_questions"][GATE]
    with served(browser, project) as (server, page, errors):
        open_gate_question(page)

        # 1. Investigate: the desk opens on the question; the author sends the request to the coding agent.
        page.locator('#studio-atelier [data-key="question-ask:explore"]').click()
        page.wait_for_selector("#studio-atelier .atl-desk:not([hidden])", timeout=10000)
        assert "Are the Hollow Gate and the Gate Table" in page.locator("#studio-atelier .atl-desk-title").inner_text()
        page.locator("#architecture-creative-agent-panel [data-creative-submit]").click()
        page.wait_for_function(
            "document.querySelector('#architecture-creative-agent-panel [role=status]').textContent.includes('prepared')",
            timeout=15000)
        request = project_architecture_inquiry(store)["request"]
        assert request is not None

        # 2. The coding agent answers the prepared request (replayed); the author pastes the answer and validates it.
        answer = replay(request, INQUIRY_RESULT)
        page.locator('#architecture-creative-agent-panel [aria-label="Host-agent inquiry response"]').fill(answer)
        page.locator("#architecture-creative-agent-panel button", has_text="Validate inquiry response").click()
        page.wait_for_selector('#architecture-creative-agent-panel button[data-alternative-id="h2"]', timeout=15000)
        # Asking changed nothing: the Architecture and both Books are as they were.
        assert _candidate(store)["candidate"]["open_questions"][GATE] == before_question
        assert book_records(project) == before_books

        # 3. The author chooses the second alternative as the basis for a revision, in words of their own.
        page.locator('#architecture-creative-agent-panel textarea[aria-label="Your creative intention"]').fill(REVISION_INSTRUCTION)
        page.locator('#architecture-creative-agent-panel button[data-alternative-id="h2"]').click()
        page.wait_for_function("document.querySelector('#architecture-handoff') && !document.querySelector('#architecture-handoff').hidden",
                               timeout=15000)
        waiting = project_architecture(store)["request"]
        assert waiting is not None
        revised = copy.deepcopy(_candidate(store)["candidate"])
        revised["open_questions"][GATE] = revised["open_questions"][GATE] + REWORDED
        page.evaluate("() => { const d = document.getElementById('architecture-handoff'); d.open = true; }")
        page.locator("#architecture-response").fill(replay(waiting, revised))
        page.locator("#architecture-complete").click()
        page.wait_for_selector("#architecture-review:not([hidden])", timeout=15000)

        # 4. Before Apply: the review names the question change, and the Architecture is still the same.
        review = page.locator("#architecture-review").inner_text()
        assert "Open question reworded, identity kept" in review
        assert _candidate(store)["candidate"]["open_questions"][GATE] == before_question

        # 5. Explicit Apply.
        page.locator("#architecture-apply").click()
        page.wait_for_function("document.getElementById('architecture-review').hidden", timeout=15000)
        assert _candidate(store)["candidate"]["open_questions"][GATE].endswith(REWORDED)
        assert _candidate(store)["candidate"]["open_question_ids"][GATE] == GATE_ID
        assert book_records(project) == before_books  # Books are not rewritten by an Architecture Apply.

        # 6. Back to the question: once the revision is applied the desk closes, and the question is read again with its
        # updated history. If the desk is still open, its own way back is used.
        if page.locator("#studio-atelier .atl-desk-back").first.is_visible():
            page.locator("#studio-atelier .atl-desk-back").first.click()
        page.wait_for_selector("#studio-atelier .atl-qhistory", timeout=15000)
        text = folio_text(page)
        assert "reworded, same position" in text
        assert f"Your revision request: “{REVISION_INSTRUCTION}”" in text
        assert f"The alternative you chose in the coding-agent desk: “{ALTERNATIVE_TITLE}”" in text
        # Both Books now refer to the earlier wording, and the question keeps its identity.
        assert text.count("this may warrant reconsideration") == 2
        assert "Read Book 24" in text and "Read Book 25" in text


def test_declining_every_alternative_changes_nothing(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    before_candidate = json.dumps(_candidate(store)["candidate"], sort_keys=True)
    before_books = book_records(project)
    with served(browser, project) as (server, page, errors):
        open_gate_question(page)
        page.locator('#studio-atelier [data-key="question-ask:challenge"]').click()
        page.wait_for_selector("#studio-atelier .atl-desk:not([hidden])", timeout=10000)
        page.locator("#architecture-creative-agent-panel [data-creative-submit]").click()
        page.wait_for_function(
            "document.querySelector('#architecture-creative-agent-panel [role=status]').textContent.includes('prepared')",
            timeout=15000)
        request = project_architecture_inquiry(store)["request"]
        page.locator('#architecture-creative-agent-panel [aria-label="Host-agent inquiry response"]').fill(
            replay(request, {**INQUIRY_RESULT, "hypotheses": [{"title": "One reading", "description": "A single reading, "
                                                                 "not a set of alternatives.",
                                                                 "divergence_axis": None}]}))
        page.locator("#architecture-creative-agent-panel button", has_text="Validate inquiry response").click()
        page.wait_for_function(
            "document.querySelector('#architecture-creative-agent-panel').textContent.includes('leaves the Architecture as it is')",
            timeout=15000)
        # The author declines: no alternative is chosen, the desk is left, and the question is read as it was.
        page.locator("#studio-atelier .atl-desk-back").first.click()
        page.wait_for_selector("#studio-atelier .atl-qhistory", timeout=10000)
        text = folio_text(page)
        assert "Continuing question. Its identity was first recorded in revision 3" in text
        assert "reworded, same position" not in text
        assert project_architecture(store)["review"] is None
        assert json.dumps(_candidate(store)["candidate"], sort_keys=True) == before_candidate
        assert book_records(project) == before_books
        assert not errors


def test_the_question_projection_is_served_read_only(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    before = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}
    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    try:
        url = f"http://127.0.0.1:{server.port}/api/beginner/studio/canvases/{CANVAS}/architecture-questions"
        with urllib.request.urlopen(url, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    finally:
        server.stop()
        thread.join(timeout=5)
    assert body["schema"] == "studio-architecture-questions/1" and body["authority"] == "read_only_owner_records"
    gate = next(q for q in body["questions"] if q["id"] == GATE_ID)
    assert gate["standing"] == "continuing" and gate["history"]["introduced_in_recorded_history"] is True
    after = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob("*") if p.is_file()}
    assert after == before


@pytest.fixture(scope="module")
def legacy(tmp_path_factory):
    """The Spring Ledger study before any question has an identity: wording only."""
    root = tmp_path_factory.mktemp("question-legacy") / "discovery"
    discovery.seed_discovery(root)
    return root


def test_questions_without_identity_stay_visible_and_are_not_asked_about_as_continuing(browser, legacy, tmp_path):
    project = copy_of(legacy, tmp_path)
    with served(browser, project) as (server, page, errors):
        page.locator('#studio-atelier [data-key="questions-all"]').click()
        assert page.locator("#studio-atelier .atl-question-item", has_text="Wording only").count() >= 10
        assert page.locator("#studio-atelier .atl-question-item", has_text="Continuing").count() == 0
        page.locator(f'#studio-atelier .atl-question-item[data-key="question:index:{GATE}"]').click()
        page.wait_for_selector("#studio-atelier .atl-qhistory", timeout=10000)
        text = folio_text(page)
        assert "Wording only. This question has no recorded identity yet" in text
        assert "It needs a recorded identity before it can be asked about" in text
        assert page.locator('#studio-atelier [data-key^="question-ask:"]').count() == 0
        assert not errors


def test_a_removed_question_is_no_longer_open_and_removing_it_is_not_an_answer(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)

    def remove_gate(candidate):
        index = candidate["open_question_ids"].index(GATE_ID)
        del candidate["open_questions"][index]
        del candidate["open_question_ids"][index]

    impact.revise_architecture(store_for(project), "Remove the Gate Table question.", remove_gate)
    with served(browser, project) as (server, page, errors):
        page.locator('#studio-atelier [data-key="questions-all"]').click()
        assert "No longer open · 1" in folio_text(page)
        page.locator(f'#studio-atelier .atl-question-item[data-key="question:{GATE_ID}"]').click()
        page.wait_for_selector("#studio-atelier .atl-qhistory", timeout=10000)
        text = folio_text(page)
        assert "No longer open in the working Architecture" in text
        assert "Removing it is not an answer" in text
        assert "Not in the working Architecture" in text
        assert "A question no longer open cannot be asked about" in text
        assert text.count("The question is no longer open in the Architecture. Removing it is not an answer") == 2
        assert page.locator('#studio-atelier [data-key^="question-ask:"]').count() == 0
        assert not errors


def _reword(candidate):
    index = candidate["open_question_ids"].index(GATE_ID)
    candidate["open_questions"][index] += REWORDED


def test_a_failed_reading_of_the_questions_is_not_retried_by_the_render_it_causes(browser, identified, tmp_path):
    """A question read that fails is shown as failed and asked again only by "Try again", never by the render it causes."""
    project = copy_of(identified, tmp_path)
    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    requests = []
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def fail(route):
        requests.append(route.request.url)
        route.fulfill(status=500, content_type="application/json", body='{"error": "unavailable"}')

    try:
        page.route("**/architecture-questions", fail)
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas={CANVAS}&atelier", wait_until="networkidle")
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        page.wait_for_selector("#studio-atelier .atl-questions", state="attached", timeout=20000)
        page.wait_for_timeout(1500)
        assert "Could not read the open questions" in folio_text(page)
        settled = len(requests)
        page.wait_for_timeout(1500)
        assert len(requests) == settled, (settled, len(requests))
        assert settled <= 3, settled
        # "Try again" asks once more, and the failed answer again shows the failure without another request.
        page.locator('#studio-atelier [data-key="questions-retry"]').click()
        page.wait_for_timeout(1500)
        assert len(requests) == settled + 1, (settled, len(requests))
        assert "Could not read the open questions" in folio_text(page)
        assert not errors, errors
    finally:
        page.close()
        server.stop()
        thread.join(timeout=5)
