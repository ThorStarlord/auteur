"""The served Atelier's narrative deliberation: an author compares two continuing questions, investigates them together,
reads the recorded history the coding agent was given, chooses an alternative, reviews a revision that changes only one of
the two questions, applies it explicitly, and returns to the comparison with the updated history.

The coding agent's answers are replayed fixtures built from the prepared requests. Nothing calls a provider, and a replayed
answer is an interaction fixture, not new creative reasoning.
"""
import copy
import json
import os
import shutil
import sys
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.studio_architecture import _candidate, project_architecture
from auteur.beginner.studio_architecture_inquiry import project_architecture_inquiry
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_beginner_studio_question_workspace_browser import (  # noqa: E402
    book_records, browser, copy_of, folio_text, identified, served, store_for,
)
from test_persistent_narrative_questions import identity_for  # noqa: E402

GATE = 14
GATE_ID = identity_for(GATE)
OTHER = 0
OTHER_ID = identity_for(OTHER)
OUTSIDE = 2  # a question the comparison does not concern
REWORDED = " Revised: whether the Council may pass through it."
REVISION_INSTRUCTION = "Let the Gate Table decide the tally, so the question about hours is the question about who may pass."
COMPARISON = {
    "schema_version": 1,
    "analysis": ("The two questions turn on the same Council tally. One asks whether the Gate Table is accepted; "
                 "the other asks what the ledger counts. The record does not say they are one question."),
    "recorded_observations": [
        {"kind": "question", "id": GATE_ID, "claim": "The working Architecture records this question as open."},
        {"kind": "question", "id": OTHER_ID, "claim": "The working Architecture records this question as open."},
    ],
    "hypotheses": [
        {"title": "The tally as the shared mechanism", "divergence_axis": "causal_engine",
         "description": "The Council tally decides both who may pass and what the ledger records, so one decision would develop both."},
        {"title": "Two independent questions", "divergence_axis": "structure",
         "description": "Each question keeps its own mechanism; connecting them would concentrate the theme without a shared cause."},
    ],
    "uncertainties": ["Whether any Book relies on the tally being the same thing as the hours column."],
}


def capture(page, name: str) -> None:
    """Save a served screenshot when AUTEUR_DELIBERATION_EVIDENCE names a folder; the test does not require it."""
    folder = os.environ.get("AUTEUR_DELIBERATION_EVIDENCE")
    if folder:
        Path(folder).mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(Path(folder) / name), full_page=False)


def replay(request: dict, payload) -> str:
    response = build_host_agent_response(HostAgentRequest(**request), json.dumps(payload), runtime="replay")
    return json.dumps(response.model_dump(), default=str)


def open_question_from_list(page, identifier: str):
    """From the list of all questions (opened first if the page is elsewhere), the question is read in the folio."""
    item = page.locator(f'#studio-atelier .atl-question-item[data-key="question:{identifier}"]')
    if item.count() == 0:
        page.locator('#studio-atelier [data-key="questions-all"]').click()
        item = page.locator(f'#studio-atelier .atl-question-item[data-key="question:{identifier}"]')
    item.click()
    page.wait_for_selector("#studio-atelier .atl-qhistory", timeout=10000)


def comparison_text(page) -> str:
    return page.locator("#studio-atelier .atl-qcompare").text_content()


