from pathlib import Path

import pytest
import yaml

from auteur.expression import ChapterExpressionStore, ExpressionStore
from auteur.provenance import ArtifactStore, Lifecycle


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def make_project(tmp_path: Path) -> tuple[Path, list[Path], Path]:
    project = tmp_path / "project"
    outline = project / "chapter_07.yaml"
    write_yaml(outline, {"id": "chapter_07", "chapter_id": "chapter_07", "scenes": ["scene_07_02", "scene_07_01", "scene_07_03"]})
    ArtifactStore(project).accept(outline, "chapter_outline")
    scenes = []
    expressions = ExpressionStore(project)
    for scene_id in ("scene_07_01", "scene_07_02", "scene_07_03"):
        scene = project / "chapters" / "07" / "scenes" / f"{scene_id}.yaml"
        write_yaml(scene, {"id": scene_id, "chapter_id": "chapter_07", "participants": ["mara"], "pov_character_id": "mara", "outcome": f"outcome for {scene_id}"})
        ArtifactStore(project).accept(scene, "scene_realization")
        candidate = expressions.generate(scene, f"Prose for {scene_id}.")
        expressions.accept(candidate.candidate_id)
        scenes.append(scene)
    return project, scenes, outline


def test_three_accepted_scene_expressions_compose_with_markers_and_section_map(tmp_path: Path) -> None:
    project, scenes, _ = make_project(tmp_path)
    before = {scene: scene.read_text(encoding="utf-8") for scene in scenes}
    store = ChapterExpressionStore(project)
    assembly = store.compose("07")
    text = (store.chapter_dir("07") / "chapter_v001.md").read_text(encoding="utf-8")
    assert assembly.artifact_type == "expression_chapter"
    assert [item["scene_id"] for item in assembly.source_scenes] == ["scene_07_02", "scene_07_01", "scene_07_03"]
    assert "<!-- auteur:scene id=scene_07_02 expression_revision=1 -->" in text
    assert "<!-- auteur:end-scene id=scene_07_03 -->" in text
    assert assembly.section_map[0]["section_id"] == "scene_07_02"
    assert {scene: scene.read_text(encoding="utf-8") for scene in scenes} == before


def test_mixed_scene_expression_revisions_are_valid(tmp_path: Path) -> None:
    project, scenes, _ = make_project(tmp_path)
    expressions = ExpressionStore(project)
    expressions.generate(scenes[0], "Replacement prose.")
    expressions.accept("scene_07_01:prose_v002")
    assembly = ChapterExpressionStore(project).compose("chapter_07")
    selected = {item["scene_id"]: item["expression_revision"] for item in assembly.source_scenes}
    assert selected["scene_07_01"] == 2
    assert set(selected.values()) == {1, 2}


def test_missing_or_rejected_scene_expression_blocks_composition(tmp_path: Path) -> None:
    project, scenes, _ = make_project(tmp_path)
    accepted = project / "chapters" / "07" / "scenes" / "scene_07_02" / "accepted.yaml"
    metadata = yaml.safe_load(accepted.read_text(encoding="utf-8"))
    metadata["lifecycle"] = Lifecycle.REJECTED.value
    accepted.write_text(yaml.safe_dump(metadata, sort_keys=False), encoding="utf-8")
    with pytest.raises(ValueError, match="not accepted"):
        ChapterExpressionStore(project).compose("07")
    assert not (ChapterExpressionStore(project).chapter_dir("07") / "chapter_v001.md").exists()


def test_transition_is_chapter_owned_and_boundary_is_validated(tmp_path: Path) -> None:
    project, _, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    assembly = store.compose("07", transitions={"t1": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "text": "At dawn."}})
    assert assembly.transitions[0]["transition_id"] == "t1"
    assert assembly.section_map[1]["kind"] == "transition"
    with pytest.raises(ValueError, match="invalid Scene boundary"):
        store.compose("07", transitions={"bad": {"before_scene": "scene_07_02", "after_scene": "scene_07_03", "text": "Wrong."}})


def test_acceptance_preserves_versions_and_staleness_is_dependency_specific(tmp_path: Path) -> None:
    project, scenes, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    first = store.compose("07")
    store.accept(first.artifact_id, accepted_by="author")
    second = store.compose("07")
    store.accept(second.artifact_id, accepted_by="author")
    assert store.inspect(first.artifact_id).lifecycle is Lifecycle.REPLACED
    assert (store.chapter_dir("07") / "chapter_v001.md").exists()
    changed = scenes[0]
    changed.write_text(changed.read_text(encoding="utf-8").replace("outcome for scene_07_01", "changed outcome"), encoding="utf-8")
    status = store.status(second.artifact_id)
    assert status["freshness"] == "stale"
    assert any(item["scene_id"] == "scene_07_01" for item in status["stale_reasons"])


def test_clean_export_removes_markers_but_internal_manuscript_keeps_them(tmp_path: Path) -> None:
    project, _, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    assembly = store.compose("07")
    clean = store.clean_export(assembly.artifact_id)
    assert "auteur:scene" not in clean
    assert "Prose for scene_07_01." in clean


