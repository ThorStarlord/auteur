"""The served Atelier's opportunity discovery, end to end: the author invokes discovery without choosing questions, the
coding agent's answer (replayed from the prepared request) is validated, a possibility's evidence is inspected, the
possibility is investigated through the existing deliberation desk, a reviewed revision is applied, and the author returns
to the discovery with its investigation recorded. A second journey declines every possibility and changes no record; a
third shows an answer that finds nothing worth recording.

The coding agent's answers are replayed fixtures, built from the prepared requests. Nothing calls a provider.
"""
import copy
import json
import os
import sys
from pathlib import Path

from auteur.beginner.studio_architecture import _candidate, project_architecture
from auteur.beginner.studio_architecture_discovery import project_architecture_discoveries
from auteur.beginner.studio_architecture_inquiry import project_architecture_inquiry
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_beginner_studio_question_workspace_browser import (  # noqa: E402
    book_records, browser, copy_of, folio_text, identified, served, store_for,
)
from test_persistent_narrative_questions import identity_for  # noqa: E402

REFORM = identity_for(12)
PLURALITY = identity_for(13)
TITLE = "The ledger as the stance test"
NEXT = "Ask whether the hours the ledger records are the stewardship tally the Council keeps."
REVISION_INSTRUCTION = "Let the ledger's hours settle what the Council counts, so the stance question becomes a question about counting."
REWORDED = " Revised: the Council counts hours, not hands."

DISCOVERY = {
    "schema_version": 1,
    "coverage_note": "I read the working Architecture and every continuing question, and set aside the finale alternatives.",
    "possibilities": [{
        "title": TITLE,
        "kind": "shared_mechanism",
        "possibility": "If the ledger counts hours, the plurality question becomes a question about who may be counted, and the stance question about how the institution counts.",
        "significance": "It would tie two open decisions to one recorded mechanism instead of leaving them as separate problems.",
        "questions": [REFORM, PLURALITY],
        "evidence": [{"ref_kind": "node", "ref_id": "eng_ledger", "note": "The ledger now records hours worked."}],
        "basis": "grounded",
        "assumptions": ["The Council reads the ledger as its tally."],
        "counterevidence": ["A Book decision may need a separate count."],
        "gains": "One mechanism with two payoffs.",
        "costs": "The two questions stop being independent.",
        "next_investigation": NEXT,
    }],
    "no_possibility_reason": None,
    "uncertainties": ["Whether any Book relies on the tally being the hours column."],
}
NOTHING = {
    "schema_version": 1,
    "coverage_note": "I read every continuing question and the recorded mechanisms; none supports a stronger possibility.",
    "possibilities": [],
    "no_possibility_reason": "The recorded mechanisms do not yet connect these questions beyond the ledger, which is already a shared fact.",
    "uncertainties": [],
}
COMPARISON = {
    "schema_version": 1,
    "analysis": "The two questions turn on the same tally, but the record does not say they are one question.",
    "recorded_observations": [
        {"kind": "question", "id": REFORM, "claim": "The working Architecture records this question as open."},
        {"kind": "question", "id": PLURALITY, "claim": "The working Architecture records this question as open."},
    ],
    "hypotheses": [
        {"title": "The tally as the shared mechanism", "divergence_axis": "causal_engine",
         "description": "The Council tally decides both who may pass and what the ledger records."},
        {"title": "Two independent questions", "divergence_axis": "structure",
         "description": "Each question keeps its own mechanism; connecting them concentrates the theme."},
    ],
    "uncertainties": ["Whether any Book relies on the tally being the hours column."],
}
ALTERNATIVE = "Two independent questions"


def replay(request: dict, payload) -> str:
    response = build_host_agent_response(HostAgentRequest(**request), json.dumps(payload), runtime="replay")
    return json.dumps(response.model_dump(), default=str)


def capture(page, name: str) -> None:
    folder = os.environ.get("AUTEUR_DISCOVERY_EVIDENCE")
    if folder:
        Path(folder).mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(Path(folder) / name), full_page=False)


