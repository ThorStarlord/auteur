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
    AuthorshipVector,
    DependencySymmetry,
    DramaticFunction,
    EssenceTraitSource,
    MoralAlignment,
    MotifType,
    PersonalityTrait,
    PhilosophyTag,
    ProtagonistSubtype,
    RelationshipType,
    TropeTag,
    Vice,
    Virtue,
    VulnerabilityFamily,
)
from auteur.character.models import (
    ArcChange,
    ArcEngine,
    ArchetypalLayer,
    CharacterCategorization,
    CharacterIdentity,
    EssenceProfile,
    EssenceTrait,
    IdeologicalProfile,
    Motif,
    MotifProfile,
    PsychologicalLayer,
    RelationshipArc,
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


# ============================================================================
# New enum tests (PhilosophyTag, AuthorshipVector, DependencySymmetry, MotifType, EssenceTraitSource)
# ============================================================================


def test_philosophy_tag_enum_values():
    assert PhilosophyTag.PROTECTION_THROUGH_HIERARCHY.value == "protection_through_hierarchy"
    assert PhilosophyTag.LOYALTY_THROUGH_ALLEGIANCE.value == "loyalty_through_allegiance"


def test_authorship_vector_enum_values():
    assert AuthorshipVector.MUTUAL.value == "mutual"
    assert AuthorshipVector.CONTESTED.value == "contested"


def test_dependency_symmetry_enum_values():
    assert DependencySymmetry.CODEPENDENT.value == "codependent"
    assert DependencySymmetry.RECURSIVE_DEPENDENCY.value == "recursive_dependency"


def test_motif_type_enum_values():
    assert MotifType.GESTURE.value == "gesture"
    assert MotifType.VERBAL_TIC.value == "verbal_tic"


def test_essence_trait_source_enum_values():
    assert EssenceTraitSource.PERSONAL.value == "personal"
    assert EssenceTraitSource.INSERTED.value == "inserted"


# ============================================================================
# New model tests: IdeologicalProfile, EssenceProfile, MotifProfile, enriched TextureLayer, enriched RelationshipSignature
# ============================================================================


def test_ideological_profile_defaults():
    ip = IdeologicalProfile()
    assert ip.worldview is None
    assert ip.philosophy_tags == []


def test_ideological_profile_full():
    ip = IdeologicalProfile(
        worldview="Protection Through Hierarchy",
        philosophy_tags=[PhilosophyTag.PROTECTION_THROUGH_HIERARCHY],
    )
    assert ip.worldview == "Protection Through Hierarchy"
    assert PhilosophyTag.PROTECTION_THROUGH_HIERARCHY in ip.philosophy_tags


def test_essence_trait():
    et = EssenceTrait(name="curious", source=EssenceTraitSource.PERSONAL, description="Driven to understand.")
    assert et.name == "curious"
    assert et.source == EssenceTraitSource.PERSONAL


def test_essence_profile_defaults():
    ep = EssenceProfile()
    assert ep.personal_traits == []
    assert ep.bond_traits == []


def test_essence_profile_full():
    ep = EssenceProfile(
        personal_traits=[
            EssenceTrait(name="curious", source=EssenceTraitSource.PERSONAL),
        ],
        bond_traits=[
            EssenceTrait(name="patient", source=EssenceTraitSource.BOND, description="Acquired through mentorship."),
        ],
    )
    assert len(ep.personal_traits) == 1
    assert len(ep.bond_traits) == 1
    assert ep.bond_traits[0].source == EssenceTraitSource.BOND


def test_motif():
    m = Motif(behavior="pauses at thresholds", type=MotifType.RITUAL, significance="Hesitation before commitment.")
    assert m.behavior == "pauses at thresholds"
    assert m.type == MotifType.RITUAL
    assert m.significance != ""


def test_motif_profile_defaults():
    mp = MotifProfile()
    assert mp.motifs == []


def test_motif_profile_full():
    mp = MotifProfile(motifs=[
        Motif(behavior="traces patterns on surfaces", type=MotifType.GESTURE, significance="Need for order."),
    ])
    assert len(mp.motifs) == 1
    assert mp.motifs[0].type == MotifType.GESTURE


def test_texture_layer_enriched():
    t = TextureLayer(
        voice=TextureVoice(cadence="clipped"),
        habits=["folds receipts"],
        gestures=["silently fixes collar during stress"],
        rituals=["checks evacuation exits repeatedly"],
        social_habits=["deliberately breaks rules in front of others"],
        behavioral_tells=["folds receipts when anxious"],
    )
    assert len(t.gestures) == 1
    assert len(t.rituals) == 1
    assert len(t.social_habits) == 1
    assert len(t.behavioral_tells) == 1
    assert t.gestures[0] == "silently fixes collar during stress"


def test_relationship_signature_enriched():
    sig = RelationshipSignature(
        other="Kael",
        type=RelationshipType.RIVALRY,
        intensity=0.8,
        ideological_alignment="opposed",
        authorship_vector=AuthorshipVector.CONTESTED,
        dependency_symmetry=DependencySymmetry.EQUAL,
    )
    assert sig.ideological_alignment == "opposed"
    assert sig.authorship_vector == AuthorshipVector.CONTESTED
    assert sig.dependency_symmetry == DependencySymmetry.EQUAL


def test_character_identity_with_new_layers():
    ci = CharacterIdentity(
        ideology=IdeologicalProfile(
            worldview="Salvation Through Knowledge",
            philosophy_tags=[PhilosophyTag.SALVATION_THROUGH_KNOWLEDGE],
        ),
        essence=EssenceProfile(
            personal_traits=[EssenceTrait(name="curious", source=EssenceTraitSource.PERSONAL)],
        ),
        motifs=MotifProfile(motifs=[
            Motif(behavior="pauses at thresholds", type=MotifType.RITUAL, significance="Hesitation."),
        ]),
        texture=TextureLayer(
            gestures=["silently fixes collar"],
            rituals=["edits announcement boards at night"],
        ),
    )
    assert ci.ideology.philosophy_tags == [PhilosophyTag.SALVATION_THROUGH_KNOWLEDGE]
    assert ci.essence.personal_traits[0].name == "curious"
    assert ci.motifs.motifs[0].type == MotifType.RITUAL
    assert ci.texture.gestures[0] == "silently fixes collar"


# ============================================================================
# New model roundtrip tests
# ============================================================================


def test_ideological_profile_roundtrip():
    ip = IdeologicalProfile(
        worldview="Protection Through Hierarchy",
        philosophy_tags=[PhilosophyTag.PROTECTION_THROUGH_HIERARCHY],
    )
    data = ip.model_dump(mode="json")
    restored = IdeologicalProfile.model_validate(data)
    assert restored.worldview == "Protection Through Hierarchy"
    assert restored.philosophy_tags == [PhilosophyTag.PROTECTION_THROUGH_HIERARCHY]


def test_essence_profile_roundtrip():
    ep = EssenceProfile(
        personal_traits=[EssenceTrait(name="brave", source=EssenceTraitSource.PERSONAL)],
        bond_traits=[EssenceTrait(name="wise", source=EssenceTraitSource.BOND)],
    )
    data = ep.model_dump(mode="json")
    restored = EssenceProfile.model_validate(data)
    assert restored.personal_traits[0].name == "brave"
    assert restored.bond_traits[0].source == EssenceTraitSource.BOND


def test_motif_profile_roundtrip():
    mp = MotifProfile(motifs=[
        Motif(behavior="traces patterns", type=MotifType.GESTURE, significance="Order."),
    ])
    data = mp.model_dump(mode="json")
    restored = MotifProfile.model_validate(data)
    assert restored.motifs[0].behavior == "traces patterns"
    assert restored.motifs[0].type == MotifType.GESTURE


def test_enriched_relationship_signature_roundtrip():
    sig = RelationshipSignature(
        other="Vlak",
        type=RelationshipType.RIVALRY,
        intensity=0.9,
        ideological_alignment="opposed",
        authorship_vector=AuthorshipVector.CONTESTED,
        dependency_symmetry=DependencySymmetry.ASYMMETRIC,
    )
    data = sig.model_dump(mode="json")
    restored = RelationshipSignature.model_validate(data)
    assert restored.ideological_alignment == "opposed"
    assert restored.authorship_vector == AuthorshipVector.CONTESTED
    assert restored.dependency_symmetry == DependencySymmetry.ASYMMETRIC


def test_character_identity_new_layers_roundtrip():
    ci = CharacterIdentity(
        ideology=IdeologicalProfile(
            philosophy_tags=[PhilosophyTag.SALVATION_THROUGH_KNOWLEDGE],
        ),
        essence=EssenceProfile(
            personal_traits=[EssenceTrait(name="curious", source=EssenceTraitSource.PERSONAL)],
        ),
        motifs=MotifProfile(motifs=[
            Motif(behavior="pauses at thresholds", type=MotifType.RITUAL),
        ]),
    )
    data = ci.model_dump(mode="json")
    restored = CharacterIdentity.model_validate(data)
    assert restored.ideology.philosophy_tags == [PhilosophyTag.SALVATION_THROUGH_KNOWLEDGE]
    assert restored.essence.personal_traits[0].name == "curious"
    assert restored.motifs.motifs[0].type == MotifType.RITUAL


def test_new_layers_in_character_identity_dict_roundtrip():
    bp_data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "ideology": {
                 "worldview": "Salvation Through Knowledge",
                 "philosophy_tags": ["salvation_through_knowledge"],
             },
             "essence": {
                 "personal_traits": [{"name": "curious", "source": "personal", "description": "Driven to understand."}],
                 "bond_traits": [{"name": "patient", "source": "bond", "description": "Learned from mentor."}],
             },
             "motifs": {
                 "motifs": [{"behavior": "pauses at thresholds", "type": "ritual", "significance": "Hesitation."}],
             },
             "texture": {
                 "gestures": ["silently fixes collar"],
                 "rituals": ["edits announcement boards at night"],
                 "behavioral_tells": ["folds receipts when anxious"],
             },
         }},
    ])
    bp = StoryBlueprint.model_validate(bp_data)
    identity = bp.characters[0].identity
    assert identity["ideology"]["worldview"] == "Salvation Through Knowledge"
    assert identity["essence"]["personal_traits"][0]["name"] == "curious"
    assert identity["motifs"]["motifs"][0]["type"] == "ritual"
    assert identity["texture"]["gestures"][0] == "silently fixes collar"
    assert "edits announcement boards at night" in identity["texture"]["rituals"]


