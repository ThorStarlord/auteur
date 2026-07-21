"""CLI for convergence workflow — argparse subcommand registration."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from auteur.convergence.candidates import CandidateStore
from auteur.convergence.comparison import compare_candidates
from auteur.convergence.models import (
    GenerationStrategy,
    RevisionTarget,
    SourceObligation,
)
from auteur.convergence.obligations import collect_obligations
from auteur.convergence.persistence import ConvergenceStore
from auteur.convergence.planner import ProposalStore
from auteur.convergence.preservation import analyze_preservation
from auteur.convergence.scope import (
    handle_ambiguous_target,
    resolve_target,
    resolve_target_from_impact,
)


def register_realization_subcommands(sub) -> None:
    """Register convergence subcommands under 'realization'."""
    p = sub.add_parser("realization", help="Manage scene/chapter realization convergence and revision.")
    rs = p.add_subparsers(dest="realization_command", required=True)

    p_status = rs.add_parser("status", help="Show convergence status for a chapter/scene.")
    p_status.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_status.add_argument("--chapter", type=int, required=True, help="Chapter index.")
    p_status.add_argument("--scene", type=str, default=None, help="Scene ID.")
    p_status.add_argument("--json", action="store_true", help="Output JSON.")

    p_revise = rs.add_parser("revise", help="Inspect or initialize a revision workflow.")
    p_revise.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_revise.add_argument("--chapter", type=int, required=True, help="Chapter index.")
    p_revise.add_argument("--scene", type=str, default=None, help="Scene ID.")
    p_revise.add_argument("--json", action="store_true", help="Output JSON.")

    p_candidates = rs.add_parser("candidates", help="List candidates for a chapter/scene.")
    p_candidates.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_candidates.add_argument("--chapter", type=int, required=True, help="Chapter index.")
    p_candidates.add_argument("--scene", type=str, default=None, help="Scene ID.")
    p_candidates.add_argument("--json", action="store_true", help="Output JSON.")

    p_generate = rs.add_parser("generate-candidate", help="Generate a candidate realization.")
    p_generate.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_generate.add_argument("--chapter", type=int, required=True, help="Chapter index.")
    p_generate.add_argument("--scene", type=str, default=None, help="Scene ID.")
    p_generate.add_argument("--strategy", type=str, default="minimal_repair", choices=[s.value for s in GenerationStrategy], help="Generation strategy.")
    p_generate.add_argument("--json", action="store_true", help="Output JSON.")

    p_register = rs.add_parser("register-candidate", help="Register an externally authored candidate.")
    p_register.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_register.add_argument("--chapter", type=int, required=True, help="Chapter index.")
    p_register.add_argument("--scene", type=str, default=None, help="Scene ID.")
    p_register.add_argument("--file", type=Path, required=True, help="Path to the candidate content file.")
    p_register.add_argument("--json", action="store_true", help="Output JSON.")

    p_compare = rs.add_parser("compare", help="Compare candidates for a target.")
    p_compare.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_compare.add_argument("--chapter", type=int, required=True, help="Chapter index.")
    p_compare.add_argument("--scene", type=str, default=None, help="Scene ID.")
    p_compare.add_argument("--candidate", action="append", default=[], help="Candidate IDs to compare (repeatable).")
    p_compare.add_argument("--json", action="store_true", help="Output JSON.")

    p_reconcile = rs.add_parser("reconcile", help="Create a reconciliation proposal.")
    p_reconcile.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_reconcile.add_argument("--chapter", type=int, required=True, help="Chapter index.")
    p_reconcile.add_argument("--scene", type=str, default=None, help="Scene ID.")
    p_reconcile.add_argument("--json", action="store_true", help="Output JSON.")


def handle_realization_status(args) -> int:
    """Handle 'realization status' command."""
    project = Path(args.project).resolve()
    if not (project / ".auteur").exists() and not (project / "story_identity.yaml").exists():
        print(f"Error: Not an auteur project: {project}", file=sys.stderr)
        return 1

    target = resolve_target(project, chapter_index=args.chapter, scene_id=args.scene)
    store = ConvergenceStore(project)
    candidate_store = CandidateStore(project)
    obligations = collect_obligations(project, target)
    preserved = analyze_preservation(project, target)
    candidates = candidate_store.list_candidates(target.target_id)

    output = _format_status(target, obligations, preserved, candidates)

    if getattr(args, "json", False):
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(_format_status_human(target, obligations, preserved, candidates, store))

    return 0


def handle_realization_revise(args) -> int:
    """Handle 'realization revise' command."""
    project = Path(args.project).resolve()
    if not (project / ".auteur").exists() and not (project / "story_identity.yaml").exists():
        print(f"Error: Not an auteur project: {project}", file=sys.stderr)
        return 1

    target = resolve_target(project, chapter_index=args.chapter, scene_id=args.scene)
    store = ConvergenceStore(project)
    store.save_target(target)
    store.update_latest("target", target.target_id)

    obligations = collect_obligations(project, target)
    preserved = analyze_preservation(project, target)

    output = _format_status(target, obligations, preserved, [])

    if getattr(args, "json", False):
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        lines = ["Revision target initialized:", f"  Target: Chapter {target.chapter_index}"]
        if target.scene_id:
            lines.append(f"  Scene: {target.scene_id}")
        lines.append(f"  Scope: {target.scope.value}")
        lines.append(f"  Target ID: {target.target_id}")
        lines.append("")
        lines.append("Next: generate or register candidates")
        print("\n".join(lines))

    return 0


def handle_realization_candidates(args) -> int:
    """Handle 'realization candidates' command."""
    project = Path(args.project).resolve()
    if not (project / ".auteur").exists() and not (project / "story_identity.yaml").exists():
        print(f"Error: Not an auteur project: {project}", file=sys.stderr)
        return 1

    target = resolve_target(project, chapter_index=args.chapter, scene_id=args.scene)
    store = CandidateStore(project)
    candidates = store.list_candidates(target.target_id)

    if not candidates:
        if getattr(args, "json", False):
            print(json.dumps({"candidates": [], "target_id": target.target_id}))
        else:
            print(f"No candidates found for target Chapter {target.chapter_index}")
            if target.scene_id:
                print(f"  Scene: {target.scene_id}")
            print("  Use 'generate-candidate' or 'register-candidate' to create one.")
        return 0

    if getattr(args, "json", False):
        print(json.dumps([c.model_dump(mode="json") for c in candidates], indent=2, sort_keys=True))
    else:
        print(f"Candidates for Chapter {target.chapter_index}")
        if target.scene_id:
            print(f"  Scene: {target.scene_id}")
        for c in candidates:
            print(f"  {c.candidate_id}")
            print(f"    Status: {c.status.value}")
            print(f"    Strategy: {c.generation_strategy}")
            print(f"    Freshness: {c.freshness}")
            print(f"    Created: {c.created_at}")
            print(f"    Obligations: {len(c.obligations_satisfied)}/{len(c.obligations)} satisfied")

    return 0


def handle_realization_generate_candidate(args) -> int:
    """Handle 'realization generate-candidate' command."""
    project = Path(args.project).resolve()
    if not (project / ".auteur").exists() and not (project / "story_identity.yaml").exists():
        print(f"Error: Not an auteur project: {project}", file=sys.stderr)
        return 1

    target = resolve_target(project, chapter_index=args.chapter, scene_id=args.scene)
    strategy = GenerationStrategy(args.strategy)
    obligations = collect_obligations(project, target)
    preserved = analyze_preservation(project, target)

    store = CandidateStore(project)
    candidate = store.generate_candidate(
        target=target,
        strategy=strategy,
        obligations=[o.obligation_id for o in obligations],
        preserved_regions=preserved,
    )

    output = candidate.model_dump(mode="json")
    if getattr(args, "json", False):
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"Generated candidate: {candidate.candidate_id}")
        print(f"  Target: Chapter {target.chapter_index}")
        if target.scene_id:
            print(f"  Scene: {target.scene_id}")
        print(f"  Strategy: {strategy.value}")
        print(f"  Status: {candidate.status.value}")
        print("  No accepted prose was changed.")

    return 0


def handle_realization_register_candidate(args) -> int:
    """Handle 'realization register-candidate' command."""
    project = Path(args.project).resolve()
    if not (project / ".auteur").exists() and not (project / "story_identity.yaml").exists():
        print(f"Error: Not an auteur project: {project}", file=sys.stderr)
        return 1

    content_path = Path(args.file).resolve()
    if not content_path.exists():
        print(f"Error: File not found: {content_path}", file=sys.stderr)
        return 1

    target = resolve_target(project, chapter_index=args.chapter, scene_id=args.scene)
    obligations = collect_obligations(project, target)
    preserved = analyze_preservation(project, target)

    store = CandidateStore(project)
    try:
        candidate = store.register_candidate(
            target=target,
            content_path=content_path,
            obligations=[o.obligation_id for o in obligations],
            preserved_regions=preserved,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output = candidate.model_dump(mode="json")
    if getattr(args, "json", False):
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"Registered candidate: {candidate.candidate_id}")
        print(f"  Source: {content_path}")
        print(f"  Target: Chapter {target.chapter_index}")
        if target.scene_id:
            print(f"  Scene: {target.scene_id}")
        print("  No accepted prose was changed.")

    return 0


def handle_realization_compare(args) -> int:
    """Handle 'realization compare' command."""
    project = Path(args.project).resolve()
    if not (project / ".auteur").exists() and not (project / "story_identity.yaml").exists():
        print(f"Error: Not an auteur project: {project}", file=sys.stderr)
        return 1

    target = resolve_target(project, chapter_index=args.chapter, scene_id=args.scene)
    store = CandidateStore(project)
    proposal_store = ProposalStore(project)

    if args.candidate:
        candidates = []
        for cid in args.candidate:
            c = store.get_candidate(cid)
            if c is None:
                print(f"Error: Candidate not found: {cid}", file=sys.stderr)
                return 1
            candidates.append(c)
    else:
        candidates = store.list_candidates(target.target_id)

    if len(candidates) < 2:
        print(f"Need at least 2 candidates to compare (found {len(candidates)})", file=sys.stderr)
        return 1

    comparison = compare_candidates(target, candidates)
    proposal_store.save_comparison(comparison)

    output = comparison.model_dump(mode="json")
    if getattr(args, "json", False):
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        print(f"Comparison: {comparison.comparison_id}")
        print(f"  Target: Chapter {target.chapter_index}")
        if target.scene_id:
            print(f"  Scene: {target.scene_id}")
        print(f"  Candidates: {', '.join(comparison.candidate_ids)}")
        print()
        for dim in comparison.dimensions:
            adv = "A" if dim.advantage == "candidate_a" else ("B" if dim.advantage == "candidate_b" else "—")
            print(f"  {dim.name}:  A={dim.candidate_a_value}, B={dim.candidate_b_value}  ({adv})")
        if comparison.conflicts:
            print()
            print("  Conflicts:")
            for conf in comparison.conflicts:
                print(f"    - {conf.description}")
        print()
        if comparison.recommended_candidate_id:
            print(f"  Recommended (workflow priority): {comparison.recommended_candidate_id}")
            print(f"  ({comparison.recommendation_disclaimer})")

    return 0


def handle_realization_reconcile(args) -> int:
    """Handle 'realization reconcile' command."""
    project = Path(args.project).resolve()
    if not (project / ".auteur").exists() and not (project / "story_identity.yaml").exists():
        print(f"Error: Not an auteur project: {project}", file=sys.stderr)
        return 1

    target = resolve_target(project, chapter_index=args.chapter, scene_id=args.scene)
    store = CandidateStore(project)
    obligations = collect_obligations(project, target)
    candidates = store.list_candidates(target.target_id)

    if len(candidates) < 1:
        print("Need at least 1 candidate to reconcile", file=sys.stderr)
        return 1

    comparison = compare_candidates(target, candidates)
    proposal_store = ProposalStore(project)
    proposal = proposal_store.create_proposal(target, candidates, comparison, obligations)

    output = proposal.model_dump(mode="json")
    if getattr(args, "json", False):
        print(json.dumps(output, indent=2, sort_keys=True))
    else:
        _print_reconciliation_human(target, proposal, store, candidates)

    return 0


def _format_status(
    target: RevisionTarget,
    obligations: list[SourceObligation],
    preserved: list[Any],
    candidates: list[Any],
) -> dict[str, Any]:
    return {
        "target": target.model_dump(mode="json"),
        "obligations": [o.model_dump(mode="json") for o in obligations],
        "preserved": [p.model_dump(mode="json") for p in preserved] if preserved else [],
        "candidates": [c.model_dump(mode="json") for c in candidates],
    }


def _format_status_human(
    target: RevisionTarget,
    obligations: list[SourceObligation],
    preserved: list[Any],
    candidates: list[Any],
    store: ConvergenceStore,
) -> str:
    lines = ["Revision Target:"]
    lines.append(f"  Chapter {target.chapter_index}")
    if target.scene_id:
        lines.append(f"  Scene: {target.scene_id}")
    lines.append(f"  Scope: {target.scope.value}")
    if target.impact_finding_id:
        lines.append(f"  Triggered by impact: {target.impact_finding_id}")

    lines.append("")
    required = [o for o in obligations if o.kind.value == "required"]
    advisory = [o for o in obligations if o.kind.value == "advisory"]
    lines.append(f"Required obligations ({len(required)}):")
    for o in required:
        lines.append(f"  - {o.description}")
    if advisory:
        lines.append(f"Advisory ({len(advisory)}):")
        for o in advisory:
            lines.append(f"  - {o.description}")

    lines.append("")
    lines.append(f"Preserved regions ({len(preserved)}):")
    for p in preserved:
        location = p.beat_id or p.section_id or p.scene_id or "—"
        lines.append(f"  {location}: {p.status.value}")
        if p.reason:
            lines.append(f"    Reason: {p.reason}")

    lines.append("")
    lines.append(f"Candidates ({len(candidates)}):")
    for c in candidates:
        lines.append(f"  {c.candidate_id} — {c.status.value}, {c.freshness}")
        if c.generation_strategy:
            lines.append(f"    Strategy: {c.generation_strategy}")

    state = store.gather_state(str(store.project))
    lines.append("")
    lines.append(f"Summary: {state.status_summary}")
    lines.append("")
    lines.append("No accepted prose will be changed.")

    return "\n".join(lines)


def _print_reconciliation_human(
    target: RevisionTarget,
    proposal: Any,
    store: CandidateStore,
    candidates: list[Any],
) -> None:
    print("Reconciliation Proposal:")
    print(f"  Target: Chapter {target.chapter_index}")
    if target.scene_id:
        print(f"  Scene: {target.scene_id}")
    print(f"  Proposal ID: {proposal.proposal_id}")
    print()
    print(f"  Candidates considered: {', '.join(proposal.candidate_ids)}")
    print()
    print(f"  Satisfied obligations ({len(proposal.satisfied_obligations)}):")
    for ob_id in proposal.satisfied_obligations:
        print(f"    ✓ {ob_id}")
    print()
    print(f"  Unsatisfied obligations ({len(proposal.unsatisfied_obligations)}):")
    for ob_id in proposal.unsatisfied_obligations:
        print(f"    ✗ {ob_id}")
    if proposal.conflicts:
        print()
        print(f"  Conflicts ({len(proposal.conflicts)}):")
        for conflict in proposal.conflicts:
            print(f"    - {conflict.description}")
            print(f"      Recommended: {conflict.recommended_action}")
    if proposal.authority_required_choices:
        print()
        print("  Authority required:")
        for choice in proposal.authority_required_choices:
            print(f"    ! {choice}")
    print()
    print("  No accepted prose was changed.")


def dispatch_realization(args) -> int:
    """Dispatch to the appropriate realization handler."""
    handlers = {
        "status": handle_realization_status,
        "revise": handle_realization_revise,
        "candidates": handle_realization_candidates,
        "generate-candidate": handle_realization_generate_candidate,
        "register-candidate": handle_realization_register_candidate,
        "compare": handle_realization_compare,
        "reconcile": handle_realization_reconcile,
    }
    handler = handlers.get(args.realization_command)
    if handler is None:
        print(f"Error: Unknown realization command: {args.realization_command}", file=sys.stderr)
        return 1
    return handler(args)
