"""
Email notifier module for DockerForge.

This module provides functionality for sending email notifications.
"""

import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Union

import html2text

from src.config.config_manager import get_config
from src.notifications.notification_manager import Notification
from src.notifications.template_manager import get_template_manager
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("email_notifier")


class EmailNotifier:
    """Email notifier for sending email notifications."""

    def __init__(self):
        """Initialize the email notifier."""
        self._template_manager = get_template_manager()
        logger.debug("Email notifier initialized")

    def _get_smtp_config(self) -> Dict[str, Any]:
        """Get SMTP configuration from config.

        Returns:
            Dictionary with SMTP configuration
        """
        return {
            "server": get_config("notifications.channels.email.smtp_server", ""),
            "port": get_config("notifications.channels.email.smtp_port", 587),
            "use_tls": get_config("notifications.channels.email.use_tls", True),
            "username": get_config("notifications.channels.email.username", ""),
            "password": get_config("notifications.channels.email.password", ""),
            "from_address": get_config("notifications.channels.email.from_address", ""),
            "recipients": get_config("notifications.channels.email.recipients", []),
        }

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate SMTP configuration.

        Args:
            config: SMTP configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        if not config["server"]:
            logger.warning("SMTP server not configured")
            return False

        if not config["port"]:
            logger.warning("SMTP port not configured")
            return False

        if not config["username"]:
            logger.warning("SMTP username not configured")
            return False

        if not config["password"]:
            logger.warning("SMTP password not configured")
            return False

        if not config["from_address"]:
            logger.warning("SMTP from address not configured")
            return False

        if not config["recipients"]:
            logger.warning("SMTP recipients not configured")
            return False

        return True

    def _create_email_message(self, notification: Notification) -> MIMEMultipart:
        """Create email message from notification.

        Args:
            notification: The notification to create email from

        Returns:
            Email message
        """
        # Get SMTP configuration
        config = self._get_smtp_config()

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = notification.title
        message["From"] = config["from_address"]
        message["To"] = ", ".join(config["recipients"])

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

        # Render HTML template
        html_content = self._template_manager.render_template(
            template_id, "html", context
        )

        if html_content:
            # Create HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Convert HTML to text
            h2t = html2text.HTML2Text()
            h2t.ignore_links = False
            text_content = h2t.handle(html_content)

            # Create text part
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)
        else:
            # Render text template
            text_content = self._template_manager.render_template(
                template_id, "text", context
            )

            if text_content:
                # Create text part
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            else:
                # Use default text
                text_part = MIMEText(
                    f"{notification.title}\n\n{notification.message}", "plain"
                )
                message.attach(text_part)

        return message

    def send(self, notification: Notification) -> bool:
        """Send a notification via email.

        Args:
            notification: The notification to send

        Returns:
            True if the notification was sent, False otherwise
        """
        # Check if email notifications are enabled
        if not get_config("notifications.channels.email.enabled", False):
            logger.debug("Email notifications are disabled")
            return False

        # Get SMTP configuration
        config = self._get_smtp_config()

        # Validate configuration
        if not self._validate_config(config):
            logger.warning("Invalid SMTP configuration")
            return False

        try:
            # Create message
            message = self._create_email_message(notification)

            # Connect to SMTP server
            if config["use_tls"]:
                smtp = smtplib.SMTP(config["server"], config["port"])
                smtp.starttls()
            else:
                smtp = smtplib.SMTP(config["server"], config["port"])

            # Login
            smtp.login(config["username"], config["password"])

            # Send message
            smtp.send_message(message)

            # Disconnect
            smtp.quit()

            logger.info(f"Email notification sent: {notification.title}")
            return True
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
