"""Author workspace status — auteur status, the git-status equivalent for a novel.

Aggregates project health, artifact status, freshness, and reconciliation state
into a single author-facing summary. Read-only, never mutates any artifact.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _safe_nested(data: Any, *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dicts even when intermediate values are not dicts."""
    for key in keys:
        if not isinstance(data, dict):
            return default
        data = data.get(key, {})
    return data if data else default


def _read_yaml(path: Path) -> dict[str, Any] | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return None


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8")) or {}
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _artifact_status(path: Path) -> str:
    data = _read_yaml(path)
    if data is None:
        return "missing"
    lifecycle = data.get("lifecycle", "unknown")
    authority = data.get("authority", "unknown")
    if lifecycle == "accepted":
        return f"accepted (rev {data.get('revision', '?')})"
    if lifecycle in ("replaced", "archived"):
        return f"replaced (was rev {data.get('revision', '?')})"
    if lifecycle == "proposed":
        return f"proposed (rev {data.get('revision', '?')})"
    return f"{lifecycle}/{authority}"


def _chapter_status(project_root: Path, chapter_id: str) -> dict[str, Any]:
    """Gather status for a single chapter."""
    result: dict[str, Any] = {"chapter_id": chapter_id, "expression": "missing", "reconciliation": "missing", "scenes": 0}

    for chap_dir in sorted(project_root.glob("chapters/*")):
        if not chap_dir.is_dir():
            continue
        # Match by chapter_id or numeric prefix
        accepted = chap_dir / "expression" / "accepted.yaml"
        if not accepted.exists():
            continue
        data = _read_yaml(accepted)
        if data is None:
            continue
        src = data.get("source_chapter", {})
        cid = src.get("artifact_id", "")
        if cid != chapter_id and chap_dir.name != chapter_id.replace("chapter_", ""):
            continue

        result["expression"] = f"accepted (rev {data.get('revision', '?')})"

        # Scene count
        scenes = data.get("source_scenes", []) or data.get("sections", [])
        result["scenes"] = len(scenes)

        # Reconciliation status
        recon_dir = chap_dir / "expression" / "reconciliation"
        publications = sorted(recon_dir.glob("publications/*/publication.yaml")) if recon_dir.exists() else []
        if publications:
            pub = _read_yaml(publications[-1])
            if pub:
                pubid = pub.get("publication_id", "")
                completion = recon_dir / "publications" / pubid / "completion.yaml"
                comp = _read_yaml(completion)
                if comp:
                    result["reconciliation"] = f"completed ({comp.get('completion_status', '?')})"
                else:
                    result["reconciliation"] = f"published ({pubid[:16]}...)"
        else:
            inspections = sorted(recon_dir.glob("inspections/*.yaml")) if recon_dir.exists() else []
            if inspections:
                result["reconciliation"] = "inspected"
            else:
                result["reconciliation"] = "not_started"
        break

    return result


def _book_status(project_root: Path) -> dict[str, Any]:
    """Gather book expression and reconciliation status."""
    result: dict[str, Any] = {
        "expression": "missing",
        "manuscript": "missing",
        "acceptances": 0,
        "completions": 0,
        "latest_acceptance": None,
        "latest_completion": None,
    }

    # Book expression
    book_dir = project_root / "book" / "expression"
    accepted = book_dir / "accepted.yaml"
    if accepted.exists():
        data = _read_yaml(accepted)
        if data:
            rev = data.get("revision", "?")
            result["expression"] = f"accepted (rev {rev})"
            result["accepted_at"] = data.get("accepted_at", "")

    # Manuscript file
    manuscripts = sorted(book_dir.glob("book_v*.md"))
    if manuscripts:
        result["manuscript"] = f"exists ({manuscripts[-1].name})"

    # Acceptances
    acceptances_dir = project_root / ".auteur" / "book" / "expression" / "acceptances"
    if acceptances_dir.exists():
        acc_files = sorted(acceptances_dir.glob("*.yaml"))
        result["acceptances"] = len(acc_files)
        if acc_files:
            last = _read_yaml(acc_files[-1])
            if last:
                result["latest_acceptance"] = last.get("accepted_at", "")

    # Completions
    completions_dir = project_root / ".auteur" / "book" / "expression" / "completions"
    if completions_dir.exists():
        comp_files = sorted(completions_dir.glob("*.yaml"))
        result["completions"] = len(comp_files)
        if comp_files:
            last = _read_yaml(comp_files[-1])
            if last:
                result["latest_completion"] = last.get("completed_at", "")

    return result


