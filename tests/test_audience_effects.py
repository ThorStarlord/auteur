"""Tests for Mass-Appeal Narrative Architecture (MANA) audience-effect diagnostics."""

from __future__ import annotations

from copy import deepcopy

from auteur.audience_effects import (
    AudienceEffectDimension,
    AudienceEffectState,
    AudienceEvidenceStage,
    EpistemicBasis,
    analyze_audience_effects,
)
from auteur.blueprint import StoryBlueprint


def _base_data() -> dict:
    return {
        "identity": {
            "title": "The Long Road",
            "author_intent": "A war veteran seeks redemption after betraying his unit.",
            "length_class": "novel",
            "genre": "literary",
            "mode": "tragic",
            "target_audience": "adult",
            "pov_type": "third_person_limited_single",
        },
        "contract": {
            "content_rating": "R",
            "mandatory_ending_tone": "bittersweet",
        },
        "emotional_design": {
            "overall_emotional_arc": "guilt -> confrontation -> partial absolution",
        },
        "theme": {
            "central_question": "Can a person be forgiven for a cowardly act they cannot undo?",
            "thesis": "Redemption is possible only when the self-lie is dismantled.",
            "motifs": ["silence", "uniforms", "maps"],
        },
    }


def _identity_blueprint() -> StoryBlueprint:
    return StoryBlueprint.model_validate(_base_data())


def _structure_blueprint() -> StoryBlueprint:
    data = _base_data()
    data["identity"]["target_experience"] = {
        "primary": "painful hope",
        "progression": "guilt -> dread -> earned release",
    }
    data["story_engine"] = {
        "main_thread": {
            "type": "main_plot",
            "want": {
                "author_text": "The veteran wants to repair the life he broke.",
                "checkable_claims": [],
            },
            "resistance": {
                "author_text": "The people he betrayed no longer trust his motives.",
                "checkable_claims": [],
            },
            "conflict": {
                "author_text": "Every attempt at repair exposes another concealed betrayal.",
                "checkable_claims": [],
            },
            "stakes": {
                "author_text": "He may lose his remaining family and the possibility of forgiveness.",
                "checkable_claims": [],
            },
            "change": {
                "author_text": "He stops seeking absolution and chooses accountable repair.",
                "checkable_claims": [],
            },
            "thematic_function": "Tests whether redemption can exist without erasing harm.",
        },
        "threads": [],
    }
    data["contract"]["expected_elements"] = ["public confession", "irreversible repair choice"]
    data["tension_waveform"] = {
        "target_curve": [
            {"chapter_index": 1, "score": 3, "label": "uneasy_return"},
            {"chapter_index": 12, "score": 7, "label": "truth_reversal"},
            {"chapter_index": 24, "score": 10, "label": "climax_confession"},
        ],
        "realized_scores": [],
    }
    return StoryBlueprint.model_validate(data)


def _by_dimension(report, dimension: AudienceEffectDimension):
    return next(item for item in report.findings if item.dimension is dimension)


def test_identity_stage_refuses_to_invent_structure_evidence():
    report = analyze_audience_effects(_identity_blueprint())

    assert report.available_evidence_stage is AudienceEvidenceStage.IDENTITY
    assert _by_dimension(
        report, AudienceEffectDimension.NARRATIVE_LEGIBILITY
    ).state is AudienceEffectState.SUPPORTED
    assert _by_dimension(
        report, AudienceEffectDimension.MOTIVATIONAL_ATTACHMENT
    ).state is AudienceEffectState.UNESTABLISHED
    assert _by_dimension(
        report, AudienceEffectDimension.PREDICTIVE_ENGAGEMENT
    ).state is AudienceEffectState.NOT_YET_ASSESSABLE


def test_structure_stage_uses_existing_engine_and_reader_promise():
    report = analyze_audience_effects(_structure_blueprint())

    assert report.available_evidence_stage is AudienceEvidenceStage.STRUCTURE
    assert _by_dimension(
        report, AudienceEffectDimension.MOTIVATIONAL_ATTACHMENT
    ).state is AudienceEffectState.SUPPORTED
    assert _by_dimension(
        report, AudienceEffectDimension.PREDICTIVE_ENGAGEMENT
    ).state is AudienceEffectState.SUPPORTED
    assert _by_dimension(
        report, AudienceEffectDimension.EMOTIONAL_LEGIBILITY
    ).state is AudienceEffectState.SUPPORTED
    assert _by_dimension(
        report, AudienceEffectDimension.PAYOFF_ARCHITECTURE
    ).state is AudienceEffectState.SUPPORTED


def test_blueprint_only_report_marks_later_claims_not_yet_assessable():
    report = analyze_audience_effects(_structure_blueprint())

    for dimension in (
        AudienceEffectDimension.GROUNDED_CREDIBILITY,
        AudienceEffectDimension.AFFECTIVE_COMMITMENT,
        AudienceEffectDimension.MEMORABILITY,
        AudienceEffectDimension.TRANSMISSION,
    ):
        assert _by_dimension(
            report, dimension
        ).state is AudienceEffectState.NOT_YET_ASSESSABLE


def test_guidance_is_noncanonical_and_only_targets_current_gaps():
    report = analyze_audience_effects(_identity_blueprint())
    guided = {item.dimension for item in report.guidance}

    assert AudienceEffectDimension.MOTIVATIONAL_ATTACHMENT in guided
    assert AudienceEffectDimension.EMOTIONAL_LEGIBILITY in guided
    assert AudienceEffectDimension.GROUNDED_CREDIBILITY not in guided
    assert all(item.authority_status == "DERIVED / NOT CANON" for item in report.guidance)


def test_report_contains_epistemic_basis_but_no_mass_appeal_score():
    report = analyze_audience_effects(_structure_blueprint())
    payload = report.model_dump(mode="json")

    assert "score" not in payload
    assert "probability" not in payload
    assert all(
        EpistemicBasis.PROJECT_EVIDENCE in finding.epistemic_basis
        for finding in report.findings
    )

    def _keys(value):
        if isinstance(value, dict):
            for key, item in value.items():
                yield key
                yield from _keys(item)
        elif isinstance(value, list):
            for item in value:
                yield from _keys(item)

    keys = set(_keys(payload))
    assert "score" not in keys
    assert "probability" not in keys


def test_analysis_does_not_mutate_blueprint():
    blueprint = _structure_blueprint()
    before = deepcopy(blueprint.model_dump(mode="json"))

    analyze_audience_effects(blueprint)

    assert blueprint.model_dump(mode="json") == before
