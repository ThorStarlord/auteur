"""Auteur CLI — parser construction: subcommands, flags, and argparse wiring."""

from __future__ import annotations

import argparse
from pathlib import Path


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


class _HideSuppressedFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        if action.help == argparse.SUPPRESS: return ""
        return super()._format_action(action)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argparse parser with all subcommands."""
    parser = argparse.ArgumentParser(prog="auteur",
        description="Agentic narrative engineering toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status", help="Show project health summary (like git status for a novel).")
    p.add_argument("--project", type=Path, default=Path("."), help="Project root directory (default: current directory).")
    p.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text.")
    p.add_argument("--verbose", action="store_true", help="Show detailed artifact IDs.")

    p = sub.add_parser("publish", help="Render accepted Book to HTML, EPUB, or other formats.")
    p.add_argument("--project", type=Path, default=Path("."), help="Project root directory (default: current directory).")
    p.add_argument("--format", default="html", help="Output format(s): html, epub, or comma-separated (default: html).")
    p.add_argument("--output", type=Path, default=None, help="Output file path (derived from project name if omitted).")
    p.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: project root).")
    p.add_argument("--css", type=Path, default=None, help="Path to custom CSS file for HTML/EPUB styling.")
    p.add_argument("--no-title-page", action="store_true", help="Omit title page from HTML output.")
    p.add_argument("--no-toc", action="store_true", help="Omit table of contents from HTML output.")

    p = sub.add_parser("init", help="Create a new project directory.")
    p.add_argument("path", type=Path)
    p.add_argument("--from", dest="blueprint_path", type=Path, required=True)
    p.add_argument("--force", action="store_true",
        help="Re-initialize an existing auteur project directory.")

    # Plan command is now a subcommand group registered by planning.cli
    from auteur.planning.cli import register_plan_subcommands
    register_plan_subcommands(sub)

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

    p = ss.add_parser("propose",
        help="Generate chapter structure proposals from diagnostics.")
    p.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory.")
    p.add_argument("--apply", type=str, default=None,
        help="Proposal ID to apply.")
    p.add_argument("--list", action="store_true",
        help="List pending proposals.")
    p.add_argument("--json", action="store_true",
        help="Output as JSON.")
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
    p = ss.add_parser("publish",
        help="Publish chapter structure artifacts as a standalone document.")
    p.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory.")
    p.add_argument("--output", type=Path, default=None,
        help="Output path for the published document.")
    p.add_argument("--format", choices=["yaml", "md"], default="md",
        help="Output format (default: markdown).")
    p = sub.add_parser("scene", help="Manage scene realization artifacts.")
    scs = p.add_subparsers(dest="scene_command", required=True)
    p = scs.add_parser("publish",
        help="Publish scene realization artifacts as a standalone document.")
    p.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory.")
    p.add_argument("--output", type=Path, default=None,
        help="Output path for the published document.")
    p.add_argument("--format", choices=["yaml", "md"], default="md",
        help="Output format (default: markdown).")
    p = sub.add_parser("reasoning", help="Inspect derived reasoning reviews and run book-level analysis.")
    rs = p.add_subparsers(dest="reasoning_command", required=True)
    p = rs.add_parser("review", help="Show an author-facing derived reasoning review.")
    p.add_argument("review", type=Path)
    p.add_argument("--json", action="store_true", help="Show the complete derived review JSON.")
    p = rs.add_parser("inspect", help="Inspect one derived review group.")
    p.add_argument("review", type=Path)
    p.add_argument("group")
    p.add_argument("--json", action="store_true", help="Show the complete group JSON.")
    p = rs.add_parser("book", help="Run deterministic Book Manuscript reasoning analysis.")
    p.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory (default: current directory).")
    p.add_argument("--json", action="store_true",
        help="Output as JSON.")
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
    p = bs.add_parser("publish",
        help="Publish a blueprint as a standalone human-readable document.")
    p.add_argument("blueprint", type=Path,
        help="Path to blueprint.yaml.")
    p.add_argument("--output", type=Path, default=None,
        help="Output path (default: <blueprint_dir>/published/).")
    p.add_argument("--format", choices=["yaml", "md"], default="md",
        help="Output format (default: markdown).")
    from auteur.genre_builder.cli import register_genre_builder_subcommands
    register_genre_builder_subcommands(sub)

    p = sub.add_parser("dashboard",
        help="Show a unified author dashboard with status, lifecycle, and alerts.")
    p.add_argument("--project", type=Path, default=Path("."),
        help="Project root directory (default: current directory).")
    p.add_argument("--json", action="store_true",
        help="Output as JSON.")

    from auteur.series.cli import register_series_subcommands
    register_series_subcommands(sub)
    from auteur.relations.cli import register_relations_subcommands
    register_relations_subcommands(sub)
    from auteur.roundtrip.cli import register_roundtrip_subcommands
    register_roundtrip_subcommands(sub)
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

    from auteur.expression.cli import register_expression_subcommands
    register_expression_subcommands(sub)

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

    from auteur.workflow.cli import register_workflow_subcommands
    register_workflow_subcommands(sub)

    from auteur.impact.cli import register_impact_subcommands
    register_impact_subcommands(sub)

    from auteur.convergence.cli import register_realization_subcommands
    register_realization_subcommands(sub)

    from auteur.decision.cli import register_decision_subcommands
    register_decision_subcommands(sub)

    from auteur.review.cli import register_review_subcommands
    register_review_subcommands(sub)

    from auteur.simulation.cli import register_simulate_subcommands
    register_simulate_subcommands(sub)

    from auteur.portfolio.cli import register_portfolio_subcommands
    register_portfolio_subcommands(sub)

    from auteur.commitment.cli import register_commit_subcommands
    register_commit_subcommands(sub)

    from auteur.lifecycle.cli import register_lifecycle_subcommands
    register_lifecycle_subcommands(sub)

    from auteur.notify.cli import register_notify_subcommands
    register_notify_subcommands(sub)

    return parser
