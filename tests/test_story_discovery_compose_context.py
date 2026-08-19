from types import SimpleNamespace

from auteur.story_discovery_compose import _resolve_composition_premise


def test_composition_premise_prefers_declared_author_premise():
    primary = SimpleNamespace(core_answer="Candidate core answer.")
    report = {
        "premise_summary": "Report premise.",
        "declared_author_intent": {"premise": "Declared source premise."},
    }
    assert _resolve_composition_premise(report, primary) == "Declared source premise."


def test_composition_premise_falls_back_without_declared_intent():
    primary = SimpleNamespace(core_answer="Candidate core answer.")
    assert _resolve_composition_premise({"premise_summary": "Report premise."}, primary) == "Report premise."
    assert _resolve_composition_premise({}, primary) == "Candidate core answer."
