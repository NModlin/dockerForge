"""
Alert manager for the DockerForge Web UI.

This module provides a simple alert manager for handling alerts.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

# Initialize logger
logger = logging.getLogger(__name__)


class AlertManager:
    """
    Simple alert manager for handling alerts.
    """

    def __init__(self):
        """
        Initialize the alert manager.
        """
        # In-memory storage for active alerts
        self._active_alerts: Dict[str, Dict[str, Any]] = {}

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all active alerts.

        Returns:
            List[Dict[str, Any]]: List of active alerts
        """
        return list(self._active_alerts.values())

    def add_alert(self, alert: Dict[str, Any]) -> None:
        """
        Add an alert.

        Args:
            alert (Dict[str, Any]): Alert to add
        """
        if "id" not in alert:
            logger.error("Alert must have an ID")
            return

        self._active_alerts[alert["id"]] = alert
        logger.info(f"Added alert {alert['id']}")

    def acknowledge_alert(self, alert_id: str) -> None:
        """
        Acknowledge an alert.

        Args:
            alert_id (str): Alert ID
        """
        if alert_id not in self._active_alerts:
            logger.warning(f"Alert {alert_id} not found")
            return

        self._active_alerts[alert_id]["acknowledged"] = True
        logger.info(f"Acknowledged alert {alert_id}")

    def resolve_alert(self, alert_id: str) -> None:
        """
        Resolve an alert.

        Args:
            alert_id (str): Alert ID
        """
        if alert_id not in self._active_alerts:
            logger.warning(f"Alert {alert_id} not found")
            return

        self._active_alerts[alert_id]["resolved"] = True
        logger.info(f"Resolved alert {alert_id}")

        # Remove the alert from active alerts
        del self._active_alerts[alert_id]
