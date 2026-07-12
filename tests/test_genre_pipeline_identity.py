import pytest
import inspect

from auteur.blueprint import Genre, StoryMode
from auteur.genre_pipeline.identity import IdentityCompilationError, compile_story_identity
from auteur.genre_pipeline.registry import get_all_genres, get_genre_pipeline
from auteur.genre_pipeline.templates import build_pipeline_descriptor
from auteur.netorare.identity_generator import IdentityGenerator
from auteur.structure.diagnostics import (
    DiagnosticLayer,
    DiagnosticSeverity,
    StructureDiagnostic,
)


def complete_choices(spec, core_id: str) -> dict[int, dict[str, str]]:
    descriptor = build_pipeline_descriptor(spec, core_id)
    choices = {
        phase.number: {field.id: field.options[0].id for field in phase.fields}
        for phase in descriptor.phases
        if phase.fields
    }
    if core_id == "paranoia":
        choices[8]["truth_ambiguity"] = "ambiguous"
    return choices


def test_every_core_compiles_a_contextual_valid_identity():
    for spec in get_all_genres():
        for core_id in spec.core_ids:
            result = compile_story_identity(spec, core_id, complete_choices(spec, core_id))
            identity = result.identity
            profile = spec.identity_profile_factory(core_id)

            assert identity.title == profile.default_title
            assert identity.title != "The Story"
            assert identity.story_type.genre == spec.genre
            assert identity.story_type.mode == profile.default_mode
            assert identity.target_experience.primary == spec.template_factory(core_id).primary_emotion
            assert identity.target_experience.progression == profile.progression
            assert identity.open_questions
            assert identity.alternatives
            assert not result.error_diagnostics


def test_title_and_mode_are_author_overridable():
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)

    result = compile_story_identity(
        spec,
        "tender_surrender",
        complete_choices(spec, "tender_surrender"),
        working_title="Held in Trust",
        mode=StoryMode.COMIC,
    )

    assert result.identity.title == "Held in Trust"
    assert result.identity.story_type.mode == StoryMode.COMIC


def test_invalid_choices_block_identity_compilation():
    spec = get_genre_pipeline(Genre.MYSTERY)
    choices = complete_choices(spec, "howdunit")
    choices[4]["want"] = "not-an-option"

    with pytest.raises(IdentityCompilationError, match="invalid option"):
        compile_story_identity(spec, "howdunit", choices)


def test_contextual_questions_and_alternatives_use_template_language():
    spec = get_genre_pipeline(Genre.MYSTERY)
    result = compile_story_identity(spec, "howdunit", complete_choices(spec, "howdunit"))

    assert any("investigation style" in question.lower() for question in result.identity.open_questions)
    assert any("logical deduction" in question.lower() for question in result.identity.open_questions)
    assert any("intuitive investigation" in alternative.lower() for alternative in result.identity.alternatives)


def test_legacy_identity_generator_delegates_to_neutral_compiler():
    spec = get_genre_pipeline(Genre.GENTLEFEMDOM)
    identity = IdentityGenerator.from_choices(
        "sensual_dominance",
        complete_choices(spec, "sensual_dominance"),
    )

    assert identity.story_type.mode == StoryMode.INTIMATE
    assert identity.title == "Untitled: Sensual Dominance"
    source = inspect.getsource(IdentityGenerator.from_choices)
    assert "get_genre_pipeline_for_core" in source
    assert "core_id in" not in source


def test_compilation_result_separates_warning_and_info_diagnostics():
    spec = get_genre_pipeline(Genre.MYSTERY)
    compiled = compile_story_identity(spec, "howdunit", complete_choices(spec, "howdunit"))
    warning = StructureDiagnostic(
        severity=DiagnosticSeverity.WARNING,
        layer=DiagnosticLayer.SCOPE,
        rule="test.warning",
        message="Warning diagnostic",
    )
    info = StructureDiagnostic(
        severity=DiagnosticSeverity.INFO,
        layer=DiagnosticLayer.SCOPE,
        rule="test.info",
        message="Informational diagnostic",
    )

    result = type(compiled)(compiled.identity, (warning, info))

    assert result.warning_diagnostics == (warning,)


def test_gentlefemdom_validation_has_no_legacy_identity_import():
    from pathlib import Path

    source = Path(__file__).parents[1].joinpath("src", "auteur", "gentlefemdom", "validation.py").read_text(encoding="utf-8")

    assert "auteur.netorare.identity_generator" not in source
