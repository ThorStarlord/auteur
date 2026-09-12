"""Typed routing seam for authority-bearing artifact acceptance."""

from __future__ import annotations

from typing import Any, Protocol


class AcceptanceOwner(Protocol):
    """Artifact owner capable of accepting one of its candidates."""

    def can_accept(self, target_artifact_id: str) -> bool: ...

    def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> Any: ...


class AcceptanceRegistry:
    """Resolve exactly one canonical acceptance owner for a target."""

    def __init__(self) -> None:
        self._owners: list[AcceptanceOwner] = []

    def register(self, owner: AcceptanceOwner) -> None:
        self._owners.append(owner)

    def accept(self, target_artifact_id: str, candidate_id: str, *, confirm: bool) -> Any:
        matches = [owner for owner in self._owners if owner.can_accept(target_artifact_id)]
        if not matches:
            raise ValueError(f"No acceptance owner registered for artifact: {target_artifact_id}")
        if len(matches) > 1:
            raise ValueError(f"Multiple acceptance owners registered for artifact: {target_artifact_id}")
        return matches[0].accept(target_artifact_id, candidate_id, confirm=confirm)
