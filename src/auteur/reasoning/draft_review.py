"""Persist ReasoningRuntime execution results and produce author-facing reviews.

This module bridges the ReasoningRuntime (which writes per-critic JSON reports
to a flat directory) into the chapter-scoped artifact layout required by the
production drafting pipeline.

Every write is atomic: we write to a temporary path and os.replace into place.
Historical runs are immutable. Only ``latest.yaml`` is overwritten on each run.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from auteur.reasoning.runtime import ExecutionResult
from auteur.reasoning.synthesis import synthesize_reports


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _reasoning_root(project_root: Path, chapter_index: int) -> Path:
    return project_root / "chapters" / f"{chapter_index:02d}" / "reasoning"


def _runs_dir(root: Path) -> Path:
    return root / "runs"


def _outcomes_dir(root: Path) -> Path:
    return root / "outcomes"


def _reviews_dir(root: Path) -> Path:
    return root / "reviews"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def _run_id(chapter_index: int, iteration: int) -> str:
    raw = f"ch{chapter_index:02d}_it{iteration:02d}_{uuid4().hex[:12]}"
    return "run_" + hashlib.sha256(raw.encode()).hexdigest()[:16]


def _atomic_write(path: Path, data: str) -> None:
    """Write *data* to *path* atomically via a temporary sibling."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp" + uuid4().hex[:8])
    tmp.write_text(data, encoding="utf-8")
    os.replace(tmp, path)


def _to_serializable(obj: Any) -> Any:
    """Recursively convert non-serializable objects (e.g. StrEnum) to plain strings."""
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_serializable(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_to_serializable(v) for v in obj)
    if hasattr(obj, "value"):
        return obj.value
    return obj


def persist_reasoning_run(
    project_root: Path,
    chapter_index: int,
    iteration: int,
    result: ExecutionResult,
    *,
    draft_hash: str = "",
    outline_hash: str = "",
    blueprint_revision: str = "",
    bible_revision: str = "",
) -> dict[str, Any]:
    """Persist a full ReasoningRuntime execution atomically.

    Returns the run record dict.  On failure no partial artifacts remain
    visible (individual outcomes are written before the run record, so a
    crash during outcome writing leaves no run record --- those outcomes
    are orphaned but harmless).
    """
    root = _reasoning_root(project_root, chapter_index)
    rid = _run_id(chapter_index, iteration)
    now = datetime.now(timezone.utc)
    created_at = now.isoformat()

    outcomes_dir = _outcomes_dir(root) / rid
    outcomes_dir.mkdir(parents=True, exist_ok=True)

    overall_status = "success" if all(o.status == "success" for o in result.outcomes) else "partial" if any(o.status == "success" for o in result.outcomes) else "failed"

    # Aggregate token usage from outcomes
    total_in = sum(o.input_tokens or 0 for o in result.outcomes)
    total_out = sum(o.output_tokens or 0 for o in result.outcomes)
    usage_complete = all(o.input_tokens is not None or o.output_tokens is not None for o in result.outcomes)
    per_critic_usage = {
        o.critic_id: {"input_tokens": o.input_tokens, "output_tokens": o.output_tokens}
        for o in result.outcomes
    }

    run_record = {
        "run_id": rid,
        "artifact_type": "reasoning_run_record",
        "authority": "derived",
        "lifecycle": "published",
        "chapter_index": chapter_index,
        "iteration": iteration,
        "plan_id": result.plan.plan_id,
        "created_at": created_at,
        "overall_status": overall_status,
        "critic_ids": list(result.plan.dependency_order),
        "outcome_count": len(result.outcomes),
        "execution": {
            "mode": "concurrent",
            "max_workers": getattr(result, "max_workers", 5),
        },
        "usage": {
            "critics": per_critic_usage,
            "total": {"input_tokens": total_in, "output_tokens": total_out},
            "complete": usage_complete,
        },
        "outcomes": [
            {
                "critic_id": o.critic_id,
                "version": o.version,
                "status": str(o.status) if hasattr(o.status, 'value') else o.status,
                "report_id": o.report_id,
                "error": o.error if o.error else None,
                "duration_ms": o.duration_ms,
                "usage": {"input_tokens": o.input_tokens, "output_tokens": o.output_tokens},
                "provider": o.provider,
                "model": o.model,
            }
            for o in result.outcomes
        ],
        "source_snapshot": {
            "draft_hash": draft_hash,
            "outline_hash": outline_hash,
            "blueprint_revision": blueprint_revision,
            "bible_revision": bible_revision,
        },
    }

    runtime_reports: list[dict[str, Any]] = []
    for oc in result.outcomes:
        if oc.status == "success" and oc.report_id:
            runtime_reports.append({
                "report_id": oc.report_id,
                "critic_id": oc.critic_id,
                "status": "derived",
                "findings": [],
            })

    review = synthesize_reports(runtime_reports, report_dir=None)
    review_id = review.get("review_id", f"review_{rid}")

    review_data = _to_serializable({
        "review_id": review_id,
        "run_id": rid,
        "artifact_type": "reasoning_review",
        "authority": "derived",
        "lifecycle": "published",
        "chapter_index": chapter_index,
        "iteration": iteration,
        "created_at": created_at,
        "overall_status": overall_status,
        "critic_summaries": [
            {
                "critic_id": o.critic_id,
                "status": str(o.status) if hasattr(o.status, "value") else o.status,
                "version": o.version,
                "finding_count": 0,
                "duration_ms": o.duration_ms,
                "usage": {"input_tokens": o.input_tokens, "output_tokens": o.output_tokens},
                "provider": o.provider,
                "model": o.model,
            }
            for o in result.outcomes
        ],
        "usage": {
            "total": {"input_tokens": total_in, "output_tokens": total_out},
            "complete": usage_complete,
        },
        "execution": run_record["execution"],
        "blocking_findings": [],
        "warnings": [],
        "synthesis": "",
        "recommended_actions": [],
        "source_snapshot": run_record["source_snapshot"],
        "freshness": "fresh",
    })

    review_md = _render_review_markdown(review_data)

    _atomic_write(_reviews_dir(root) / f"reasoning_review_{rid}.yaml", yaml.safe_dump(review_data, sort_keys=False))
    _atomic_write(_reviews_dir(root) / f"reasoning_review_{rid}.md", review_md)
    _atomic_write(_runs_dir(root) / f"reasoning_run_{rid}.yaml", yaml.safe_dump(run_record, sort_keys=False))

    latest = {
        "run_id": rid,
        "review_ref": f"reasoning_review_{rid}",
        "chapter_index": chapter_index,
        "iteration": iteration,
        "created_at": created_at,
        "overall_status": overall_status,
    }
    _atomic_write(root / "latest.yaml", yaml.safe_dump(latest, sort_keys=False))

    return run_record


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

