"""Architecture opens with a short readable design, and each perspective starts on the first screen (#619).

The 2026-11-03 design asks for a *short* readable architecture first and keeps the graph-first Studio
as a constraint; the 2026-10-11 plan asks that the graph, explanations and timeline not sit below a
long report. The full linear report stays available as the non-visual equivalent.
"""
import json
import os

import pytest
from playwright.sync_api import sync_playwright

from auteur.beginner.server import BeginnerWorkspaceServer
from auteur.beginner.studio_architecture import complete_architecture, prepare_architecture
from auteur.beginner.studio_store import CanvasStore
from auteur.host_agent import HostAgentRequest, build_host_agent_response


def node(id_, title, category, summary):
    return {"id": id_, "title": title, "category": category, "summary": summary}


def target(id_, emotion, role, effect):
    return {"id": id_, "emotion": emotion, "role": role, "intended_effect": effect,
            "eliciting_condition": "A visible cost is paid.", "aesthetic_strategy": "Concrete costs first.",
            "provenance": "agent_proposed"}


ARCHITECTURE = {
    "schema_version": 2,
    "summary": "Power is earned through kept oaths, and every oath binds the paladin closer to her god.",
    "nodes": [
        node("progression", "Progression fantasy", "genre", "Visible, earned growth."),
        node("tragic", "Tragic undertow", "genre", "Each victory deepens a binding."),
        node("oath_power", "Oaths as power", "engine", "Each kept oath grants a capability and an obligation."),
        node("earned_breakthrough", "Earned breakthrough", "trope", "Power arrives after visible sacrifice."),
        node("ladder", "Oath ladder", "structure", "Escalating trials."),
    ],
    "links": [{"id": "breakthrough-uses-oaths", "source": "earned_breakthrough", "target": "oath_power",
               "function": "implements"}],
    "emotion_targets": [target("joy_growth", "joy", "primary", "Satisfaction in hard-won capability."),
                        target("fear_binding", "fear", "supporting", "Dread that each gain narrows her future.")],
    "genre_contracts": [
        {"genre_node_id": "progression", "role": "governing", "emotion_target_ids": ["joy_growth"],
         "trope_functions": ["Earned breakthrough converts sacrifice into capability."],
         "narrative_engine": "Kept oaths grant capability.", "structural_pattern": "Challenge, effort, growth.",
         "payoff_expectations": ["She reaches the highest tier."]},
        {"genre_node_id": "tragic", "role": "tertiary", "emotion_target_ids": ["fear_binding"],
         "trope_functions": ["The mentor's price shows the end in advance."],
         "narrative_engine": "Each gain tightens the binding.", "structural_pattern": "Rising undertow.",
         "payoff_expectations": ["The binding is understood."]},
    ],
    "genre_interactions": [{"id": "growth-vs-dread", "source_genre_id": "progression", "target_genre_id": "tragic",
                            "kind": "creates_tension", "mechanism": "Every power gain is a deeper binding."}],
    "phases": [
        {"id": "ash", "title": "Ash and the first oath", "order": 1, "narrative_function": "The first cost of power.",
         "genre_activations": [{"genre_node_id": "progression", "basic_emotions": ["joy"],
                                "structural_function": "The first tier."}]},
        {"id": "refusal", "title": "The refused oath", "order": 2, "narrative_function": "She keeps her freedom.",
         "genre_activations": [{"genre_node_id": "tragic", "basic_emotions": ["fear"],
                                "structural_function": "The binding breaks."}]},
    ],
    "open_questions": ["Does she keep the powers she earned before the god spoke?"],
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


def top(page, selector):
    return page.evaluate("""selector => {
        const e = document.querySelector(selector);
        return e && !e.hidden && e.offsetParent !== null ? e.getBoundingClientRect().top + scrollY : null;
    }""", selector)


def test_architecture_opens_short_and_every_perspective_starts_on_the_first_screen(tmp_path, browser):
    store = CanvasStore(tmp_path, "oath")
    store.create()
    store.apply("create-item", expected_revision=0, command_id="vision", payload={"item": {
        "id": "story-vision", "title": "Story Vision", "content": "A paladin rebuilds her power one oath at a time."},
        "position": {"x": 20, "y": 20}})
    pending = prepare_architecture(store)
    complete_architecture(store, build_host_agent_response(
        HostAgentRequest(**pending["request"]), json.dumps(ARCHITECTURE), runtime="browser-test", model="fixture",
    ).model_dump())
    server = BeginnerWorkspaceServer(tmp_path, port=0)
    thread = server.start_in_thread()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    try:
        page.goto(f"http://127.0.0.1:{server.port}/studio.html?canvas=oath")
        page.wait_for_selector("#architecture-reader:not([hidden])")
        reader = page.locator("#architecture-reader")
        glance = reader.inner_text()
        assert "At a glance" in glance
        assert "Narrative engines: Oaths as power" in glance
        assert "Progression fantasy creates tension with Tragic undertow" in glance
        assert "Development: 2 phases — Ash and the first oath → The refused oath" in glance
        # The long sections are present but collapsed; the graph follows a short overview.
        full = page.locator("#architecture-reader details.architecture-reader-full")
        assert full.get_attribute("open") is None
        assert "Functional tropes" not in glance
        assert reader.bounding_box()["height"] < 600
        assert top(page, "#viewport") < 1000

        page.get_by_text("Read the full architecture").click()
        assert "Functional tropes" in reader.inner_text()
        assert "Every power gain is a deeper binding." in reader.inner_text()

        # Other perspectives replace the overview instead of sitting below it.
        for facet, surface in (("tropes", "#studio-explanatory-hero"), ("genres", "#studio-explanatory-hero"),
                               ("timeline", "#genre-timeline")):
            page.locator(f'[data-architecture-facet="{facet}"]').click()
            assert reader.is_hidden(), facet
            assert top(page, surface) < 900, facet
        assert "Ash and the first oath" in page.locator("#genre-timeline").inner_text()

        # Story Realization never shows the architecture report in its work area.
        page.locator("#workspace-realization").click()
        assert reader.is_hidden()
        page.locator("#workspace-architecture").click()
        page.locator('[data-architecture-facet="overview"]').click()
        assert reader.is_visible()

        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth") <= 390
        page.locator('[data-architecture-facet="tropes"]').click()
        assert reader.is_hidden() and top(page, "#studio-explanatory-hero") < 1100
        assert errors == []
        assert not (tmp_path / "story_identity.yaml").exists()
    finally:
        page.close()
        server.stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
