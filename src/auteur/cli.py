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

    p_audit = sub.add_parser("audit", help="Run Bible audit diagnostics to detect lore drift.")
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

    # Identity subcommands
    p_identity = sub.add_parser("identity", help="Manage story identities.")
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

    p_state_check = state_sub.add_parser("check", help="Unified dual audit of blueprint and bible state consistency.")
    p_state_check.add_argument("project", type=Path)

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
    if args.command == "identity" and args.identity_command == "validate":
        return _cmd_identity_validate(args.identity)
    if args.command == "identity" and args.identity_command == "compile":
        return _cmd_identity_compile(args.identity, args.output)
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
    client = build_client(provider, model)
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
    client = build_client(provider, model)
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
                4: DiagnosticLayer.CONSTRAINTS,
                5: DiagnosticLayer.STRUCTURAL_FORCES,
                6: DiagnosticLayer.CARRIERS,
                7: DiagnosticLayer.THEME,
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
            4: DiagnosticLayer.CONSTRAINTS,
            5: DiagnosticLayer.STRUCTURAL_FORCES,
            6: DiagnosticLayer.CARRIERS,
            7: DiagnosticLayer.THEME,
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
        
        llm = build_client(provider, model)
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