"""
Configuration auditor module for DockerForge.

This module provides functionality to audit Docker configurations against
security best practices, including CIS Docker Benchmark checks.
"""

import json
import logging
import os
import re
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from src.config.config_manager import get_config
from src.docker.connection_manager import get_docker_client
from src.platforms.platform_detector import get_platform_info
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("security.config_auditor")


class ConfigAuditor:
    """
    Configuration auditor for Docker security best practices.
    """

    def __init__(self):
        """Initialize the configuration auditor."""
        self.docker_client = get_docker_client()
        self.config = get_config("security.config_auditor", {})
        self.platform_info = get_platform_info()
        self.docker_bench_path = self.config.get("docker_bench_path", "")
        self.results_dir = self.config.get(
            "results_dir", os.path.expanduser("~/.dockerforge/audit-results")
        )

        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)

    def check_docker_bench_installed(self) -> bool:
        """
        Check if Docker Bench Security is installed.

        Returns:
            bool: True if Docker Bench Security is installed, False otherwise.
        """
        if self.docker_bench_path and os.path.exists(self.docker_bench_path):
            return True

        # Check common locations
        common_paths = [
            os.path.expanduser("~/docker-bench-security/docker-bench-security.sh"),
            "/usr/local/bin/docker-bench-security",
            "/opt/docker-bench-security/docker-bench-security.sh",
        ]

        for path in common_paths:
            if os.path.exists(path):
                self.docker_bench_path = path
                return True

        return False

    def install_docker_bench(self) -> bool:
        """
        Install Docker Bench Security if not already installed.

        Returns:
            bool: True if installation was successful, False otherwise.
        """
        logger.info("Installing Docker Bench Security...")

        try:
            # Clone the repository
            clone_dir = os.path.expanduser("~/.dockerforge/docker-bench-security")

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(clone_dir), exist_ok=True)

            # Remove existing directory if it exists
            if os.path.exists(clone_dir):
                import shutil

                shutil.rmtree(clone_dir)

            # Clone the repository
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "https://github.com/docker/docker-bench-security.git",
                    clone_dir,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(
                    f"Failed to clone Docker Bench Security repository: {result.stderr}"
                )
                return False

            # Set the path
            self.docker_bench_path = os.path.join(clone_dir, "docker-bench-security.sh")

            # Make the script executable
            os.chmod(self.docker_bench_path, 0o755)

            logger.info("Docker Bench Security installed successfully")
            return True

        except Exception as e:
            logger.error(f"Error installing Docker Bench Security: {str(e)}")
            return False

    def run_docker_bench(
        self,
        check_type: Optional[str] = None,
        output_format: str = "json",
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Run Docker Bench Security to audit Docker configuration.

        Args:
            check_type: Type of check to run (container, daemon, etc.).
            output_format: Output format (json, txt).
            timeout: Timeout for the audit in seconds.

        Returns:
            Dict containing the audit results.
        """
        logger.info("Running Docker Bench Security audit")

        # Check if Docker Bench Security is installed
        if not self.check_docker_bench_installed():
            logger.warning("Docker Bench Security not found, attempting to install")
            if not self.install_docker_bench():
                raise RuntimeError(
                    "Failed to install Docker Bench Security. Please install it manually."
                )

        # Prepare command
        cmd = [self.docker_bench_path]

        # Add check type if provided
        if check_type:
            cmd.extend(["-c", check_type])

        # Add output format
        if output_format == "json":
            cmd.append("-j")

        # Create temporary file for output
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=f".{output_format}"
        ) as temp_file:
            temp_file_path = temp_file.name

        try:
            # Run Docker Bench Security
            logger.debug(f"Running command: {' '.join(cmd)}")

            # Docker Bench Security requires root privileges
            if self.platform_info.is_root:
                # Run as root
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            elif self.platform_info.has_sudo:
                # Run with sudo
                sudo_cmd = ["sudo"] + cmd
                result = subprocess.run(
                    sudo_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            else:
                # Cannot run with elevated privileges
                logger.error("Docker Bench Security requires root privileges")
                return {
                    "success": False,
                    "error": "Docker Bench Security requires root privileges",
                    "timestamp": datetime.now().isoformat(),
                }

            # Check for errors
            if result.returncode != 0:
                logger.error(f"Docker Bench Security audit failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "timestamp": datetime.now().isoformat(),
                }

            # Save output to file
            with open(temp_file_path, "w") as f:
                f.write(result.stdout)

            # Parse output
            if output_format == "json":
                try:
                    audit_result = json.loads(result.stdout)
                    audit_result["success"] = True
                    audit_result["timestamp"] = datetime.now().isoformat()

                    # Save result to results directory
                    result_file = os.path.join(
                        self.results_dir,
                        f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    )
                    with open(result_file, "w") as f:
                        json.dump(audit_result, f, indent=2)

                    return audit_result
                except json.JSONDecodeError as e:
                    logger.error(
                        f"Failed to parse Docker Bench Security output: {str(e)}"
                    )
                    return {
                        "success": False,
                        "error": f"Failed to parse Docker Bench Security output: {str(e)}",
                        "timestamp": datetime.now().isoformat(),
                    }
            else:
                # Save text output to results directory
                result_file = os.path.join(
                    self.results_dir,
                    f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                )
                with open(result_file, "w") as f:
                    f.write(result.stdout)

                # Return text output
                return {
                    "success": True,
                    "output": result.stdout,
                    "output_file": result_file,
                    "timestamp": datetime.now().isoformat(),
                }

        except subprocess.TimeoutExpired:
            logger.error(
                f"Docker Bench Security audit timed out after {timeout} seconds"
            )
            return {
                "success": False,
                "error": f"Audit timed out after {timeout} seconds",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error running Docker Bench Security audit: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def run_custom_audit(self, audit_checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run custom audit checks on Docker configuration.

        Args:
            audit_checks: List of audit checks to run.
                Each check should be a dict with the following keys:
                - id: Check ID
                - description: Check description
                - command: Command to run
                - expected_output: Expected output (regex)
                - remediation: Remediation steps

        Returns:
            Dict containing the audit results.
        """
        logger.info("Running custom Docker configuration audit")

        # Initialize results
        results = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "summary": {
                "total": len(audit_checks),
                "passed": 0,
                "failed": 0,
                "skipped": 0,
            },
        }

        # Run each check
        for check in audit_checks:
            check_id = check.get("id", "unknown")
            description = check.get("description", "")
            command = check.get("command", "")
            expected_output = check.get("expected_output", "")
            remediation = check.get("remediation", "")

            logger.debug(f"Running check {check_id}: {description}")

            # Skip if no command
            if not command:
                logger.warning(f"Skipping check {check_id}: No command specified")
                results["checks"].append(
                    {
                        "id": check_id,
                        "description": description,
                        "status": "skipped",
                        "reason": "No command specified",
                    }
                )
                results["summary"]["skipped"] += 1
                continue

            try:
                # Run command
                result = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )

                # Check output
                output = result.stdout.strip()
                if result.returncode != 0:
                    # Command failed
                    results["checks"].append(
                        {
                            "id": check_id,
                            "description": description,
                            "status": "failed",
                            "output": output,
                            "error": result.stderr.strip(),
                            "remediation": remediation,
                        }
                    )
                    results["summary"]["failed"] += 1
                elif expected_output and not re.search(
                    expected_output, output, re.MULTILINE
                ):
                    # Output doesn't match expected
                    results["checks"].append(
                        {
                            "id": check_id,
                            "description": description,
                            "status": "failed",
                            "output": output,
                            "expected": expected_output,
                            "remediation": remediation,
                        }
                    )
                    results["summary"]["failed"] += 1
                else:
                    # Check passed
                    results["checks"].append(
                        {
                            "id": check_id,
                            "description": description,
                            "status": "passed",
                            "output": output,
                        }
                    )
                    results["summary"]["passed"] += 1

            except Exception as e:
                logger.error(f"Error running check {check_id}: {str(e)}")
                results["checks"].append(
                    {
                        "id": check_id,
                        "description": description,
                        "status": "error",
                        "error": str(e),
                        "remediation": remediation,
                    }
                )
                results["summary"]["failed"] += 1

        # Save result to results directory
        result_file = os.path.join(
            self.results_dir,
            f"custom_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(result_file, "w") as f:
            json.dump(results, f, indent=2)

        return results

    def get_audit_summary(self, audit_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of audit results.

        Args:
            audit_result: Audit result from run_docker_bench() or run_custom_audit().

        Returns:
            Dict containing audit summary.
        """
        if not audit_result.get("success", False):
            return {
                "success": False,
                "error": audit_result.get("error", "Unknown error"),
                "timestamp": audit_result.get("timestamp", datetime.now().isoformat()),
            }

        # Initialize summary
        summary = {
            "success": True,
            "timestamp": audit_result.get("timestamp", datetime.now().isoformat()),
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "score": 0.0,
            "categories": {},
            "critical_issues": [],
        }

        # Process Docker Bench Security results
        if "tests" in audit_result:
            tests = audit_result["tests"]

            for test in tests:
                category = test.get("desc", "Unknown")
                summary["categories"][category] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "warnings": 0,
                    "score": 0.0,
                }

                for result in test.get("results", []):
                    summary["total_checks"] += 1
                    summary["categories"][category]["total"] += 1

                    status = result.get("result", "").lower()
                    if status == "pass":
                        summary["passed"] += 1
                        summary["categories"][category]["passed"] += 1
                    elif status == "warn":
                        summary["warnings"] += 1
                        summary["categories"][category]["warnings"] += 1
                    elif status == "fail":
                        summary["failed"] += 1
                        summary["categories"][category]["failed"] += 1

                        # Add to critical issues if level is high
                        if result.get("level", "").lower() == "level 1":
                            summary["critical_issues"].append(
                                {
                                    "id": result.get("id", "unknown"),
                                    "description": result.get("desc", ""),
                                    "remediation": result.get("remediation", ""),
                                }
                            )

                # Calculate category score
                if summary["categories"][category]["total"] > 0:
                    category_score = (
                        summary["categories"][category]["passed"]
                        / summary["categories"][category]["total"]
                    ) * 100
                    summary["categories"][category]["score"] = round(category_score, 2)

            # Calculate overall score
            if summary["total_checks"] > 0:
                overall_score = (summary["passed"] / summary["total_checks"]) * 100
                summary["score"] = round(overall_score, 2)

        # Process custom audit results
        elif "checks" in audit_result:
            checks = audit_result["checks"]
            summary["total_checks"] = len(checks)

            for check in checks:
                status = check.get("status", "").lower()
                if status == "passed":
                    summary["passed"] += 1
                elif status == "failed":
                    summary["failed"] += 1

                    # Add to critical issues
                    summary["critical_issues"].append(
                        {
                            "id": check.get("id", "unknown"),
                            "description": check.get("description", ""),
                            "remediation": check.get("remediation", ""),
                        }
                    )
                elif status == "warning":
                    summary["warnings"] += 1

            # Calculate overall score
            if summary["total_checks"] > 0:
                overall_score = (summary["passed"] / summary["total_checks"]) * 100
                summary["score"] = round(overall_score, 2)

        return summary

    def get_remediation_steps(
        self, audit_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate remediation steps for failed audit checks.

        Args:
            audit_result: Audit result from run_docker_bench() or run_custom_audit().

        Returns:
            List of remediation steps.
        """
        remediation_steps = []

        # Process Docker Bench Security results
        if "tests" in audit_result:
            tests = audit_result["tests"]

            for test in tests:
                for result in test.get("results", []):
                    if result.get("result", "").lower() == "fail":
                        remediation_steps.append(
                            {
                                "id": result.get("id", "unknown"),
                                "description": result.get("desc", ""),
                                "remediation": result.get("remediation", ""),
                                "level": result.get("level", "unknown"),
                            }
                        )

        # Process custom audit results
        elif "checks" in audit_result:
            checks = audit_result["checks"]

            for check in checks:
                if check.get("status", "").lower() == "failed":
                    remediation_steps.append(
                        {
                            "id": check.get("id", "unknown"),
                            "description": check.get("description", ""),
                            "remediation": check.get("remediation", ""),
                            "level": check.get("level", "unknown"),
                        }
                    )

        return remediation_steps

    def get_security_reporter(self):
        """
        Returns a SecurityReporter instance configured with the current audit settings.

        Returns:
            SecurityReporter: The security reporter instance.
        """
        # Import here to avoid circular imports
        from src.security.security_reporter import get_security_reporter

        reporter = get_security_reporter()

        # Configure the reporter with our settings
        reporter.docker_client = self.docker_client
        reporter.config.update(self.config)
        if hasattr(self, "audit_results"):
            reporter.audit_results = self.audit_results

        return reporter


# Singleton instance
_config_auditor = None


def get_config_auditor() -> ConfigAuditor:
    """
    Get the configuration auditor instance.

    Returns:
        ConfigAuditor: The configuration auditor instance.
    """
    global _config_auditor
    if _config_auditor is None:
        _config_auditor = ConfigAuditor()
    return _config_auditor
