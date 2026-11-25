"""Served Atelier: a Book decision's open question can be asked about, and the question is what the desk asks.

The author sees the question a Book decision refers to, asks about it, and the desk opens on the question with the
Book's element as evidence. Submitting prepares a host-agent request that is not executed and changes nothing.
"""
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
import seed_book_discovery_study as discovery  # noqa: E402
import seed_book_impact_study as impact  # noqa: E402
from test_persistent_narrative_questions import assign_identities  # noqa: E402

CANVAS = discovery.SPRING
LEDGER = "structure|structure-node:eng_ledger"


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        instance = playwright.chromium.launch(headless=True, args=["--no-sandbox"])
        yield instance
        instance.close()


@pytest.fixture(scope="module")
def identified(tmp_path_factory):
    root = tmp_path_factory.mktemp("question-browser") / "discovery"
    store = discovery.seed_discovery(root)
    impact.revise_architecture(store, "Give each open question a stable identity.", assign_identities)
    discovery.reconcile_book_24(root)
    return root


def test_a_decision_question_is_asked_about_and_the_desk_asks_the_question(browser, identified, tmp_path):
    project = tmp_path / "discovery"
    shutil.copytree(identified, project)
    server = BeginnerWorkspaceServer(project, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas={CANVAS}&atelier", wait_until="networkidle")
        page.wait_for_selector("#studio-atelier .atl-star", state="attached", timeout=20000)
        time.sleep(0.6)
        page.evaluate("(id) => document.querySelector('#studio-atelier .atl-star[data-id=\"' + id + '\"]').click()", LEDGER)
        page.wait_for_function("document.querySelector('#studio-atelier .atl-series .atl-series-status')", timeout=10000)
        page.locator('#studio-atelier [data-key="series-open:24"]').click()
        page.wait_for_selector("#studio-atelier .atl-decision-questions", timeout=10000)
        assert "A recorded decision refers to" not in page.locator("#studio-atelier").inner_text()  # current wording is quiet
        page.locator('#studio-atelier [data-key^="book-question:24:"]').first.click()
        page.wait_for_function("!document.querySelector('#studio-atelier .atl-desk').hidden", timeout=15000)
        time.sleep(0.6)
        assert "Asking about" in page.locator("#studio-atelier .atl-desk-title").inner_text() or \
            "Your question about" in page.locator("#studio-atelier .atl-desk-title").inner_text()
        assert "Is the Book 20 hands-to-draw conversion" in page.locator("#studio-atelier .atl-desk-title").inner_text()
        page.locator("#architecture-creative-agent-panel textarea").first.fill("Does the earlier formulation still fit?")
        page.locator("#architecture-creative-agent-panel [data-creative-submit]").click()
        page.wait_for_function(
            "document.querySelector('#architecture-creative-agent-panel [role=status]').textContent.includes('prepared')",
            timeout=15000)
        assert not errors
    finally:
        page.close()
        server.stop()
        thread.join(timeout=5)