def _reconciliation_status(project_root: Path) -> dict[str, Any]:
    """Gather Book-level reconciliation status."""
    result: dict[str, Any] = {
        "status": "not_started",
        "inspection": None,
        "publication": None,
        "acceptance": None,
        "completion": None,
    }

    # Check for book reconciliation artifacts in .auteur namespace
    book_recon = project_root / ".auteur" / "book" / "expression" / "reconciliation"
    if not book_recon.exists():
        # Legacy path
        book_recon = project_root / "book" / "expression" / "reconciliation"
        if not book_recon.exists():
            return result

    # Inspections
    inspections = sorted(book_recon.glob("inspections/*.yaml"))
    if inspections:
        result["inspection"] = inspections[-1].stem[:20]

    # Routing
    routings = sorted(book_recon.glob("routing/*.yaml"))
    if routings:
        result["routing"] = routings[-1].stem[:20]

    # Plans
    plans = sorted(book_recon.glob("plans/*.yaml"))
    if plans:
        result["plan"] = plans[-1].stem[:20]

    # Publications
    publications = sorted(book_recon.glob("publications/*/publication.yaml"))
    if publications:
        result["publication"] = publications[-1].parent.name[:20]

    # Acceptances
    acceptances = sorted(book_recon.glob("acceptances/*.yaml"))
    if acceptances:
        result["acceptance"] = acceptances[-1].stem[:32]
        result["status"] = "accepted"

    # Completions
    completions = sorted(book_recon.glob("completions/*.yaml"))
    if completions:
        result["completion"] = completions[-1].stem[:32]
        result["status"] = "completed"

    return result


def _find_blocks(project_root: Path) -> list[dict[str, str]]:
    """Identify what blocks progression through the workflow."""
    blocks: list[dict[str, str]] = []

    # Identity check
    identity_paths = [
        project_root / "story_identity.yaml",
        project_root / ".auteur" / "state" / "artifacts" / "story_identity.yaml",
    ]
    identity_ok = any(p.exists() for p in identity_paths)
    if not identity_ok:
        blocks.append({"artifact": "identity", "severity": "blocking", "message": "no accepted story identity found"})

    # Blueprint check
    bp = project_root / "blueprint.yaml"
    if not bp.exists():
        blocks.append({"artifact": "blueprint", "severity": "blocking", "message": "no blueprint.yaml found"})
    elif _read_yaml(bp) is None:
        blocks.append({"artifact": "blueprint", "severity": "error", "message": "blueprint.yaml is unparseable"})

    # Chapter expressions
    chapter_dirs = sorted(project_root.glob("chapters/*"))
    for ch in chapter_dirs:
        if not ch.is_dir():
            continue
        cid = ch.name
        a = ch / "expression" / "accepted.yaml"
        if not a.exists():
            continue
        data = _read_yaml(a)
        if data and data.get("freshness") == "stale":
            src = data.get("source_chapter", {})
            sid = src.get("artifact_id", cid)
            blocks.append({"artifact": f"chapter:{sid}", "severity": "warning", "message": f"chapter expression is stale"})

    # Book expression
    book_acc = project_root / "book" / "expression" / "accepted.yaml"
    if book_acc.exists():
        data = _read_yaml(book_acc)
        if data and data.get("freshness") == "stale":
            blocks.append({"artifact": "book", "severity": "warning", "message": "book expression is stale"})

    return blocks


