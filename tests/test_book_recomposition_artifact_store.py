from __future__ import annotations

from pathlib import Path

from auteur.expression.book_recomposition_artifacts import (
    BookRecompositionArtifactStore,
)
from auteur.expression.book_reconciliation import BookReconciliationStore


def test_recomposition_artifact_paths_match_facade(tmp_path: Path) -> None:
    store = BookRecompositionArtifactStore(tmp_path)
    facade = BookReconciliationStore(tmp_path)

    assert facade._recompositions_dir() == store.recompositions_dir()
    assert facade._recomposition_path("pub_001") == store.recomposition_path("pub_001")
    assert facade._comparisons_dir() == store.comparisons_dir()
    assert facade._comparison_path("cmp_001") == store.comparison_path("cmp_001")


def test_facade_roundtrips_recomposition_and_comparison(tmp_path: Path) -> None:
    store = BookRecompositionArtifactStore(tmp_path)
    facade = BookReconciliationStore(tmp_path)

    recomposed = {
        "recomposition_id": "book_recomposition_pub_001",
        "publication_id": "pub_001",
        "authority": "derived",
        "lifecycle": "proposed",
    }
    facade._store_recomposed_book(recomposed)

    comparison = {
        "comparison_id": "cmp_001",
        "artifact_type": "book_recomposition_comparison",
        "authority": "derived",
        "lifecycle": "evaluated",
    }
    facade._store_comparison_report(comparison)

    assert facade.load_recomposed_book("pub_001") == recomposed
    assert facade.load_book_comparison("cmp_001") == comparison
    assert store.load_recomposed_book("pub_001") == recomposed
    assert store.load_book_comparison("cmp_001") == comparison


def test_recomposition_store_missing_artifacts_preserve_errors(tmp_path: Path) -> None:
    store = BookRecompositionArtifactStore(tmp_path)

    try:
        store.load_recomposed_book("pub_missing")
    except FileNotFoundError as exc:
        assert "Book recomposition not found: pub_missing" in str(exc)
    else:
        raise AssertionError("missing recomposition should fail")

    try:
        store.load_book_comparison("cmp_missing")
    except FileNotFoundError as exc:
        assert "Book comparison not found: cmp_missing" in str(exc)
    else:
        raise AssertionError("missing comparison should fail")
