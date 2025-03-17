"""
Webhook notifier module for DockerForge.

This module provides functionality for sending webhook notifications.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import requests

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.notifications.notification_manager import Notification
from src.notifications.template_manager import get_template_manager

# Set up logging
logger = get_logger("webhook_notifier")


class WebhookNotifier:
    """Webhook notifier for sending webhook notifications."""
    
    def __init__(self):
        """Initialize the webhook notifier."""
        self._template_manager = get_template_manager()
        logger.debug("Webhook notifier initialized")
    
    def _get_webhook_config(self) -> Dict[str, Any]:
        """Get webhook configuration from config.
        
        Returns:
            Dictionary with webhook configuration
        """
        return {
            "url": get_config("notifications.channels.webhook.url", ""),
            "headers": get_config("notifications.channels.webhook.headers", {}),
        }
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate webhook configuration.
        
        Args:
            config: Webhook configuration
            
        Returns:
            True if configuration is valid, False otherwise
        """
        if not config["url"]:
            logger.warning("Webhook URL not configured")
            return False
        
        return True
    
    def _create_webhook_payload(self, notification: Notification) -> Dict[str, Any]:
        """Create webhook payload from notification.
        
        Args:
            notification: The notification to create payload from
            
        Returns:
            Webhook payload
        """
        # Prepare payload
        payload = {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "severity": notification.severity.value,
            "notification_type": notification.notification_type.value,
            "timestamp": datetime.now().isoformat(),
            "metadata": notification.metadata,
            "actions": notification.actions,
        }
        
        # Add container info if present
        if notification.container_id:
            payload["container_id"] = notification.container_id
        
        if notification.container_name:
            payload["container_name"] = notification.container_name
        
        # Add issue info if present
        if notification.issue_id:
            payload["issue_id"] = notification.issue_id
        
        # Add fix info if present
        if notification.fix_id:
            payload["fix_id"] = notification.fix_id
        
        return payload
    
    def send(self, notification: Notification) -> bool:
        """Send a notification via webhook.
        
        Args:
            notification: The notification to send
            
        Returns:
            True if the notification was sent, False otherwise
        """
        # Check if webhook notifications are enabled
        if not get_config("notifications.channels.webhook.enabled", False):
            logger.debug("Webhook notifications are disabled")
            return False
        
        # Get webhook configuration
        config = self._get_webhook_config()
        
        # Validate configuration
        if not self._validate_config(config):
            logger.warning("Invalid webhook configuration")
            return False
        
        try:
            # Create payload
            payload = self._create_webhook_payload(notification)
            
            # Set default headers
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "DockerForge/1.0",
            }
            
            # Add custom headers
            if config["headers"]:
                headers.update(config["headers"])
            
            # Send notification
            response = requests.post(
                config["url"],
                json=payload,
                headers=headers,
                timeout=10,
            )
            
            # Check response
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook notification sent: {notification.title}")
                return True
            else:
                logger.error(f"Error sending webhook notification: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
            return False
