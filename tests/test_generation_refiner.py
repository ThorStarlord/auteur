"""Tests for generation_refiner — LLM bridge for the generative path.
"""
from __future__ import annotations

import pytest
import yaml

from auteur.blueprint import (
    StoryBlueprint,
    TargetExperience,
    ThreadType,
)
from auteur.llm import LLMResponse
from auteur.llm.fake import FakeClient
from auteur.structure.generation_refiner import (
    build_refinement_prompt,
    llm_refine_story_engine,
    parse_refinement_response,
)
from auteur.structure.generator import (
    GenerationProposal,
    StructuralForcesSynthesis,
    generate_story_engine,
)

_MINIMAL_DATA: dict = {
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
    ],
}

_REFINED_YAML = """\
structural_forces:
  want: Kael must face the truth of the betrayal he buried
  resistance: His former commander protects the lie that destroyed their unit
  conflict: Seeking redemption forces Kael to betray the survivors he swore to protect
  stakes: Kael's soul and the last shred of his family name
  change: Kael learns that redemption costs more than guilt could ever extract
main_thread:
  name: main_plot
  thread_type: main_plot
  want: Kael wants to uncover what really happened at the siege
  function: Drives causality, escalation, and the primary emotional arc
  carriers:
    - Kael
  confidence: 0.95
  rationale: Kael's search for truth drives every major plot turn.
subordinate_threads:
  - name: Kael_arc
    thread_type: character_arc
    want: Kael must reckon with the gap between the man he was and the man he became
    function: pressures_change
    carriers:
      - Kael
    confidence: 0.85
    rationale: Tracks Kael's internal transformation from denial to acceptance.
constraints_honored:
  - "Target experience: catharsis"
  - "Genre: literary"
"""


@pytest.fixture
def blueprint() -> StoryBlueprint:
    return StoryBlueprint.model_validate(_MINIMAL_DATA)


class TestBuildRefinementPrompt:
    def test_includes_title_and_intent(self, blueprint: StoryBlueprint) -> None:
        prompt = build_refinement_prompt(blueprint)
        assert "The Long Road" in prompt
        assert "betraying his unit" in prompt

    def test_includes_character_names(self, blueprint: StoryBlueprint) -> None:
        prompt = build_refinement_prompt(blueprint)
        assert "Kael" in prompt

    def test_includes_archetypal_forces_when_provided(self, blueprint: StoryBlueprint) -> None:
        forces = StructuralForcesSynthesis(
            want="To find closure",
            resistance="The past resists integration",
            conflict="Holding on prevents healing",
            stakes="Identity and peace",
            change="The protagonist carries loss differently",
            rationale="Test rationale.",
        )
        prompt = build_refinement_prompt(blueprint, forces)
        assert "To find closure" in prompt

    def test_includes_theme(self, blueprint: StoryBlueprint) -> None:
        prompt = build_refinement_prompt(blueprint)
        assert "self-lie" in prompt


class TestParseRefinementResponse:
    def test_parses_clean_yaml(self) -> None:
        data = parse_refinement_response(_REFINED_YAML)
        assert "structural_forces" in data
        assert "main_thread" in data
        assert "subordinate_threads" in data

    def test_parses_yaml_with_fences(self) -> None:
        text = f"```yaml\n{_REFINED_YAML}\n```"
        data = parse_refinement_response(text)
        assert "structural_forces" in data

    def test_parses_yaml_with_bare_fences(self) -> None:
        text = f"```\n{_REFINED_YAML}\n```"
        data = parse_refinement_response(text)
        assert "structural_forces" in data

    def test_raises_on_invalid_yaml(self) -> None:
        with pytest.raises((ValueError, yaml.YAMLError)):
            parse_refinement_response("{{invalid: yaml: {{{")


class TestLlmRefineStoryEngine:
    def test_llm_refines_forces_and_threads(self, blueprint: StoryBlueprint) -> None:
        fake = FakeClient([LLMResponse(text=_REFINED_YAML, input_tokens=100, output_tokens=200)])
        result = llm_refine_story_engine(blueprint, fake)
        assert isinstance(result, GenerationProposal)
        assert "Kael" in result.structural_forces.want
        assert result.generation_method == "llm-refined"

    def test_falls_back_on_llm_failure(self, blueprint: StoryBlueprint) -> None:
        from auteur.llm import RetriableError
        fake = FakeClient([RetriableError("LLM unavailable")])
        result = llm_refine_story_engine(blueprint, fake)
        assert isinstance(result, GenerationProposal)
        assert result.generation_method == "target-experience-driven"

    def test_falls_back_on_parse_failure(self, blueprint: StoryBlueprint) -> None:
        fake = FakeClient([LLMResponse(text="{{ bad yaml }}", input_tokens=10, output_tokens=5)])
        result = llm_refine_story_engine(blueprint, fake)
        assert isinstance(result, GenerationProposal)

    def test_preserves_potential_issues_on_fallback(self, blueprint: StoryBlueprint) -> None:
        fake = FakeClient([LLMResponse(text="{{ bad yaml }}", input_tokens=10, output_tokens=5)])
        result = llm_refine_story_engine(blueprint, fake)
        assert len(result.potential_issues) > 0

    def test_subordinate_threads_are_refined(self, blueprint: StoryBlueprint) -> None:
        fake = FakeClient([LLMResponse(text=_REFINED_YAML, input_tokens=100, output_tokens=200)])
        result = llm_refine_story_engine(blueprint, fake)
        assert len(result.subordinate_threads) >= 1
        assert result.subordinate_threads[0].carriers == ["Kael"]

    def test_llm_is_called_with_system_prompt(self, blueprint: StoryBlueprint) -> None:
        fake = FakeClient([LLMResponse(text=_REFINED_YAML, input_tokens=100, output_tokens=200)])
        llm_refine_story_engine(blueprint, fake)
        assert len(fake.calls) == 1
        assert fake.calls[0].system
        assert "story structure refiner" in fake.calls[0].system.casefold()


class TestGenerateStoryEngineWithLLM:
    def test_generate_with_llm_refines_proposal(self, blueprint: StoryBlueprint) -> None:
        fake = FakeClient([LLMResponse(text=_REFINED_YAML, input_tokens=100, output_tokens=200)])
        result = generate_story_engine(blueprint, llm=fake)
        assert isinstance(result, GenerationProposal)
        assert result.generation_method == "llm-refined"

    def test_generate_without_llm_uses_templates(self, blueprint: StoryBlueprint) -> None:
        result = generate_story_engine(blueprint)
        assert isinstance(result, GenerationProposal)
        assert result.generation_method == "target-experience-driven"