def test_new_layers_yaml_roundtrip(tmp_path):
    bp_data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "ideology": {"philosophy_tags": ["salvation_through_knowledge"]},
             "essence": {
                 "personal_traits": [{"name": "curious", "source": "personal"}],
             },
             "motifs": {
                 "motifs": [{"behavior": "pauses", "type": "ritual"}],
             },
         }},
    ])
    bp = StoryBlueprint.model_validate(bp_data)
    serialized = yaml.safe_dump(bp.model_dump(mode="json"))
    loaded = yaml.safe_load(serialized)
    restored = StoryBlueprint.model_validate(loaded)
    identity = restored.characters[0].identity
    assert identity["ideology"]["philosophy_tags"] == ["salvation_through_knowledge"]
    assert identity["essence"]["personal_traits"][0]["name"] == "curious"
    assert identity["motifs"]["motifs"][0]["behavior"] == "pauses"


# ============================================================================
# New analyzer diagnostics
# ============================================================================


def test_analyzer_ideological_contrast():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"ideology": {"philosophy_tags": ["salvation_through_rebellion"]}}},
        {"name": "Vlak", "role": "antagonist", "arc_type": "corruption",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"ideology": {"philosophy_tags": ["protection_through_hierarchy"]}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "characters.ideological_contrast_detected" for d in diagnostics)


