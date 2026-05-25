"""Tests for layered character categorization: enums, models, analyzer, categorizer, CLI."""

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
    ArcChange,
    ArcEngine,
    ArchetypalLayer,
    CharacterCategorization,
    CharacterIdentity,
    PsychologicalLayer,
    RelationshipMesh,
    RelationshipSignature,
    RoleInference,
    StructuralRole,
    TextureLayer,
    TextureVoice,
    ThematicAlignment,
)


# ============================================================================
# Enum tests (unchanged — enums are preserved)
# ============================================================================


def test_archetype_enum_values():
    assert Archetype.HERO.value == "hero"
    assert Archetype.VILLAIN.value == "villain"


def test_moral_alignment_enum_values():
    assert MoralAlignment.LAWFUL_GOOD.value == "lawful_good"


def test_dramatic_function_enum_values():
    assert DramaticFunction.EMOTIONAL_ANCHOR.value == "emotional_anchor"


def test_trope_tag_enum_values():
    assert TropeTag.CHOSEN_ONE.value == "chosen_one"


def test_relationship_type_enum_values():
    assert RelationshipType.TRUST.value == "trust"
    assert RelationshipType.MENTORSHIP.value == "mentorship"


# ============================================================================
# Layered model tests
# ============================================================================


def test_structural_role_defaults():
    r = StructuralRole()
    assert r.secondary == []


def test_structural_role_with_functions():
    r = StructuralRole(secondary=[DramaticFunction.EMOTIONAL_ANCHOR, DramaticFunction.CATALYST])
    assert len(r.secondary) == 2


def test_archetypal_layer_defaults():
    a = ArchetypalLayer()
    assert a.core is None
    assert a.shadow is None


def test_archetypal_layer_full():
    a = ArchetypalLayer(core=Archetype.TRAGIC_HERO, shadow=Archetype.SHADOW)
    assert a.core == Archetype.TRAGIC_HERO
    assert a.shadow == Archetype.SHADOW


def test_psychological_layer_defaults():
    p = PsychologicalLayer()
    assert p.wound is None
    assert p.contradictions == []


def test_psychological_layer_full():
    p = PsychologicalLayer(
        wound="abandonment",
        fear="irrelevance",
        desire="recognition",
        contradictions=["compassionate_to_strangers", "cruel_to_family"],
    )
    assert p.wound == "abandonment"
    assert len(p.contradictions) == 2


def test_texture_voice():
    v = TextureVoice(cadence="clipped", vocabulary="technical")
    assert v.cadence == "clipped"
    assert v.vocabulary == "technical"


def test_texture_layer():
    t = TextureLayer(
        voice=TextureVoice(cadence="lilting"),
        habits=["folds receipts obsessively"],
        aesthetic=["silver jewelry"],
    )
    assert t.voice.cadence == "lilting"
    assert len(t.habits) == 1
    assert len(t.aesthetic) == 1


def test_arc_change():
    ac = ArcChange(from_="control", to="vulnerability")
    assert ac.from_ == "control"
    assert ac.to == "vulnerability"


def test_arc_engine():
    ae = ArcEngine(positive_change=ArcChange(from_="guilt", to="peace"))
    assert ae.positive_change.from_ == "guilt"


def test_relationship_signature():
    sig = RelationshipSignature(other="Kael", type=RelationshipType.RIVALRY, intensity=0.8)
    assert sig.other == "Kael"
    assert sig.intensity == 0.8


def test_relationship_mesh():
    mesh = RelationshipMesh(
        relationships=[RelationshipSignature(other="Kael", type=RelationshipType.RIVALRY, intensity=0.8)]
    )
    assert len(mesh.relationships) == 1


def test_thematic_alignment():
    ta = ThematicAlignment(theme="redemption", stance="embodies")
    assert ta.theme == "redemption"


def test_role_inference():
    ri = RoleInference(inferred_role="social_hub", confidence=0.7)
    assert ri.inferred_role == "social_hub"


def test_character_identity_defaults():
    ci = CharacterIdentity()
    assert ci.narrative_role is None
    assert ci.archetype is None
    assert ci.psychology is None
    assert ci.texture is None
    assert ci.arc is None
    assert ci.trope_tags == []


