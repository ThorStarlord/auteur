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
    manifest = json.loads((artifact_dir / "import_manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] == artifact_dir.name
    assert manifest["chapter"] == 3
    assert manifest["source_draft"] == "draft_v2.md"
    assert (artifact_dir / "imported_draft.md").read_text(encoding="utf-8") == "Line one changed.\nLine two.\n"
    diff = json.loads((artifact_dir / "diff_report.json").read_text(encoding="utf-8"))
    assert diff["source_draft"] == "draft_v2.md"
    assert diff["changed_lines"][0]["old"] == "Line one."
    proposals = yaml.safe_load((artifact_dir / "canon_update_proposals.yaml").read_text(encoding="utf-8"))
    assert proposals["proposals"] == []
    assert original_draft.read_text(encoding="utf-8") == "Line one.\nLine two.\n"
    assert (project / "relations.yaml").read_text(encoding="utf-8") == original_relations
    assert (project / "bible.json").read_text(encoding="utf-8") == original_bible


def test_import_strips_bom_from_diff_report_and_imported_artifact(tmp_path) -> None:
    project = _project(tmp_path)
    source = project / "chapters" / "03" / "draft_v2.md"
    source.write_text("\ufeffLine one.\nLine two.\n", encoding="utf-8")
    edited = tmp_path / "edited.md"
    edited.write_text("\ufeffLine one changed.\nLine two.\n", encoding="utf-8")

    assert main(["import", "chapter", str(project), "3", str(edited)]) == 0

    artifact_dir = sorted((project / "imports" / "chapter_03").iterdir())[-1]
    imported = (artifact_dir / "imported_draft.md").read_text(encoding="utf-8")
    diff = json.loads((artifact_dir / "diff_report.json").read_text(encoding="utf-8"))
    assert "\ufeff" not in imported
    assert "\ufeff" not in json.dumps(diff)


def test_import_drift_report_declares_analysis_mode(tmp_path) -> None:
    project = _project(tmp_path)
    edited = tmp_path / "edited.md"
    edited.write_text("Line one changed.\nLine two.\n", encoding="utf-8")

    assert main(["import", "chapter", str(project), "3", str(edited)]) == 0

    artifact_dir = sorted((project / "imports" / "chapter_03").iterdir())[-1]
    drift = json.loads((artifact_dir / "drift_report.json").read_text(encoding="utf-8"))
    assert drift["analysis_mode"] == "declared_relation_changes"
    assert "relation_changes.yaml" in drift["note"]


def test_import_cli_output_includes_next_step_commands(tmp_path, capsys) -> None:
    project = _project(tmp_path)
    edited = tmp_path / "edited.md"
    edited.write_text("Line one changed.\nLine two.\n", encoding="utf-8")

    assert main(["import", "chapter", str(project), "3", str(edited)]) == 0

    captured = capsys.readouterr()
    assert "Import run ID:" in captured.out
    assert "auteur import promote-draft" in captured.out
    assert "auteur import confirm" in captured.out


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

    assert main(["import", "confirm", str(project), "3", "--run", artifact_dir.name, "--proposal", proposal_id]) == 0

    proposals = yaml.safe_load(proposals_path.read_text(encoding="utf-8"))
    assert proposals["proposals"][0]["status"] == "accepted"
    assert yaml.safe_load((project / "relations.yaml").read_text(encoding="utf-8"))["relations"][0]["trust"] == 20


def test_import_confirm_targets_selected_run_not_latest(tmp_path) -> None:
    project = _project(tmp_path)
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
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"
    first.write_text("First import.\n", encoding="utf-8")
    second.write_text("Second import.\n", encoding="utf-8")
    assert main(["import", "chapter", str(project), "3", str(first)]) == 0
    first_run = sorted((project / "imports" / "chapter_03").iterdir())[-1].name
    assert main(["import", "chapter", str(project), "3", str(second)]) == 0
    runs = sorted((project / "imports" / "chapter_03").iterdir())
    first_dir = project / "imports" / "chapter_03" / first_run
    latest_dir = runs[-1]
    proposal_id = yaml.safe_load((first_dir / "canon_update_proposals.yaml").read_text(encoding="utf-8"))[
        "proposals"
    ][0]["id"]

    assert main(["import", "confirm", str(project), "3", "--run", first_run, "--proposal", proposal_id]) == 0

    first_proposals = yaml.safe_load((first_dir / "canon_update_proposals.yaml").read_text(encoding="utf-8"))
    latest_proposals = yaml.safe_load((latest_dir / "canon_update_proposals.yaml").read_text(encoding="utf-8"))
    assert first_proposals["proposals"][0]["status"] == "accepted"
    assert latest_proposals["proposals"][0]["status"] == "proposed"


def test_import_confirm_wrong_run_fails(tmp_path) -> None:
    project = _project(tmp_path)
    edited = tmp_path / "edited.md"
    edited.write_text("Line one changed.\nLine two.\n", encoding="utf-8")
    assert main(["import", "chapter", str(project), "3", str(edited)]) == 0

    assert main(["import", "confirm", str(project), "3", "--run", "missing_run", "--proposal", "proposal"]) != 0


def test_import_promote_draft_writes_next_draft_without_mutating_canon(tmp_path) -> None:
    project = _project(tmp_path)
    edited = tmp_path / "edited.md"
    edited.write_text("Promoted imported text.\n", encoding="utf-8")
    original_final = (project / "chapters" / "03" / "final.md").read_text(encoding="utf-8")
    original_bible = (project / "bible.json").read_text(encoding="utf-8")
    original_relations = (project / "relations.yaml").read_text(encoding="utf-8")
    assert main(["import", "chapter", str(project), "3", str(edited)]) == 0
    run_id = sorted((project / "imports" / "chapter_03").iterdir())[-1].name

    assert main(["import", "promote-draft", str(project), "3", "--run", run_id]) == 0

    chapter_dir = project / "chapters" / "03"
    assert (chapter_dir / "draft_v3.md").read_text(encoding="utf-8") == "Promoted imported text.\n"
    assert (chapter_dir / "draft_v2.md").read_text(encoding="utf-8") == "Line one.\nLine two.\n"
    assert (chapter_dir / "final.md").read_text(encoding="utf-8") == original_final
    assert (project / "bible.json").read_text(encoding="utf-8") == original_bible
    assert (project / "relations.yaml").read_text(encoding="utf-8") == original_relations
