"""The Studio's status line: an announcement survives a canvas save that finishes after it.

A coding agent's answer is announced on the shared status line when it arrives. Refreshing the Architecture also schedules a
canvas save (its viewport), and that save's confirmation used to replace the announcement whenever it finished later. The
contract is that the announcement stays, with the confirmation added to it. This test makes the ordering deterministic: the
save is held at the network until the answer is announced, and only then released.
"""
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tests"))
import test_beginner_studio_atelier_discovery_browser as T  # noqa: E402
from auteur.beginner.studio_architecture_inquiry import complete_architecture_inquiry, project_architecture_inquiry  # noqa: E402
from auteur.beginner.studio_store import CanvasStore  # noqa: E402
from test_beginner_studio_book_discovery import answer  # noqa: E402

ANSWER_ANNOUNCED = "Your coding agent’s answer arrived"
SAVED = "Working canvas saved locally"
SAVE_URL = "**/commands/replace-working-document"

# Flags the first canvas-save response that carries a revision, as the page parses it. The page's completion runs in the same
# task as that parse, so once the flag is set the completion's status write has happened.
SAVE_PARSED = """() => {
  window.__saveParsed = false;
  const json = Response.prototype.json;
  Response.prototype.json = function () {
    return json.call(this).then(function (body) {
      if (body && typeof body === 'object' && 'revision' in body && 'deleted' in body) window.__saveParsed = true;
      return body;
    });
  };
}"""


# The same served project and browser fixtures as the discovery journeys, imported so pytest can resolve them here.
from test_beginner_studio_atelier_discovery_browser import browser, pristine, served  # noqa: E402,F401


def test_an_answer_stays_announced_when_a_save_finishes_after_it(browser, served):
    project, base = served
    page, log = T.open_discovery(browser, base)
    held = []
    page.route(SAVE_URL, lambda route: held.append(route))
    page.evaluate(SAVE_PARSED)

    page.locator(T.q("book-investigate:24")).click()
    time.sleep(0.6)
    page.locator(f"{T.PANEL} [data-creative-submit]").click()
    page.wait_for_function(f"document.querySelector('{T.PANEL} [role=status]').textContent.includes('prepared')", timeout=15000)
    store = CanvasStore(project, T.CANVAS)
    complete_architecture_inquiry(store, answer(project_architecture_inquiry(store)))

    # The refresh schedules the canvas save; it is held at the network until the announcement is on the page.
    page.locator("#architecture-refresh").click()
    page.wait_for_function(f"document.querySelector('#status').textContent.includes('{ANSWER_ANNOUNCED}')", timeout=15000)
    deadline = time.time() + 15
    while not held and time.time() < deadline:
        page.wait_for_timeout(50)
    assert held, "the refresh did not schedule a canvas save, so the ordering under test did not occur"
    assert ANSWER_ANNOUNCED in page.locator("#status").inner_text()

    held[0].continue_()
    page.wait_for_function("window.__saveParsed === true", timeout=15000)

    status = page.locator("#status").inner_text()
    assert ANSWER_ANNOUNCED in status, status
    assert SAVED in status, status
    assert page.evaluate("document.activeElement && document.activeElement.dataset.inquiryAnswer === 'true'")
    assert not log["errors"]


def test_a_canvas_switch_leaves_the_previous_announcement_behind(browser, served):
    """The shared save state belongs to one canvas. A switch waits for the pending save, then loads the new canvas as a new
    page, so the previous canvas's announcement cannot appear on it."""
    project, base = served
    page, log = T.open_discovery(browser, base)
    held = []
    page.route(SAVE_URL, lambda route: held.append(route))
    page.locator(T.q("book-investigate:24")).click()
    time.sleep(0.6)
    page.locator(f"{T.PANEL} [data-creative-submit]").click()
    page.wait_for_function(f"document.querySelector('{T.PANEL} [role=status]').textContent.includes('prepared')", timeout=15000)
    store = CanvasStore(project, T.CANVAS)
    complete_architecture_inquiry(store, answer(project_architecture_inquiry(store)))
    page.locator("#architecture-refresh").click()
    page.wait_for_function(f"document.querySelector('#status').textContent.includes('{ANSWER_ANNOUNCED}')", timeout=15000)
    deadline = time.time() + 15
    while not held and time.time() < deadline:
        page.wait_for_timeout(50)
    assert held, "the refresh did not schedule a canvas save"

    # Switching canvases waits for the pending save; release it so the switch can proceed.
    page.evaluate("document.getElementById('new-canvas').click()")
    held[0].continue_()
    page.wait_for_url(lambda url: f"canvas={T.CANVAS}" not in url, timeout=20000)
    page.wait_for_load_state("networkidle")
    page.wait_for_function("document.querySelector('#status').textContent.length > 0", timeout=20000)
    assert ANSWER_ANNOUNCED not in page.locator("#status").inner_text()
    assert not log["errors"]
