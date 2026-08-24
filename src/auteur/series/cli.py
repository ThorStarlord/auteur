from __future__ import annotations

from pathlib import Path

import yaml

from auteur.series.formatters import (
    format_series_bible_success,
    format_series_compile_success,
    format_series_diagnostics_success,
    format_series_graph_success,
    format_series_validate_success,
)
from auteur.series.handlers import (
    handle_series_bible,
    handle_series_compile,
    handle_series_diagnose,
    handle_series_graph,
    handle_series_validate,
)
from auteur.series.models import SeriesIdentity
from auteur.series.serializers import (
    serialize_series_bible,
    serialize_series_compile,
    serialize_series_diagnostics,
    serialize_series_graph,
)
from auteur.series.vertical_slice_formatters import (
    format_series_journey_focus,
    format_series_journey_map,
)
from auteur.series.vertical_slice_models import (
    BookDirection,
    RealizationCandidate,
    SeriesDirection,
)
from auteur.series.vertical_slice_service import SeriesVerticalSliceService


_CLI_AUTHOR = "author"


def register_series_subcommands(sub) -> None:
    parser = sub.add_parser("series", help="Manage whole-series narrative contracts.")
    commands = parser.add_subparsers(dest="series_command", required=True)

    p = commands.add_parser("validate", help="Validate a series_identity.yaml file.")
    p.add_argument("series", type=Path)

    p = commands.add_parser("compile", help="Compile series book plans into StoryIdentity files.")
    p.add_argument("series", type=Path)
    p.add_argument("--output", type=Path, required=True)

    p = commands.add_parser("diagnose", help="Run deterministic cross-book diagnostics.")
    p.add_argument("series", type=Path)
    p.add_argument("--output", type=Path, default=None)

    p = commands.add_parser("graph", help="Write narrative dependency graph.")
    p.add_argument("series", type=Path)
    p.add_argument("--output", type=Path, default=None)

    p = commands.add_parser("bible", help="Compile series_bible.json.")
    p.add_argument("series", type=Path)
    p.add_argument("--output", type=Path, default=None)

    journey = commands.add_parser(
        "journey", help="Guide the sparse Series vertical-slice journey."
    )
    journey_commands = journey.add_subparsers(
        dest="journey_command", required=True
    )

    p = journey_commands.add_parser(
        "propose-series", help="Create a sparse Series Direction proposal."
    )
    p.add_argument("project", type=Path)
    p.add_argument("--input", type=Path, required=True)

    p = journey_commands.add_parser(
        "accept-series", help="Accept a Series Direction proposal."
    )
    p.add_argument("project", type=Path)
    p.add_argument("proposal_id")

    p = journey_commands.add_parser(
        "propose-book", help="Create a local Book Direction proposal."
    )
    p.add_argument("project", type=Path)
    p.add_argument("--input", type=Path, required=True)

    p = journey_commands.add_parser(
        "accept-book", help="Accept a local Book Direction proposal."
    )
    p.add_argument("project", type=Path)
    p.add_argument("proposal_id")

    p = journey_commands.add_parser(
        "propose-outcome", help="Create a bounded outcome candidate."
    )
    p.add_argument("project", type=Path)
    p.add_argument("--input", type=Path, required=True)

    p = journey_commands.add_parser(
        "accept-outcome", help="Accept a bounded outcome candidate."
    )
    p.add_argument("project", type=Path)
    p.add_argument("candidate_id")

    p = journey_commands.add_parser(
        "plan-next-book", help="Explicitly enter later-Book planning."
    )
    p.add_argument("project", type=Path)
    p.add_argument("--book", type=int, required=True)

    p = journey_commands.add_parser(
        "map", help="Show established context and the next decision."
    )
    p.add_argument("project", type=Path)
    p.add_argument("--book", type=int, required=True)
    p.add_argument("--detail", action="store_true")

    p = journey_commands.add_parser(
        "focus", help="Show one recommendation and the author choices."
    )
    p.add_argument("project", type=Path)
    p.add_argument("--book", type=int, required=True)
    p.add_argument("--detail", action="store_true")

    p = journey_commands.add_parser(
        "decide", help="Record a bounded, non-authoritative workflow choice."
    )
    p.add_argument("project", type=Path)
    p.add_argument("proposal_id")
    p.add_argument("--choice", required=True)


def load_series(path: Path) -> SeriesIdentity:
    if path.is_dir():
        path = path / "series_identity.yaml"
    return SeriesIdentity.from_yaml(path)


def _load_journey_input(path: Path, model_type):
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return model_type.model_validate(payload)


