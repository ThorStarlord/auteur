import pytest
from pydantic import ValidationError

from auteur.critic import CriticFinding, ValidationReport


def test_critic_finding_validates_severity():
    f = CriticFinding(
        critic="contract",
        severity="error",
        rule="forbidden_trope:chosen_one_prophecy",
        evidence="scene 2: 'the prophecy named him'",
        requested_change="remove all prophecy framing",
    )
    assert f.severity == "error"


def test_critic_finding_rejects_unknown_severity():
    with pytest.raises(ValidationError):
        CriticFinding(
            critic="contract",
            severity="bogus",
            rule="x",
            evidence="y",
            requested_change="z",
        )


def test_validation_report_passed_true_on_no_errors():
    report = ValidationReport(
        chapter_index=1,
        iteration=1,
        findings=[
            CriticFinding(
                critic="slop",
                severity="warning",
                rule="cliche",
                evidence="'a testament to'",
                requested_change="rephrase",
            ),
        ],
        passed=True,
    )
    assert report.passed is True


def test_validation_report_passed_false_on_any_error():
    report = ValidationReport(
        chapter_index=1,
        iteration=1,
        findings=[
            CriticFinding(
                critic="contract",
                severity="error",
                rule="r",
                evidence="e",
                requested_change="c",
            ),
        ],
        passed=False,
    )
    assert report.passed is False
