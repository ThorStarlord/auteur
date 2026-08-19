"""Phase F1 tests for narrative-architecture preferences.

F1 defines a Layer 0 controlled vocabulary and Layer 1 Identity commitments only.
It must preserve UNKNOWN semantics, survive Story Discovery acceptance, and remain
inert during bounded Identity-to-Structure propagation until later Phase F slices
define behavior.
"""

from copy import deepcopy

import pytest
import yaml

from auteur.blueprint import Genre, StoryMedium, StoryMode, TargetAudience, TargetExperience
from auteur.cli import main
from auteur.identity import HighLevelCentralEngine, StoryIdentity, StoryType, compile_to_blueprint
from auteur.narrative_ontology.architecture_preferences import (
    CausalDistributionPreference,
    ComplexityPreference,
    EngineHierarchyPreference,
    NarrativeArchitecturePreferences,
)
from auteur.narrative_ontology.loader.ontology_loader import OntologyLoader


def _identity(
    preferences: NarrativeArchitecturePreferences | None = None,
) -> StoryIdentity:
    return StoryIdentity(
        title="Architecture Preference Test",
        core_answer="A detective repairs a public lie without losing the people caught inside it.",
        target_experience=TargetExperience(
            primary="moral tension",
            progression="curiosity -> pressure -> bittersweet clarity",
            avoid=[],
        ),
        story_type=StoryType(
            medium=StoryMedium.NOVEL,
            mode=StoryMode.TRAGIC,
            genre=Genre.MYSTERY,
            target_audience=TargetAudience.ADULT,
        ),
        central_engine=HighLevelCentralEngine(
            want="The detective wants to expose the true cause of the scandal.",
            resistance="Powerful institutions protect the useful public explanation.",
            conflict="Every truthful disclosure endangers someone the detective wants to protect.",
            stakes="The public record, innocent lives, and the detective's closest relationship.",
            change="The detective accepts that truthful repair requires choosing which costs to own.",
        ),
        architecture_preferences=preferences,
    )


def test_architecture_preferences_are_layer0_vocabulary_not_base_narrative_concept():
    """Preference dimensions type Identity but are not a 13th in-story entity."""
    loader = OntologyLoader()

    assert len(loader.load_base_ontology()) == 12
    assert loader.get_concept("NarrativeArchitecturePreference") == {}
    assert [value.value for value in ComplexityPreference] == [
        "focused",
        "layered",
        "maximalist",
    ]
    assert [value.value for value in CausalDistributionPreference] == [
        "concentrated",
        "layered",
        "mixed",
    ]
    assert [value.value for value in EngineHierarchyPreference] == [
        "single_center",
        "primary_with_layers",
        "ensemble",
    ]


def test_legacy_story_identity_has_no_hidden_architecture_default():
    identity = _identity()
    payload = identity.model_dump(mode="json")
    payload.pop("architecture_preferences", None)

    loaded = StoryIdentity.model_validate(payload)

    assert loaded.architecture_preferences is None


@pytest.mark.parametrize("value", list(ComplexityPreference))
def test_complexity_values_round_trip(value: ComplexityPreference):
    prefs = NarrativeArchitecturePreferences(complexity=value)
    loaded = NarrativeArchitecturePreferences.model_validate(prefs.model_dump(mode="json"))

    assert loaded.complexity is value
    assert loaded.causal_distribution is None
    assert loaded.engine_hierarchy is None


@pytest.mark.parametrize("value", list(CausalDistributionPreference))
def test_causal_distribution_values_round_trip(value: CausalDistributionPreference):
    prefs = NarrativeArchitecturePreferences(causal_distribution=value)
    loaded = NarrativeArchitecturePreferences.model_validate(prefs.model_dump(mode="json"))

    assert loaded.causal_distribution is value
    assert loaded.complexity is None
    assert loaded.engine_hierarchy is None


@pytest.mark.parametrize("value", list(EngineHierarchyPreference))
def test_engine_hierarchy_values_round_trip(value: EngineHierarchyPreference):
    prefs = NarrativeArchitecturePreferences(engine_hierarchy=value)
    loaded = NarrativeArchitecturePreferences.model_validate(prefs.model_dump(mode="json"))

    assert loaded.engine_hierarchy is value
    assert loaded.complexity is None
    assert loaded.causal_distribution is None


def test_story_identity_yaml_round_trip_preserves_explicit_and_unknown_dimensions():
    identity = _identity(
        NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.MAXIMALIST,
            causal_distribution=CausalDistributionPreference.MIXED,
        )
    )

    serialized = yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False)
    loaded = StoryIdentity.model_validate(yaml.safe_load(serialized))

    assert loaded.architecture_preferences is not None
    assert loaded.architecture_preferences.complexity is ComplexityPreference.MAXIMALIST
    assert (
        loaded.architecture_preferences.causal_distribution
        is CausalDistributionPreference.MIXED
    )
    assert loaded.architecture_preferences.engine_hierarchy is None


def test_story_discovery_accept_preserves_architecture_preferences(tmp_path):
    discovery_dir = tmp_path / "story_discovery"
    discovery_dir.mkdir()
    candidate = discovery_dir / "candidate_1.yaml"
    identity = _identity(
        NarrativeArchitecturePreferences(
            complexity=ComplexityPreference.MAXIMALIST,
            causal_distribution=CausalDistributionPreference.MIXED,
            engine_hierarchy=EngineHierarchyPreference.PRIMARY_WITH_LAYERS,
        )
    )
    candidate.write_text(
        yaml.safe_dump(identity.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )
    (discovery_dir / "discovery_report.yaml").write_text(
        yaml.safe_dump({"chosen_candidate": None}),
        encoding="utf-8",
    )
    output = tmp_path / "story_identity.yaml"

    exit_code = main(
        [
            "story-discovery",
            "accept",
            str(candidate),
            "--output",
            str(output),
            "--keep-candidates",
        ]
    )

    assert exit_code == 0
    promoted = StoryIdentity.model_validate(yaml.safe_load(output.read_text(encoding="utf-8")))
    assert promoted.architecture_preferences is not None
    assert promoted.architecture_preferences.model_dump(mode="json") == {
        "complexity": "maximalist",
        "causal_distribution": "mixed",
        "engine_hierarchy": "primary_with_layers",
    }


def test_architecture_preferences_do_not_propagate_to_blueprint_in_f1():
    baseline = _identity()
    baseline_payload = baseline.model_dump(mode="json")
    with_preferences_payload = deepcopy(baseline_payload)
    with_preferences_payload["architecture_preferences"] = {
        "complexity": "maximalist",
        "causal_distribution": "mixed",
        "engine_hierarchy": "primary_with_layers",
    }
    with_preferences = StoryIdentity.model_validate(with_preferences_payload)

    baseline_blueprint = compile_to_blueprint(baseline)
    preference_blueprint = compile_to_blueprint(with_preferences)

    assert preference_blueprint.model_dump(mode="json") == baseline_blueprint.model_dump(
        mode="json"
    )
    assert with_preferences.architecture_preferences is not None
    assert baseline.architecture_preferences is None
