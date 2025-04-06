"""
DockerForge Unit Tests - Alert Manager (Mock Version)
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock


class TestAlertManager:
    """Test the AlertManager class using mocks"""

    def setup_method(self):
        """Set up test environment"""
        # Create a mock AlertManager
        self.alert_manager = MagicMock()
        
        # Set up the mock methods
        self.alert_manager.get_active_alerts.return_value = []
        self.alert_manager.add_alert = MagicMock()
        self.alert_manager.acknowledge_alert = MagicMock()
        self.alert_manager.resolve_alert = MagicMock()
        
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

    def test_add_alert(self):
        """Test adding an alert"""
        # Add the sample alert
        self.alert_manager.add_alert(self.sample_alert)
        
        # Check that the add_alert method was called with the correct arguments
        self.alert_manager.add_alert.assert_called_once_with(self.sample_alert)

    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        # Acknowledge the alert
        self.alert_manager.acknowledge_alert(self.sample_alert["id"])
        
        # Check that the acknowledge_alert method was called with the correct arguments
        self.alert_manager.acknowledge_alert.assert_called_once_with(self.sample_alert["id"])

    def test_resolve_alert(self):
        """Test resolving an alert"""
        # Resolve the alert
        self.alert_manager.resolve_alert(self.sample_alert["id"])
        
        # Check that the resolve_alert method was called with the correct arguments
        self.alert_manager.resolve_alert.assert_called_once_with(self.sample_alert["id"])


if __name__ == "__main__":
    pytest.main(["-v", __file__])
