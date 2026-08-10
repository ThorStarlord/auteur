"""Expression CLI — register subcommands and dispatch handlers."""
from __future__ import annotations

import sys
from pathlib import Path

from auteur.cli_formatters import format_error
from auteur.expression.formatters import (
    format_accept_chapter,
    format_book_accept,
    format_book_accept_recomposed,
    format_book_accept_recomposed_duplicate,
    format_book_accept_recomposed_error,
    format_book_candidate_history,
    format_book_compare,
    format_book_compare_recomposition,
    format_book_compare_recomposition_error,
    format_book_complete,
    format_book_complete_duplicate,
    format_book_complete_error,
    format_book_compose,
    format_book_decision,
    format_book_inspect,
    format_book_inspect_acceptance,
    format_book_inspect_comparison,
    format_book_inspect_completion,
    format_book_inspect_manuscript,
    format_book_inspect_publication,
    format_book_plan,
    format_book_publish,
    format_book_publish_error,
    format_book_recompose,
    format_book_recompose_error,
    format_book_route_inspection,
    format_book_show_candidate_decision,
    format_book_show_inspection,
    format_book_show_plan,
    format_book_show_recomposition,
    format_compare,
    format_compare_chapters,
    format_compose_chapter,
    format_generate,
    format_inspect,
    format_inspect_chapter,
    format_inspect_manuscript,
    format_not_found,
    format_reconcile_accept_chapter,
    format_reconcile_complete,
    format_reconcile_decide,
    format_reconcile_decisions,
    format_reconcile_inspect,
    format_reconcile_inspect_publication,
    format_reconcile_plan,
    format_reconcile_propose,
    format_reconcile_publish,
    format_reconcile_publish_error,
    format_reconcile_recompose,
    format_reconcile_review,
    format_reconcile_show,
    format_reconcile_show_plan,
    format_reject_accept,
)
from auteur.expression.serializers import serialize_export_book, serialize_export_chapter

def _err(m):
    print(format_error(m), file=sys.stderr)


def _pilot_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / ".auteur").is_dir() or (parent / "story_identity.yaml").exists() or (parent / "blueprint.yaml").exists():
            return parent
    return path.parent