def prepare_and_answer(page, store, answer: dict, goal: str = "") -> dict:
    """Invoke discovery from the atlas, prepare the request, and paste the replayed answer. Returns the request."""
    page.locator('#studio-atelier [data-key="discover-open"]').click()
    page.wait_for_selector("#studio-atelier .atl-discover-request", timeout=10000)
    if goal:
        page.locator('#studio-atelier textarea[aria-label="Optional goal for the discovery"]').fill(goal)
    page.locator('#studio-atelier [data-key="discover-prepare"]').click()
    page.wait_for_selector('#studio-atelier textarea[aria-label="Prepared discovery request"]', timeout=15000)
    request = project_architecture_discoveries(store)["pending"]["request"]
    page.locator('#studio-atelier textarea[aria-label="Discovery response"]').fill(replay(request, answer))
    page.locator('#studio-atelier [data-key="discover-validate"]').click()
    return request


def test_discovery_is_invoked_without_choosing_questions_and_its_possibility_is_investigated_and_applied(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    before_books = book_records(project)
    before_reform = _candidate(store)["candidate"]["open_questions"][12]
    with served(browser, project) as (server, page, errors):
        # 1. Invoke discovery from the atlas. Nothing has run yet, and no question was chosen.
        prepare_and_answer(page, store, DISCOVERY, goal="Where could the tally and the stance support each other?")
        page.wait_for_selector('#studio-atelier [data-key="discover-investigate:p1"]', timeout=15000)
        text = folio_text(page)
        assert TITLE in text and "Ready to investigate" in text
        assert "Where could the tally and the stance support each other?" in text
        assert _candidate(store)["candidate"]["open_questions"][12] == before_reform
        capture(page, "1-discovery-results.png")

        # 2. Inspect the evidence and the uncertainty, each behind its own disclosure.
        page.locator("#studio-atelier details[data-key^=\"discover:\"][data-key$=\":evidence\"] summary").first.click()
        assert "Architecture element · eng_ledger · still in the Architecture" in folio_text(page)
        page.locator("#studio-atelier details[data-key^=\"discover:\"][data-key$=\":uncertainty\"] summary").first.click()
        assert "the agent’s proposal, not established fact" in folio_text(page)
        assert "Counterevidence: A Book decision may need a separate count." in folio_text(page)

        # 3. Investigate the possibility: its own questions go to the comparison and the desk, and no request is sent yet.
        page.locator('#studio-atelier [data-key="discover-investigate:p1"]').click()
        page.wait_for_selector("#studio-atelier .atl-desk:not([hidden])", timeout=10000)
        assert page.locator("#architecture-creative-agent-panel .creative-anchor-chip").count() == 2
        assert f"From a discovered possibility: “{TITLE}”" in page.locator("#architecture-creative-agent-panel").text_content()
        suggestion = page.locator('#architecture-creative-agent-panel textarea[aria-label="Your creative intention"]').input_value()
        assert suggestion == NEXT
        assert project_architecture_inquiry(store)["request"] is None

        # 4. The author sends the investigation, the coding agent answers (replayed), and the author chooses an alternative.
        page.locator("#architecture-creative-agent-panel [data-creative-submit]").click()
        page.wait_for_function(
            "document.querySelector('#architecture-creative-agent-panel [role=status]').textContent.includes('prepared')",
            timeout=15000)
        request = project_architecture_inquiry(store)["request"]
        user = json.loads(request["user"])
        assert user["from_discovery"]["possibility_id"] == "p1"
        assert user["graph_intent"]["operation"] == "compare"
        page.locator('#architecture-creative-agent-panel [aria-label="Host-agent inquiry response"]').fill(replay(request, COMPARISON))
        page.locator("#architecture-creative-agent-panel button", has_text="Validate inquiry response").click()
        page.wait_for_selector('#architecture-creative-agent-panel button[data-alternative-id="h2"]', timeout=15000)
        page.locator('#architecture-creative-agent-panel textarea[aria-label="Your creative intention"]').fill(REVISION_INSTRUCTION)
        page.locator('#architecture-creative-agent-panel button[data-alternative-id="h2"]').click()
        page.wait_for_function(
            "document.getElementById('architecture-handoff') && !document.getElementById('architecture-handoff').hidden",
            timeout=15000)

        # 5. A reviewed revision, prepared from the alternative and changing only the stance question.
        waiting = project_architecture(store)["request"]
        revised = copy.deepcopy(_candidate(store)["candidate"])
        revised["open_questions"][12] = revised["open_questions"][12] + REWORDED
        page.evaluate("() => { document.getElementById('architecture-handoff').open = true; }")
        page.locator("#architecture-response").fill(replay(waiting, revised))
        page.locator("#architecture-complete").click()
        page.wait_for_selector("#architecture-review:not([hidden])", timeout=15000)
        review = page.locator("#architecture-review").inner_text()
        assert f"Developed from a discovered possibility: “{TITLE}”" in review
        assert "This inquiry concerned two open questions. This revision changes one of them; the others are unchanged." in review
        assert _candidate(store)["candidate"]["open_questions"][12] == before_reform
        capture(page, "2-review-from-possibility.png")

        # 6. Explicit Apply. The Books are not rewritten.
        page.locator("#architecture-apply").click()
        page.wait_for_function("document.getElementById('architecture-review').hidden", timeout=15000)
        assert _candidate(store)["candidate"]["open_questions"][12].endswith(REWORDED)
        assert book_records(project) == before_books

        # 7. Return to the discovery: the possibility records its investigation and the applied revision.
        if page.locator("#studio-atelier .atl-desk-back").first.is_visible():
            page.locator("#studio-atelier .atl-desk-back").first.click()
        page.wait_for_selector('#studio-atelier [data-key="discover-reread"]', timeout=15000)
        page.locator('#studio-atelier [data-key="discover-reread"]').click()
        page.wait_for_function(
            "document.querySelector('#studio-atelier .atl-folio').textContent.includes('a revision made from it has been applied')",
            timeout=15000)
        capture(page, "3-return-to-discovery.png")
        overflow = page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 1, overflow
        assert errors == []


def test_declining_every_possibility_and_leaving_the_rest_changes_no_record(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    before_candidate = json.dumps(_candidate(store)["candidate"], sort_keys=True)
    before_books = book_records(project)
    with served(browser, project) as (server, page, errors):
        prepare_and_answer(page, store, DISCOVERY)
        page.wait_for_selector('#studio-atelier [data-key="discover-decision:p1"]', timeout=15000)
        page.locator('#studio-atelier [data-key="discover-decision:p1"]').click()
        # The decision button keeps its key when it becomes Reopen, so wait for the words the decline produces.
        page.wait_for_function(
            "document.querySelector('#studio-atelier .atl-folio').textContent.includes('Declined. Nothing in the Architecture')",
            timeout=10000)
        assert "Declined. Nothing in the Architecture or a Book was changed." in folio_text(page)
        capture(page, "4-declined.png")

        # Narrow screen: the discovery reads without horizontal scrolling.
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(300)
        overflow = page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 1, overflow
        capture(page, "5-discovery-narrow-390.png")
        page.set_viewport_size({"width": 1440, "height": 900})
        assert errors == []
    assert json.dumps(_candidate(store)["candidate"], sort_keys=True) == before_candidate
    assert book_records(project) == before_books
    decision = project_architecture_discoveries(store)["discoveries"][0]["possibilities"][0]["decision"]
    assert decision["decision"] == "declined"


def test_an_answer_that_finds_nothing_worth_recording_says_why_and_changes_nothing(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    before_candidate = json.dumps(_candidate(store)["candidate"], sort_keys=True)
    before_books = book_records(project)
    with served(browser, project) as (server, page, errors):
        prepare_and_answer(page, store, NOTHING)
        page.wait_for_selector("#studio-atelier .atl-discover-run", timeout=15000)
        assert NOTHING["no_possibility_reason"] in folio_text(page)
        assert page.locator('#studio-atelier [data-key^="discover-investigate:"]').count() == 0
        capture(page, "6-no-worthwhile-possibility.png")
        assert errors == []
    assert json.dumps(_candidate(store)["candidate"], sort_keys=True) == before_candidate
    assert book_records(project) == before_books
