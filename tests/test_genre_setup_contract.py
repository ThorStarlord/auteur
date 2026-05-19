from auteur.blueprint import StoryBlueprint, Genre
from auteur.genres.registry import load_genre_contract
from auteur.genres.models import NarrativeRunway, RequirementLevel
from auteur.structure import DiagnosticLayer, DiagnosticSeverity, analyze_structure
from tests.test_structure_analyzer import _blueprint_data_with_story_engine


def test_registered_genres_setup_contracts():
    # Romance contract
    romance_contract = load_genre_contract(Genre.ROMANCE)
    assert romance_contract.setup_contract.emotional_runway == NarrativeRunway.MEDIUM
    assert romance_contract.setup_contract.relationship_establishment == RequirementLevel.REQUIRED
    assert "Establish the protagonist's status quo and relational void/wound" in romance_contract.setup_contract.minimum_setup_beats

    # Netorare contract (long runway, required relationship establishment)
    ntr_contract = load_genre_contract(Genre.NETORARE)
    assert ntr_contract.setup_contract.emotional_runway == NarrativeRunway.LONG
    assert ntr_contract.setup_contract.relationship_establishment == RequirementLevel.REQUIRED
    assert "A scene showing ordinary trust." in ntr_contract.setup_contract.minimum_setup_beats

    # Netori contract (long runway, required relationship establishment)
    ntri_contract = load_genre_contract(Genre.NETORI)
    assert ntri_contract.setup_contract.emotional_runway == NarrativeRunway.LONG
    assert ntri_contract.setup_contract.relationship_establishment == RequirementLevel.REQUIRED
    assert "Rival appears to hold a legitimate prior claim." in ntri_contract.setup_contract.minimum_setup_beats


def test_fallback_genre_has_setup_contract():
    # Literary uses fallback or custom
    literary_contract = load_genre_contract(Genre.LITERARY)
    assert literary_contract.setup_contract is not None
    assert literary_contract.setup_contract.emotional_runway == NarrativeRunway.MEDIUM


def test_insufficient_runway_diagnostic_warning():
    # Create a blueprint data for Netorare but with short_story container length
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "netorare"
    data["identity"]["length_class"] = "short_story"
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    # Filter the insufficient runway warning
    runway_diagnostics = [d for d in diagnostics if d.rule == "genre.setup_contract.insufficient_runway"]
    assert len(runway_diagnostics) == 1
    
    d = runway_diagnostics[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.SCOPE
    assert "requires a 'long' emotional runway, but the story container length is 'short_story'" in d.message
    assert "genre = Netorare" in d.evidence
    assert "emotional_runway = long" in d.evidence
    assert "length_class = short_story" in d.evidence
    assert len(d.repair_options.preserve_intent) > 0


def test_sufficient_runway_diagnostic_no_warning():
    # Create a blueprint data for Netorare with novel container length
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "netorare"
    data["identity"]["length_class"] = "novel"
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    runway_diagnostics = [d for d in diagnostics if d.rule == "genre.setup_contract.insufficient_runway"]
    assert len(runway_diagnostics) == 0
