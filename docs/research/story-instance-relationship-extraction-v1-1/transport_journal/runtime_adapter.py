"""Minimal live-worker adapter delegating to the qualified Journal."""
from __future__ import annotations

from pathlib import Path

from transport_journal import Journal, JournalError, rebuild_ledger


class RuntimeAdapter:
    """Enforce launch/bind/wait/capture/complete ordering around a worker."""

    def __init__(self, journal: Journal):
        self.journal = journal

    def allocate(self, payload: dict) -> None:
        self.journal.allocate(payload)

    def before_launch(self, opaque_id: str) -> None:
        event = self.journal.root / opaque_id / "01-allocated.json"
        if not event.is_file():
            raise JournalError("allocation event must exist before launch")

    def bind(self, opaque_id: str, agent_id: str, launch_timestamp: str) -> None:
        self.journal.bind(opaque_id, agent_id, launch_timestamp)

    def before_wait(self, opaque_id: str, agent_id: str) -> None:
        event = self.journal.root / opaque_id / "02-agent-bound.json"
        if not event.is_file():
            raise JournalError("agent binding must exist before wait")
        import json
        bound = json.loads(event.read_text())
        if bound.get("agent_id") != agent_id:
            raise JournalError("wait agent does not match durable binding")

    def capture(self, opaque_id: str, agent_id: str, response: str,
                completion_timestamp: str, tools_used: bool) -> dict:
        return self.journal.capture(
            opaque_id, agent_id, response, completion_timestamp, tools_used
        )

    def complete(self, opaque_id: str, agent_id: str,
                 raw_response_sha256: str) -> None:
        event = self.journal.root / opaque_id / "03-response-captured.json"
        if not event.is_file():
            raise JournalError("response capture must exist before complete")
        self.journal.complete(opaque_id, agent_id, raw_response_sha256)

    def reconcile(self, expected_positions):
        return __import__("transport_journal").reconcile(
            self.journal.root, expected_positions
        )

    def rebuild_ledger(self, target: Path, simulate_failure: bool = False):
        return rebuild_ledger(self.journal.root, target, simulate_failure)
