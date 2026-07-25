"""Notification service — application boundary."""

from __future__ import annotations

from pathlib import Path

from auteur.notify.models import NotificationFinding
from auteur.notify.scanner import NotificationScanner


class NotificationService:
    """Application-service boundary for author notifications."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.scanner = NotificationScanner(self.project_root)

    def scan(self) -> list[NotificationFinding]:
        """Scan all subsystems and return actionable findings."""
        return self.scanner.scan()

    def has_findings(self) -> bool:
        """Check if there are any findings."""
        return len(self.scan()) > 0
