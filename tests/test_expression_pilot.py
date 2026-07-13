from pathlib import Path

import yaml

from auteur.cli import main
from auteur.expression import ExpressionStore, build_scene_prompt
from auteur.provenance import ArtifactStore, Lifecycle


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def make_project(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "project"
    scene = project / "chapters" / "07" / "scenes" / "scene_07_01.yaml"
    write_yaml(scene, {
        "id": "scene_07_01",
        "chapter_id": "chapter_07",
        "participants": ["mara", "jon"],
        "pov_character_id": "mara",
        "location": "archive",
        "goal": "find the ledger",
        "opposition": "the archive is locked",
        "turn": "the ledger reveals the signature",
        "decision": "hide the ledger",
        "outcome": "mara hides the ledger",
        "knowledge": ["the ledger exists"],
        "emotional_changes": ["suspicion to resolve"],
        "arc_realizations": ["mara chooses trust"],
    })
    ArtifactStore(project).accept(scene, "scene_realization")
    return project, scene


def test_scene_prompt_separates_facts_constraints_and_freedom(tmp_path: Path) -> None:
    _, scene = make_project(tmp_path)
    prompt = build_scene_prompt(scene, {"pov": "close third", "tense": "past"})
    assert "CANONICAL FACTS" in prompt
    assert "EXPRESSION CONSTRAINTS" in prompt
    assert "EXPRESSION FREEDOM" in prompt
    assert "mara hides the ledger" in prompt
    assert "Do not change the Scene Realization" in prompt


def test_generate_persists_versioned_candidate_and_transformation_metadata(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    candidate = store.generate(scene, "Mara lifted the ledger and hid it.", executor={"kind": "human-authored"})
    assert candidate.artifact_type == "expression_scene_prose"
    assert candidate.lifecycle.value == "draft"
    assert candidate.transformation.id == "realization.generate_expression"
    assert candidate.transformation.version == 1
    assert candidate.source_scene.revision == 1
    assert candidate.source_scene.content_hash.startswith("sha256:")
    assert (store.candidate_dir(scene) / "prose_v001.md").is_file()
    assert (store.candidate_dir(scene) / "prose_v001.yaml").is_file()


def test_multiple_candidates_coexist_without_overwrite(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    first = store.generate(scene, "First version.")
    second = store.generate(scene, "Second version.")
    assert first.candidate_id != second.candidate_id
    assert (store.candidate_dir(scene) / "prose_v001.md").read_text() == "First version."
    assert (store.candidate_dir(scene) / "prose_v002.md").read_text() == "Second version."


def test_generation_does_not_mutate_source_or_bible(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    before = scene.read_text(encoding="utf-8")
    ExpressionStore(project).generate(scene, "Draft prose.")
    assert scene.read_text(encoding="utf-8") == before
    assert not (project / "bible.json").exists()


def test_generation_failure_leaves_no_candidate(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    try:
        store.generate(scene, lambda: (_ for _ in ()).throw(RuntimeError("generation failed")))
    except RuntimeError:
        pass
    assert not store.candidate_dir(scene).exists()


def test_acceptance_is_explicit_and_preserves_previous_candidates(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    first = store.generate(scene, "First.")
    second = store.generate(scene, "Second.")
    accepted = store.accept(second.candidate_id, accepted_by="author")
    assert accepted.lifecycle is Lifecycle.ACCEPTED
    assert store.inspect(first.candidate_id).lifecycle is Lifecycle.DRAFT
    assert store.inspect(second.candidate_id).accepted_by == "author"
    assert store.accepted_path(scene, second.candidate_id).is_file()


def test_scene_revision_makes_candidate_stale_but_preserves_prose(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    candidate = store.generate(scene, "Original prose.")
    write_yaml(scene, {"id": "scene_07_01", "chapter_id": "chapter_07", "outcome": "new outcome"})
    status = store.status(candidate.candidate_id)
    assert status["freshness"] == "stale"
    assert store.prose_path(candidate.candidate_id).read_text() == "Original prose."


def test_structural_problem_creates_proposal_without_mutation(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    before = scene.read_text(encoding="utf-8")
    proposal = store.create_upstream_proposal(
        scene,
        problem="The decision lacks sufficient pressure in prose.",
        suggested_change="Strengthen opposition before the decision.",
        evidence="The draft reaches the decision without a blocking action.",
    )
    assert proposal["target_artifact"] == "scene_07_01"
    assert proposal["target_layer"] == "Realization"
    assert scene.read_text(encoding="utf-8") == before


def test_expression_cli_generate_inspect_accept(tmp_path: Path, capsys) -> None:
    project, scene = make_project(tmp_path)
    assert main(["expression", "generate", str(scene), "--text", "CLI prose."]) == 0
    output = capsys.readouterr().out
    candidate_id = output.strip().splitlines()[-1]
    assert main(["expression", "inspect", candidate_id, "--project", str(project)]) == 0
    assert "expression_scene_prose" in capsys.readouterr().out
    assert main(["expression", "accept", candidate_id, "--project", str(project)]) == 0
    assert "accepted" in capsys.readouterr().out


def test_stale_candidate_requires_review_and_revalidation_creates_metadata_revision(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    candidate = store.generate(scene, "Original.")
    write_yaml(scene, {"id": "scene_07_01", "chapter_id": "chapter_07", "outcome": "revised outcome"})
    try:
        store.accept(candidate.candidate_id)
    except ValueError as exc:
        assert "stale" in str(exc)
    else:
        raise AssertionError("stale candidate was accepted")
    revised = store.revalidate(candidate.candidate_id, reviewed_by="sam")
    assert revised.metadata_revision == 2
    assert revised.review_state.value == "none"
    assert store.status(candidate.candidate_id)["freshness"] == "fresh"


def test_divergence_requires_acknowledgement_and_reopens_after_later_change(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    candidate = store.generate(scene, "Original.")
    write_yaml(scene, {"id": "scene_07_01", "chapter_id": "chapter_07", "outcome": "new outcome"})
    acknowledged = store.acknowledge(candidate.candidate_id, acknowledged_by="sam", reason="Author intentionally retains the original ending.")
    assert acknowledged.review_state.value == "acknowledged_divergence"
    accepted = store.accept(candidate.candidate_id, accepted_by="sam", allow_divergence=True)
    assert accepted.lifecycle is Lifecycle.ACCEPTED
    write_yaml(scene, {"id": "scene_07_01", "chapter_id": "chapter_07", "outcome": "third outcome"})
    assert store.status(candidate.candidate_id)["review_state"] == "review_required"


def test_structured_validation_evidence_and_semantic_findings_have_actions(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    findings = store.validate_prose(scene, "Mara writes a scene.", realization_evidence={"outcome": {"status": "contradicted"}})
    assert findings[0]["severity"] == "error"
    assert findings[0]["recommended_action"]
    findings = store.validate_prose(scene, "Jon privately knew the ledger exists.")
    assert any(item["code"] == "private_knowledge_exposure" for item in findings)


def test_compare_and_reject_preserve_candidates(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    first = store.generate(scene, "First.")
    second = store.generate(scene, "Second.")
    comparison = store.compare(first.candidate_id, second.candidate_id)
    assert "diff" in comparison
    rejected = store.reject(first.candidate_id, rejected_by="sam", reason="Less precise.")
    assert rejected.lifecycle is Lifecycle.REJECTED
    assert store.prose_path(first.candidate_id).read_text() == "First."


def test_proposal_records_target_hash_and_becomes_stale(tmp_path: Path) -> None:
    project, scene = make_project(tmp_path)
    store = ExpressionStore(project)
    proposal = store.create_upstream_proposal(scene, problem="Insufficient pressure.", suggested_change="Strengthen opposition.", evidence="The decision is unblocked.")
    assert proposal["target_projected_hash"].startswith("sha256:")
    assert store.proposal_status(proposal["proposal_id"])["stale"] is False
    write_yaml(scene, {"id": "scene_07_01", "chapter_id": "chapter_07", "outcome": "changed"})
    assert store.proposal_status(proposal["proposal_id"])["status"] == "stale"
