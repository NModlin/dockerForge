"""
DockerForge Integration Tests - Monitoring API
"""

import json
import os
import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the necessary modules
from src.web.api.main import app


class TestMonitoringAPI:
    """Test the monitoring API endpoints"""

    def setup_method(self):
        """Set up test environment"""
        self.client = TestClient(app)

        # Create a test user and get a token
        self.user_data = {"username": "testuser", "password": "testpassword"}

        # Try to create a user (this might fail if the user already exists)
        try:
            self.client.post("/auth/register", json=self.user_data)
        except Exception:
            pass

        # Log in and get a token
        response = self.client.post(
            "/auth/token",
            data={
                "username": self.user_data["username"],
                "password": self.user_data["password"],
            },
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    def test_get_host_metrics(self):
        """Test getting host metrics"""
        if not self.token:
            pytest.skip("Authentication failed")

        response = self.client.get("/monitoring/host/metrics", headers=self.headers)

        # Check that the request was successful
        assert response.status_code == 200

        # Check that the response contains the expected fields
        data = response.json()
        assert "timestamp" in data
        assert "cpu" in data
        assert "memory" in data
        assert "disk" in data
        assert "network" in data

        # Check CPU metrics
        assert "percent" in data["cpu"]
        assert "count" in data["cpu"]

        # Check memory metrics
        assert "virtual" in data["memory"]
        assert "swap" in data["memory"]
        assert "total" in data["memory"]["virtual"]
        assert "used" in data["memory"]["virtual"]
        assert "percent" in data["memory"]["virtual"]

    def test_get_host_metrics_history(self):
        """Test getting host metrics history"""
        if not self.token:
            pytest.skip("Authentication failed")

        # Test for each metric type
        metric_types = ["cpu", "memory", "disk", "network"]

        for metric_type in metric_types:
            response = self.client.get(
                f"/monitoring/host/metrics/history/{metric_type}",
                params={"hours": 1},
                headers=self.headers,
            )

            # Check that the request was successful
            assert response.status_code == 200

            # Check that the response is a list
            data = response.json()
            assert isinstance(data, list)

            # If there are metrics, check their structure
            if data:
                assert "timestamp" in data[0]
                assert "data" in data[0]

    def test_get_system_info(self):
        """Test getting system information"""
        if not self.token:
            pytest.skip("Authentication failed")

        response = self.client.get("/monitoring/host/system-info", headers=self.headers)

        # Check that the request was successful
        assert response.status_code == 200

        # Check that the response contains the expected fields
        data = response.json()
        assert "platform" in data
        assert "system" in data
        assert "release" in data
        assert "version" in data
        assert "architecture" in data
        assert "processor" in data
        assert "hostname" in data
        assert "python_version" in data
        assert "cpu_count" in data
        assert "physical_cpu_count" in data
        assert "memory_total" in data
        assert "boot_time" in data
        assert "docker" in data

    def test_get_resource_stats_summary(self):
        """Test getting resource stats summary"""
        if not self.token:
            pytest.skip("Authentication failed")

        response = self.client.get(
            "/monitoring/host/stats-summary", headers=self.headers
        )

        # Check that the request was successful
        assert response.status_code == 200

        # Check that the response contains the expected fields
        data = response.json()
        assert "cpu_usage" in data
        assert "cpu_cores" in data
        assert "memory_usage_percent" in data
        assert "memory_used" in data
        assert "memory_total" in data
        assert "disk_usage_percent" in data
        assert "disk_used" in data
        assert "disk_total" in data
        assert "container_count" in data
        assert "running_containers" in data
        assert "image_count" in data
        assert "volume_count" in data
        assert "network_count" in data

        # Check that containers field is present and is a list
        assert "containers" in data
        assert isinstance(data["containers"], list)

        # If there are containers, check their structure
        if data["containers"]:
            container = data["containers"][0]
            assert "id" in container
            assert "name" in container
            assert "cpu_percent" in container
            assert "memory_percent" in container
            assert "memory_usage" in container

    def test_get_alerts(self):
        """Test getting alerts"""
        if not self.token:
            pytest.skip("Authentication failed")

        response = self.client.get("/monitoring/alerts", headers=self.headers)

        # Check that the request was successful
        assert response.status_code == 200

        # Check that the response is a list
        data = response.json()
        assert isinstance(data, list)

        # If there are alerts, check their structure
        if data:
            alert = data[0]
            assert "id" in alert
            assert "title" in alert
            assert "description" in alert
            assert "severity" in alert
            assert "timestamp" in alert
            assert "acknowledged" in alert
            assert "resolved" in alert
            assert "resource" in alert

            # Check resource structure
            resource = alert["resource"]
            assert "type" in resource
            assert "id" in resource
            assert "name" in resource

            # Check metrics structure if present
            if "metrics" in alert and alert["metrics"]:
                metric = alert["metrics"][0]
                assert "name" in metric
                assert "value" in metric
                assert "unit" in metric

    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        if not self.token:
            pytest.skip("Authentication failed")

        # First, get the list of alerts
        response = self.client.get("/monitoring/alerts", headers=self.headers)

        # Check that the request was successful
        assert response.status_code == 200

        # Get the alerts
        alerts = response.json()

        # If there are no alerts, skip the test
        if not alerts:
            pytest.skip("No alerts available for testing")

        # Get the first alert
        alert_id = alerts[0]["id"]

        # Acknowledge the alert
        response = self.client.post(
            f"/monitoring/alerts/{alert_id}/acknowledge", headers=self.headers
        )

        # Check that the request was successful
        assert response.status_code == 200

        # Check that the response contains the expected fields
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert data["status"] == "success"

        # Get the alerts again to check that the alert was acknowledged
        response = self.client.get("/monitoring/alerts", headers=self.headers)

        # Check that the request was successful
        assert response.status_code == 200

        # Get the alerts
        alerts = response.json()

        # Find the alert we acknowledged
        for alert in alerts:
            if alert["id"] == alert_id:
                assert alert["acknowledged"] is True
                break

    def test_resolve_alert(self):
        """Test resolving an alert"""
        if not self.token:
            pytest.skip("Authentication failed")

        # First, get the list of alerts
        response = self.client.get("/monitoring/alerts", headers=self.headers)

        # Check that the request was successful
        assert response.status_code == 200

        # Get the alerts
        alerts = response.json()

        # If there are no alerts, skip the test
        if not alerts:
            pytest.skip("No alerts available for testing")

        # Get the first alert
        alert_id = alerts[0]["id"]

        # Resolve the alert
        response = self.client.post(
            f"/monitoring/alerts/{alert_id}/resolve", headers=self.headers
        )

        # Check that the request was successful
        assert response.status_code == 200

        # Check that the response contains the expected fields
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert data["status"] == "success"

        # Get the alerts again to check that the alert was resolved
        response = self.client.get("/monitoring/alerts", headers=self.headers)

        # Check that the request was successful
        assert response.status_code == 200

        # Get the alerts
        alerts = response.json()

        # Check that the alert is no longer in the list
        for alert in alerts:
            assert alert["id"] != alert_id


if __name__ == "__main__":
    pytest.main(["-v", __file__])
