from pathlib import Path

from auteur.canonical_story import CanonicalStoryBootstrap
from auteur.expression.book import BookExpressionStore


def test_book_composes_accepts_stales_and_exports_from_accepted_chapters(tmp_path: Path) -> None:
    reference = Path("examples/canonical_story")
    bootstrap = CanonicalStoryBootstrap(reference)
    bootstrap.copy_to(tmp_path)
    bootstrap.accept_native_identity_and_structure(tmp_path)
    bootstrap.accept_scene_realizations(tmp_path)
    first = bootstrap.bootstrap_expressions(tmp_path)
    second = bootstrap.bootstrap_second_chapter(tmp_path)
    store = BookExpressionStore(tmp_path)
    initial = store.compose(["chapter_01", "chapter_02"], title="The Lantern at Low Water")
    store.accept(initial["book_expression_id"])
    assert initial["authority"] == "derived"
    assert [item["chapter_id"] for item in initial["chapters"]] == ["chapter_01", "chapter_02"]
    assert initial["chapters"][0]["content_hash"]
    assert "lantern" in store._path(initial["revision"], "md").read_text(encoding="utf-8").lower()
    revised = __import__("auteur.expression.composition", fromlist=["ChapterExpressionStore"]).ChapterExpressionStore(tmp_path).compose("chapter_01")
    __import__("auteur.expression.composition", fromlist=["ChapterExpressionStore"]).ChapterExpressionStore(tmp_path).accept(revised.artifact_id)
    assert store.inspect(initial["book_expression_id"])["freshness"] == "stale"
    recomposed = store.compose(["chapter_01", "chapter_02"], title="The Lantern at Low Water")
    assert recomposed["revision"] == 2
    accepted = store.accept(recomposed["book_expression_id"])
    assert accepted["lifecycle"] == "accepted"
    output = store.export(accepted["book_expression_id"], tmp_path / "export.md")
    assert "auteur:scene" not in output.read_text(encoding="utf-8")
