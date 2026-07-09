from __future__ import annotations

import json
import yaml

from auteur.cli import main


def _project(tmp_path):
    project = tmp_path / "project"
    chapter = project / "chapters" / "03"
    chapter.mkdir(parents=True)
    (chapter / "draft_v1.md").write_text("old\n", encoding="utf-8")
    (chapter / "draft_v2.md").write_text("Line one.\nLine two.\n", encoding="utf-8")
    (chapter / "final.md").write_text("final text\n", encoding="utf-8")
    (project / "bible.json").write_text('{"characters": {}}\n', encoding="utf-8")
    (project / "relations.yaml").write_text(
        yaml.safe_dump(
            {
                "relations": [
                    {
                        "id": "elena_marcus",
                        "from_character": "Elena",
                        "to_character": "Marcus",
                        "trust": 20,
                    }
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return project


def test_export_chapter_markdown_uses_latest_draft(tmp_path) -> None:
    project = _project(tmp_path)

    assert main(["export", "chapter", str(project), "3", "--format", "md"]) == 0

    exported = project / "exports" / "chapter_03" / "draft_v2.md"
    assert exported.read_text(encoding="utf-8") == "Line one.\nLine two.\n"


def test_import_chapter_markdown_writes_artifacts_and_does_not_mutate_canon(tmp_path) -> None:
    project = _project(tmp_path)
    edited = tmp_path / "edited.md"
    edited.write_text("Line one changed.\nLine two.\n", encoding="utf-8")
    original_draft = project / "chapters" / "03" / "draft_v2.md"
    original_relations = (project / "relations.yaml").read_text(encoding="utf-8")
    original_bible = (project / "bible.json").read_text(encoding="utf-8")

    assert main(["import", "chapter", str(project), "3", str(edited)]) == 0

    import_dirs = sorted((project / "imports" / "chapter_03").iterdir())
    artifact_dir = import_dirs[-1]
    assert (artifact_dir / "imported_draft.md").read_text(encoding="utf-8") == "Line one changed.\nLine two.\n"
    diff = json.loads((artifact_dir / "diff_report.json").read_text(encoding="utf-8"))
    assert diff["source_draft"] == "draft_v2.md"
    assert diff["changed_lines"][0]["old"] == "Line one."
    proposals = yaml.safe_load((artifact_dir / "canon_update_proposals.yaml").read_text(encoding="utf-8"))
    assert proposals["proposals"] == []
    assert original_draft.read_text(encoding="utf-8") == "Line one.\nLine two.\n"
    assert (project / "relations.yaml").read_text(encoding="utf-8") == original_relations
    assert (project / "bible.json").read_text(encoding="utf-8") == original_bible


def test_import_confirm_marks_proposal_without_updating_relations(tmp_path) -> None:
    project = _project(tmp_path)
    edited = tmp_path / "edited.md"
    edited.write_text("Line one changed.\nLine two.\n", encoding="utf-8")
    change_path = project / "chapters" / "03" / "relation_changes.yaml"
    change_path.write_text(
        yaml.safe_dump(
            {
                "chapter": 3,
                "relation_changes": [
                    {"relation": "elena_marcus", "trust": 5, "reason": "A warmer exchange."}
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    assert main(["import", "chapter", str(project), "3", str(edited)]) == 0
    artifact_dir = sorted((project / "imports" / "chapter_03").iterdir())[-1]
    proposals_path = artifact_dir / "canon_update_proposals.yaml"
    proposal_id = yaml.safe_load(proposals_path.read_text(encoding="utf-8"))["proposals"][0]["id"]

    assert main(["import", "confirm", str(project), "3", "--proposal", proposal_id]) == 0

    proposals = yaml.safe_load(proposals_path.read_text(encoding="utf-8"))
    assert proposals["proposals"][0]["status"] == "accepted"
    assert yaml.safe_load((project / "relations.yaml").read_text(encoding="utf-8"))["relations"][0]["trust"] == 20
