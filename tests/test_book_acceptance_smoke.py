from __future__ import annotations

from pathlib import Path

from auteur.expression.book import BookExpressionStore
from auteur.expression.book_reconciliation import BookReconciliationStore
from conftest import copy_bootstrap_template


def test_book_acceptance_minimal_supported_path(tmp_path: Path) -> None:
    """Smallest deterministic Book-acceptance path used to distinguish regression from suite runtime."""
    project = tmp_path / "project"
    project.mkdir(parents=True)
    copy_bootstrap_template(project)

    book_store = BookExpressionStore(project)
    book = book_store.compose(["chapter_01", "chapter_02"], title="Acceptance Sentinel")
    book_store.accept(book["book_expression_id"])

    accepted_markdown = project / "book" / "expression" / "book_v001.md"
    external = project / "external.md"
    external.write_bytes(accepted_markdown.read_bytes())

    reconciliation = BookReconciliationStore(project)
    inspection = reconciliation.inspect(external, book["book_expression_id"])
    routed = reconciliation.route(inspection["inspection_id"])
    plan = reconciliation.plan(
        inspection["inspection_id"],
        [proposal_id for proposal_id in routed["book_proposals"]],
    )
    publication = reconciliation.publish(plan["plan_id"])
    ok, recomposed = reconciliation.recompose_book_from_accepted_sources(publication["publication_id"])
    assert ok

    ok, comparison = reconciliation.compare_book_recomposition(
        recomposed["recomposition_id"],
        external,
    )
    assert ok
    assert comparison["summary"]["ready_for_acceptance"] is True

    ok, accepted = reconciliation.accept_recomposed_book(comparison["comparison_id"])
    assert ok
    assert accepted["accepted_book_revision"]["authority"] == "accepted"
    assert accepted["accepted_book_revision"]["canonical"] is True
    assert reconciliation.current_accepted_book_pointer()["current_revision"] == 2