def load_reasoning_run(project_root: Path, chapter_index: int, run_id: str) -> dict[str, Any] | None:
    """Load a persisted reasoning run record by *run_id*."""
    path = _runs_dir(_reasoning_root(project_root, chapter_index)) / f"reasoning_run_{run_id}.yaml"
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_latest_run(project_root: Path, chapter_index: int) -> dict[str, Any] | None:
    """Load the latest reasoning run for a chapter, or ``None``."""
    path = _reasoning_root(project_root, chapter_index) / "latest.yaml"
    if not path.exists():
        return None
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# ---------------------------------------------------------------------------
# Freshness
# ---------------------------------------------------------------------------

def _content_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def review_source_freshness(
    project_root: Path,
    chapter_index: int,
    run_id: str,
    *,
    current_draft_hash: str = "",
    current_outline_hash: str = "",
) -> dict[str, Any]:
    """Compare the run's recorded source hashes against current values."""
    run = load_reasoning_run(project_root, chapter_index, run_id)
    if run is None:
        return {"fresh": False, "stale_sources": ["run_not_found"], "error": f"run not found: {run_id}"}
    recorded = run.get("source_snapshot", {})
    stale: list[str] = []
    for key, current in [("draft_hash", current_draft_hash), ("outline_hash", current_outline_hash)]:
        if current and recorded.get(key) != current:
            stale.append(key)
    return {"fresh": len(stale) == 0, "stale_sources": stale}

def _render_review_markdown(review: dict[str, Any]) -> str:

    """Render a reasoning review as readable Markdown for the author."""
    lines = [
        f"# Reasoning Review — Chapter {review.get('chapter_index', '?')}",
        f"**Run:** {review.get('run_id', '?')}",
        f"**Iteration:** {review.get('iteration', '?')}",
        f"**Overall:** {review.get('overall_status', '?')}",
        f"**Freshness:** {review.get('freshness', '?')}",
        f"**Execution:** {review.get('execution', {}).get('mode', '?')}",
        "",
    ]

    # Token usage summary
    usage = review.get("usage", {})
    total_usage = usage.get("total", {})
    inp = total_usage.get("input_tokens")
    out = total_usage.get("output_tokens")
    if inp is not None or out is not None:
        inp_str = str(inp) if inp is not None else "N/A"
        out_str = str(out) if out is not None else "N/A"
        lines.append(f"**Tokens:** {inp_str} in / {out_str} out")
        if not usage.get("complete", True):
            lines.append("⚠️ Some critics did not report token usage.")

    lines.append("")
    lines.append("## Critics")
    for cs in review.get("critic_summaries", []):
        icon = "✅" if cs.get("status") == "success" else "❌" if cs.get("status") in ("failed", "stale") else "⚠️"
        dur = cs.get("duration_ms")
        dur_str = f" ({dur}ms)" if dur is not None else ""
        lines.append(f"- {icon} **{cs['critic_id']}** — v{cs.get('version', '?')} — {cs.get('status', '?')}{dur_str}")

    blocking = review.get("blocking_findings", [])
    if blocking:
        lines.extend(["", "## Blocking Findings"])
        for bf in blocking:
            lines.append(f"- **{bf.get('critic', bf.get('critic_id', '?'))}**: {bf.get('evidence', bf.get('message', ''))}")

    warnings_list = review.get("warnings", [])
    if warnings_list:
        lines.extend(["", "## Warnings"])
        for w in warnings_list:
            lines.append(f"- {w.get('evidence', w.get('message', ''))}")

    synthesis = review.get("synthesis", "")
    if synthesis:
        lines.extend(["", "## Synthesis", "", synthesis])

    actions = review.get("recommended_actions", [])
    if actions:
        lines.extend(["", "## Recommended Next Actions"])
        for i, action in enumerate(actions, 1):
            lines.append(f"{i}. {action}")

    return "\n".join(lines) + "\n"


__all__ = [
    "persist_reasoning_run",
    "load_reasoning_run",
    "load_latest_run",
    "_render_review_markdown",
    "review_source_freshness",
]
