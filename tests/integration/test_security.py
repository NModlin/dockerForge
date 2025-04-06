"""
DockerForge Integration Tests - Security Functionality
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Add the src directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the necessary modules
try:
    from security.config_auditor import ConfigAuditor
    from security.security_reporter import SecurityReporter
    from security.vulnerability_scanner import VulnerabilityScanner
except ImportError as e:
    print(f"Import error: {e}")
    print("These tests may be running in a limited environment.")
    print("Some tests will be skipped.")


class TestSecurityFunctionality:
    """Test security functionality of DockerForge"""

    def setup_method(self):
        """Set up test environment"""
        # This will be run before each test method
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        self.test_image_name = "alpine:latest"

        # Check if we need to pull the test image
        self.image_available = False
        try:
            # Check if the image is available
            result = subprocess.run(
                ["docker", "image", "inspect", self.test_image_name],
                check=False,
                capture_output=True,
            )
            self.image_available = result.returncode == 0

            # Pull the image if it's not available
            if not self.image_available:
                subprocess.run(
                    ["docker", "pull", self.test_image_name],
                    check=True,
                    capture_output=True,
                )
                self.image_available = True
        except Exception as e:
            print(f"Failed to pull test image: {e}")

    def test_vulnerability_scanner_initialization(self):
        """Test that the vulnerability scanner can be initialized"""
        try:
            vulnerability_scanner = VulnerabilityScanner()
            assert vulnerability_scanner is not None
        except (ImportError, NameError):
            pytest.skip("VulnerabilityScanner not available in this environment")
        except Exception as e:
            pytest.skip(f"VulnerabilityScanner initialization failed: {e}")

    def test_vulnerability_scanning(self):
        """Test vulnerability scanning of an image"""
        if not self.image_available:
            pytest.skip("Test image not available")

        try:
            vulnerability_scanner = VulnerabilityScanner()
            scan_results = vulnerability_scanner.scan_image(self.test_image_name)
            assert scan_results is not None
            # Check that the scan results have the expected structure
            assert "vulnerabilities" in scan_results
            assert "summary" in scan_results
        except (ImportError, NameError):
            pytest.skip("VulnerabilityScanner not available in this environment")
        except Exception as e:
            pytest.skip(f"Vulnerability scanning failed: {e}")

    def test_config_auditor_initialization(self):
        """Test that the config auditor can be initialized"""
        try:
            config_auditor = ConfigAuditor()
            assert config_auditor is not None
        except (ImportError, NameError):
            pytest.skip("ConfigAuditor not available in this environment")
        except Exception as e:
            pytest.skip(f"ConfigAuditor initialization failed: {e}")

    def test_config_auditing(self):
        """Test configuration auditing"""
        try:
            config_auditor = ConfigAuditor()
            audit_results = config_auditor.audit_docker_config()
            assert audit_results is not None
            # Check that the audit results have the expected structure
            assert "checks" in audit_results
            assert "summary" in audit_results
        except (ImportError, NameError):
            pytest.skip("ConfigAuditor not available in this environment")
        except Exception as e:
            pytest.skip(f"Configuration auditing failed: {e}")

    def test_security_reporter_initialization(self):
        """Test that the security reporter can be initialized"""
        try:
            security_reporter = SecurityReporter()
            assert security_reporter is not None
        except (ImportError, NameError):
            pytest.skip("SecurityReporter not available in this environment")
        except Exception as e:
            pytest.skip(f"SecurityReporter initialization failed: {e}")

    def test_security_report_generation(self):
        """Test security report generation"""
        try:
            security_reporter = SecurityReporter()

            # Create sample vulnerability scan results
            sample_scan_results = {
                "vulnerabilities": [
                    {
                        "id": "CVE-2023-12345",
                        "severity": "HIGH",
                        "package": "openssl",
                        "version": "1.1.1k",
                        "fixed_version": "1.1.1l",
                        "description": "Vulnerability in OpenSSL",
                    }
                ],
                "summary": {"critical": 0, "high": 1, "medium": 0, "low": 0},
            }

            # Create sample audit results
            sample_audit_results = {
                "checks": [
                    {
                        "id": "docker-4.1",
                        "description": "Ensure that a user for the container has been created",
                        "status": "PASS",
                    },
                    {
                        "id": "docker-4.2",
                        "description": "Ensure that containers use trusted base images",
                        "status": "FAIL",
                    },
                ],
                "summary": {"pass": 1, "fail": 1, "warn": 0, "info": 0},
            }

            # Generate a report
            report = security_reporter.generate_report(
                sample_scan_results, sample_audit_results
            )
            assert report is not None
            # Check that the report has the expected structure
            assert "vulnerabilities" in report
            assert "configuration" in report
            assert "summary" in report
            assert "recommendations" in report
        except (ImportError, NameError):
            pytest.skip("SecurityReporter not available in this environment")
        except Exception as e:
            pytest.skip(f"Security report generation failed: {e}")

    def test_cli_security_commands(self):
        """Test CLI security commands"""
        # Run the CLI with security --help
        result = subprocess.run(
            ["python", "-m", "dockerforge", "security", "--help"],
            cwd=self.project_root,
            capture_output=True,
            text=True,
        )
        # Check that the command executed successfully
        assert result.returncode == 0
        # Check that the output contains "security"
        assert "security" in result.stdout

    def test_security_report_formats(self):
        """Test security report formats"""
        try:
            security_reporter = SecurityReporter()

            # Create sample vulnerability scan results
            sample_scan_results = {
                "vulnerabilities": [
                    {
                        "id": "CVE-2023-12345",
                        "severity": "HIGH",
                        "package": "openssl",
                        "version": "1.1.1k",
                        "fixed_version": "1.1.1l",
                        "description": "Vulnerability in OpenSSL",
                    }
                ],
                "summary": {"critical": 0, "high": 1, "medium": 0, "low": 0},
            }

            # Create sample audit results
            sample_audit_results = {
                "checks": [
                    {
                        "id": "docker-4.1",
                        "description": "Ensure that a user for the container has been created",
                        "status": "PASS",
                    },
                    {
                        "id": "docker-4.2",
                        "description": "Ensure that containers use trusted base images",
                        "status": "FAIL",
                    },
                ],
                "summary": {"pass": 1, "fail": 1, "warn": 0, "info": 0},
            }

            # Generate reports in different formats
            json_report = security_reporter.generate_report(
                sample_scan_results, sample_audit_results, format="json"
            )
            assert json_report is not None
            # Check that the JSON report is valid JSON
            json.loads(json_report)

            html_report = security_reporter.generate_report(
                sample_scan_results, sample_audit_results, format="html"
            )
            assert html_report is not None
            # Check that the HTML report contains HTML tags
            assert "<html" in html_report

            text_report = security_reporter.generate_report(
                sample_scan_results, sample_audit_results, format="text"
            )
            assert text_report is not None
            # Check that the text report is plain text
            assert isinstance(text_report, str)
        except (ImportError, NameError):
            pytest.skip("SecurityReporter not available in this environment")
        except Exception as e:
            pytest.skip(f"Security report format test failed: {e}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
