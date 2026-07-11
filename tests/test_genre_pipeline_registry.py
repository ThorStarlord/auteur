from auteur.blueprint import Genre, StoryMode
from auteur.genres.registry import get_all_genres, get_genre_pipeline


EXPECTED_MODES = {
    "classic_humiliation": StoryMode.TRAGIC,
    "horror": StoryMode.TRAGIC,
    "mystery": StoryMode.NOIR,
    "howdunit": StoryMode.PROCEDURAL,
    "paranoia": StoryMode.NOIR,
    "cozy": StoryMode.COMIC,
    "sensual_dominance": StoryMode.INTIMATE,
    "tender_surrender": StoryMode.INTIMATE,
    "romantic_authority": StoryMode.INTIMATE,
}


def test_built_in_pipeline_specs_expose_operational_runtime_fields():
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)

    assert spec.default_core_id == "sensual_dominance"
    assert spec.default_port == 8767
    assert spec.contract_loader().genre_id == "gentlefemdom"
    assert spec.identity_profile_factory("sensual_dominance").default_mode == StoryMode.INTIMATE


def test_every_core_has_a_unique_route_and_complete_identity_profile():
    seen: set[str] = set()

    for spec in get_all_genres():
        assert spec.default_core_id in spec.core_ids
        for core_id in spec.core_ids:
            assert core_id not in seen
            seen.add(core_id)

            profile = spec.identity_profile_factory(core_id)
            assert profile.display_name
            assert profile.default_title
            assert profile.progression
            assert profile.default_mode == EXPECTED_MODES[core_id]

    assert seen == set(EXPECTED_MODES)


def test_pipeline_spec_drops_catalog_only_fields():
    spec = get_genre_pipeline(Genre.MYSTERY)

    assert not hasattr(spec, "contract_file")
    assert not hasattr(spec, "session_dir_name")
    assert not hasattr(spec, "identity_strategy")


def test_auteur_genres_reexports_operational_registry_interfaces():
    from auteur.genres import (
        CoreIdentityProfile,
        GenrePipelineSpec,
        get_genre_pipeline_for_core,
    )

    spec = get_genre_pipeline_for_core("cozy")
    assert isinstance(spec, GenrePipelineSpec)
    assert isinstance(spec.identity_profile_factory("cozy"), CoreIdentityProfile)

