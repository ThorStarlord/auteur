import json
import yaml

from auteur.blueprint import StoryMode
from auteur.genre_packs.models import AdherencePosture
from auteur.structure.analyzer import analyze_structure
from auteur.structure.diagnostics import DiagnosticSeverity
from tests.test_profile_diagnostic_visibility import _make_base_identity, _make_profile
from auteur.identity import compile_to_blueprint
from auteur.cli import main
import pytest


def _diagnostic_for(identity, *, required=None, rejected=None, pattern="transformative_resolution", posture=None):
    identity.genre_profile = _make_profile(
        required=required,
        rejected=rejected,
        pattern=pattern,
        posture=posture or AdherencePosture.CONVENTIONAL,
    )
    blueprint = compile_to_blueprint(identity)
    if required:
        blueprint.contract.expected_elements = [
            item for item in blueprint.contract.expected_elements
            if item not in required[:1]
        ]
    if rejected:
        blueprint.contract.expected_elements.append(rejected[0])
    return next(
        diagnostic for diagnostic in analyze_structure(
            blueprint,
            adherence_posture=posture,
        )
        if diagnostic.rule.startswith("profile.resolution_contract")
    )


def test_profile_severity_policy_covers_all_postures():
    from auteur.structure.profile_severity import severity_for_profile_diagnostic

    expected = {
        AdherencePosture.CONVENTIONAL: DiagnosticSeverity.ERROR,
        AdherencePosture.FLEXIBLE: DiagnosticSeverity.WARNING,
        AdherencePosture.REVISIONIST: DiagnosticSeverity.WARNING,
        AdherencePosture.SUBVERSIVE: DiagnosticSeverity.WARNING,
        AdherencePosture.DECONSTRUCTIVE: DiagnosticSeverity.INFO,
    }
    for posture, severity in expected.items():
        assert severity_for_profile_diagnostic(
            posture,
            "profile.resolution_contract.missing_required_outcome",
        ) == severity
        assert severity_for_profile_diagnostic(
            posture,
            "profile.resolution_contract.rejected_outcome_present",
        ) == severity
        assert severity_for_profile_diagnostic(
            posture,
            "profile.resolution_contract.ending_tone_conflict",
        ) == (DiagnosticSeverity.WARNING if posture != AdherencePosture.DECONSTRUCTIVE else DiagnosticSeverity.INFO)


def test_missing_posture_defaults_to_conventional_severity():
    from auteur.structure.profile_severity import severity_for_profile_diagnostic

    assert severity_for_profile_diagnostic(
        None,
        "profile.resolution_contract.missing_required_outcome",
    ) == DiagnosticSeverity.ERROR


def test_profile_diagnostic_contains_posture_metadata_and_explanation():
    identity = _make_base_identity()
    diagnostic = _diagnostic_for(
        identity,
        required=["missing_outcome"],
        posture=AdherencePosture.CONVENTIONAL,
    )

    assert diagnostic.severity == DiagnosticSeverity.ERROR
    assert diagnostic.genre_recommendation_flow["adherence_posture"] == "conventional"
    assert diagnostic.genre_recommendation_flow["effective_severity"] == "error"
    assert "CONVENTIONAL" in diagnostic.message
    assert "error rather than a warning" in diagnostic.message


def test_deconstructive_resolution_conflict_is_info_without_mutation():
    identity = _make_base_identity()
    identity.story_type.mode = StoryMode.COMIC
    diagnostic = _diagnostic_for(
        identity,
        pattern="dark_transgression_resolution",
        posture=AdherencePosture.DECONSTRUCTIVE,
    )

    assert diagnostic.rule == "profile.resolution_contract.ending_tone_conflict"
    assert diagnostic.severity == DiagnosticSeverity.INFO
    assert diagnostic.genre_recommendation_flow["adherence_posture"] == "deconstructive"


@pytest.mark.parametrize(
    ("posture", "expected"),
    [
        (AdherencePosture.CONVENTIONAL, DiagnosticSeverity.ERROR),
        (AdherencePosture.FLEXIBLE, DiagnosticSeverity.WARNING),
        (AdherencePosture.REVISIONIST, DiagnosticSeverity.WARNING),
        (AdherencePosture.SUBVERSIVE, DiagnosticSeverity.WARNING),
        (AdherencePosture.DECONSTRUCTIVE, DiagnosticSeverity.INFO),
    ],
)
def test_rejected_outcome_severity_follows_posture(posture, expected):
    identity = _make_base_identity()
    diagnostic = _diagnostic_for(
        identity,
        rejected=["rejected_outcome"],
        posture=posture,
    )

    assert diagnostic.rule == "profile.resolution_contract.rejected_outcome_present"
    assert diagnostic.severity == expected


