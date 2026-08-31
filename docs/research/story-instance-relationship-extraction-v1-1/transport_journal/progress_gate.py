"""Executor-local cumulative reconciliation for V1.1 progress."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from transport_journal import Reconciliation


@dataclass(frozen=True)
class ProgressReconciliation:
    """Aggregate journal result plus the allocation-set diagnostics."""

    expected_positions: frozenset[int]
    allocated_positions: frozenset[int]
    malformed_allocations: int
    reconciliation: Reconciliation


def _allocation_positions(journal_root: Path) -> tuple[frozenset[int], int]:
    positions: set[int] = set()
    malformed = 0
    root = Path(journal_root)
    if not root.exists():
        return frozenset(), 0

    for observation_dir in sorted(root.iterdir()):
        if not observation_dir.is_dir():
            continue
        allocation = observation_dir / "01-allocated.json"
        try:
            payload = json.loads(allocation.read_text())
            position = payload["schedule_position"]
            if isinstance(position, bool) or not isinstance(position, int):
                raise ValueError("schedule_position must be an integer")
            positions.add(position)
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            malformed += 1
    return frozenset(positions), malformed


def derive_allocated_positions(journal_root: Path) -> frozenset[int]:
    """Derive all valid allocated schedule positions in a journal root."""

    positions, _ = _allocation_positions(journal_root)
    return positions


def reconcile_all_allocated(adapter) -> ProgressReconciliation:
    """Reconcile every authoritative allocation currently in the journal.

    The caller supplies only the adapter.  This prevents normal execution from
    accidentally reconciling a singleton current-position set.
    """

    positions, malformed = _allocation_positions(adapter.journal.root)
    reconciliation = adapter.reconcile(expected_positions=positions)
    return ProgressReconciliation(
        expected_positions=positions,
        allocated_positions=positions,
        malformed_allocations=malformed,
        reconciliation=reconciliation,
    )
