"""
Discord notifier module for DockerForge.

This module provides functionality for sending Discord notifications.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook

from src.config.config_manager import get_config
from src.notifications.notification_manager import Notification
from src.notifications.template_manager import get_template_manager
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("discord_notifier")


class DiscordNotifier:
    """Discord notifier for sending Discord notifications."""

    def __init__(self):
        """Initialize the Discord notifier."""
        self._template_manager = get_template_manager()
        logger.debug("Discord notifier initialized")

    def _get_discord_config(self) -> Dict[str, Any]:
        """Get Discord configuration from config.

        Returns:
            Dictionary with Discord configuration
        """
        return {
            "webhook_url": get_config("notifications.channels.discord.webhook_url", ""),
            "username": get_config(
                "notifications.channels.discord.username", "DockerForge"
            ),
            "avatar_url": get_config("notifications.channels.discord.avatar_url", ""),
        }

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate Discord configuration.

        Args:
            config: Discord configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        if not config["webhook_url"]:
            logger.warning("Discord webhook URL not configured")
            return False

        return True

    def _create_discord_webhook(
        self, notification: Notification
    ) -> Optional[DiscordWebhook]:
        """Create Discord webhook from notification.

        Args:
            notification: The notification to create webhook from

        Returns:
            Discord webhook, or None if creation failed
        """
        # Get Discord configuration
        config = self._get_discord_config()

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

        # Create webhook
        webhook = DiscordWebhook(
            url=config["webhook_url"],
            username=config["username"],
            avatar_url=config["avatar_url"] if config["avatar_url"] else None,
        )

        # Render Discord template
        discord_content = self._template_manager.render_template(
            template_id, "discord", context
        )

        if discord_content:
            try:
                # Parse JSON content
                content = json.loads(discord_content)

                # Add content if present
                if "content" in content:
                    webhook.content = content["content"]

                # Add embeds if present
                if "embeds" in content:
                    for embed_data in content["embeds"]:
                        embed = DiscordEmbed()

                        # Set title
                        if "title" in embed_data:
                            embed.set_title(embed_data["title"])

                        # Set description
                        if "description" in embed_data:
                            embed.set_description(embed_data["description"])

                        # Set color
                        if "color" in embed_data:
                            embed.set_color(embed_data["color"])
                        else:
                            # Set color based on severity
                            if notification.severity.value == "critical":
                                embed.set_color(0x9C27B0)  # Purple
                            elif notification.severity.value == "error":
                                embed.set_color(0xF44336)  # Red
                            elif notification.severity.value == "warning":
                                embed.set_color(0xFF9800)  # Orange
                            else:
                                embed.set_color(0x2196F3)  # Blue

                        # Set timestamp
                        if "timestamp" in embed_data:
                            embed.set_timestamp(embed_data["timestamp"])

                        # Set footer
                        if "footer" in embed_data:
                            embed.set_footer(
                                text=embed_data["footer"].get("text", ""),
                                icon_url=embed_data["footer"].get("icon_url", ""),
                            )

                        # Set thumbnail
                        if "thumbnail" in embed_data:
                            embed.set_thumbnail(
                                url=embed_data["thumbnail"].get("url", "")
                            )

                        # Set image
                        if "image" in embed_data:
                            embed.set_image(url=embed_data["image"].get("url", ""))

                        # Set author
                        if "author" in embed_data:
                            embed.set_author(
                                name=embed_data["author"].get("name", ""),
                                url=embed_data["author"].get("url", ""),
                                icon_url=embed_data["author"].get("icon_url", ""),
                            )

                        # Add fields
                        if "fields" in embed_data:
                            for field in embed_data["fields"]:
                                embed.add_embed_field(
                                    name=field.get("name", ""),
                                    value=field.get("value", ""),
                                    inline=field.get("inline", False),
                                )

                        # Add embed to webhook
                        webhook.add_embed(embed)

                return webhook
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error parsing Discord template: {str(e)}")

        # Use default embed
        embed = DiscordEmbed(
            title=notification.title,
            description=notification.message,
        )

        # Set color based on severity
        if notification.severity.value == "critical":
            embed.set_color(0x9C27B0)  # Purple
        elif notification.severity.value == "error":
            embed.set_color(0xF44336)  # Red
        elif notification.severity.value == "warning":
            embed.set_color(0xFF9800)  # Orange
        else:
            embed.set_color(0x2196F3)  # Blue

        # Add severity field
        embed.add_embed_field(
            name="Severity",
            value=notification.severity.value.upper(),
            inline=True,
        )

        # Add container field if present
        if notification.container_name:
            embed.add_embed_field(
                name="Container",
                value=notification.container_name,
                inline=True,
            )

        # Add timestamp
        embed.set_timestamp()

        # Add footer
        embed.set_footer(text="DockerForge Notification")

        # Add embed to webhook
        webhook.add_embed(embed)

        return webhook

    def send(self, notification: Notification) -> bool:
        """Send a notification via Discord.

        Args:
            notification: The notification to send

        Returns:
            True if the notification was sent, False otherwise
        """
        # Check if Discord notifications are enabled
        if not get_config("notifications.channels.discord.enabled", False):
            logger.debug("Discord notifications are disabled")
            return False

        # Get Discord configuration
        config = self._get_discord_config()

        # Validate configuration
        if not self._validate_config(config):
            logger.warning("Invalid Discord configuration")
            return False

        try:
            # Create webhook
            webhook = self._create_discord_webhook(notification)

            if not webhook:
                logger.error("Failed to create Discord webhook")
                return False

            # Send notification
            response = webhook.execute()

            # Check response
            if response.status_code == 204:
                logger.info(f"Discord notification sent: {notification.title}")
                return True
            else:
                logger.error(
                    f"Error sending Discord notification: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error sending Discord notification: {str(e)}")
            return False
