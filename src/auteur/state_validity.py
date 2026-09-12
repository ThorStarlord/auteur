"""Shared state-validity vocabulary for cross-domain artifact probes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ArtifactValidity(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"
    MISSING = "missing"
    MALFORMED = "malformed"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class StateValidity:
    artifact_id: str
    status: ArtifactValidity
    reason: str = ""

    @property
    def blocking(self) -> bool:
        return self.status is not ArtifactValidity.FRESH

    @property
    def evidence_freshness(self):
        from auteur.decision.models import EvidenceFreshness

        return EvidenceFreshness.CURRENT if self.status is ArtifactValidity.FRESH else (
            EvidenceFreshness.STALE if self.status is ArtifactValidity.STALE else EvidenceFreshness.UNKNOWN
        )

    @classmethod
    def fresh(cls, artifact_id: str) -> "StateValidity":
        return cls(artifact_id, ArtifactValidity.FRESH)

    @classmethod
    def stale(cls, artifact_id: str, reason: str) -> "StateValidity":
        return cls(artifact_id, ArtifactValidity.STALE, reason)

    @classmethod
    def missing(cls, artifact_id: str, reason: str = "artifact is missing") -> "StateValidity":
        return cls(artifact_id, ArtifactValidity.MISSING, reason)

    @classmethod
    def malformed(cls, artifact_id: str, reason: str) -> "StateValidity":
        return cls(artifact_id, ArtifactValidity.MALFORMED, reason)

    @classmethod
    def unknown(cls, artifact_id: str, reason: str = "validity could not be established") -> "StateValidity":
        return cls(artifact_id, ArtifactValidity.UNKNOWN, reason)

    @classmethod
    def unavailable(cls, artifact_id: str, reason: str) -> "StateValidity":
        return cls(artifact_id, ArtifactValidity.UNAVAILABLE, reason)
