from pathlib import Path

import yaml

from auteur.provenance import (
    ArtifactStore,
    DependencyKind,
    DependencySource,
    DependencySpec,
    Lifecycle,
    ReviewState,
)
from auteur.cli import main


def write_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def make_pilot(tmp_path: Path) -> tuple[ArtifactStore, Path, Path, Path, Path]:
    project = tmp_path / "project"
    project.mkdir()
    identity = project / "story_identity.yaml"
    blueprint = project / "blueprint.yaml"
    chapter = project / "chapter_07.yaml"
    scene = project / "scene_07_03.yaml"
    write_yaml(identity, {"title": "First", "core_answer": "Trust", "genre": "mystery", "emotional_core": "belonging"})
    write_yaml(blueprint, {"story_identity": "story_identity", "want": "Trust"})
    write_yaml(chapter, {"blueprint": "blueprint", "function": "reveal"})
    write_yaml(scene, {"chapter": "chapter_07", "outcome": "secret revealed"})
    return ArtifactStore(project), identity, blueprint, chapter, scene


def test_initial_acceptance_records_sidecar_and_hash(tmp_path: Path) -> None:
    store, identity, _, _, _ = make_pilot(tmp_path)

    metadata = store.accept(identity, "story_identity")

    assert metadata.revision == 1
    assert metadata.lifecycle is Lifecycle.ACCEPTED
    assert metadata.review_state is ReviewState.NONE
    assert metadata.content_hash.startswith("sha256:")
    assert store.sidecar_path("story_identity").is_file()


def test_yaml_formatting_does_not_change_hash_but_semantics_do(tmp_path: Path) -> None:
    store, identity, _, _, _ = make_pilot(tmp_path)
    first = store.accept(identity, "story_identity")
    identity.write_text("genre: mystery\ncore_answer: Trust\nemotional_core: belonging\ntitle: First\n", encoding="utf-8")
    assert store.content_hash(identity) == first.content_hash
    identity.write_text("genre: mystery\ncore_answer: Betrayal\nemotional_core: belonging\ntitle: First\n", encoding="utf-8")
    assert store.content_hash(identity) != first.content_hash


