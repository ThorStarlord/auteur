from auteur.blueprint import Genre
from auteur.genre_pipeline.registry import get_all_genres, get_genre_pipeline
from auteur.genre_pipeline.templates import build_pipeline_descriptor
from auteur.genre_pipeline.validation import validate_pipeline_choices


def complete_first_choices(spec, core_id: str) -> dict[int, dict[str, str]]:
    descriptor = build_pipeline_descriptor(spec, core_id)
    choices = {
        phase.number: {field.id: field.options[0].id for field in phase.fields}
        for phase in descriptor.phases
        if phase.fields
    }
    if core_id == "paranoia":
        choices[8]["truth_ambiguity"] = "ambiguous"
    return choices


def test_normalized_complete_choices_validate_for_every_built_in_core():
    for spec in get_all_genres():
        for core_id in spec.core_ids:
            result = validate_pipeline_choices(
                spec,
                core_id,
                complete_first_choices(spec, core_id),
                require_complete=True,
            )
            assert result.is_valid, f"{core_id}: {result.errors}"


def test_gentlefemdom_semantic_phase_keys_are_adapted_for_legacy_validator():
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    choices = complete_first_choices(spec, "sensual_dominance")

    result = validate_pipeline_choices(spec, "sensual_dominance", choices, require_complete=True)

    assert result.is_valid
    assert not any("Unknown field" in error for error in result.errors)


def test_invalid_option_is_rejected_before_genre_validator_runs():
    spec = get_genre_pipeline(Genre.MYSTERY)
    choices = complete_first_choices(spec, "howdunit")
    choices[7]["clue_distribution"] = "not-a-real-option"

    result = validate_pipeline_choices(spec, "howdunit", choices)

    assert result.is_valid is False
    assert result.errors == [
        "Phase 7 field 'clue_distribution' has invalid option 'not-a-real-option'."
    ]


def test_completion_requires_every_selectable_field():
    spec = get_genre_pipeline(Genre.MYSTERY)
    choices = complete_first_choices(spec, "howdunit")
    del choices[4]["stakes"]

    result = validate_pipeline_choices(spec, "howdunit", choices, require_complete=True)

    assert result.is_valid is False
    assert "Phase 4 requires a 'stakes' selection." in result.errors
