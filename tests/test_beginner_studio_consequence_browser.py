"""The served Studio's consequence analysis of a pending revision, end to end.

The author sees a proposed working revision in the review; asks for its consequences; pastes the coding agent's answer
(a replayed fixture built from the exact request, so nothing calls a provider); reads the concerns, the recorded Book
relationships, and the alternatives with their gains and costs; and may investigate an alternative through the existing
creative panel. Apply is never blocked by the analysis. Declining (leaving the proposal unapplied) changes no narrative
record. An analysis of an earlier proposal is labelled as such, never presented as the current one.
"""
import contextlib
import json
import shutil
import sys
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture_consequence import project_architecture_consequence
from auteur.beginner.studio_architecture_inquiry import project_architecture_inquiry
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "tests"))
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_architecture_consequence import (  # noqa: E402
    INSTRUCTION, Q_CONVERSION, packet_of, propose, reword_conversion, snapshot,
)
from test_architecture_consequence_v3 import (  # noqa: E402
    COMPACT, compact_under_retained_terms, mechanism_answer, valid_answer_v3,
)
from test_persistent_narrative_questions import assign_identities  # noqa: E402
from test_persistent_question_journey import reconcile  # noqa: E402

CANVAS = discovery.SPRING
BOOK = 24


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        yield instance
        instance.close()


@pytest.fixture(scope="module")
def identified(tmp_path_factory):
    root = tmp_path_factory.mktemp("consequence-served") / "discovery"
    store = discovery.seed_discovery(root)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    reconcile(store, root, BOOK)
    return root


def copy_of(identified: Path, tmp_path: Path) -> Path:
    target = tmp_path / "discovery"
    shutil.copytree(identified, target)
    return target


def store_for(project: Path) -> CanvasStore:
    return CanvasStore(project, CANVAS)


@contextlib.contextmanager
def served_studio(browser, project: Path, width: int = 1440, height: int = 900):
    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": width, "height": height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas={CANVAS}", wait_until="networkidle")
        page.wait_for_selector("#architecture-status", state="attached", timeout=20000)
        yield server, page, errors
        assert not errors, errors
    finally:
        page.close()
        server.stop()
        thread.join(timeout=5)


def narrative_snapshot(project: Path) -> dict[str, bytes]:
    """The narrative records only. Investigating an alternative prepares an inquiry request through the existing deliberation
    path, which is a request record of its own, not a change to the canvas, the Architecture or a Working Book."""
    return {path: data for path, data in snapshot(project).items() if "inquiries" not in Path(path).parts}


def section_text(page) -> str:
    return page.locator("#architecture-consequence").text_content()


def replay(request: dict, payload) -> str:
    response = build_host_agent_response(
        HostAgentRequest(**request), json.dumps(payload), runtime="consequence-served-replay")
    return json.dumps(response.model_dump(), default=str)


def ask_and_answer(page, store, answer=valid_answer_v3) -> dict:
    """Ask about the proposal on screen and paste the replayed answer built from its exact request."""
    page.locator("#architecture-consequence .consequence-prepare").click()
    page.wait_for_selector("#architecture-consequence textarea.consequence-request", timeout=15000)
    request = json.loads(page.locator("#architecture-consequence textarea.consequence-request").input_value())
    packet = json.loads(request["user"])["consequence_packet"]
    page.locator("#consequence-response").fill(replay(request, answer(packet)))
    page.locator("#architecture-consequence .consequence-submit").click()
    page.wait_for_selector("#architecture-consequence .consequence-concern", timeout=15000)
    return request


