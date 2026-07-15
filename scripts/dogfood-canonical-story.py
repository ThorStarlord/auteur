"""Run the read-only canonical-story dogfood in a temporary workspace."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from auteur.reasoning import (
    ArtifactRevision,
    ArtifactRevisionAdapter,
    CriticRegistry,
    ReasoningRuntime,
    RuntimeRequest,
    register_setup_payoff_critic,
    synthesize_reports,
)
from auteur.canonical_story import CanonicalStoryBootstrap
from auteur.reasoning.cli import format_review


ROOT = Path(__file__).parents[1] / "examples" / "canonical_story"


def run() -> dict:
    required = [
        "story_identity.yaml", "blueprint.md", "external_edit.md",
        "expected_review.md", "expected_publication.md",
        "chapter_01/scene_01/realization.yaml",
        "chapter_01/scene_01/expression.md",
        "chapter_01/scene_02/realization.yaml",
        "chapter_01/scene_02/expression.md",
        "chapter_01/scene_03/realization.yaml",
        "chapter_01/scene_03/expression.md",
        "chapter_01/scene_04/realization.yaml",
        "chapter_01/scene_04/expression.md",
        "chapter_01/scene_05/realization.yaml",
        "chapter_01/scene_05/expression.md",
    ]
    with tempfile.TemporaryDirectory(prefix="auteur-canonical-story-") as tmp:
        bootstrap = CanonicalStoryBootstrap(ROOT)
        workspace_root = Path(tmp)
        workspace = bootstrap.copy_to(workspace_root)
        accepted_realizations = bootstrap.accept_scene_realizations(workspace_root)
        report_dir = workspace / "reasoning"
        registry = CriticRegistry()
        register_setup_payoff_critic(registry)
        runtime = ReasoningRuntime(registry, report_dir)
        source = ArtifactRevision(
            artifact_id="canonical-story-chapter-01",
            artifact_type="chapter_structure",
            revision=1,
            content_hash=ArtifactRevisionAdapter.hash_content(
                (workspace / "chapter_01" / "scenes.md").read_text(encoding="utf-8")
            ),
        )
        result = runtime.run(RuntimeRequest(
            request_id="canonical-story-dogfood",
            critic_ids=("structure.setup_payoff",),
            inputs={"series": {"book_plans": [{"book_number": 1}], "narrative_setups": []},
                    "scope": "standalone"},
            source_revisions={"chapter": source},
        ))
        report_paths = [report_dir / f"{outcome.report_id}.json"
                        for outcome in result.outcomes if outcome.report_id]
        reports = [json.loads(path.read_text(encoding="utf-8")) for path in report_paths]
        review = synthesize_reports(reports, report_dir=workspace / "reconciliation")
        return {
            "project": "The Lantern at Low Water",
            "copied_to_temporary_workspace": True,
            "required_artifacts_present": all((workspace / path).is_file() for path in required),
            "accepted_scene_realizations": len(accepted_realizations),
            "critic_statuses": [outcome.status.value for outcome in result.outcomes],
            "review_id": review["review_id"],
            "review_text": format_review(review),
            "derived_artifacts_written_to": "temporary workspace only",
            "untraversed_stages": ["native Blueprint acceptance", "Chapter Expression acceptance", "external reconciliation", "publication", "candidate decision", "Chapter acceptance"],
            "friction": "Canonical reference files are human-readable demonstration artifacts; native Blueprint/Chapter/Expression and reconciliation stores require additional adapters.",
        }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
