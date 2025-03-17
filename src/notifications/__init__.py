"""
Notification system for DockerForge.

This package provides functionality for sending notifications through various channels
and managing notification preferences.
"""

from src.notifications.notification_manager import get_notification_manager, NotificationManager
from src.notifications.preference_manager import get_preference_manager, PreferenceManager
