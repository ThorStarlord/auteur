from pathlib import Path

from auteur.revision import RevisionLedger


def test_revision_ledger_classifies_missing_artifact_as_blocking(tmp_path: Path) -> None:
    result = RevisionLedger(tmp_path).validate(tmp_path / "missing.yaml", "chapter_outline")

    assert result.status.value == "missing"
    assert result.blocking is True


def test_revision_ledger_classifies_untracked_artifact_as_unknown(tmp_path: Path) -> None:
    path = tmp_path / "story.yaml"
    path.write_text("id: story\n", encoding="utf-8")

    result = RevisionLedger(tmp_path).validate(path, "story")

    assert result.status.value == "unknown"
