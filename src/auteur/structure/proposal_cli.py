"""Explicit review and selection for noncanonical Structure proposals."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

import yaml

from auteur.story_design_packs.models import source_fingerprint
from auteur.story_design_packs.session import TutorSessionStore
from auteur.structure.proposal_models import StructureProposal


_AUTHORITY = "NONCANONICAL PROPOSAL / NOT APPLIED"


def parse_proposal_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="auteur structure proposal")
    sub = parser.add_subparsers(dest="proposal_command", required=True)

    inspect = sub.add_parser("inspect", help="Inspect one noncanonical Structure proposal.")
    inspect.add_argument("proposal", type=Path)
    inspect.add_argument("--project", type=Path, default=Path("."))
    inspect.add_argument("--json", action="store_true")

    select = sub.add_parser("select", help="Select one proposal option without applying it.")
    select.add_argument("proposal", type=Path)
    select.add_argument("--option", required=True)
    select.add_argument("--author", default=None)
    select.add_argument("--project", type=Path, default=Path("."))
    select.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def _path(project: Path, proposal: Path) -> tuple[Path, Path]:
    root = project.resolve()
    path = proposal.resolve() if proposal.is_absolute() else (root / proposal).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Structure proposal path must stay inside the selected project")
    if not path.is_file():
        raise ValueError(f"Structure proposal not found: {proposal}")
    return root, path


def _load(path: Path) -> StructureProposal:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return StructureProposal.model_validate(raw)
    except Exception as exc:
        raise ValueError(f"Invalid Structure proposal {path}: {exc}") from exc


def _tutor_current(project: Path, proposal: StructureProposal) -> bool | None:
    rule = proposal.source_rule or ""
    if not rule.startswith("tutor_session:"):
        return None
    parts = rule.split(":", 2)
    if len(parts) != 3:
        return False
    session_id = parts[1]
    try:
        session = TutorSessionStore(project).load(session_id)
    except Exception:
        return False
    if session.status == "stale":
        return False
    current: dict[str, str] = {}
    for key in sorted(session.source_fingerprints):
        if "=" not in key:
            return False
        _name, raw = key.split("=", 1)
        source = (project / raw).resolve()
        if not source.is_relative_to(project) or not source.is_file():
            return False
        current[key] = source_fingerprint(source.read_bytes())
    if current != session.source_fingerprints:
        return False
    digest = hashlib.sha256(
        json.dumps(current, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return digest == parts[2]


def _relative(project: Path, path: Path) -> str:
    return path.relative_to(project).as_posix()


def _payload(project: Path, path: Path, proposal: StructureProposal) -> dict[str, object]:
    selected = proposal.selection.selected_option_id or None
    accepted = bool(
        selected
        and proposal.decision is not None
        and proposal.decision.status == "accepted"
        and proposal.decision.selected_option_id == selected
    )
    rel = _relative(project, path)
    return {
        "proposal_id": proposal.proposal_id,
        "proposal_path": rel,
        "summary": proposal.summary,
        "source_rule": proposal.source_rule,
        "source_domain": proposal.source_domain,
        "options": [
            {
                "id": option.id,
                "summary": option.summary,
                "tradeoffs": option.tradeoffs,
                "data": option.data,
            }
            for option in proposal.options
        ],
        "selected_option_id": selected,
        "decision": proposal.decision.model_dump(mode="json") if proposal.decision else None,
        "source_current": _tutor_current(project, proposal),
        "authority_status": _AUTHORITY,
        "mutates_story": False,
        "ready_for_revision_plan": accepted,
        "select_command": (
            None if accepted else f"auteur structure proposal select {rel} --option <OPTION_ID> --project ."
        ),
        "next_command": (
            f"auteur structure revision plan --proposal {rel} --project ." if accepted else None
        ),
    }


def _atomic_save(path: Path, proposal: StructureProposal) -> None:
    rendered = yaml.safe_dump(
        proposal.model_dump(mode="json"), sort_keys=False, allow_unicode=True
    )
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _print_human(data: dict[str, object]) -> None:
    print(f"Proposal: {data['proposal_id']}")
    print(f"Status: {data['authority_status']}")
    print(f"Summary: {data['summary']}")
    print("Options:")
    for option in data["options"]:  # type: ignore[union-attr]
        marker = "*" if option["id"] == data["selected_option_id"] else "-"
        print(f"  {marker} {option['id']}: {option['summary']}")
        print(f"    Tradeoffs: {option['tradeoffs']}")
    if data["source_current"] is False:
        print("Source currentness: STALE / UNRESOLVED")
    if data["next_command"]:
        print(f"Next authoritative workflow: {data['next_command']}")
    elif data["select_command"]:
        print(f"Selection command: {data['select_command']}")
    print("No accepted story artifact was changed by this review/selection step.")


def dispatch_proposal_argv(argv: list[str]) -> int:
    args = parse_proposal_args(argv)
    try:
        project, path = _path(args.project, args.proposal)
        proposal = _load(path)
        if args.proposal_command == "select":
            current = _tutor_current(project, proposal)
            if current is False:
                raise ValueError("Tutor-generated Structure proposal is stale; regenerate it before selection")
            existing = proposal.selection.selected_option_id
            if existing:
                if existing != args.option:
                    raise ValueError("Structure proposal is already selected; selection history is not overwritten")
            else:
                proposal.accept(args.option, author=args.author)
                _atomic_save(path, proposal)
        data = _payload(project, path, proposal)
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=__import__("sys").stderr)
        return 1

    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        _print_human(data)
    return 0