def _suggest_command(project_root: Path) -> str | None:
    """Suggest the next sensible CLI command based on project state."""
    bp = project_root / "blueprint.yaml"
    if not bp.exists() or not bp.is_file():
        return "auteur init --from <story_identity.yaml> <project_path>"

    chapter_dirs = sorted(project_root.glob("chapters/*"))
    has_accepted_chapters = False
    for ch in chapter_dirs:
        a = ch / "expression" / "accepted.yaml"
        if a.exists():
            has_accepted_chapters = True
            break

    if not has_accepted_chapters:
        # Find first chapter dir
        for ch in chapter_dirs:
            if ch.is_dir():
                return f"auteur draft {project_root} {int(ch.name):d}"
        return "auteur cartographer compile <blueprint_path>"

    book_acc = project_root / "book" / "expression" / "accepted.yaml"
    if not book_acc.exists():
        chapters = [ch.name for ch in chapter_dirs if ch.is_dir()]
        ch_ids = [f"chapter_{int(ch.name):02d}" for ch in chapter_dirs if ch.is_dir()]
        if len(ch_ids) >= 2:
            return f"auteur expression compose-book {project_root} --chapter {ch_ids[0]} --chapter {ch_ids[1]} --title \"My Novel\""
        return f"auteur expression compose-book {project_root} --chapter {ch_ids[0]} --title \"My Novel\""

    # Check if book reconciliation is complete
    status = _reconciliation_status(project_root)
    if status.get("completion"):
        return None  # Everything is done
    if status.get("acceptance"):
        return f"auteur expression complete-book-reconciliation <acceptance_id> --project {project_root}"
    return f"auteur expression inspect-book-manuscript <manuscript> --against <book_id> --project {project_root}"


def gather_status(project_root: Path) -> dict[str, Any]:
    """Gather comprehensive project status. Read-only."""
    root = Path(project_root)

    # Identity
    identity_data = _read_yaml(root / "story_identity.yaml")
    if identity_data is None:
        identity_data = _read_yaml(root / ".auteur" / "state" / "artifacts" / "story_identity.yaml")
    identity_status: dict[str, Any] = {"status": "missing"}
    if identity_data:
        identity_status = {
            "status": identity_data.get("lifecycle", "present"),
            "genres": _safe_nested(identity_data, "genre", "primary", "unknown"),
            "medium": _safe_nested(identity_data, "medium", "primary", "unknown"),
            "title": identity_data.get("title", identity_data.get("working_title", "untitled")),
        }

    # Blueprint
    bp_data = _read_yaml(root / "blueprint.yaml")
    bp_lines = 0
    if bp_data:
        bp_lines = len(bp_data.get("chapters", bp_data.get("structure", {}).get("chapters", [])))
    blueprint_status: dict[str, Any] = {"status": "present" if bp_data else "missing"}
    if bp_data:
        blueprint_status["chapters"] = bp_lines

    # Structure
    diag_dir = root / "structure" / "diagnostics"
    diag_files = sorted(diag_dir.glob("*.json")) if diag_dir.exists() else []
    latest_diag = None
    if diag_files:
        d = _read_json(diag_files[-1])
        if d:
            errors = sum(1 for i in d.get("items", []) if i.get("severity") == "error")
            warnings = sum(1 for i in d.get("items", []) if i.get("severity") == "warning")
            latest_diag = {"errors": errors, "warnings": warnings, "total": len(d.get("items", []))}

    # Chapters
    chapters = []
    for ch_dir in sorted(root.glob("chapters/*")):
        if not ch_dir.is_dir():
            continue
        cid = ch_dir.name
        chapters.append(_chapter_status(root, cid))
    if not chapters:
        chapters = None

    # Book
    book = _book_status(root)

    # Reconciliation
    reconciliation = _reconciliation_status(root)

    # Blocks
    blocks = _find_blocks(root)

    # Suggested command
    suggested = _suggest_command(root)

    # Freshness overview
    stale_items = [b["artifact"] for b in blocks if b.get("severity") == "warning"]

    return {
        "project": str(root),
        "gathered_at": datetime.now(timezone.utc).isoformat(),
        "identity": identity_status,
        "blueprint": blueprint_status,
        "structure_diagnostics": latest_diag,
        "chapters": chapters,
        "book": book,
        "reconciliation": reconciliation,
        "stale": stale_items,
        "blocks": blocks,
        "suggested_command": suggested,
    }


