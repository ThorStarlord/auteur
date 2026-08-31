"""Append-only, write-once transport evidence for research runs."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class JournalError(RuntimeError):
    pass


def _bytes(value) -> bytes:
    return value if isinstance(value, bytes) else value.encode("utf-8")


def _publish_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".event-", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            raise JournalError(f"event already exists: {path}")
        try:
            os.link(temp, path)
        except FileExistsError as exc:
            raise JournalError(f"event already exists: {path}") from exc
        temp.unlink()
        if path.read_bytes() != data:
            raise JournalError(f"published bytes differ: {path}")
    finally:
        if temp.exists():
            temp.unlink()


def _event(path: Path, payload: dict) -> None:
    if not isinstance(payload, dict):
        raise JournalError("event payload must be an object")
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    _publish_once(path, data)


class Journal:
    def __init__(self, root: Path):
        self.root = Path(root)

    def _dir(self, oid: str) -> Path:
        if not oid or "/" in oid or "\\" in oid:
            raise JournalError("invalid opaque observation ID")
        return self.root / oid

    def allocate(self, payload: dict) -> None:
        required = {"run_id", "schedule_position", "opaque_observation_id", "role"}
        if not required <= payload.keys():
            raise JournalError("allocation fields missing")
        d = self._dir(payload["opaque_observation_id"])
        if d.exists():
            raise JournalError("opaque observation already allocated")
        _event(d / "01-allocated.json", payload)

    def bind(self, oid: str, agent_id: str, launch_timestamp: str) -> None:
        d = self._dir(oid)
        if not (d / "01-allocated.json").exists():
            raise JournalError("observation is not allocated")
        _event(d / "02-agent-bound.json", {
            "opaque_observation_id": oid, "agent_id": agent_id,
            "launch_timestamp": launch_timestamp,
        })

    def capture(self, oid: str, agent_id: str, response: str,
                completion_timestamp: str, tools_used: bool) -> dict:
        d = self._dir(oid)
        bound = json.loads((d / "02-agent-bound.json").read_text())
        if bound["agent_id"] != agent_id:
            raise JournalError("agent binding mismatch")
        raw_path = d / "raw-response.txt"
        raw = _bytes(response)
        _publish_once(raw_path, raw)
        digest = hashlib.sha256(raw).hexdigest()
        _event(d / "03-response-captured.json", {
            "opaque_observation_id": oid, "agent_id": agent_id,
            "raw_response_path": str(raw_path),
            "raw_response_sha256": digest,
            "completion_timestamp": completion_timestamp,
            "tools_used": bool(tools_used),
        })
        return {"raw_response_path": str(raw_path), "raw_response_sha256": digest}

    def complete(self, oid: str, agent_id: str, raw_response_sha256: str) -> None:
        d = self._dir(oid)
        capture = json.loads((d / "03-response-captured.json").read_text())
        if capture["agent_id"] != agent_id or capture["raw_response_sha256"] != raw_response_sha256:
            raise JournalError("completion binding mismatch")
        _event(d / "04-complete.json", {
            "opaque_observation_id": oid, "agent_id": agent_id,
            "raw_response_sha256": raw_response_sha256,
            "completion_state": "COMPLETE",
        })


@dataclass(frozen=True)
class Reconciliation:
    ready: bool
    complete_chains: int
    unique_opaque_ids: int
    unique_agent_ids: int
    hash_mismatches: int
    incomplete_chains: int
    conflicting_bindings: int


def _records(root: Path):
    for d in sorted(Path(root).iterdir()) if Path(root).exists() else []:
        if d.is_dir():
            yield d


def reconcile(root: Path, expected_positions: Iterable[int]) -> Reconciliation:
    rows = list(_records(Path(root)))
    ids = []
    agents = []
    mismatches = 0
    incomplete = 0
    complete = 0
    for d in rows:
        try:
            allocation = json.loads((d / "01-allocated.json").read_text())
            bound = json.loads((d / "02-agent-bound.json").read_text())
            capture = json.loads((d / "03-response-captured.json").read_text())
            done = json.loads((d / "04-complete.json").read_text())
            oid = allocation["opaque_observation_id"]
            agent = bound["agent_id"]
            ids.append(oid)
            agents.append(agent)
            raw = Path(capture["raw_response_path"])
            actual = hashlib.sha256(raw.read_bytes()).hexdigest()
            if actual != capture["raw_response_sha256"] or capture["raw_response_sha256"] != done["raw_response_sha256"]:
                mismatches += 1
            if done["completion_state"] != "COMPLETE":
                incomplete += 1
            else:
                complete += 1
        except (OSError, KeyError, json.JSONDecodeError):
            incomplete += 1
    duplicate_ids = len(ids) - len(set(ids))
    conflicting = len(agents) - len(set(agents))
    expected = set(expected_positions)
    positions = set()
    for d in rows:
        try:
            positions.add(json.loads((d / "01-allocated.json").read_text())["schedule_position"])
        except (OSError, KeyError, json.JSONDecodeError):
            pass
    missing = len(expected - positions)
    ready = (complete == len(expected) == len(rows) and missing == 0 and
             len(ids) == len(set(ids)) and len(agents) == len(set(agents)) and
             mismatches == 0 and incomplete == 0)
    return Reconciliation(ready, complete, len(set(ids)), len(set(agents)),
                          mismatches, incomplete + missing, conflicting + duplicate_ids)


def rebuild_ledger(root: Path, target: Path | None = None,
                   simulate_failure: bool = False) -> dict:
    root, target = Path(root), Path(target or Path(root).parent / "transport-ledger.json")
    result = []
    for d in _records(root):
        for name in ("01-allocated.json", "02-agent-bound.json",
                     "03-response-captured.json", "04-complete.json"):
            if not (d / name).exists():
                raise JournalError("cannot rebuild from incomplete event chain")
        a = json.loads((d / "01-allocated.json").read_text())
        b = json.loads((d / "02-agent-bound.json").read_text())
        c = json.loads((d / "03-response-captured.json").read_text())
        q = json.loads((d / "04-complete.json").read_text())
        result.append({"schedule_position": a["schedule_position"],
                       "opaque_observation_id": a["opaque_observation_id"],
                       "role": a["role"], "agent_id": b["agent_id"],
                       "raw_response_path": c["raw_response_path"],
                       "raw_response_sha256": q["raw_response_sha256"],
                       "final_status": q["completion_state"]})
    result.sort(key=lambda x: x["schedule_position"])
    output = {"derived": "REBUILDABLE_NON_AUTHORITATIVE", "records": result}
    data = json.dumps(output, sort_keys=True, indent=2).encode() + b"\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".ledger-", dir=target.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        json.loads(temp.read_text())
        if simulate_failure:
            raise JournalError("simulated derived-ledger failure")
        os.replace(temp, target)
        return output
    finally:
        if temp.exists():
            temp.unlink()

