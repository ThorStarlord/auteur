"""Read-only author-facing commands for derived reasoning reviews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def format_review(review: dict[str, Any]) -> str:
    lines = [f"Reasoning review {review.get('review_id', '(unnamed)')}",
             f"Status: {review.get('freshness', {}).get('status', 'unknown')}"]
    stale = review.get("freshness", {}).get("stale_reports", [])
    if stale:
        lines.append(f"Stale reports: {', '.join(stale)}")
    lines.append("Top concerns:")
    for item in sorted(review.get("priorities", []), key=lambda value: value.get("rank", 0)):
        group = next((candidate for candidate in review.get("groups", [])
                      if candidate.get("group_id") == item.get("group_id")), None)
        if group is None:
            continue
        marker = "CONFLICT" if group.get("conflict") else ""
        affected = f" [{', '.join(group.get('affected_artifacts', []))}]" if group.get("affected_artifacts") else ""
        lines.append(f"  {item.get('rank')}. {group.get('summary')} {marker}{affected}".rstrip())
        lines.append(f"     Next: {group.get('next_action', 'Inspect the source reasoning.')}")
    lines.append(f"Source reports: {len(review.get('source_reports', []))}")
    lines.append("Use --json for provenance and full claim references.")
    return "\n".join(lines)


def load_review(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