def test_two_questions_are_compared_investigated_revised_and_applied_with_their_history(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    before_books = book_records(project)
    before_gate = _candidate(store)["candidate"]["open_questions"][GATE]
    before_other = _candidate(store)["candidate"]["open_questions"][OTHER]
    with served(browser, project) as (server, page, errors):
        # 1. Select: the Gate Table question, then the other question, from the list of all questions.
        open_question_from_list(page, GATE_ID)
        page.locator(f'#studio-atelier [data-key="question-compare:{GATE_ID}"]').click()
        assert "Comparing · 1 of 3" in comparison_text(page)
        page.locator('#studio-atelier [data-key="question-back"]').first.click()
        open_question_from_list(page, OTHER_ID)
        page.locator(f'#studio-atelier [data-key="question-compare:{OTHER_ID}"]').click()
        assert "Comparing · 2 of 3" in comparison_text(page)
        capture(page, "1-compare-two-questions.png")
        # Selecting changed nothing.
        assert _candidate(store)["candidate"]["open_questions"][GATE] == before_gate
        assert book_records(project) == before_books

        # 2. Investigate together: the desk opens on both questions, with a suggestion in an empty field only.
        page.locator('#studio-atelier [data-key="compare-ask:connect_to_ask"]').click()
        page.wait_for_selector("#studio-atelier .atl-desk:not([hidden])", timeout=10000)
        assert "Your comparison of 2 open questions" in page.locator("#studio-atelier .atl-desk-title").inner_text()
        assert page.locator("#architecture-creative-agent-panel .creative-anchor-chip").count() == 2
        suggestion = page.locator('#architecture-creative-agent-panel textarea[aria-label="Your creative intention"]').input_value()
        assert suggestion.startswith("How might these two unresolved questions")
        page.locator("#architecture-creative-agent-panel [data-creative-submit]").click()
        page.wait_for_function(
            "document.querySelector('#architecture-creative-agent-panel [role=status]').textContent.includes('prepared')",
            timeout=15000)
        request = project_architecture_inquiry(store)["request"]
        user = json.loads(request["user"])
        assert user["graph_intent"]["operation"] == "connect_to_ask"
        assert [a["id"] for a in user["graph_intent"]["anchors"]] == [GATE_ID, OTHER_ID]
        assert user["deliberation"]["questions"] and len(user["deliberation"]["questions"]) == 2

        # 3. The coding agent answers (replayed); the author pastes the answer and validates it.
        page.locator('#architecture-creative-agent-panel [aria-label="Host-agent inquiry response"]').fill(
            replay(request, COMPARISON))
        page.locator("#architecture-creative-agent-panel button", has_text="Validate inquiry response").click()
        page.wait_for_selector('#architecture-creative-agent-panel button[data-alternative-id="h2"]', timeout=15000)
        panel = page.locator("#architecture-creative-agent-panel")
        # The evidence the answer was given is one disclosure away, grouped by what kind of evidence each line is.
        evidence = panel.locator('details[data-deliberation="true"]').text_content()
        assert "Current wording" in evidence
        assert "Recorded change · introduced" in evidence
        assert "The author’s request then · “Give each open question a stable identity.”" in evidence
        assert ("names this question itself" in evidence) or ("the Book owner matched it" in evidence)
        assert "Working Book decision (a noncanonical proposal)" in evidence
        assert "Agent interpretation — noncanonical" in panel.text_content()
        disclosure = panel.locator('details[data-deliberation="true"]')
        disclosure.evaluate("d => { d.open = true; }")
        disclosure.scroll_into_view_if_needed()
        capture(page, "2-answer-and-evidence.png")
        # Asking changed nothing.
        assert _candidate(store)["candidate"]["open_questions"][GATE] == before_gate
        assert book_records(project) == before_books

        # 4. The author chooses the second alternative, in words of their own.
        panel.locator('textarea[aria-label="Your creative intention"]').fill(REVISION_INSTRUCTION)
        panel.locator('button[data-alternative-id="h2"]').click()
        page.wait_for_function(
            "document.getElementById('architecture-handoff') && !document.getElementById('architecture-handoff').hidden",
            timeout=15000)
        waiting = project_architecture(store)["request"]
        assert waiting is not None
        revised = copy.deepcopy(_candidate(store)["candidate"])
        revised["open_questions"][GATE] = revised["open_questions"][GATE] + REWORDED
        # The revision also rewords a question the comparison did not concern: the review must say so.
        revised["open_questions"][OUTSIDE] = revised["open_questions"][OUTSIDE] + " Revised in passing."
        page.evaluate("() => { document.getElementById('architecture-handoff').open = true; }")
        page.locator("#architecture-response").fill(replay(waiting, revised))
        page.locator("#architecture-complete").click()
        page.wait_for_selector("#architecture-review:not([hidden])", timeout=15000)

        # 5. Review before Apply: the change to one question is named, and the scope says the other was not changed.
        review = page.locator("#architecture-review").inner_text()
        assert "Open question reworded, identity kept" in review
        assert "This inquiry concerned two open questions. This revision changes one of them; the others are unchanged." in review
        assert "This revision also changes one open question the inquiry did not concern." in review
        assert _candidate(store)["candidate"]["open_questions"][GATE] == before_gate

        capture(page, "3-review-scope.png")
        # 6. Explicit Apply. The other question is untouched.
        page.locator("#architecture-apply").click()
        page.wait_for_function("document.getElementById('architecture-review').hidden", timeout=15000)
        assert _candidate(store)["candidate"]["open_questions"][GATE].endswith(REWORDED)
        assert _candidate(store)["candidate"]["open_questions"][OTHER] == before_other
        assert _candidate(store)["candidate"]["open_questions"][OUTSIDE].endswith("Revised in passing.")
        assert book_records(project) == before_books

        # 7. Return: the author is back at the question the comparison began from, and the comparison is still there.
        if page.locator("#studio-atelier .atl-desk-back").first.is_visible():
            page.locator("#studio-atelier .atl-desk-back").first.click()
        page.wait_for_selector("#studio-atelier .atl-qcompare", timeout=15000)
        assert "Comparing · 2 of 3" in comparison_text(page)

        capture(page, "4-return-to-comparison.png")
        # 8. The updated history of the changed question names the revision and the alternative that produced it.
        page.locator('#studio-atelier [data-key="question-back"]').first.click()
        page.locator(f'#studio-atelier .atl-question-item[data-key="question:{GATE_ID}"]').click()
        page.wait_for_selector("#studio-atelier .atl-qhistory", timeout=10000)
        text = folio_text(page)
        assert "reworded, same position" in text
        assert f"Your revision request: “{REVISION_INSTRUCTION}”" in text
        assert "The alternative you chose in the coding-agent desk: “Two independent questions”" in text
        assert text.count("this may warrant reconsideration") == 2
        assert "Read Book 24" in text and "Read Book 25" in text
        assert errors == []

        # 9. Narrow screen: the comparison reads without horizontal scrolling.
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_timeout(300)
        page.locator('#studio-atelier [data-key="question-back"]').first.click()
        page.wait_for_selector("#studio-atelier .atl-qcompare", timeout=10000)
        overflow = page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 1, overflow
        capture(page, "5-comparison-narrow-390.png")
        page.set_viewport_size({"width": 1440, "height": 900})


def test_declining_the_comparison_changes_no_record(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    before_candidate = json.dumps(_candidate(store)["candidate"], sort_keys=True)
    before_books = book_records(project)
    with served(browser, project) as (server, page, errors):
        open_question_from_list(page, GATE_ID)
        page.locator(f'#studio-atelier [data-key="question-compare:{GATE_ID}"]').click()
        page.locator('#studio-atelier [data-key="question-back"]').first.click()
        open_question_from_list(page, OTHER_ID)
        page.locator(f'#studio-atelier [data-key="question-compare:{OTHER_ID}"]').click()
        page.locator('#studio-atelier [data-key="compare-ask:challenge"]').click()
        page.wait_for_selector("#studio-atelier .atl-desk:not([hidden])", timeout=10000)
        page.locator("#architecture-creative-agent-panel [data-creative-submit]").click()
        page.wait_for_function(
            "document.querySelector('#architecture-creative-agent-panel [role=status]').textContent.includes('prepared')",
            timeout=15000)
        request = project_architecture_inquiry(store)["request"]
        page.locator('#architecture-creative-agent-panel [aria-label="Host-agent inquiry response"]').fill(
            replay(request, COMPARISON))
        page.locator("#architecture-creative-agent-panel button", has_text="Validate inquiry response").click()
        page.wait_for_selector('#architecture-creative-agent-panel button[data-alternative-id="h2"]', timeout=15000)
        # The author reads the answer and chooses none of its alternatives.
    assert json.dumps(_candidate(store)["candidate"], sort_keys=True) == before_candidate
    assert book_records(project) == before_books
    assert project_architecture_inquiry(store)["result"] is not None
