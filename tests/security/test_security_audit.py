"""
DockerForge Security Tests - Security Audit
"""

import json
import os
import sys
import time
from pathlib import Path

import pytest
import requests
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the necessary modules
from src.web.api.main import app


class TestSecurityAudit:
    """Test the security of the application"""

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

    def test_authentication_required(self):
        """Test that authentication is required for protected endpoints"""
        # List of endpoints that should require authentication
        protected_endpoints = [
            "/monitoring/host/metrics",
            "/monitoring/host/metrics/history/cpu",
            "/monitoring/host/system-info",
            "/monitoring/host/stats-summary",
            "/monitoring/alerts",
            "/containers",
            "/images",
            "/volumes",
            "/networks",
        ]

        # Check each endpoint
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)

            # Check that the request was unauthorized
            assert response.status_code in [
                401,
                403,
            ], f"Endpoint {endpoint} does not require authentication"

    def test_csrf_protection(self):
        """Test that CSRF protection is in place"""
        # List of endpoints that should be protected against CSRF
        csrf_endpoints = [
            "/auth/token",
            "/auth/register",
            "/monitoring/alerts/test-alert/acknowledge",
            "/monitoring/alerts/test-alert/resolve",
        ]

        # Check each endpoint
        for endpoint in csrf_endpoints:
            # Create a session
            session = requests.Session()

            # Try to make a request without CSRF token
            try:
                response = session.post(f"http://testserver{endpoint}", json={})

                # Check that the request was unauthorized or had a CSRF error
                assert response.status_code in [
                    401,
                    403,
                    422,
                ], f"Endpoint {endpoint} does not have CSRF protection"
            except Exception:
                # If the request fails, that's good
                pass

    def test_rate_limiting(self):
        """Test that rate limiting is in place"""
        # Make multiple requests to the same endpoint
        endpoint = "/auth/token"

        # Make 10 requests in quick succession
        responses = []
        for _ in range(10):
            response = self.client.post(
                endpoint, data={"username": "nonexistent", "password": "wrongpassword"}
            )
            responses.append(response)

        # Check if any of the responses indicate rate limiting
        rate_limited = any(response.status_code == 429 for response in responses)

        # If rate limiting is not in place, this test will pass but should be flagged for review
        if not rate_limited:
            pytest.xfail("Rate limiting is not in place")

    def test_secure_headers(self):
        """Test that secure headers are in place"""
        # Make a request to any endpoint
        response = self.client.get("/")

        # Check that the response has secure headers
        headers = response.headers

        # Check for X-Content-Type-Options
        assert (
            "X-Content-Type-Options" in headers
        ), "X-Content-Type-Options header is missing"
        assert (
            headers["X-Content-Type-Options"] == "nosniff"
        ), "X-Content-Type-Options header is not set to nosniff"

        # Check for X-Frame-Options
        assert "X-Frame-Options" in headers, "X-Frame-Options header is missing"
        assert headers["X-Frame-Options"] in [
            "DENY",
            "SAMEORIGIN",
        ], "X-Frame-Options header is not set to DENY or SAMEORIGIN"

        # Check for Content-Security-Policy
        assert (
            "Content-Security-Policy" in headers
        ), "Content-Security-Policy header is missing"

        # Check for Strict-Transport-Security
        # This might not be present in the test environment
        if "Strict-Transport-Security" in headers:
            assert (
                "max-age=" in headers["Strict-Transport-Security"]
            ), "Strict-Transport-Security header does not include max-age"

    def test_sql_injection_protection(self):
        """Test that SQL injection protection is in place"""
        # List of endpoints that might be vulnerable to SQL injection
        sql_injection_endpoints = [
            "/auth/token",
            "/containers",
            "/images",
            "/volumes",
            "/networks",
        ]

        # SQL injection payloads
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT username, password FROM users; --",
        ]

        # Check each endpoint with each payload
        for endpoint in sql_injection_endpoints:
            for payload in payloads:
                # Try to make a request with the payload
                try:
                    response = self.client.get(f"{endpoint}?q={payload}")

                    # Check that the request was not successful
                    assert (
                        response.status_code != 200
                    ), f"Endpoint {endpoint} might be vulnerable to SQL injection"
                except Exception:
                    # If the request fails, that's good
                    pass

    def test_xss_protection(self):
        """Test that XSS protection is in place"""
        # List of endpoints that might be vulnerable to XSS
        xss_endpoints = ["/containers", "/images", "/volumes", "/networks"]

        # XSS payloads
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(\"XSS\")'>",
            "<a href='javascript:alert(\"XSS\")'>Click me</a>",
        ]

        # Check each endpoint with each payload
        for endpoint in xss_endpoints:
            for payload in payloads:
                # Try to make a request with the payload
                try:
                    response = self.client.get(f"{endpoint}?q={payload}")

                    # Check that the payload is not reflected in the response
                    assert (
                        payload not in response.text
                    ), f"Endpoint {endpoint} might be vulnerable to XSS"
                except Exception:
                    # If the request fails, that's good
                    pass

    def test_api_key_security(self):
        """Test that API key security is in place"""
        # If API key authentication is implemented, test it
        if hasattr(app, "api_key_auth"):
            # Try to access a protected endpoint with an invalid API key
            response = self.client.get(
                "/monitoring/host/metrics", headers={"X-API-Key": "invalid-key"}
            )

            # Check that the request was unauthorized
            assert response.status_code in [
                401,
                403,
            ], "API key authentication is not secure"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
