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
    write_yaml(identity, {"title": "First", "core_answer": "Trust", "genre": "mystery"})
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
    identity.write_text("genre: mystery\ncore_answer: Trust\ntitle: First\n", encoding="utf-8")
    assert store.content_hash(identity) == first.content_hash
    identity.write_text("genre: mystery\ncore_answer: Betrayal\ntitle: First\n", encoding="utf-8")
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


def test_state_adopt_and_status_cli(tmp_path: Path, capsys) -> None:
    _, identity, _, _, _ = make_pilot(tmp_path)
    assert main(["state", "adopt", str(identity), "--type", "story_identity"]) == 0
    assert main(["state", "status", str(identity)]) == 0
    assert "tracked" in capsys.readouterr().out
