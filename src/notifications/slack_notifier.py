"""
Slack notifier module for DockerForge.

This module provides functionality for sending Slack notifications.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from src.config.config_manager import get_config
from src.notifications.notification_manager import Notification
from src.notifications.template_manager import get_template_manager
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("slack_notifier")


class SlackNotifier:
    """Slack notifier for sending Slack notifications."""

    def __init__(self):
        """Initialize the Slack notifier."""
        self._template_manager = get_template_manager()
        logger.debug("Slack notifier initialized")

    def _get_slack_config(self) -> Dict[str, Any]:
        """Get Slack configuration from config.

        Returns:
            Dictionary with Slack configuration
        """
        return {
            "webhook_url": get_config("notifications.channels.slack.webhook_url", ""),
            "channel": get_config(
                "notifications.channels.slack.channel", "#docker-alerts"
            ),
            "username": get_config(
                "notifications.channels.slack.username", "DockerForge"
            ),
            "icon_emoji": get_config(
                "notifications.channels.slack.icon_emoji", ":whale:"
            ),
        }

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Slack configuration.

        Args:
            config: Slack configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        if not config["webhook_url"]:
            logger.warning("Slack webhook URL not configured")
            return False

        return True

    def _create_slack_payload(self, notification: Notification) -> Dict[str, Any]:
        """Create Slack payload from notification.

        Args:
            notification: The notification to create payload from

        Returns:
            Slack payload
        """
        # Get Slack configuration
        config = self._get_slack_config()

        # Get template
        template_id = notification.metadata.get("template_id", "default")

        # Prepare context
        context = {
            "title": notification.title,
            "message": notification.message,
            "severity": notification.severity.value,
            "notification_type": notification.notification_type.value,
            "container_id": notification.container_id,
            "container_name": notification.container_name,
            "issue_id": notification.issue_id,
            "fix_id": notification.fix_id,
            "timestamp": datetime.now(),
            "actions": notification.actions,
        }

        # Add metadata to context
        for key, value in notification.metadata.items():
            if key != "template_id" and key not in context:
                context[key] = value

        # Render Slack template
        slack_content = self._template_manager.render_template(
            template_id, "slack", context
        )

        if slack_content:
            try:
                # Parse JSON content
                blocks = json.loads(slack_content)

                # Create payload
                payload = {
                    "channel": config["channel"],
                    "username": config["username"],
                    "icon_emoji": config["icon_emoji"],
                }

                # Add blocks
                if "blocks" in blocks:
                    payload["blocks"] = blocks["blocks"]

                # Add attachments if present
                if "attachments" in blocks:
                    payload["attachments"] = blocks["attachments"]

                return payload
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing Slack template: {str(e)}")

        # Use default payload
        return {
            "channel": config["channel"],
            "username": config["username"],
            "icon_emoji": config["icon_emoji"],
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": notification.title,
                        "emoji": True,
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": notification.message},
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:* {notification.severity.value.upper()}",
                        }
                    ],
                },
            ],
        }

    def send(self, notification: Notification) -> bool:
        """Send a notification via Slack.

        Args:
            notification: The notification to send

        Returns:
            True if the notification was sent, False otherwise
        """
        # Check if Slack notifications are enabled
        if not get_config("notifications.channels.slack.enabled", False):
            logger.debug("Slack notifications are disabled")
            return False

        # Get Slack configuration
        config = self._get_slack_config()

        # Validate configuration
        if not self._validate_config(config):
            logger.warning("Invalid Slack configuration")
            return False

        try:
            # Create payload
            payload = self._create_slack_payload(notification)

            # Send notification
            response = requests.post(
                config["webhook_url"],
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            # Check response
            if response.status_code == 200 and response.text == "ok":
                logger.info(f"Slack notification sent: {notification.title}")
                return True
            else:
                logger.error(
                    f"Error sending Slack notification: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return False
