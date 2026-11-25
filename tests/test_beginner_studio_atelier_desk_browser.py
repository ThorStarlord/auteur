"""Served Atelier: the coding-agent desk opens beside the concept it examines, and returns to it.

Asking from a Book discovery opens the desk in place of the folio: over the reading edge of the atlas on wide
screens, where the examined concept stays in the open part of the atlas, and beneath the atlas on narrow screens.
Returning closes the desk, puts focus where the author can see it, and loses nothing that was typed. Escape in
the desk returns to the atlas without deselecting the concept.
"""
import time

from test_beginner_studio_atelier_discovery_browser import (  # noqa: F401  (fixtures and helpers)
    browser, open_discovery, pristine, q, served,
)

BACK = "#studio-atelier .atl-desk-back"
LIVE = "document.querySelector('#studio-atelier .atl-live').textContent"
FIELD = "#architecture-creative-agent-panel textarea"
SNAPSHOT = "document.getElementById('studio-atelier').atelierStudy.snapshot()"


def desk_state(page):
    return page.evaluate("""() => {
      const d = document.querySelector('#studio-atelier .atl-desk');
      const f = document.querySelector('#studio-atelier .atl-folio');
      const stage = document.querySelector('#studio-atelier .atl-stage').getBoundingClientRect();
      const box = d.getBoundingClientRect();
      return {open: !d.hidden, folioInert: f.inert, stageBottom: stage.bottom, deskLeft: box.left, deskTop: box.top,
        panelInDesk: d.contains(document.getElementById('architecture-creative-agent-panel'))};
    }""")


def open_desk_from_discovery(page):
    page.locator(q("book-investigate:24")).click()
    page.wait_for_function("!document.querySelector('#studio-atelier .atl-desk').hidden", timeout=10000)
    time.sleep(0.6)


def test_asking_opens_the_desk_beside_the_atlas_and_keeps_the_concept_in_view(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    open_desk_from_discovery(page)
    state = desk_state(page)
    assert state["open"] and state["folioInert"] and state["panelInDesk"]
    assert state["deskLeft"] > 700, state  # the desk takes the reading edge at 1440 wide
    focus_id = page.evaluate(SNAPSHOT + ".focus")
    star = page.evaluate("""(id) => {
      const s = document.querySelector('#studio-atelier .atl-star[data-id="' + id + '"]');
      return s ? s.getBoundingClientRect().right : null;
    }""", focus_id)
    assert star is not None and star <= state["deskLeft"], (star, state)
    assert not log["errors"]


def test_returning_to_the_atlas_closes_the_desk_and_keeps_what_was_typed(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    open_desk_from_discovery(page)
    page.locator(FIELD).first.fill("an unsent thought")
    page.locator(BACK).click()
    time.sleep(0.4)
    state = desk_state(page)
    assert not state["open"] and not state["folioInert"], state
    # Back on the desktop the discovery card is beside the atlas again, so focus returns to it.
    assert page.evaluate("document.activeElement && document.activeElement.dataset.key") == "book-discovery-h:24"
    open_desk_from_discovery(page)
    assert page.locator(FIELD).first.input_value() == "an unsent thought"
    assert not log["errors"]


def test_escape_in_the_desk_returns_to_the_atlas_and_keeps_the_concept(browser, served):
    project, base = served
    page, log = open_discovery(browser, base)
    open_desk_from_discovery(page)
    focus_before = page.evaluate(SNAPSHOT + ".focus")
    page.locator(BACK).focus()
    page.keyboard.press("Escape")
    time.sleep(0.4)
    assert not desk_state(page)["open"]
    assert page.evaluate(SNAPSHOT + ".focus") == focus_before  # the concept stays selected
    assert not log["errors"]


def test_phone_desk_sits_beneath_the_atlas_and_returns_to_it(browser, served):
    project, base = served
    page, log = open_discovery(browser, base, width=390, height=844)
    open_desk_from_discovery(page)
    state = desk_state(page)
    assert state["open"] and state["panelInDesk"]
    assert state["deskTop"] >= state["stageBottom"] - 2, state  # beneath the atlas, not over it
    page.locator(BACK).click()
    time.sleep(0.5)
    state = desk_state(page)
    assert not state["open"], state
    atlas_top = page.evaluate("document.getElementById('studio-atelier').getBoundingClientRect().top")
    assert atlas_top <= 40, atlas_top  # the atlas is back on screen
    assert page.evaluate("document.getElementById('studio-atelier').contains(document.activeElement)")
    assert "Back to the atlas" in page.evaluate(LIVE)
    assert not log["errors"]
