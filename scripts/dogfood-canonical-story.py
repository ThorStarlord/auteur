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
from auteur.expression.reconciliation import ReconciliationStore
from auteur.expression.composition import ChapterExpressionStore
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
        "chapter_02/README.md", "chapter_02/scene_01/realization.yaml",
        "chapter_02/scene_01/expression.md",
    ]
    with tempfile.TemporaryDirectory(prefix="auteur-canonical-story-") as tmp:
        bootstrap = CanonicalStoryBootstrap(ROOT)
        workspace_root = Path(tmp)
        workspace = bootstrap.copy_to(workspace_root)
        native = bootstrap.accept_native_identity_and_structure(workspace_root)
        accepted_realizations = bootstrap.accept_scene_realizations(workspace_root)
        expressions = bootstrap.bootstrap_expressions(workspace_root)
        second = bootstrap.bootstrap_second_chapter(workspace_root)
        book = bootstrap.bootstrap_book(workspace_root, [
            expressions["chapter_expression"]["artifact_id"],
            second["chapter_expression"]["artifact_id"],
        ])
        from auteur.expression.book import BookExpressionStore
        book_store = BookExpressionStore(workspace_root)
        initial_book = book["accepted"]["book_expression_id"]
        chapter_store = ChapterExpressionStore(workspace_root)
        revised_chapter = chapter_store.compose("chapter_01")
        revised_chapter = chapter_store.accept(revised_chapter.artifact_id, accepted_by="canonical-dogfood")
        stale_book = book_store.inspect(initial_book)
        recomposed_book = book_store.compose([revised_chapter.artifact_id.split(":", 1)[0], second["chapter_expression"]["artifact_id"].split(":", 1)[0]], title="The Lantern at Low Water")
        accepted_book = book_store.accept(recomposed_book["book_expression_id"], accepted_by="canonical-dogfood")
        exported_book = workspace_root / "book_export.md"
        book_store.export(accepted_book["book_expression_id"], exported_book)
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
        reconciliation = ReconciliationStore(workspace_root)
        inspection = reconciliation.inspect(
            bootstrap.external_edit_path(workspace_root),
            expressions["chapter_expression"]["artifact_id"],
        )
        proposed = reconciliation.propose(inspection["inspection_id"])
        plan = reconciliation.plan(inspection["inspection_id"], proposed["proposal_ids"])
        publication = reconciliation.publish(plan["application_set_id"])
        publication_id = publication["publication_id"]
        publication_review = reconciliation.review(publication_id)
        decisions = {}
        scene_candidates_seen = 0
        for candidate in publication_review["candidates"]:
            if candidate["candidate_type"] == "transition":
                decision = "deferred"
            else:
                scene_candidates_seen += 1
                decision = {1: "accepted", 3: "rejected"}.get(scene_candidates_seen, "deferred")
            decisions[candidate["candidate_id"]] = reconciliation.decide(
                candidate["candidate_id"], decision, decided_by="canonical-dogfood",
                rationale=f"canonical mixed-decision dogfood: {decision}",
            )
        recomposed = reconciliation.recompose(publication_id)
        accepted_recomposed = reconciliation.accept_recomposed_chapter(
            publication_id, recomposed["chapter_expression"],
            accepted_by="canonical-dogfood", allow_review=True,
        )
        completion = reconciliation.complete(
            publication_id, "partially_reconciled",
            completed_by="canonical-dogfood",
            rationale="accepted one Scene, rejected one Scene, deferred the transition",
        )
        return {
            "project": "The Lantern at Low Water",
            "copied_to_temporary_workspace": True,
            "required_artifacts_present": all((workspace / path).is_file() for path in required),
            "accepted_scene_realizations": len(accepted_realizations),
            "accepted_identity": native["identity"] is not None,
            "accepted_blueprint": native["blueprint"] is not None,
            "accepted_chapter_structure": native["chapter"] is not None,
            "accepted_scene_expressions": len(expressions["scene_expressions"]),
            "accepted_chapter_expression": expressions["chapter_expression"]["artifact_id"],
            "accepted_transitions": len(expressions["transitions"]),
            "accepted_second_chapter": second["chapter_expression"]["artifact_id"],
            "accepted_book": accepted_book["book_expression_id"],
            "book_initial": {"id": initial_book, "freshness_after_chapter_revision": stale_book["freshness"]},
            "book_recomposed": recomposed_book["book_expression_id"],
            "book_export_clean": "auteur:scene" not in exported_book.read_text(encoding="utf-8"),
            "critic_statuses": [outcome.status.value for outcome in result.outcomes],
            "review_id": review["review_id"],
            "review_text": format_review(review),
            "reconciliation": {
                "inspection_id": inspection["inspection_id"],
                "proposal_ids": proposed["proposal_ids"],
                "application_set_id": plan["application_set_id"],
                "publication_id": publication_id,
                "publication_status": publication_review["status"],
                "decisions": {key: value["decision"] for key, value in decisions.items()},
                "recomposed_chapter_expression": recomposed["chapter_expression"],
                "accepted_chapter_expression": accepted_recomposed["chapter_expression"],
                "completion_status": completion["completion_status"],
            },
            "derived_artifacts_written_to": "temporary workspace only",
            "untraversed_stages": [],
            "friction": "None in the bounded canonical reconciliation workflow.",
        }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
