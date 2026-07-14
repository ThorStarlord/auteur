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


def test_reconciliation_inspection_and_scene_patch_proposal_are_noncanonical(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, scenes, _ = make_project(tmp_path)
    assembly_store = ChapterExpressionStore(project)
    assembly = assembly_store.compose("07")
    manuscript = assembly_store.chapter_dir("07") / "edited.md"
    text = (assembly_store.chapter_dir("07") / "chapter_v001.md").read_text(encoding="utf-8")
    manuscript.write_text(text.replace("Prose for scene_07_01.", "Mara kept the ledger close."), encoding="utf-8")
    before = scenes[0].read_text(encoding="utf-8")
    store = ReconciliationStore(project)
    report = store.inspect(manuscript, assembly.artifact_id)
    assert any(item["classification"] == "modified" for item in report["findings"])
    result = store.propose(report["inspection_id"])
    assert result["proposal_ids"]
    assert scenes[0].read_text(encoding="utf-8") == before


def test_reconciliation_classifies_markerless_cross_boundary_and_missing_sections(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assembly_store = ChapterExpressionStore(project)
    assembly = assembly_store.compose("07")
    manuscript = assembly_store.chapter_dir("07") / "markerless.md"
    manuscript.write_text("A rewritten chapter without ownership markers.", encoding="utf-8")
    report = ReconciliationStore(project).inspect(manuscript, assembly.artifact_id)
    assert report["status"] == "unresolved"
    assert any(item["classification"] == "markerless" for item in report["findings"])


def test_reconciliation_clean_and_transition_ownership_have_no_unsourced_noise(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assembly_store = ChapterExpressionStore(project)
    transition = {"t1": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "text": "At dusk."}}
    assembly = assembly_store.compose("07", transitions=transition)
    manuscript = assembly_store.chapter_dir("07") / "external.md"
    manuscript.write_text(assembly_store._metadata_path(assembly.artifact_id).with_suffix(".md").read_text(encoding="utf-8"), encoding="utf-8")
    report = ReconciliationStore(project).inspect(manuscript, assembly.artifact_id)
    assert report["status"] == "no_changes"
    assert report["findings"] == []
    assert report["recognized_transitions"][0]["owner"] == "Chapter transition"


def test_markerless_reconciliation_keeps_hierarchical_consequences(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assembly = ChapterExpressionStore(project).compose("07", transitions={"t1": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "text": "At dusk."}})
    manuscript = tmp_path / "markerless.md"
    manuscript.write_text("No ownership markers.", encoding="utf-8")
    report = ReconciliationStore(project).inspect(manuscript, assembly.artifact_id)
    assert [item["classification"] for item in report["findings"]].count("markerless") == 1
    assert report["primary_finding"]["classification"] == "markerless"
    assert not any(item["classification"] in {"missing", "unsourced"} for item in report["findings"])
    consequences = report["findings"][0]["detail"]["consequences"]
    assert any(item["code"] == "transition_mapping_unavailable" for item in consequences)


def test_reconciliation_normalizes_transition_missing_duplicate_and_revision_errors(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    transition = {"t1": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "revision": 1, "text": "At dusk."}}
    assembly_store = ChapterExpressionStore(project)
    assembly = assembly_store.compose("07", transitions=transition)
    path = assembly_store._metadata_path(assembly.artifact_id).with_suffix(".md")
    text = path.read_text(encoding="utf-8")
    start = "<!-- auteur:transition id=t1 revision=1 -->"
    end = "<!-- auteur:end-transition id=t1 -->"
    missing = text.replace(start + "\nAt dusk.\n" + end, "")
    missing_path = tmp_path / "missing.md"
    missing_path.write_text(missing, encoding="utf-8")
    missing_report = ReconciliationStore(project).inspect(missing_path, assembly.artifact_id)
    assert any(item["classification"] == "transition_missing" for item in missing_report["findings"])

    duplicate_path = tmp_path / "duplicate.md"
    duplicate_path.write_text(text.replace(end, end + "\n" + start + "\nAt dusk.\n" + end), encoding="utf-8")
    duplicate_report = ReconciliationStore(project).inspect(duplicate_path, assembly.artifact_id)
    assert any(item["classification"] == "transition_duplicated" for item in duplicate_report["findings"])

    malformed_path = tmp_path / "malformed.md"
    malformed_path.write_text(text.replace(start, "<!-- auteur:transition id=t1 revision=9 -->"), encoding="utf-8")
    malformed_report = ReconciliationStore(project).inspect(malformed_path, assembly.artifact_id)
    assert any(item["classification"] == "transition_malformed" for item in malformed_report["findings"])


def test_reconciliation_scene_change_persists_evidence_and_proposal_deduplicates(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assembly_store = ChapterExpressionStore(project)
    assembly = assembly_store.compose("07")
    path = assembly_store._metadata_path(assembly.artifact_id).with_suffix(".md")
    manuscript = tmp_path / "edited.md"
    manuscript.write_text(path.read_text(encoding="utf-8").replace("Prose for scene_07_01.", "Mara kept the ledger close."), encoding="utf-8")
    store = ReconciliationStore(project)
    report = store.inspect(manuscript, assembly.artifact_id)
    scene = next(item for item in report["findings"] if item["classification"] == "modified")
    assert scene["detail"]["change_metrics"]["classification_reason"]
    result = store.propose(report["inspection_id"])
    assert len(result["proposal_ids"]) == 1
    assert len(store.propose(report["inspection_id"])["proposal_ids"]) == 1


def test_reconciliation_records_structural_review_evidence_for_fact_like_rewrite(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assembly_store = ChapterExpressionStore(project)
    assembly = assembly_store.compose("07")
    path = assembly_store._metadata_path(assembly.artifact_id).with_suffix(".md")
    manuscript = tmp_path / "structural.md"
    manuscript.write_text(path.read_text(encoding="utf-8").replace("Prose for scene_07_01.", "Mara discovered the hidden archive and decided to leave."), encoding="utf-8")
    report = ReconciliationStore(project).inspect(manuscript, assembly.artifact_id)
    scene = next(item for item in report["findings"] if item["classification"] == "modified")
    metrics = scene["detail"]["change_metrics"]
    assert metrics["structured_fact_findings"]
    assert "structural review" in metrics["classification_reason"]


def test_reconciliation_cli_creates_and_shows_report(tmp_path: Path, capsys) -> None:
    from auteur.cli import main
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assembly = ChapterExpressionStore(project).compose("07")
    manuscript = tmp_path / "edited.md"
    manuscript.write_text("No markers; manual mapping required.", encoding="utf-8")
    assert main(["expression", "reconcile", "inspect", str(manuscript), "--against", assembly.artifact_id, "--project", str(project)]) == 0
    output = capsys.readouterr().out
    assert "reconciliation inspection" in output
    report = next(project.glob("chapters/07/expression/reconciliation/inspections/*.yaml"))
    import yaml as _yaml
    inspection = _yaml.safe_load(report.read_text(encoding="utf-8"))
    assert main(["expression", "reconcile", "show", inspection["inspection_id"], "--project", str(project)]) == 0
    assert "unresolved" in capsys.readouterr().out


def test_reconciliation_application_plan_is_ready_and_noncanonical(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, scenes, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    assembly = store.compose("07")
    manuscript = store.chapter_dir("07") / "edited.md"
    manuscript.write_text((store._metadata_path(assembly.artifact_id).with_suffix(".md")).read_text(encoding="utf-8").replace("Prose for scene_07_01.", "Edited prose."), encoding="utf-8")
    reconcile = ReconciliationStore(project)
    report = reconcile.inspect(manuscript, assembly.artifact_id)
    proposals = reconcile.propose(report["inspection_id"])
    plan = reconcile.plan(report["inspection_id"], proposals["proposal_ids"])
    assert plan["readiness"] == "ready"
    assert plan["planned_outputs"][0]["output_type"] == "scene_expression_candidate"
    assert plan["recomposition_preview"]["canonical"] is False
    assert not (project / "chapters/07/expression/scenes").exists()


def test_reconciliation_application_plan_rejects_duplicate_and_stale_selection(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    store = ChapterExpressionStore(project)
    assembly = store.compose("07")
    manuscript = store.chapter_dir("07") / "edited.md"
    manuscript.write_text((store._metadata_path(assembly.artifact_id).with_suffix(".md")).read_text(encoding="utf-8").replace("Prose for scene_07_01.", "Edited prose."), encoding="utf-8")
    reconcile = ReconciliationStore(project)
    report = reconcile.inspect(manuscript, assembly.artifact_id)
    proposal_id = reconcile.propose(report["inspection_id"])["proposal_ids"][0]
    scenes_path = project / "chapters/07/scenes/scene_07_01.yaml"
    ExpressionStore(project).generate(scenes_path, "New accepted prose.")
    ExpressionStore(project).accept("scene_07_01:prose_v002")
    plan = reconcile.plan(report["inspection_id"], [proposal_id, proposal_id])
    assert plan["readiness"] in {"conflicted", "stale"}
    assert any(item["conflict_code"] == "duplicate_proposal_selection" for item in plan["conflicts"])
    assert any(item["classification"] == "stale" for item in plan["freshness_results"])


def test_reconciliation_publication_creates_unaccepted_candidates_and_chapter(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assembly_store = ChapterExpressionStore(project)
    assembly = assembly_store.compose("07")
    manuscript = assembly_store.chapter_dir("07") / "edited.md"
    manuscript.write_text(assembly_store._metadata_path(assembly.artifact_id).with_suffix(".md").read_text(encoding="utf-8").replace("Prose for scene_07_01.", "Published wording."), encoding="utf-8")
    store = ReconciliationStore(project)
    report = store.inspect(manuscript, assembly.artifact_id)
    proposal = store.propose(report["inspection_id"])["proposal_ids"][0]
    plan = store.plan(report["inspection_id"], [proposal])
    publication = store.publish(plan["application_set_id"])
    assert publication["status"] == "published"
    candidate = project / "chapters/07/scenes/scene_07_01/prose_v002.yaml"
    metadata = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    assert metadata["lifecycle"] == "proposed"
    assert metadata["authority"] == "draft"
    chapter = yaml.safe_load((assembly_store._metadata_path(publication["chapter_expression"])).read_text(encoding="utf-8"))
    assert chapter["lifecycle"] == "proposed"
    assert chapter["transformation"]["id"] == "expression.publish_application"


def test_reconciliation_publication_rolls_back_candidates_on_composition_failure(tmp_path: Path, monkeypatch) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assembly_store = ChapterExpressionStore(project)
    assembly = assembly_store.compose("07")
    manuscript = assembly_store.chapter_dir("07") / "edited.md"
    manuscript.write_text(assembly_store._metadata_path(assembly.artifact_id).with_suffix(".md").read_text(encoding="utf-8").replace("Prose for scene_07_01.", "Published wording."), encoding="utf-8")
    store = ReconciliationStore(project)
    report = store.inspect(manuscript, assembly.artifact_id)
    proposal = store.propose(report["inspection_id"])["proposal_ids"][0]
    plan = store.plan(report["inspection_id"], [proposal])
    monkeypatch.setattr(store.composition, "compose", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("simulated filesystem failure")))
    with pytest.raises(RuntimeError, match="simulated filesystem failure"):
        store.publish(plan["application_set_id"])
    assert not list(project.glob("chapters/07/scenes/scene_07_01/prose_v002.yaml"))
    assert not list(project.glob("chapters/07/expression/transition_candidates/*"))


def test_mixed_publication_preserves_transition_identity_and_boundary(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import ReconciliationStore
    project, _, _ = make_project(tmp_path)
    assemblies = ChapterExpressionStore(project)
    assembly = assemblies.compose("07", transitions={"t1": {"transition_id": "t1", "before_scene": "scene_07_02", "after_scene": "scene_07_01", "revision": 1, "text": "At dawn."}})
    manuscript = assemblies.chapter_dir("07") / "edited.md"
    manuscript.write_text(assemblies._metadata_path(assembly.artifact_id).with_suffix(".md").read_text(encoding="utf-8").replace("Prose for scene_07_01.", "Published wording.").replace("At dawn.", "At dusk."), encoding="utf-8")
    store = ReconciliationStore(project)
    report = store.inspect(manuscript, assembly.artifact_id)
    proposal_ids = store.propose(report["inspection_id"])["proposal_ids"]
    plan = store.plan(report["inspection_id"], proposal_ids)
    publication = store.publish(plan["application_set_id"])
    transition = yaml.safe_load((project / "chapters/07/expression/transition_candidates/t1_v002.yaml").read_text(encoding="utf-8"))
    assert transition["transition_id"] == "t1"
    assert transition["boundary"] == {"before_scene": "scene_07_02", "after_scene": "scene_07_01"}
    chapter = yaml.safe_load(assemblies._metadata_path(publication["chapter_expression"]).read_text(encoding="utf-8"))
    published_transition = next(item for item in chapter["transitions"] if item["transition_id"] == "t1")
    assert published_transition["before_scene"] == "scene_07_02"
    assert published_transition["after_scene"] == "scene_07_01"
    assert chapter["lifecycle"] == "proposed"


def test_publication_revalidates_stale_scene_plan_before_staging(tmp_path: Path) -> None:
    from auteur.expression.reconciliation import PublicationRejected, ReconciliationStore
    project, scenes, _ = make_project(tmp_path)
    assemblies = ChapterExpressionStore(project)
    assembly = assemblies.compose("07")
    manuscript = assemblies.chapter_dir("07") / "edited.md"
    manuscript.write_text(assemblies._metadata_path(assembly.artifact_id).with_suffix(".md").read_text(encoding="utf-8").replace("Prose for scene_07_01.", "Edited."), encoding="utf-8")
    store = ReconciliationStore(project)
    report = store.inspect(manuscript, assembly.artifact_id)
    proposal_id = store.propose(report["inspection_id"])["proposal_ids"][0]
    plan = store.plan(report["inspection_id"], [proposal_id])
    ExpressionStore(project).generate(scenes[0], "New accepted source.")
    ExpressionStore(project).accept("scene_07_01:prose_v002")
    with pytest.raises(PublicationRejected) as error:
        store.publish(plan["application_set_id"])
    assert error.value.result["status"] == "rejected_stale"
    assert any(item["code"] == "TARGET_REVISION_CHANGED" for item in error.value.result["stale_reasons"])
    assert plan["planned_readiness"]["status"] == "ready"
    assert not (project / "chapters/07/scenes/scene_07_01/prose_v003.yaml").exists()
    assert not list((project / "chapters/07/expression/reconciliation/publications").glob("*"))