def test_analyzer_ideological_convergence():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"ideology": {"philosophy_tags": ["salvation_through_knowledge"]}}},
        {"name": "Vlak", "role": "antagonist", "arc_type": "corruption",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"ideology": {"philosophy_tags": ["salvation_through_knowledge"]}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "characters.ideological_convergence" for d in diagnostics)


def test_analyzer_ideological_contrast_no_false_positive():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"ideology": {"philosophy_tags": ["salvation_through_knowledge"]}}},
        {"name": "Vlak", "role": "antagonist", "arc_type": "corruption",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"ideology": {"philosophy_tags": ["order_through_structure"]}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    contrast = [d for d in diagnostics if d.rule == "characters.ideological_contrast_detected"]
    assert len(contrast) == 0


def test_analyzer_motif_missing_for_protagonist():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"archetype": {"core": "hero"}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.motifs.missing" for d in diagnostics)


def test_analyzer_motif_not_missing_when_present():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "archetype": {"core": "hero"},
             "motifs": {"motifs": [{"behavior": "pauses", "type": "ritual"}]},
         }},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    motif_missing = [d for d in diagnostics if d.rule == "character.motifs.missing"]
    assert len(motif_missing) == 0


def test_analyzer_essence_empty_warning():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"essence": {}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.essence.empty" for d in diagnostics)


