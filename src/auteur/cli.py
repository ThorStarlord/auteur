"""Auteur CLI.

Subcommands:
  init    create a project directory from a blueprint
  plan    render the Cartographer prompt (debug, no LLM call)
  draft   plan -> draft -> critique -> iterate (writes artifacts)
  accept  promote the latest draft_v*.md to final.md and update bible
  retry   continue iterating past previous max-iterations cap
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from auteur.blueprint import StoryBlueprint
from auteur.critic import ValidationReport
from auteur.llm import LLMClient
from auteur.pipeline import PipelineRunner
from auteur.project import Project
from auteur.structure import DiagnosticSeverity, analyze_structure
from auteur.structure.proposals import load_resolved_rules, resolve_proposal, write_audit_repair_proposals
from auteur.structure.diagnostics import DiagnosticLayer
from auteur.structure.proposals import (
    StructureProposal,
    apply_proposal_to_blueprint,
    propose_repairs_from_diagnostics,
)


class _HideSuppressedFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        if action.help == argparse.SUPPRESS:
            return ""
        return super()._format_action(action)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="auteur", description="Agentic narrative engineering toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new project directory.")
    p_init.add_argument("path", type=Path)
    p_init.add_argument("--from", dest="blueprint_path", type=Path, required=True)
    p_init.add_argument("--force", action="store_true", help="Re-initialize an existing auteur project directory.")

    p_plan = sub.add_parser("plan", help="Render the Cartographer prompt for a chapter (no LLM call).")
    p_plan.add_argument("blueprint", type=Path)
    p_plan.add_argument("chapter", type=int)

    p_draft = sub.add_parser("draft", help="Plan, draft, validate, iterate one chapter.")
    p_draft.add_argument("project", type=Path)
    p_draft.add_argument("chapter", type=int)
    p_draft.add_argument("--max-iterations", type=int, default=3)
    p_draft.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p_draft.add_argument("--model", default=None)

    p_accept = sub.add_parser("accept", help="Promote the latest draft_v*.md to final.md.")
    p_accept.add_argument("project", type=Path)
    p_accept.add_argument("chapter", type=int)

    p_retry = sub.add_parser("retry", help="Continue iterating past previous max-iterations cap.")
    p_retry.add_argument("project", type=Path)
    p_retry.add_argument("chapter", type=int)
    p_retry.add_argument("--max-iterations", type=int, default=3)
    p_retry.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p_retry.add_argument("--model", default=None)

    p_audit = sub.add_parser(
        "audit",
        help="Run Bible Audit diagnostics to detect carrier-state lore drift across chapters (Layer 6).",
    )
    p_audit.add_argument("project", type=Path)
    p_audit.add_argument("--repair", action="store_true", help="Write repair proposals to structure/proposals/.")
    p_audit.add_argument("--accept", default=None, help="Resolve a proposal by ID (requires --option).")
    p_audit.add_argument("--option", default=None, help="Option ID to select when using --accept.")
    p_audit.add_argument(
        "--layers",
        default="all",
        help='Layer or layer range to audit. Examples: "6", "1-5", "all" (default).',
    )

    p_structure = sub.add_parser("structure", help="Run whole-story structure commands.")
    structure_sub = p_structure.add_subparsers(dest="structure_command", required=True)
    p_structure_diagnose = structure_sub.add_parser(
        "diagnose",
        help="Run deterministic whole-story structure diagnostics.",
    )
    p_structure_diagnose.add_argument("blueprint", type=Path)
    p_structure_diagnose.add_argument("--output", type=Path, default=None)
    p_structure_propose_repairs = structure_sub.add_parser(
        "propose-repairs",
        help="Run structure diagnostics and write repair proposal artifacts.",
    )
    p_structure_propose_repairs.add_argument("blueprint", type=Path)
    p_structure_apply = structure_sub.add_parser(
        "apply",
        help="Apply a selected structure proposal option to a blueprint.",
    )
    p_structure_apply.add_argument("proposal", type=Path)
    p_structure_apply.add_argument("blueprint", type=Path)
    p_structure_apply.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory for the new blueprint file (default: source blueprint directory).",
    )
    p_structure_apply.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the source blueprint file. Disabled by default.",
    )
    p_structure_generate = structure_sub.add_parser(
        "generate",
        help="Generate a story engine from target experience (top-down synthesis).",
    )
    p_structure_generate.add_argument(
        "blueprint",
        type=Path,
        help="Blueprint with target_experience but no story_engine.",
    )
    p_structure_generate.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for generated story_engine proposal.",
    )

    # Identity subcommands
    p_identity = sub.add_parser(
        "identity",
        help="Manage story identities.",
        formatter_class=_HideSuppressedFormatter,
    )
    identity_sub = p_identity.add_subparsers(dest="identity_command", required=True)
    p_identity_validate = identity_sub.add_parser(
        "validate",
        help="Validate a story_identity.yaml file.",
    )
    p_identity_validate.add_argument("identity", type=Path)
    p_identity_compile = identity_sub.add_parser(
        "compile",
        help="Compile a story_identity.yaml into a blueprint.yaml skeleton.",
    )
    p_identity_compile.add_argument("identity", type=Path)
    p_identity_compile.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Target output path for the compiled blueprint.yaml skeleton.",
    )
    p_identity_recommend = identity_sub.add_parser(
        "recommend",
        help="Recommend an opinionated story_identity.yaml from a raw premise.",
    )
    p_identity_recommend.add_argument("premise", type=str, help="Raw premise text or path to file containing it.")
    p_identity_recommend.add_argument("--genre", type=str, default=None, help="Constrain to a specific genre.")
    p_identity_recommend.add_argument("--medium", type=str, default=None, help="Constrain to a specific medium.")
    p_identity_recommend.add_argument("--mode", type=str, default=None, help="Constrain to a story mode (e.g. tragic, comic, noir, epic, intimate, absurdist).")
    p_identity_recommend.add_argument(
        "--output",
        type=Path,
        default=Path("story_identity.yaml"),
        help="Target output path for the recommended story_identity.yaml.",
    )
    p_identity_recommend.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p_identity_recommend.add_argument("--model", default=None)
    p_identity_recommend.add_argument(
        "--recommend-mode",
        choices=["opinionated", "open-ended"],
        default="opinionated",
        help=argparse.SUPPRESS,
    )
    p_identity_recommend.add_argument(
        "--candidates",
        type=int,
        default=3,
        help=argparse.SUPPRESS,
    )
    p_identity_recommend.add_argument(
        "--strict-candidate-count",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    p_identity_recommend.add_argument(
        "--debug",
        action="store_true",
        help="Export all failed candidate attempts to .auteur/runs/<timestamp>/.",
    )

    p_identity_accept_candidate = identity_sub.add_parser(
        "accept-candidate",
        help=argparse.SUPPRESS,
    )
    p_identity_accept_candidate.add_argument("candidate", type=Path, help=argparse.SUPPRESS)
    p_identity_accept_candidate.add_argument(
        "--output",
        type=Path,
        default=Path("story_identity.yaml"),
        help=argparse.SUPPRESS,
    )
    p_identity_accept_candidate.add_argument(
        "--keep-candidates",
        action="store_true",
        help=argparse.SUPPRESS,
    )


    # Blueprint subcommands
    p_blueprint = sub.add_parser("blueprint", help="Manage story blueprints.")
    blueprint_sub = p_blueprint.add_subparsers(dest="blueprint_command", required=True)
    p_blueprint_seed = blueprint_sub.add_parser(
        "seed",
        help="Seed a blueprint.yaml skeleton from a story_identity.yaml.",
    )
    p_blueprint_seed.add_argument("identity", type=Path)
    p_blueprint_seed.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Target output path for the compiled blueprint.yaml skeleton.",
    )

    # State subcommands
    p_state = sub.add_parser("state", help="Manage story state layers programmatically.")
    state_sub = p_state.add_subparsers(dest="state_command", required=True)

    p_state_check = state_sub.add_parser(
        "check",
        help=(
            "Run Structure Diagnostic (Layers 1-5, 9) and Bible Audit (Layer 6) "
            "in one pass. Optionally validate Scene Representation (Layer 7) "
            "against an outline.yaml with --outline."
        ),
    )
    p_state_check.add_argument("project", type=Path)
    p_state_check.add_argument(
        "--outline",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Path to outline.yaml for Layer 7 (Scene Representation) carrier "
            "validation. When omitted, a warning is emitted and Layer 7 is skipped."
        ),
    )

    p_state_update = state_sub.add_parser("update", help="Safe, transactional update of project files.")
    p_state_update.add_argument("project", type=Path)
    p_state_update.add_argument("file", type=Path)
    p_state_update.add_argument("--key", type=str, required=True, help="Dotted path target to update.")
    p_state_update.add_argument("--val", type=str, required=True, help="New value (parsed dynamically as JSON or string).")

    p_state_prepare = state_sub.add_parser("prepare", help="Compile handoff context packets using strict templates.")
    p_state_prepare.add_argument("project", type=Path)
    p_state_prepare.add_argument("phase", choices=["ideation", "drafting", "revision", "recovery"], help="Handoff phase target.")
    p_state_prepare.add_argument("--scope", choices=["engine", "chapter", "prose"], required=True, help="Target context scope.")
    p_state_prepare.add_argument("--out", type=Path, default=None, help="Output destination file path.")
    p_state_prepare.add_argument("--chapter", type=int, default=None, help="Specific chapter index context.")

    p_state_canon = state_sub.add_parser("canon", help="Generate high-fidelity summary facts report.")
    p_state_canon.add_argument("project", type=Path)
    p_state_canon.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")

    p_state_confirm = state_sub.add_parser("confirm", help="Validate and merge recovery locked layers into canonical state.")
    p_state_confirm.add_argument("project", type=Path)
    p_state_confirm.add_argument("recovery_run", type=Path, help="Path to the recovery_run.yaml payload.")

    # Cartographer subcommands
    p_cartographer = sub.add_parser("cartographer", help="Manage story outlines.")
    cartographer_sub = p_cartographer.add_subparsers(dest="cartographer_command", required=True)
    
    p_cart_compile = cartographer_sub.add_parser(
        "compile",
        help="Compile a blueprint into a unified cartographer outline.",
    )
    p_cart_compile.add_argument("blueprint", type=Path)
    p_cart_compile.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output destination path for the unified cartographer_outline.yaml file.",
    )
    p_cart_compile.add_argument(
        "--split",
        action="store_true",
        default=True,
        help="Auto-split compiled chapters into chapters/XX/outline.yaml.",
    )
    p_cart_compile.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p_cart_compile.add_argument("--model", default=None)

    p_cart_validate = cartographer_sub.add_parser(
        "validate",
        help="Deterministic, local validator for compiled cartographer outlines.",
    )
    p_cart_validate.add_argument("outline", type=Path)
    p_cart_validate.add_argument("--blueprint", type=Path, default=None, help="Blueprint to compare tension target against.")

    args = parser.parse_args(argv)

    if args.command == "init":
        return _cmd_init(args.path, args.blueprint_path, force=args.force)
    if args.command == "plan":
        return _cmd_plan(args.blueprint, args.chapter)
    if args.command == "draft":
        return _cmd_draft(args.project, args.chapter, args.max_iterations, args.provider, args.model)
    if args.command == "accept":
        return _cmd_accept(args.project, args.chapter)
    if args.command == "retry":
        return _cmd_retry(args.project, args.chapter, args.max_iterations, args.provider, args.model)
    if args.command == "audit":
        return _cmd_audit(args.project, repair=args.repair, accept=args.accept, option=args.option, layers=args.layers)
    if args.command == "structure" and args.structure_command == "diagnose":
        return _cmd_structure_diagnose(args.blueprint, args.output)
    if args.command == "structure" and args.structure_command == "propose-repairs":
        return _cmd_structure_propose_repairs(args.blueprint)
    if args.command == "structure" and args.structure_command == "apply":
        return _cmd_structure_apply(args.proposal, args.blueprint, args.output, args.in_place)
    if args.command == "structure" and args.structure_command == "generate":
        return _cmd_structure_generate(args.blueprint, args.output)
    if args.command == "identity" and args.identity_command == "validate":
        return _cmd_identity_validate(args.identity)
    if args.command == "identity" and args.identity_command == "compile":
        return _cmd_identity_compile(args.identity, args.output)
    if args.command == "identity" and args.identity_command == "recommend":
        rec_mode = args.recommend_mode
        story_mode = args.mode
        if args.mode in ("open-ended", "open_ended"):
            print("Warning: --mode open-ended is deprecated. Use --recommend-mode open-ended instead.", file=sys.stderr)
            rec_mode = "open_ended"
            story_mode = None
        if rec_mode == "open-ended":
            rec_mode = "open_ended"
        return _cmd_identity_recommend(
            premise=args.premise,
            genre=args.genre,
            medium=args.medium,
            mode=story_mode,
            output_path=args.output,
            provider=args.provider,
            model=args.model,
            recommend_mode=rec_mode,
            candidates_count=args.candidates,
            strict_candidate_count=args.strict_candidate_count,
            debug=args.debug,
        )
    if args.command == "identity" and args.identity_command == "accept-candidate":
        return _cmd_identity_accept_candidate(
            candidate_path=args.candidate,
            output_path=args.output,
            keep_candidates=args.keep_candidates,
        )

    if args.command == "blueprint" and args.blueprint_command == "seed":
        return _cmd_blueprint_seed(args.identity, args.output)
    if args.command == "state":
        from auteur.structure.state import (
            state_check,
            state_update,
            state_prepare,
            state_canon,
            state_confirm,
        )
        if args.state_command == "check":
            outline_path: Path | None = getattr(args, "outline", None)
            if outline_path is not None:
                if not outline_path.exists():
                    import sys as _sys
                    print(f"Error: Outline file not found: {outline_path}", file=_sys.stderr)
                    return 1
                from auteur.structure.outline_audit import load_outline
                try:
                    outline = load_outline(str(outline_path))
                except ValueError as exc:
                    import sys as _sys
                    print(f"Error: {exc}", file=_sys.stderr)
                    return 1
                return state_check(args.project, outline=outline)
            return state_check(args.project)
        if args.state_command == "update":
            return state_update(args.project, args.file, args.key, args.val)
        if args.state_command == "prepare":
            return state_prepare(args.project, args.phase, args.scope, args.out, args.chapter)
        if args.state_command == "canon":
            return state_canon(args.project, args.format)
        if args.state_command == "confirm":
            return state_confirm(args.project, args.recovery_run)
    if args.command == "cartographer":
        if args.cartographer_command == "compile":
            return _cmd_cartographer_compile(
                blueprint_path=args.blueprint,
                output_path=args.output,
                split=args.split,
                provider=args.provider,
                model=args.model
            )
        if args.cartographer_command == "validate":
            return _cmd_cartographer_validate(
                outline_path=args.outline,
                blueprint_path=args.blueprint
            )
    parser.print_help()
    return 2


def _cmd_init(path: Path, blueprint_path: Path, *, force: bool = False) -> int:
    # --- Safe overwrite with --force ---
    if path.exists() and not force:
        print(f"Error: project path already exists: {path}", file=sys.stderr)
        return 1

    if force and path.exists():
        # Strict project detection: only allow re-init if directory looks like
        # an auteur project (both blueprint.yaml and bible.json exist).
        if not (path / "blueprint.yaml").is_file() or not (path / "bible.json").is_file():
            print(
                "Error: --force requires an existing auteur project"
                " directory (blueprint.yaml + bible.json).",
                file=sys.stderr,
            )
            return 1
        import shutil
        shutil.rmtree(str(path))

    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1

    # --- Pre-init validation ---
    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
    except Exception as exc:
        msg = str(exc)
        print(f"Error: invalid blueprint — {msg}", file=sys.stderr)
        return 1

    Project.init(path, blueprint)
    print(f"Initialized project at {path}")
    return 0


def _cmd_plan(blueprint_path: Path, chapter_index: int) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint file not found: {blueprint_path}", file=sys.stderr)
        return 1
    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    result = PipelineRunner(blueprint).plan_chapter(chapter_index)
    print("--- SYSTEM PROMPT ---\n")
    print(result.system_prompt)
    print("\n--- USER MESSAGE ---\n")
    print(result.user_message)
    return 0


def _cmd_structure_diagnose(blueprint_path: Path, output_path: Path | None = None) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1
    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
    except (ValueError, yaml.YAMLError) as exc:
        print(f"Error: invalid blueprint {blueprint_path}: {exc}", file=sys.stderr)
        return 1
    diagnostics = analyze_structure(blueprint)
    report = {"diagnostics": [diagnostic.model_dump(mode="json") for diagnostic in diagnostics]}
    report_json = json.dumps(report, indent=2)
    if output_path is not None:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(f"{report_json}\n", encoding="utf-8")
        except OSError as exc:
            print(f"Error: failed to write report to {output_path}: {exc}", file=sys.stderr)
            return 1
    print(report_json)
    if any(diagnostic.severity == DiagnosticSeverity.ERROR for diagnostic in diagnostics):
        return 4
    return 0


def _cmd_structure_propose_repairs(blueprint_path: Path) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1
    try:
        blueprint, diagnostics_dir, proposals_dir = _load_blueprint_and_structure_dirs(
            blueprint_path
        )
    except (ValueError, yaml.YAMLError, OSError) as exc:
        print(f"Error: invalid blueprint {blueprint_path}: {exc}", file=sys.stderr)
        return 1

    diagnostics = analyze_structure(blueprint)
    report = {"diagnostics": [diagnostic.model_dump(mode="json") for diagnostic in diagnostics]}
    proposals = propose_repairs_from_diagnostics(diagnostics)

    try:
        report_path = diagnostics_dir / "structure_report.json"
        report_path.write_text(
            f"{json.dumps(report, indent=2, ensure_ascii=False)}\n",
            encoding="utf-8",
        )

        proposal_paths = []
        for proposal in proposals:
            proposal_path = proposals_dir / f"{proposal.proposal_id}.yaml"
            proposal_path.write_text(
                yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
                encoding="utf-8",
            )
            proposal_paths.append(proposal_path)
    except OSError as exc:
        print(f"Error: failed to write structure artifacts: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "diagnostic_count": len(diagnostics),
                "proposal_count": len(proposals),
                "report_path": str(report_path),
                "proposal_paths": [str(path) for path in proposal_paths],
            },
            indent=2,
        )
    )
    return 0


def _cmd_structure_apply(
    proposal_path: Path,
    blueprint_path: Path,
    output_path: Path | None,
    in_place: bool,
) -> int:
    if not proposal_path.exists():
        print(f"Error: proposal not found: {proposal_path}", file=sys.stderr)
        return 1
    if not blueprint_path.exists():
        print(f"Error: blueprint not found: {blueprint_path}", file=sys.stderr)
        return 1
    if in_place and output_path is not None:
        print("Error: --output cannot be used with --in-place", file=sys.stderr)
        return 1

    try:
        proposal_payload = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
        proposal = StructureProposal.model_validate(proposal_payload)
    except (ValueError, yaml.YAMLError, OSError) as exc:
        print(f"Error: invalid proposal {proposal_path}: {exc}", file=sys.stderr)
        return 1

    if proposal.source_domain == "bible_audit":
        print(
            (
                "Error: bible_audit proposals cannot be applied to blueprints. "
                "Resolve them with `auteur audit --accept ... --option ...`."
            ),
            file=sys.stderr,
        )
        return 1

    try:
        blueprint, _, _ = _load_blueprint_and_structure_dirs(blueprint_path)
    except (ValueError, yaml.YAMLError, OSError) as exc:
        print(f"Error: invalid blueprint {blueprint_path}: {exc}", file=sys.stderr)
        return 1

    if (
        not proposal.selection.selected_option_id
        and proposal.decision is not None
        and proposal.decision.status == "accepted"
    ):
        proposal.selection.selected_option_id = proposal.decision.selected_option_id
        if not proposal.selection.custom_data and proposal.decision.custom_data:
            proposal.selection.custom_data = proposal.decision.custom_data

    if not proposal.selection.selected_option_id:
        print(
            "Error: proposal must include an accepted or selected option before apply",
            file=sys.stderr,
        )
        return 1

    option_ids = {option.id for option in proposal.options}
    if proposal.selection.selected_option_id not in option_ids:
        print(
            (
                "Error: selected_option_id "
                f"{proposal.selection.selected_option_id!r} not found in proposal options"
            ),
            file=sys.stderr,
        )
        return 1

    source_blueprint_path = _resolve_blueprint_file_path(blueprint_path)

    try:
        _, target_path = apply_proposal_to_blueprint(
            proposal,
            blueprint,
            output_dir=str(output_path or source_blueprint_path.parent) if not in_place else None,
            original_path=str(source_blueprint_path) if in_place else None,
            in_place=in_place,
        )
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(f"Error: failed to apply proposal {proposal_path}: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "proposal_path": str(proposal_path),
                "source_blueprint_path": str(source_blueprint_path),
                "target_path": str(target_path),
                "in_place": in_place,
                "selected_option_id": proposal.selection.selected_option_id,
            },
            indent=2,
        )
    )
    return 0


def _cmd_structure_generate(blueprint_path: Path, output_path: Path | None = None) -> int:
    """
    Generate a story engine from target experience (top-down structure synthesis).
    """
    from auteur.structure.generator import generate_story_engine
    from auteur.structure.diagnostics import DiagnosticSeverity

    if not blueprint_path.exists():
        print(f"Error: blueprint file not found: {blueprint_path}", file=sys.stderr)
        return 1

    try:
        blueprint = StoryBlueprint.from_yaml(blueprint_path)
    except Exception as e:
        print(f"Error: failed to parse blueprint {blueprint_path}: {e}", file=sys.stderr)
        return 1

    # Generate story engine
    result = generate_story_engine(blueprint)

    # Handle diagnostics (errors)
    if isinstance(result, list):
        # result is a list of diagnostics
        errors = [d for d in result if d.severity == DiagnosticSeverity.ERROR]
        warnings = [d for d in result if d.severity == DiagnosticSeverity.WARNING]

        for diag in errors:
            print(f"ERROR: {diag.message}", file=sys.stderr)
            if diag.evidence:
                for ev in diag.evidence:
                    print(f"  - {ev}", file=sys.stderr)

        for diag in warnings:
            print(f"WARNING: {diag.message}", file=sys.stderr)

        if errors:
            return 1
        return 0

    # result is a GenerationProposal
    proposal = result

    # Output the proposal
    import json
    proposal_dict = proposal.model_dump(mode="json")

    output = json.dumps(proposal_dict, indent=2)
    print(output)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output + "\n", encoding="utf-8")
        print(f"\nProposal written to {output_path}", file=sys.stderr)

    return 0


def _load_blueprint_and_structure_dirs(
    blueprint_path: Path,
) -> tuple[StoryBlueprint, Path, Path]:
    if blueprint_path.is_dir():
        project = Project.load(blueprint_path)
        return (
            project.blueprint,
            project.structure_diagnostics_dir(),
            project.structure_proposals_dir(),
        )

    if blueprint_path.name == "blueprint.yaml" and (blueprint_path.parent / "bible.json").exists():
        project = Project.load(blueprint_path.parent)
        return (
            project.blueprint,
            project.structure_diagnostics_dir(),
            project.structure_proposals_dir(),
        )

    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    diagnostics_dir = blueprint_path.parent / "structure" / "diagnostics"
    proposals_dir = blueprint_path.parent / "structure" / "proposals"
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    proposals_dir.mkdir(parents=True, exist_ok=True)
    return blueprint, diagnostics_dir, proposals_dir


def _resolve_blueprint_file_path(blueprint_path: Path) -> Path:
    if blueprint_path.is_dir():
        return blueprint_path / "blueprint.yaml"
    return blueprint_path


def _cmd_draft(
    project_path: Path,
    chapter_index: int,
    max_iterations: int,
    provider: str,
    model: str | None,
) -> int:
    project = Project.load(project_path)
    from auteur.llm.factory import build_client
    client = build_client(provider, model, agent_type="bard", blueprint=project.blueprint)
    runner = PipelineRunner(project.blueprint, bible=project.bible)

    def _progress(i: int, report: Any) -> None:
        if report.passed:
            status = "PASSED"
        else:
            errors = sum(1 for f in report.findings if f.severity == "error")
            status = f"FAILED ({errors} errors)"
        print(f"  iteration {i}: {status}")

    result = runner.draft_chapter(
        chapter_index,
        llm=client,
        project=project,
        max_iterations=max_iterations,
        on_iteration=_progress,
    )

    if result.conflict_report is not None:
        print(f"CONFLICT: {result.conflict_report}", file=sys.stderr)
        print(f"  See {project.chapter_dir(chapter_index) / 'outline.yaml'} for details.", file=sys.stderr)
        return 3
    if result.accepted:
        print(f"ACCEPTED on iteration {result.iterations}.")
        print(f"  final.md: {result.final_path}")
        print(f"  tokens: {result.total_input_tokens} in / {result.total_output_tokens} out")
        return 0
    print(f"NOT ACCEPTED after {result.iterations} iterations.", file=sys.stderr)
    print(f"  Latest draft and validation kept on disk.", file=sys.stderr)
    if result.critic_proposal_paths:
        print(f"  Critic repair proposals written to structure/proposals/.", file=sys.stderr)
        print(f"  Review with: auteur audit --show", file=sys.stderr)
    print(f"  Edit manually then: auteur accept {project_path} {chapter_index}", file=sys.stderr)
    print(f"  Or:                  auteur retry {project_path} {chapter_index}", file=sys.stderr)
    return 2


def _cmd_accept(project_path: Path, chapter_index: int) -> int:
    project = Project.load(project_path)
    chapter_dir = project.chapter_dir(chapter_index)
    drafts = _sorted_drafts(chapter_dir)
    if not drafts:
        print(f"No drafts found in {chapter_dir}", file=sys.stderr)
        return 1
    latest = drafts[-1]
    project.write_final(chapter_index, latest.read_text(encoding="utf-8"))

    outline_path = chapter_dir / "outline.yaml"
    summary = ""
    tension: int | None = None
    if outline_path.exists():
        outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
        summary = outline.get("chapter_summary", "")
        t = outline.get("estimated_chapter_tension")
        if isinstance(t, int):
            tension = t

    project.bible.record_event(chapter_index=chapter_index, summary=summary, deltas={"manually_accepted": True})
    if tension is not None:
        project.bible.record_tension(chapter_index, tension)
    project.bible.save()
    print(f"Accepted {latest.name} as final.md for chapter {chapter_index}.")
    return 0


def _cmd_audit(project_path: Path, *, repair: bool = False, accept: str | None = None, option: str | None = None, layers: str = "all") -> int:
    """Run Bible audit diagnostics on a project and print results.
    When `repair` is True, also write proposal artifacts.  When `accept` is set, resolve the named proposal."""
    from auteur.blueprint import StoryBlueprint

    blueprint_path = project_path / "blueprint.yaml"
    if not blueprint_path.exists():
        print(f"No blueprint.yaml found in {project_path}", file=sys.stderr)
        return 1

    bible_path = project_path / "bible.json"
    if not bible_path.exists():
        print(f"No bible.json found in {project_path}", file=sys.stderr)
        return 1

    # --- Handle --accept (proposal resolution) ---
    if accept is not None:
        if option is None:
            print("--accept requires --option.", file=sys.stderr)
            return 1
        return resolve_proposal(project_path, accept, option)

    from auteur.bible import StoryBible
    from auteur.structure.analyzer import run_all_diagnostics
    from auteur.structure.diagnostics import StructureDiagnostic
    from auteur.structure.proposal_resolution import load_resolved_rules, write_audit_repair_proposals

    blueprint = StoryBlueprint.from_yaml(blueprint_path)
    bible = StoryBible(bible_path)

    # --- Load resolved proposals to filter output ---
    resolved_rules: set[str] = load_resolved_rules(project_path)

    raw_diagnostics = run_all_diagnostics(blueprint, bible)
    diagnostics = [d for d in raw_diagnostics if d.rule not in resolved_rules]

    if not raw_diagnostics:
        print("No structural or lore issues detected.")
        return 0

    if not diagnostics:
        print("All previously detected issues have been resolved.")
        return 0

    from auteur.structure.diagnostics import DiagnosticLayer

    if layers != "all":
        selected = _parse_layers(layers)
        diagnostics = [d for d in diagnostics if d.layer in selected]

    # Group diagnostics by layer
    if diagnostics:
        _print_grouped_report(diagnostics)
    else:
        print("No unresolved issues found in selected layers.")

    if repair and diagnostics:
        write_audit_repair_proposals(project_path, diagnostics)

    errors = sum(1 for d in diagnostics if d.severity.value == "error")
    warnings = sum(1 for d in diagnostics if d.severity.value == "warning")
    print(f"Found {errors} unresolved error(s), {warnings} unresolved warning(s).")
    # Count resolved proposals for footer
    proposals_dir = project_path / "structure" / "proposals"
    resolved_count = 0
    if proposals_dir.is_dir():
        for pf in sorted(proposals_dir.glob("*.yaml")):
            try:
                pd = yaml.safe_load(pf.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(pd, dict):
                sel = pd.get("selection", {})
                if isinstance(sel, dict) and sel.get("selected_option_id"):
                    resolved_count += 1
    if resolved_count:
        label = "proposal" if resolved_count == 1 else "proposals"
        print(f"{resolved_count} previously resolved {label} were skipped.")
    return 1 if errors > 0 else 0


def _print_diagnostic(d: StructureDiagnostic) -> None:
    """Print a single diagnostic with evidence and repair options."""
    severity_label = d.severity.value.upper()
    print(f"[{severity_label}] {d.rule}: {d.message}")
    if d.evidence:
        print("  Evidence:")
        for line in d.evidence:
            print(f"    - {line}")
    if d.repair_options.preserve_intent:
        print("  Preserve intent:")
        for opt in d.repair_options.preserve_intent:
            print(f"    - {opt}")
    if d.repair_options.challenge_intent:
        print("  Challenge intent:")
        for opt in d.repair_options.challenge_intent:
            print(f"    - {opt}")
    print()


def _cmd_retry(
    project_path: Path,
    chapter_index: int,
    max_iterations: int,
    provider: str,
    model: str | None,
) -> int:
    project = Project.load(project_path)
    chapter_dir = project.chapter_dir(chapter_index)

    outline_path = chapter_dir / "outline.yaml"
    if not outline_path.exists():
        print(f"No outline found in {chapter_dir}; run auteur draft first.", file=sys.stderr)
        return 1
    outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
    if not isinstance(outline, dict):
        print(f"Invalid outline file: {outline_path}", file=sys.stderr)
        return 1

    drafts = _sorted_drafts(chapter_dir)
    if not drafts:
        print(f"No drafts found in {chapter_dir}; run auteur draft first.", file=sys.stderr)
        return 1
    latest = drafts[-1]
    latest_version = _draft_version(latest)

    validation_path = chapter_dir / f"validation_v{latest_version}.json"
    if not validation_path.exists():
        print(f"No validation found for {latest.name}: {validation_path}", file=sys.stderr)
        return 1
    try:
        previous_report = ValidationReport.model_validate(
            json.loads(validation_path.read_text(encoding="utf-8"))
        )
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"Invalid validation file {validation_path}: {exc}", file=sys.stderr)
        return 1

    from auteur.llm.factory import build_client
    client = build_client(provider, model, agent_type="bard", blueprint=project.blueprint)
    runner = PipelineRunner(project.blueprint, bible=project.bible)

    def _progress(i: int, report: Any) -> None:
        if report.passed:
            status = "PASSED"
        else:
            errors = sum(1 for f in report.findings if f.severity == "error")
            status = f"FAILED ({errors} errors)"
        print(f"  iteration {i}: {status}")

    result = runner.draft_chapter(
        chapter_index,
        llm=client,
        project=project,
        max_iterations=max_iterations,
        on_iteration=_progress,
        initial_outline=outline,
        start_iteration=latest_version + 1,
        prior_draft=latest.read_text(encoding="utf-8"),
        prior_findings=previous_report.findings,
    )

    if result.conflict_report is not None:
        print(f"CONFLICT: {result.conflict_report}", file=sys.stderr)
        print(f"  See {outline_path} for details.", file=sys.stderr)
        return 3
    if result.accepted:
        print(f"ACCEPTED on iteration {result.iterations}.")
        print(f"  final.md: {result.final_path}")
        print(f"  tokens: {result.total_input_tokens} in / {result.total_output_tokens} out")
        return 0
    print(f"NOT ACCEPTED after iteration {result.iterations}.", file=sys.stderr)
    print(f"  Latest draft and validation kept on disk.", file=sys.stderr)
    print(f"  Edit manually then: auteur accept {project_path} {chapter_index}", file=sys.stderr)
    print(f"  Or:                  auteur retry {project_path} {chapter_index}", file=sys.stderr)
    return 2


def _draft_version(path: Path) -> int:
    return int(path.stem.removeprefix("draft_v"))


def _sorted_drafts(chapter_dir: Path) -> list[Path]:
    return sorted(chapter_dir.glob("draft_v*.md"), key=_draft_version)




def _print_grouped_report(diagnostics: list[StructureDiagnostic]) -> None:
    """Print diagnostics grouped by layer with headers."""
    from collections import defaultdict
    _LAYER_ORDER: list[tuple[int, DiagnosticLayer, str]] = [
        (5, DiagnosticLayer.STRUCTURAL_FORCES, "Structural Forces"),
        (6, DiagnosticLayer.CARRIERS, "Carriers"),
    ]
    groups: dict[DiagnosticLayer, list[StructureDiagnostic]] = defaultdict(list)
    for d in diagnostics:
        groups[d.layer].append(d)

    for num, layer, name in _LAYER_ORDER:
        items = groups.get(layer)
        if not items:
            continue
        label = "finding" if len(items) == 1 else "findings"
        print(f"Layer {num} \u2014 {name} ({len(items)} {label})")
        for d in items:
            _print_diagnostic(d)
        print()


def _parse_layers(spec: str) -> set[DiagnosticLayer]:
    """Parse a --layers flag value into a set of DiagnosticLayer enums."""
    from auteur.structure.diagnostics import DiagnosticLayer

    spec = spec.strip()
    if spec == "all":
        return set(DiagnosticLayer)

    parts = spec.split("-")
    if len(parts) == 2:
        try:
            start, end = int(parts[0]), int(parts[1])
            layer_map = {
                1: DiagnosticLayer.TARGET_EXPERIENCE,
                2: DiagnosticLayer.CONSTRAINTS,
                3: DiagnosticLayer.SCOPE,
                4: DiagnosticLayer.STRUCTURAL_FORCES,
                5: DiagnosticLayer.THREADS,
                6: DiagnosticLayer.CARRIERS,
                7: DiagnosticLayer.REPRESENTATION,
                8: DiagnosticLayer.MODULATION,
                9: DiagnosticLayer.THEME,
            }
            return {v for k, v in layer_map.items() if start <= k <= end}
        except (ValueError, KeyError):
            return set(DiagnosticLayer)
    try:
        n = int(spec)
        layer_map = {
            1: DiagnosticLayer.TARGET_EXPERIENCE,
            2: DiagnosticLayer.CONSTRAINTS,
            3: DiagnosticLayer.SCOPE,
            4: DiagnosticLayer.STRUCTURAL_FORCES,
            5: DiagnosticLayer.THREADS,
            6: DiagnosticLayer.CARRIERS,
            7: DiagnosticLayer.REPRESENTATION,
            8: DiagnosticLayer.MODULATION,
            9: DiagnosticLayer.THEME,
        }
        return {layer_map[n]}
    except (ValueError, KeyError):
        return set(DiagnosticLayer)


def _cmd_identity_validate(identity_path: Path) -> int:
    if not identity_path.exists():
        print(f"Error: identity file not found: {identity_path}", file=sys.stderr)
        return 1
    try:
        from auteur.identity import StoryIdentity
        identity = StoryIdentity.from_yaml(identity_path)
        diagnostics = identity.validate_identity()
        if diagnostics:
            has_error = False
            for diag in diagnostics:
                severity_str = diag.severity.value.upper() if hasattr(diag.severity, "value") else str(diag.severity).upper()
                if severity_str == "ERROR":
                    has_error = True
                print(f"[{severity_str}] Layer: {diag.layer.value if hasattr(diag.layer, 'value') else diag.layer} | Rule: {diag.rule}", file=sys.stderr)
                print(f"  Message: {diag.message}", file=sys.stderr)
                if diag.evidence:
                    print(f"  Evidence: {diag.evidence}", file=sys.stderr)
                if diag.repair_options:
                    if diag.repair_options.preserve_intent:
                        print(f"  Preserve Intent options: {diag.repair_options.preserve_intent}", file=sys.stderr)
                    if diag.repair_options.challenge_intent:
                        print(f"  Challenge Intent options: {diag.repair_options.challenge_intent}", file=sys.stderr)
                print("", file=sys.stderr)
            
            if has_error:
                print(f"Error: StoryIdentity {identity_path} failed structural validation.", file=sys.stderr)
                return 1
            else:
                print(f"Success: StoryIdentity {identity_path} is valid (with warnings).")
                return 0
        else:
            print(f"Success: StoryIdentity {identity_path} is valid.")
            return 0
    except Exception as exc:
        print(f"Error: invalid story identity {identity_path}: {exc}", file=sys.stderr)
        return 1


def _cmd_identity_recommend(
    premise: str,
    genre: str | None,
    medium: str | None,
    mode: str | None,
    output_path: Path,
    provider: str,
    model: str | None,
    recommend_mode: str = "opinionated",
    candidates_count: int = 3,
    strict_candidate_count: bool = False,
    debug: bool = False,
) -> int:
    import re
    import hashlib
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    from auteur.llm.factory import build_client
    from auteur.llm import LLMRequest
    from auteur.identity import StoryIdentity, StoryIdentityCandidate, StoryIdentityRecommendationSet, BestBasis, RecommendationMode
    from auteur.blueprint import Genre, StoryMedium, StoryMode
    from auteur.genres.registry import load_genre_contract
    from auteur.genres.subgenres import load_subgenre_modifier

    # 1. Resolve premise text
    premise_text = premise
    try:
        premise_path = Path(premise)
        if premise_path.exists() and premise_path.is_file():
            premise_text = premise_path.read_text(encoding="utf-8")
    except Exception:
        pass

    def _extract_yaml_block(text: str) -> str:
        match = re.search(r"```(?:yaml|json)?\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        match = re.search(r"```\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()


    # 2. Load primary genre contract if constrained
    genre_guidance = ""
    if genre:
        try:
            resolved_genre = Genre(genre.lower().strip())
            contract = load_genre_contract(resolved_genre)
            if contract:
                genre_guidance = f"""
