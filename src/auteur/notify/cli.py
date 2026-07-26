"""CLI for Author Notification (v0.18.0)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def register_notify_subcommands(sub) -> None:
    p = sub.add_parser("notify", help="Author Notification — scan for events needing attention.")
    p.add_argument("--project", type=Path, default=Path("."), help="Project root directory.")
    p.add_argument("--json", action="store_true", help="Output JSON.")


def _get_service(args) -> Any:
    from auteur.notify.service import NotificationService
    return NotificationService(args.project)


def dispatch_notify(args) -> int:
    try:
        svc = _get_service(args)
        findings = svc.scan()
        if args.json:
            print(json.dumps([f.to_dict() for f in findings], indent=2, default=str))
        else:
            if not findings:
                print("No notifications. All subsystems are in good shape.")
                return 0
            print(f"Notifications ({len(findings)}):")
            print("")
            for f in findings:
                sev = {"info": "ℹ", "warning": "⚠", "blocking": "🚫"}.get(f.severity.value, "·")
                print(f"  [{sev}] {f.title}")
                print(f"       {f.subsystem}: {f.description[:80]}")
                if f.command:
                    print(f"       → {f.command}")
                print("")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