def test_character_identity_with_layers():
    ci = CharacterIdentity(
        narrative_role=StructuralRole(secondary=[DramaticFunction.EMOTIONAL_ANCHOR]),
        archetype=ArchetypalLayer(core=Archetype.TRAGIC_HERO),
        psychology=PsychologicalLayer(wound="abandonment"),
        texture=TextureLayer(habits=["folds receipts"]),
        arc=ArcEngine(positive_change=ArcChange(from_="control", to="vulnerability")),
        trope_tags=[TropeTag.FALLEN_HERO],
    )
    assert ci.narrative_role.secondary[0] == DramaticFunction.EMOTIONAL_ANCHOR
    assert ci.archetype.core == Archetype.TRAGIC_HERO
    assert ci.psychology.wound == "abandonment"
    assert ci.texture.habits[0] == "folds receipts"
    assert ci.arc.positive_change.from_ == "control"
    assert ci.trope_tags == [TropeTag.FALLEN_HERO]


def test_character_identity_roundtrip():
    ci = CharacterIdentity(
        archetype=ArchetypalLayer(core=Archetype.MENTOR),
        narrative_role=StructuralRole(secondary=[DramaticFunction.VOICE_OF_REASON]),
    )
    data = ci.model_dump(mode="json", by_alias=True)
    restored = CharacterIdentity.model_validate(data)
    assert restored.archetype.core == Archetype.MENTOR
    assert restored.narrative_role.secondary == [DramaticFunction.VOICE_OF_REASON]


def test_character_categorization_defaults():
    cc = CharacterCategorization()
    assert cc.identity.archetype is None
    assert cc.role_inferences == []


# ============================================================================
# Character model integration tests
# ============================================================================


def test_character_identity_field_is_optional():
    char = Character(name="Kael", role=CharacterRole.PROTAGONIST, arc_type=ArcType.GROWTH,
                     arc_start_percentage=0, arc_end_percentage=100)
    assert char.identity is None


def test_character_identity_field_accepts_layered_dict():
    char = Character(
        name="Kael",
        role=CharacterRole.PROTAGONIST,
        arc_type=ArcType.GROWTH,
        arc_start_percentage=0,
        arc_end_percentage=100,
        identity={
            "archetype": {"core": "tragic_hero"},
            "narrative_role": {"secondary": ["emotional_anchor"]},
            "psychology": {"wound": "abandonment"},
        },
    )
    assert char.identity is not None
    assert char.identity["archetype"]["core"] == "tragic_hero"


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
        "contract": {"content_rating": "PG", "mandatory_ending_tone": "hopeful"},
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
                    "archetype": {"core": "tragic_hero", "shadow": "shadow"},
                    "narrative_role": {"secondary": ["emotional_anchor", "catalyst"]},
                    "psychology": {"wound": "abandonment", "fear": "irrelevance"},
                },
            }
        ],
    }
    bp = StoryBlueprint.model_validate(bp_data)
    assert bp.characters[0].identity["archetype"]["core"] == "tragic_hero"
    assert bp.characters[0].identity["narrative_role"]["secondary"] == ["emotional_anchor", "catalyst"]


def test_character_categorization_field():
    char = Character(
        name="Kael",
        role=CharacterRole.PROTAGONIST,
        arc_type=ArcType.GROWTH,
        arc_start_percentage=0,
        arc_end_percentage=100,
        categorization={
            "identity": {"archetype": {"core": "hero"}},
            "relationship_signatures": [{"other": "Vlak", "type": "rivalry", "intensity": 0.9}],
        },
    )
    assert char.categorization["identity"]["archetype"]["core"] == "hero"


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
        "contract": {"content_rating": "PG", "mandatory_ending_tone": "hopeful"},
        "emotional_design": {"overall_emotional_arc": "rise"},
        "theme": {"central_question": "?", "thesis": "."},
        **overrides,
    }
    return data


def test_analyzer_empty_characters():
    bp = StoryBlueprint.model_validate(_minimal_blueprint_data())
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "characters.missing" for d in diagnostics)


def test_analyzer_missing_identity_warning():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.identity.missing" for d in diagnostics)


def test_analyzer_missing_core_archetype():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"narrative_role": {"secondary": ["emotional_anchor"]}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.archetype.core_missing" for d in diagnostics)


def test_analyzer_no_antagonist_warning():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "ally", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "characters.no_antagonist" for d in diagnostics)


