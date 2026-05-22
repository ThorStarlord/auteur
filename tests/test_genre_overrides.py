from auteur.blueprint import StoryBlueprint, OverrideType
from auteur.structure import DiagnosticLayer, DiagnosticSeverity, analyze_structure
from tests.test_structure_analyzer import _blueprint_data_with_story_engine


def test_runway_no_override_has_flow():
    # Netorare with short_story has runway mismatch and generates the recommendation flow
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "netorare"
    data["identity"]["length_class"] = "short_story"
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    runway_diagnostics = [d for d in diagnostics if d.rule == "genre.setup_contract.insufficient_runway"]
    assert len(runway_diagnostics) == 1
    
    d = runway_diagnostics[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.SCOPE
    assert d.genre_recommendation_flow is not None
    
    flow = d.genre_recommendation_flow
    assert flow["selected_genre"] == "netorare"
    assert flow["load_bearing_expectation"] == "emotional_runway_before_betrayal"
    assert flow["user_override"] == "remove_long_build_up"
    assert flow["auteur_diagnosis"] == "genre_contract_risk"
    assert "betrayal impact" in flow["consequence"]
    
    options = flow["options"]
    assert "preserve_genre" in options
    assert "subvert_genre" in options
    assert "reclassify" in options
    assert "override_anyway" in options
    
    assert "compressed emotional runway" in options["preserve_genre"]["recommendation"]
    assert "shock, destabilization, brutality" in options["subvert_genre"]["recommendation"]
    assert "betrayal vignette" in options["reclassify"]["recommendation"]


def test_runway_override_compression():
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "netorare"
    data["identity"]["length_class"] = "short_story"
    # Provide override
    data["identity"]["genre_overrides"] = {
        "emotional_runway": {
            "load_bearing_expectation": "emotional_runway",
            "user_override": "compress setup to one key scene",
            "override_type": "compression",
            "rationale": "Tight execution constraint"
        }
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    # Original mismatch warning should be suppressed
    original = [d for d in diagnostics if d.rule == "genre.setup_contract.insufficient_runway"]
    assert len(original) == 0
    
    # Advice override diagnostic should exist
    override_diagnostics = [d for d in diagnostics if d.rule == "genre.setup_contract.insufficient_runway.compressed"]
    assert len(override_diagnostics) == 1
    
    d = override_diagnostics[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.SCOPE
    assert "overridden via compression" in d.message
    assert "override_type = compression" in d.evidence


def test_runway_override_subversion():
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "netorare"
    data["identity"]["length_class"] = "short_story"
    # Provide override
    data["identity"]["genre_overrides"] = {
        "emotional_runway": {
            "load_bearing_expectation": "emotional_runway",
            "user_override": "sudden betrayal without build-up",
            "override_type": "subversion",
            "rationale": "Jarring artistic shock"
        }
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    override_diagnostics = [d for d in diagnostics if d.rule == "genre.setup_contract.insufficient_runway.subverted"]
    assert len(override_diagnostics) == 1
    
    d = override_diagnostics[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.SCOPE
    assert "overridden via subversion" in d.message
    assert "shock, destabilization, or brutality" in d.message


def test_runway_override_reclassification():
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "netorare"
    data["identity"]["length_class"] = "short_story"
    # Provide override
    data["identity"]["genre_overrides"] = {
        "emotional_runway": {
            "load_bearing_expectation": "emotional_runway",
            "user_override": "no setup, immediate transgressive vignette",
            "override_type": "reclassification",
            "rationale": "Not a full novel narrative"
        }
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    override_diagnostics = [d for d in diagnostics if d.rule == "genre.setup_contract.insufficient_runway.reclassified"]
    assert len(override_diagnostics) == 1
    
    d = override_diagnostics[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.SCOPE
    assert "overridden via reclassification" in d.message
    assert "breaks the standard Netorare contract" in d.message


def test_ending_tone_override():
    # Romance contract forbids tragic endings, but override allows it via subversion
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "romance"
    data["contract"]["mandatory_ending_tone"] = "tragic"
    data["identity"]["genre_overrides"] = {
        "ending_tone": {
            "load_bearing_expectation": "ending_tone",
            "user_override": "unhappy ending to subvert genre fairy tales",
            "override_type": "subversion",
            "rationale": "Artistic subversion"
        }
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    # Error should be suppressed
    errors = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.ending_tone"]
    assert len(errors) == 0
    
    # Advice diagnostic warning should exist
    override_diagnostics = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.ending_tone.subversion"]
    assert len(override_diagnostics) == 1
    
    d = override_diagnostics[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.CONSTRAINTS
    assert "overridden via subversion" in d.message


def test_required_trope_override():
    # Romance requires the "happily ever after or happy for now" trope, forbidden by contract but overridden
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "romance"
    data["contract"]["forbidden_tropes"] = ["happily ever after or happy for now"]
    data["identity"]["genre_overrides"] = {
        "trope.happily_ever_after_or_happy_for_now": {
            "load_bearing_expectation": "trope.happily_ever_after_or_happy_for_now",
            "user_override": "no happy ending in this dark romance",
            "override_type": "reclassification",
            "rationale": "Shifting to gothic tragedy"
        }
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    # Error should be suppressed
    errors = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.required_trope_forbidden"]
    assert len(errors) == 0
    
    # Advice diagnostic warning should exist
    override_diagnostics = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.required_trope_forbidden.reclassification"]
    assert len(override_diagnostics) == 1
    
    d = override_diagnostics[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.CONSTRAINTS
    assert "forbidden but overridden via reclassification" in d.message

def test_ending_tone_override_safe_variation():
    # Romance contract forbids tragic endings, but override allows it via safe_variation
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "romance"
    data["contract"]["mandatory_ending_tone"] = "tragic"
    data["identity"]["genre_overrides"] = {
        "ending_tone": {
            "load_bearing_expectation": "ending_tone",
            "user_override": "a bittersweet ending leaning towards tragic",
            "override_type": "safe_variation",
            "rationale": "Slight deviation but still romantic"
        }
    }

    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)

    # Error should be suppressed
    errors = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.ending_tone"]
    assert len(errors) == 0

    # Advice diagnostic warning should exist
    override_diagnostics = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.ending_tone.safe_variation"]
    assert len(override_diagnostics) == 1

    d = override_diagnostics[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.CONSTRAINTS
    assert "overridden via safe_variation" in d.message

def test_missing_override_emits_error():
    # Romance contract forbids tragic endings. Missing override should emit error.
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "romance"
    data["contract"]["mandatory_ending_tone"] = "tragic"
    # No genre_overrides specified

    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)

    errors = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.ending_tone"]
    assert len(errors) == 1

    d = errors[0]
    assert d.severity == DiagnosticSeverity.ERROR
    assert d.layer == DiagnosticLayer.CONSTRAINTS
    assert "is forbidden by the" in d.message

def test_declared_override_downgrades_error():
    # Romance contract forbids tragic endings, but a declared override suppresses the error and leaves a warning.
    data = _blueprint_data_with_story_engine()
    data["identity"]["genre"] = "romance"
    data["contract"]["mandatory_ending_tone"] = "tragic"
    data["identity"]["genre_overrides"] = {
        "ending_tone": {
            "load_bearing_expectation": "ending_tone",
            "user_override": "dark ending for a horror romance",
            "override_type": "reclassification",
            "rationale": "It's horror"
        }
    }

    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)

    # Original error is missing
    errors = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.ending_tone"]
    assert len(errors) == 0

    # Warning remains
    warnings = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.ending_tone.reclassification"]
    assert len(warnings) == 1

    d = warnings[0]
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.layer == DiagnosticLayer.CONSTRAINTS
    assert "overridden via reclassification" in d.message
    assert "dark ending for a horror romance" in d.message
