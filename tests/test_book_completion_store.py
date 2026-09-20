from __future__ import annotations

from pathlib import Path

import yaml

from auteur.expression.book_completion import BookCompletionStore
from auteur.expression.book_reconciliation import BookReconciliationStore


def test_completion_store_paths_match_facade(tmp_path: Path) -> None:
    store = BookCompletionStore(tmp_path)
    facade = BookReconciliationStore(tmp_path)

    assert facade._completions_dir() == store.completions_dir()
    assert facade._completion_path("complete_001") == store.completion_path(
        "complete_001"
    )
    assert facade._completion_manifest_path(
        "complete_001"
    ) == store.completion_manifest_path("complete_001")
    assert facade._completion_staging_dir(
        "complete_001"
    ) == store.completion_staging_dir("complete_001")


def test_facade_loads_and_finds_completion_through_store(tmp_path: Path) -> None:
    store = BookCompletionStore(tmp_path)
    facade = BookReconciliationStore(tmp_path)

    completion = {
        "completion_id": "complete_001",
        "source_acceptance_id": "accept_001",
        "artifact_type": "book_reconciliation_completion",
    }
    path = store.completion_path("complete_001")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(completion), encoding="utf-8")

    assert facade.load_book_reconciliation_completion("complete_001") == completion
    assert facade._find_prior_completion("accept_001") == completion


def test_completion_store_missing_artifacts_preserve_errors(tmp_path: Path) -> None:
    store = BookCompletionStore(tmp_path)

    assert store.find_prior_completion("accept_missing") is None

    try:
        store.load_completion("complete_missing")
    except FileNotFoundError as exc:
        assert "Book reconciliation completion not found: complete_missing" in str(exc)
    else:
        raise AssertionError("missing reconciliation completion should fail")