@pytest.mark.parametrize("posture", list(AdherencePosture))
def test_ending_conflict_is_warning_except_deconstructive(posture):
    identity = _make_base_identity()
    identity.story_type.mode = StoryMode.COMIC
    diagnostic = _diagnostic_for(
        identity,
        pattern="dark_transgression_resolution",
        posture=posture,
    )

    expected = DiagnosticSeverity.INFO if posture is AdherencePosture.DECONSTRUCTIVE else DiagnosticSeverity.WARNING
    assert diagnostic.rule == "profile.resolution_contract.ending_tone_conflict"
    assert diagnostic.severity == expected


def test_conventional_error_does_not_block_compilation():
    identity = _make_base_identity()
    identity.genre_profile = _make_profile(
        required=["required_outcome"],
        posture=AdherencePosture.CONVENTIONAL,
    )
    blueprint = compile_to_blueprint(identity)
    blueprint.contract.expected_elements.clear()
    diagnostics = analyze_structure(blueprint, adherence_posture=AdherencePosture.CONVENTIONAL)

    assert any(d.severity == DiagnosticSeverity.ERROR for d in diagnostics if d.rule.startswith("profile."))
    assert blueprint.profile_derivation is not None


def test_override_suppresses_only_targeted_required_outcome():
    identity = _make_base_identity()
    identity.story_type.mode = StoryMode.COMIC
    identity.genre_profile = _make_profile(
        required=["overridden_outcome"],
        pattern="dark_transgression_resolution",
        posture=AdherencePosture.DECONSTRUCTIVE,
        overrides=[
            {
                "target_expectation": "accepted_resolution_contract.required_outcomes",
                "recommended_value": "overridden_outcome",
                "replacement_value": "replacement_outcome",
                "author_rationale": "Intentional divergence.",
            }
        ],
    )
    blueprint = compile_to_blueprint(identity)
    blueprint.contract.expected_elements = ["replacement_outcome"]
    diagnostics = analyze_structure(
        blueprint,
        adherence_posture=AdherencePosture.DECONSTRUCTIVE,
    )

    missing = [
        diagnostic for diagnostic in diagnostics
        if diagnostic.rule == "profile.resolution_contract.missing_required_outcome"
    ]
    assert len(missing) == 0
    assert any(d.rule == "profile.resolution_contract.ending_tone_conflict" for d in diagnostics)


def test_posture_survives_identity_round_trip():
    identity = _make_base_identity()
    identity.genre_profile = _make_profile(posture=AdherencePosture.REVISIONIST)
    reloaded = type(identity).model_validate(identity.model_dump(mode="json"))

    assert reloaded.genre_profile.adherence_posture is AdherencePosture.REVISIONIST


def test_public_json_and_human_outputs_share_posture_severity(tmp_path, capsys):
    identity = _make_base_identity()
    identity.genre_profile = _make_profile(
        required=["missing_outcome"],
        posture=AdherencePosture.CONVENTIONAL,
    )
    project = tmp_path / "project"
    project.mkdir()
    identity.to_yaml(project / "story_identity.yaml")
    blueprint = compile_to_blueprint(identity)
    blueprint.contract.expected_elements.clear()
    auteur_dir = project / ".auteur"
    auteur_dir.mkdir()
    (auteur_dir / "blueprint.yaml").write_text(
        yaml.safe_dump(blueprint.model_dump(mode="json"), sort_keys=False),
        encoding="utf-8",
    )

    assert main(["genre", "diagnose", "--project", str(project)]) == 0
    human = capsys.readouterr().out
    assert "[error]" in human
    assert "CONVENTIONAL" in human

    assert main(["genre", "diagnose", "--project", str(project), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    profile = next(item for item in payload if item["rule"].startswith("profile."))
    assert profile["severity"] == "error"
    assert profile["genre_recommendation_flow"]["adherence_posture"] == "conventional"
