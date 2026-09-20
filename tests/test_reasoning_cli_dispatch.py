from __future__ import annotations

import json
from types import SimpleNamespace

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
