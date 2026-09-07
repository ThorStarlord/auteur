import json

from auteur.cli import main


def test_series_context_is_read_only_and_progressively_disclosed(tmp_path, capsys):
    records = tmp_path / "records.json"
    records.write_text(json.dumps([{
        "item_id": "promise-1",
        "kind": "promise",
        "summary": "The debt remains unpaid.",
        "book_number": 1,
        "status": "open",
        "dependent_books": [3],
    }]), encoding="utf-8")
    assert main(["series", "context", str(tmp_path), "--book", "3", "--records", str(records)]) == 0
    output = capsys.readouterr().out
    assert "Context before Book 3" in output
    assert "DERIVED / NOT CANON" in output
    assert not (tmp_path / "series_identity.yaml").exists()
