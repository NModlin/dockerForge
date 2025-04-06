"""
DockerForge Performance Tests - Performance Testing
"""

import pytest
import sys
import os
import json
import time
import statistics
import concurrent.futures
from pathlib import Path
from fastapi.testclient import TestClient

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the necessary modules
from src.web.api.main import app


class TestPerformance:
    """Test the performance of the application"""

    def setup_method(self):
        """Set up test environment"""
        self.client = TestClient(app)
        
        # Create a test user and get a token
        self.user_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        # Try to create a user (this might fail if the user already exists)
        try:
            self.client.post("/auth/register", json=self.user_data)
        except Exception:
            pass
        
        # Log in and get a token
        response = self.client.post("/auth/token", data={
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    def test_api_response_time(self):
        """Test the response time of API endpoints"""
        # List of endpoints to test
        endpoints = [
            "/monitoring/host/metrics",
            "/monitoring/host/system-info",
            "/monitoring/host/stats-summary",
            "/monitoring/alerts",
            "/containers",
            "/images",
            "/volumes",
            "/networks"
        ]
        
        # Number of requests to make for each endpoint
        num_requests = 10
        
        # Maximum acceptable response time in seconds
        max_response_time = 1.0
        
        # Test each endpoint
        for endpoint in endpoints:
            response_times = []
            
            for _ in range(num_requests):
                start_time = time.time()
                response = self.client.get(endpoint, headers=self.headers)
                end_time = time.time()
                
                # Calculate response time
                response_time = end_time - start_time
                response_times.append(response_time)
            
            # Calculate statistics
            avg_response_time = statistics.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            p95_time = sorted(response_times)[int(num_requests * 0.95)]
            
            # Print statistics
            print(f"Endpoint: {endpoint}")
            print(f"  Average response time: {avg_response_time:.3f} seconds")
            print(f"  Maximum response time: {max_time:.3f} seconds")
            print(f"  Minimum response time: {min_time:.3f} seconds")
            print(f"  95th percentile response time: {p95_time:.3f} seconds")
            
            # Check that the average response time is acceptable
            assert avg_response_time < max_response_time, f"Average response time for {endpoint} is too high: {avg_response_time:.3f} seconds"

    def test_concurrent_requests(self):
        """Test the performance of concurrent requests"""
        # Endpoint to test
        endpoint = "/monitoring/host/metrics"
        
        # Number of concurrent requests
        num_concurrent = 10
        
        # Maximum acceptable response time in seconds
        max_response_time = 2.0
        
        # Function to make a request
        def make_request():
            start_time = time.time()
            response = self.client.get(endpoint, headers=self.headers)
            end_time = time.time()
            
            # Calculate response time
            response_time = end_time - start_time
            
            return response_time
        
        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            response_times = list(executor.map(lambda _: make_request(), range(num_concurrent)))
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        p95_time = sorted(response_times)[int(num_concurrent * 0.95)]
        
        # Print statistics
        print(f"Concurrent requests to {endpoint}")
        print(f"  Number of concurrent requests: {num_concurrent}")
        print(f"  Average response time: {avg_response_time:.3f} seconds")
        print(f"  Maximum response time: {max_time:.3f} seconds")
        print(f"  Minimum response time: {min_time:.3f} seconds")
        print(f"  95th percentile response time: {p95_time:.3f} seconds")
        
        # Check that the average response time is acceptable
        assert avg_response_time < max_response_time, f"Average response time for concurrent requests to {endpoint} is too high: {avg_response_time:.3f} seconds"

    def test_database_performance(self):
        """Test the performance of database operations"""
        # This test is more complex and would require direct access to the database
        # For now, we'll just test the API endpoints that involve database operations
        
        # Endpoint to test
        endpoint = "/monitoring/host/metrics/history/cpu"
        
        # Number of requests to make
        num_requests = 5
        
        # Maximum acceptable response time in seconds
        max_response_time = 1.5
        
        # Test the endpoint
        response_times = []
        
        for _ in range(num_requests):
            start_time = time.time()
            response = self.client.get(endpoint, params={"hours": 24}, headers=self.headers)
            end_time = time.time()
            
            # Calculate response time
            response_time = end_time - start_time
            response_times.append(response_time)
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # Print statistics
        print(f"Database performance test for {endpoint}")
        print(f"  Average response time: {avg_response_time:.3f} seconds")
        print(f"  Maximum response time: {max_time:.3f} seconds")
        print(f"  Minimum response time: {min_time:.3f} seconds")
        
        # Check that the average response time is acceptable
        assert avg_response_time < max_response_time, f"Average response time for database operations is too high: {avg_response_time:.3f} seconds"

    def test_memory_usage(self):
        """Test the memory usage of the application"""
        # This test would require monitoring the memory usage of the application process
        # For now, we'll just make a note that this should be tested manually
        
        pytest.skip("Memory usage testing requires manual monitoring")

    def test_cpu_usage(self):
        """Test the CPU usage of the application"""
        # This test would require monitoring the CPU usage of the application process
        # For now, we'll just make a note that this should be tested manually
        
        pytest.skip("CPU usage testing requires manual monitoring")

    def test_load_testing(self):
        """Test the application under load"""
        # This test would require a load testing tool like Locust
        # For now, we'll just make a note that this should be tested separately
        
        pytest.skip("Load testing requires a separate tool like Locust")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
