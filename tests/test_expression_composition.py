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
    assembly = store.compose("07", transitions={"scene_07_02->scene_07_01": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "text": "At dawn."}})
    assert assembly.transitions[0]["transition_id"] == "t1"
    assert assembly.section_map[1]["kind"] == "transition"
    with pytest.raises(ValueError, match="invalid Scene boundary"):
        store.compose("07", transitions={"scene_07_02->scene_07_01": {"before_scene": "scene_07_01", "after_scene": "scene_07_03", "text": "Wrong."}})


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
