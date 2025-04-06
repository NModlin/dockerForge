"""
DockerForge Unit Tests - Alert Manager
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the necessary modules
from src.resource_monitoring.alert_manager import AlertManager


class TestAlertManager:
    """Test the AlertManager class"""

    def setup_method(self):
        """Set up test environment"""
        self.alert_manager = AlertManager()

        # Sample alert data
        self.sample_alert = {
            "id": "test-alert-1",
            "title": "Test Alert",
            "description": "This is a test alert",
            "severity": "warning",
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False,
            "resolved": False,
            "resource": {
                "type": "container",
                "id": "test-container",
                "name": "test-container-name"
            },
            "metrics": [
                {
                    "name": "CPU Usage",
                    "value": 90.5,
                    "unit": "%"
                }
            ]
        }

    def test_initialization(self):
        """Test that the alert manager can be initialized"""
        assert self.alert_manager is not None
        assert hasattr(self.alert_manager, '_active_alerts')
        assert isinstance(self.alert_manager._active_alerts, dict)
        assert len(self.alert_manager._active_alerts) == 0

    def test_add_alert(self):
        """Test adding an alert"""
        # Add the sample alert
        self.alert_manager.add_alert(self.sample_alert)

        # Check that the alert was added
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0]["id"] == self.sample_alert["id"]
        assert active_alerts[0]["title"] == self.sample_alert["title"]
        assert active_alerts[0]["severity"] == self.sample_alert["severity"]

    def test_add_alert_without_id(self):
        """Test adding an alert without an ID"""
        # Create an alert without an ID
        alert_without_id = self.sample_alert.copy()
        del alert_without_id["id"]

        # Add the alert
        self.alert_manager.add_alert(alert_without_id)

        # Check that the alert was not added
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 0

    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        # Add the sample alert
        self.alert_manager.add_alert(self.sample_alert)

        # Acknowledge the alert
        self.alert_manager.acknowledge_alert(self.sample_alert["id"])

        # Check that the alert was acknowledged
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 1
        assert active_alerts[0]["acknowledged"] is True

    def test_acknowledge_nonexistent_alert(self):
        """Test acknowledging a nonexistent alert"""
        # Acknowledge a nonexistent alert
        self.alert_manager.acknowledge_alert("nonexistent-alert")

        # Check that no alerts were added
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 0

    def test_resolve_alert(self):
        """Test resolving an alert"""
        # Add the sample alert
        self.alert_manager.add_alert(self.sample_alert)

        # Resolve the alert
        self.alert_manager.resolve_alert(self.sample_alert["id"])

        # Check that the alert was removed
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 0

    def test_resolve_nonexistent_alert(self):
        """Test resolving a nonexistent alert"""
        # Resolve a nonexistent alert
        self.alert_manager.resolve_alert("nonexistent-alert")

        # Check that no alerts were added
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 0

    def test_multiple_alerts(self):
        """Test adding multiple alerts"""
        # Add the sample alert
        self.alert_manager.add_alert(self.sample_alert)

        # Add another alert
        second_alert = self.sample_alert.copy()
        second_alert["id"] = "test-alert-2"
        second_alert["title"] = "Second Test Alert"
        self.alert_manager.add_alert(second_alert)

        # Check that both alerts were added
        active_alerts = self.alert_manager.get_active_alerts()
        assert len(active_alerts) == 2

        # Check that the alerts have the correct IDs
        alert_ids = [alert["id"] for alert in active_alerts]
        assert self.sample_alert["id"] in alert_ids
        assert second_alert["id"] in alert_ids


if __name__ == "__main__":
    pytest.main(["-v", __file__])
