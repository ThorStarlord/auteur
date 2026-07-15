"""Deterministic synthesis of independent reasoning reports."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def _id(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()[:16]


def _finding_key(report: Mapping[str, Any], finding: Mapping[str, Any]) -> str:
    return str(finding.get("rule") or finding.get("source") or finding.get("statement") or report.get("critic_id"))


def synthesize_reports(
    reports: Sequence[Mapping[str, Any]],
    *,
    report_dir: Path | None = None,
    current_inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build and optionally persist a derived review without mutating inputs."""
    source_reports = [{"report_id": report.get("report_id"),
                       "critic_id": report.get("critic_id"),
                       "critic_version": report.get("critic_version")}
                      for report in reports]
    stale = []
    for report in reports:
        expected = report.get("source_snapshot", {})
        if current_inputs is not None:
            current = {key: value.get("revision") if isinstance(value, Mapping) else None
                       for key, value in sorted(current_inputs.items())}
            if expected != current:
                stale.append(report.get("report_id"))
    groups: dict[str, list[dict[str, Any]]] = {}
    for report in reports:
        for claim in report.get("claims", []):
            key = _finding_key(report, claim)
            groups.setdefault(key, []).append({"report_id": report.get("report_id"),
                                               "critic_id": report.get("critic_id"),
                                               "claim": claim})
    group_items = []
    for index, (key, claims) in enumerate(sorted(groups.items()), 1):
        statements = {item["claim"].get("statement") for item in claims}
        conflict = len(statements) > 1
        group_items.append({
            "group_id": f"group-{index}",
            "claim_refs": [{"report_id": item["report_id"], "claim_id": item["claim"].get("claim_id")} for item in claims],
            "overlap_basis": f"shared reasoning key: {key}",
            "summary": next(iter(statements)) if len(statements) == 1 else "Conflicting claims require author review.",
            "conflict": conflict,
            "evidence_count": sum(len(report.get("evidence", [])) for report in reports
                                   if report.get("report_id") in {item["report_id"] for item in claims}),
        })
    conflicts = [{"conflict_id": f"conflict-{i}", "claim_refs": group["claim_refs"],
                  "conflict_type": "claim_statement_disagreement",
                  "explanation": "Source critics make different claims for the same reasoning key."}
                 for i, group in enumerate((g for g in group_items if g["conflict"]), 1)]
    priorities = [{"group_id": group["group_id"], "rank": i,
                   "rank_basis": "declared report evidence count; confidence methods not combined"}
                  for i, group in enumerate(sorted(group_items, key=lambda item: (-item["evidence_count"], item["group_id"])), 1)]
    review = {
        "review_id": _id([report.get("report_id") for report in reports]),
        "artifact_type": "reasoning_review",
        "source_reports": source_reports,
        "groups": group_items,
        "conflicts": conflicts,
        "priorities": priorities,
        "recommendations": [],
        "confidence": {"method": "not_combined", "explanation": "Source confidence methods remain separate."},
        "freshness": {"status": "stale" if stale else "fresh", "stale_reports": stale},
        "status": "derived",
    }
    if report_dir is not None:
        path = Path(report_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / f"{review['review_id']}.json").write_text(json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return review