def test_the_proposal_is_examined_answered_and_investigated_without_gating_apply(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    before = narrative_snapshot(project)
    with served_studio(browser, project) as (_server, page, _errors):
        page.wait_for_selector("#architecture-consequence:not([hidden])", timeout=20000)
        assert page.locator("#architecture-consequence .consequence-concern").count() == 0
        ask_and_answer(page, store)
        text = section_text(page)
        assert "About this proposal, not yet applied." in text
        assert "Whether the conversion is a lasting settlement" in text
        assert "May be displaced" in text and "New concern" in text
        assert "Reach: May reach later Books through a conditional inheritance." in text
        assert "Your instruction names this concern." in text
        # Version 2: the recorded mechanisms behind the reading, each with its provenance, and the inheritance Book 24 records.
        assert "Recorded mechanisms this reading rests on" in text
        assert "What later Books may inherit" in text
        assert "Recorded inheritance" in text and "Plausible inheritance" in text
        assert "Possible developmental trajectories (hypothetical)" in text
        assert page.locator("#architecture-consequence .consequence-hypothetical").first.text_content() == "Hypothetical"
        mechanism = page.locator("#architecture-consequence details.consequence-mechanism-details").first
        assert "Preserved in the proposal" in mechanism.text_content() or "Transformed by the proposal" in mechanism.text_content()
        mechanism.locator(":scope > summary").click()
        assert "Reading (agent interpretation):" in section_text(page)
        # The author sees what the analysis examined, and the evidence for a concern, behind disclosures.
        page.locator("#architecture-consequence details.consequence-examined > summary").click()
        assert "Working Books whose decisions were read: 24." in section_text(page)
        assert "Mechanisms offered:" in section_text(page)
        page.locator("#architecture-consequence details.consequence-evidence summary").first.click()
        assert "Working Book decision (Book 24) · question in proposal: reworded" in section_text(page)
        # Apply is not gated by the analysis, even though it reports a concern that may be displaced.
        assert page.locator("#architecture-apply").is_enabled()
        # Investigate the alternative: its questions go to the creative panel's inquiry, and nothing is applied.
        page.locator("#architecture-consequence .consequence-investigate").first.click()
        page.wait_for_function(
            "document.querySelector('#architecture-consequence .consequence-notice') && "
            "document.querySelector('#architecture-consequence .consequence-notice').textContent.includes('Investigation prepared')",
            timeout=15000)
        inquiry = project_architecture_inquiry(store)["request"]
        assert json.loads(inquiry["user"])["from_consequence"]["alternative_id"] == "a1"
        # The wording the investigation carries stays attributed to the analysis, on the page, in the creative panel.
        origin = page.locator("#architecture-creative-agent-panel .creative-origin").text_content()
        assert "From an alternative a consequence analysis of this proposal set out" in origin, origin
        assert "not yours" in origin, origin
        assert narrative_snapshot(project) == before, "the analysis or its investigation changed narrative state"
        # Apply is the author's own act: the applied revision's analysis then reads as historical about an applied change.
        page.locator("#architecture-apply").click()
        page.wait_for_function("!document.querySelector('#architecture-consequence') || "
                               "document.querySelector('#architecture-consequence').hidden", timeout=15000)
    assert project_architecture_consequence(store)["standing"] == "applied"


def test_declining_the_proposal_leaves_the_analysis_readable_and_changes_no_narrative_record(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    before = narrative_snapshot(project)
    with served_studio(browser, project, width=390, height=844) as (_server, page, _errors):
        page.wait_for_selector("#architecture-consequence:not([hidden])", timeout=20000)
        ask_and_answer(page, store)
        # Declining is leaving the proposal unapplied. Reloading shows the same analysis, still about this proposal.
        page.reload(wait_until="networkidle")
        page.wait_for_selector("#architecture-consequence .consequence-concern", timeout=15000)
        assert "About this proposal, not yet applied." in section_text(page)
        # On a narrow screen the analysis fits its width: no horizontal page scroll.
        overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow <= 1, overflow
        box = page.locator("#architecture-consequence").bounding_box()
        assert box["width"] <= 390
    assert narrative_snapshot(project) == before


def test_an_analysis_of_an_earlier_proposal_is_labelled_and_the_proposal_on_screen_can_be_asked_about(
        browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    from test_architecture_consequence import replay as owner_replay
    from auteur.beginner.studio_architecture_consequence import (
        complete_architecture_consequence, prepare_architecture_consequence)
    prepared = prepare_architecture_consequence(store)
    complete_architecture_consequence(store, owner_replay(prepared["request"], valid_answer_v3(packet_of(prepared))))
    # A different revision replaces the proposal the analysis examined.
    propose(store, "Say how reading is taught.",
            lambda c: c["nodes"][0].__setitem__("summary", c["nodes"][0]["summary"] + " Revised for the test."))
    with served_studio(browser, project) as (_server, page, _errors):
        page.wait_for_selector("#architecture-consequence:not([hidden])", timeout=20000)
        page.wait_for_selector("#architecture-consequence .consequence-concern", timeout=15000)
        text = section_text(page)
        assert "About an earlier proposal. It is not the proposal on screen." in text
        assert "About this proposal, not yet applied." not in text
        assert page.locator("#architecture-consequence .consequence-investigate").count() == 0
        # The proposal on screen has no analysis of its own: it can be asked about now.
        page.locator("#architecture-consequence .consequence-prepare").click()
        page.wait_for_selector("#architecture-consequence textarea.consequence-request", timeout=15000)
        assert "About this proposal, not yet applied." in section_text(page)
    assert project_architecture_consequence(store)["standing"] == "current"


def focus_inside_section(page) -> bool:
    return page.evaluate("!!document.activeElement && !!document.activeElement.closest('#architecture-consequence')")


def test_keyboard_focus_stays_in_the_analysis_and_an_unsent_answer_survives_a_refusal(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    with served_studio(browser, project) as (_server, page, _errors):
        page.wait_for_selector("#architecture-consequence:not([hidden])", timeout=20000)
        page.locator("#architecture-consequence .consequence-prepare").focus()
        page.keyboard.press("Enter")
        page.wait_for_selector("#architecture-consequence textarea.consequence-request", timeout=15000)
        assert focus_inside_section(page), "focus fell out of the analysis after Ask"
        # A response the owner refuses keeps the author's text, and says why.
        page.locator("#consequence-response").fill("{ this is not a response")
        page.locator("#architecture-consequence .consequence-submit").click()
        page.wait_for_selector("#architecture-consequence .consequence-error", timeout=15000)
        assert "must be valid HostAgentResponse JSON" in section_text(page)
        assert page.locator("#consequence-response").input_value() == "{ this is not a response"
        assert focus_inside_section(page), "focus fell out of the analysis after a refusal"
        # The announcement reaches the persistent live region, outside the panel that is redrawn.
        assert "must be valid" in page.locator("#architecture-consequence-alert").text_content()


def test_a_double_press_of_investigate_sends_one_inquiry(browser, identified, tmp_path):
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, INSTRUCTION, reword_conversion)
    with served_studio(browser, project) as (_server, page, _errors):
        page.wait_for_selector("#architecture-consequence:not([hidden])", timeout=20000)
        ask_and_answer(page, store)
        posts = []
        page.on("request", lambda request: posts.append(request.url) if request.method == "POST" and
                "/architecture/inquiry/prepare" in request.url else None)
        # A double press is two clicks in one task, before any reply can arrive; a second click after the reply is a new ask.
        page.evaluate("""() => {
            const b = document.querySelector('#architecture-consequence .consequence-investigate');
            b.click(); b.click();
        }""")
        page.wait_for_function(
            "document.querySelector('#architecture-consequence .consequence-notice') && "
            "document.querySelector('#architecture-consequence .consequence-notice').textContent.includes('Investigation prepared')",
            timeout=15000)
        assert len(posts) == 1, posts


def test_a_mechanism_alone_is_read_as_a_connection_and_investigated_from_the_served_page(browser, identified, tmp_path):
    """PR #647's motivating case: a recorded relation changes and no question does. The alternative concerns the mechanism alone."""
    project = copy_of(identified, tmp_path)
    store = store_for(project)
    propose(store, "Make the Mill Compact's labour duty apply in every season.", compact_under_retained_terms)
    before = narrative_snapshot(project)
    with served_studio(browser, project) as (_server, page, _errors):
        page.wait_for_selector("#architecture-consequence:not([hidden])", timeout=20000)
        ask_and_answer(page, store, answer=lambda packet: mechanism_answer(packet))
        text = section_text(page)
        assert "How the mechanisms relate" in text
        assert "Between: link l_compact_hands_in_kind (transformed) and link l_trade_draws_without_return" in text
        assert "The recorded graph: Both name the same node as an endpoint (node inst_mill_compact)." in text
        assert "Mechanism it concerns (no question needed): link l_compact_hands_in_kind" in text
        assert page.locator("#architecture-consequence .consequence-alternative .consequence-questions").count() == 0
        page.locator("#architecture-consequence .consequence-investigate").first.click()
        page.wait_for_function(
            "document.querySelector('#architecture-consequence .consequence-notice') && "
            "document.querySelector('#architecture-consequence .consequence-notice').textContent.includes('Investigation prepared')",
            timeout=15000)
        inquiry = json.loads(project_architecture_inquiry(store)["request"]["user"])
        assert inquiry["from_consequence"]["questions"] == []
        assert inquiry["from_consequence"]["mechanisms"][0]["record_id"] == COMPACT
        assert inquiry["graph_intent"]["anchors"][0]["kind"] == "link"
        assert inquiry["graph_intent"]["anchors"][0]["id"] == COMPACT
        assert narrative_snapshot(project) == before, "the mechanism's analysis and its investigation changed narrative state"
