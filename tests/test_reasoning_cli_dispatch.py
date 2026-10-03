from __future__ import annotations

import json
from types import SimpleNamespace

import yaml

from auteur.reasoning.cli import dispatch_reasoning


def _review(tmp_path):
    path = tmp_path / "review.json"
    path.write_text(
        json.dumps(
            {
                "review_id": "review-1",
                "freshness": {"status": "fresh"},
                "priorities": [],
                "groups": [
                    {
                        "group_id": "structure",
                        "summary": "Structure concern",
                        "overlap_basis": "shared evidence",
                        "claim_refs": ["claim-1"],
                    }
                ],
                "critic_summaries": [],
                "source_reports": [],
            }
        ),
        encoding="utf-8",
    )
    return path


def _blueprint(tmp_path):
    path = tmp_path / "blueprint.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "identity": {
                    "title": "The Long Road",
                    "author_intent": "A veteran seeks redemption after betraying his unit.",
                    "length_class": "novel",
                    "genre": "literary",
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
                    "central_question": "Can harm be repaired without erasing it?",
                    "thesis": "Repair requires accountability rather than absolution.",
                    "motifs": ["maps"],
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_reasoning_review_dispatch_preserves_human_output(tmp_path, capsys) -> None:
    errors: list[str] = []
    rc = dispatch_reasoning(
        SimpleNamespace(
            reasoning_command="review",
            review=_review(tmp_path),
            json=False,
        ),
        errors.append,
    )

    assert rc == 0
    assert errors == []
    assert "Reasoning review review-1" in capsys.readouterr().out


def test_reasoning_inspect_dispatch_preserves_group_lookup(tmp_path, capsys) -> None:
    errors: list[str] = []
    rc = dispatch_reasoning(
        SimpleNamespace(
            reasoning_command="inspect",
            review=_review(tmp_path),
            group="structure",
            json=False,
        ),
        errors.append,
    )

    assert rc == 0
    assert errors == []
    output = capsys.readouterr().out
    assert "structure: Structure concern" in output
    assert "Claims: ['claim-1']" in output


def test_reasoning_dispatch_fails_closed_for_missing_review(tmp_path) -> None:
    errors: list[str] = []
    rc = dispatch_reasoning(
        SimpleNamespace(
            reasoning_command="review",
            review=tmp_path / "missing.json",
            json=False,
        ),
        errors.append,
    )

    assert rc == 1
    assert errors == [f"reasoning review not found: {tmp_path / 'missing.json'}"]



def test_reasoning_audience_dispatch_outputs_typed_json(tmp_path, capsys) -> None:
    errors: list[str] = []
    rc = dispatch_reasoning(
        SimpleNamespace(
            reasoning_command="audience",
            blueprint=_blueprint(tmp_path),
            json=True,
        ),
        errors.append,
    )

    assert rc == 0
    assert errors == []
    payload = json.loads(capsys.readouterr().out)
    assert payload["architecture"] == "mass_appeal_narrative_architecture"
    assert payload["authority_status"] == "DERIVED / NOT CANON"
    assert payload["available_evidence_stage"] == "identity"
    assert len(payload["findings"]) == 10


def test_reasoning_audience_dispatch_fails_closed_for_missing_blueprint(tmp_path) -> None:
    errors: list[str] = []
    missing = tmp_path / "missing.yaml"

    rc = dispatch_reasoning(
        SimpleNamespace(
            reasoning_command="audience",
            blueprint=missing,
            json=False,
        ),
        errors.append,
    )

    assert rc == 1
    assert errors == [f"blueprint not found: {missing}"]
