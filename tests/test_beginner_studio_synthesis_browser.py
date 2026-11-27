"""The served long-horizon synthesis, on the Spring Ledger study.

The author chooses developments from the Architecture on screen, asks in ordinary language, and the page prepares a request bound
to exactly those developments. A pasted response for that exact request is stored and read as a trajectory; a refused one keeps the
author's text. A follow-up keeps the developments and gives the earlier judgement to the agent as text only. Nothing is applied, and
the narrative records do not change. The replayed answers here test the controls' mechanics; the authentic syntheses are verified by
the evidence captures, against exact request equivalence.
"""
import json
import sys
from pathlib import Path

from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
from test_architecture_consequence import snapshot  # noqa: E402
from test_architecture_synthesis import COMPACT_QUESTION, valid_answer  # noqa: E402
from test_beginner_studio_consequence_browser import (  # noqa: E402,F401 - the fixtures and helpers of the served suite
    browser, copy_of, identified, served_studio, store_for,
)

QUESTION = "How might the compact's settlement develop across the next Books without becoming repetitive?"


def records_without_judgements(project: Path) -> dict[str, bytes]:
    """The narrative and Architecture records. A synthesis writes request records of its own, which are not canon."""
    return {path: data for path, data in snapshot(project).items() if "synthesis" not in Path(path).parts}


def replay(request: dict, payload) -> str:
    response = build_host_agent_response(HostAgentRequest(**request), json.dumps(payload), runtime="synthesis-served-replay")
    return json.dumps(response.model_dump())


def open_panel(page):
    page.wait_for_selector("#architecture-synthesis:not([hidden])", timeout=20000)
    page.wait_for_selector('input[data-development^="question:"]', timeout=20000)


def prepare(page, question=QUESTION):
    page.locator('textarea[data-synthesis="question"]').fill(question)
    page.locator('button[data-synthesis="prepare"]').click()
    page.wait_for_selector("textarea.synthesis-request", timeout=20000)
    return json.loads(page.locator("textarea.synthesis-request").input_value())


def test_the_synthesis_is_offered_for_the_working_architecture_and_prepares_a_request_bound_to_its_developments(
        browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    before = records_without_judgements(project)
    with served_studio(browser, project) as (_server, page, _errors):
        open_panel(page)
        page.locator(f'input[data-development="question:{COMPACT_QUESTION}"]').check()
        request = prepare(page)
        assert request["settings"]["operation"] == "synthesize_architecture_development"
        user = json.loads(request["user"])
        assert [row["ref"] for row in user["developments"]] == [COMPACT_QUESTION]
        assert user["question"] == QUESTION
        assert "Awaiting your coding agent" in page.locator("#architecture-synthesis-root").inner_text()
    assert records_without_judgements(project) == before, "preparing a synthesis changed no record"


def test_a_pasted_response_for_the_exact_request_is_stored_and_read_as_a_trajectory(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    with served_studio(browser, project) as (_server, page, _errors):
        open_panel(page)
        page.locator(f'input[data-development="question:{COMPACT_QUESTION}"]').check()
        request = prepare(page)
        page.locator("textarea.synthesis-response").fill(replay(request, valid_answer(json.loads(request["user"]))))
        page.locator('button[data-synthesis="submit"]').click()
        page.wait_for_selector(".synthesis-stage", timeout=20000)
        assert page.locator(".synthesis-stage").count() == 2
        text = page.locator("#architecture-synthesis-root").inner_text()
        assert "Book 24" in text and "Beyond the existing Books" in text
        assert "Current:" in text, "the standing is stated in words"
        assert "Nothing is applied" in page.locator("#architecture-synthesis-status").inner_text()


def test_a_refused_response_keeps_the_authors_pasted_text_and_says_why(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    with served_studio(browser, project) as (_server, page, _errors):
        open_panel(page)
        page.locator(f'input[data-development="question:{COMPACT_QUESTION}"]').check()
        request = prepare(page)
        answer = valid_answer(json.loads(request["user"]))
        answer["trajectory"][0]["evidence"] = ["E999"]
        pasted = replay(request, answer)
        page.locator("textarea.synthesis-response").fill(pasted)
        page.locator('button[data-synthesis="submit"]').click()
        page.wait_for_selector(".synthesis-error", timeout=20000)
        assert "E999" in page.locator(".synthesis-error").inner_text()
        assert page.locator("textarea.synthesis-response").input_value() == pasted, "the author's pasted text is kept"
        assert page.locator("textarea.synthesis-request").count() == 1


def test_a_follow_up_keeps_the_developments_and_gives_the_earlier_judgement_to_the_agent_as_text(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    with served_studio(browser, project) as (_server, page, _errors):
        open_panel(page)
        page.locator(f'input[data-development="question:{COMPACT_QUESTION}"]').check()
        first = prepare(page)
        page.locator("textarea.synthesis-response").fill(replay(first, valid_answer(json.loads(first["user"]))))
        page.locator('button[data-synthesis="submit"]').click()
        page.wait_for_selector(".synthesis-stage", timeout=20000)
        page.locator('button[data-synthesis="continue"]').click()
        page.locator('textarea[data-synthesis="criticism"]').fill("The settlement is a promise the record does not yet show anyone keeping.")
        follow = prepare(page, question="What would the follow-up need to show?")
        assert follow["settings"]["prior_request_sha256"] == first["request_sha256"]
        assert json.loads(follow["user"])["prior_judgement"]["request_sha256"] == first["request_sha256"]
        assert json.loads(follow["user"])["criticism"][0]["text"].startswith("The settlement is a promise")


def test_the_synthesis_fits_a_narrow_screen_without_horizontal_overflow(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    with served_studio(browser, project, width=390, height=844) as (_server, page, errors):
        open_panel(page)
        page.locator(f'input[data-development="question:{COMPACT_QUESTION}"]').check()
        request = prepare(page)
        page.locator("textarea.synthesis-response").fill(replay(request, valid_answer(json.loads(request["user"]))))
        page.locator('button[data-synthesis="submit"]').click()
        page.wait_for_selector(".synthesis-stage", timeout=20000)
        overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow == 0, overflow
        assert not [error for error in errors if error.strip()]