Primary Genre Contract Details ({contract.display_name}):
- Audience Product: {contract.audience_product}
- Core Truth: {contract.core_truth}
- Required Tropes: {", ".join(contract.required_tropes)}
- Forbidden Mismatches: {", ".join(contract.forbidden_mismatches)}
"""
        except Exception:
            pass

    genres_list = [g.value for g in Genre]
    mediums_list = [m.value for m in StoryMedium]
    modes_list = [o.value for o in StoryMode]

    # Helper to generate a single candidate
    def _generate_candidate(basis: BestBasis, index: int, attempt_limit: int = 4) -> tuple[StoryIdentity | None, list[str]]:
        basis_guideline = ""
        if basis == BestBasis.GENRE_ALIGNED:
            basis_guideline = "Optimize for the primary genre contract promise, core truth, required tropes, and audience expectations."
        elif basis == BestBasis.STRUCTURALLY_COHERENT:
            basis_guideline = "Optimize for tight conflict escalation, causal plot momentum, want/change transformational alignment, and subplot discipline."
        elif basis == BestBasis.FAITHFUL_TO_INPUT:
            basis_guideline = "Optimize for preserving the literal details, quirky eccentricities, and specific tone of the author's original premise without over-commercializing or genericizing it."
        elif basis == BestBasis.EMOTIONALLY_POWERFUL:
            basis_guideline = "Maximize emotional stakes, cathartic affect, target emotional trajectories, and character psychological depth within the genre's psychology budget."

        system_prompt = f"""You are an expert, opinionated narrative compiler. Your job is to take a raw creative premise/idea and translate it into a single, cohesive, structurally sound recommended story identity.

