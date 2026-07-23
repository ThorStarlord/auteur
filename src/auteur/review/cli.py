"""CLI for Author Review Sessions."""

from __future__ import annotations

import json as _json
import sys
from pathlib import Path

from auteur.review.service import ReviewService


def register_review_subcommands(sub) -> None:
    """Register review subcommands under 'review'."""
    p = sub.add_parser("review", help="Author Review Sessions — review decisions, make choices, accept candidates.")
    rs = p.add_subparsers(dest="review_command", required=True)

    p_start = rs.add_parser("start", help="Start a new review session or resume existing.")
    p_start.add_argument("--decision", type=str, default=None, help="Explicit decision ID to review.")
    p_start.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_start.add_argument("--json", action="store_true", help="Output JSON.")

    p_status = rs.add_parser("status", help="Show current review session status.")
    p_status.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_status.add_argument("--json", action="store_true", help="Output JSON.")

    p_inspect = rs.add_parser("inspect", help="Inspect a review session.")
    p_inspect.add_argument("session_id", type=str, help="Session ID.")
    p_inspect.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_inspect.add_argument("--json", action="store_true", help="Output JSON.")
    p_inspect.add_argument("--events", action="store_true", help="Show events.")

    p_choose = rs.add_parser("choose", help="Record an author choice.")
    p_choose.add_argument("session_id", type=str, help="Session ID.")
    p_choose.add_argument("--choice", type=str, required=True, help="Choice ID.")
    p_choose.add_argument("--option", type=str, required=True, help="Selected option.")
    p_choose.add_argument("--reason", type=str, default="", help="Rationale.")
    p_choose.add_argument("--supersede", type=str, default=None, help="Choice ID to supersede.")
    p_choose.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_choose.add_argument("--json", action="store_true", help="Output JSON.")

    p_prepare = rs.add_parser("prepare", help="Prepare acceptance for a candidate.")
    p_prepare.add_argument("session_id", type=str, help="Session ID.")
    p_prepare.add_argument("--candidate", type=str, required=True, help="Candidate ID.")
    p_prepare.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_prepare.add_argument("--json", action="store_true", help="Output JSON.")

    p_accept = rs.add_parser("accept", help="Perform authority-bearing acceptance.")
    p_accept.add_argument("session_id", type=str, help="Session ID.")
    p_accept.add_argument("--candidate", type=str, required=True, help="Candidate ID.")
    p_accept.add_argument("--confirm", action="store_true", help="Confirm acceptance.")
    p_accept.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_accept.add_argument("--json", action="store_true", help="Output JSON.")

    p_resume = rs.add_parser("resume", help="Resume an existing session.")
    p_resume.add_argument("session_id", type=str, help="Session ID.")
    p_resume.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_resume.add_argument("--json", action="store_true", help="Output JSON.")

    p_history = rs.add_parser("history", help="Show session event history.")
    p_history.add_argument("session_id", type=str, help="Session ID.")
    p_history.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_history.add_argument("--json", action="store_true", help="Output JSON.")

    p_list = rs.add_parser("list", help="List all review sessions.")
    p_list.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_list.add_argument("--json", action="store_true", help="Output JSON.")

    p_abort = rs.add_parser("abort", help="Abort an active session.")
    p_abort.add_argument("session_id", type=str, help="Session ID.")
    p_abort.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p_abort.add_argument("--json", action="store_true", help="Output JSON.")


def dispatch_review(args) -> int:
    """Dispatch to the appropriate review handler."""
    handlers = {
        "start": _handle_start,
        "status": _handle_status,
        "inspect": _handle_inspect,
        "choose": _handle_choose,
        "prepare": _handle_prepare,
        "accept": _handle_accept,
        "resume": _handle_resume,
        "history": _handle_history,
        "list": _handle_list,
        "abort": _handle_abort,
    }
    handler = handlers.get(args.review_command)
    if handler is None:
        print(f"Error: Unknown review command: {args.review_command}", file=sys.stderr)
        return 1
    return handler(args)