def test_analyzer_archetype_redundancy():
    data = _minimal_blueprint_data(story_engine={
        "main_thread": {
            "want": {"author_text": "Kael wants truth", "checkable_claims": []},
            "resistance": {"author_text": "The lie", "checkable_claims": []},
            "conflict": {"author_text": "Clash", "checkable_claims": []},
            "stakes": {"author_text": "Everything", "checkable_claims": []},
            "change": {"author_text": "Kael learns", "checkable_claims": []},
            "thematic_function": "Tests truth.",
        },
        "threads": [],
    }, characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"archetype": {"core": "hero"}}},
        {"name": "Vlak", "role": "antagonist", "arc_type": "corruption",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"archetype": {"core": "hero"}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "characters.archetype_redundancy" for d in diagnostics)


def test_analyzer_shadow_matches_core():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"archetype": {"core": "villain", "shadow": "villain"}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.archetype.shadow_matches_core" for d in diagnostics)


def test_analyzer_voice_convergence():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"texture": {"voice": {"cadence": "clipped", "vocabulary": "technical"}}}},
        {"name": "Vlak", "role": "antagonist", "arc_type": "corruption",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"texture": {"voice": {"cadence": "clipped", "vocabulary": "technical"}}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "characters.voice_cadence_convergence" for d in diagnostics)


def test_analyzer_clean_with_full_identity():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "archetype": {"core": "tragic_hero"},
             "narrative_role": {"secondary": ["emotional_anchor"]},
         }},
        {"name": "Vlak", "role": "antagonist", "arc_type": "corruption",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "archetype": {"core": "villain"},
             "narrative_role": {"secondary": ["ideological_opposition"]},
         }},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    identity_missing = [d for d in diagnostics if d.rule == "character.identity.missing"]
    assert len(identity_missing) == 0


