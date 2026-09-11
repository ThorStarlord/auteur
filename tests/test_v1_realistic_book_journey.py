from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from auteur.expression import ExpressionStore
from auteur.expression.book import BookExpressionStore
from auteur.expression.composition import ChapterExpressionStore
from auteur.provenance import ArtifactStore
from auteur.publish import PublishError, PublishingSnapshot, publish


CHAPTER_COUNT = 20
SCENES_PER_CHAPTER = 3


def _build_novel(project: Path) -> tuple[list[str], list[str], Path]:
    artifact_store = ArtifactStore(project)
    expression_store = ExpressionStore(project)
    chapter_store = ChapterExpressionStore(project)
    chapter_ids: list[str] = []
    chapter_expression_ids: list[str] = []
    first_scene: Path | None = None

    for chapter_number in range(1, CHAPTER_COUNT + 1):
        chapter_id = f"chapter_{chapter_number:02d}"
        scene_ids = [
            f"scene_{chapter_number:02d}_{scene_number:02d}"
            for scene_number in range(1, SCENES_PER_CHAPTER + 1)
        ]
        outline = project / "chapters" / f"{chapter_number:02d}" / "outline.yaml"
        outline.parent.mkdir(parents=True, exist_ok=True)
        outline.write_text(
            yaml.safe_dump(
                {
                    "id": chapter_id,
                    "chapter_id": chapter_id,
                    "scenes": scene_ids,
                    "function": f"advance long-form pressure {chapter_number}",
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        artifact_store.accept(outline, "chapter_outline")

        for scene_number, scene_id in enumerate(scene_ids, 1):
            scene = outline.parent / "scenes" / f"{scene_id}.yaml"
            scene.parent.mkdir(parents=True, exist_ok=True)
            scene.write_text(
                yaml.safe_dump(
                    {
                        "id": scene_id,
                        "chapter_id": chapter_id,
                        "participants": ["protagonist", f"support_{chapter_number % 4}"],
                        "pov_character_id": "protagonist",
                        "location": f"location_{chapter_number % 5}",
                        "goal": f"advance objective {chapter_number}.{scene_number}",
                        "opposition": f"pressure_{chapter_number}_{scene_number}",
                        "turn": f"turn_{chapter_number}_{scene_number}",
                        "decision": f"decision_{chapter_number}_{scene_number}",
                        "outcome": f"outcome_{chapter_number}_{scene_number}",
                        "knowledge": [f"fact_{chapter_number}_{scene_number}"],
                        "emotional_changes": ["pressure to resolve"],
                        "arc_realizations": [f"arc_checkpoint_{chapter_number}"],
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            artifact_store.accept(scene, "scene_realization")
            candidate = expression_store.generate(
                scene,
                (
                    f"Chapter {chapter_number}, scene {scene_number}. "
                    f"The protagonist completes {scene_id} without changing its accepted facts."
                ),
            )
            expression_store.accept(candidate.candidate_id)
            if first_scene is None:
                first_scene = scene

        chapter_expression = chapter_store.compose(chapter_id)
        accepted_chapter = chapter_store.accept(chapter_expression.artifact_id)
        chapter_ids.append(chapter_id)
        chapter_expression_ids.append(accepted_chapter.artifact_id)

    assert first_scene is not None
    return chapter_ids, chapter_expression_ids, first_scene


def test_realistic_v1_book_journey_restarts_publishes_and_blocks_stale_publication(
    tmp_path: Path,
) -> None:
    project = tmp_path / "novel"
    project.mkdir()
    chapter_ids, chapter_expression_ids, first_scene = _build_novel(project)

    assert len(chapter_ids) == CHAPTER_COUNT
    assert CHAPTER_COUNT * SCENES_PER_CHAPTER == 60

    book_store = BookExpressionStore(project)
    book = book_store.compose(chapter_ids, title="V1 Qualification Novel")
    accepted = book_store.accept(book["book_expression_id"])
    assert book_store.inspect(accepted["book_expression_id"])["freshness"] == "fresh"

    # Full process/store reconstruction must preserve the accepted chain.
    restarted_book_store = BookExpressionStore(project)
    restarted_chapter_store = ChapterExpressionStore(project)
    assert restarted_book_store.inspect(accepted["book_expression_id"])["freshness"] == "fresh"
    assert all(
        restarted_chapter_store.status(expression_id)["freshness"] == "fresh"
        for expression_id in chapter_expression_ids
    )

    outputs = tmp_path / "publication"
    result = publish(project, formats=["html", "epub"], output_dir=outputs)
    assert result["source_revision"] == accepted["revision"]
    assert (outputs / "book.html").is_file()
    assert (outputs / "book.epub").is_file()

    # Change one accepted Scene Realization without silently rewriting Expression.
    raw = yaml.safe_load(first_scene.read_text(encoding="utf-8"))
    raw["outcome"] = "revised accepted outcome after structural reconsideration"
    first_scene.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    ArtifactStore(project).accept(first_scene, "scene_realization")

    chapter_status = ChapterExpressionStore(project).status(chapter_expression_ids[0])
    assert chapter_status["freshness"] == "stale"

    book_status = BookExpressionStore(project).inspect(accepted["book_expression_id"])
    assert book_status["freshness"] == "stale"
    assert any(
        item.get("chapter_freshness") == "stale"
        for item in book_status["stale_sources"]
    )

    # A byte-identical accepted Book is no longer sufficient for publication:
    # transitive accepted-source freshness is a release boundary too.
    with pytest.raises(PublishError, match="Accepted Book is stale"):
        PublishingSnapshot(project)
