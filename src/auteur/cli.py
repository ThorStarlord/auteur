"""Auteur CLI \u2014 dispatch layer: argparse -> handlers -> formatters/serializers."""

from __future__ import annotations

import argparse, datetime, hashlib, json, shutil, sys
from pathlib import Path
import yaml


def _pilot_artifact_type(path: Path) -> str:
    if path.name == "story_identity.yaml":
        return "story_identity"
    if path.name == "blueprint.yaml":
        return "blueprint"
    if path.name.startswith("scene_"):
        return "scene_realization"
    if path.name.startswith("chapter_") or path.name == "outline.yaml":
        return "chapter_outline"
    return path.stem


def _pilot_project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / ".auteur").is_dir() or (parent / "story_identity.yaml").exists() or (parent / "blueprint.yaml").exists():
            return parent
    return path.parent

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
from auteur.narrative_blueprint.cli_blueprint import handle_blueprint_init, handle_blueprint_list
from auteur.narrative_orchestration.cli_orchestration import (
    handle_orchestration_seed,
    handle_orchestration_validate,
    handle_orchestration_graph,
    handle_orchestration_status,
)
from auteur.narrative_realization.cli_realization import (
    handle_realization_seed,
    handle_realization_validate,
    handle_realization_inspect,
    handle_realization_graph,
)
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

    p = sub.add_parser("status", help="Show project health summary (like git status for a novel).")
    p.add_argument("--project", type=Path, default=Path("."), help="Project root directory (default: current directory).")
    p.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text.")
    p.add_argument("--verbose", action="store_true", help="Show detailed artifact IDs.")

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
    p.add_argument("--regenerate-outline", action="store_true", help="Regenerate an existing outline explicitly.")

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

    p = sub.add_parser("reasoning", help="Inspect derived reasoning reviews.")
    rs = p.add_subparsers(dest="reasoning_command", required=True)
    p = rs.add_parser("review", help="Show an author-facing derived reasoning review.")
    p.add_argument("review", type=Path)
    p.add_argument("--json", action="store_true", help="Show the complete derived review JSON.")
    p = rs.add_parser("inspect", help="Inspect one derived review group.")
    p.add_argument("review", type=Path)
    p.add_argument("group")
    p.add_argument("--json", action="store_true", help="Show the complete group JSON.")

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

    for command, help_text in (
        ("status", "Show pilot provenance status for an artifact."),
        ("explain", "Explain pilot provenance staleness or invalidity."),
        ("adopt", "Create baseline provenance for a legacy artifact."),
        ("accept", "Accept a pilot artifact and create a provenance revision."),
        ("archive", "Archive a pilot artifact without deleting its content."),
        ("affected-by", "Show direct and transitive artifacts affected by an artifact."),
    ):
        p = sts.add_parser(command, help=help_text)
        p.add_argument("artifact", type=Path)
        if command in {"adopt", "accept", "archive"}:
            p.add_argument("--type", dest="artifact_type", default=None)
        if command == "archive":
            p.add_argument("--reason", default="archived by author")
        if command == "affected-by":
            p.add_argument("--json", action="store_true", dest="json_output")

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

    from auteur.narrative_ontology.cli_ontology import register_ontology_subcommands
    register_ontology_subcommands(sub)

    return parser

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments and return namespace."""
    parser = _build_parser()
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "reasoning":
        from auteur.reasoning.cli import format_review, load_review
        try:
            review = load_review(args.review)
        except FileNotFoundError:
            _err(f"reasoning review not found: {args.review}")
            return 1
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            _err(f"invalid reasoning review {args.review}: {exc}")
            return 1
        if args.reasoning_command == "review":
            print(json.dumps(review, indent=2, sort_keys=True) if args.json else format_review(review))
            return 0
        group = next((item for item in review.get("groups", []) if item.get("group_id") == args.group), None)
        if group is None:
            _err(f"reasoning group not found: {args.group}")
            return 1
        print(json.dumps(group, indent=2, sort_keys=True) if args.json else
              f"{group.get('group_id')}: {group.get('summary')}\nBasis: {group.get('overlap_basis')}\nClaims: {group.get('claim_refs')}")
        return 0
    # === status ===
    if args.command == "status":
        from auteur.status import gather_status, format_status
        status = gather_status(args.project)
        if args.json:
            print(json.dumps(status, indent=2, default=str))
        else:
            print(format_status(status, verbose=args.verbose))
        return 0
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
                    # Keep the discovery report/comparison as durable provenance;
                    # only remove unselected candidate YAML files.
                    for candidate_file in candidate_dir.glob("candidate_*.yaml"):
                        if candidate_file != args.candidate:
                            candidate_file.unlink()
                    print(f"Retained discovery provenance at {candidate_dir}")
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
                    for candidate in result["candidates"]: print(f"- {candidate['owner']}: {candidate['candidate_id']} — {candidate['status']} ({candidate['freshness']})")
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
                            print(f"Transition {transition['transition_id']}: {transition['classification']} — Owner: {transition['owner']}")
                    elif any(f["classification"] == "markerless" for f in report["findings"]):
                        print("Chapter manuscript cannot be reconciled automatically.")
                        print("Reason: No Auteur Scene or transition markers were found.")
                        consequences = report["findings"][0].get("detail", {}).get("consequences", [])
                        for consequence in consequences:
                            ids = consequence.get("scene_ids", consequence.get("transition_ids", []))
                            print(f"  - {consequence['code']}: {', '.join(ids)}")
                    else:
                        for finding in report["findings"]:
                            print(f"{finding['classification']}: {finding.get('source_section') or 'chapter'} — {finding['evidence']}")
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
                        print(f"- {proposal['proposal_type']} → {proposal.get('target_artifact_id') or 'Chapter transition'}")
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
        if args.state_command in {"status", "explain", "adopt", "accept", "archive", "affected-by"}:
            from auteur.provenance import ArtifactStore
            artifact = args.artifact
            project = _pilot_project_root(artifact)
            artifact_type = getattr(args, "artifact_type", None) or _pilot_artifact_type(artifact)
            store = ArtifactStore(project)
            if args.state_command == "affected-by":
                affected = store.impact(store._artifact_id(artifact))
                if args.json_output:
                    print(json.dumps({"artifact_id": store._artifact_id(artifact), "affected": affected}, indent=2))
                else:
                    print(f"Affected by {store._artifact_id(artifact)}:")
                    for item in affected:
                        relation = "direct" if item["direct"] else "transitive"
                        print(f"- {item['artifact_id']} ({relation}; {item['health']}/{item['freshness']}; {item['reason']})")
                return 0
            if args.state_command == "status":
                print(json.dumps(store.status(artifact, artifact_type).model_dump(mode="json"), indent=2))
                return 0
            if args.state_command == "explain":
                print(json.dumps(store.explain(artifact, artifact_type), indent=2))
                return 0
            if args.state_command == "adopt":
                store.adopt(artifact, artifact_type)
                return 0
            if args.state_command == "accept":
                if store.accept(artifact, artifact_type) is None:
                    _err("archived artifact cannot be accepted")
                    return 1
                return 0
            store.archive(artifact, artifact_type, reason=args.reason, by="author")
            return 0
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
    # Registered genre pipelines all share one command implementation.  Keep
    # the legacy branches below as compatibility handlers for existing callers.
    from auteur.genre_pipeline.registry import get_genre_pipeline
    from auteur.genre_pipeline.cli import GenrePipelineCommand
    try:
        registered_spec = get_genre_pipeline(args.command)
    except ValueError:
        registered_spec = None
    if registered_spec is not None and getattr(args, f"{registered_spec.slug}_command", None) in {"init", "resume"}:
        command_name = getattr(args, f"{registered_spec.slug}_command")
        try:
            return GenrePipelineCommand(
                project_path=args.project,
                spec=registered_spec,
                core_id=getattr(args, "core", registered_spec.default_core_id),
                mode=getattr(args, "mode", None),
                provider=getattr(args, "provider", None),
                port=args.port,
                timeout=args.timeout,
                debug=args.debug,
                resume=command_name == "resume",
                no_browser=getattr(args, "no_browser", False),
            ).run()
        except ValueError as exc:
            _err(str(exc))
            return 2


    # === ontology ===
    if args.command == "ontology":
        from auteur.narrative_ontology.cli_ontology import (
            handle_ontology_inspect,
            handle_ontology_list,
            handle_ontology_validate,
            handle_ontology_themes,
        )
        if args.ontology_command == "inspect":
            return handle_ontology_inspect(args)
        if args.ontology_command == "list":
            return handle_ontology_list(args)
        if args.ontology_command == "validate":
            return handle_ontology_validate(args)
        if args.ontology_command == "themes":
            return handle_ontology_themes(args)

    return 0

def _draft_retry(args, *, is_retry: bool) -> int:
    from auteur.llm.factory import build_client
    proj = Project.load(args.project)
    client = build_client(args.provider, args.model, agent_type="bard", blueprint=proj.blueprint)
    result = handle_retry(proj, args.chapter, args.max_iterations, client) if is_retry else \
             handle_draft(proj, args.chapter, args.max_iterations, client, regenerate_outline=getattr(args, "regenerate_outline", False))
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
