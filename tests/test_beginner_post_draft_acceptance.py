import json
from pathlib import Path

from auteur.beginner.post_draft import accept_latest_chapter


def test_acceptance_bridge_delegates_once_and_records_receipt(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    calls: list[int] = []

    def owner(root: Path, index: int) -> object:
        calls.append(index)
        (root / "chapters" / "01" / "final.md").write_text("candidate", encoding="utf-8")
        return {"accepted": True}

    first = accept_latest_chapter(tmp_path, 1, command_id="cmd-1", owner=owner)
    second = accept_latest_chapter(tmp_path, 1, command_id="cmd-1", owner=owner)

    assert first.reconciled is False
    assert second.reconciled is True
    assert calls == [1]
    receipt = tmp_path / ".auteur" / "beginner" / "acceptance" / "1-cmd-1.json"
    assert json.loads(receipt.read_text(encoding="utf-8"))["status"] == "complete"


def test_acceptance_retry_reconciles_after_owner_crash(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "draft_v1.md").write_text("candidate", encoding="utf-8")
    calls = 0

    def owner(root: Path, index: int) -> object:
        nonlocal calls
        calls += 1
        (root / "chapters" / "01" / "final.md").write_text("candidate", encoding="utf-8")
        if calls == 1:
            raise RuntimeError("crash after authority")
        return {"accepted": True}

    try:
        accept_latest_chapter(tmp_path, 1, command_id="cmd-2", owner=owner)
    except RuntimeError:
        pass

    result = accept_latest_chapter(tmp_path, 1, command_id="cmd-2", owner=owner)

    assert result.reconciled is True
    assert calls == 1