def test_analyzer_mentor_contrast():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"archetype": {"core": "hero"}}},
        {"name": "Gandalf", "role": "ally", "arc_type": "flat",
         "arc_start_percentage": 0, "arc_end_percentage": 0,
         "identity": {"archetype": {"core": "mentor"}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    mentor_contrast = [d for d in diagnostics if d.rule == "character.mentor_no_ideological_contrast"]
    assert len(mentor_contrast) == 0


def test_analyzer_mentor_same_as_protagonist():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"archetype": {"core": "mentor"}}},
        {"name": "Guide", "role": "ally", "arc_type": "flat",
         "arc_start_percentage": 0, "arc_end_percentage": 0,
         "identity": {"archetype": {"core": "mentor"}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    mentor_warning = [d for d in diagnostics if d.rule == "character.mentor_no_ideological_contrast"]
    assert len(mentor_warning) > 0


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


def test_categorizer_proposes_narrative_role():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert DramaticFunction.EMOTIONAL_ANCHOR in cats["Kael"].identity.narrative_role.secondary
    assert DramaticFunction.IDEOLOGICAL_OPPOSITION in cats["Vlak"].identity.narrative_role.secondary


def test_categorizer_proposes_archetype():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
        _make_char("Old Man", CharacterRole.MENTOR),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.archetype.core == Archetype.HERO
    assert cats["Vlak"].identity.archetype.core == Archetype.VILLAIN
    assert cats["Old Man"].identity.archetype.core == Archetype.MENTOR


def test_categorizer_proposes_arc_change():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST, arc=ArcType.GROWTH),
        _make_char("Vlak", CharacterRole.ANTAGONIST, arc=ArcType.CORRUPTION),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.arc.positive_change.from_ == "naivety"
    assert cats["Kael"].identity.arc.positive_change.to == "wisdom"
    assert cats["Vlak"].identity.arc.positive_change.from_ == "driven"


def test_categorizer_proposes_psychology():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert "driven_but_vulnerable" in cats["Kael"].identity.psychology.contradictions


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
    report = json.loads(capsys.readouterr().out)
    assert report["characters"] == []


def test_cli_character_show_with_characters(tmp_path, capsys):
    chars = [{"name": "Kael", "role": "protagonist", "arc_type": "growth",
              "arc_start_percentage": 0, "arc_end_percentage": 100}]
    bp_path = _make_blueprint_yaml(tmp_path, chars)
    args = _MockArgs(blueprint=bp_path, output=None)
    rc = handle_character_command(args)
    assert rc == 0
    report = json.loads(capsys.readouterr().out)
    assert len(report["characters"]) == 1
    assert report["characters"][0]["name"] == "Kael"


def test_cli_character_show_layers(tmp_path, capsys):
    chars = [{"name": "Kael", "role": "protagonist", "arc_type": "growth",
              "arc_start_percentage": 0, "arc_end_percentage": 100,
              "identity": {
                  "archetype": {"core": "tragic_hero"},
                  "narrative_role": {"secondary": ["emotional_anchor"]},
                  "psychology": {"wound": "abandonment"},
              }}]
    bp_path = _make_blueprint_yaml(tmp_path, chars)
    args = _MockArgs(blueprint=bp_path, output=None)
    rc = handle_character_command(args)
    assert rc == 0
    report = json.loads(capsys.readouterr().out)
    layers = report["characters"][0]["layers"]
    assert layers["archetype"]["core"] == "tragic_hero"
    assert "emotional_anchor" in layers["narrative_role"]["secondary"]
    assert layers["psychology"]["wound"] == "abandonment"


def test_cli_character_diagnose(tmp_path, capsys):
    bp_path = _make_blueprint_yaml(tmp_path, [])
    args = _MockArgs(blueprint=bp_path, output=None, character_command="diagnose")
    rc = handle_character_command(args)
    assert rc == 0


def test_cli_character_categorize(tmp_path, capsys):
    chars = [{"name": "Kael", "role": "protagonist", "arc_type": "growth",
              "arc_start_percentage": 0, "arc_end_percentage": 100}]
    bp_path = _make_blueprint_yaml(tmp_path, chars)
    args = _MockArgs(blueprint=bp_path, character_command="categorize")
    rc = handle_character_command(args)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert "Kael" in out
    assert out["Kael"]["identity"]["archetype"]["core"] == "hero"


def test_cli_character_show_writes_to_output(tmp_path):
    chars = [{"name": "Kael", "role": "protagonist", "arc_type": "growth",
              "arc_start_percentage": 0, "arc_end_percentage": 100}]
    bp_path = _make_blueprint_yaml(tmp_path, chars)
    out_path = tmp_path / "report.json"
    args = _MockArgs(blueprint=bp_path, output=out_path, character_command="show")
    rc = handle_character_command(args)
    assert rc == 0
    assert out_path.exists()


def test_cli_character_show_missing_blueprint(tmp_path, capsys):
    args = _MockArgs(blueprint=tmp_path / "nonexistent.yaml", output=None, character_command="show")
    rc = handle_character_command(args)
    assert rc == 1


# ============================================================================
# Integration: Identity roundtrip through blueprint YAML serialization
# ============================================================================


def test_layered_identity_serialization_roundtrip(tmp_path):
    bp_data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "archetype": {"core": "tragic_hero", "shadow": "shadow"},
             "narrative_role": {"secondary": ["emotional_anchor", "audience_surrogate"]},
             "psychology": {"wound": "abandonment", "fear": "irrelevance",
                            "desire": "recognition",
                            "contradictions": ["compassionate_to_strangers", "cruel_to_family"]},
             "texture": {"voice": {"cadence": "clipped", "vocabulary": "technical"},
                         "habits": ["folds receipts obsessively"],
                         "aesthetic": ["silver jewelry"]},
             "arc": {"positive_change": {"from": "control", "to": "vulnerability"}},
             "trope_tags": ["fallen_hero", "dark_past"],
         }},
    ])
    bp = StoryBlueprint.model_validate(bp_data)
    serialized = yaml.safe_dump(bp.model_dump(mode="json"))
    loaded_data = yaml.safe_load(serialized)
    restored = StoryBlueprint.model_validate(loaded_data)
    identity = restored.characters[0].identity
    assert identity["archetype"]["core"] == "tragic_hero"
    assert identity["archetype"]["shadow"] == "shadow"
    assert identity["narrative_role"]["secondary"] == ["emotional_anchor", "audience_surrogate"]
    assert identity["psychology"]["wound"] == "abandonment"
    assert identity["texture"]["voice"]["cadence"] == "clipped"
    assert identity["arc"]["positive_change"]["from"] == "control"
    assert "fallen_hero" in identity["trope_tags"]
