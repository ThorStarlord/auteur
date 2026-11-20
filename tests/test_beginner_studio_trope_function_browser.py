"""One trope is reached from each genre-specific function that realises it, in the served Studio (#622 follow-up)."""
import json
import os

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response

ARCHITECTURE = {
    "schema_version": 2,
    "summary": "A records mystery becomes a succession thriller; the same trope costs both genres differently.",
    "nodes": [
        {"id": "mystery", "title": "Records mystery", "category": "genre", "summary": "Fair-play inquiry."},
        {"id": "thriller", "title": "Succession thriller", "category": "genre", "summary": "A race for the heir."},
        {"id": "pyrrhic", "title": "Pyrrhic victory", "category": "trope", "summary": "Winning destroys what it was for."},
        {"id": "grief_rx", "title": "Grief with defiant hope", "category": "reader_experience",
         "summary": "Mourning that refuses despair."},
    ],
    "links": [{"id": "pyrrhic-evokes", "source": "pyrrhic", "target": "grief_rx", "function": "aims to evoke"}],
    "emotion_targets": [
        {"id": "curious", "emotion": "joy", "role": "primary", "intended_effect": "Delight.",
         "eliciting_condition": "A clue reframes.", "aesthetic_strategy": "Documents.", "provenance": "agent_proposed"},
        {"id": "dread", "emotion": "fear", "role": "supporting", "intended_effect": "Dread.",
         "eliciting_condition": "A truth is used.", "aesthetic_strategy": "Withholding.", "provenance": "agent_proposed"},
    ],
    "genre_contracts": [
        {"genre_node_id": "mystery", "role": "governing", "emotion_target_ids": ["curious"],
         "trope_functions": ["The price of a solved mystery is the record's trust."],
         "trope_function_refs": [{"function_index": 0, "trope_node_id": "pyrrhic"}],
         "narrative_engine": "Documents reveal falsified history.", "structural_pattern": "Question, evidence, reframing.",
         "payoff_expectations": ["The drowning is explained fairly."]},
        {"genre_node_id": "thriller", "role": "supporting", "emotion_target_ids": ["dread"],
         "trope_functions": ["Winning the succession costs the heir her name."],
         "trope_function_refs": [{"function_index": 0, "trope_node_id": "pyrrhic"}],
         "narrative_engine": "Factions race the tide calendar.", "structural_pattern": "Deadlines and betrayals.",
         "payoff_expectations": ["The heir survives."]},
    ],
    "phases": [
        {"id": "war", "title": "The spring-tide war", "order": 1, "narrative_function": "The race.",
         "genre_activations": [{"genre_node_id": "thriller", "basic_emotions": ["fear"],
                                "trope_functions": ["Winning the succession costs the heir her name."],
                                "trope_function_refs": [{"function_index": 0, "trope_node_id": "pyrrhic"}],
                                "structural_function": "The race."}]},
    ],
}


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as playwright:
        options = {"headless": True, "args": ["--no-sandbox"]}
        if os.environ.get("CHROMIUM_PATH"):
            options["executable_path"] = os.environ["CHROMIUM_PATH"]
        instance = playwright.chromium.launch(**options)
        yield instance
        instance.close()


def test_one_trope_reaches_each_genre_specific_function_and_returns(tmp_path, browser):
    store = CanvasStore(tmp_path, "tide")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={"item": {
        "id": "story-vision", "title": "Story Vision", "content": "A records mystery."}, "position": {"x": 20, "y": 20}})
    pending = prepare_architecture(store)
    complete_architecture(store, build_host_agent_response(
        HostAgentRequest(**pending["request"]), json.dumps(ARCHITECTURE), runtime="browser-test", model="fixture",
    ).model_dump())
    before = (store.directory / "canvas.json").read_bytes()
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    hero = page.locator("#studio-explanatory-hero")
    trail = page.locator("#studio-semantic-trail")
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=tide")
        page.wait_for_selector("#architecture-reader:not([hidden])")
        page.locator('[data-architecture-facet="tropes"]').click()
        page.locator("#architecture-facet-list button", has_text="Pyrrhic victory").click()
        # The shared trope lists each genre-specific function that realises it, with its own source.
        reached = hero.locator("button.studio-semantic-link", has_text="performed as a function here")
        assert reached.count() == 2
        assert "Pyrrhic victory" in hero.inner_text()

        # Trope -> one genre-specific function: the link names the function, not a merged trope.
        hero.locator("button.studio-semantic-link", has_text="Winning the succession costs the heir").first.click()
        assert "Winning the succession costs the heir her name." in hero.inner_text()
        assert "Succession thriller" in page.locator("#inspector").inner_text()

        # Previous Context returns to the trope it came from.
        trail.locator("button", has_text="Previous context").evaluate("button => button.click()")
        assert "Pyrrhic victory" in hero.inner_text()
        assert reached.count() == 2

        # Keyboard: the phase link opens the timeline and Previous Context returns.
        page.locator('[data-architecture-facet="genres"]').click()
        page.locator("#architecture-facet-list button", has_text="Succession thriller").click()
        link = hero.locator("button.studio-semantic-link", has_text="spring-tide war")
        link.focus()
        page.keyboard.press("Enter")
        assert page.locator('[data-architecture-facet="timeline"]').get_attribute("aria-pressed") == "true"
        assert "spring-tide war" in page.locator("#inspector").inner_text()
        assert errors == []
        assert (store.directory / "canvas.json").read_bytes() == before
        assert not (tmp_path / "story_identity.yaml").exists()
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
