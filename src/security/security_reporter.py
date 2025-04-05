"""
Security reporter module for DockerForge.

This module provides functionality to generate security reports based on
vulnerability scans and configuration audits.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time

from src.utils.logging_manager import get_logger
from src.config.config_manager import get_config
from src.security.vulnerability_scanner import get_vulnerability_scanner
from src.security.config_auditor import get_config_auditor

# Set up logging
logger = get_logger("security.security_reporter")


class SecurityReporter:
    """
    Security reporter for generating comprehensive security reports.
    """

    def __init__(self, docker_client=None, config=None, audit_results=None):
        """Initialize the security reporter.

        Args:
            docker_client: Docker client instance. If None, a new client will be created.
            config: Configuration dictionary. If None, default configuration will be used.
            audit_results: Audit results from a previous audit. If None, no audit results will be used.
        """
        self.config = config or get_config("security.security_reporter", {})
        self.reports_dir = self.config.get("reports_dir", os.path.expanduser("~/.dockerforge/security-reports"))
        self.vulnerability_scanner = get_vulnerability_scanner()
        self.config_auditor = get_config_auditor()
        self.docker_client = docker_client
        self.audit_results = audit_results
        self.logger = logger

        # Create reports directory if it doesn't exist
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_vulnerability_report(
        self,
        image_name: Optional[str] = None,
        severity: Optional[List[str]] = None,
        output_format: str = "json",
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a vulnerability report for a Docker image.

        Args:
            image_name: Name of the Docker image to scan. If None, scan all images.
            severity: List of severity levels to include (e.g., ["HIGH", "CRITICAL"]).
            output_format: Output format (json, html, text).
            include_summary: Whether to include a summary in the report.

        Returns:
            Dict containing the vulnerability report.
        """
        logger.info(f"Generating vulnerability report for {'all images' if image_name is None else image_name}")

        # Initialize report
        report = {
            "type": "vulnerability",
            "timestamp": datetime.now().isoformat(),
            "target": image_name or "all_images",
            "results": {},
            "summary": {}
        }

        try:
            # Scan image(s)
            if image_name:
                # Scan single image
                scan_result = self.vulnerability_scanner.scan_image(
                    image_name=image_name,
                    severity=severity,
                    output_format="json"  # Always use JSON for processing
                )
                report["results"] = {image_name: scan_result}

                # Generate summary if requested
                if include_summary:
                    report["summary"] = self.vulnerability_scanner.get_vulnerability_summary(scan_result)
            else:
                # Scan all images
                scan_results = self.vulnerability_scanner.scan_all_images(
                    severity=severity,
                    output_format="json"  # Always use JSON for processing
                )
                report["results"] = scan_results

                # Generate summary if requested
                if include_summary:
                    # Aggregate summaries
                    total_vulnerabilities = 0
                    severity_counts = {
                        "CRITICAL": 0,
                        "HIGH": 0,
                        "MEDIUM": 0,
                        "LOW": 0,
                        "UNKNOWN": 0
                    }
                    fixable_vulnerabilities = 0
                    top_vulnerabilities = []

                    for image_id, result in scan_results.items():
                        if result.get("success", False):
                            summary = self.vulnerability_scanner.get_vulnerability_summary(result)

                            # Aggregate counts
                            total_vulnerabilities += summary.get("total_vulnerabilities", 0)

                            for severity, count in summary.get("severity_counts", {}).items():
                                severity_counts[severity] += count

                            fixable_vulnerabilities += summary.get("fixable_vulnerabilities", 0)

                            # Add top vulnerabilities
                            for vuln in summary.get("top_vulnerabilities", []):
                                vuln["image"] = result.get("image", "unknown")
                                top_vulnerabilities.append(vuln)

                    # Sort top vulnerabilities by CVSS score
                    top_vulnerabilities = sorted(
                        top_vulnerabilities,
                        key=lambda v: v.get("cvss_score", 0),
                        reverse=True
                    )[:20]  # Limit to top 20

                    # Create aggregate summary
                    report["summary"] = {
                        "total_images": len(scan_results),
                        "total_vulnerabilities": total_vulnerabilities,
                        "severity_counts": severity_counts,
                        "fixable_vulnerabilities": fixable_vulnerabilities,
                        "top_vulnerabilities": top_vulnerabilities
                    }

            # Save report to file
            report_file = os.path.join(
                self.reports_dir,
                f"vulnerability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            # Convert to requested format
            if output_format == "html":
                html_report = self._convert_to_html(report, "vulnerability")
                html_file = os.path.join(
                    self.reports_dir,
                    f"vulnerability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                )
                with open(html_file, "w") as f:
                    f.write(html_report)
                report["html_file"] = html_file
            elif output_format == "text":
                text_report = self._convert_to_text(report, "vulnerability")
                text_file = os.path.join(
                    self.reports_dir,
                    f"vulnerability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                with open(text_file, "w") as f:
                    f.write(text_report)
                report["text_file"] = text_file

            report["report_file"] = report_file
            return report

        except Exception as e:
            logger.error(f"Error generating vulnerability report: {str(e)}")
            report["error"] = str(e)
            return report

    def generate_audit_report(
        self,
        check_type: Optional[str] = None,
        output_format: str = "json",
        include_summary: bool = True,
        include_remediation: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an audit report for Docker configuration.

        Args:
            check_type: Type of check to run (container, daemon, etc.).
            output_format: Output format (json, html, text).
            include_summary: Whether to include a summary in the report.
            include_remediation: Whether to include remediation steps in the report.

        Returns:
            Dict containing the audit report.
        """
        logger.info(f"Generating audit report for Docker configuration")

        # Initialize report
        report = {
            "type": "audit",
            "timestamp": datetime.now().isoformat(),
            "check_type": check_type or "all",
            "results": {},
            "summary": {},
            "remediation_steps": []
        }

        try:
            # Run audit
            audit_result = self.config_auditor.run_docker_bench(
                check_type=check_type,
                output_format="json"  # Always use JSON for processing
            )
            report["results"] = audit_result

            # Generate summary if requested
            if include_summary:
                report["summary"] = self.config_auditor.get_audit_summary(audit_result)

            # Generate remediation steps if requested
            if include_remediation:
                report["remediation_steps"] = self.config_auditor.get_remediation_steps(audit_result)

            # Save report to file
            report_file = os.path.join(
                self.reports_dir,
                f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            # Convert to requested format
            if output_format == "html":
                html_report = self._convert_to_html(report, "audit")
                html_file = os.path.join(
                    self.reports_dir,
                    f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                )
                with open(html_file, "w") as f:
                    f.write(html_report)
                report["html_file"] = html_file
            elif output_format == "text":
                text_report = self._convert_to_text(report, "audit")
                text_file = os.path.join(
                    self.reports_dir,
                    f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                with open(text_file, "w") as f:
                    f.write(text_report)
                report["text_file"] = text_file

            report["report_file"] = report_file
            return report

        except Exception as e:
            logger.error(f"Error generating audit report: {str(e)}")
            report["error"] = str(e)
            return report

    def generate_comprehensive_report(
        self,
        image_name: Optional[str] = None,
        check_type: Optional[str] = None,
        severity: Optional[List[str]] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive security report including vulnerabilities and audit.

        Args:
            image_name: Name of the Docker image to scan for vulnerabilities.
            check_type: Type of check to run for audit.
            severity: List of severity levels to include for vulnerabilities.
            output_format: Output format (json, html, text).

        Returns:
            Dict containing the comprehensive report.
        """
        logger.info(f"Generating comprehensive security report")

        # Initialize report
        report = {
            "type": "comprehensive",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vulnerability_report": {},
            "audit_report": {},
            "summary": {
                "overall_score": 0.0,
                "vulnerability_score": 0.0,
                "audit_score": 0.0,
                "critical_issues": [],
                "high_priority_remediation": []
            }
        }

        try:
            # Generate vulnerability report
            vulnerability_report = self.generate_vulnerability_report(
                image_name=image_name,
                severity=severity,
                output_format="json",  # Always use JSON for processing
                include_summary=True
            )
            report["vulnerability_report"] = vulnerability_report

            # Generate audit report
            audit_report = self.generate_audit_report(
                check_type=check_type,
                output_format="json",  # Always use JSON for processing
                include_summary=True,
                include_remediation=True
            )
            report["audit_report"] = audit_report

            # Generate overall summary
            vulnerability_summary = vulnerability_report.get("summary", {})
            audit_summary = audit_report.get("summary", {})

            # Calculate vulnerability score (0-100, higher is better)
            total_vulns = sum(vulnerability_summary.get("severity_counts", {}).values())
            if total_vulns > 0:
                # Weight vulnerabilities by severity
                weighted_score = (
                    vulnerability_summary.get("severity_counts", {}).get("CRITICAL", 0) * 10 +
                    vulnerability_summary.get("severity_counts", {}).get("HIGH", 0) * 5 +
                    vulnerability_summary.get("severity_counts", {}).get("MEDIUM", 0) * 2 +
                    vulnerability_summary.get("severity_counts", {}).get("LOW", 0) * 1
                )
                max_weighted_score = total_vulns * 10  # Worst case: all CRITICAL
                vulnerability_score = 100 - (weighted_score / max_weighted_score * 100)
            else:
                vulnerability_score = 100.0

            # Get audit score
            audit_score = audit_summary.get("score", 0.0)

            # Calculate overall score (average of vulnerability and audit scores)
            overall_score = (vulnerability_score + audit_score) / 2

            report["summary"]["vulnerability_score"] = round(vulnerability_score, 2)
            report["summary"]["audit_score"] = round(audit_score, 2)
            report["summary"]["overall_score"] = round(overall_score, 2)

            # Collect critical issues
            # Add top vulnerabilities
            for vuln in vulnerability_summary.get("top_vulnerabilities", [])[:5]:
                report["summary"]["critical_issues"].append({
                    "type": "vulnerability",
                    "id": vuln.get("id", "unknown"),
                    "severity": vuln.get("severity", "unknown"),
                    "title": vuln.get("title", ""),
                    "description": vuln.get("description", ""),
                    "affected_component": f"{vuln.get('package', 'unknown')} {vuln.get('installed_version', '')}"
                })

            # Add critical audit issues
            for issue in audit_summary.get("critical_issues", [])[:5]:
                report["summary"]["critical_issues"].append({
                    "type": "audit",
                    "id": issue.get("id", "unknown"),
                    "severity": "HIGH",
                    "title": issue.get("id", "unknown"),
                    "description": issue.get("description", "")
                })

            # Add high priority remediation steps
            # Add vulnerability fixes
            for vuln in vulnerability_summary.get("top_vulnerabilities", [])[:3]:
                if vuln.get("fixed_version"):
                    report["summary"]["high_priority_remediation"].append({
                        "type": "vulnerability",
                        "id": vuln.get("id", "unknown"),
                        "title": f"Update {vuln.get('package', 'unknown')} to {vuln.get('fixed_version', '')}",
                        "description": f"Update {vuln.get('package', 'unknown')} from {vuln.get('installed_version', '')} to {vuln.get('fixed_version', '')} to fix {vuln.get('id', 'unknown')}"
                    })

            # Add audit remediation steps
            for step in audit_report.get("remediation_steps", [])[:5]:
                report["summary"]["high_priority_remediation"].append({
                    "type": "audit",
                    "id": step.get("id", "unknown"),
                    "title": step.get("id", "unknown"),
                    "description": step.get("remediation", "")
                })

            # Save report to file
            report_file = os.path.join(
                self.reports_dir,
                f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            # Convert to requested format
            if output_format == "html":
                html_report = self._convert_to_html(report, "comprehensive")
                html_file = os.path.join(
                    self.reports_dir,
                    f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                )
                with open(html_file, "w") as f:
                    f.write(html_report)
                report["html_file"] = html_file
            elif output_format == "text":
                text_report = self._convert_to_text(report, "comprehensive")
                text_file = os.path.join(
                    self.reports_dir,
                    f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                with open(text_file, "w") as f:
                    f.write(text_report)
                report["text_file"] = text_file

            report["report_file"] = report_file
            return report

        except Exception as e:
            logger.error(f"Error generating comprehensive report: {str(e)}")
            report["error"] = str(e)
            return report

    def _convert_to_html(self, report: Dict[str, Any], report_type: str) -> str:
        """
        Convert a report to HTML format.

        Args:
            report: Report data.
            report_type: Type of report (vulnerability, audit, comprehensive).

        Returns:
            HTML string.
        """
        try:
            # Import Jinja2 for templating
            from jinja2 import Template

            # Create a simple HTML template
            template_str = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Docker Security Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    h2 { color: #666; margin-top: 20px; }
                    pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Docker Security Report: {{ report_type }}</h1>
                <h2>Generated on: {{ timestamp }}</h2>
                <pre>{{ content }}</pre>
            </body>
            </html>
            """

            # Create template and render
            template = Template(template_str)
            return template.render(
                report_type=report_type.capitalize(),
                timestamp=report.get("timestamp", datetime.now().isoformat()),
                content=json.dumps(report, indent=2)
            )
        except Exception as e:
            self.logger.error(f"Error converting report to HTML: {str(e)}")
            return f"Error generating HTML report: {str(e)}"

    def _convert_to_text(self, report: Dict[str, Any], report_type: str) -> str:
        """
        Convert a report to text format.

        Args:
            report: Report data.
            report_type: Type of report (vulnerability, audit, comprehensive).

        Returns:
            Text string.
        """
        try:
            # Create a simple text report
            text = []
            text.append(f"=== Docker {report_type.capitalize()} Report ===")
            text.append(f"Generated on: {report.get('timestamp', datetime.now().isoformat())}")
            text.append("")

            # Add summary if available
            if "summary" in report:
                text.append("--- Summary ---")
                if report_type == "vulnerability":
                    text.append(f"Total Vulnerabilities: {report['summary'].get('total_vulnerabilities', 0)}")
                    text.append("Severity Counts:")
                    for severity, count in report["summary"].get("severity_counts", {}).items():
                        text.append(f"  {severity}: {count}")
                elif report_type == "audit":
                    text.append(f"Total Checks: {report['summary'].get('total_checks', 0)}")
                    text.append(f"Passed: {report['summary'].get('passed', 0)}")
                    text.append(f"Failed: {report['summary'].get('failed', 0)}")
                    text.append(f"Score: {report['summary'].get('score', 0)}%")
                elif report_type == "comprehensive":
                    text.append(f"Overall Score: {report['summary'].get('overall_score', 0)}%")
                    text.append(f"Vulnerability Score: {report['summary'].get('vulnerability_score', 0)}%")
                    text.append(f"Audit Score: {report['summary'].get('audit_score', 0)}%")
                text.append("")

            # Add report file path
            if "report_file" in report:
                text.append(f"Full report saved to: {report['report_file']}")

            return "\n".join(text)
        except Exception as e:
            self.logger.error(f"Error converting report to text: {str(e)}")
            return f"Error generating text report: {str(e)}"


# Singleton instance
_security_reporter = None


def get_security_reporter() -> SecurityReporter:
    """
    Get the security reporter instance.

    Returns:
        SecurityReporter: The security reporter instance.
    """
    global _security_reporter
    if _security_reporter is None:
        _security_reporter = SecurityReporter()
    return _security_reporter
