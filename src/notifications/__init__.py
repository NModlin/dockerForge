"""
Notification system for DockerForge.

This package provides functionality for sending notifications through various channels
and managing notification preferences.
"""

from src.notifications.notification_manager import (
    NotificationManager,
    get_notification_manager,
)
from src.notifications.preference_manager import (
    PreferenceManager,
    get_preference_manager,
)
