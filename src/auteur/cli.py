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
        return _cmd_audit(args.project, repair=args.repair, accept=args.accept, option=args.option)
    if args.command == "structure" and args.structure_command == "diagnose":
        return _cmd_structure_diagnose(args.blueprint, args.output)
    if args.command == "structure" and args.structure_command == "propose-repairs":
        return _cmd_structure_propose_repairs(args.blueprint)
    if args.command == "structure" and args.structure_command == "apply":
        return _cmd_structure_apply(args.proposal, args.blueprint, args.output, args.in_place)
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
    client = _build_client(provider, model)
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


def _cmd_audit(project_path: Path, *, repair: bool = False, accept: str | None = None, option: str | None = None) -> int:
    """Run Bible audit diagnostics on a project and print results.
    When `repair` is True, also write proposal artifacts.  When `accept` is set, resolve the named proposal."""
    from auteur.structure.bible_audit import audit_bible_locations

    if not project_path.is_dir():
        print(f"Project path is not a directory: {project_path}", file=sys.stderr)
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
        return _resolve_proposal(project_path, accept, option)

    from auteur.bible import StoryBible
    bible = StoryBible(bible_path)

    # --- Load resolved proposals to filter output ---
    resolved_rules: set[str] = _load_resolved_rules(project_path)

    raw_diagnostics = audit_bible_locations(bible)
    diagnostics = [d for d in raw_diagnostics if d.rule not in resolved_rules]

    if not raw_diagnostics:
        print("No lore drift detected.")
        return 0

    if not diagnostics:
        print("All previously detected lore drift has been resolved.")
        return 0

    for d in diagnostics:
        _print_diagnostic(d)

    if repair and diagnostics:
        _write_audit_repair_proposals(project_path, diagnostics)

    errors = sum(1 for d in diagnostics if d.severity.value == "error")
    warnings = sum(1 for d in diagnostics if d.severity.value == "warning")
    print(f"Found {errors} unresolved error(s), {warnings} unresolved warning(s).")
    return 1 if errors > 0 else 0


def _write_audit_repair_proposals(
    project_path: Path,
    diagnostics: list[object],
) -> None:
    """Serialize Bible audit diagnostics into StructureProposal YAML files."""
    from auteur.structure.proposals import (
        ProposalOption,
        ProposalType,
        StructureProposal,
    )

    proposals_dir = project_path / "structure" / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)

    # Collect existing proposal file stems to avoid overwriting resolved ones
    existing_proposals = {p.stem for p in proposals_dir.glob("repair_*.yaml")}

    for idx, d in enumerate(diagnostics, start=1):
        options: list[ProposalOption] = []
        for pi, preserve in enumerate(d.repair_options.preserve_intent, start=1):
            options.append(
                ProposalOption(
                    id=f"preserve_{pi}",
                    summary=preserve,
                    tradeoffs=(
                        "Preserves the story's declared intent while "
                        "resolving the continuity break."
                    ),
                    data={},
                )
            )
        for ci, challenge in enumerate(d.repair_options.challenge_intent, start=1):
            options.append(
                ProposalOption(
                    id=f"challenge_{ci}",
                    summary=challenge,
                    tradeoffs=(
                        "Questions a higher-level assumption to resolve "
                        "the continuity break."
                    ),
                    data={},
                )
            )

        proposal = StructureProposal(
            proposal_id=f"repair_{idx}_{d.rule.replace('.', '_')}",
            type=ProposalType.REPAIR,
            source_rule=d.rule,
            summary=f"[{d.severity.value.upper()}] {d.rule}: {d.message}",
            options=options,
        )

        # Skip if a proposal file for this ID already exists (preserve resolved state)
        if proposal.proposal_id in existing_proposals:
            continue

        proposal_path = proposals_dir / f"{proposal.proposal_id}.yaml"
        import yaml as _yaml
        proposal_path.write_text(
            _yaml.safe_dump(proposal.model_dump(mode="json"), sort_keys=False),
            encoding="utf-8",
        )

    print(f"Wrote {len(diagnostics)} repair proposal(s) to {proposals_dir}")


def _print_diagnostic(d: object) -> None:
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


def _load_resolved_rules(project_path: Path) -> set[str]:
    """Scan structure/proposals/ for YAML files with a non-empty selected_option_id.
    Return the set of source_rule values that have been resolved."""
    import yaml as _yaml
    proposals_dir = project_path / "structure" / "proposals"
    if not proposals_dir.is_dir():
        return set()

    resolved: set[str] = set()
    for proposal_file in sorted(proposals_dir.glob("*.yaml")):
        try:
            data = _yaml.safe_load(proposal_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        selection = data.get("selection", {})
        if isinstance(selection, dict) and selection.get("selected_option_id"):
            source_rule = data.get("source_rule")
            if source_rule:
                resolved.add(source_rule)
    return resolved


def _resolve_proposal(project_path: Path, proposal_id: str, option_id: str) -> int:
    """Load a proposal YAML, set the selected option, record a decision, and save."""
    import yaml as _yaml
    from datetime import datetime, timezone

    proposals_dir = project_path / "structure" / "proposals"
    proposal_path = proposals_dir / f"{proposal_id}.yaml"

    if not proposal_path.exists():
        print(f"Proposal not found: {proposal_path}", file=sys.stderr)
        return 1

    try:
        data = _yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Failed to parse {proposal_path}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print(f"Invalid proposal format: {proposal_path}", file=sys.stderr)
        return 1

    options = data.get("options", [])
    option_ids = [o.get("id") for o in options if isinstance(o, dict)]
    if option_id not in option_ids:
        print(
            f"Option '{option_id}' not found in proposal. "
            f"Available: {option_ids}",
            file=sys.stderr,
        )
        return 1

    data["selection"] = {
        "selected_option_id": option_id,
        "custom_data": {},
    }
    data["decision"] = {
        "selected_option_id": option_id,
        "custom_data": {},
        "status": "accepted",
        "author": None,
        "references": [],
        "accepted_at": datetime.now(timezone.utc).isoformat(),
    }

    proposal_path.write_text(
        _yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )
    print(f"Resolved {proposal_id} with option '{option_id}'.")
    return 0



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

    client = _build_client(provider, model)
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


def _build_client(provider: str, model: str | None) -> LLMClient:
    """Construct the production client for the chosen provider.

    Patched in tests with a FakeClient.
    """
    if provider == "anthropic":
        from auteur.llm.anthropic import AnthropicClient
        return AnthropicClient(default_model=model or "claude-sonnet-4-6")
    if provider == "openai":
        from auteur.llm.openai import OpenAIClient
        return OpenAIClient(default_model=model or "gpt-4o")
    raise ValueError(f"Unknown provider: {provider}")


if __name__ == "__main__":
    raise SystemExit(main())