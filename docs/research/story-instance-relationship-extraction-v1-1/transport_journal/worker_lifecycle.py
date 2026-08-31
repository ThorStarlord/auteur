"""Research-local evidence and launch gate for worker slot lifecycle."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path


class LifecycleError(RuntimeError):
    """The next worker cannot safely be launched."""


@dataclass(frozen=True)
class LifecycleReadiness:
    ready: bool
    allocated: int
    closed: int


def _event_path(root: Path, opaque_id: str, name: str) -> Path:
    return Path(root) / opaque_id / name


def record_worker_closed(
    journal_root: Path,
    opaque_id: str,
    agent_id: str,
    close_operation: str,
    close_result,
) -> dict:
    """Persist one successful exact-agent close acknowledgement.

    Closure evidence is separate from the append-only transport journal and is
    itself write-once. A worker may be recorded closed only after its complete
    journal chain exists and its durable binding matches the supplied agent.
    """

    complete = _event_path(journal_root, opaque_id, "04-complete.json")
    bound = _event_path(journal_root, opaque_id, "02-agent-bound.json")
    target = _event_path(journal_root, opaque_id, "05-worker-closed.json")
    if not complete.is_file() or not bound.is_file():
        raise LifecycleError("worker cannot close before journal completion")
    try:
        bound_payload = json.loads(bound.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleError("agent binding is unreadable") from exc
    if bound_payload.get("agent_id") != agent_id:
        raise LifecycleError("close agent does not match durable binding")
    if not close_operation or close_result is None:
        raise LifecycleError("close acknowledgement is required")
    try:
        data = json.dumps({
            "opaque_observation_id": opaque_id,
            "agent_id": agent_id,
            "close_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "close_operation": close_operation,
            "close_result": close_result,
        }, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    except (TypeError, ValueError) as exc:
        raise LifecycleError("close acknowledgement is not JSON-serializable") from exc
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise LifecycleError("worker closure evidence already exists") from exc
    return json.loads(data)


def assert_next_launch_permitted(journal_root: Path) -> dict:
    """Require every allocated observation to be complete and explicitly closed."""

    root = Path(journal_root)
    allocated = 0
    closed = 0
    for observation_dir in sorted(root.iterdir()) if root.exists() else []:
        if not observation_dir.is_dir() or not (observation_dir / "01-allocated.json").exists():
            continue
        allocated += 1
        complete = observation_dir / "04-complete.json"
        closure = observation_dir / "05-worker-closed.json"
        if not complete.is_file():
            raise LifecycleError(f"observation is not complete: {observation_dir.name}")
        if not closure.is_file():
            raise LifecycleError(f"worker is not closed: {observation_dir.name}")
        try:
            binding = json.loads((observation_dir / "02-agent-bound.json").read_text())
            record = json.loads(closure.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise LifecycleError(f"closure evidence is unreadable: {observation_dir.name}") from exc
        if (record.get("opaque_observation_id") != observation_dir.name or
                record.get("agent_id") != binding.get("agent_id")):
            raise LifecycleError(f"closure evidence binding mismatch: {observation_dir.name}")
        closed += 1
    return LifecycleReadiness(allocated == closed, allocated, closed)
