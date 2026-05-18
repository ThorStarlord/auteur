from auteur.blueprint import StoryBlueprint
from auteur.structure import DiagnosticLayer, DiagnosticSeverity, analyze_structure

def _minimal_thriller_blueprint_data() -> dict[str, object]:
    return {
        "identity": {
            "title": "Action Under Fire",
            "author_intent": "A fast-paced ticking clock thriller.",
            "length_class": "novel",
            "genre": "thriller",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "PG-13",
            "mandatory_ending_tone": "hopeful",
            "forbidden_tropes": [],
        },
        "emotional_design": {
            "overall_emotional_arc": "adrenaline and tension",
        },
        "theme": {
            "central_question": "Can the agent diffuse the bomb before the clock runs out?",
            "thesis": "Compliance with evil is slow suicide.",
            "motifs": [],
        },
    }

def _claim(text: str) -> dict[str, object]:
    return {"author_text": text, "checkable_claims": []}

def test_compliant_thriller_no_warnings():
    data = _minimal_thriller_blueprint_data()
    # Add a clean story engine
    data["story_engine"] = {
        "main_thread": {
            "want": _claim("Expose the double agent in the agency."),
            "resistance": _claim("The double agent has diplomatic immunity."),
            "conflict": _claim("A cat and mouse chase across Europe."),
            "stakes": _claim("Failure means a chemical attack on Brussels."),
            "change": _claim("The agent goes rogue to secure the arrest."),
            "thematic_function": "Shows compliance is suicide.",
        },
        "threads": [],
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    # Check that there are no genre-based warnings or errors
    genre_rules = [d for d in diagnostics if d.rule.startswith("genre.")]
    assert genre_rules == []

def test_thriller_therapy_bias_warning():
    data = _minimal_thriller_blueprint_data()
    # Introduce therapeutic trauma/healing/therapy words into the thesis and story want
    data["theme"]["thesis"] = "Exposing the double agent will heal the protagonist's inner wound."
    data["story_engine"] = {
        "main_thread": {
            "want": _claim("Expose the agent to resolve his identity crisis and process childhood trauma."),
            "resistance": _claim("The double agent uses therapy terms."),
            "conflict": _claim("A fight that triggers repressed memories."),
            "stakes": _claim("His psychological healing is at risk."),
            "change": _claim("He learns to forgive himself."),
            "thematic_function": "Expresses healing of the trauma.",
        },
        "threads": [],
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    # Filter for the therapy bias trap warning
    warnings = [d for d in diagnostics if d.rule == "genre.psychology_budget.therapy_bias_trap"]
    assert len(warnings) == 1
    w = warnings[0]
    assert w.severity == DiagnosticSeverity.WARNING
    assert w.layer == DiagnosticLayer.TARGET_EXPERIENCE
    assert "inner wound" in w.evidence[1]
    assert "trauma" in w.evidence[1]

def test_romance_tragic_ending_forbidden_error():
    # Romance contract forbids tragic endings
    data = _minimal_thriller_blueprint_data()
    data["identity"]["genre"] = "romance"
    data["contract"]["mandatory_ending_tone"] = "tragic"
    data["story_engine"] = {
        "main_thread": {
            "want": _claim("Win back the love of her life."),
            "resistance": _claim("They belong to rival social classes."),
            "conflict": _claim("Struggling to build a life together."),
            "stakes": _claim("Losing her heart forever."),
            "change": _claim("They both embrace mutual support."),
            "thematic_function": "Love wins.",
        },
        "threads": [],
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    # Filter for forbidden mismatches
    errors = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.ending_tone"]
    assert len(errors) == 1
    e = errors[0]
    assert e.severity == DiagnosticSeverity.ERROR
    assert e.layer == DiagnosticLayer.CONSTRAINTS
    assert "tragic ending" in e.evidence[1]

def test_romance_required_trope_forbidden_error():
    # Romance requires the "happily ever after or happy for now" trope
    data = _minimal_thriller_blueprint_data()
    data["identity"]["genre"] = "romance"
    data["contract"]["forbidden_tropes"] = ["happily ever after or happy for now"]
    data["story_engine"] = {
        "main_thread": {
            "want": _claim("Win back the love of her life."),
            "resistance": _claim("They belong to rival social classes."),
            "conflict": _claim("Struggling to build a life together."),
            "stakes": _claim("Losing her heart forever."),
            "change": _claim("They both embrace mutual support."),
            "thematic_function": "Love wins.",
        },
        "threads": [],
    }
    
    blueprint = StoryBlueprint.model_validate(data)
    diagnostics = analyze_structure(blueprint)
    
    # Filter for the required trope forbidden mismatch
    errors = [d for d in diagnostics if d.rule == "genre.forbidden_mismatch.required_trope_forbidden"]
    assert len(errors) == 1
    e = errors[0]
    assert e.severity == DiagnosticSeverity.ERROR
    assert e.layer == DiagnosticLayer.CONSTRAINTS
    assert e.evidence[0] == "required_trope = happily ever after or happy for now"
