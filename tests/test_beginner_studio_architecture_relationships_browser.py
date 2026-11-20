"""From an explanation the author reaches recorded genre interactions, the phases a genre acts in,
and declared emotional links, then returns (#620). Projection/presentation only."""
import json
import os

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


def contract(genre, role, target):
    return {"genre_node_id": genre, "role": role, "emotion_target_ids": [target],
            "trope_functions": [f"{genre} trope function"], "narrative_engine": f"{genre} engine",
            "structural_pattern": f"{genre} pattern", "payoff_expectations": ["payoff"]}


def target(id_, emotion):
    return {"id": id_, "emotion": emotion, "role": "primary", "intended_effect": "effect",
            "eliciting_condition": "condition", "aesthetic_strategy": "strategy", "provenance": "agent_proposed"}


ARCHITECTURE = {
    "schema_version": 2,
    "summary": "A records mystery yields to a succession thriller and resolves as tragedy.",
    "nodes": [
        {"id": "mystery", "title": "Records mystery", "category": "genre", "summary": "Fair-play inquiry."},
        {"id": "thriller", "title": "Succession thriller", "category": "genre", "summary": "A race for the heir."},
        {"id": "pyrrhic", "title": "Pyrrhic victory", "category": "trope", "summary": "Winning is the cost."},
        {"id": "grief_rx", "title": "Grief with defiant hope", "category": "reader_experience",
         "summary": "Mourning that refuses despair."},
    ],
    "links": [{"id": "pyrrhic-evokes", "source": "pyrrhic", "target": "grief_rx", "function": "aims to evoke"}],
    "emotion_targets": [target("curious", "joy"), target("dread", "fear")],
    "genre_contracts": [contract("mystery", "governing", "curious"), contract("thriller", "supporting", "dread")],
    "genre_interactions": [{"id": "squeeze", "source_genre_id": "thriller", "target_genre_id": "mystery",
                            "kind": "constrains", "mechanism": "Deadlines stop the archivist verifying evidence.",
                            "risk": "Readers stop trying to solve it."}],
    "phases": [
        {"id": "b2_war", "title": "Book 2 · The spring-tide war", "order": 2, "narrative_function": "War.",
         "genre_activations": [{"genre_node_id": "thriller", "basic_emotions": ["fear", "surprise"],
                                "structural_function": "The reversal and the race."}]},
        {"id": "b1_reading", "title": "Book 1 · The second reading", "order": 1, "narrative_function": "Reframe.",
         "genre_activations": [{"genre_node_id": "thriller", "basic_emotions": ["fear"],
                                "structural_function": "First weaponised truth."},
                               {"genre_node_id": "mystery", "basic_emotions": ["joy"],
                                "structural_function": "Fair clues."}]},
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


def test_genre_interactions_phases_and_emotional_links_are_navigable_and_return(tmp_path, browser):
    store = CanvasStore(tmp_path, "crown")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={"item": {
        "id": "story-vision", "title": "Story Vision", "content": "A three-book records mystery."},
        "position": {"x": 20, "y": 20}})
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
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=crown")
        page.wait_for_selector("#architecture-reader:not([hidden])")
        page.locator('[data-architecture-facet="genres"]').click()
        page.locator("#architecture-facet-list button", has_text="Succession thriller").click()
        related = hero.locator(".studio-explanation-related")
        assert related.locator("h4").all_text_contents() == [
            "Genres", "Reader emotions", "Tropes", "Structure and engines", "Across the story"]
        why = related.locator(".studio-semantic-why", has_text="Deadlines stop").get_attribute("id")
        assert related.locator(f'button[aria-describedby="{why}"]').inner_text().startswith("Explore Records mystery")
        text = related.inner_text()
        assert "Records mystery · constrains" in text
        assert "Deadlines stop the archivist verifying evidence. Risk: Readers stop trying to solve it." in text
        # Phases in story order, each with the genre's local function there.
        phases = related.locator("button", has_text="active in").all_inner_texts()
        assert [p.split(" · active")[0] for p in phases] == [
            "Explore Book 1 · The second reading", "Explore Book 2 · The spring-tide war"]
        assert "fear, surprise · The reversal and the race." in text

        # The constrained genre reads the relationship from its own side.
        related.locator("button", has_text="Records mystery · constrains").click()
        assert hero.locator("h2").inner_text() == "Records mystery"
        assert "Succession thriller · constrained by" in hero.locator(".studio-explanation-related").inner_text()
        page.get_by_role("button", name="← Previous context").click()
        assert hero.locator("h2").inner_text() == "Succession thriller"

        # Into the timeline at the phase, and back.
        related.locator("button", has_text="Book 2 · The spring-tide war · active in").click()
        assert page.locator('[data-architecture-facet="timeline"]').get_attribute("aria-pressed") == "true"
        assert "Book 2 · The spring-tide war" in page.locator("#inspector").inner_text()
        page.get_by_role("button", name="← Previous context").click()
        assert hero.locator("h2").inner_text() == "Succession thriller"

        # A declared trope → reader-experience link resolves instead of being dropped.
        page.locator('[data-architecture-facet="tropes"]').click()
        page.locator("#architecture-facet-list button", has_text="Pyrrhic victory").click()
        hero.locator("button", has_text="Grief with defiant hope · aims to evoke").click()
        assert page.locator('[data-architecture-facet="emotions"]').get_attribute("aria-pressed") == "true"
        inspector = page.locator("#inspector").inner_text()
        assert "Grief with defiant hope" in inspector and "Reader experience (graph node)" in inspector
        assert "aims to evoke" in page.locator("#studio-semantic-arrival").inner_text()
        page.get_by_role("button", name="← Previous context").click()
        assert hero.locator("h2").inner_text() == "Pyrrhic victory"
        page.locator('[data-architecture-facet="emotions"]').click()

        # An emotion target lists the phases that name its basic emotion.
        page.locator("#architecture-facet-list button", has_text="fear").first.click()
        assert "name the basic emotion fear (not a claim about this target specifically)" in page.locator(
            "#inspector").inner_text()
        phase_buttons = page.locator("#inspector button", has_text="Phase naming fear").all_inner_texts()
        assert phase_buttons == ["Phase naming fear: Book 1 · The second reading",
                                 "Phase naming fear: Book 2 · The spring-tide war"]
        assert errors == []
        assert (store.directory / "canvas.json").read_bytes() == before
        assert not (tmp_path / "story_identity.yaml").exists()
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