def _get_service(args) -> ReviewService:
    if not args.project.exists():
        print(f"Error: Project directory not found: {args.project}", file=sys.stderr)
        raise SystemExit(1)
    return ReviewService(args.project)


def _handle_start(args) -> int:
    try:
        service = _get_service(args)
        session = service.start(decision_id=args.decision)
        if args.json:
            print(_json.dumps(_session_to_dict(session), indent=2, default=str))
        else:
            print(f"Review session started: {session.session_id[:16]}...")
            print(f"  Decision: {session.target.decision_id if session.target else 'N/A'}")
            print(f"  State: {session.state.value}")
            if session.target:
                print(f"  Reason: {session.target.selection_reason}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_status(args) -> int:
    try:
        service = _get_service(args)
        status = service.status()
        if args.json:
            print(_json.dumps(status, indent=2, default=str))
        else:
            print(f"Review Status — {status['total_sessions']} total sessions")
            if status.get("active_session"):
                a = status["active_session"]
                print(f"  Active: {a['session_id'][:16]}... ({a['state']})")
                print(f"  Decision: {a['decision_id']}")
            else:
                print("  No active session")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_inspect(args) -> int:
    try:
        service = _get_service(args)
        session = service.inspect(args.session_id)
        if args.json:
            d = _session_to_dict(session)
            if args.events:
                d["events"] = [_event_to_dict(e) for e in session.events]
            print(_json.dumps(d, indent=2, default=str))
        else:
            print(f"Session: {session.session_id[:16]}...")
            print(f"  State: {session.state.value}")
            if session.target:
                print(f"  Decision: {session.target.decision_id}")
                print(f"  Target: {session.target.target_artifact_id}")
                print(f"  Chapter: {session.target.chapter_index}")
                print(f"  Reason: {session.target.selection_reason}")
            print(f"  Choices: {len(session.choices)}")
            for c in session.choices:
                status = f"→ {c.selected_option}" if c.selected_option else "(open)"
                print(f"    - {c.choice_id[:12]}... {c.question[:60]}: {status}")
            if session.preparation:
                prep_status = "READY" if session.preparation.prepared else "BLOCKED"
                print(f"  Preparation: {prep_status}")
                if session.preparation.blockers:
                    for b in session.preparation.blockers:
                        print(f"    - {b}")
            if session.acceptance:
                print(f"  Acceptance: {'✓' if session.acceptance.accepted else 'FAILED'} {session.acceptance.acceptance_id[:16] if session.acceptance.acceptance_id else ''}")
            if session.impact_refresh:
                print(f"  Impact refresh: {'✓' if session.impact_refresh.refreshed else 'FAILED'}")
            if session.error_info:
                print(f"  Error: {session.error_info}")
            print(f"  Events: {session.event_count}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_choose(args) -> int:
    try:
        service = _get_service(args)
        session = service.record_choice(
            args.session_id, args.choice, args.option,
            rationale=args.reason, supersede=args.supersede,
        )
        if args.json:
            print(_json.dumps(_session_to_dict(session), indent=2, default=str))
        else:
            print(f"Choice recorded: {args.choice[:16]}... → {args.option}")
            print(f"  Session state: {session.state.value}")
            remaining = [c for c in session.choices if c.selected_option is None]
            if remaining:
                print(f"  Remaining choices: {len(remaining)}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_prepare(args) -> int:
    try:
        service = _get_service(args)
        session = service.prepare_acceptance(args.session_id, args.candidate)
        if args.json:
            print(_json.dumps(_session_to_dict(session), indent=2, default=str))
        else:
            if session.preparation and session.preparation.prepared:
                print(f"Acceptance prepared: {args.candidate}")
                print(f"  Session state: {session.state.value}")
                print("  Run 'auteur review accept' to proceed.")
            else:
                print(f"Acceptance blocked for {args.candidate}")
                if session.preparation:
                    for b in session.preparation.blockers:
                        print(f"  - {b}")
                return 1
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_accept(args) -> int:
    try:
        service = _get_service(args)
        session = service.accept(args.session_id, args.candidate, confirm=args.confirm)
        if args.json:
            print(_json.dumps(_session_to_dict(session), indent=2, default=str))
        else:
            if session.acceptance and session.acceptance.accepted:
                print(f"Acceptance completed: {args.candidate}")
                print(f"  Acceptance ID: {session.acceptance.acceptance_id[:16]}...")
                print(f"  Session state: {session.state.value}")
            else:
                error = session.acceptance.error if session.acceptance else "unknown"
                print(f"Acceptance failed: {error}")
                return 1
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_resume(args) -> int:
    try:
        service = _get_service(args)
        session = service.resume(args.session_id)
        if args.json:
            print(_json.dumps(_session_to_dict(session), indent=2, default=str))
        else:
            if session.state == ReviewSessionState.STALE:
                print(f"Session {args.session_id[:16]}... is stale.")
                print(f"  Reason: {session.error_info}")
                print("  Start a new session to review the current state.")
                return 1
            print(f"Session resumed: {args.session_id[:16]}...")
            print(f"  State: {session.state.value}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_history(args) -> int:
    try:
        service = _get_service(args)
        events = service.history(args.session_id)
        if args.json:
            print(_json.dumps([_event_to_dict(e) for e in events], indent=2, default=str))
        else:
            print(f"Session History — {args.session_id[:16]}... ({len(events)} events)")
            for i, e in enumerate(events, 1):
                print(f"  {i:3d}. [{e.event_type.value}] {e.timestamp[:19]}")
                if e.payload:
                    for k, v in e.payload.items():
                        print(f"       {k}={v}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_list(args) -> int:
    try:
        service = _get_service(args)
        sessions = service.list_sessions()
        if args.json:
            print(_json.dumps([{
                "session_id": s.session_id,
                "decision_id": s.decision_id,
                "state": s.state.value,
                "target_artifact_id": s.target_artifact_id,
                "chapter_index": s.chapter_index,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            } for s in sessions], indent=2, default=str))
        else:
            if not sessions:
                print("No review sessions")
            else:
                print(f"Sessions ({len(sessions)}):")
                for s in sessions:
                    print(f"  {s.session_id[:16]}... {s.state.value:20s} "
                          f"ch{s.chapter_index} {s.decision_id[:16]}...")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_abort(args) -> int:
    try:
        service = _get_service(args)
        session = service.abort(args.session_id)
        if args.json:
            print(_json.dumps(_session_to_dict(session), indent=2, default=str))
        else:
            print(f"Session aborted: {args.session_id[:16]}...")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _session_to_dict(session: ReviewSession) -> dict[str, Any]:
    from auteur.review.models import ReviewSession, ReviewSessionState
    return {
        "session_id": session.session_id,
        "project": session.project,
        "state": session.state.value,
        "target": {
            "decision_id": session.target.decision_id,
            "target_artifact_id": session.target.target_artifact_id,
            "chapter_index": session.target.chapter_index,
            "selection_reason": session.target.selection_reason,
        } if session.target else None,
        "choices": [
            {
                "choice_id": c.choice_id,
                "question": c.question,
                "selected_option": c.selected_option,
                "rationale": c.rationale,
            }
            for c in session.choices
        ],
        "preparation": {
            "prepared": session.preparation.prepared,
            "blockers": session.preparation.blockers,
            "candidate_id": session.preparation.candidate_id,
        } if session.preparation else None,
        "acceptance": {
            "accepted": session.acceptance.accepted,
            "acceptance_id": session.acceptance.acceptance_id,
            "candidate_id": session.acceptance.candidate_id,
        } if session.acceptance else None,
        "impact_refresh": {
            "refreshed": session.impact_refresh.refreshed,
            "affected_artifacts": session.impact_refresh.affected_artifacts,
        } if session.impact_refresh else None,
        "event_count": session.event_count,
        "error_info": session.error_info,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


def _event_to_dict(event: ReviewEvent) -> dict[str, Any]:
    from auteur.review.models import ReviewEvent
    return {
        "event_id": event.event_id,
        "sequence": event.sequence,
        "event_type": event.event_type.value,
        "timestamp": event.timestamp,
        "actor": event.actor,
        "payload": event.payload,
        "event_hash": event.event_hash,
    }
