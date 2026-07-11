import inspect

from auteur.blueprint import Genre, StoryMode
from auteur.genre_pipeline.registry import get_all_genres, get_genre_pipeline
from auteur.genre_pipeline.templates import build_pipeline_descriptor, normalize_template_options


def _phase(descriptor, number: int):
    return next(phase for phase in descriptor.phases if phase.number == number)


def test_every_built_in_core_produces_a_nine_phase_descriptor():
    for spec in get_all_genres():
        for core_id in spec.core_ids:
            descriptor = build_pipeline_descriptor(spec, core_id)

            assert [phase.number for phase in descriptor.phases] == list(range(1, 10))
            assert descriptor.genre == spec.genre
            assert descriptor.core_id == core_id
            assert descriptor.default_mode == spec.identity_profile_factory(core_id).default_mode
            assert StoryMode.INTIMATE in descriptor.available_modes


def test_optionless_netorare_context_phases_are_derived():
    spec = get_genre_pipeline(Genre.NETORARE)
    descriptor = build_pipeline_descriptor(spec, "classic_humiliation")

    for number in (1, 2, 3):
        phase = _phase(descriptor, number)
        assert phase.derived is True
        assert phase.fields == []
        assert phase.derived_summary


def test_flat_mystery_structural_forces_are_grouped_by_force():
    spec = get_genre_pipeline(Genre.MYSTERY)
    descriptor = build_pipeline_descriptor(spec, "howdunit")
    phase = _phase(descriptor, 4)

    assert [field.id for field in phase.fields] == [
        "want",
        "resistance",
        "conflict",
        "stakes",
        "change",
    ]
    assert all(field.options for field in phase.fields)


def test_flat_non_structural_options_use_the_phase_id_as_field_name():
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    descriptor = build_pipeline_descriptor(spec, "sensual_dominance")

    assert [field.id for field in _phase(descriptor, 5).fields] == ["boundary_clarity"]


def test_horror_exposes_the_inescapable_resistance_required_by_its_validator():
    spec = get_genre_pipeline(Genre.NETORARE)
    descriptor = build_pipeline_descriptor(spec, "horror")
    fields = {field.id: field for field in _phase(descriptor, 4).fields}

    assert [option.id for option in fields["resistance"].options] == ["resistance-inescapable"]


def test_template_normalization_contains_no_genre_name_dispatch():
    source = inspect.getsource(normalize_template_options)

    assert "Genre." not in source
    assert "spec.genre" not in source
