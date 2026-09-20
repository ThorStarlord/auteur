from __future__ import annotations

from pathlib import Path

import yaml

from auteur.expression.book_application_artifacts import BookApplicationArtifactStore
from auteur.expression.book_reconciliation import BookReconciliationStore


def test_application_artifact_paths_match_facade(tmp_path: Path) -> None:
    store = BookApplicationArtifactStore(tmp_path)
    facade = BookReconciliationStore(tmp_path)

    assert facade._inspection_path("inspection_001") == store.inspection_path(
        "inspection_001"
    )
    assert facade._proposal_path("proposal_001") == store.proposal_path("proposal_001")
    assert facade._plan_path("plan_001") == store.plan_path("plan_001")
    assert facade._publication_path("publication_001") == store.publication_path(
        "publication_001"
    )


def test_facade_loads_application_artifacts_through_store(tmp_path: Path) -> None:
    store = BookApplicationArtifactStore(tmp_path)
    facade = BookReconciliationStore(tmp_path)

    artifacts = {
        store.inspection_path("inspection_001"): {
            "inspection_id": "inspection_001",
        },
        store.proposal_path("proposal_001"): {
            "proposal_id": "proposal_001",
        },
        store.plan_path("plan_001"): {
            "plan_id": "plan_001",
        },
        store.publication_path("publication_001"): {
            "publication_id": "publication_001",
        },
        store.preview_path("publication_001"): {
            "publication_id": "publication_001",
            "artifact_type": "book_application_preview",
        },
        store.candidate_path("candidate_001"): {
            "candidate_id": "candidate_001",
        },
    }
    for path, artifact in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(artifact), encoding="utf-8")

    assert facade._load_inspection("inspection_001") == artifacts[
        store.inspection_path("inspection_001")
    ]
    assert facade._load_proposal("proposal_001") == artifacts[
        store.proposal_path("proposal_001")
    ]
    assert facade._load_plan("plan_001") == artifacts[store.plan_path("plan_001")]
    assert facade.inspect_book_publication("publication_001") == artifacts[
        store.publication_path("publication_001")
    ]
    assert facade.load_book_preview("publication_001") == artifacts[
        store.preview_path("publication_001")
    ]
    assert facade.load_book_candidate("candidate_001") == artifacts[
        store.candidate_path("candidate_001")
    ]


def test_application_artifact_missing_behavior_is_preserved(tmp_path: Path) -> None:
    store = BookApplicationArtifactStore(tmp_path)

    assert store.load_proposal("proposal_missing") is None

    cases = [
        (lambda: store.load_inspection("inspection_missing"), "Book inspection not found"),
        (lambda: store.load_plan("plan_missing"), "Book application plan not found"),
        (lambda: store.load_publication("publication_missing"), "Book publication not found"),
        (lambda: store.load_preview("preview_missing"), "Book preview not found"),
        (lambda: store.load_candidate("candidate_missing"), "Book candidate not found"),
    ]
    for loader, expected in cases:
        try:
            loader()
        except FileNotFoundError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"missing artifact should fail: {expected}")
