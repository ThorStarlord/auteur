from pathlib import Path

from auteur.expression.book import BookExpressionStore
from auteur.expression.book_reconciliation import BookReconciliationStore


def make_book(tmp_path: Path) -> tuple[Path, str]:
    project = tmp_path / "project"; project.mkdir(parents=True, exist_ok=True)
    from conftest import copy_bootstrap_template as _cbt
    _cbt(project)
    book = BookExpressionStore(project).compose(
        ["chapter_01", "chapter_02"], title="The Lantern at Low Water"
    )
    return project, book["book_expression_id"]


def test_marked_unchanged_book_has_no_findings_and_markerless_is_unresolved(tmp_path: Path) -> None:
    project, book_id = make_book(tmp_path)
    store = BookReconciliationStore(project)
    manuscript = project / "book" / "expression" / "book_v001.md"
    unchanged = store.inspect(manuscript, book_id)
    assert unchanged["status"] == "no_changes"
    markerless = project / "markerless.md"
    markerless.write_text("Plain manuscript text.", encoding="utf-8")
    result = store.inspect(markerless, book_id)
    assert result["status"] == "unresolved"
    assert [item["classification"] for item in result["unresolved_findings"]] == ["markerless"]


def test_separator_edit_creates_book_proposal_without_canonical_mutation(tmp_path: Path) -> None:
    project, book_id = make_book(tmp_path)
    book_path = project / "book" / "expression" / "book_v001.md"
    original = book_path.read_text(encoding="utf-8")
    edited = project / "edited.md"
    edited.write_text(original.replace("\n---\n", "\n***\n"), encoding="utf-8")
    store = BookReconciliationStore(project)
    inspection = store.inspect(edited, book_id)
    assert inspection["book_findings"][0]["classification"] == "separator_changed"
    routed = store.route(inspection["inspection_id"])
    assert routed["status"] == "routed"
    assert len(routed["book_proposals"]) == 1
    assert book_path.read_text(encoding="utf-8") == original


def test_stale_book_blocks_routing(tmp_path: Path) -> None:
    project, book_id = make_book(tmp_path)
    book = BookExpressionStore(project)
    manuscript = project / "book" / "expression" / "book_v001.md"
    inspection = BookReconciliationStore(project).inspect(manuscript, book_id)
    chapter_store = __import__("auteur.expression.composition", fromlist=["ChapterExpressionStore"]).ChapterExpressionStore(project)
    revised = chapter_store.compose("chapter_01")
    chapter_store.accept(revised.artifact_id)
    routed = BookReconciliationStore(project).route(inspection["inspection_id"])
    assert routed["status"] == "stale"
    assert not list((project / "book" / "expression" / "reconciliation" / "routing").glob("*"))