You must recommend exactly one direction (choose the best-suited genre, medium, and mode) for this story to maximize its narrative potential. Do not be vague or generic.

Optimization Lens (best_basis: '{basis.value}'):
{basis_guideline}

The available genres, mediums, and modes are:
Genres:
{", ".join(genres_list)}

Mediums:
{", ".join(mediums_list)}

Modes:
{", ".join(modes_list)}

{genre_guidance}

Note on Genre Runway constraints:
Each genre has a minimum viable length requirement. For instance, epic fantasy, mystery, or thrillers typically require a longer medium (e.g. novel, novella) rather than a short story. If you specify a genre, ensure the medium matches or exceeds its runway requirements, unless you specify runway_compression in author_overrides.

Here are the rules for a valid StoryIdentity:
1. The 'change' field in central_engine must describe a genuine transformation (how the protagonist/world changes after the conflict) and MUST NOT duplicate or merely restate the 'want' field.
2. The chosen mode must be compatible with the genre's ending tone restrictions. For example, Romance forbids tragic endings.
3. The 'target_experience.avoid' list must NOT contain the primary emotional experience or any progression steps.

Your response must contain ONLY a single YAML code block defining the recommended story identity matching the following schema structure:

```yaml
title: "Title of the Story"
core_answer: "One sentence summarizing the premise, main thread conflict, and resolution."
target_experience:
  primary: "the primary emotion/experience to evoke"
  progression: "emotion1 -> emotion2 -> emotion3"
  avoid:
    - "avoided emotion1"
story_type:
  medium: "medium_value"
  mode: "mode_value"
  genre: "genre_value"
  subgenres:
    - "subgenre1"  # e.g., for mystery: locked_room, hardboiled, cozy
  target_audience: "adult"
  length_class: null
central_engine:
  want: "What the protagonist desperately wants."
  resistance: "The chief force resisting that want."
  conflict: "The clash between want and resistance."
  stakes: "What is lost if they fail."
  change: "How they/the world are transformed after the conflict."
not_this:
  - "what this story should not be"
open_questions:
  - "open questions to resolve"
confidence: 0.95
alternatives:
  - "alternative direction 1"
recommendation_mode: "{recommend_mode}"
best_basis: "{basis.value}"
why_this_is_best: "Explanation of why this specific setup is best optimized for this lens."
rejected_directions:
  - "rejected direction 1"
author_overrides: []
```