def test_marker_inspection_maps_marked_text_and_flags_markerless_divergence(tmp_path: Path) -> None:
    project, _, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    assembly = store.compose("07")
    manuscript = (store.chapter_dir("07") / "chapter_v001.md").read_text(encoding="utf-8")
    assert store.inspect_markers(manuscript)["status"] == "mapped"
    assert store.inspect_markers("Edited chapter without markers.")["status"] == "unresolved_divergence"


def test_divergent_scene_section_requires_chapter_review_acknowledgement(tmp_path: Path) -> None:
    project, scenes, _ = make_project(tmp_path)
    expressions = ExpressionStore(project)
    candidate = expressions.generate(scenes[0], "Divergent prose.")
    scene_dir = scenes[0].parent / scenes[0].stem
    accepted = yaml.safe_load((scene_dir / "accepted.yaml").read_text(encoding="utf-8"))
    accepted["lifecycle"] = "accepted"
    accepted["review_state"] = "acknowledged_divergence"
    accepted["reviewed_source"] = accepted.get("source_scene")
    (scene_dir / "accepted.yaml").write_text(yaml.safe_dump(accepted, sort_keys=False), encoding="utf-8")
    candidate_meta = scene_dir / "prose_v001.yaml"
    candidate_meta.write_text(yaml.safe_dump(accepted, sort_keys=False), encoding="utf-8")
    assembly = ChapterExpressionStore(project).compose("07")
    assert assembly.review_state.value == "review_required"
    with pytest.raises(ValueError, match="requires explicit review"):
        ChapterExpressionStore(project).accept(assembly.artifact_id)


def test_transition_manifest_change_stales_assembly_and_event_requires_review(tmp_path: Path) -> None:
    project, _, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    transition = {"t1": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "revision": 1, "lifecycle": "accepted", "text": "Mara crossed the hall.", "declared_events": ["new revelation"]}}
    assembly = store.compose("07", transitions=transition)
    assert assembly.review_state.value == "review_required"
    transition["t1"]["text"] = "The archive fell silent."
    store.save_transitions("07", transition)
    status = store.status(assembly.artifact_id)
    assert any(item["code"] == "transition_changed" for item in status["stale_reasons"])


def test_transition_boundary_and_lifecycle_are_validated(tmp_path: Path) -> None:
    project, _, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    with pytest.raises(ValueError, match="invalid Scene boundary"):
        store.compose("07", transitions={"bad": {"transition_id": "bad", "before_scene": "scene_07_02", "after_scene": "scene_07_03", "text": "Wrong boundary."}})
    assembly = store.compose("07", transitions={"t1": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "lifecycle": "archived", "text": "Old bridge."}})
    assert store.status(assembly.artifact_id)["health"] == "invalid"


def test_strict_marker_inspection_reports_malformed_and_mismatched_markers(tmp_path: Path) -> None:
    report = ChapterExpressionStore(tmp_path).inspect_markers("""<!-- auteur:scene id=scene_01 expression_revision=x -->\nText\n<!-- auteur:end-scene id=scene_02 -->""")
    codes = {finding["code"] for finding in report["findings"]}
    assert "malformed_marker" in codes
    assert "ambiguous_marker" in codes
    assert all("line" in finding and "recommended_action" in finding for finding in report["findings"])


def test_marked_and_markerless_manuscript_reports_are_read_only(tmp_path: Path) -> None:
    project, scenes, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    assembly = store.compose("07")
    manuscript = store.chapter_dir("07") / "external.md"
    original_scene = scenes[0].read_text(encoding="utf-8")
    internal = (store.chapter_dir("07") / "chapter_v001.md").read_text(encoding="utf-8")
    manuscript.write_text(internal.replace("Prose for scene_07_02.", "Edited Scene Two."), encoding="utf-8")
    report = store.inspect_manuscript(manuscript, assembly.artifact_id)
    assert report["modified"][0]["scene_id"] == "scene_07_02"
    manuscript.write_text("Markerless edited manuscript.", encoding="utf-8")
    unresolved = store.inspect_manuscript(manuscript, assembly.artifact_id)
    assert unresolved["status"] == "unresolved_divergence"
    assert scenes[0].read_text(encoding="utf-8") == original_scene


def test_export_and_chapter_comparison_cli(tmp_path: Path, capsys) -> None:
    from auteur.cli import main
    project, _, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    first = store.compose("07")
    second = store.compose("07", transitions={"t1": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "text": "At dusk."}})
    output = tmp_path / "clean.md"
    assert main(["expression", "export-chapter", first.artifact_id, "--project", str(project), "--output", str(output), "--clean"]) == 0
    assert "auteur:scene" not in output.read_text(encoding="utf-8")
    assert main(["expression", "compare-chapters", first.artifact_id, second.artifact_id, "--project", str(project)]) == 0
    assert "transitions_a" in capsys.readouterr().out
