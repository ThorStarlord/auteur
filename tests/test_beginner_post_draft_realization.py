import json
from pathlib import Path

from auteur.beginner.post_draft import project_chapter_outcome, project_next_chapter_context


def test_accepted_chapter_outcome_is_derived_without_mutating_bible(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "final.md").write_text("Maya learns the truth.\n", encoding="utf-8")
    bible = tmp_path / "bible.json"
    bible.write_text(json.dumps({"events": [{"chapter_index": 1, "summary": "truth revealed"}]}), encoding="utf-8")
    before = bible.read_text(encoding="utf-8")

    outcome = project_chapter_outcome(tmp_path, 1)

    assert outcome["accepted_expression"] == "final.md"
    assert outcome["events"] == [{"chapter_index": 1, "summary": "truth revealed"}]
    assert bible.read_text(encoding="utf-8") == before


def test_next_chapter_context_references_accepted_prior_chapter(tmp_path: Path) -> None:
    chapter = tmp_path / "chapters" / "01"
    chapter.mkdir(parents=True)
    (chapter / "final.md").write_text("accepted", encoding="utf-8")
    (tmp_path / "bible.json").write_text(json.dumps({"events": []}), encoding="utf-8")

    context = project_next_chapter_context(tmp_path, 2)

    assert context["chapter_index"] == 2
    assert context["prior_accepted_chapters"] == [1]
    assert context["prior_chapter_refs"][0]["path"] == "chapters/01/final.md"
