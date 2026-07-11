"""Auteur CLI \u2014 dispatch layer: argparse -> handlers -> formatters/serializers."""

from __future__ import annotations

import argparse, datetime, hashlib, shutil, sys
from pathlib import Path
import yaml

from auteur.blueprint import StoryBlueprint
from auteur.cli_formatters import (
    format_accept, format_audit, format_cartographer_compile,
    format_cartographer_compile_success, format_cartographer_validate,
    format_cartographer_validate_success, format_draft, format_draft_not_accepted,
    format_error, format_identity_compile, format_identity_compile_success,
    format_identity_validate, format_identity_validate_success, format_init,
    format_plan, format_retry, format_structure_apply, format_structure_diagnose,
    format_structure_generate, format_structure_propose_repairs,
)
from auteur.cli_handlers import (
    IdentityValidateData, RecommendOpenEndedData,
    RecommendOpinionatedData, handle_accept, handle_audit,
    handle_audit_resolve_proposal, handle_cartographer_compile,
    handle_cartographer_validate, handle_compile_to_blueprint, handle_draft,
    handle_identity_promote, handle_identity_recommend,
    handle_identity_validate, handle_init, handle_plan, handle_retry,
    handle_structure_apply, handle_structure_diagnose,
    handle_structure_generate, handle_structure_propose_repairs,
)
from auteur.cli_serializers import (
    serialize_audit, serialize_compile_blueprint, serialize_identity_openended,
    serialize_identity_opinionated, serialize_identity_promote,
    serialize_identity_validate, serialize_story_discovery, serialize_structure_diagnose,
    serialize_structure_generate_text, serialize_structure_propose_repairs,
)
from auteur.cli_netorare import handle_netorare_init
from auteur.cli_mystery import handle_mystery_init
from auteur.cli_gentlefemdom import handle_gentlefemdom_init
from auteur.project import Project
from auteur.structure.proposals import StructureProposal

_err = lambda m: print(format_error(m), file=sys.stderr)

class _HideSuppressedFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        if action.help == argparse.SUPPRESS: return ""
        return super()._format_action(action)

