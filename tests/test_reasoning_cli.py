import json

from auteur.cli import main


def test_reasoning_review_cli_is_concise_and_json_is_explicit(tmp_path, capsys):
    path = tmp_path / "review.json"
    path.write_text(json.dumps({
        "review_id": "r1", "freshness": {"status": "fresh", "stale_reports": []},
        "groups": [{"group_id": "group-1", "summary": "Inspect setup", "conflict": False}],
        "priorities": [{"group_id": "group-1", "rank": 1}],
        "source_reports": [{"report_id": "source-1"}],
    }))
    assert main(["reasoning", "review", str(path)]) == 0
    output = capsys.readouterr().out
    assert "Top concerns:" in output
    assert "--json" in output
    assert main(["reasoning", "inspect", str(path), "group-1", "--json"]) == 0
    assert '"group_id": "group-1"' in capsys.readouterr().out
