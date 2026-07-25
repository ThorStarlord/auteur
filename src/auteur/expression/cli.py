"""Expression CLI — register subcommands and dispatch handlers."""
from __future__ import annotations

import json
import sys
from pathlib import Path
import yaml

from auteur.cli_formatters import format_error

_err = lambda m: print(format_error(m), file=sys.stderr)


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
    p.add_argument("manuscript", type=Path); p.add_argument("--against", required=True); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("route-book-inspection", help="Route a Book inspection to Chapter reconciliation or Book proposals.")
    p.add_argument("inspection_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true")
    p = expression_sub.add_parser("show-book-inspection", help="Show a Book external-edit inspection.")
    p.add_argument("inspection_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true")
    p = expression_sub.add_parser("plan-book-reconciliation", help="Create a derived Book reconciliation application plan.")
    p.add_argument("inspection_id"); p.add_argument("--proposal", action="append", dest="proposals", default=[], required=True, help="Book proposal ID (repeatable)."); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("show-book-plan", help="Show a Book reconciliation application plan.")
    p.add_argument("plan_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("publish-book-reconciliation", help="Publish a ready Book plan into unaccepted candidates.")
    p.add_argument("plan_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("inspect-book-publication", help="Inspect a Book reconciliation publication transaction.")
    p.add_argument("publication_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    for _decision_cmd, _decision_help in (
        ("approve-book-candidate", "Approve a published Book candidate for recomposition (append-only decision; no recomposition, no acceptance)."),
        ("reject-book-candidate", "Reject a published Book candidate (append-only decision; supersedes any prior decision)."),
        ("defer-book-candidate", "Defer a published Book candidate (nonterminal; can be approved or rejected later)."),
    ):
        p = expression_sub.add_parser(_decision_cmd, help=_decision_help)
        p.add_argument("candidate"); p.add_argument("--reason", required=True); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("recompose-book-from-accepted", help="Recompose a derived, noncanonical Book from current accepted Chapter and Book-owned pointers.")
    p.add_argument("publication_id"); p.add_argument("--require-book-revision", dest="require_book_revision", default=None, help="Block unless the current accepted Book is this revision."); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("show-book-recomposition", help="Show the most recent Book recomposition artifact.")
    p.add_argument("publication_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("compare-book-recomposition", help="Compare a Book recomposition against an external manuscript (read-only, deterministic).")
    p.add_argument("recomposition_id"); p.add_argument("--external-manuscript", dest="external_manuscript", type=Path, default=None, help="External manuscript path (defaults to the source inspection's manuscript)."); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("inspect-book-comparison", help="Inspect a Book recomposition-vs-manuscript comparison report.")
    p.add_argument("comparison_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("accept-recomposed-book", help="Accept an exact-match recomposed Book as canonical (immutable revision + acceptance record, atomic pointer move).")
    p.add_argument("comparison_id"); p.add_argument("--reason", default=None, help="Optional acceptance rationale recorded in the immutable artifacts."); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("inspect-book-acceptance", help="Inspect a Book acceptance record.")
    p.add_argument("acceptance_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("complete-book-reconciliation", help="Complete the Book reconciliation workflow (administrative closure, no narrative changes).")
    p.add_argument("acceptance_id"); p.add_argument("--reason", default=None, help="Optional completion rationale recorded in the immutable record."); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("inspect-book-reconciliation-completion", help="Inspect a Book reconciliation completion record.")
    p.add_argument("completion_id"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("show-book-candidate-decision", help="Show a Book candidate decision record.")
    p.add_argument("decision"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
    p = expression_sub.add_parser("book-candidate-history", help="Show the append-only decision history and active status for a Book candidate.")
    p.add_argument("candidate"); p.add_argument("--project", type=Path, required=True); p.add_argument("--json", action="store_true"); p.add_argument("--verbose", action="store_true")
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
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print("Reconciliation application plan")
                    print(f"Status: {result['readiness']}")
                    print("Selected proposals:")
                    for proposal_id in result["proposal_ids"]:
                        print(f"- {proposal_id}")
                    print("Planned outputs:")
                    for output in result["planned_outputs"]:
                        print(f"- {output['output_type']} for {output.get('target_scene', output.get('target_transition'))}")
                    print("No canonical artifacts will be changed.")
                    if result["readiness"] != "ready": print("Resolve the listed freshness or conflict findings before proceeding.")
                return 0
            if args.reconcile_command == "show-plan":
                result = store.show_plan(args.application_set_id)
                if args.json or args.verbose: print(json.dumps(result, indent=2) if args.json else yaml.safe_dump(result, sort_keys=False))
                else: print(f"Reconciliation application plan {result['application_set_id']}\nStatus: {result['readiness']}\nSelected proposals: {len(result['proposal_ids'])}\nNo canonical artifacts will be changed.")
                return 0
            if args.reconcile_command == "publish":
                try:
                    result = store.publish(args.plan_id)
                except ValueError as exc:
                    result = getattr(exc, "result", {"status": "rejected_stale", "message": str(exc), "visible_outputs_created": False})
                    if args.json or args.verbose:
                        print(json.dumps(result, indent=2))
                    else:
                        print("Publication stopped: application plan is stale.")
                        for reason in result.get("stale_reasons", []): print(f"- {reason.get('code')}: {reason.get('recommended_action', reason.get('detail', 'dependency changed'))}")
                        print("No candidates or Chapter preview were created.")
                        print("Next action: Create a new reconciliation inspection and application plan.")
                    return 1
                if args.json: print(json.dumps(result, indent=2))
                else: print(f"Reconciliation publication {result['publication_id']}\nStatus: published\nPublished candidates remain unaccepted.\nNo canonical artifacts were changed.")
                return 0
            if args.reconcile_command == "inspect-publication":
                result = store.inspect_publication(args.publication_id)
                if args.json: print(json.dumps(result, indent=2))
                else: print(f"Reconciliation publication {result['publication_id']}\nStatus: {result['status']}\nChapter candidate: {result['chapter_expression']}")
                return 0
            if args.reconcile_command == "review":
                result = store.review(args.publication_id)
                if args.json or args.verbose: print(json.dumps(result, indent=2) if args.json else yaml.safe_dump(result, sort_keys=False))
                else:
                    print(f"Reconciliation publication review\n\nPublication: {result['publication_id']}\nStatus: {result['status']}")
                    for candidate in result["candidates"]: print(f"- {candidate['owner']}: {candidate['candidate_id']} \u2014 {candidate['status']} ({candidate['freshness']})")
                    print("\nNext actions:"); [print(f"- {action}") for action in result["next_actions"]]
                return 0
            if args.reconcile_command == "decide":
                decision = "accepted" if args.accept else "rejected" if args.reject else "deferred"
                try: result = store.decide(args.candidate_id, decision, decided_by=args.by, rationale=args.reason)
                except ValueError as exc:
                    _err(str(exc)); return 1
                if args.json or args.verbose: print(json.dumps(result, indent=2) if args.json else yaml.safe_dump(result, sort_keys=False))
                else: print(f"Candidate: {result['candidate_id']}\nDecision: {result['decision']}\nAccepted pointer changed: {result['result']['accepted_pointer_changed']}\nNext action: review the publication summary.")
                return 0
            if args.reconcile_command == "decisions":
                result = store.decisions(args.publication_id)
                print(json.dumps(result, indent=2) if args.json else yaml.safe_dump(result, sort_keys=False) if args.verbose else f"Publication {args.publication_id}\nStatus: {result['review']['status']}\nDecisions: {len(result['decisions'])}")
                return 0
            if args.reconcile_command == "recompose":
                try: result = store.recompose(args.publication_id)
                except ValueError as exc: _err(str(exc)); return 1
                if args.json or args.verbose: print(json.dumps(result, indent=2) if args.json else yaml.safe_dump(result, sort_keys=False))
                else: print(f"Canonical-source Chapter recomposition\nChapter Expression: {result['chapter_expression']}\nStatus: {result['status']}\nSources: accepted only\nCanonical Chapter acceptance is not performed.")
                return 0
            if args.reconcile_command == "accept-chapter":
                try: result = store.accept_recomposed_chapter(args.publication_id, args.chapter_expression, accepted_by=args.by, allow_review=args.allow_review)
                except ValueError as exc: _err(str(exc)); return 1
                print(json.dumps(result, indent=2) if args.json else f"Accepted Chapter Expression {result['chapter_expression']} from accepted sources. Reconciliation remains separately completable.")
                return 0
            if args.reconcile_command == "complete":
                try: result = store.complete(args.publication_id, args.status, completed_by=args.by, rationale=args.reason)
                except ValueError as exc: _err(str(exc)); return 1
                print(json.dumps(result, indent=2) if args.json else f"Reconciliation {args.publication_id} completed as {args.status}.")
                return 0
            if args.reconcile_command == "inspect":
                report = store.inspect(args.manuscript, args.against)
                if args.json:
                    print(json.dumps(report, indent=2))
                else:
                    print(f"Chapter reconciliation inspection {report['inspection_id']}")
                    print(f"Status: {report['status']}")
                    if report["status"] == "no_changes":
                        print("No changes detected.")
                        for transition in report.get("recognized_transitions", []):
                            print(f"Transition {transition['transition_id']}: {transition['classification']} \u2014 Owner: {transition['owner']}")
                    elif any(f["classification"] == "markerless" for f in report["findings"]):
                        print("Chapter manuscript cannot be reconciled automatically.")
                        print("Reason: No Auteur Scene or transition markers were found.")
                        consequences = report["findings"][0].get("detail", {}).get("consequences", [])
                        for consequence in consequences:
                            ids = consequence.get("scene_ids", consequence.get("transition_ids", []))
                            print(f"  - {consequence['code']}: {', '.join(ids)}")
                    else:
                        for finding in report["findings"]:
                            print(f"{finding['classification']}: {finding.get('source_section') or 'chapter'} \u2014 {finding['evidence']}")
                            print(f"  Owner: {finding['owner']}")
                    print(f"Proposals: {len(report.get('proposal_ids', []))}")
                return 0
            if args.reconcile_command == "propose":
                result = store.propose(args.inspection_id)
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Reconciliation proposals for {args.inspection_id}: {len(result['proposal_ids'])} created.")
                    for proposal in result["proposals"]:
                        print(f"- {proposal['proposal_type']} \u2192 {proposal.get('target_artifact_id') or 'Chapter transition'}")
                        print(f"  Source revision: {proposal['target_revision']}; Status: {proposal['status']}; Next action: review before applying")
                return 0
            result = store.proposal_status(args.identifier) if args.identifier.startswith("proposal_") else store.show(args.identifier)
            if args.json or args.verbose:
                print(json.dumps(result, indent=2) if args.json else yaml.safe_dump(result, sort_keys=False))
            elif args.identifier.startswith("proposal_"):
                proposal = result["proposal"] if "proposal" in result else result
                print(f"Proposal {proposal['proposal_id']}: {proposal['proposal_type']}")
                print(f"Target: {proposal.get('target_artifact_id') or 'Chapter transition'}")
                print(f"Source revision: {proposal.get('target_revision')}; Status: {result.get('status', proposal.get('status'))}")
                print("Next action: review the proposal before applying it.")
            else:
                print(f"Chapter reconciliation inspection {result.get('inspection_id', result.get('run_id', args.identifier))}")
                print(f"Status: {result.get('status', 'unknown')}")
                print(f"Findings: {len(result.get('findings', []))}; Proposals: {len(result.get('proposal_ids', []))}")
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
            print(metadata.candidate_id)
            return 0
        if args.expression_command == "compose-chapter":
            if args.scene:
                _err("scene selection overrides are not supported in the deterministic pilot")
                return 2
            metadata = ChapterExpressionStore(args.project).compose(args.chapter)
            print(metadata.artifact_id)
            return 0
        if args.expression_command == "inspect-chapter":
            store = ChapterExpressionStore(args.project)
            metadata = store.inspect(args.chapter_expression)
            status = store.status(args.chapter_expression)
            if args.json or args.verbose:
                print(json.dumps({"metadata": metadata.model_dump(mode="json"), "status": status}, indent=2))
                return 0
            print(f"Chapter {metadata.source_chapter['artifact_id']} | assembly revision {metadata.revision} | {metadata.lifecycle.value} | {status['freshness']} | {status['health']}")
            for scene in metadata.source_scenes:
                print(f"  {scene['scene_id']} -> prose_v{scene['expression_revision']:03d} ({scene['freshness']})")
            for transition in metadata.transitions:
                print(f"  transition {transition['transition_id']} ({transition['before_scene']} -> {transition['after_scene']})")
            if status["stale_reasons"]:
                print("Recommended action: recompose or review the affected dependencies.")
            return 0
        if args.expression_command == "accept-chapter":
            metadata = ChapterExpressionStore(args.project).accept(args.chapter_expression, accepted_by=args.by, allow_review=args.allow_review)
            print(json.dumps(metadata.model_dump(mode="json"), indent=2))
            return 0
        if args.expression_command == "inspect-manuscript":
            print(json.dumps(ChapterExpressionStore(args.project).inspect_manuscript(args.manuscript, args.against), indent=2))
            return 0
        if args.expression_command == "export-chapter":
            store = ChapterExpressionStore(args.project)
            if args.output.exists():
                _err(f"output already exists: {args.output}; choose another path")
                return 2
            text = store.clean_export(args.chapter_expression) if args.clean else store._metadata_path(args.chapter_expression).with_suffix(".md").read_text(encoding="utf-8")
            args.output.write_text(text, encoding="utf-8")
            if args.clean:
                print("Warning: clean export removes Scene markers and is not round-trip-safe.", file=sys.stderr)
            print(args.output)
            return 0
        if args.expression_command == "compare-chapters":
            store = ChapterExpressionStore(args.project)
            first, second = store.inspect(args.assembly_a), store.inspect(args.assembly_b)
            report = {"assembly_a": first.artifact_id, "assembly_b": second.artifact_id, "scene_revisions": {item["scene_id"]: {"a": item["expression_revision"], "b": next((other["expression_revision"] for other in second.source_scenes if other["scene_id"] == item["scene_id"]), None)} for item in first.source_scenes}, "order_a": first.source_order, "order_b": second.source_order, "transitions_a": first.transitions, "transitions_b": second.transitions}
            import difflib
            text_a = store._metadata_path(first.artifact_id).with_suffix(".md").read_text(encoding="utf-8")
            text_b = store._metadata_path(second.artifact_id).with_suffix(".md").read_text(encoding="utf-8")
            report["diff"] = "".join(difflib.unified_diff(text_a.splitlines(True), text_b.splitlines(True), fromfile=first.artifact_id, tofile=second.artifact_id))
            print(json.dumps(report, indent=2))
            return 0
        if args.expression_command in {"compose-book", "inspect-book", "compare-books", "accept-book", "export-book", "inspect-book-manuscript", "route-book-inspection", "show-book-inspection", "plan-book-reconciliation", "show-book-plan", "publish-book-reconciliation", "inspect-book-publication", "approve-book-candidate", "reject-book-candidate", "defer-book-candidate", "show-book-candidate-decision", "book-candidate-history", "recompose-book-from-accepted", "show-book-recomposition", "compare-book-recomposition", "inspect-book-comparison", "accept-recomposed-book", "inspect-book-acceptance", "complete-book-reconciliation", "inspect-book-reconciliation-completion"}:
            from auteur.expression.book import BookExpressionStore
            from auteur.expression.book_reconciliation import BookPublicationRejected, BookReconciliationStore
            _decision_status = {"approve-book-candidate": "approved", "reject-book-candidate": "rejected", "defer-book-candidate": "deferred"}
            if args.expression_command in _decision_status:
                store = BookReconciliationStore(args.project)
                success, result = store.decide_candidate(args.candidate, _decision_status[args.expression_command], args.reason)
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                    return 0 if success else 1
                if not success:
                    print("Book candidate decision rejected: stale sources")
                    for reason in result["reasons"]:
                        print(f"  - {reason['code']}")
                    print("No decision was recorded. Publish a fresh Book candidate and decide again.")
                    return 1
                decision = result
                print("Book candidate decision")
                print(f"Candidate: {decision['candidate_id']}")
                print(f"Decision: {decision['decision']['status']} | \"{decision['decision']['reason']}\" (sequence {decision['decision_sequence']})")
                if decision.get("supersedes"):
                    print(f"Supersedes: {decision['supersedes']}")
                if decision.get("accepted_source_id"):
                    print(f"Accepted Book-owned source: {decision['accepted_source_id']}")
                if decision.get("pointer_moved"):
                    ptr = decision["pointer"]
                    print(f"Accepted-source pointer: {ptr['owned_kind']}/{ptr['element_id']} -> revision {ptr['current_revision']}")
                else:
                    print("Accepted-source pointer: unchanged")
                print(f"Decided at: {decision['decided_at']}")
                print("Preview updated: yes")
                print("Book pointer changed: no")
                return 0
            if args.expression_command == "book-candidate-history":
                result = BookReconciliationStore(args.project).book_candidate_decision_history(args.candidate)
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Book candidate {result['candidate_id']}")
                    print(f"Active status: {result['active_status']}")
                    print(f"Decisions ({len(result['decisions'])}):")
                    for d in result["decisions"]:
                        print(f"  {d['decision_sequence']}. {d['decision']['status']} | \"{d['decision']['reason']}\" @ {d['decided_at']}")
                return 0
            if args.expression_command == "show-book-candidate-decision":
                result = BookReconciliationStore(args.project).show_book_candidate_decision(args.decision)
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                else:
                    print("Book candidate decision")
                    print(f"Candidate: {result['candidate_id']}")
                    print(f"Decision: {result['decision']['status']} | \"{result['decision']['reason']}\" (sequence {result.get('decision_sequence', 1)})")
                    if result.get("supersedes"):
                        print(f"Supersedes: {result['supersedes']}")
                    if result.get("accepted_source_id"):
                        print(f"Accepted Book-owned source: {result['accepted_source_id']}")
                    print(f"Decided at: {result['decided_at']}")
                    print(f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']}")
                return 0
            if args.expression_command == "plan-book-reconciliation":
                result = BookReconciliationStore(args.project).plan(args.inspection_id, args.proposals)
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Book reconciliation application plan {result['plan_id']}")
                    print(f"Source Book: {result['source_book_expression']} (revision {result['source_book_revision']})")
                    print(f"Selected proposals: {len(result['selected_proposals'])}")
                    print(f"Readiness: {result['readiness']['status']}")
                    if result["conflicts"]: print(f"Conflicts: {', '.join(sorted({c['conflict_code'] for c in result['conflicts']}))}")
                    print("No candidates, preview, or pointers were created.")
                    print("Recommended next action: " + ("publish this plan into unaccepted candidates" if result["readiness"]["status"] == "ready" else "resolve readiness issues, then re-plan"))
                return 0
            if args.expression_command == "show-book-plan":
                result = BookReconciliationStore(args.project).show_book_plan(args.plan_id)
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Book reconciliation application plan {result['plan_id']}")
                    print(f"Source Book: {result['source_book_expression']} (revision {result['source_book_revision']})")
                    print(f"Selected proposals: {len(result['selected_proposals'])}")
                    print(f"Planned candidates: {len(result['planned_outputs'])}")
                    print(f"Readiness: {result['readiness']['status']}")
                return 0
            if args.expression_command == "publish-book-reconciliation":
                try:
                    result = BookReconciliationStore(args.project).publish(args.plan_id)
                except BookPublicationRejected as exc:
                    if args.json or args.verbose:
                        print(json.dumps(exc.result, indent=2))
                    else:
                        print(f"Book publication rejected: {exc.result['status']}")
                        for reason in exc.result.get("reasons", []):
                            print(f"  - {reason.get('code')}: {reason.get('recommended_action')}")
                        print(f"Visible outputs created: {exc.result.get('visible_outputs_created')}")
                    return 1
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Book reconciliation publication {result['publication_id']}")
                    print(f"Source Book: {result['source_book_expression']} (revision {result['source_book_revision']})")
                    print(f"Published candidates: {len(result['published_candidates'])}")
                    print(f"Preview status: {result['preview']['role']} ({result['preview']['lifecycle']}, noncanonical)")
                    print("Acceptance status: none")
                    print("Accepted Book pointer changed: no")
                    print("Recommended next action: review the published candidates (acceptance is a separate, future step)")
                return 0
            if args.expression_command == "inspect-book-publication":
                result = BookReconciliationStore(args.project).inspect_book_publication(args.publication_id)
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Book reconciliation publication {result['publication_id']}")
                    print(f"Source Book: {result['source_book_expression']} (revision {result['source_book_revision']})")
                    print(f"Published candidates: {len(result['published_candidates'])}")
                    print(f"Preview status: {result['preview']['role']} ({result['preview']['lifecycle']}, noncanonical)")
                    print(f"Acceptance status: {result['acceptance_status']}")
                    print(f"Accepted Book pointer changed: {'yes' if result['accepted_book_pointer_changed'] else 'no'}")
                return 0
            if args.expression_command == "recompose-book-from-accepted":
                store = BookReconciliationStore(args.project)
                success, result = store.recompose_book_from_accepted_sources(args.publication_id, book_revision_required=args.require_book_revision)
                if args.json or args.verbose:
                    print(json.dumps(result if success else result.result, indent=2))
                    return 0 if success else 1
                if not success:
                    print(f"Book recomposition blocked: {result.status}")
                    print(f"Primary reason: {result.reason}")
                    for reason in result.result.get("reasons", []):
                        print(f"  - {reason.get('code')}: {reason.get('recommended_action')}")
                    print("No recomposition artifact was created.")
                    print(f"Recommended action: {result.recommended_action}")
                    return 1
                owned = result["source_pointers"]["book_owned"]
                print("Book recomposition (derived, noncanonical)")
                print(f"Publication: {result['publication_id']}")
                print(f"Source Book: {result['source_book_expression']} (revision {result['source_book_revision']})")
                print(f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']} | Role: {result['role']} | Canonical: {result['canonical']}")
                print(f"Chapters: {len(result['chapters'])} in order {result['order']}")
                print(f"Separator pointer: {'yes' if owned['separator_pointer_id'] else 'default'}")
                print(f"Order pointer: {'yes' if owned['order_pointer_id'] else 'default'}")
                print(f"Title pointer: {'yes' if owned['title_rendering_pointer_id'] else 'default'}")
                print(f"Inserted material pointers: {len(owned['inserted_material_pointer_ids'])}")
                print(f"Content hash: {result['content_hash']}")
                print("Accepted Book pointer changed: no")
                return 0
            if args.expression_command == "show-book-recomposition":
                try:
                    result = BookReconciliationStore(args.project).load_recomposed_book(args.publication_id)
                except FileNotFoundError:
                    print(f"No recomposition found for publication: {args.publication_id}")
                    print("Recommended action: run recompose-book-from-accepted first.")
                    return 1
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                else:
                    owned = result["source_pointers"]["book_owned"]
                    print("Book recomposition (derived, noncanonical)")
                    print(f"Publication: {result['publication_id']}")
                    print(f"Inspection: {result['inspection_id']}")
                    print(f"Role: {result['role']} | Canonical: {result['canonical']}")
                    print(f"Chapters: {len(result['chapters'])} in order {result['order']}")
                    print(f"Book-owned pointers used: separator={bool(owned['separator_pointer_id'])}, order={bool(owned['order_pointer_id'])}, title={bool(owned['title_rendering_pointer_id'])}, material={len(owned['inserted_material_pointer_ids'])}")
                    print(f"Content hash: {result['content_hash']}")
                    print(f"Recomposed at: {result['recomposed_at']}")
                return 0
            if args.expression_command == "compare-book-recomposition":
                store = BookReconciliationStore(args.project)
                success, result = store.compare_book_recomposition(args.recomposition_id, args.external_manuscript)
                if args.json or args.verbose:
                    print(json.dumps(result if success else result.result, indent=2))
                    return 0 if success else 1
                if not success:
                    print(f"Book comparison blocked: {result.status}")
                    print(f"Primary reason: {result.reason}")
                    for reason in result.result.get("reasons", []):
                        print(f"  - {reason.get('code')}: {reason.get('recommended_action')}")
                    print("No comparison report was created.")
                    print(f"Recommended action: {result.recommended_action}")
                    return 1
                counts = result["summary"]["residual_counts"]
                owned_types = sorted({s["owned_kind"] for s in result["book_owned_sources"] if s.get("owned_kind")})
                print("Book recomposition comparison (derived, evaluated, noncanonical)")
                print(f"Comparison: {result['comparison_id']}")
                print(f"Exact match: {counts['exact_match']}")
                print(f"Ready for Book acceptance: {'yes' if result['summary']['ready_for_book_acceptance'] else 'no'}")
                print("Residuals:")
                print(f"  Book-owned: {counts['book_owned_residual']} ({', '.join(owned_types) or 'none'})")
                print(f"  Chapter-owned: {counts['chapter_owned_residual']}")
                print(f"  Structural: {counts['structural_residual']}")
                print(f"  Marker: {counts['marker_residual']}")
                print(f"  Unresolved: {counts['unresolved_residual']}")
                print("Accepted pointers changed: no")
                if result["summary"]["ready_for_book_acceptance"]:
                    action = "accept Book"
                elif counts["chapter_owned_residual"] or counts["structural_residual"] or counts["unresolved_residual"]:
                    action = "re-examine residuals"
                else:
                    action = "re-approve sources"
                print(f"Recommended next action: {action}")
                return 0
            if args.expression_command == "inspect-book-comparison":
                try:
                    result = BookReconciliationStore(args.project).load_book_comparison(args.comparison_id)
                except FileNotFoundError:
                    print(f"No comparison found: {args.comparison_id}")
                    print("Recommended action: run compare-book-recomposition first.")
                    return 1
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2))
                else:
                    counts = result["summary"]["residual_counts"]
                    print("Book recomposition comparison")
                    print(f"Comparison: {result['comparison_id']}")
                    print(f"Recomposition: {result['source_recomposition_id']}")
                    print(f"External manuscript: {result['external_manuscript']['path']}")
                    print(f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']} | Role: {result['role']} | Canonical: {result['canonical']}")
                    print(f"Exact match: {result['summary']['exact_match']}")
                    print(f"Ready for Book acceptance: {'yes' if result['summary']['ready_for_book_acceptance'] else 'no'}")
                    print(f"Findings: {len(result['findings'])} (exact={counts['exact_match']}, book-owned={counts['book_owned_residual']}, chapter-owned={counts['chapter_owned_residual']}, structural={counts['structural_residual']}, marker={counts['marker_residual']}, unresolved={counts['unresolved_residual']})")
                return 0
            if args.expression_command == "accept-recomposed-book":
                store = BookReconciliationStore(args.project)
                success, result = store.accept_recomposed_book(args.comparison_id, args.reason)
                if args.json or args.verbose:
                    print(json.dumps(result if success else result.result, indent=2, default=str))
                    return 0 if success else 1
                if not success:
                    print(f"Book acceptance blocked: {result.status}")
                    print(f"Primary reason: {result.reason}")
                    print("No accepted Book revision, acceptance record, or pointer move was created.")
                    print(f"Recommended action: {result.recommended_action}")
                    return 1
                if result.get("status") == "duplicate":
                    print("Book accepted: yes (duplicate)")
                    print(f"Prior acceptance: {result['prior_acceptance_id']}")
                    print(f"Accepted revision: {result['accepted_book_revision']}")
                    print("No new Book revision or acceptance record created.")
                    print("Recommended next action: inspect the prior acceptance")
                    return 0
                revision = result["accepted_book_revision"]
                record = result["acceptance_record"]
                counts_source = store.load_book_comparison(args.comparison_id)["summary"]["residual_counts"]
                print("Book accepted: yes")
                print(f"Previous revision: {record['previous_book_revision']}")
                print(f"Accepted revision: {revision['revision']}")
                print("Comparison exact match: yes")
                print(f"Residual findings: {sum(v for k, v in counts_source.items() if k != 'exact_match')}")
                print("Accepted Book pointer moved: yes")
                print("Chapter pointers changed: no")
                print("Book-owned pointers changed: no")
                print("Reconciliation completed: no")
                print("Recommended next action: verify reconciliation completion eligibility")
                return 0
            if args.expression_command == "inspect-book-acceptance":
                try:
                    result = BookReconciliationStore(args.project).load_book_acceptance(args.acceptance_id)
                except FileNotFoundError:
                    print(f"No acceptance found: {args.acceptance_id}")
                    print("Recommended action: run accept-recomposed-book first.")
                    return 1
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2, default=str))
                else:
                    transition = result["pointer_transition"]
                    print("Book reconciliation acceptance")
                    print(f"Acceptance: {result['acceptance_id']}")
                    print(f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']}")
                    print(f"Accepted Book: {result['accepted_book_expression_id']} (revision {result['accepted_book_revision']})")
                    print(f"Previous Book: {result['previous_book_expression_id']} (revision {result['previous_book_revision']})")
                    print(f"Source comparison: {result['source_comparison_id']}")
                    print(f"Source recomposition: {result['source_recomposition_id']}")
                    print(f"Chapter sources: {len(result['accepted_chapter_sources'])} | Book-owned sources: {len(result['accepted_book_owned_sources'])}")
                    print(f"Pointer moved: {transition['previous_pointer_id']} -> {transition['current_pointer_id']}")
                return 0
            if args.expression_command == "complete-book-reconciliation":
                store = BookReconciliationStore(args.project)
                success, result = store.complete_book_reconciliation(args.acceptance_id, args.reason)
                if args.json or args.verbose:
                    print(json.dumps(result if success else result.result, indent=2, default=str))
                    return 0 if success else 1
                if not success:
                    print(f"Reconciliation completion blocked: {result.status}")
                    print(f"Primary reason: {result.reason}")
                    print("No completion record was created.")
                    print(f"Recommended action: {result.recommended_action}")
                    return 1
                if result.get("status") == "duplicate":
                    print("Reconciliation completed: yes (duplicate)")
                    print(f"Prior completion: {result['prior_completion_id']}")
                    print("No new completion record created.")
                    print("Recommended next action: inspect the prior completion")
                    return 0
                record = result["completion_record"]
                ch_count = len(record.get("chapter_reconciliations", []))
                ch_done = sum(1 for c in record.get("chapter_reconciliations", []) if "completed" in (c.get("status") or ""))
                bo_count = len(record.get("book_owned_resolutions", []))
                deferred = sum(1 for r in record.get("book_owned_resolutions", []) if "deferred" in (r.get("resolution") or ""))
                print("Reconciliation completed: yes")
                print(f"Accepted Book revision: {record['accepted_book']['revision']}")
                print("Comparison exact match: yes")
                print("Residual findings: 0")
                print(f"Chapter reconciliations complete: {ch_done}/{ch_count}")
                print(f"Book-owned proposals resolved: {bo_count}/{bo_count}")
                print(f"Deferred items remaining: {deferred}")
                print("Accepted Book pointer changed: no")
                print("Narrative artifacts mutated: no")
                return 0
            if args.expression_command == "inspect-book-reconciliation-completion":
                try:
                    result = BookReconciliationStore(args.project).load_book_reconciliation_completion(args.completion_id)
                except FileNotFoundError:
                    print(f"No completion found: {args.completion_id}")
                    print("Recommended action: run complete-book-reconciliation first.")
                    return 1
                if args.json or args.verbose:
                    print(json.dumps(result, indent=2, default=str))
                else:
                    book = result["accepted_book"]
                    ch = result.get("chapter_reconciliations", [])
                    bo = result.get("book_owned_resolutions", [])
                    print("Book reconciliation completion")
                    print(f"Completion: {result['completion_id']}")
                    print(f"Authority: {result['authority']} | Lifecycle: {result['lifecycle']}")
                    print(f"Accepted Book: {book['expression_id']} (revision {book['revision']})")
                    print(f"Source acceptance: {result['source_acceptance_id']}")
                    print(f"Comparison exact match: {result['verification']['exact_match']}")
                    print(f"Chapters: {len(ch)} | Book-owned resolutions: {len(bo)}")
                return 0
            if args.expression_command == "inspect-book-manuscript":
                result = BookReconciliationStore(args.project).inspect(args.manuscript, args.against)
                if args.json or args.verbose: print(json.dumps(result, indent=2))
                else:
                    print(f"Book edit inspection\nBook: {result['book_expression_id']}\nSource revision: {result['book_revision']}\nStatus: {result['status']}")
                    print(f"Chapter-local changes: {len(result['chapter_findings'])}\nBook-owned changes: {len(result['book_findings'])}\nUnresolved: {len(result['unresolved_findings'])}\nNo canonical artifacts were changed.")
                return 0
            if args.expression_command == "route-book-inspection":
                result = BookReconciliationStore(args.project).route(args.inspection_id)
                print(json.dumps(result, indent=2) if args.json else f"Book inspection routing\nStatus: {result['status']}\nChapter routes: {len(result.get('chapter_routes', []))}\nBook proposals: {len(result.get('book_proposals', []))}\nUnresolved: {len(result.get('unresolved', []))}")
                return 0
            if args.expression_command == "show-book-inspection":
                result = BookReconciliationStore(args.project)._load_inspection(args.inspection_id)
                print(json.dumps(result, indent=2) if args.json else f"Book edit inspection {result['inspection_id']}\nStatus: {result['status']}\nChapter-local changes: {len(result['chapter_findings'])}\nBook-owned changes: {len(result['book_findings'])}\nUnresolved: {len(result['unresolved_findings'])}")
                return 0
            if args.expression_command == "compose-book":
                print(BookExpressionStore(args.project).compose(args.chapters, title=args.title, separator=args.separator)["book_expression_id"])
                return 0
            book_store = BookExpressionStore(args.project)
            if args.expression_command == "inspect-book":
                result = book_store.inspect(args.book_expression)
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    metadata = result["metadata"]
                    print(f"Book {metadata['book_id']} | revision {metadata['revision']} | {metadata['lifecycle']} | {result['freshness']}")
                    for chapter in metadata["chapters"]:
                        print(f"  {chapter['position']}: {chapter['chapter_id']} -> {chapter['chapter_expression_id']} v{chapter['accepted_revision']:03d}")
                    if result["stale_sources"]: print(f"Recommended action: {result['recommended_action']}")
                return 0
            if args.expression_command == "compare-books":
                print(json.dumps(book_store.compare(args.book_a, args.book_b), indent=2))
                return 0
            if args.expression_command == "accept-book":
                print(json.dumps(book_store.accept(args.book_expression, accepted_by=args.by), indent=2))
                return 0
            book_store.export(args.book_expression, args.output)
            print(args.output)
            return 0
        store = ExpressionStore(args.project)
        if args.expression_command == "inspect":
            metadata = store.inspect(args.candidate)
            status = store.status(args.candidate)
            print(f"Candidate {metadata.candidate_id} ({metadata.source_scene.artifact_id})")
            print(f"Status: {status['lifecycle']}; freshness: {status['freshness']}; review: {status['review_state']}")
            print("Recommended actions: " + "; ".join(status.get("recommended_actions", [])))
            print(json.dumps({"metadata": metadata.model_dump(mode="json"), "status": status}, indent=2))
            return 0
        if args.expression_command == "compare":
            print(json.dumps(store.compare(args.candidate_a, args.candidate_b), indent=2))
            return 0
        if args.expression_command == "reject":
            metadata = store.reject(args.candidate, rejected_by=args.by, reason=args.reason)
        elif args.expression_command == "revalidate":
            metadata = store.revalidate(args.candidate, reviewed_by=args.by)
        elif args.expression_command == "acknowledge":
            metadata = store.acknowledge(args.candidate, acknowledged_by=args.by, reason=args.reason)
        else:
            metadata = store.accept(args.candidate, accepted_by=args.by, allow_divergence=args.allow_divergence)
        print(json.dumps(metadata.model_dump(mode="json"), indent=2))
        return 0