def register_expression_subcommands(sub):
    p = sub.add_parser("expression", help="Generate and review Scene Realization prose candidates.")
    expression_sub = p.add_subparsers(dest="expression_command", required=True)
    p = expression_sub.add_parser("generate", help="Generate one versioned prose candidate for a Scene Realization.")
    p.add_argument("scene", type=Path)
    p.add_argument("--text", default=None)
    p.add_argument("--text-file", type=Path, default=None)
    p.add_argument("--pov", default=None)
    p.add_argument("--tense", default=None)
    p.add_argument("--narrative-distance", default=None)
    p.add_argument("--voice-id", default=None)
    p.add_argument("--target-effect", default=None)
    p.add_argument("--executor-kind", default="human-authored")
    p.add_argument("--provider", default=None)
    p.add_argument("--model", default=None)
    p = expression_sub.add_parser("inspect", help="Inspect a prose candidate.")
    p.add_argument("candidate")
    p.add_argument("--project", type=Path, required=True)
    p = expression_sub.add_parser("compare", help="Compare two prose candidates.")
    p.add_argument("candidate_a")
    p.add_argument("candidate_b")
    p.add_argument("--project", type=Path, required=True)
    p = expression_sub.add_parser("reject", help="Reject a prose candidate while preserving its history.")
    p.add_argument("candidate")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--by", default="author")
    p.add_argument("--reason", default="")
    p = expression_sub.add_parser("revalidate", help="Review a stale candidate as aligned with the current Scene.")
    p.add_argument("candidate")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--by", default="author")
    p = expression_sub.add_parser("acknowledge", help="Acknowledge intentional divergence from the current Scene.")
    p.add_argument("candidate")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--by", default="author")
    p.add_argument("--reason", required=True)
    p = expression_sub.add_parser("accept", help="Explicitly accept a prose candidate.")
    p.add_argument("candidate")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--by", default="author")
    p.add_argument("--allow-divergence", action="store_true")
    p = expression_sub.add_parser("compose-chapter", help="Compose accepted Scene Expressions into a derived Chapter Expression.")
    p.add_argument("chapter")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--scene", action="append", default=[], help="Override selected Scene as scene_id=prose_vNNN.")
    p = expression_sub.add_parser("inspect-chapter", help="Inspect a Chapter Expression assembly.")
    p.add_argument("chapter_expression")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("accept-chapter", help="Accept a Chapter Expression assembly.")
    p.add_argument("chapter_expression")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--by", default="author")
    p.add_argument("--allow-review", action="store_true")
    p = expression_sub.add_parser("inspect-manuscript", help="Inspect a marked or markerless external Chapter manuscript.")
    p.add_argument("manuscript", type=Path)
    p.add_argument("--against", required=True)
    p.add_argument("--project", type=Path, required=True)
    p = expression_sub.add_parser("export-chapter", help="Export a Chapter Expression manuscript.")
    p.add_argument("chapter_expression")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    export_group = p.add_mutually_exclusive_group(required=True)
    export_group.add_argument("--clean", action="store_true")
    export_group.add_argument("--with-markers", action="store_true")
    p = expression_sub.add_parser("compare-chapters", help="Compare two Chapter Expression assemblies.")
    p.add_argument("assembly_a")
    p.add_argument("assembly_b")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p = expression_sub.add_parser("compose-book", help="Compose accepted Chapter Expressions into a derived Book Manuscript.")
    p.add_argument("project", type=Path)
    p.add_argument("--chapter", action="append", dest="chapters", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--separator", default="---")
    p = expression_sub.add_parser("inspect-book", help="Inspect a Book Manuscript and its freshness.")
    p.add_argument("book_expression")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p = expression_sub.add_parser("compare-books", help="Compare two Book Manuscript assemblies.")
    p.add_argument("book_a")
    p.add_argument("book_b")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p = expression_sub.add_parser("accept-book", help="Explicitly accept a Book Manuscript assembly.")
    p.add_argument("book_expression")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--by", default="author")
    p = expression_sub.add_parser("export-book", help="Export a clean Book Manuscript.")
    p.add_argument("book_expression")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = expression_sub.add_parser("inspect-book-manuscript", help="Inspect a marked external Book manuscript without mutation.")
    p.add_argument("manuscript", type=Path)
    p.add_argument("--against", required=True)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("route-book-inspection", help="Route a Book inspection to Chapter reconciliation or Book proposals.")
    p.add_argument("inspection_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p = expression_sub.add_parser("show-book-inspection", help="Show a Book external-edit inspection.")
    p.add_argument("inspection_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p = expression_sub.add_parser("plan-book-reconciliation", help="Create a derived Book reconciliation application plan.")
    p.add_argument("inspection_id")
    p.add_argument("--proposal", action="append", dest="proposals", default=[], required=True, help="Book proposal ID (repeatable).")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("show-book-plan", help="Show a Book reconciliation application plan.")
    p.add_argument("plan_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("publish-book-reconciliation", help="Publish a ready Book plan into unaccepted candidates.")
    p.add_argument("plan_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("inspect-book-publication", help="Inspect a Book reconciliation publication transaction.")
    p.add_argument("publication_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    for _decision_cmd, _decision_help in (
        ("approve-book-candidate", "Approve a published Book candidate for recomposition (append-only decision; no recomposition, no acceptance)."),
        ("reject-book-candidate", "Reject a published Book candidate (append-only decision; supersedes any prior decision)."),
        ("defer-book-candidate", "Defer a published Book candidate (nonterminal; can be approved or rejected later)."),
    ):
        p = expression_sub.add_parser(_decision_cmd, help=_decision_help)
        p.add_argument("candidate")
        p.add_argument("--reason", required=True)
        p.add_argument("--project", type=Path, required=True)
        p.add_argument("--json", action="store_true")
        p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("recompose-book-from-accepted", help="Recompose a derived, noncanonical Book from current accepted Chapter and Book-owned pointers.")
    p.add_argument("publication_id")
    p.add_argument("--require-book-revision", dest="require_book_revision", default=None, help="Block unless the current accepted Book is this revision.")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("show-book-recomposition", help="Show the most recent Book recomposition artifact.")
    p.add_argument("publication_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("compare-book-recomposition", help="Compare a Book recomposition against an external manuscript (read-only, deterministic).")
    p.add_argument("recomposition_id")
    p.add_argument("--external-manuscript", dest="external_manuscript", type=Path, default=None, help="External manuscript path (defaults to the source inspection's manuscript).")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("inspect-book-comparison", help="Inspect a Book recomposition-vs-manuscript comparison report.")
    p.add_argument("comparison_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("accept-recomposed-book", help="Accept an exact-match recomposed Book as canonical (immutable revision + acceptance record, atomic pointer move).")
    p.add_argument("comparison_id")
    p.add_argument("--reason", default=None, help="Optional acceptance rationale recorded in the immutable artifacts.")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("inspect-book-acceptance", help="Inspect a Book acceptance record.")
    p.add_argument("acceptance_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("complete-book-reconciliation", help="Complete the Book reconciliation workflow (administrative closure, no narrative changes).")
    p.add_argument("acceptance_id")
    p.add_argument("--reason", default=None, help="Optional completion rationale recorded in the immutable record.")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("inspect-book-reconciliation-completion", help="Inspect a Book reconciliation completion record.")
    p.add_argument("completion_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("show-book-candidate-decision", help="Show a Book candidate decision record.")
    p.add_argument("decision")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("book-candidate-history", help="Show the append-only decision history and active status for a Book candidate.")
    p.add_argument("candidate")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("reconcile", help="Inspect and propose Chapter manuscript reconciliation actions.")
    reconcile_sub = p.add_subparsers(dest="reconcile_command", required=True)
    p = reconcile_sub.add_parser("inspect", help="Create a read-only reconciliation inspection report.")
    p.add_argument("manuscript", type=Path)
    p.add_argument("--against", required=True)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("propose", help="Create noncanonical reconciliation proposals.")
    p.add_argument("inspection_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("show", help="Show a reconciliation run, inspection, or proposal.")
    p.add_argument("identifier")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("plan", help="Create a read-only reconciliation application plan.")
    p.add_argument("--inspection", required=True)
    p.add_argument("--select", required=True, help="Comma-separated proposal IDs.")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("show-plan", help="Show a reconciliation application plan.")
    p.add_argument("application_set_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("publish", help="Publish a ready reconciliation plan into unaccepted candidates.")
    p.add_argument("plan_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("inspect-publication", help="Inspect a reconciliation publication transaction.")
    p.add_argument("publication_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("review", help="Review published reconciliation candidates.")
    p.add_argument("publication_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("decide", help="Accept, reject, or defer one published candidate.")
    p.add_argument("candidate_id")
    decision_group = p.add_mutually_exclusive_group(required=True)
    decision_group.add_argument("--accept", action="store_true")
    decision_group.add_argument("--reject", action="store_true")
    decision_group.add_argument("--defer", action="store_true")
    p.add_argument("--by", default="author")
    p.add_argument("--reason", default="")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("decisions", help="Show reconciliation candidate decisions.")
    p.add_argument("publication_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("recompose", help="Recompose a Chapter from current accepted sources.")
    p.add_argument("publication_id")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p = reconcile_sub.add_parser("accept-chapter", help="Accept a recomposed Chapter Expression.")
    p.add_argument("publication_id")
    p.add_argument("chapter_expression")
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--by", default="author")
    p.add_argument("--allow-review", action="store_true")
    p.add_argument("--json", action="store_true")
    p = reconcile_sub.add_parser("complete", help="Close a reconciliation workflow.")
    p.add_argument("publication_id")
    p.add_argument("--status", required=True, choices=["reconciled", "partially_reconciled", "divergent", "abandoned", "superseded"])
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--by", default="author")
    p.add_argument("--reason", default="")
    p.add_argument("--json", action="store_true")


def dispatch_expression(args) -> int:
    # === expression pilot ===
    if args.command == "expression":
        from auteur.expression import ChapterExpressionStore, ExpressionConstraints, ExpressionStore
        if args.expression_command == "reconcile":
            from auteur.expression.reconciliation import ReconciliationStore
            store = ReconciliationStore(args.project)
            if args.reconcile_command == "plan":
                result = store.plan(args.inspection, [item for item in args.select.split(",") if item])
                print(format_reconcile_plan(result, json_mode=args.json))
                return 0
            if args.reconcile_command == "show-plan":
                result = store.show_plan(args.application_set_id)
                print(format_reconcile_show_plan(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.reconcile_command == "publish":
                try:
                    result = store.publish(args.plan_id)
                except ValueError as exc:
                    print(format_reconcile_publish_error(exc, json_mode=args.json, verbose=args.verbose))
                    return 1
                print(format_reconcile_publish(result, json_mode=args.json))
                return 0
            if args.reconcile_command == "inspect-publication":
                result = store.inspect_publication(args.publication_id)
                print(format_reconcile_inspect_publication(result, json_mode=args.json))
                return 0
            if args.reconcile_command == "review":
                result = store.review(args.publication_id)
                print(format_reconcile_review(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.reconcile_command == "decide":
                decision = "accepted" if args.accept else "rejected" if args.reject else "deferred"
                try:
                    result = store.decide(args.candidate_id, decision, decided_by=args.by, rationale=args.reason)
                except ValueError as exc:
                    _err(str(exc))
                    return 1
                print(format_reconcile_decide(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.reconcile_command == "decisions":
                result = store.decisions(args.publication_id)
                print(format_reconcile_decisions(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.reconcile_command == "recompose":
                try:
                    result = store.recompose(args.publication_id)
                except ValueError as exc:
                    _err(str(exc))
                    return 1
                print(format_reconcile_recompose(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.reconcile_command == "accept-chapter":
                try:
                    result = store.accept_recomposed_chapter(args.publication_id, args.chapter_expression, accepted_by=args.by, allow_review=args.allow_review)
                except ValueError as exc:
                    _err(str(exc))
                    return 1
                print(format_reconcile_accept_chapter(result, json_mode=args.json))
                return 0
            if args.reconcile_command == "complete":
                try:
                    result = store.complete(args.publication_id, args.status, completed_by=args.by, rationale=args.reason)
                except ValueError as exc:
                    _err(str(exc))
                    return 1
                print(format_reconcile_complete(result, json_mode=args.json, publication_id=args.publication_id, status=args.status))
                return 0
            if args.reconcile_command == "inspect":
                report = store.inspect(args.manuscript, args.against)
                print(format_reconcile_inspect(report, json_mode=args.json))
                return 0
            if args.reconcile_command == "propose":
                result = store.propose(args.inspection_id)
                print(format_reconcile_propose(result, json_mode=args.json))
                return 0
            result = store.proposal_status(args.identifier) if args.identifier.startswith("proposal_") else store.show(args.identifier)
            print(format_reconcile_show(result, json_mode=args.json, verbose=args.verbose, identifier=args.identifier))
            return 0
        if args.expression_command == "generate":
            if args.text is None and args.text_file is None:
                _err("expression generate requires --text or --text-file")
                return 1
            if args.text is not None and args.text_file is not None:
                _err("provide only one of --text or --text-file")
                return 1
            text = args.text if args.text is not None else args.text_file.read_text(encoding="utf-8")
            project = _pilot_project_root(args.scene)
            constraints = ExpressionConstraints(
                pov=args.pov, tense=args.tense, narrative_distance=args.narrative_distance,
                voice_id=args.voice_id, target_effect=args.target_effect,
            )
            metadata = ExpressionStore(project).generate(
                args.scene, text, constraints=constraints,
                executor={"kind": args.executor_kind, "provider": args.provider, "model": args.model},
            )
            print(format_generate(metadata.candidate_id))
            return 0
        if args.expression_command == "compose-chapter":
            if args.scene:
                _err("scene selection overrides are not supported in the deterministic pilot")
                return 2
            metadata = ChapterExpressionStore(args.project).compose(args.chapter)
            print(format_compose_chapter(metadata.artifact_id))
            return 0
        if args.expression_command == "inspect-chapter":
            store = ChapterExpressionStore(args.project)
            metadata = store.inspect(args.chapter_expression)
            status = store.status(args.chapter_expression)
            print(format_inspect_chapter(metadata, status, json_mode=args.json, verbose=args.verbose))
            return 0
        if args.expression_command == "accept-chapter":
            metadata = ChapterExpressionStore(args.project).accept(args.chapter_expression, accepted_by=args.by, allow_review=args.allow_review)
            print(format_accept_chapter(metadata))
            return 0
        if args.expression_command == "inspect-manuscript":
            print(format_inspect_manuscript(ChapterExpressionStore(args.project).inspect_manuscript(args.manuscript, args.against)))
            return 0
        if args.expression_command == "export-chapter":
            try:
                result = serialize_export_chapter(ChapterExpressionStore(args.project), args.chapter_expression, args.output, args.clean, _err=_err)
            except FileExistsError:
                _err(f"output already exists: {args.output}; choose another path")
                return 2
            print(result)
            return 0
        if args.expression_command == "compare-chapters":
            store = ChapterExpressionStore(args.project)
            first, second = store.inspect(args.assembly_a), store.inspect(args.assembly_b)
            report = {"assembly_a": first.artifact_id, "assembly_b": second.artifact_id, "scene_revisions": {item["scene_id"]: {"a": item["expression_revision"], "b": next((other["expression_revision"] for other in second.source_scenes if other["scene_id"] == item["scene_id"]), None)} for item in first.source_scenes}, "order_a": first.source_order, "order_b": second.source_order, "transitions_a": first.transitions, "transitions_b": second.transitions}
            import difflib
            text_a = store._metadata_path(first.artifact_id).with_suffix(".md").read_text(encoding="utf-8")
            text_b = store._metadata_path(second.artifact_id).with_suffix(".md").read_text(encoding="utf-8")
            report["diff"] = "".join(difflib.unified_diff(text_a.splitlines(True), text_b.splitlines(True), fromfile=first.artifact_id, tofile=second.artifact_id))
            print(format_compare_chapters(report))
            return 0
        if args.expression_command in {"compose-book", "inspect-book", "compare-books", "accept-book", "export-book", "inspect-book-manuscript", "route-book-inspection", "show-book-inspection", "plan-book-reconciliation", "show-book-plan", "publish-book-reconciliation", "inspect-book-publication", "approve-book-candidate", "reject-book-candidate", "defer-book-candidate", "show-book-candidate-decision", "book-candidate-history", "recompose-book-from-accepted", "show-book-recomposition", "compare-book-recomposition", "inspect-book-comparison", "accept-recomposed-book", "inspect-book-acceptance", "complete-book-reconciliation", "inspect-book-reconciliation-completion"}:
            from auteur.expression.book import BookExpressionStore
            from auteur.expression.book_reconciliation import BookPublicationRejected, BookReconciliationStore
            _decision_status = {"approve-book-candidate": "approved", "reject-book-candidate": "rejected", "defer-book-candidate": "deferred"}
            if args.expression_command in _decision_status:
                store = BookReconciliationStore(args.project)
                success, result = store.decide_candidate(args.candidate, _decision_status[args.expression_command], args.reason)
                print(format_book_decision(result, success, json_mode=args.json, verbose=args.verbose))
                return 0 if success else 1
            if args.expression_command == "book-candidate-history":
                result = BookReconciliationStore(args.project).book_candidate_decision_history(args.candidate)
                print(format_book_candidate_history(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "show-book-candidate-decision":
                result = BookReconciliationStore(args.project).show_book_candidate_decision(args.decision)
                print(format_book_show_candidate_decision(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "plan-book-reconciliation":
                result = BookReconciliationStore(args.project).plan(args.inspection_id, args.proposals)
                print(format_book_plan(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "show-book-plan":
                result = BookReconciliationStore(args.project).show_book_plan(args.plan_id)
                print(format_book_show_plan(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "publish-book-reconciliation":
                try:
                    result = BookReconciliationStore(args.project).publish(args.plan_id)
                except BookPublicationRejected as exc:
                    print(format_book_publish_error(exc, json_mode=args.json, verbose=args.verbose))
                    return 1
                print(format_book_publish(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "inspect-book-publication":
                result = BookReconciliationStore(args.project).inspect_book_publication(args.publication_id)
                print(format_book_inspect_publication(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "recompose-book-from-accepted":
                store = BookReconciliationStore(args.project)
                success, result = store.recompose_book_from_accepted_sources(args.publication_id, book_revision_required=args.require_book_revision)
                if not success:
                    print(format_book_recompose_error(result, json_mode=args.json, verbose=args.verbose))
                    return 1
                print(format_book_recompose(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "show-book-recomposition":
                try:
                    result = BookReconciliationStore(args.project).load_recomposed_book(args.publication_id)
                except FileNotFoundError:
                    print(format_not_found("recomposition", args.publication_id, "run recompose-book-from-accepted first."))
                    return 1
                print(format_book_show_recomposition(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "compare-book-recomposition":
                store = BookReconciliationStore(args.project)
                success, result = store.compare_book_recomposition(args.recomposition_id, args.external_manuscript)
                if not success:
                    print(format_book_compare_recomposition_error(result, json_mode=args.json, verbose=args.verbose))
                    return 1
                print(format_book_compare_recomposition(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "inspect-book-comparison":
                try:
                    result = BookReconciliationStore(args.project).load_book_comparison(args.comparison_id)
                except FileNotFoundError:
                    print(format_not_found("comparison", args.comparison_id, "run compare-book-recomposition first."))
                    return 1
                print(format_book_inspect_comparison(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "accept-recomposed-book":
                store = BookReconciliationStore(args.project)
                success, result = store.accept_recomposed_book(args.comparison_id, args.reason)
                if not success:
                    print(format_book_accept_recomposed_error(result, json_mode=args.json, verbose=args.verbose))
                    return 1
                if result.get("status") == "duplicate":
                    print(format_book_accept_recomposed_duplicate(result, json_mode=getattr(args, 'json', False)))
                    return 0
                counts_source = store.load_book_comparison(args.comparison_id)["summary"]["residual_counts"]
                print(format_book_accept_recomposed(result, counts_source=counts_source, json_mode=getattr(args, 'json', False)))
                return 0
            if args.expression_command == "inspect-book-acceptance":
                try:
                    result = BookReconciliationStore(args.project).load_book_acceptance(args.acceptance_id)
                except FileNotFoundError:
                    print(format_not_found("acceptance", args.acceptance_id, "run accept-recomposed-book first."))
                    return 1
                print(format_book_inspect_acceptance(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "complete-book-reconciliation":
                store = BookReconciliationStore(args.project)
                success, result = store.complete_book_reconciliation(args.acceptance_id, args.reason)
                if not success:
                    print(format_book_complete_error(result, json_mode=args.json, verbose=args.verbose))
                    return 1
                if result.get("status") == "duplicate":
                    print(format_book_complete_duplicate(result, json_mode=getattr(args, 'json', False)))
                    return 0
                print(format_book_complete(result, json_mode=getattr(args, 'json', False)))
                return 0
            if args.expression_command == "inspect-book-reconciliation-completion":
                try:
                    result = BookReconciliationStore(args.project).load_book_reconciliation_completion(args.completion_id)
                except FileNotFoundError:
                    print(format_not_found("completion", args.completion_id, "run complete-book-reconciliation first."))
                    return 1
                print(format_book_inspect_completion(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "inspect-book-manuscript":
                result = BookReconciliationStore(args.project).inspect(args.manuscript, args.against)
                print(format_book_inspect_manuscript(result, json_mode=args.json, verbose=args.verbose))
                return 0
            if args.expression_command == "route-book-inspection":
                result = BookReconciliationStore(args.project).route(args.inspection_id)
                print(format_book_route_inspection(result, json_mode=args.json))
                return 0
            if args.expression_command == "show-book-inspection":
                result = BookReconciliationStore(args.project)._load_inspection(args.inspection_id)
                print(format_book_show_inspection(result, json_mode=args.json))
                return 0
            if args.expression_command == "compose-book":
                print(format_book_compose(BookExpressionStore(args.project).compose(args.chapters, title=args.title, separator=args.separator)["book_expression_id"]))
                return 0
            book_store = BookExpressionStore(args.project)
            if args.expression_command == "inspect-book":
                result = book_store.inspect(args.book_expression)
                print(format_book_inspect(result, json_mode=args.json))
                return 0
            if args.expression_command == "compare-books":
                print(format_book_compare(book_store.compare(args.book_a, args.book_b)))
                return 0
            if args.expression_command == "accept-book":
                print(format_book_accept(book_store.accept(args.book_expression, accepted_by=args.by)))
                return 0
            print(serialize_export_book(book_store, args.book_expression, args.output))
            return 0
        store = ExpressionStore(args.project)
        if args.expression_command == "inspect":
            metadata = store.inspect(args.candidate)
            status = store.status(args.candidate)
            print(format_inspect(metadata, status, json_mode=getattr(args, 'json', False), verbose=getattr(args, 'verbose', False)))
            return 0
        if args.expression_command == "compare":
            print(format_compare(store.compare(args.candidate_a, args.candidate_b)))
            return 0
        if args.expression_command == "reject":
            metadata = store.reject(args.candidate, rejected_by=args.by, reason=args.reason)
        elif args.expression_command == "revalidate":
            metadata = store.revalidate(args.candidate, reviewed_by=args.by)
        elif args.expression_command == "acknowledge":
            metadata = store.acknowledge(args.candidate, acknowledged_by=args.by, reason=args.reason)
        else:
            metadata = store.accept(args.candidate, accepted_by=args.by, allow_divergence=args.allow_divergence)
        print(format_reject_accept(metadata))
        return 0
