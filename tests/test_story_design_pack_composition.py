from auteur.story_design_packs.composition import compose_packs


def test_composition_synthesizes_interactions_and_pins_hashes():
    result = compose_packs(["superhero", "anti_hero", "hard_determinism", "corporate_superhuman_metropolis"])
    assert len(result.selected_packs) == 4
    assert result.reinforcing_patterns
    assert result.productive_tensions
    assert any("×" in item for item in result.reinforcing_patterns + result.productive_tensions)
    assert len(result.applicable_design_priors) >= 8
    assert all(item.content_hash for item in result.pack_provenance)


def test_composition_does_not_create_a_silent_conflict_winner():
    result = compose_packs(["anti_hero", "hard_determinism"])
    assert result.productive_tensions
    assert result.actual_conflicts == []