def handle_series_journey_command(args) -> int:
    service = SeriesVerticalSliceService(args.project)
    try:
        if args.journey_command == "propose-series":
            proposal = service.propose_series_direction(
                _load_journey_input(args.input, SeriesDirection)
            )
            print("Series Direction proposal saved.")
            print(f"Proposal ID: {proposal.proposal_id}")
            return 0

        if args.journey_command == "accept-series":
            accepted = service.accept_series_direction(
                args.proposal_id, accepted_by=_CLI_AUTHOR
            )
            print(f"Accepted Series Direction: {accepted.direction.title}")
            return 0

        if args.journey_command == "propose-book":
            proposal = service.propose_book_direction(
                _load_journey_input(args.input, BookDirection)
            )
            print(
                f"Book {proposal.direction.book_number} Direction proposal "
                "saved."
            )
            print(f"Proposal ID: {proposal.proposal_id}")
            return 0

        if args.journey_command == "accept-book":
            accepted = service.accept_book_direction(
                args.proposal_id, accepted_by=_CLI_AUTHOR
            )
            print(
                f"Accepted Book {accepted.direction.book_number} Direction: "
                f"{accepted.direction.identity.title}"
            )
            return 0

        if args.journey_command == "propose-outcome":
            candidate = service.propose_realization(
                _load_journey_input(args.input, RealizationCandidate)
            )
            print(f"Book {candidate.book_number} outcome proposal saved.")
            print(f"Candidate ID: {candidate.candidate_id}")
            return 0

        if args.journey_command == "accept-outcome":
            accepted = service.accept_realization(
                args.candidate_id, accepted_by=_CLI_AUTHOR
            )
            print(f"Accepted Book {accepted.book_number} outcome.")
            return 0

        if args.journey_command == "plan-next-book":
            entry = service.enter_book_planning(
                args.book, entered_by=_CLI_AUTHOR
            )
            print(f"Entered exploratory planning for Book {entry.book_number}.")
            return 0

        if args.journey_command == "map":
            context = service.derive_book_context(args.book)
            decision = service.propose_next_decision(args.book)
            print(
                format_series_journey_map(
                    context, decision, detail=args.detail
                )
            )
            return 0

        if args.journey_command == "focus":
            decision = service.propose_next_decision(args.book)
            print(
                format_series_journey_focus(decision, detail=args.detail)
            )
            return 0

        if args.journey_command == "decide":
            if args.choice == "recommended":
                action = "choose_recommended"
                selected_option_id = None
            elif args.choice == "defer":
                action = "defer"
                selected_option_id = None
            else:
                action = "choose_other"
                selected_option_id = args.choice
            recorded = service.record_decision_action(
                args.proposal_id,
                action=action,
                selected_option_id=selected_option_id,
            )
            print(f"Recorded decision action: {recorded.action}")
            return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1

    return 1


def handle_series_command(args) -> int:
    if args.series_command == "journey":
        return handle_series_journey_command(args)

    try:
        series = load_series(args.series)
    except Exception as exc:
        print(f"Error: invalid series identity: {exc}")
        return 1

    if args.series_command == "validate":
        result = handle_series_validate(series)
        if not result.is_success:
            print(f"Error: {result.error}")
            return result.exit_code
        print(format_series_validate_success(str(args.series)))
        return result.exit_code

    if args.series_command == "compile":
        result = handle_series_compile(series)
        if not result.is_success:
            print(f"Error: {result.error}")
            return result.exit_code
        written = serialize_series_compile(result, args.output)
        for path in written:
            print(f"Wrote {path}")
        print(format_series_compile_success(len(written), str(args.output)))
        return result.exit_code

    if args.series_command == "diagnose":
        result = handle_series_diagnose(series)
        output = args.output or Path("series") / "diagnostics" / "series_report.json"
        serialize_series_diagnostics(result, output)
        print(format_series_diagnostics_success(str(output)))
        diagnostics = result.data.diagnostics
        return 1 if [d for d in diagnostics if getattr(d.severity, "value", d.severity) == "error"] else 0

    if args.series_command == "graph":
        result = handle_series_graph(series)
        output = args.output or Path("series") / "dependency_graph.yaml"
        serialize_series_graph(result, output)
        print(format_series_graph_success(str(output)))
        print(f"Mermaid visualization written to {output.with_suffix('.mmd')}")
        return result.exit_code

    if args.series_command == "bible":
        result = handle_series_bible(series)
        output = args.output or Path("series_bible.json")
        serialize_series_bible(result, output)
        print(format_series_bible_success(str(output)))
        return result.exit_code

    return 1
