"""
Notification manager module for DockerForge.

This module provides functionality for sending notifications through various channels.
"""

import json
import logging
import os
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("notification_manager")


class NotificationSeverity(Enum):
    """Notification severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationType(Enum):
    """Types of notifications."""

    CONTAINER_EXIT = "container_exit"
    CONTAINER_OOM = "container_oom"
    HIGH_RESOURCE_USAGE = "high_resource_usage"
    SECURITY_ISSUE = "security_issue"
    UPDATE_AVAILABLE = "update_available"
    FIX_PROPOSAL = "fix_proposal"
    FIX_APPLIED = "fix_applied"
    CUSTOM = "custom"


class Notification:
    """Notification class representing a single notification."""

    def __init__(
        self,
        title: str,
        message: str,
        severity: NotificationSeverity = NotificationSeverity.INFO,
        notification_type: NotificationType = NotificationType.CUSTOM,
        container_id: Optional[str] = None,
        container_name: Optional[str] = None,
        issue_id: Optional[str] = None,
        fix_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
    ):
        """Initialize a notification.

        Args:
            title: The notification title
            message: The notification message
            severity: The notification severity
            notification_type: The notification type
            container_id: Optional container ID
            container_name: Optional container name
            issue_id: Optional issue ID
            fix_id: Optional fix ID
            metadata: Optional metadata
            actions: Optional actions that can be taken
        """
        self.id = self._generate_id()
        self.title = title
        self.message = message
        self.severity = severity
        self.notification_type = notification_type
        self.container_id = container_id
        self.container_name = container_name
        self.issue_id = issue_id
        self.fix_id = fix_id
        self.metadata = metadata or {}
        self.actions = actions or []
        self.created_at = datetime.now()
        self.sent = False
        self.sent_at = None
        self.sent_to = []
        self.acknowledged = False
        self.acknowledged_at = None
        self.acknowledged_by = None

    def _generate_id(self) -> str:
        """Generate a unique ID for the notification."""
        import uuid

        return f"notification_{uuid.uuid4().hex[:12]}"

    def mark_as_sent(self, channel: str) -> None:
        """Mark the notification as sent.

        Args:
            channel: The channel the notification was sent to
        """
        self.sent = True
        self.sent_at = datetime.now()
        self.sent_to.append(channel)

    def acknowledge(self, user: Optional[str] = None) -> None:
        """Acknowledge the notification.

        Args:
            user: The user who acknowledged the notification
        """
        self.acknowledged = True
        self.acknowledged_at = datetime.now()
        self.acknowledged_by = user

    def to_dict(self) -> Dict[str, Any]:
        """Convert the notification to a dictionary.

        Returns:
            A dictionary representation of the notification
        """
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "notification_type": self.notification_type.value,
            "container_id": self.container_id,
            "container_name": self.container_name,
            "issue_id": self.issue_id,
            "fix_id": self.fix_id,
            "metadata": self.metadata,
            "actions": self.actions,
            "created_at": self.created_at.isoformat(),
            "sent": self.sent,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "sent_to": self.sent_to,
            "acknowledged": self.acknowledged,
            "acknowledged_at": (
                self.acknowledged_at.isoformat() if self.acknowledged_at else None
            ),
            "acknowledged_by": self.acknowledged_by,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """Create a notification from a dictionary.

        Args:
            data: The dictionary to create the notification from

        Returns:
            A new Notification instance
        """
        notification = cls(
            title=data["title"],
            message=data["message"],
            severity=NotificationSeverity(data["severity"]),
            notification_type=NotificationType(data["notification_type"]),
            container_id=data.get("container_id"),
            container_name=data.get("container_name"),
            issue_id=data.get("issue_id"),
            fix_id=data.get("fix_id"),
            metadata=data.get("metadata", {}),
            actions=data.get("actions", []),
        )

        notification.id = data["id"]
        notification.created_at = datetime.fromisoformat(data["created_at"])
        notification.sent = data["sent"]

        if data["sent_at"]:
            notification.sent_at = datetime.fromisoformat(data["sent_at"])

        notification.sent_to = data["sent_to"]
        notification.acknowledged = data["acknowledged"]

        if data["acknowledged_at"]:
            notification.acknowledged_at = datetime.fromisoformat(
                data["acknowledged_at"]
            )

        notification.acknowledged_by = data["acknowledged_by"]

        return notification

    def __str__(self) -> str:
        """Return a string representation of the notification."""
        return f"{self.severity.value.upper()}: {self.title} - {self.message}"


class NotificationManager:
    """Manager for sending notifications through various channels."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Create a new NotificationManager instance (singleton)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NotificationManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        """Initialize the notification manager."""
        if self._initialized:
            return

        self._initialized = True
        self._notifiers = {}
        self._notification_history = []
        self._notification_counts = {
            "hourly": 0,
            "daily": 0,
            "last_hour_reset": datetime.now(),
            "last_day_reset": datetime.now(),
        }

        # Load notification channels
        self._load_notifiers()

        # Load notification history
        self._load_notification_history()

        logger.info("Notification manager initialized")

    def _load_notifiers(self) -> None:
        """Load notification channels from configuration."""
        # Import notifiers
        from src.notifications.discord_notifier import DiscordNotifier
        from src.notifications.email_notifier import EmailNotifier
        from src.notifications.slack_notifier import SlackNotifier
        from src.notifications.webhook_notifier import WebhookNotifier

        # Create notifiers
        self._notifiers = {
            "email": EmailNotifier(),
            "slack": SlackNotifier(),
            "discord": DiscordNotifier(),
            "webhook": WebhookNotifier(),
        }

    def _load_notification_history(self) -> None:
        """Load notification history from disk."""
        data_dir = os.path.expanduser(get_config("general.data_dir"))
        history_file = os.path.join(data_dir, "notification_history.json")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    data = json.load(f)

                    # Load notifications
                    self._notification_history = [
                        Notification.from_dict(n) for n in data["notifications"]
                    ]

                    # Load counts
                    self._notification_counts = {
                        "hourly": data["counts"]["hourly"],
                        "daily": data["counts"]["daily"],
                        "last_hour_reset": datetime.fromisoformat(
                            data["counts"]["last_hour_reset"]
                        ),
                        "last_day_reset": datetime.fromisoformat(
                            data["counts"]["last_day_reset"]
                        ),
                    }

                    logger.info(
                        f"Loaded {len(self._notification_history)} notifications from history"
                    )
            except Exception as e:
                logger.error(f"Error loading notification history: {str(e)}")

    def _save_notification_history(self) -> None:
        """Save notification history to disk."""
        data_dir = os.path.expanduser(get_config("general.data_dir"))
        history_file = os.path.join(data_dir, "notification_history.json")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        try:
            with open(history_file, "w") as f:
                data = {
                    "notifications": [n.to_dict() for n in self._notification_history],
                    "counts": {
                        "hourly": self._notification_counts["hourly"],
                        "daily": self._notification_counts["daily"],
                        "last_hour_reset": self._notification_counts[
                            "last_hour_reset"
                        ].isoformat(),
                        "last_day_reset": self._notification_counts[
                            "last_day_reset"
                        ].isoformat(),
                    },
                }
                json.dump(data, f, indent=2)

                logger.debug(
                    f"Saved {len(self._notification_history)} notifications to history"
                )
        except Exception as e:
            logger.error(f"Error saving notification history: {str(e)}")

    def _update_notification_counts(self) -> None:
        """Update notification counts and reset if needed."""
        now = datetime.now()

        # Reset hourly count if an hour has passed
        if now - self._notification_counts["last_hour_reset"] >= timedelta(hours=1):
            self._notification_counts["hourly"] = 0
            self._notification_counts["last_hour_reset"] = now
            logger.debug("Reset hourly notification count")

        # Reset daily count if a day has passed
        if now - self._notification_counts["last_day_reset"] >= timedelta(days=1):
            self._notification_counts["daily"] = 0
            self._notification_counts["last_day_reset"] = now
            logger.debug("Reset daily notification count")

    def _should_throttle(self, notification: Notification) -> bool:
        """Check if notification should be throttled.

        Args:
            notification: The notification to check

        Returns:
            True if the notification should be throttled, False otherwise
        """
        # Update counts
        self._update_notification_counts()

        # Get throttling settings
        throttling_enabled = get_config(
            "notifications.preferences.throttling.enabled", True
        )

        if not throttling_enabled:
            return False

        # Check quiet hours
        quiet_hours_enabled = get_config(
            "notifications.preferences.throttling.quiet_hours.enabled", False
        )

        if quiet_hours_enabled:
            now = datetime.now()
            start_time_str = get_config(
                "notifications.preferences.throttling.quiet_hours.start", "22:00"
            )
            end_time_str = get_config(
                "notifications.preferences.throttling.quiet_hours.end", "08:00"
            )

            # Parse time strings
            start_hour, start_minute = map(int, start_time_str.split(":"))
            end_hour, end_minute = map(int, end_time_str.split(":"))

            start_time = now.replace(
                hour=start_hour, minute=start_minute, second=0, microsecond=0
            )
            end_time = now.replace(
                hour=end_hour, minute=end_minute, second=0, microsecond=0
            )

            # Handle overnight quiet hours
            if start_time > end_time:
                # If current time is after start or before end, it's quiet hours
                if now >= start_time or now <= end_time:
                    # Only throttle non-critical notifications during quiet hours
                    if notification.severity != NotificationSeverity.CRITICAL:
                        logger.debug(
                            f"Throttling notification during quiet hours: {notification.title}"
                        )
                        return True
            else:
                # If current time is between start and end, it's quiet hours
                if start_time <= now <= end_time:
                    # Only throttle non-critical notifications during quiet hours
                    if notification.severity != NotificationSeverity.CRITICAL:
                        logger.debug(
                            f"Throttling notification during quiet hours: {notification.title}"
                        )
                        return True

        # Check hourly limit
        max_hourly = get_config(
            "notifications.preferences.throttling.max_notifications_per_hour", 10
        )

        if self._notification_counts["hourly"] >= max_hourly:
            # Only throttle non-critical notifications when hourly limit is reached
            if notification.severity != NotificationSeverity.CRITICAL:
                logger.debug(
                    f"Throttling notification due to hourly limit: {notification.title}"
                )
                return True

        # Check daily limit
        max_daily = get_config(
            "notifications.preferences.throttling.max_notifications_per_day", 50
        )

        if self._notification_counts["daily"] >= max_daily:
            # Only throttle non-critical notifications when daily limit is reached
            if notification.severity != NotificationSeverity.CRITICAL:
                logger.debug(
                    f"Throttling notification due to daily limit: {notification.title}"
                )
                return True

        # Check for similar notifications
        group_similar = get_config(
            "notifications.preferences.throttling.group_similar", True
        )

        if group_similar:
            # Look for similar notifications in the last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)

            for n in self._notification_history:
                if n.created_at >= one_hour_ago and n.title == notification.title:
                    # Found a similar notification
                    logger.debug(
                        f"Throttling similar notification: {notification.title}"
                    )
                    return True

        return False

    def _should_send_by_severity(self, severity: NotificationSeverity) -> bool:
        """Check if notification should be sent based on severity.

        Args:
            severity: The notification severity

        Returns:
            True if the notification should be sent, False otherwise
        """
        # Get severity thresholds
        thresholds = {
            NotificationSeverity.INFO: get_config(
                "notifications.preferences.severity_thresholds.info", False
            ),
            NotificationSeverity.WARNING: get_config(
                "notifications.preferences.severity_thresholds.warning", True
            ),
            NotificationSeverity.ERROR: get_config(
                "notifications.preferences.severity_thresholds.error", True
            ),
            NotificationSeverity.CRITICAL: get_config(
                "notifications.preferences.severity_thresholds.critical", True
            ),
        }

        return thresholds.get(severity, True)

    def _should_send_by_type(self, notification_type: NotificationType) -> bool:
        """Check if notification should be sent based on type.

        Args:
            notification_type: The notification type

        Returns:
            True if the notification should be sent, False otherwise
        """
        # Get type preferences
        type_prefs = {
            NotificationType.CONTAINER_EXIT: get_config(
                "notifications.preferences.notification_types.container_exit", True
            ),
            NotificationType.CONTAINER_OOM: get_config(
                "notifications.preferences.notification_types.container_oom", True
            ),
            NotificationType.HIGH_RESOURCE_USAGE: get_config(
                "notifications.preferences.notification_types.high_resource_usage", True
            ),
            NotificationType.SECURITY_ISSUE: get_config(
                "notifications.preferences.notification_types.security_issue", True
            ),
            NotificationType.UPDATE_AVAILABLE: get_config(
                "notifications.preferences.notification_types.update_available", True
            ),
            NotificationType.FIX_PROPOSAL: get_config(
                "notifications.preferences.notification_types.fix_proposal", True
            ),
            NotificationType.FIX_APPLIED: get_config(
                "notifications.preferences.notification_types.fix_applied", True
            ),
            NotificationType.CUSTOM: True,  # Always send custom notifications
        }

        return type_prefs.get(notification_type, True)

    def _get_channels_for_notification(self, notification: Notification) -> List[str]:
        """Get channels to send notification to.

        Args:
            notification: The notification to send

        Returns:
            List of channel names to send to
        """
        # Check if notifications are enabled
        if not get_config("notifications.enabled", True):
            return []

        # Get default channel
        default_channel = get_config("notifications.default_channel", "slack")

        # Get enabled channels
        enabled_channels = []

        for channel in self._notifiers.keys():
            if get_config(f"notifications.channels.{channel}.enabled", False):
                enabled_channels.append(channel)

        if not enabled_channels:
            logger.warning("No notification channels are enabled")
            return []

        # Determine channels based on severity
        if notification.severity == NotificationSeverity.CRITICAL:
            # Send critical notifications to all enabled channels
            return enabled_channels
        elif notification.severity == NotificationSeverity.ERROR:
            # Send error notifications to default channel if enabled, otherwise first enabled
            if default_channel in enabled_channels:
                return [default_channel]
            else:
                return [enabled_channels[0]]
        else:
            # Send other notifications to default channel if enabled, otherwise first enabled
            if default_channel in enabled_channels:
                return [default_channel]
            else:
                return [enabled_channels[0]]

    def send_notification(self, notification: Notification) -> bool:
        """Send a notification through appropriate channels.

        Args:
            notification: The notification to send

        Returns:
            True if the notification was sent, False otherwise
        """
        # Check if notification should be sent based on severity
        if not self._should_send_by_severity(notification.severity):
            logger.debug(
                f"Not sending notification due to severity threshold: {notification.title}"
            )
            return False

        # Check if notification should be sent based on type
        if not self._should_send_by_type(notification.notification_type):
            logger.debug(
                f"Not sending notification due to type preference: {notification.title}"
            )
            return False

        # Check if notification should be throttled
        if self._should_throttle(notification):
            logger.debug(
                f"Not sending notification due to throttling: {notification.title}"
            )
            return False

        # Get channels to send to
        channels = self._get_channels_for_notification(notification)

        if not channels:
            logger.warning(
                f"No channels available to send notification: {notification.title}"
            )
            return False

        # Send notification to each channel
        success = False

        for channel in channels:
            if channel in self._notifiers:
                try:
                    result = self._notifiers[channel].send(notification)

                    if result:
                        notification.mark_as_sent(channel)
                        success = True
                        logger.info(
                            f"Sent notification to {channel}: {notification.title}"
                        )
                    else:
                        logger.warning(
                            f"Failed to send notification to {channel}: {notification.title}"
                        )
                except Exception as e:
                    logger.error(f"Error sending notification to {channel}: {str(e)}")
            else:
                logger.warning(f"Unknown notification channel: {channel}")

        # Update counts if notification was sent
        if success:
            self._notification_counts["hourly"] += 1
            self._notification_counts["daily"] += 1

        # Add to history
        self._notification_history.append(notification)

        # Trim history if needed (keep last 1000 notifications)
        if len(self._notification_history) > 1000:
            self._notification_history = self._notification_history[-1000:]

        # Save history
        self._save_notification_history()

        return success

    def create_and_send_notification(
        self,
        title: str,
        message: str,
        severity: Union[NotificationSeverity, str] = NotificationSeverity.INFO,
        notification_type: Union[NotificationType, str] = NotificationType.CUSTOM,
        container_id: Optional[str] = None,
        container_name: Optional[str] = None,
        issue_id: Optional[str] = None,
        fix_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Notification]:
        """Create and send a notification.

        Args:
            title: The notification title
            message: The notification message
            severity: The notification severity
            notification_type: The notification type
            container_id: Optional container ID
            container_name: Optional container name
            issue_id: Optional issue ID
            fix_id: Optional fix ID
            metadata: Optional metadata
            actions: Optional actions that can be taken

        Returns:
            The notification if it was sent, None otherwise
        """
        # Convert string severity to enum if needed
        if isinstance(severity, str):
            try:
                severity = NotificationSeverity(severity)
            except ValueError:
                logger.warning(f"Invalid severity: {severity}, using INFO")
                severity = NotificationSeverity.INFO

        # Convert string notification type to enum if needed
        if isinstance(notification_type, str):
            try:
                notification_type = NotificationType(notification_type)
            except ValueError:
                logger.warning(
                    f"Invalid notification type: {notification_type}, using CUSTOM"
                )
                notification_type = NotificationType.CUSTOM

        # Create notification
        notification = Notification(
            title=title,
            message=message,
            severity=severity,
            notification_type=notification_type,
            container_id=container_id,
            container_name=container_name,
            issue_id=issue_id,
            fix_id=fix_id,
            metadata=metadata,
            actions=actions,
        )

        # Send notification
        if self.send_notification(notification):
            return notification

        return None

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID.

        Args:
            notification_id: The notification ID

        Returns:
            The notification if found, None otherwise
        """
        for notification in self._notification_history:
            if notification.id == notification_id:
                return notification

        return None

    def get_notifications(
        self,
        limit: int = 100,
        offset: int = 0,
        severity: Optional[NotificationSeverity] = None,
        notification_type: Optional[NotificationType] = None,
        container_id: Optional[str] = None,
        issue_id: Optional[str] = None,
        fix_id: Optional[str] = None,
        acknowledged: Optional[bool] = None,
    ) -> List[Notification]:
        """Get notifications with optional filtering.

        Args:
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            severity: Filter by severity
            notification_type: Filter by notification type
            container_id: Filter by container ID
            issue_id: Filter by issue ID
            fix_id: Filter by fix ID
            acknowledged: Filter by acknowledged status

        Returns:
            List of notifications matching the filters
        """
        # Filter notifications
        filtered = self._notification_history

        if severity:
            filtered = [n for n in filtered if n.severity == severity]

        if notification_type:
            filtered = [n for n in filtered if n.notification_type == notification_type]

        if container_id:
            filtered = [n for n in filtered if n.container_id == container_id]

        if issue_id:
            filtered = [n for n in filtered if n.issue_id == issue_id]

        if fix_id:
            filtered = [n for n in filtered if n.fix_id == fix_id]

        if acknowledged is not None:
            filtered = [n for n in filtered if n.acknowledged == acknowledged]

        # Sort by created_at (newest first)
        filtered.sort(key=lambda n: n.created_at, reverse=True)

        # Apply pagination
        return filtered[offset : offset + limit]

    def acknowledge_notification(
        self, notification_id: str, user: Optional[str] = None
    ) -> bool:
        """Acknowledge a notification.

        Args:
            notification_id: The notification ID
            user: The user who acknowledged the notification

        Returns:
            True if the notification was acknowledged, False otherwise
        """
        notification = self.get_notification(notification_id)

        if notification:
            notification.acknowledge(user)
            self._save_notification_history()
            logger.info(f"Notification acknowledged: {notification.title}")
            return True

        return False

    def clear_history(self) -> None:
        """Clear notification history."""
        self._notification_history = []
        self._save_notification_history()
        logger.info("Notification history cleared")


def get_notification_manager() -> NotificationManager:
    """Get the notification manager instance.

    Returns:
        The notification manager instance
    """
    return NotificationManager()
