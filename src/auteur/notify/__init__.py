"""Author Notification (v0.18.0).

Proactive scanning for events that need author attention — divergence,
review readiness, lifecycle gaps, execution failures.
"""

from auteur.notify.models import NotificationFinding, NotificationType, NotificationSeverity
from auteur.notify.service import NotificationService

__all__ = [
    "NotificationFinding",
    "NotificationType",
    "NotificationSeverity",
    "NotificationService",
]