def test_analyzer_essence_not_empty_when_populated():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"essence": {"personal_traits": [{"name": "curious", "source": "personal"}]}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    essence_empty = [d for d in diagnostics if d.rule == "character.essence.empty"]
    assert len(essence_empty) == 0


def test_analyzer_texture_shallow_warning():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"texture": {"voice": {"cadence": "clipped"}}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.texture.shallow" for d in diagnostics)


def test_analyzer_texture_not_shallow_with_gestures():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"texture": {"gestures": ["silently fixes collar"]}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    shallow = [d for d in diagnostics if d.rule == "character.texture.shallow"]
    assert len(shallow) == 0


def test_analyzer_ideological_no_tags_no_diagnostic():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100},
        {"name": "Vlak", "role": "antagonist", "arc_type": "corruption",
         "arc_start_percentage": 0, "arc_end_percentage": 100},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    ideological_rules = [d for d in diagnostics if "ideological" in d.rule]
    assert len(ideological_rules) == 0


# ============================================================================
# New categorizer tests
# ============================================================================


def test_categorizer_proposes_ideology():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.ideology is not None
    assert len(cats["Kael"].identity.ideology.philosophy_tags) > 0
    assert cats["Kael"].identity.ideology.worldview is not None


def test_categorizer_proposes_essence():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.essence is not None
    assert len(cats["Kael"].identity.essence.personal_traits) > 0


def test_categorizer_proposes_motifs():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.motifs is not None
    assert len(cats["Kael"].identity.motifs.motifs) > 0
    assert cats["Vlak"].identity.motifs is not None
    assert len(cats["Vlak"].identity.motifs.motifs) > 0


def test_categorizer_proposes_texture_gestures():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.texture is not None
    assert len(cats["Kael"].identity.texture.gestures) > 0