Make sure the output is valid YAML, contains no conversational preamble/postamble, and strictly adheres to the schema.
"""

        constraints_text = []
        if genre:
            constraints_text.append(f"Constraint: You MUST set story_type.genre to '{genre}'.")
        if medium:
            constraints_text.append(f"Constraint: You MUST set story_type.medium to '{medium}'.")
        if mode:
            constraints_text.append(f"Constraint: You MUST set story_type.mode to '{mode}'.")

        constraints_str = "\n".join(constraints_text)
        user_prompt = f"Raw Premise:\n{premise_text}\n\n{constraints_str}\n\nPlease generate the story identity recommendation YAML block."

        client = build_client(provider, model)
        last_output = ""
        validation_feedback = ""

        for attempt in range(1, attempt_limit + 1):
            try:
                if attempt == 1:
                    req_user = user_prompt
                else:
                    req_user = (
                        user_prompt
                        + f"\n\n--- PREVIOUS ATTEMPT OUTPUT ---\n{last_output}\n\n"
                        + f"--- VALIDATION ERRORS ---\n{validation_feedback}\n\n"
                        + "Please correct the errors and output ONLY the corrected YAML block. "
                        + "You MUST NOT add items to 'author_overrides' to bypass these validation errors. "
                        + "Resolve them by correcting the actual content fields."
                    )

                req = LLMRequest(
                    system=system_prompt,
                    user=req_user,
                    max_tokens=4096,
                    temperature=0.7,
                    model=model,
                )

                response = client.complete(req)
                last_output = response.text

                yaml_text = _extract_yaml_block(last_output)
                data = yaml.safe_load(yaml_text)
                if not isinstance(data, dict):
                    raise ValueError("LLM output is not a dictionary.")

                if "story_type" not in data or not isinstance(data["story_type"], dict):
                    data["story_type"] = {}
                if genre:
                    data["story_type"]["genre"] = genre
                if medium:
                    data["story_type"]["medium"] = medium
                if mode:
                    data["story_type"]["mode"] = mode

                identity = StoryIdentity.model_validate(data)

                # Refuse auto-overrides: LLM cannot inject overrides
                auto_overrides_detected = False
                if identity.author_overrides:
                    auto_overrides_detected = True
                    from auteur.structure.diagnostics import StructureDiagnostic, DiagnosticSeverity, DiagnosticLayer, RepairOptions
                    auto_override_diag = StructureDiagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        layer=DiagnosticLayer.CONSTRAINTS,
                        rule="identity.auto_overrides_forbidden",
                        message="Generating auto-overrides is forbidden. Do not add overrides to 'author_overrides'. Resolve the underlying issue by changing the story elements.",
                        evidence=[f"author_overrides = {identity.author_overrides}"],
                        repair_options=RepairOptions(
                            preserve_intent=["Clear the author_overrides list and fix the underlying validation errors instead."],
                            challenge_intent=[]
                        )
                    )
                    identity.author_overrides = []

                diagnostics = identity.validate_identity()
                if auto_overrides_detected:
                    diagnostics.append(auto_override_diag)

                errors = [
                    d for d in diagnostics
                    if (d.severity.value.lower() == "error" if hasattr(d.severity, "value") else str(d.severity).lower() == "error")
                ]

                if not errors:
                    # Apply warning confidence penalty
                    warnings = [
                        d for d in diagnostics
                        if (d.severity.value.lower() == "warning" if hasattr(d.severity, "value") else str(d.severity).lower() == "warning")
                    ]
                    if warnings:
                        # Lower confidence score by 0.05 per warning, cap at 0.10
                        original_confidence = identity.confidence or 1.0
                        identity.confidence = max(0.10, round(original_confidence - 0.05 * len(warnings), 2))
                    # Valid candidate found
                    return identity, [str(d.message) for d in diagnostics]
                else:
                    err_lines = []
                    for err in errors:
                        err_lines.append(f"- Rule: {err.rule} | Message: {err.message}")
                    validation_feedback = "\n".join(err_lines)
                    print(f"Validation failed on attempt {attempt} for basis {basis.value}:\n{validation_feedback}", file=sys.stderr)
                    if debug:
                        debug_dir = Path(".auteur/runs") / timestamp
                        debug_dir.mkdir(parents=True, exist_ok=True)
                        attempt_file = debug_dir / f"candidate_{index}_{basis.value}_attempt_{attempt}.txt"
                        log_content = [
                            f"Basis: {basis.value}",
                            f"Attempt: {attempt}",
                            f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
                            "\n--- LLM RAW OUTPUT ---",
                            last_output,
                            "\n--- VALIDATION ERRORS ---",
                            validation_feedback
                        ]
                        attempt_file.write_text("\n".join(log_content), encoding="utf-8")

            except Exception as exc:
                validation_feedback = f"Error during parsing/validation: {exc}"
                print(f"Parsing/Validation failed on attempt {attempt} for basis {basis.value}: {exc}", file=sys.stderr)
                if debug:
                    debug_dir = Path(".auteur/runs") / timestamp
                    debug_dir.mkdir(parents=True, exist_ok=True)
                    attempt_file = debug_dir / f"candidate_{index}_{basis.value}_attempt_{attempt}.txt"
                    log_content = [
                        f"Basis: {basis.value}",
                        f"Attempt: {attempt}",
                        f"Timestamp: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
                        "\n--- LLM RAW OUTPUT ---",
                        last_output,
                        "\n--- EXCEPTION ---",
                        validation_feedback
                    ]
                    attempt_file.write_text("\n".join(log_content), encoding="utf-8")

        return None, []

    # 3. Handle Opinionated Mode (Default)
    if recommend_mode == "opinionated":
        identity, warnings = _generate_candidate(BestBasis.GENRE_ALIGNED, 1)
        if identity:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            identity.to_yaml(output_path)
            print(f"Success: saved recommended story identity to {output_path}")
            if warnings:
                print("Warnings encountered during generation:")
                for w in warnings:
                    print(f" - {w}")
            return 0
        else:
            print("Error: failed to generate a valid StoryIdentity after maximum retries.", file=sys.stderr)
            return 1

    # 4. Handle Open-Ended Mode
    elif recommend_mode == "open_ended":
        candidate_dir = output_path.parent / "story_identity_candidates"
        candidate_dir.mkdir(parents=True, exist_ok=True)

        bases_mapping = {
            1: BestBasis.GENRE_ALIGNED,
            2: BestBasis.STRUCTURALLY_COHERENT,
            3: BestBasis.FAITHFUL_TO_INPUT,
            4: BestBasis.EMOTIONALLY_POWERFUL,
        }

        labels_mapping = {
            BestBasis.GENRE_ALIGNED: "Genre-contract benchmark",
            BestBasis.STRUCTURALLY_COHERENT: "Cleanest story engine",
            BestBasis.FAITHFUL_TO_INPUT: "Most faithful / most idiosyncratic",
            BestBasis.EMOTIONALLY_POWERFUL: "Highest affect / character-pressure",
        }

        generated_candidates: list[StoryIdentityCandidate] = []
        valid_count = 0

        # Generate candidates sequentially
        for idx in range(1, candidates_count + 1):
            basis = bases_mapping.get(idx, BestBasis.GENRE_ALIGNED)
            print(f"\nGenerating candidate {idx}/{candidates_count} ({basis.value})...")
            identity, diagnostics_messages = _generate_candidate(basis, idx)

            candidate_id = f"candidate_{idx}"
            candidate_path = candidate_dir / f"{candidate_id}.yaml"

            if identity:
                identity.to_yaml(candidate_path)
                valid_count += 1
                status = "valid"
                if diagnostics_messages:
                    status = "valid_with_warnings"

                # Compute hash
                content = candidate_path.read_text(encoding="utf-8")
                chash = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()

                # Build summary info
                sum_req = LLMRequest(
                    system="You are an assistant summarizing a story identity. Provide a concise 1-sentence recommendation summary, a list of 2 key tradeoffs, 2 risks, and 2 ideal scenarios this candidate is best for. Output ONLY valid JSON structure: {\"summary\": \"...\", \"tradeoffs\": [\"...\", \"...\"], \"risks\": [\"...\", \"...\"], \"best_for\": [\"...\", \"...\"]}",
                    user=f"Story Identity:\n{content}",
                    max_tokens=500,
                    temperature=0.3,
                    model=model,
                )
                try:
                    summary_resp = client.complete(sum_req).text
                    json_match = re.search(r"(\{.*\})", summary_resp, re.DOTALL)
                    s_data = json.loads(json_match.group(1)) if json_match else {}
                except Exception:
                    s_data = {}

                generated_candidates.append(
                    StoryIdentityCandidate(
                        candidate_id=candidate_id,
                        path=str(candidate_path),
                        label=labels_mapping.get(basis, f"Option {idx}"),
                        best_basis=basis,
                        recommendation_summary=s_data.get("summary", identity.why_this_is_best or "No summary available."),
                        tradeoffs=s_data.get("tradeoffs", []),
                        risks=s_data.get("risks", []),
                        best_for=s_data.get("best_for", []),
                        validation_status=status,
                        warning_count=len(diagnostics_messages),
                        content_hash=chash,
                    )
                )
            else:
                print(f"Error: Candidate {idx} ({basis.value}) failed to validate after maximum retries.", file=sys.stderr)
                if strict_candidate_count:
                    print("Strict candidate count flag is active. Aborting recommendation process.", file=sys.stderr)
                    return 1

        if valid_count == 0:
            print("Error: 0 valid candidates survived validation checks.", file=sys.stderr)
            return 1

        # Write recommendation_set.yaml
        rec_set = StoryIdentityRecommendationSet(
            mode=RecommendationMode.OPEN_ENDED,
            source_input_path=premise,
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            requested_candidates=candidates_count,
            valid_candidates=valid_count,
            recommended_candidate_id=generated_candidates[0].candidate_id if generated_candidates else None,
            candidates=generated_candidates,
        )

        rec_set_path = candidate_dir / "recommendation_set.yaml"
        rec_set_path.write_text(
            yaml.safe_dump(rec_set.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )

        # Write comparison.md
        comparison_lines = [
            "# Story Identity Candidate Comparison",
            f"\nSource Premise File/Text: `{premise}`",
            f"Generated At: {rec_set.generated_at}\n",
            "| Candidate | Lens / Basis | Status | Summary |",
            "| --- | --- | --- | --- |"
        ]
        for c in generated_candidates:
            comparison_lines.append(f"| `{c.candidate_id}` | **{c.best_basis.value}** ({c.label}) | {c.validation_status} ({c.warning_count} warnings) | {c.recommendation_summary} |")

        comparison_lines.append("\n## Tradeoffs & Risks\n")
        for c in generated_candidates:
            comparison_lines.append(f"### {c.candidate_id}: {c.label}")
            comparison_lines.append(f"**Lens**: `{c.best_basis.value}`")
            comparison_lines.append(f"**Summary**: {c.recommendation_summary}")
            if c.tradeoffs:
                comparison_lines.append("\n*Tradeoffs*:")
                for t in c.tradeoffs:
                    comparison_lines.append(f"- {t}")
            if c.risks:
                comparison_lines.append("\n*Risks*:")
                for r in c.risks:
                    comparison_lines.append(f"- {r}")
            if c.best_for:
                comparison_lines.append("\n*Best For*:")
                for bf in c.best_for:
                    comparison_lines.append(f"- {bf}")
            comparison_lines.append("")

        comparison_path = candidate_dir / "comparison.md"
        comparison_path.write_text("\n".join(comparison_lines), encoding="utf-8")

        print(f"\nSuccess: generated {valid_count} candidates under {candidate_dir}/")
        print(f"Metadata index written to {rec_set_path}")
        print(f"Comparison document written to {comparison_path}")
        return 0

    return 1


def _cmd_identity_accept_candidate(candidate_path: Path, output_path: Path, keep_candidates: bool) -> int:
    import shutil
    import hashlib
    from auteur.identity import StoryIdentity, StoryIdentityRecommendationSet

    if not candidate_path.exists():
        print(f"Error: Candidate file not found: {candidate_path}", file=sys.stderr)
        return 1

    try:
        identity = StoryIdentity.from_yaml(candidate_path)
    except Exception as exc:
        print(f"Error: failed to parse candidate YAML: {exc}", file=sys.stderr)
        return 1

    # Run validation checks
    diagnostics = identity.validate_identity()
    errors = [
        d for d in diagnostics
        if (d.severity.value.lower() == "error" if hasattr(d.severity, "value") else str(d.severity).lower() == "error")
    ]
    if errors:
        print("Error: candidate failed structural validation. Promotion aborted.", file=sys.stderr)
        for err in errors:
            print(f" - {err.message}", file=sys.stderr)
        return 1

    # Optional warning logger
    warnings = [
        d for d in diagnostics
        if (d.severity.value.lower() == "warning" if hasattr(d.severity, "value") else str(d.severity).lower() == "warning")
    ]
    if warnings:
        print("Warnings present in promoted candidate:")
        for warn in warnings:
            print(f" - {warn.message}")

    # Check for recommendation_set.yaml hash mismatch if present
    parent_dir = candidate_path.parent
    rec_set_path = parent_dir / "recommendation_set.yaml"
    if rec_set_path.exists():
        try:
            with open(rec_set_path, "r", encoding="utf-8") as f:
                rec_data = yaml.safe_load(f)
            rec_set = StoryIdentityRecommendationSet.model_validate(rec_data)

            # Compute current hash
            content = candidate_path.read_text(encoding="utf-8")
            current_hash = "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()

            # Find matching candidate metadata
            matching_candidate = None
            for c in rec_set.candidates:
                if Path(c.path).resolve() == candidate_path.resolve():
                    matching_candidate = c
                    break

            if matching_candidate:
                if matching_candidate.content_hash != current_hash:
                    print("[WARNING] Candidate file has been manually modified since recommendation generation index was created.")
        except Exception as exc:
            print(f"[WARNING] Failed to verify candidate hash against recommendation_set.yaml index: {exc}", file=sys.stderr)

    # Promote to target output path
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        identity.to_yaml(output_path)
        print(f"Success: promoted candidate {candidate_path} to {output_path}")
    except Exception as exc:
        print(f"Error: failed to promote candidate to {output_path}: {exc}", file=sys.stderr)
        return 1

    # Cleanup candidate directory if required and is standard location
    if not keep_candidates:
        candidate_dir = parent_dir
        if candidate_dir.name == "story_identity_candidates" and candidate_dir.exists():
            try:
                shutil.rmtree(candidate_dir)
                print(f"Cleaned up candidate directory: {candidate_dir}")
            except Exception as exc:
                print(f"[WARNING] Failed to delete candidate directory {candidate_dir}: {exc}", file=sys.stderr)

    return 0



def _cmd_identity_compile(identity_path: Path, output_path: Path) -> int:
    return _compile_identity_to_blueprint(identity_path, output_path)


def _cmd_blueprint_seed(identity_path: Path, output_path: Path) -> int:
    return _compile_identity_to_blueprint(identity_path, output_path)


def _compile_identity_to_blueprint(identity_path: Path, output_path: Path) -> int:
    if not identity_path.exists():
        print(f"Error: identity file not found: {identity_path}", file=sys.stderr)
        return 1
    try:
        from auteur.identity import StoryIdentity, compile_to_blueprint
        identity = StoryIdentity.from_yaml(identity_path)
        
        # Run validation before compiling
        diagnostics = identity.validate_identity()
        has_error = any(
            (diag.severity.value.lower() == "error" if hasattr(diag.severity, "value") else str(diag.severity).lower() == "error")
            for diag in diagnostics
        )
        if has_error:
            print(f"Error: compilation aborted. StoryIdentity {identity_path} contains structural validation errors:", file=sys.stderr)
            for diag in diagnostics:
                severity_str = diag.severity.value.upper() if hasattr(diag.severity, "value") else str(diag.severity).upper()
                if severity_str == "ERROR":
                    print(f"  - [{severity_str}] Rule: {diag.rule} | Message: {diag.message}", file=sys.stderr)
            return 1

        blueprint = compile_to_blueprint(identity)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            yaml.safe_dump(blueprint.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )
        print(f"Success: compiled identity {identity_path} to blueprint {output_path}")
        return 0
    except Exception as exc:
        print(f"Error: failed to compile story identity {identity_path}: {exc}", file=sys.stderr)
        return 1



def _cmd_cartographer_compile(
    blueprint_path: Path,
    output_path: Path,
    split: bool,
    provider: str,
    model: str | None
) -> int:
    if not blueprint_path.exists():
        print(f"Error: blueprint file not found: {blueprint_path}", file=sys.stderr)
        return 1
    try:
        from auteur.llm.factory import build_client
        from auteur.cartographer_compiler import compile_outline
        from auteur.blueprint import StoryBlueprint
        
        # Try to load blueprint for per-agent model routing
        _bp = None
        try:
            _bp = StoryBlueprint.from_yaml(blueprint_path)
        except Exception:
            pass
        llm = build_client(provider, model, agent_type="cartographer", blueprint=_bp)
        project_path = blueprint_path.parent
        compile_outline(
            project_path=project_path,
            blueprint_path=blueprint_path,
            output_path=output_path,
            split_output=split,
            llm=llm
        )
        print(f"Success: compiled outline into {output_path}")
        return 0
    except Exception as exc:
        print(f"Error: failed to compile outline: {exc}", file=sys.stderr)
        return 1


def _cmd_cartographer_validate(
    outline_path: Path,
    blueprint_path: Path | None
) -> int:
    if not outline_path.exists():
        print(f"Error: outline file not found: {outline_path}", file=sys.stderr)
        return 1
    try:
        from auteur.cartographer_compiler import validate_outline
        validate_outline(outline_path, blueprint_path)
        print(f"Success: outline {outline_path} is valid.")
        return 0
    except Exception as exc:
        print(f"Error: outline validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())