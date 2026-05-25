"""Tests for structure generator — top-down synthesis and bottom-up symptom diagnosis.

RED: These tests are the first coverage for generator.py. They must pass before
any refactoring of the generation or symptom-diagnosis code.
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from auteur.blueprint import (
    Character,
    CharacterRole,
    StoryBlueprint,
    TargetExperience,
    ThreadType,
)
from auteur.identity import StoryIdentity
from auteur.structure.diagnostics import DiagnosticLayer, DiagnosticSeverity
from auteur.structure.generator import (
    GenerationProposal,
    StructuralForcesSynthesis,
    SymptomDiagnosis,
    _extract_carrier_names,
    diagnose_symptom,
    generate_main_thread,
    generate_story_engine,
    generate_subordinate_threads,
    synthesize_structural_forces,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_MINIMAL_BLUEPRINT_DATA: dict = {
    "identity": {
        "title": "The Long Road",
        "author_intent": "A war veteran seeks redemption after betraying his unit.",
        "length_class": "novel",
        "genre": "literary",
        "mode": "tragic",
        "target_audience": "adult",
        "pov_type": "third_person_limited_single",
        "target_experience": {
            "primary": "catharsis",
            "progression": "guilt -> confrontation -> acceptance",
        },
    },
    "contract": {
        "content_rating": "R",
        "mandatory_ending_tone": "bittersweet",
    },
    "emotional_design": {
        "overall_emotional_arc": "guilt -> confrontation -> acceptance",
    },
    "theme": {
        "central_question": "Can a person be forgiven for a cowardly act they cannot undo?",
        "thesis": "Redemption is possible only when the self-lie is dismantled.",
        "motifs": ["silence", "uniforms", "maps"],
    },
    "characters": [
        {
            "name": "Kael",
            "role": "protagonist",
            "arc_type": "growth",
            "arc_start_percentage": 0,
            "arc_end_percentage": 100,
        },
        {
            "name": "Malachai",
            "role": "antagonist",
            "arc_type": "fall",
            "arc_start_percentage": 0,
            "arc_end_percentage": 80,
        },
    ],
}


@pytest.fixture
def blueprint() -> StoryBlueprint:
    return StoryBlueprint.model_validate(_MINIMAL_BLUEPRINT_DATA)


@pytest.fixture
def blueprint_no_target_exp() -> StoryBlueprint:
    data = deepcopy(_MINIMAL_BLUEPRINT_DATA)
    del data["identity"]["target_experience"]
    return StoryBlueprint.model_validate(data)


@pytest.fixture
def blueprint_no_characters() -> StoryBlueprint:
    data = deepcopy(_MINIMAL_BLUEPRINT_DATA)
    data["characters"] = []
    return StoryBlueprint.model_validate(data)


# ---------------------------------------------------------------------------
# Tests: synthesize_structural_forces
# ---------------------------------------------------------------------------


class TestSynthesizeStructuralForces:
    def test_returns_forces_with_valid_blueprint(self, blueprint: StoryBlueprint) -> None:
        forces = synthesize_structural_forces(blueprint)
        assert isinstance(forces, StructuralForcesSynthesis)
        assert forces.want
        assert forces.resistance
        assert forces.conflict
        assert forces.stakes
        assert forces.change

    def test_returns_none_when_no_target_experience(self, blueprint_no_target_exp: StoryBlueprint) -> None:
        forces = synthesize_structural_forces(blueprint_no_target_exp)
        assert forces is None

    def test_catharsis_literary_known_fallback(self, blueprint: StoryBlueprint) -> None:
        forces = synthesize_structural_forces(blueprint)
        assert forces is not None
        assert "closure" in forces.want.casefold() or "acceptance" in forces.want.casefold()

    def test_dread_thriller_pair(self) -> None:
        data = deepcopy(_MINIMAL_BLUEPRINT_DATA)
        data["identity"]["genre"] = "thriller"
        data["identity"]["target_experience"] = {"primary": "dread", "progression": "tension -> dread"}
        bp = StoryBlueprint.model_validate(data)
        forces = synthesize_structural_forces(bp)
        assert forces is not None
        assert "stop the threat" in forces.want.casefold()
        assert "one step ahead" in forces.resistance

    def test_unknown_feeling_falls_back_to_generic(self) -> None:
        data = deepcopy(_MINIMAL_BLUEPRINT_DATA)
        data["identity"]["target_experience"] = {"primary": "nostalgia", "progression": "warmth -> melancholy"}
        bp = StoryBlueprint.model_validate(data)
        forces = synthesize_structural_forces(bp)
        assert forces is not None
        assert forces.rationale

    def test_rationale_includes_genre_and_target_experience(self, blueprint: StoryBlueprint) -> None:
        forces = synthesize_structural_forces(blueprint)
        assert forces is not None
        assert "catharsis" in forces.rationale
        assert "literary" in forces.rationale


# ---------------------------------------------------------------------------
# Tests: generate_main_thread
# ---------------------------------------------------------------------------


class TestGenerateMainThread:
    def test_uses_protagonist_name(self) -> None:
        data = deepcopy(_MINIMAL_BLUEPRINT_DATA)
        bp = StoryBlueprint.model_validate(data)
        forces = StructuralForcesSynthesis(
            want="the protagonist seeks redemption",
            resistance="The past will not release its grip",
            conflict="Facing the past shatters the present illusion",
            stakes="Identity and peace",
            change="The protagonist integrates the past into a coherent self",
            rationale="Test.",
        )
        thread = generate_main_thread(bp, forces)
        assert "Kael" in thread.want
        assert thread.thread_type == ThreadType.MAIN_PLOT
        assert thread.carriers == ["Kael"]
        assert thread.confidence == 0.95

    def test_fallback_protagonist_name(self) -> None:
        data = deepcopy(_MINIMAL_BLUEPRINT_DATA)
        data["characters"] = []
        bp = StoryBlueprint.model_validate(data)
        forces = StructuralForcesSynthesis(
            want="the protagonist achieves a positive outcome",
            resistance="Circumstance and doubt block the way",
            conflict="Success requires sacrificing something equally important",
            stakes="The dream and the self",
            change="The protagonist redefines what success means",
            rationale="Generic fallback.",
        )
        thread = generate_main_thread(bp, forces)
        assert "the protagonist" in thread.want


# ---------------------------------------------------------------------------
# Tests: generate_subordinate_threads
# ---------------------------------------------------------------------------


class TestGenerateSubordinateThreads:
    def test_generates_character_arc_for_protagonist(self, blueprint: StoryBlueprint) -> None:
        forces = synthesize_structural_forces(blueprint)
        assert forces is not None
        main = generate_main_thread(blueprint, forces)
        threads = generate_subordinate_threads(blueprint, forces, main)
        arc_threads = [t for t in threads if t.thread_type == ThreadType.CHARACTER_ARC]
        assert len(arc_threads) >= 1
        assert "Kael" in arc_threads[0].name

    def test_generates_relationship_arcs_for_primary_pairs(self, blueprint: StoryBlueprint) -> None:
        forces = synthesize_structural_forces(blueprint)
        assert forces is not None
        main = generate_main_thread(blueprint, forces)
        threads = generate_subordinate_threads(blueprint, forces, main)
        rel_threads = [t for t in threads if t.thread_type == ThreadType.RELATIONSHIP_ARC]
        assert len(rel_threads) >= 1
        rivalry_threads = [t for t in rel_threads if "rivalry" in t.name]
        assert len(rivalry_threads) >= 1

    def test_generates_thematic_echo(self, blueprint: StoryBlueprint) -> None:
        forces = synthesize_structural_forces(blueprint)
        assert forces is not None
        main = generate_main_thread(blueprint, forces)
        threads = generate_subordinate_threads(blueprint, forces, main)
        echo_threads = [t for t in threads if t.thread_type == ThreadType.THEMATIC_ECHO]
        assert len(echo_threads) == 1
        assert echo_threads[0].name == "thematic_echo"

    def test_generates_antagonist_pressure_thread(self, blueprint: StoryBlueprint) -> None:
        forces = synthesize_structural_forces(blueprint)
        assert forces is not None
        main = generate_main_thread(blueprint, forces)
        threads = generate_subordinate_threads(blueprint, forces, main)
        ant_threads = [t for t in threads if "pressure" in t.name]
        assert len(ant_threads) >= 1
        assert "Malachai" in ant_threads[0].name


# ---------------------------------------------------------------------------
# Tests: generate_story_engine
# ---------------------------------------------------------------------------


class TestGenerateStoryEngine:
    def test_returns_proposal_with_valid_blueprint(self, blueprint: StoryBlueprint) -> None:
        result = generate_story_engine(blueprint)
        assert isinstance(result, GenerationProposal)
        assert result.main_thread.thread_type == ThreadType.MAIN_PLOT
        assert len(result.subordinate_threads) >= 1
        assert result.generation_method == "target-experience-driven"

    def test_returns_diagnostics_when_no_target_experience(self, blueprint_no_target_exp: StoryBlueprint) -> None:
        result = generate_story_engine(blueprint_no_target_exp)
        assert isinstance(result, list)
        assert any(d.rule == "target_experience_required_for_generation" for d in result)

    def test_returns_diagnostics_when_no_characters(self, blueprint_no_characters: StoryBlueprint) -> None:
        result = generate_story_engine(blueprint_no_characters)
        assert isinstance(result, list)
        assert any(d.rule == "characters_required_for_generation" for d in result)

    def test_potential_issues_are_listed(self, blueprint: StoryBlueprint) -> None:
        result = generate_story_engine(blueprint)
        assert isinstance(result, GenerationProposal)
        assert len(result.potential_issues) > 0

    def test_constraints_honored_includes_genre(self, blueprint: StoryBlueprint) -> None:
        result = generate_story_engine(blueprint)
        assert isinstance(result, GenerationProposal)
        genre_entry = [c for c in result.constraints_honored if "Genre" in c]
        assert len(genre_entry) == 1
        assert "literary" in genre_entry[0]


# ---------------------------------------------------------------------------
# Tests: diagnose_symptom
# ---------------------------------------------------------------------------


class TestDiagnoseSymptom:
    def test_midpoint_symptom_matches_threads_layer(self) -> None:
        results = diagnose_symptom("The midpoint feels flat")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.THREADS

    def test_stakes_symptom_matches_structural_forces(self) -> None:
        results = diagnose_symptom("The stakes feel too low")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.STRUCTURAL_FORCES

    def test_ending_symptom_matches_structural_forces(self) -> None:
        results = diagnose_symptom("The ending fizzles")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.STRUCTURAL_FORCES

    def test_character_symptom_matches_carriers(self) -> None:
        results = diagnose_symptom("The characters feel thin and cardboard")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.CARRIERS

    def test_multiple_keywords_boost_one_result(self) -> None:
        results = diagnose_symptom("The midpoint sags and the pacing is slow")
        assert len(results) >= 1
        thread_matches = [r for r in results if r.likely_layer == DiagnosticLayer.THREADS]
        assert len(thread_matches) >= 1

    def test_pacing_symptom_matches_scope(self) -> None:
        results = diagnose_symptom("The pacing is uneven and feels rushed")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.SCOPE

    def test_subplot_symptom_matches_threads(self) -> None:
        results = diagnose_symptom("The subplot goes nowhere")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.THREADS

    def test_world_symptom_matches_constraints(self) -> None:
        results = diagnose_symptom("The world feels generic")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.CONSTRAINTS

    def test_theme_symptom_matches_theme(self) -> None:
        results = diagnose_symptom("The theme is shallow and preachy")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.THEME

    def test_tone_symptom_matches_target_experience(self) -> None:
        results = diagnose_symptom("The tone is confused and gives emotional whiplash")
        assert len(results) >= 1
        assert results[0].likely_layer == DiagnosticLayer.TARGET_EXPERIENCE

    def test_unknown_symptom_returns_fallback(self) -> None:
        results = diagnose_symptom("The prose is purple")
        assert len(results) == 1
        assert "does not match" in results[0].root_cause_hypothesis

    def test_empty_symptom_returns_fallback(self) -> None:
        results = diagnose_symptom("")
        assert len(results) == 1

    def test_symptom_diagnosis_has_expected_fields(self) -> None:
        results = diagnose_symptom("Stakes are low")
        d = results[0]
        assert isinstance(d, SymptomDiagnosis)
        assert d.symptom
        assert d.likely_layer
        assert d.root_cause_hypothesis
        assert d.recommendation

    def test_alternative_hypotheses_are_listed(self) -> None:
        results = diagnose_symptom("Stakes are low")
        d = results[0]
        assert len(d.alternative_hypotheses) > 0


# ---------------------------------------------------------------------------
# Tests: _extract_carrier_names
# ---------------------------------------------------------------------------


class TestExtractCarrierNames:
    def test_extracts_all_character_names(self, blueprint: StoryBlueprint) -> None:
        carriers = _extract_carrier_names(blueprint)
        assert "Kael" in carriers
        assert "Malachai" in carriers

    def test_adds_faction_for_antagonist(self, blueprint: StoryBlueprint) -> None:
        carriers = _extract_carrier_names(blueprint)
        assert "Malachai_faction" in carriers

    def test_adds_circle_for_deuteragonist(self) -> None:
        data = deepcopy(_MINIMAL_BLUEPRINT_DATA)
        data["characters"].append({"name": "Lira", "role": "deuteragonist", "arc_type": "growth", "arc_start_percentage": 0, "arc_end_percentage": 100})
        data["identity"]["target_experience"] = {"primary": "hope", "progression": "loss -> hope"}
        bp = StoryBlueprint.model_validate(data)
        carriers = _extract_carrier_names(bp)
        assert "Lira_circle" in carriers

    def test_returns_empty_for_no_characters(self) -> None:
        data = dict(_MINIMAL_BLUEPRINT_DATA)
        del data["identity"]["target_experience"]
        data["characters"] = []
        bp = StoryBlueprint.model_validate(data)
        carriers = _extract_carrier_names(bp)
        assert carriers == []
