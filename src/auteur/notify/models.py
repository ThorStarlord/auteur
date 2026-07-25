"""Models for Author Notification subsystem (v0.18.0)."""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass, field
from typing import Any


def _stable_id(*parts: str) -> str:
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class NotificationType(str, enum.Enum):
    DIVERGENCE = "divergence"
    STALE_COMMITMENT = "stale_commitment"
    REVIEW_READY = "review_ready"
    LIFECYCLE_GAP = "lifecycle_gap"
    EXECUTION_FAILURE = "execution_failure"
    ACCEPTANCE_READY = "acceptance_ready"


class NotificationSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


@dataclass
class NotificationFinding:
    """A single finding from a notification scan."""
    finding_id: str
    notification_type: NotificationType
    severity: NotificationSeverity
    title: str
    description: str = ""
    subsystem: str = ""
    command: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "type": self.notification_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "subsystem": self.subsystem,
            "command": self.command,
            "details": self.details,
        }
