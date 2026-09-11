from __future__ import annotations

from pathlib import Path

import yaml

from auteur.expression import ExpressionStore
from auteur.provenance import ArtifactStore, Lifecycle


def _write_scene(project: Path, chapter: int, scene_number: int) -> Path:
    scene_id = f"scene_{chapter:02d}_{scene_number:02d}"
    path = project / "chapters" / f"{chapter:02d}" / "scenes" / f"{scene_id}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "id": scene_id,
                "chapter_id": f"chapter_{chapter:02d}",
                "participants": ["protagonist", f"support_{chapter % 4}"],
                "pov_character_id": "protagonist",
                "location": f"location_{chapter % 5}",
                "goal": f"advance chapter {chapter} objective",
                "opposition": f"pressure_{scene_number}",
                "turn": f"turn_{chapter}_{scene_number}",
                "decision": f"decision_{chapter}_{scene_number}",
                "outcome": f"outcome_{chapter}_{scene_number}",
                "knowledge": [f"fact_{chapter}_{scene_number}"],
                "emotional_changes": ["pressure to resolve"],
                "arc_realizations": [f"arc_checkpoint_{chapter}"],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def test_v1_book_scale_topology_survives_restart_and_propagates_scene_staleness(tmp_path: Path):
    project = tmp_path / "novel"
    store = ArtifactStore(project)
    scenes: list[Path] = []
    for chapter in range(1, 21):
        for scene_number in range(1, 4):
            scene = _write_scene(project, chapter, scene_number)
            store.accept(scene, "scene_realization")
            scenes.append(scene)

    assert len(scenes) == 60
    expected = {
        str(scene.relative_to(project)): (
            store.status(scene, "scene_realization").revision,
            store.content_hash(scene),
        )
        for scene in scenes
    }

    restarted = ArtifactStore(project)
    for scene in scenes:
        status = restarted.status(scene, "scene_realization")
        revision, digest = expected[str(scene.relative_to(project))]
        assert status.lifecycle is Lifecycle.ACCEPTED
        assert status.revision == revision
        assert restarted.content_hash(scene) == digest

    expression = ExpressionStore(project)
    candidate = expression.generate(scenes[0], "The protagonist completes the accepted scene action.")
    expression.accept(candidate.candidate_id)
    assert expression.status(candidate.candidate_id)["freshness"] == "fresh"

    raw = yaml.safe_load(scenes[0].read_text(encoding="utf-8"))
    raw["outcome"] = "revised accepted outcome"
    scenes[0].write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    restarted.accept(scenes[0], "scene_realization")

    after_restart = ExpressionStore(project)
    status = after_restart.status(candidate.candidate_id)
    assert status["freshness"] == "stale"
    assert status["review_required"] is True
