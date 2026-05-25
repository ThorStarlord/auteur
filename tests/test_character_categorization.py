"""Tests for character categorization: enums, models, analyzer, categorizer, and CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from auteur.blueprint import (
    ArcMilestone,
    ArcType,
    Character,
    CharacterRole,
    CharacterState,
    Relationship,
    StoryBlueprint,
)
from auteur.character.analyzer import analyze_character_categorization
from auteur.character.categorizer import CategorizationEngine
from auteur.character.cli import handle_character_command
from auteur.character.enums import (
    Archetype,
    DramaticFunction,
    MoralAlignment,
    PersonalityTrait,
    ProtagonistSubtype,
    RelationshipType,
    TropeTag,
    Vice,
    Virtue,
)
from auteur.character.models import (
    CharacterCategorization,
    CharacterIdentity,
    RelationshipSignature,
    RoleInference,
    ThematicAlignment,
)


# ============================================================================
# Enum tests
# ============================================================================


def test_archetype_enum_values():
    assert Archetype.HERO.value == "hero"
    assert Archetype.VILLAIN.value == "villain"
    assert Archetype.MENTOR.value == "mentor"
    assert Archetype.SHADOW.value == "shadow"


def test_moral_alignment_enum_values():
    assert MoralAlignment.LAWFUL_GOOD.value == "lawful_good"
    assert MoralAlignment.CHAOTIC_EVIL.value == "chaotic_evil"


def test_virtue_enum_values():
    assert Virtue.JUSTICE.value == "justice"
    assert Virtue.COURAGE.value == "courage"


def test_vice_enum_values():
    assert Vice.GREED.value == "greed"
    assert Vice.PRIDE.value == "pride"


def test_personality_trait_enum_values():
    assert PersonalityTrait.OPEN_CURIOUS.value == "open_curious"
    assert PersonalityTrait.STABLE_CONFIDENT.value == "stable_confident"


def test_protagonist_subtype_enum_values():
    assert ProtagonistSubtype.CLASSIC_HERO.value == "classic_hero"
    assert ProtagonistSubtype.ANTI_HERO.value == "anti_hero"


def test_dramatic_function_enum_values():
    assert DramaticFunction.EMOTIONAL_ANCHOR.value == "emotional_anchor"
    assert DramaticFunction.COMIC_RELIEF.value == "comic_relief"


def test_trope_tag_enum_values():
    assert TropeTag.CHOSEN_ONE.value == "chosen_one"
    assert TropeTag.MENTOR_DEATH.value == "mentor_death"


def test_relationship_type_enum_values():
    assert RelationshipType.TRUST.value == "trust"
    assert RelationshipType.RIVALRY.value == "rivalry"
    assert RelationshipType.MENTORSHIP.value == "mentorship"


# ============================================================================
# Model tests
# ============================================================================


def test_character_identity_defaults():
    identity = CharacterIdentity()
    assert identity.archetype is None
    assert identity.moral_alignment is None
    assert identity.dramatic_functions == []
    assert identity.trope_tags == []


def test_character_identity_full():
    identity = CharacterIdentity(
        archetype=Archetype.TRAGIC_HERO,
        moral_alignment=MoralAlignment.CHAOTIC_GOOD,
        virtues=[Virtue.COURAGE, Virtue.JUSTICE],
        vices=[Vice.PRIDE],
        personality_traits=[PersonalityTrait.NEUROTIC_SENSITIVE],
        dramatic_functions=[DramaticFunction.EMOTIONAL_ANCHOR],
        trope_tags=[TropeTag.FALLEN_HERO],
        custom_tags=["doomed", "rebel"],
    )
    assert identity.archetype == Archetype.TRAGIC_HERO
    assert identity.moral_alignment == MoralAlignment.CHAOTIC_GOOD
    assert len(identity.virtues) == 2
    assert len(identity.vices) == 1
    assert len(identity.personality_traits) == 1
    assert identity.custom_tags == ["doomed", "rebel"]


def test_character_identity_roundtrip():
    identity = CharacterIdentity(
        archetype=Archetype.MENTOR,
        moral_alignment=MoralAlignment.LAWFUL_GOOD,
        dramatic_functions=[DramaticFunction.VOICE_OF_REASON],
    )
    data = identity.model_dump(mode="json")
    restored = CharacterIdentity.model_validate(data)
    assert restored.archetype == Archetype.MENTOR
    assert restored.moral_alignment == MoralAlignment.LAWFUL_GOOD


def test_relationship_signature():
    sig = RelationshipSignature(other="Kael", type=RelationshipType.RIVALRY, intensity=0.8)
    assert sig.other == "Kael"
    assert sig.type == RelationshipType.RIVALRY
    assert sig.intensity == 0.8


def test_thematic_alignment():
    ta = ThematicAlignment(theme="redemption", stance="embodies")
    assert ta.theme == "redemption"
    assert ta.stance == "embodies"


def test_role_inference():
    ri = RoleInference(inferred_role="social_hub", confidence=0.7, evidence=["Has 3 relationships."])
    assert ri.inferred_role == "social_hub"
    assert ri.confidence == 0.7


def test_character_categorization_defaults():
    cat = CharacterCategorization()
    assert cat.identity.archetype is None
    assert cat.relationship_signatures == []
    assert cat.role_inferences == []


# ============================================================================
# Character model integration tests
# ============================================================================


def test_character_identity_field_is_optional():
    char = Character(name="Kael", role=CharacterRole.PROTAGONIST, arc_type=ArcType.GROWTH,
                     arc_start_percentage=0, arc_end_percentage=100)
    assert char.identity is None


def test_character_identity_field_accepts_dict():
    char = Character(
        name="Kael",
        role=CharacterRole.PROTAGONIST,
        arc_type=ArcType.GROWTH,
        arc_start_percentage=0,
        arc_end_percentage=100,
        identity={"archetype": "hero", "moral_alignment": "neutral_good"},
    )
    assert char.identity is not None
    assert char.identity["archetype"] == "hero"


def test_character_with_identity_roundtrip_through_blueprint():
    bp_data = {
        "identity": {
            "title": "Test",
            "author_intent": "Test.",
            "length_class": "novella",
            "genre": "epic_fantasy",
            "medium": "novella",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG",
            "mandatory_ending_tone": "hopeful",
        },
        "emotional_design": {"overall_emotional_arc": "rise"},
        "theme": {"central_question": "?", "thesis": "."},
        "characters": [
            {
                "name": "Kael",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "identity": {
                    "archetype": "tragic_hero",
                    "moral_alignment": "chaotic_good",
                    "dramatic_functions": ["emotional_anchor"],
                },
            }
        ],
    }
    bp = StoryBlueprint.model_validate(bp_data)
    assert len(bp.characters) == 1
    assert bp.characters[0].identity is not None
    identity_data = bp.characters[0].identity
    assert identity_data["archetype"] == "tragic_hero"
    assert identity_data["moral_alignment"] == "chaotic_good"


def test_character_categorization_field():
    char = Character(
        name="Kael",
        role=CharacterRole.PROTAGONIST,
        arc_type=ArcType.GROWTH,
        arc_start_percentage=0,
        arc_end_percentage=100,
        categorization={
            "identity": {"archetype": "hero"},
            "relationship_signatures": [{"other": "Vlak", "type": "rivalry", "intensity": 0.9}],
        },
    )
    assert char.categorization is not None
    assert char.categorization["identity"]["archetype"] == "hero"


# ============================================================================
# Analyzer tests
# ============================================================================


def _minimal_blueprint_data(**overrides: object) -> dict:
    data = {
        "identity": {
            "title": "Test Story",
            "author_intent": "A test premise.",
            "length_class": "novel",
            "genre": "epic_fantasy",
            "medium": "novel",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG",
            "mandatory_ending_tone": "hopeful",
        },
        "emotional_design": {"overall_emotional_arc": "rise"},
        "theme": {"central_question": "?", "thesis": "."},
        **overrides,
    }
    return data


def test_analyzer_empty_characters():
    data = _minimal_blueprint_data()
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "characters.missing" for d in diagnostics)


def test_analyzer_missing_identity_warning():
    data = _minimal_blueprint_data(
        characters=[
            {
                "name": "Kael",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
            }
        ]
    )
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.identity.missing" for d in diagnostics)


def test_analyzer_missing_archetype_for_primary_role():
    data = _minimal_blueprint_data(
        characters=[
            {
                "name": "Kael",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "identity": {
                    "moral_alignment": "neutral_good",
                },
            }
        ]
    )
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.archetype.missing_for_primary_role" for d in diagnostics)


def test_analyzer_no_antagonist_warning():
    data = _minimal_blueprint_data(
        characters=[
            {
                "name": "Kael",
                "role": "ally",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
            }
        ]
    )
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "characters.no_antagonist" for d in diagnostics)


def test_analyzer_clean_with_full_identity():
    data = _minimal_blueprint_data(
        characters=[
            {
                "name": "Kael",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "identity": {
                    "archetype": "hero",
                    "moral_alignment": "neutral_good",
                    "dramatic_functions": ["emotional_anchor"],
                },
            },
            {
                "name": "Vlak",
                "role": "antagonist",
                "arc_type": "corruption",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "identity": {
                    "archetype": "villain",
                    "moral_alignment": "neutral_evil",
                    "dramatic_functions": ["ideological_opposition"],
                },
            },
        ]
    )
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    identity_missing = [d for d in diagnostics if d.rule == "character.identity.missing"]
    assert len(identity_missing) == 0


# ============================================================================
# Categorizer tests
# ============================================================================


def _make_char(name: str, role: CharacterRole, arc: ArcType = ArcType.GROWTH,
               identity: dict | None = None, relationships: list | None = None) -> Character:
    return Character(
        name=name,
        role=role,
        arc_type=arc,
        arc_start_percentage=0,
        arc_end_percentage=100,
        identity=identity,
        current_state=CharacterState(
            relationships=[Relationship(**r) for r in (relationships or [])],
        ),
    )


def _make_blueprint(chars: list[Character]) -> StoryBlueprint:
    data = _minimal_blueprint_data()
    bp = StoryBlueprint.model_validate(data)
    bp.characters = chars
    return bp


def test_categorizer_suggests_archetype_by_role():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
        _make_char("Old Man", CharacterRole.MENTOR),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.archetype == Archetype.HERO
    assert cats["Vlak"].identity.archetype == Archetype.VILLAIN
    assert cats["Old Man"].identity.archetype == Archetype.MENTOR


def test_categorizer_suggests_alignment_by_role():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.moral_alignment == MoralAlignment.NEUTRAL_GOOD
    assert cats["Vlak"].identity.moral_alignment == MoralAlignment.NEUTRAL_EVIL


def test_categorizer_suggests_dramatic_functions():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert DramaticFunction.EMOTIONAL_ANCHOR in cats["Kael"].identity.dramatic_functions
    assert DramaticFunction.IDEOLOGICAL_OPPOSITION in cats["Vlak"].identity.dramatic_functions


def test_categorizer_infers_relationship_signatures():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST, relationships=[
            {"other": "Vlak", "kind": "rivalry", "intensity": 0.9},
            {"other": "Old Man", "kind": "mentorship", "intensity": 0.7},
        ]),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    sigs = cats["Kael"].relationship_signatures
    assert len(sigs) == 2
    assert sigs[0].type == RelationshipType.RIVALRY
    assert sigs[1].type == RelationshipType.MENTORSHIP


def test_categorizer_suggests_trope_tags_by_arc():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST, arc=ArcType.CORRUPTION),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert TropeTag.CORRUPTION_ARC in cats["Kael"].identity.trope_tags


def test_categorizer_infers_social_hub_role():
    bp = _make_blueprint([
        _make_char("Hub", CharacterRole.SUPPORTING, relationships=[
            {"other": "A", "kind": "friend", "intensity": 0.8},
            {"other": "B", "kind": "friend", "intensity": 0.9},
            {"other": "C", "kind": "ally", "intensity": 0.7},
        ]),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert len(cats["Hub"].role_inferences) > 0


def test_categorizer_returns_dict_for_all_characters():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
        _make_char("Side", CharacterRole.SUPPORTING),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert set(cats.keys()) == {"Kael", "Vlak", "Side"}


# ============================================================================
# CLI tests
# ============================================================================


def _make_blueprint_yaml(tmp_path: Path, chars: list[dict]) -> Path:
    data = _minimal_blueprint_data(characters=chars)
    path = tmp_path / "blueprint.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


class _MockArgs:
    def __init__(self, **kwargs):
        self.character_command = "show"
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_cli_character_show_no_characters(tmp_path, capsys):
    bp_path = _make_blueprint_yaml(tmp_path, [])
    args = _MockArgs(blueprint=bp_path, output=None)
    rc = handle_character_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    report = json.loads(out)
    assert report["characters"] == []


def test_cli_character_show_with_characters(tmp_path, capsys):
    chars = [
        {
            "name": "Kael",
            "role": "protagonist",
            "arc_type": "growth",
            "arc_start_percentage": 0,
            "arc_end_percentage": 100,
        }
    ]
    bp_path = _make_blueprint_yaml(tmp_path, chars)
    args = _MockArgs(blueprint=bp_path, output=None)
    rc = handle_character_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    report = json.loads(out)
    assert len(report["characters"]) == 1
    assert report["characters"][0]["name"] == "Kael"


def test_cli_character_show_identity(tmp_path, capsys):
    chars = [
        {
            "name": "Kael",
            "role": "protagonist",
            "arc_type": "growth",
            "arc_start_percentage": 0,
            "arc_end_percentage": 100,
            "identity": {
                "archetype": "hero",
                "moral_alignment": "neutral_good",
                "dramatic_functions": ["emotional_anchor"],
                "trope_tags": ["chosen_one"],
            },
        }
    ]
    bp_path = _make_blueprint_yaml(tmp_path, chars)
    args = _MockArgs(blueprint=bp_path, output=None)
    rc = handle_character_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    report = json.loads(out)
    identity = report["characters"][0]["identity"]
    assert identity["archetype"] == "hero"
    assert identity["moral_alignment"] == "neutral_good"
    assert "emotional_anchor" in identity["dramatic_functions"]
    assert "chosen_one" in identity["trope_tags"]


def test_cli_character_diagnose(tmp_path, capsys):
    bp_path = _make_blueprint_yaml(tmp_path, [])
    args = _MockArgs(blueprint=bp_path, output=None, character_command="diagnose")
    rc = handle_character_command(args)
    assert rc == 0


def test_cli_character_categorize(tmp_path, capsys):
    chars = [
        {
            "name": "Kael",
            "role": "protagonist",
            "arc_type": "growth",
            "arc_start_percentage": 0,
            "arc_end_percentage": 100,
        }
    ]
    bp_path = _make_blueprint_yaml(tmp_path, chars)
    args = _MockArgs(blueprint=bp_path, character_command="categorize")
    rc = handle_character_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    cats = json.loads(out)
    assert "Kael" in cats
    assert cats["Kael"]["identity"]["archetype"] == "hero"


def test_cli_character_show_writes_to_output(tmp_path):
    chars = [
        {
            "name": "Kael",
            "role": "protagonist",
            "arc_type": "growth",
            "arc_start_percentage": 0,
            "arc_end_percentage": 100,
        }
    ]
    bp_path = _make_blueprint_yaml(tmp_path, chars)
    out_path = tmp_path / "report.json"
    args = _MockArgs(blueprint=bp_path, output=out_path, character_command="show")
    rc = handle_character_command(args)
    assert rc == 0
    assert out_path.exists()
    report = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(report["characters"]) == 1


def test_cli_character_show_missing_blueprint(tmp_path, capsys):
    args = _MockArgs(blueprint=tmp_path / "nonexistent.yaml", output=None, character_command="show")
    rc = handle_character_command(args)
    assert rc == 1


# ============================================================================
# Integration: Identity roundtrip through blueprint YAML serialization
# ============================================================================


def test_identity_serialization_roundtrip(tmp_path):
    bp_data = _minimal_blueprint_data(
        characters=[
            {
                "name": "Kael",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "identity": {
                    "archetype": "tragic_hero",
                    "moral_alignment": "chaotic_good",
                    "virtues": ["courage", "justice"],
                    "vices": ["pride"],
                    "dramatic_functions": ["emotional_anchor", "audience_surrogate"],
                    "trope_tags": ["fallen_hero", "dark_past"],
                },
            }
        ]
    )
    bp = StoryBlueprint.model_validate(bp_data)
    serialized = yaml.safe_dump(bp.model_dump(mode="json"))
    loaded_data = yaml.safe_load(serialized)
    restored = StoryBlueprint.model_validate(loaded_data)
    assert restored.characters[0].identity["archetype"] == "tragic_hero"
    assert restored.characters[0].identity["moral_alignment"] == "chaotic_good"
    assert "courage" in restored.characters[0].identity["virtues"]
    assert "emotional_anchor" in restored.characters[0].identity["dramatic_functions"]
    assert "fallen_hero" in restored.characters[0].identity["trope_tags"]


def test_categorization_field_serialization_roundtrip(tmp_path):
    bp_data = _minimal_blueprint_data(
        characters=[
            {
                "name": "Kael",
                "role": "protagonist",
                "arc_type": "growth",
                "arc_start_percentage": 0,
                "arc_end_percentage": 100,
                "categorization": {
                    "identity": {"archetype": "hero"},
                    "relationship_signatures": [
                        {"other": "Vlak", "type": "rivalry", "intensity": 0.9}
                    ],
                },
            }
        ]
    )
    bp = StoryBlueprint.model_validate(bp_data)
    serialized = yaml.safe_dump(bp.model_dump(mode="json"))
    loaded_data = yaml.safe_load(serialized)
    restored = StoryBlueprint.model_validate(loaded_data)
    assert restored.characters[0].categorization is not None
    cat = restored.characters[0].categorization
    assert cat["identity"]["archetype"] == "hero"
    assert cat["relationship_signatures"][0]["other"] == "Vlak"
