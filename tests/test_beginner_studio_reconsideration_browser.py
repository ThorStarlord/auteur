"""The served reconsideration of one claim of an accepted consequence analysis.

The author opens "Reconsider this claim" beneath a claim, asks a question, prepares the request, pastes the coding agent's
answer, and reads the owner-validated reconsideration beneath the claim it concerns. A refused answer keeps the author's
unsent text. Nothing is applied, and the analysis and the narrative are unchanged. The replayed answers here test the controls'
mechanics; the authentic accepted reconsiderations are verified by the evidence captures, against exact request equivalence.
"""
import json
import sys
from pathlib import Path

from auteur.beginner.studio_architecture_consequence import project_architecture_consequence
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_architecture_consequence import INSTRUCTION, propose  # noqa: E402
from test_architecture_consequence_v3 import compact_under_retained_terms, mechanism_answer  # noqa: E402
from test_beginner_studio_consequence_browser import (  # noqa: E402,F401 - the fixtures and helpers of the served suite
    ask_and_answer, browser, copy_of, identified, narrative_snapshot, served_studio, store_for,
)

REACH_KEY = "reach:null"


def reconsideration_answer(packet, **overrides):
    base = {"schema_version": 1, "disposition": "qualified",
            "new_consideration": "The reach claim was read against the recovered coverage record.",
            "reconsidered_judgment": "The reach stands only as a candidate until the cited Book elements are read.",
            "evidence": [packet["evidence"][0]["id"]], "criticism_assessments": [], "remaining_uncertainty": [],
            "downstream": []}
    base.update(overrides)
    return base


def open_reach_slot(page):
    page.locator(f'details[data-key="reconsider:{REACH_KEY}"] > summary').click()
    page.wait_for_selector(f'textarea[data-key="reconsider-question:{REACH_KEY}"]', timeout=15000)


def test_a_reach_claim_offers_a_reconsideration_that_is_prepared_bound_to_the_analysis_and_stored_beside_it(
        browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, "Make the Mill Compact's labour duty apply in every season.", compact_under_retained_terms)
    before = narrative_snapshot(project)
    with served_studio(browser, project) as (_server, page, errors):
        packet = json.loads(ask_and_answer(page, store, answer=mechanism_answer)["user"])["consequence_packet"]
        analysis = project_architecture_consequence(store)
        analysis_sha, result_before = analysis["request_sha256"], analysis["result"]
        open_reach_slot(page)
        page.locator(f'textarea[data-key="reconsider-question:{REACH_KEY}"]').fill(
            "Is the reach claim supported by the recovered coverage record?")
        page.locator(f'button[data-key="reconsider-prepare:{REACH_KEY}"]').click()
        page.wait_for_selector("textarea.consequence-reconsider-request", timeout=15000)
        request = json.loads(page.locator("textarea.consequence-reconsider-request").input_value())
        assert request["settings"]["analysis_request_sha256"] == analysis_sha
        assert request["settings"]["operation"] == "reconsider_consequence"
        admitted = json.loads(request["user"])["allowed_evidence"][:1]
        response = build_host_agent_response(
            HostAgentRequest(**request), json.dumps(reconsideration_answer(packet, evidence=admitted)),
            runtime="consequence-test").model_dump()
        page.locator("textarea.consequence-reconsider-response").fill(json.dumps(response))
        page.locator(f'button[data-key="reconsider-submit:{REACH_KEY}"]').click()
        page.wait_for_selector('article.consequence-reconsideration[data-disposition="qualified"]', timeout=15000)
        card_text = page.locator("article.consequence-reconsideration").first.inner_text()
        assert "Qualified" in card_text
        assert "Judgment: The reach stands only as a candidate" in card_text
        assert "Advisory." in card_text
        assert not [error for error in errors if error.strip()]
    assert narrative_snapshot(project) == before, "a reconsideration changed narrative state"
    assert project_architecture_consequence(store)["result"] == result_before, "the analysis was rewritten"


def test_a_refused_reconsideration_keeps_the_author_text_and_says_why(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, "Make the Mill Compact's labour duty apply in every season.", compact_under_retained_terms)
    with served_studio(browser, project) as (_server, page, _errors):
        packet = json.loads(ask_and_answer(page, store, answer=mechanism_answer)["user"])["consequence_packet"]
        open_reach_slot(page)
        page.locator(f'textarea[data-key="reconsider-question:{REACH_KEY}"]').fill("Check the reach.")
        page.locator(f'button[data-key="reconsider-prepare:{REACH_KEY}"]').click()
        page.wait_for_selector("textarea.consequence-reconsider-request", timeout=15000)
        request = json.loads(page.locator("textarea.consequence-reconsider-request").input_value())
        admitted = json.loads(request["user"])["allowed_evidence"][:1]
        wrong = build_host_agent_response(HostAgentRequest(**request), json.dumps(reconsideration_answer(
            packet, disposition="corrected", evidence=admitted)), runtime="consequence-test").model_dump()
        pasted = json.dumps(wrong)
        page.locator("textarea.consequence-reconsider-response").fill(pasted)
        page.locator(f'button[data-key="reconsider-submit:{REACH_KEY}"]').click()
        page.wait_for_selector("#architecture-consequence .consequence-error", timeout=15000)
        assert "a correction must rest on recovered source" in page.locator(
            "#architecture-consequence .consequence-error").inner_text()
        # The author's unsent response survives the refusal, and the request is still shown to copy.
        assert page.locator("textarea.consequence-reconsider-response").input_value() == pasted
        assert page.locator("textarea.consequence-reconsider-request").count() == 1


def test_a_reconsideration_with_no_question_is_not_sent_and_the_author_text_is_kept(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, "Make the Mill Compact's labour duty apply in every season.", compact_under_retained_terms)
    with served_studio(browser, project) as (_server, page, _errors):
        ask_and_answer(page, store, answer=mechanism_answer)
        open_reach_slot(page)
        page.locator(f'textarea[data-key="reconsider-criticism:{REACH_KEY}"]').fill("A criticism the author wants weighed.")
        page.locator(f'button[data-key="reconsider-prepare:{REACH_KEY}"]').click()
        page.wait_for_selector("#architecture-consequence .consequence-error", timeout=15000)
        assert "Say what should be reconsidered first" in page.locator("#architecture-consequence .consequence-error").inner_text()
        assert page.locator(f'textarea[data-key="reconsider-criticism:{REACH_KEY}"]').input_value() == "A criticism the author wants weighed."


def test_the_reconsideration_control_fits_a_narrow_screen_without_horizontal_overflow(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, "Make the Mill Compact's labour duty apply in every season.", compact_under_retained_terms)
    with served_studio(browser, project, width=390, height=844) as (_server, page, errors):
        packet = json.loads(ask_and_answer(page, store, answer=mechanism_answer)["user"])["consequence_packet"]
        open_reach_slot(page)
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow == 0, overflow
        assert not [error for error in errors if error.strip()]
        assert packet["evidence"]