def format_status(status: dict[str, Any], verbose: bool = False) -> str:
    """Format the status dict for human-readable terminal output."""
    lines: list[str] = []
    title = status.get("identity", {}).get("title", "Project")
    lines.append(f"Project: {title}")
    lines.append(f"  Path:    {status['project']}")

    # Identity
    id_s = status.get("identity", {})
    lines.append(f"\nIdentity:  {id_s.get('status', 'missing')}")
    if id_s.get("genres"):
        lines.append(f"  Genre:    {id_s['genres']}")
    if id_s.get("medium"):
        lines.append(f"  Medium:   {id_s['medium']}")

    # Blueprint
    bp_s = status.get("blueprint", {})
    if bp_s.get("status") == "present":
        ch_count = bp_s.get("chapters", "?")
        lines.append(f"\nBlueprint: accepted ({ch_count} chapters planned)")

    # Structure diagnostics
    diag = status.get("structure_diagnostics")
    if diag:
        lines.append(f"\nStructure: {diag['errors']} errors, {diag['warnings']} warnings ({diag['total']} total)")
    else:
        lines.append(f"\nStructure: not yet diagnosed")

    # Chapters
    chapters = status.get("chapters")
    if chapters:
        lines.append(f"\nChapters:")
        for ch in chapters:
            sc = ch.get("scenes", 0)
            expr = ch.get("expression", "missing")
            recon = ch.get("reconciliation", "not_started")
            lines.append(f"  {ch['chapter_id']}:  {expr}, {sc} scenes, reconciliation: {recon}")

    # Book
    book = status.get("book", {})
    lines.append(f"\nBook:")
    lines.append(f"  Expression: {book.get('expression', 'missing')}")
    lines.append(f"  Acceptances: {book.get('acceptances', 0)}")
    if book.get("completions"):
        lines.append(f"  Completions: {book.get('completions', 0)}")

    # Reconciliation
    recon = status.get("reconciliation", {})
    rstatus = recon.get("status", "not_started")
    lines.append(f"\nReconciliation: {rstatus}")
    if verbose and recon.get("inspection"):
        lines.append(f"  Inspection:    {recon['inspection']}")
    if verbose and recon.get("publication"):
        lines.append(f"  Publication:   {recon['publication']}")
    if verbose and recon.get("acceptance"):
        lines.append(f"  Acceptance:    {recon['acceptance']}")
    if verbose and recon.get("completion"):
        lines.append(f"  Completion:    {recon['completion']}")

    # Stale
    stale = status.get("stale", [])
    if stale:
        lines.append(f"\nStale: {', '.join(stale)}")

    # Blocks
    blocks = status.get("blocks", [])
    blocking = [b for b in blocks if b.get("severity") == "blocking"]
    warnings = [b for b in blocks if b.get("severity") == "warning"]
    if blocking:
        lines.append(f"\nBLOCKING:")
        for b in blocking:
            lines.append(f"  {b['artifact']}: {b['message']}")
    if warnings:
        lines.append(f"\nWarnings:")
        for b in warnings:
            lines.append(f"  {b['artifact']}: {b['message']}")

    # Suggested command
    cmd = status.get("suggested_command")
    if cmd:
        lines.append(f"\nSuggested next:\n  {cmd}")
    else:
        lines.append(f"\nNo suggested next command — everything looks current.")

    return "\n".join(lines)
