import pytest
from auteur.netorare.core_templates import HumiliationTemplate, HorrorTemplate, MysteryTemplate

def test_humiliation_template_has_all_phases():
    t = HumiliationTemplate()
    assert t.phases == {
        1: "emotional_core",
        2: "genre_contract",
        3: "scope",
        4: "structural_forces",
        5: "threads",
        6: "carriers",
        7: "representation",
        8: "modulation",
        9: "resonance"
    }

def test_humiliation_layer_4_want_options():
    t = HumiliationTemplate()
    options = t.get_options(4)
    assert "want" in options
    assert len(options["want"]) >= 3
    assert all(isinstance(opt, dict) for opt in options["want"])
    assert all("id" in opt and "label" in opt for opt in options["want"])

def test_humiliation_layer_4_has_constraints():
    t = HumiliationTemplate()
    constraints = t.get_constraints(4)
    assert "want_not_equal_change" in constraints
    assert "resistance_blocks_want" in constraints

def test_horror_template_distinct_from_humiliation():
    hum = HumiliationTemplate()
    hor = HorrorTemplate()
    assert hum.get_options(4) != hor.get_options(4)

def test_mystery_template_distinct_from_others():
    hum = HumiliationTemplate()
    mys = MysteryTemplate()
    assert hum.get_options(4) != mys.get_options(4)
