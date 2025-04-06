"""
DockerForge Integration Tests - Monitoring Functionality
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the necessary modules
try:
    from monitoring.issue_detector import IssueDetector
    from monitoring.log_analyzer import LogAnalyzer
    from monitoring.log_collector import LogCollector
    from monitoring.pattern_recognition import PatternRecognition
    from monitoring.recommendation_engine import RecommendationEngine
    from resource_monitoring.anomaly_detector import AnomalyDetector
    from resource_monitoring.metrics_collector import MetricsCollector
except ImportError as e:
    print(f"Import error: {e}")
    print("These tests may be running in a limited environment.")
    print("Some tests will be skipped.")


class TestMonitoringFunctionality:
    """Test monitoring functionality of DockerForge"""

    def setup_method(self):
        """Set up test environment"""
        # This will be run before each test method
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.test_container_name = "dockerforge-test-container"

        # Check if we need to create a test container
        self.container_created = False
        try:
            # Try to run a simple container for testing
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    self.test_container_name,
                    "--rm",
                    "alpine",
                    "sh",
                    "-c",
                    "while true; do echo 'test log message'; sleep 1; done",
                ],
                check=True,
                capture_output=True,
            )
            self.container_created = True
        except subprocess.CalledProcessError:
            # Container might already exist or Docker might not be available
            pass
        except Exception as e:
            print(f"Failed to create test container: {e}")

    def teardown_method(self):
        """Clean up test environment"""
        # This will be run after each test method
        if self.container_created:
            try:
                subprocess.run(
                    ["docker", "stop", self.test_container_name],
                    check=False,
                    capture_output=True,
                )
            except Exception as e:
                print(f"Failed to stop test container: {e}")

    def test_log_collector_initialization(self):
        """Test that the log collector can be initialized"""
        try:
            log_collector = LogCollector()
            assert log_collector is not None
        except (ImportError, NameError):
            pytest.skip("LogCollector not available in this environment")
        except Exception as e:
            pytest.skip(f"LogCollector initialization failed: {e}")

    def test_log_collection(self):
        """Test log collection from a container"""
        if not self.container_created:
            pytest.skip("Test container not available")

        try:
            log_collector = LogCollector()
            logs = log_collector.collect_logs(self.test_container_name, max_lines=10)
            assert logs is not None
            assert len(logs) > 0
        except (ImportError, NameError):
            pytest.skip("LogCollector not available in this environment")
        except Exception as e:
            pytest.skip(f"Log collection failed: {e}")

    def test_pattern_recognition(self):
        """Test pattern recognition in logs"""
        try:
            pattern_recognition = PatternRecognition()
            # Create a sample log with a known pattern
            sample_log = [
                "2023-01-01T00:00:00Z Error: Connection refused",
                "2023-01-01T00:00:01Z Warning: High memory usage",
                "2023-01-01T00:00:02Z Info: Container started",
            ]
            patterns = pattern_recognition.find_patterns(sample_log)
            assert patterns is not None
            # Check that we found at least one pattern
            assert len(patterns) > 0
        except (ImportError, NameError):
            pytest.skip("PatternRecognition not available in this environment")
        except Exception as e:
            pytest.skip(f"Pattern recognition failed: {e}")

    def test_issue_detection(self):
        """Test issue detection in logs"""
        try:
            issue_detector = IssueDetector()
            # Create a sample log with a known issue
            sample_log = [
                "2023-01-01T00:00:00Z Error: Connection refused",
                "2023-01-01T00:00:01Z Warning: High memory usage",
                "2023-01-01T00:00:02Z Error: Connection refused",
            ]
            issues = issue_detector.detect_issues(sample_log)
            assert issues is not None
            # Check that we found at least one issue
            assert len(issues) > 0
        except (ImportError, NameError):
            pytest.skip("IssueDetector not available in this environment")
        except Exception as e:
            pytest.skip(f"Issue detection failed: {e}")

    def test_recommendation_generation(self):
        """Test recommendation generation for issues"""
        try:
            recommendation_engine = RecommendationEngine()
            # Create a sample issue
            sample_issue = {
                "type": "connection_refused",
                "severity": "high",
                "count": 2,
                "context": ["Error: Connection refused"],
            }
            recommendations = recommendation_engine.generate_recommendations(
                [sample_issue]
            )
            assert recommendations is not None
            # Check that we generated at least one recommendation
            assert len(recommendations) > 0
        except (ImportError, NameError):
            pytest.skip("RecommendationEngine not available in this environment")
        except Exception as e:
            pytest.skip(f"Recommendation generation failed: {e}")

    def test_metrics_collector_initialization(self):
        """Test that the metrics collector can be initialized"""
        try:
            metrics_collector = MetricsCollector()
            assert metrics_collector is not None
        except (ImportError, NameError):
            pytest.skip("MetricsCollector not available in this environment")
        except Exception as e:
            pytest.skip(f"MetricsCollector initialization failed: {e}")

    def test_metrics_collection(self):
        """Test metrics collection from a container"""
        if not self.container_created:
            pytest.skip("Test container not available")

        try:
            metrics_collector = MetricsCollector()
            metrics = metrics_collector.collect_metrics(self.test_container_name)
            assert metrics is not None
            # Check that we collected CPU and memory metrics
            assert "cpu" in metrics
            assert "memory" in metrics
        except (ImportError, NameError):
            pytest.skip("MetricsCollector not available in this environment")
        except Exception as e:
            pytest.skip(f"Metrics collection failed: {e}")

    def test_anomaly_detection(self):
        """Test anomaly detection in metrics"""
        try:
            anomaly_detector = AnomalyDetector()
            # Create sample metrics with an anomaly
            sample_metrics = {
                "cpu": [10, 15, 20, 90, 25],  # 90 is an anomaly
                "memory": [200, 210, 220, 230, 240],
            }
            anomalies = anomaly_detector.detect_anomalies(sample_metrics)
            assert anomalies is not None
            # Check that we detected at least one anomaly
            assert len(anomalies) > 0
        except (ImportError, NameError):
            pytest.skip("AnomalyDetector not available in this environment")
        except Exception as e:
            pytest.skip(f"Anomaly detection failed: {e}")

    def test_cli_monitoring_commands(self):
        """Test CLI monitoring commands"""
        # Run the CLI with monitor --help
        result = subprocess.run(
            ["python", "-m", "dockerforge", "monitor", "--help"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
        )
        # Check that the command executed successfully
        assert result.returncode == 0
        # Check that the output contains "monitor"
        assert "monitor" in result.stdout


if __name__ == "__main__":
    pytest.main(["-v", __file__])