def test_categorizer_antagonist_ideology():
    bp = _make_blueprint([
        _make_char("Vlak", CharacterRole.ANTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Vlak"].identity.ideology is not None
    assert PhilosophyTag.ORDER_THROUGH_STRUCTURE in cats["Vlak"].identity.ideology.philosophy_tags


def test_categorizer_role_specific_motifs():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
        _make_char("Guide", CharacterRole.MENTOR),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.motifs.motifs[0].type == MotifType.RITUAL
    assert cats["Vlak"].identity.motifs.motifs[0].type == MotifType.GESTURE
    assert cats["Guide"].identity.motifs.motifs[0].type == MotifType.VERBAL_TIC


# ============================================================================
# VulnerabilityFamily enum + model tests
# ============================================================================


def test_vulnerability_family_enum():
    assert VulnerabilityFamily.STATUS_CONTROL.value == "status_control"
    assert VulnerabilityFamily.ABANDONMENT.value == "abandonment"


def test_psychology_layer_with_vulnerability():
    p = PsychologicalLayer(
        vulnerability_family=VulnerabilityFamily.STATUS_CONTROL,
        defense_mechanisms=["compartmentalization", "transactional_containment"],
    )
    assert p.vulnerability_family == VulnerabilityFamily.STATUS_CONTROL
    assert "compartmentalization" in p.defense_mechanisms


def test_psychology_layer_vulnerability_defaults():
    p = PsychologicalLayer()
    assert p.vulnerability_family is None
    assert p.defense_mechanisms == []


def test_psychology_layer_full_with_vulnerability():
    p = PsychologicalLayer(
        wound="abandonment",
        fear="irrelevance",
        desire="recognition",
        contradictions=["driven_but_vulnerable"],
        vulnerability_family=VulnerabilityFamily.ABANDONMENT,
        defense_mechanisms=["intellectualization", "self_reliance"],
    )
    assert p.vulnerability_family == VulnerabilityFamily.ABANDONMENT
    assert p.defense_mechanisms == ["intellectualization", "self_reliance"]


# ============================================================================
# Social aura tests
# ============================================================================


def test_texture_layer_social_aura_defaults():
    t = TextureLayer()
    assert t.social_aura == []


def test_texture_layer_with_social_aura():
    t = TextureLayer(
        voice=TextureVoice(cadence="clipped"),
        social_aura=["executive_pressure", "emotional_distance"],
    )
    assert "executive_pressure" in t.social_aura
    assert len(t.social_aura) == 2


# ============================================================================
# RelationshipArc tests
# ============================================================================


def test_relationship_arc_defaults():
    arc = RelationshipArc(other="Vlak")
    assert arc.other == "Vlak"
    assert arc.stages == []
    assert arc.current_stage is None
    assert arc.trust_level == 0.5
    assert arc.progression_type is None


def test_relationship_arc_full():
    arc = RelationshipArc(
        other="Vlak",
        stages=["fascination", "vulnerability_discovery", "trust_formation"],
        current_stage="trust_formation",
        trust_level=0.8,
        progression_type="trust_based",
    )
    assert len(arc.stages) == 3
    assert arc.current_stage == "trust_formation"
    assert arc.trust_level == 0.8
    assert arc.progression_type == "trust_based"


def test_relationship_arc_roundtrip():
    arc = RelationshipArc(
        other="Kael",
        stages=["acquaintance", "alliance"],
        current_stage="alliance",
        trust_level=0.6,
        progression_type="adversarial",
    )
    data = arc.model_dump(mode="json")
    restored = RelationshipArc.model_validate(data)
    assert restored.other == "Kael"
    assert restored.current_stage == "alliance"
    assert restored.progression_type == "adversarial"


def test_relationship_mesh_with_arcs():
    mesh = RelationshipMesh(
        relationships=[RelationshipSignature(other="Kael", type=RelationshipType.RIVALRY, intensity=0.8)],
        arcs=[RelationshipArc(other="Kael", stages=["conflict"], progression_type="adversarial")],
    )
    assert len(mesh.arcs) == 1
    assert mesh.arcs[0].other == "Kael"
    assert mesh.arcs[0].progression_type == "adversarial"


def test_relationship_mesh_with_arcs_roundtrip():
    mesh = RelationshipMesh(
        arcs=[RelationshipArc(other="Vlak", stages=["fascination", "trust"], trust_level=0.7)],
    )
    data = mesh.model_dump(mode="json")
    restored = RelationshipMesh.model_validate(data)
    assert restored.arcs[0].other == "Vlak"
    assert restored.arcs[0].trust_level == 0.7


# ============================================================================
# New analyzer diagnostics: vulnerability, defense, social_aura, arcs
# ============================================================================


def test_analyzer_vulnerability_missing():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"psychology": {"wound": "abandonment"}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.psychology.vulnerability_missing" for d in diagnostics)


def test_analyzer_vulnerability_not_missing_when_present():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"psychology": {"vulnerability_family": "status_control"}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    vuln_missing = [d for d in diagnostics if d.rule == "character.psychology.vulnerability_missing"]
    assert len(vuln_missing) == 0


def test_analyzer_defense_missing():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"psychology": {"wound": "abandonment"}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.psychology.defense_missing" for d in diagnostics)


def test_analyzer_defense_not_missing_when_present():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"psychology": {"defense_mechanisms": ["compartmentalization"]}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    defense_missing = [d for d in diagnostics if d.rule == "character.psychology.defense_missing"]
    assert len(defense_missing) == 0


def test_analyzer_social_aura_missing():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"texture": {"voice": {"cadence": "clipped"}}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.texture.social_aura_missing" for d in diagnostics)


def test_analyzer_social_aura_not_missing_when_present():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {"texture": {"social_aura": ["executive_pressure"]}}},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    aura_missing = [d for d in diagnostics if d.rule == "character.texture.social_aura_missing"]
    assert len(aura_missing) == 0


def test_analyzer_relationship_arcs_missing():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "relationship_mesh": {
                 "relationships": [{"other": "Vlak", "type": "rivalry", "intensity": 0.9}],
             },
         }},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    assert any(d.rule == "character.relationship.arcs_missing" for d in diagnostics)


def test_analyzer_relationship_arcs_not_missing_when_present():
    data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "relationship_mesh": {
                 "relationships": [{"other": "Vlak", "type": "rivalry", "intensity": 0.9}],
                 "arcs": [{"other": "Vlak", "stages": ["conflict"], "trust_level": 0.9}],
             },
         }},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    arcs_missing = [d for d in diagnostics if d.rule == "character.relationship.arcs_missing"]
    assert len(arcs_missing) == 0


