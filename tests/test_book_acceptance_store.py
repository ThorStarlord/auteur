from __future__ import annotations

from pathlib import Path

import yaml

from auteur.expression.book_acceptance import BookAcceptanceStore
from auteur.expression.book_reconciliation import BookReconciliationStore


def test_acceptance_store_paths_match_facade(tmp_path: Path) -> None:
    store = BookAcceptanceStore(tmp_path)
    facade = BookReconciliationStore(tmp_path)

    assert facade._acceptances_dir() == store.acceptances_dir()
    assert facade._acceptance_path("accept_001") == store.acceptance_path("accept_001")
    assert facade._acceptance_manifest_path("accept_001") == store.acceptance_manifest_path(
        "accept_001"
    )
    assert facade._acceptance_staging_dir("accept_001") == store.acceptance_staging_dir(
        "accept_001"
    )
    assert facade._accepted_book_pointer_path() == store.accepted_book_pointer_path()
    assert facade._accepted_book_revision_path(
        "book_01", 2
    ) == store.accepted_book_revision_path("book_01", 2)


def test_facade_loads_pointer_revision_and_record_through_store(tmp_path: Path) -> None:
    store = BookAcceptanceStore(tmp_path)
    facade = BookReconciliationStore(tmp_path)

    pointer = {
        "artifact_type": "accepted_book_pointer",
        "book_expression_id": "book_01",
        "current_revision": 2,
    }
    pointer_path = store.accepted_book_pointer_path()
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text(yaml.safe_dump(pointer), encoding="utf-8")

    revision = {
        "artifact_type": "accepted_book_revision",
        "book_expression_id": "book_01",
        "revision": 2,
    }
    revision_path = store.accepted_book_revision_path("book_01", 2)
    revision_path.write_text(yaml.safe_dump(revision), encoding="utf-8")

    acceptance = {
        "acceptance_id": "accept_001",
        "source_comparison_id": "compare_001",
    }
    acceptance_path = store.acceptance_path("accept_001")
    acceptance_path.parent.mkdir(parents=True, exist_ok=True)
    acceptance_path.write_text(yaml.safe_dump(acceptance), encoding="utf-8")

    assert facade.current_accepted_book_pointer() == pointer
    assert facade.load_accepted_book_revision("book_01", 2) == revision
    assert facade.load_book_acceptance("accept_001") == acceptance
    assert facade._find_prior_acceptance("compare_001") == acceptance


def test_acceptance_store_missing_artifacts_preserve_errors(tmp_path: Path) -> None:
    store = BookAcceptanceStore(tmp_path)

    assert store.current_accepted_book_pointer() is None
    assert store.find_prior_acceptance("compare_missing") is None

    try:
        store.load_accepted_book_revision("book_01", 1)
    except FileNotFoundError as exc:
        assert "Accepted Book revision not found: book_01 v1" in str(exc)
    else:
        raise AssertionError("missing accepted Book revision should fail")

    try:
        store.load_book_acceptance("accept_missing")
    except FileNotFoundError as exc:
        assert "Book acceptance record not found: accept_missing" in str(exc)
    else:
        raise AssertionError("missing acceptance record should fail")