def test_title_only_identity_change_does_not_stale_blueprint(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    store.accept(
        blueprint,
        "blueprint",
        dependencies=[
            DependencySpec(
                artifact_id="story_identity",
                artifact_type="story_identity",
                path=identity,
                kind=DependencyKind.SEMANTIC,
                source=DependencySource.INFERRED,
                fields=["core_answer", "genre"],
            )
        ],
    )
    identity.write_text("title: Renamed\ncore_answer: Trust\ngenre: mystery\n", encoding="utf-8")

    assert store.status(blueprint, "blueprint").freshness == "fresh"


def test_semantic_identity_change_stales_blueprint(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    store.accept(
        blueprint,
        "blueprint",
        dependencies=[DependencySpec("story_identity", "story_identity", identity, DependencyKind.SEMANTIC, DependencySource.INFERRED, ["core_answer", "genre"])],
    )
    write_yaml(identity, {"title": "First", "core_answer": "Betrayal", "genre": "mystery"})

    status = store.status(blueprint, "blueprint")
    assert status.freshness == "stale"
    assert status.review_state is ReviewState.REVIEW_REQUIRED


def test_acceptance_after_change_creates_new_revision(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    store.accept(
        blueprint,
        "blueprint",
        dependencies=[DependencySpec("story_identity", "story_identity", identity, DependencyKind.SEMANTIC, DependencySource.INFERRED, ["core_answer"])],
    )
    write_yaml(identity, {"title": "First", "core_answer": "Betrayal", "genre": "mystery"})
    store.accept(blueprint, "blueprint")

    assert store.status(blueprint, "blueprint").revision == 2
    assert store.status(blueprint, "blueprint").freshness == "fresh"


def test_acknowledged_divergence_remains_stale(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    store.accept(
        blueprint,
        "blueprint",
        dependencies=[DependencySpec("story_identity", "story_identity", identity, DependencyKind.SEMANTIC, DependencySource.INFERRED, ["core_answer"])],
    )
    write_yaml(identity, {"title": "First", "core_answer": "Betrayal", "genre": "mystery"})
    store.accept(blueprint, "blueprint", rationale="Intentional alternate direction", acknowledge_divergence=True)

    status = store.status(blueprint, "blueprint")
    assert status.freshness == "stale"
    assert status.review_state is ReviewState.ACKNOWLEDGED_DIVERGENCE


def test_legacy_artifact_is_usable_and_adoption_creates_baseline(tmp_path: Path) -> None:
    store, identity, _, _, _ = make_pilot(tmp_path)

    status = store.status(identity, "story_identity")
    assert status.provenance_state == "unknown"
    adopted = store.adopt(identity, "story_identity")
    assert adopted.revision == 1
    assert adopted.provenance_state == "tracked"


def test_chapter_deletion_invalidates_scene_dependency(tmp_path: Path) -> None:
    store, _, _, chapter, scene = make_pilot(tmp_path)
    store.accept(chapter, "chapter_outline")
    store.accept(
        scene,
        "scene_realization",
        dependencies=[DependencySpec("chapter_07", "chapter_outline", chapter, DependencyKind.STRUCTURAL, DependencySource.INFERRED)],
    )
    chapter.unlink()

    assert store.status(scene, "scene_realization").health == "invalid"


def test_archive_preserves_id_and_rejects_active_reference(tmp_path: Path) -> None:
    store, _, _, chapter, scene = make_pilot(tmp_path)
    store.accept(chapter, "chapter_outline")
    store.accept(
        scene,
        "scene_realization",
        dependencies=[DependencySpec("chapter_07", "chapter_outline", chapter, DependencyKind.STRUCTURAL, DependencySource.INFERRED)],
    )
    store.archive(chapter, "chapter_outline", reason="removed", by="author")

    assert store.status(chapter, "chapter_outline").lifecycle is Lifecycle.ARCHIVED
    assert store.status(scene, "scene_realization").health == "invalid"
    assert store.accept(chapter, "chapter_outline") is None


def test_transitive_impact_uses_direct_edges(tmp_path: Path) -> None:
    store, identity, blueprint, chapter, scene = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    store.accept(blueprint, "blueprint", dependencies=[DependencySpec("story_identity", "story_identity", identity, DependencyKind.SEMANTIC, DependencySource.INFERRED, ["core_answer"])])
    store.accept(chapter, "chapter_outline", dependencies=[DependencySpec("blueprint", "blueprint", blueprint, DependencyKind.STRUCTURAL, DependencySource.INFERRED)])
    store.accept(scene, "scene_realization", dependencies=[DependencySpec("chapter_07", "chapter_outline", chapter, DependencyKind.STRUCTURAL, DependencySource.INFERRED)])

    assert store.affected_by("story_identity") == {"blueprint", "chapter_07", "scene_07_03"}


def test_model_suggested_dependency_is_not_canonical(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    metadata = store.accept(
        blueprint,
        "blueprint",
        dependencies=[DependencySpec("story_identity", "story_identity", identity, DependencyKind.SEMANTIC, DependencySource.SUGGESTED)],
    )

    assert metadata.dependencies[0].source is DependencySource.SUGGESTED
    assert store.affected_by("story_identity") == set()


def test_pilot_dependencies_are_inferred_on_acceptance(tmp_path: Path) -> None:
    store, identity, blueprint, chapter, scene = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    blueprint_metadata = store.accept(blueprint, "blueprint")
    chapter_metadata = store.accept(chapter, "chapter_outline")
    scene_metadata = store.accept(scene, "scene_realization")

    assert [item.artifact_id for item in blueprint_metadata.dependencies] == ["story_identity"]
    assert {item.artifact_id for item in chapter_metadata.dependencies} == {"story_identity", "blueprint"}
    assert {item.artifact_id for item in scene_metadata.dependencies} == {"blueprint", "chapter_07"}


def test_acceptance_never_overwrites_source_content(tmp_path: Path) -> None:
    store, identity, _, _, _ = make_pilot(tmp_path)
    original = identity.read_text(encoding="utf-8")
    store.accept(identity, "story_identity")
    assert identity.read_text(encoding="utf-8") == original


def test_json_hash_is_key_order_independent(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path)
    first = tmp_path / "artifact.json"
    first.write_text('{"b": 2, "a": 1}', encoding="utf-8")
    first_hash = store.content_hash(first)
    first.write_text('{"a":1,"b":2}', encoding="utf-8")
    assert store.content_hash(first) == first_hash


def test_duplicate_artifact_ids_are_invalid(tmp_path: Path) -> None:
    store, identity, _, _, _ = make_pilot(tmp_path)
    write_yaml(identity.parent / "duplicate.yaml", {"id": "story_identity"})
    assert store.status(identity, "story_identity").health == "invalid"


def test_projection_metadata_and_emotional_core_projection(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    store.accept(blueprint, "blueprint")
    record = store._load("blueprint").dependencies[0]
    assert record.projection.id == "story_identity.structural"
    assert record.projection.version == 1
    assert "emotional_core" in record.projection.fields
    assert record.projected_hash
    assert record.full_content_hash


def test_emotional_core_change_stales_blueprint_but_title_does_not(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    store.accept(blueprint, "blueprint")
    write_yaml(identity, {"title": "Changed", "core_answer": "Trust", "genre": "mystery", "emotional_core": "belonging"})
    assert store.status(blueprint, "blueprint").freshness == "fresh"
    write_yaml(identity, {"title": "Changed", "core_answer": "Trust", "genre": "mystery", "emotional_core": "isolation"})
    assert store.status(blueprint, "blueprint").freshness == "stale"


def test_same_projection_new_upstream_revision_is_fresh(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity")
    store.accept(blueprint, "blueprint")
    store.accept(identity, "story_identity")
    assert store.status(blueprint, "blueprint").freshness == "fresh"


def test_chapter_projection_limits_blueprint_impact(tmp_path: Path) -> None:
    store, identity, blueprint, chapter, _ = make_pilot(tmp_path)
    unrelated = tmp_path / "project" / "chapter_08.yaml"
    write_yaml(unrelated, {"blueprint": "blueprint", "chapter_id": "chapter_08", "function": "unrelated"})
    write_yaml(blueprint, {"story_identity": "story_identity", "chapters": {"chapter_07": {"function": "original"}, "chapter_08": {"function": "unrelated"}}})
    store.accept(identity, "story_identity"); store.accept(blueprint, "blueprint")
    store.accept(chapter, "chapter_outline"); store.accept(unrelated, "chapter_outline")
    write_yaml(blueprint, {"story_identity": "story_identity", "chapters": {"chapter_07": {"function": "changed"}, "chapter_08": {"function": "unrelated"}}})
    assert store.status(chapter, "chapter_outline").freshness == "stale"
    assert store.status(unrelated, "chapter_outline").freshness == "fresh"


def test_acknowledged_divergence_reopens_after_new_dependency_change(tmp_path: Path) -> None:
    store, identity, blueprint, _, _ = make_pilot(tmp_path)
    store.accept(identity, "story_identity"); store.accept(blueprint, "blueprint")
    write_yaml(identity, {"title": "First", "core_answer": "Changed", "genre": "mystery"})
    store.status(blueprint, "blueprint")
    store.accept(blueprint, "blueprint", acknowledge_divergence=True, rationale="intentional")
    assert store.status(blueprint, "blueprint").review_state is ReviewState.ACKNOWLEDGED_DIVERGENCE
    write_yaml(identity, {"title": "First", "core_answer": "Changed again", "genre": "mystery"})
    assert store.status(blueprint, "blueprint").review_state is ReviewState.REVIEW_REQUIRED


def test_revision_snapshots_are_readable(tmp_path: Path) -> None:
    store, identity, _, _, _ = make_pilot(tmp_path)
    first = store.accept(identity, "story_identity")
    second = store.accept(identity, "story_identity")
    assert second.revision == 2
    assert store.list_revisions("story_identity") == [1, 2]
    assert store.get_revision("story_identity", first.revision).revision == 1
    assert store.current("story_identity").revision == 2


def test_affected_by_cli_has_human_and_json_modes(tmp_path: Path, capsys) -> None:
    _, identity, blueprint, _, _ = make_pilot(tmp_path)
    main(["state", "accept", str(identity), "--type", "story_identity"])
    main(["state", "accept", str(blueprint), "--type", "blueprint"])
    assert main(["state", "affected-by", str(identity)]) == 0
    assert "blueprint" in capsys.readouterr().out
    assert main(["state", "affected-by", str(identity), "--json"]) == 0
    assert "\"artifact_id\": \"blueprint\"" in capsys.readouterr().out


def test_impossible_knowledge_is_invalid_after_predecessor_revision(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / "project")
    store.project.mkdir()
    previous = store.project / "scene_01_01.yaml"
    current = store.project / "scene_01_02.yaml"
    write_yaml(previous, {"id": "scene_01_01", "chapter_id": "chapter_01", "exit_knowledge": [{"what": "the vault is open"}]})
    write_yaml(current, {"id": "scene_01_02", "chapter_id": "chapter_01", "entry_knowledge": [{"what": "the vault is open", "source": "chapter_position"}], "temporal_relation": {"follows_scene": "scene_01_01"}})
    store.accept(previous, "scene_realization")
    store.accept(current, "scene_realization")
    write_yaml(previous, {"id": "scene_01_01", "chapter_id": "chapter_01", "exit_knowledge": []})
    status = store.status(current, "scene_realization")
    assert status.freshness == "stale"
    assert any("impossible_knowledge" in reason for reason in status.invalid_reasons)


def test_state_adopt_and_status_cli(tmp_path: Path, capsys) -> None:
    _, identity, _, _, _ = make_pilot(tmp_path)
    assert main(["state", "adopt", str(identity), "--type", "story_identity"]) == 0
    assert main(["state", "status", str(identity)]) == 0
    assert "tracked" in capsys.readouterr().out