def test_analyzer_no_false_positive_for_minor_characters():
    data = _minimal_blueprint_data(characters=[
        {"name": "Extra", "role": "supporting", "arc_type": "flat",
         "arc_start_percentage": 0, "arc_end_percentage": 0},
    ])
    bp = StoryBlueprint.model_validate(data)
    diagnostics = analyze_character_categorization(bp)
    vuln = [d for d in diagnostics if d.rule == "character.psychology.vulnerability_missing"]
    defense = [d for d in diagnostics if d.rule == "character.psychology.defense_missing"]
    aura = [d for d in diagnostics if d.rule == "character.texture.social_aura_missing"]
    assert len(vuln) == 0
    assert len(defense) == 0
    assert len(aura) == 0


# ============================================================================
# New categorizer tests: vulnerability, defense, social_aura, relationship_arcs
# ============================================================================


def test_categorizer_proposes_vulnerability_family():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.psychology.vulnerability_family == VulnerabilityFamily.INADEQUACY


def test_categorizer_proposes_defense_mechanisms():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert "intellectualization" in cats["Kael"].identity.psychology.defense_mechanisms
    assert "compartmentalization" in cats["Vlak"].identity.psychology.defense_mechanisms


def test_categorizer_proposes_social_aura():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert "earnest_pressure" in cats["Kael"].identity.texture.social_aura
    assert "executive_pressure" in cats["Vlak"].identity.texture.social_aura


def test_categorizer_proposes_relationship_arcs():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST, relationships=[
            {"other": "Vlak", "kind": "rivalry", "intensity": 0.9},
        ]),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    mesh = cats["Kael"].identity.relationship_mesh
    assert mesh is not None
    assert len(mesh.arcs) >= 1
    assert mesh.arcs[0].other == "Vlak"
    assert mesh.arcs[0].progression_type == "adversarial"


def test_categorizer_proposes_trust_based_arc_for_friendship():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST, relationships=[
            {"other": "Guide", "kind": "mentorship", "intensity": 0.7},
        ]),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    arcs = cats["Kael"].identity.relationship_mesh.arcs
    assert arcs[0].progression_type == "trust_based"


def test_categorizer_role_specific_vulnerability():
    bp = _make_blueprint([
        _make_char("Kael", CharacterRole.PROTAGONIST),
        _make_char("Vlak", CharacterRole.ANTAGONIST),
        _make_char("Guide", CharacterRole.MENTOR),
    ])
    engine = CategorizationEngine(bp)
    cats = engine.categorize_all()
    assert cats["Kael"].identity.psychology.vulnerability_family == VulnerabilityFamily.INADEQUACY
    assert cats["Vlak"].identity.psychology.vulnerability_family == VulnerabilityFamily.STATUS_CONTROL
    assert cats["Guide"].identity.psychology.vulnerability_family == VulnerabilityFamily.ISOLATION


# ============================================================================
# YAML roundtrip for vulnerability, defense, social_aura, relationship_arcs
# ============================================================================


def test_new_fields_yaml_roundtrip(tmp_path):
    bp_data = _minimal_blueprint_data(characters=[
        {"name": "Kael", "role": "protagonist", "arc_type": "growth",
         "arc_start_percentage": 0, "arc_end_percentage": 100,
         "identity": {
             "psychology": {
                 "vulnerability_family": "status_control",
                 "defense_mechanisms": ["compartmentalization"],
             },
             "texture": {
                 "social_aura": ["executive_pressure"],
             },
             "relationship_mesh": {
                 "relationships": [{"other": "Vlak", "type": "rivalry", "intensity": 0.9}],
                 "arcs": [{"other": "Vlak", "stages": ["conflict"], "trust_level": 0.9, "progression_type": "adversarial"}],
             },
         }},
    ])
    bp = StoryBlueprint.model_validate(bp_data)
    serialized = yaml.safe_dump(bp.model_dump(mode="json"))
    loaded = yaml.safe_load(serialized)
    restored = StoryBlueprint.model_validate(loaded)
    identity = restored.characters[0].identity
    assert identity["psychology"]["vulnerability_family"] == "status_control"
    assert "compartmentalization" in identity["psychology"]["defense_mechanisms"]
    assert "executive_pressure" in identity["texture"]["social_aura"]
    assert identity["relationship_mesh"]["arcs"][0]["other"] == "Vlak"
    assert identity["relationship_mesh"]["arcs"][0]["progression_type"] == "adversarial"