def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(prog="auteur",
        description="Agentic narrative engineering toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Create a new project directory.")
    p.add_argument("path", type=Path)
    p.add_argument("--from", dest="blueprint_path", type=Path, required=True)
    p.add_argument("--force", action="store_true",
        help="Re-initialize an existing auteur project directory.")

    p = sub.add_parser("plan",
        help="Render the Cartographer prompt for a chapter (no LLM call).")
    p.add_argument("blueprint", type=Path); p.add_argument("chapter", type=int)

    p = sub.add_parser("draft",
        help="Plan, draft, validate, iterate one chapter.")
    p.add_argument("project", type=Path); p.add_argument("chapter", type=int)
    p.add_argument("--max-iterations", type=int, default=3)
    p.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p.add_argument("--model", default=None)

    p = sub.add_parser("accept",
        help="Promote the latest draft_v*.md to final.md.")
    p.add_argument("project", type=Path); p.add_argument("chapter", type=int)

    p = sub.add_parser("retry",
        help="Continue iterating past previous max-iterations cap.")
    p.add_argument("project", type=Path); p.add_argument("chapter", type=int)
    p.add_argument("--max-iterations", type=int, default=3)
    p.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p.add_argument("--model", default=None)

    p = sub.add_parser("audit",
        help="Run Bible Audit diagnostics to detect carrier-state lore drift across chapters (Layer 6).")
    p.add_argument("project", type=Path)
    p.add_argument("--repair", action="store_true",
        help="Write repair proposals to structure/proposals/.")
    p.add_argument("--accept", default=None,
        help="Resolve a proposal by ID (requires --option).")
    p.add_argument("--option", default=None,
        help="Option ID to select when using --accept.")
    p.add_argument("--layers", default="all",
        help='Layer or layer range to audit. Examples: "6", "1-5", "all" (default).')

    p = sub.add_parser("structure", help="Run whole-story structure commands.")
    ss = p.add_subparsers(dest="structure_command", required=True)
    p = ss.add_parser("diagnose",
        help="Run deterministic whole-story structure diagnostics.")
    p.add_argument("blueprint", type=Path)
    p.add_argument("--output", type=Path, default=None)
    p = ss.add_parser("propose-repairs",
        help="Run structure diagnostics and write repair proposal artifacts.")
    p.add_argument("blueprint", type=Path)
    p = ss.add_parser("apply",
        help="Apply a selected structure proposal option to a blueprint.")
    p.add_argument("proposal", type=Path); p.add_argument("blueprint", type=Path)
    p.add_argument("--output", type=Path, default=None,
        help="Output directory for new blueprint (default: source blueprint directory).")
    p.add_argument("--in-place", action="store_true",
        help="Overwrite the source blueprint file. Disabled by default.")
    p = ss.add_parser("generate",
        help="Generate a story engine from target experience (top-down synthesis), "
        "or diagnose structural issues from a symptom (bottom-up).")
    p.add_argument("blueprint", type=Path,
        help="Blueprint with target_experience but no story_engine.")
    p.add_argument("--output", type=Path, default=None,
        help="Output path for generated story_engine proposal.")
    p.add_argument("--symptom", type=str, default=None,
        help="Author-described symptom (e.g. 'midpoint feels flat'). When provided, "
        "runs bottom-up symptom diagnosis instead of top-down generation.")

    p = sub.add_parser("identity", help="Manage story identities.",
        formatter_class=_HideSuppressedFormatter)
    iss = p.add_subparsers(dest="identity_command", required=True)
    p = iss.add_parser("validate", help="Validate a story_identity.yaml file.")
    p.add_argument("identity", type=Path)
    p.add_argument("--project", type=Path, default=None,
        help="Project path for resolving project-local custom genre contracts.")
    p = iss.add_parser("compile",
        help="Compile a story_identity.yaml into a blueprint.yaml skeleton.")
    p.add_argument("identity", type=Path)
    p.add_argument("--output", type=Path, required=True,
        help="Target output path for the compiled blueprint.yaml skeleton.")
    p = iss.add_parser("recommend",
        help="Recommend an opinionated story_identity.yaml from a raw premise.")
    p.add_argument("premise", type=str,
        help="Raw premise text or path to file containing it.")
    p.add_argument("--genre", type=str, default=None)
    p.add_argument("--medium", type=str, default=None)
    p.add_argument("--mode", type=str, default=None,
        help="Constrain to a story mode (e.g. tragic, comic, noir, epic).")
    p.add_argument("--output", type=Path, default=Path("story_identity.yaml"),
        help="Target output path for the recommended story_identity.yaml.")
    p.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p.add_argument("--model", default=None)
    p.add_argument("--recommend-mode", choices=["opinionated", "open-ended"],
        default="opinionated", help=argparse.SUPPRESS)
    p.add_argument("--candidates", type=int, default=3, help=argparse.SUPPRESS)
    p.add_argument("--strict-candidate-count", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--debug", action="store_true",
        help="Export all failed candidate attempts to .auteur/runs/<timestamp>/.")
    p = iss.add_parser("accept-candidate", help=argparse.SUPPRESS)
    p.add_argument("candidate", type=Path, help=argparse.SUPPRESS)
    p.add_argument("--output", type=Path, default=Path("story_identity.yaml"),
        help=argparse.SUPPRESS)
    p.add_argument("--keep-candidates", action="store_true", help=argparse.SUPPRESS)

    p = sub.add_parser("story-discovery",
        help="Explore narrative interpretations before promoting a story identity.")
    sds = p.add_subparsers(dest="story_discovery_command", required=True)
    p = sds.add_parser("run",
        help="Generate StoryIdentity candidates and an architectural comparison.")
    p.add_argument("brain_dump", type=str,
        help="Raw premise text or path to a file containing it.")
    p.add_argument("--output", type=Path, default=Path("story_discovery"),
        help="Directory for Story Discovery artifacts.")
    p.add_argument("--candidates", type=int, default=3)
    p.add_argument("--lens", action="append", default=None,
        help="Design lens to explore. Repeat to provide multiple lenses.")
    p.add_argument("--genre", type=str, default=None)
    p.add_argument("--project", type=Path, default=None,
        help="Project path for resolving project-local custom genre contracts.")
    p.add_argument("--medium", type=str, default=None)
    p.add_argument("--mode", type=str, default=None)
    p.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p.add_argument("--model", default=None)
    p.add_argument("--strict-candidate-count", action="store_true")
    p.add_argument("--debug", action="store_true",
        help="Export failed candidate attempts to .auteur/runs/<timestamp>/.")
    p = sds.add_parser("accept",
        help="Validate and promote a Story Discovery candidate to story_identity.yaml.")
    p.add_argument("candidate", type=Path)
    p.add_argument("--output", type=Path, default=Path("story_identity.yaml"))
    p.add_argument("--keep-candidates", action="store_true")

    p = sub.add_parser("blueprint", help="Manage story blueprints.")
    bs = p.add_subparsers(dest="blueprint_command", required=True)
    p = bs.add_parser("seed",
        help="Seed a blueprint.yaml skeleton from a story_identity.yaml.")
    p.add_argument("identity", type=Path)
    p.add_argument("--output", type=Path, required=True,
        help="Target output path for the compiled blueprint.yaml skeleton.")

    from auteur.character.cli import register_character_subcommands
    register_character_subcommands(sub)
    from auteur.series.cli import register_series_subcommands
    register_series_subcommands(sub)
    from auteur.editing.cli import register_edit_subcommands
    register_edit_subcommands(sub)
    from auteur.relations.cli import register_relations_subcommands
    register_relations_subcommands(sub)
    from auteur.roundtrip.cli import register_roundtrip_subcommands
    register_roundtrip_subcommands(sub)
    from auteur.genre_builder.cli import register_genre_builder_subcommands
    register_genre_builder_subcommands(sub)
    from auteur.universe.cli import register_universe_subcommands
    register_universe_subcommands(sub)
    from auteur.book.cli import register_book_subcommands
    register_book_subcommands(sub)

    p = sub.add_parser("state",
        help="Manage story state layers programmatically.")
    sts = p.add_subparsers(dest="state_command", required=True)
    p = sts.add_parser("check",
        help="Run Structure Diagnostic (Layers 1-5, 9) and Bible Audit (Layer 6) "
        "in one pass. Optionally validate Scene Representation (Layer 7) "
        "against an outline.yaml with --outline.")
    p.add_argument("project", type=Path)
    p.add_argument("--outline", type=Path, default=None, metavar="PATH",
        help="Path to outline.yaml for Layer 7 carrier validation. "
        "When omitted, a warning is emitted and Layer 7 is skipped.")
    p = sts.add_parser("update",
        help="Safe, transactional update of project files.")
    p.add_argument("project", type=Path); p.add_argument("file", type=Path)
    p.add_argument("--key", type=str, required=True)
    p.add_argument("--val", type=str, required=True,
        help="New value (parsed dynamically as JSON or string).")
    p = sts.add_parser("prepare",
        help="Compile handoff context packets using strict templates.")
    p.add_argument("project", type=Path)
    p.add_argument("phase", choices=["ideation", "drafting", "revision", "recovery"])
    p.add_argument("--scope", choices=["engine", "chapter", "prose"], required=True)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--chapter", type=int, default=None)
    p = sts.add_parser("canon",
        help="Generate high-fidelity summary facts report.")
    p.add_argument("project", type=Path)
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p = sts.add_parser("confirm",
        help="Validate and merge recovery locked layers into canonical state.")
    p.add_argument("project", type=Path)
    p.add_argument("recovery_run", type=Path,
        help="Path to the recovery_run.yaml payload.")

    p = sub.add_parser("cartographer", help="Manage story outlines.")
    cs = p.add_subparsers(dest="cartographer_command", required=True)
    p = cs.add_parser("compile",
        help="Compile a blueprint into a unified cartographer outline.")
    p.add_argument("blueprint", type=Path)
    p.add_argument("--output", type=Path, required=True,
        help="Output destination path for cartographer_outline.yaml.")
    p.add_argument("--split", action="store_true", default=True,
        help="Auto-split compiled chapters into chapters/XX/outline.yaml.")
    p.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    p.add_argument("--model", default=None)
    p = cs.add_parser("validate",
        help="Deterministic, local validator for compiled cartographer outlines.")
    p.add_argument("outline", type=Path)
    p.add_argument("--blueprint", type=Path, default=None,
        help="Blueprint to compare tension target against.")

    from auteur.genre_pipeline.cli import register_genre_pipeline_subcommands
    register_genre_pipeline_subcommands(sub)

    return parser

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments and return namespace."""
    parser = _build_parser()
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    # === init ===
    if args.command == "init":
        path = args.path
        if path.exists() and not args.force:
            _err(f"project path already exists: {path}")
            return 1
        if args.force and path.exists():
            if not (path / "blueprint.yaml").is_file() or not (path / "bible.json").is_file():
                _err("--force requires an existing auteur project directory (blueprint.yaml + bible.json).")
                return 1
            shutil.rmtree(path)
        try: bp = StoryBlueprint.from_yaml(args.blueprint_path)
        except FileNotFoundError: _err(f"blueprint not found: {args.blueprint_path}"); return 1
        except Exception as exc: _err(f"invalid blueprint \u2014 {exc}"); return 1
        result = handle_init(bp, path)
        if not result.is_success: _err(result.error); return result.exit_code
        out = format_init(result)
        if out: print(out)
        else: print(f"Initialized project at {path}")
        return 0
    # === plan ===
    if args.command == "plan":
        try: bp = StoryBlueprint.from_yaml(args.blueprint)
        except FileNotFoundError: _err(f"blueprint file not found: {args.blueprint}"); return 1
        result = handle_plan(bp, args.chapter)
        if not result.is_success: _err(result.error); return result.exit_code
        out = format_plan(result)
        if out: print(out)
        return 0
    # === draft ===
    if args.command == "draft":
        return _draft_retry(args, is_retry=False)
    # === accept ===
    if args.command == "accept":
        proj = Project.load(args.project)
        result = handle_accept(proj, args.chapter)
        if not result.is_success: _err(result.error); return result.exit_code
        out = format_accept(result)
        if out: print(out)
        return 0
    # === retry ===
    if args.command == "retry":
        return _draft_retry(args, is_retry=True)
    # === audit ===
    if args.command == "audit":
        bp_path = args.project / "blueprint.yaml"
        if not bp_path.exists(): _err(f"No blueprint.yaml found in {args.project}"); return 1
        if not (args.project / "bible.json").exists():
            _err(f"No bible.json found in {args.project}"); return 1
        if args.accept is not None:
            if args.option is None: print("--accept requires --option.", file=sys.stderr); return 1
            return handle_audit_resolve_proposal(args.project, args.accept, args.option).exit_code
        from auteur.bible import StoryBible
        result = handle_audit(StoryBlueprint.from_yaml(bp_path),
            StoryBible(args.project / "bible.json"), Project.load(args.project),
            repair=args.repair, layers=args.layers)
        if result.data is None: return result.exit_code
        d = result.data
        if not d.diagnostics and result.exit_code == 0:
            out = format_audit(result)
            if out: print(out)
            return 0
        dd = args.project / "structure" / "diagnostics"
        try:
            ap = serialize_audit(result, dd)
            if ap is None: _err("no data to serialize"); return 1
        except OSError as exc:
            _err(f"failed to write audit report to {dd / 'audit_report.json'}: {exc}"); return 1
        d.artifact_path = ap; result.data = d
        out = format_audit(result)
        if out: print(out)
        if args.repair and d.diagnostics:
            from auteur.structure.proposal_resolution import write_audit_repair_proposals
            write_audit_repair_proposals(args.project, d.diagnostics)
        return result.exit_code
    # === structure diagnose ===
    if args.command == "structure" and args.structure_command == "diagnose":
        try: bp = StoryBlueprint.from_yaml(args.blueprint)
        except FileNotFoundError: _err(f"blueprint not found: {args.blueprint}"); return 1
        except (ValueError, yaml.YAMLError) as exc:
            _err(f"invalid blueprint {args.blueprint}: {exc}"); return 1
        result = handle_structure_diagnose(bp)
        if not result.is_success: _err(result.error); return result.exit_code
        if args.output: ap = args.output
        else:
            bpp = args.blueprint
            if bpp.is_dir(): dd = Project.load(bpp).structure_diagnostics_dir()
            elif bpp.name == "blueprint.yaml" and (bpp.parent / "bible.json").exists():
                dd = Project.load(bpp.parent).structure_diagnostics_dir()
            else: dd = bpp.parent / "structure" / "diagnostics"; dd.mkdir(parents=True, exist_ok=True)
            ap = dd / "structure_report.json"
        try:
            if serialize_structure_diagnose(result, ap) is None: _err("no data to serialize"); return 1
        except OSError as exc: _err(f"failed to write report to {ap}: {exc}"); return 1
        out = format_structure_diagnose(result)
        if out: print(out)
        print(f"Diagnostics written to {ap}")
        return 4 if result.data["errors"] else 0
    # === structure propose-repairs ===
    if args.command == "structure" and args.structure_command == "propose-repairs":
        try: bp, dd, pd = _bp_dirs(args.blueprint)
        except FileNotFoundError: _err(f"blueprint not found: {args.blueprint}"); return 1
        except Exception as exc: _err(f"invalid blueprint {args.blueprint}: {exc}"); return 1
        result = handle_structure_propose_repairs(bp)
        if not result.is_success: _err(result.error); return result.exit_code
        try:
            if serialize_structure_propose_repairs(result, dd, pd) is None:
                _err("no data to serialize"); return 1
        except OSError as exc: _err(f"failed to write structure artifacts: {exc}"); return 1
        out = format_structure_propose_repairs(result)
        if out: print(out)
        return 0
    # === structure apply ===
    if args.command == "structure" and args.structure_command == "apply":
        if not args.proposal.exists(): _err(f"proposal not found: {args.proposal}"); return 1
        if not args.blueprint.exists(): _err(f"blueprint not found: {args.blueprint}"); return 1
        if args.in_place and args.output is not None:
            print("Error: --output cannot be used with --in-place", file=sys.stderr); return 1
        try: prop = StructureProposal.model_validate(
            yaml.safe_load(args.proposal.read_text(encoding="utf-8")))
        except (ValueError, yaml.YAMLError, OSError) as exc:
            _err(f"invalid proposal {args.proposal}: {exc}"); return 1
        if prop.source_domain == "bible_audit":
            _err("bible_audit proposals cannot be applied to blueprints. "
                "Resolve them with `auteur audit --accept ... --option ...`."); return 1
        try: bp, _, _ = _bp_dirs(args.blueprint)
        except Exception as exc: _err(f"invalid blueprint {args.blueprint}: {exc}"); return 1
        if (not prop.selection.selected_option_id and prop.decision is not None
                and prop.decision.status == "accepted"):
            prop.selection.selected_option_id = prop.decision.selected_option_id
            if not prop.selection.custom_data and prop.decision.custom_data:
                prop.selection.custom_data = prop.decision.custom_data
        src = args.blueprint / "blueprint.yaml" if args.blueprint.is_dir() else args.blueprint
        result = handle_structure_apply(prop, bp, in_place=args.in_place,
            output_dir=str(args.output or src.parent) if not args.in_place else None,
            original_path=str(src) if args.in_place else None)
        if not result.is_success: _err(result.error); return result.exit_code
        result.data["proposal_path"] = str(args.proposal)
        result.data["source_blueprint_path"] = str(src)
        out = format_structure_apply(result)
        if out: print(out)
        return 0
    # === structure generate ===
    if args.command == "structure" and args.structure_command == "generate":
        try: bp = StoryBlueprint.from_yaml(args.blueprint)
        except FileNotFoundError: _err(f"blueprint file not found: {args.blueprint}"); return 1
        except Exception as e: _err(f"failed to parse blueprint {args.blueprint}: {e}"); return 1
        result = handle_structure_generate(bp, symptom=args.symptom)
        if not result.is_success: _err(result.error); return result.exit_code
        d = result.data
        if d.get("is_diagnostics") and "diagnoses" in d:
            d["blueprint"] = str(args.blueprint); result.data = d
            out = format_structure_generate(result)
            if out: print(out)
            if args.output: serialize_structure_generate_text(out, args.output)
            if args.output: print(f"\nDiagnosis written to {args.output}", file=sys.stderr)
            return 0
        if d.get("is_diagnostics") and "diagnostics" in d:
            out = format_structure_generate(result)
            if out: print(out, file=sys.stderr)
            return 1 if [x for x in d["diagnostics"] if x.get("severity") == "error"] else 0
        out = format_structure_generate(result)
        if out: print(out)
        if args.output: serialize_structure_generate_text(out, args.output); print(
            f"\nProposal written to {args.output}", file=sys.stderr)
        return 0
    # === story-discovery run ===
    if args.command == "story-discovery" and args.story_discovery_command == "run":
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        premise_text = args.brain_dump
        try:
            premise_path = Path(args.brain_dump)
            if premise_path.exists() and premise_path.is_file():
                premise_text = premise_path.read_text(encoding="utf-8")
        except Exception:
            pass
        from auteur.llm.factory import build_client
        client = build_client(args.provider, args.model, agent_type="identity")
        result = handle_identity_recommend(
            client=client,
            premise_text=premise_text,
            genre=args.genre,
            medium=args.medium,
            mode=args.mode,
            recommend_mode="open_ended",
            candidates_count=args.candidates,
            discovery_lenses=args.lens,
            strict_candidate_count=args.strict_candidate_count,
            debug=args.debug,
            timestamp=ts,
            project_path=args.project,
        )
        if not result.is_success:
            _err(result.error)
            return result.exit_code
        data = result.data
        if not isinstance(data, RecommendOpenEndedData):
            _err("story discovery did not return candidate data")
            return 1
        written = serialize_story_discovery(data, args.output, args.brain_dump)
        candidate_count = len(data.candidates)
        for path in written[:candidate_count]:
            print(f"  Wrote {path.name}")
        print(f"\nSuccess: generated {candidate_count} Story Discovery candidates under {args.output}/")
        print(f"Discovery report written to {args.output / 'discovery_report.yaml'}")
        print(f"Comparison document written to {args.output / 'comparison.md'}")
        return 0
    # === story-discovery accept ===
    if args.command == "story-discovery" and args.story_discovery_command == "accept":
        from auteur.identity import StoryIdentity
        if not args.candidate.exists():
            print(f"Error: Candidate file not found: {args.candidate}", file=sys.stderr)
            return 1
        try:
            ident = StoryIdentity.from_yaml(args.candidate)
        except Exception as exc:
            print(f"Error: failed to parse candidate YAML: {exc}", file=sys.stderr)
            return 1
        result = handle_identity_promote(ident)
        if not result.is_success:
            print(f"Error: {result.error}", file=sys.stderr)
            if result.data:
                for err in result.data.diagnostics:
                    sv = err.severity.value.upper() if hasattr(err.severity, "value") else str(err.severity).upper()
                    if sv == "ERROR":
                        print(f" - {err.message}", file=sys.stderr)
            return result.exit_code
        if result.data.warnings:
            print("Warnings present in promoted candidate:")
            for w in result.data.warnings:
                print(f" - {w.message}")
        try:
            serialize_identity_promote(ident, args.output)
        except Exception as exc:
            print(f"Error: failed to promote candidate to {args.output}: {exc}", file=sys.stderr)
            return 1
        report_path = args.candidate.parent / "discovery_report.yaml"
        if report_path.exists():
            try:
                report = yaml.safe_load(report_path.read_text(encoding="utf-8")) or {}
                report["chosen_candidate"] = args.candidate.stem
                report_path.write_text(yaml.safe_dump(report, sort_keys=False), encoding="utf-8")
            except (OSError, yaml.YAMLError) as exc:
                print(f"[WARNING] Failed to update discovery report: {exc}", file=sys.stderr)
        print(f"Success: promoted candidate {args.candidate} to {args.output}")
        if not args.keep_candidates:
            candidate_dir = args.candidate.parent
            if candidate_dir.name == "story_discovery" and candidate_dir.exists():
                try:
                    shutil.rmtree(candidate_dir)
                    print(f"Cleaned up candidate directory: {candidate_dir}")
                except Exception as exc:
                    print(f"[WARNING] Failed to delete candidate directory {candidate_dir}: {exc}", file=sys.stderr)
        return 0
    # === identity validate ===
    if args.command == "identity" and args.identity_command == "validate":
        if not args.identity.exists(): _err(f"identity file not found: {args.identity}"); return 1
        try:
            from auteur.identity import StoryIdentity
            ident = StoryIdentity.from_yaml(args.identity)
            if args.project is not None:
                from auteur.genres.registry import load_project_genre_contract
                ident.genre_contract_snapshot = load_project_genre_contract(args.project, ident.story_type.genre)
        except Exception as exc: _err(f"invalid story identity {args.identity}: {exc}"); return 1
        result = handle_identity_validate(ident)
        if not result.is_success: _err(result.error); return result.exit_code
        data: IdentityValidateData = result.data
        dd = args.identity.parent / "identity"; dd.mkdir(parents=True, exist_ok=True)
        ap = dd / "validation_report.json"
        try:
            if serialize_identity_validate(result, dd) is None: _err("no data to serialize"); return 1
        except OSError as exc: _err(f"failed to write validation report to {ap}: {exc}"); return 1
        out = format_identity_validate(result)
        if out: print(out, file=sys.stderr)
        verdict = format_identity_validate_success(result, str(args.identity))
        if data.has_error:
            print(verdict, file=sys.stderr); print(f"Validation report written to {ap}", file=sys.stderr)
            return 1
        print(verdict); print(f"Validation report written to {ap}")
        return 0
    # === identity compile / blueprint seed ===
    if (args.command == "identity" and args.identity_command == "compile") or \
       (args.command == "blueprint" and args.blueprint_command == "seed"):
        if not args.identity.exists(): _err(f"identity file not found: {args.identity}"); return 1
        try:
            from auteur.identity import StoryIdentity
            ident = StoryIdentity.from_yaml(args.identity)
        except Exception as exc:
            _err(f"failed to parse story identity {args.identity}: {exc}"); return 1
        result = handle_compile_to_blueprint(ident)
        if not result.is_success: _err(result.error); return result.exit_code
        try:
            if serialize_compile_blueprint(result, args.output) is None:
                _err("no data to serialize"); return 1
        except Exception as exc:
            _err(f"failed to write blueprint to {args.output}: {exc}"); return 1
        print(format_identity_compile_success(str(args.identity), str(args.output)))
        return 0
    # === identity recommend ===
    if args.command == "identity" and args.identity_command == "recommend":
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pt = args.premise
        try:
            pp = Path(args.premise)
            if pp.exists() and pp.is_file(): pt = pp.read_text(encoding="utf-8")
        except Exception: pass
        rec_mode = args.recommend_mode; story_mode = args.mode
        if args.mode in ("open-ended", "open_ended"):
            print("Warning: --mode open-ended is deprecated. "
                "Use --recommend-mode open-ended instead.", file=sys.stderr)
            rec_mode = "open_ended"; story_mode = None
        if rec_mode == "open-ended": rec_mode = "open_ended"
        from auteur.llm.factory import build_client
        client = build_client(args.provider, args.model, agent_type="identity")
        result = handle_identity_recommend(client=client, premise_text=pt,
            genre=args.genre, medium=args.medium, mode=story_mode,
            recommend_mode=rec_mode, candidates_count=args.candidates,
            discovery_lenses=(
                ["genre_aligned", "structurally_coherent", "faithful_to_input", "emotionally_powerful"]
                if rec_mode == "open_ended" else None
            ),
            strict_candidate_count=args.strict_candidate_count,
            debug=args.debug, timestamp=ts)
        if not result.is_success: _err(result.error); return result.exit_code
        data = result.data
        if isinstance(data, RecommendOpinionatedData):
            serialize_identity_opinionated(data, args.output, debug=args.debug, timestamp=ts)
            print(f"Success: saved recommended story identity to {args.output}")
            if data.warnings:
                print("Warnings encountered during generation:")
                for w in data.warnings: print(f" - {w}")
            return 0
        elif isinstance(data, RecommendOpenEndedData):
            written = serialize_identity_openended(data, args.output, args.premise)
            cdir = written[0].parent if written else args.output.parent / "story_identity_candidates"
            for p in written[:len(data.candidates)]: print(f"  Wrote {p.name}")
            print(f"\nSuccess: generated {len(data.candidates)} candidates under {cdir}/")
            print(f"Metadata index written to {cdir / 'recommendation_set.yaml'}")
            print(f"Comparison document written to {cdir / 'comparison.md'}")
            return 0
        return 1
    # === identity accept-candidate ===
    if args.command == "identity" and args.identity_command == "accept-candidate":
        from auteur.identity import StoryIdentity, StoryIdentityRecommendationSet
        if not args.candidate.exists():
            print(f"Error: Candidate file not found: {args.candidate}", file=sys.stderr); return 1
        try: ident = StoryIdentity.from_yaml(args.candidate)
        except Exception as exc:
            print(f"Error: failed to parse candidate YAML: {exc}", file=sys.stderr); return 1
        result = handle_identity_promote(ident)
        if not result.is_success:
            print(f"Error: {result.error}", file=sys.stderr)
            if result.data:
                for err in result.data.diagnostics:
                    sv = err.severity.value.upper() if hasattr(err.severity, "value") else str(err.severity).upper()
                    if sv == "ERROR": print(f" - {err.message}", file=sys.stderr)
            return result.exit_code
        if result.data.warnings:
            print("Warnings present in promoted candidate:")
            for w in result.data.warnings:
                sv = w.severity.value.upper() if hasattr(w.severity, "value") else str(w.severity).upper()
                print(f" - {w.message}")
        pdir = args.candidate.parent; rsp = pdir / "recommendation_set.yaml"
        if rsp.exists():
            try:
                rs = StoryIdentityRecommendationSet.model_validate(
                    yaml.safe_load(open(rsp, encoding="utf-8")))
                cur = "sha256:" + hashlib.sha256(
                    args.candidate.read_text(encoding="utf-8").encode()).hexdigest()
                for c in rs.candidates:
                    if Path(c.path).resolve() == args.candidate.resolve() and c.content_hash != cur:
                        print("[WARNING] Candidate file has been manually modified "
                            "since recommendation generation index was created.")
                        break
            except Exception as exc:
                print(f"[WARNING] Failed to verify candidate hash against "
                    f"recommendation_set.yaml index: {exc}", file=sys.stderr)
        try: serialize_identity_promote(ident, args.output)
        except Exception as exc:
            print(f"Error: failed to promote candidate to {args.output}: {exc}", file=sys.stderr)
            return 1
        print(f"Success: promoted candidate {args.candidate} to {args.output}")
        if not args.keep_candidates:
            cd = pdir
            if cd.name == "story_identity_candidates" and cd.exists():
                try: shutil.rmtree(cd); print(f"Cleaned up candidate directory: {cd}")
                except Exception as exc:
                    print(f"[WARNING] Failed to delete candidate directory {cd}: {exc}", file=sys.stderr)
        return 0
    # === state ===
    if args.command == "state":
        from auteur.structure.state import (
            state_check, state_update, state_prepare, state_canon, state_confirm)
        if args.state_command == "check":
            ol: Path | None = getattr(args, "outline", None)
            if ol is not None:
                if not ol.exists(): _err(f"Outline file not found: {ol}"); return 1
                from auteur.structure.outline_audit import load_outline
                try: outline = load_outline(str(ol))
                except ValueError as exc: _err(str(exc)); return 1
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
    # === cartographer ===
    if args.command == "cartographer":
        if args.cartographer_command == "compile":
            try: bp = StoryBlueprint.from_yaml(args.blueprint)
            except FileNotFoundError: _err(f"blueprint file not found: {args.blueprint}"); return 1
            except Exception: bp = None
            try:
                from auteur.llm.factory import build_client
                llm = build_client(args.provider, args.model, agent_type="cartographer", blueprint=bp)
            except Exception as exc: _err(f"failed to build LLM client: {exc}"); return 1
            result = handle_cartographer_compile(args.blueprint, llm, args.output, split=args.split)
            if not result.is_success: _err(result.error); return result.exit_code
            out = format_cartographer_compile(result)
            if out: print(out)
            else: print(format_cartographer_compile_success(str(args.output)))
            return 0
        if args.cartographer_command == "validate":
            result = handle_cartographer_validate(args.outline, args.blueprint)
            if not result.is_success: _err(result.error); return result.exit_code
            out = format_cartographer_validate(result)
            if out: print(out)
            else: print(format_cartographer_validate_success(str(args.outline)))
            return 0
    # === character ===
    if args.command == "character":
        from auteur.character.cli import handle_character_command
        return handle_character_command(args)
    # === series ===
    if args.command == "series":
        from auteur.series.cli import handle_series_command
        return handle_series_command(args)
    # === edit ===
    if args.command == "edit":
        from auteur.editing.cli import handle_edit_command
        return handle_edit_command(args)
    # === relations ===
    if args.command == "relations":
        from auteur.relations.cli import handle_relations_command
        return handle_relations_command(args)
    # === export/import round-trip ===
    if args.command == "export":
        from auteur.roundtrip.cli import handle_export_command
        return handle_export_command(args)
    if args.command == "import":
        from auteur.roundtrip.cli import handle_import_command
        return handle_import_command(args)
    # === genre builder ===
    if args.command == "genre":
        from auteur.genre_builder.cli import handle_genre_builder_command
        return handle_genre_builder_command(args)

    # === universe ===
    if args.command == "universe":
        from auteur.universe.cli import handle_universe_command
        return handle_universe_command(args)
    if args.command == "book":
        from auteur.book.cli import handle_book_command
        return handle_book_command(args)

    # === netorare ===
    if args.command == "netorare":
        if args.netorare_command == "init":
            return handle_netorare_init(
                project_path=args.project,
                core_id=args.core,
                provider=args.provider,
                port=args.port,
                timeout=args.timeout,
                debug=args.debug,
                mode=args.mode,
            )

    # === mystery ===
    if args.command == "mystery":
        if args.mystery_command == "init":
            return handle_mystery_init(
                project_path=args.project,
                core_id=args.core,
                provider=args.provider,
                port=args.port,
                timeout=args.timeout,
                debug=args.debug,
                mode=args.mode,
            )

    # === gentlefemdom ===
    if args.command == "gentlefemdom":
        if args.gentlefemdom_command == "init":
            return handle_gentlefemdom_init(
                project_path=args.project,
                core_id=args.core,
                provider=args.provider,
                port=args.port,
                timeout=args.timeout,
                debug=args.debug,
                mode=args.mode,
            )

    return 0

def _draft_retry(args, *, is_retry: bool) -> int:
    from auteur.llm.factory import build_client
    proj = Project.load(args.project)
    client = build_client(args.provider, args.model, agent_type="bard", blueprint=proj.blueprint)
    result = handle_retry(proj, args.chapter, args.max_iterations, client) if is_retry else \
             handle_draft(proj, args.chapter, args.max_iterations, client)
    if not is_retry and result.data is None: return result.exit_code
    if is_retry and not result.is_success and result.data is None:
        _err(result.error); return result.exit_code
    d = result.data
    if d is None: return result.exit_code
    if d.conflict_report is not None:
        out = format_draft(result)
        if out: print(out, file=sys.stderr)
        print(f"  See {proj.chapter_dir(args.chapter) / 'outline.yaml'} for details.", file=sys.stderr)
        return result.exit_code
    if d.accepted:
        out = format_retry(result) if is_retry else format_draft(result)
        if out: print(out)
        return 0
    out = format_draft_not_accepted(result, str(args.project), args.chapter)
    if out: print(out, file=sys.stderr)
    return 2

def _bp_dirs(bp_path: Path) -> tuple[StoryBlueprint, Path, Path]:
    if bp_path.is_dir():
        proj = Project.load(bp_path)
        return proj.blueprint, proj.structure_diagnostics_dir(), proj.structure_proposals_dir()
    if bp_path.name == "blueprint.yaml" and (bp_path.parent / "bible.json").exists():
        proj = Project.load(bp_path.parent)
        return proj.blueprint, proj.structure_diagnostics_dir(), proj.structure_proposals_dir()
    bp = StoryBlueprint.from_yaml(bp_path)
    dd = bp_path.parent / "structure" / "diagnostics"
    pd = bp_path.parent / "structure" / "proposals"
    dd.mkdir(parents=True, exist_ok=True); pd.mkdir(parents=True, exist_ok=True)
    return bp, dd, pd

if __name__ == "__main__":
    raise SystemExit(main())
