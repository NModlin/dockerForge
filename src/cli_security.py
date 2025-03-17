"""
Command-line interface for Docker security features.

This module provides a command-line interface for Docker security scanning,
auditing, and reporting.
"""

import argparse
import json
import logging
import os
import sys
from typing import List, Optional, Dict, Any

from src.utils.logging_manager import get_logger
from src.security import get_vulnerability_scanner, get_config_auditor, get_security_reporter

# Set up logging
logger = get_logger("cli_security")


def setup_vulnerability_scan_parser(subparsers):
    """Set up the vulnerability scan command parser."""
    parser = subparsers.add_parser(
        "scan",
        help="Scan Docker images for vulnerabilities"
    )
    parser.add_argument(
        "--image",
        help="Name of the Docker image to scan. If not provided, all images will be scanned."
    )
    parser.add_argument(
        "--severity",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"],
        nargs="+",
        help="Severity levels to include in the report."
    )
    parser.add_argument(
        "--format",
        choices=["json", "html", "text"],
        default="text",
        help="Output format for the report."
    )
    parser.add_argument(
        "--output",
        help="Output file for the report. If not provided, the report will be printed to stdout."
    )
    parser.add_argument(
        "--ignore-unfixed",
        action="store_true",
        help="Ignore vulnerabilities that don't have a fix."
    )
    parser.set_defaults(func=handle_vulnerability_scan)


def setup_audit_parser(subparsers):
    """Set up the audit command parser."""
    parser = subparsers.add_parser(
        "audit",
        help="Audit Docker configuration for security best practices"
    )
    parser.add_argument(
        "--check-type",
        choices=["host", "container", "daemon", "images", "networks", "registries"],
        help="Type of check to run. If not provided, all checks will be run."
    )
    parser.add_argument(
        "--format",
        choices=["json", "html", "text"],
        default="text",
        help="Output format for the report."
    )
    parser.add_argument(
        "--output",
        help="Output file for the report. If not provided, the report will be printed to stdout."
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Don't include a summary in the report."
    )
    parser.add_argument(
        "--no-remediation",
        action="store_true",
        help="Don't include remediation steps in the report."
    )
    parser.set_defaults(func=handle_audit)


def setup_report_parser(subparsers):
    """Set up the report command parser."""
    parser = subparsers.add_parser(
        "report",
        help="Generate a comprehensive security report"
    )
    parser.add_argument(
        "--image",
        help="Name of the Docker image to scan for vulnerabilities. If not provided, all images will be scanned."
    )
    parser.add_argument(
        "--check-type",
        choices=["host", "container", "daemon", "images", "networks", "registries"],
        help="Type of check to run for audit. If not provided, all checks will be run."
    )
    parser.add_argument(
        "--severity",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"],
        nargs="+",
        help="Severity levels to include in the vulnerability report."
    )
    parser.add_argument(
        "--format",
        choices=["json", "html", "text"],
        default="text",
        help="Output format for the report."
    )
    parser.add_argument(
        "--output",
        help="Output file for the report. If not provided, the report will be printed to stdout."
    )
    parser.set_defaults(func=handle_report)


def handle_vulnerability_scan(args):
    """Handle the vulnerability scan command."""
    try:
        # Get the vulnerability scanner
        scanner = get_vulnerability_scanner()
        
        # Generate the report
        report = scanner.get_security_reporter().generate_vulnerability_report(
            image_name=args.image,
            severity=args.severity,
            output_format=args.format,
            include_summary=True
        )
        
        # Output the report
        if args.output:
            # Save to file
            if args.format == "json":
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
            else:
                # Copy the appropriate file
                src_file = report.get("html_file" if args.format == "html" else "text_file")
                if src_file and os.path.exists(src_file):
                    import shutil
                    shutil.copy2(src_file, args.output)
                else:
                    logger.error(f"Report file not found: {src_file}")
                    return 1
        else:
            # Print to stdout
            if args.format == "json":
                print(json.dumps(report, indent=2))
            elif args.format == "html":
                print(f"HTML report saved to: {report.get('html_file')}")
            else:  # text
                if "text_file" in report:
                    with open(report["text_file"], "r") as f:
                        print(f.read())
                else:
                    print(f"Report saved to: {report.get('report_file')}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error scanning for vulnerabilities: {str(e)}")
        return 1


def handle_audit(args):
    """Handle the audit command."""
    try:
        # Get the config auditor
        auditor = get_config_auditor()
        
        # Generate the report
        report = auditor.get_security_reporter().generate_audit_report(
            check_type=args.check_type,
            output_format=args.format,
            include_summary=not args.no_summary,
            include_remediation=not args.no_remediation
        )
        
        # Output the report
        if args.output:
            # Save to file
            if args.format == "json":
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
            else:
                # Copy the appropriate file
                src_file = report.get("html_file" if args.format == "html" else "text_file")
                if src_file and os.path.exists(src_file):
                    import shutil
                    shutil.copy2(src_file, args.output)
                else:
                    logger.error(f"Report file not found: {src_file}")
                    return 1
        else:
            # Print to stdout
            if args.format == "json":
                print(json.dumps(report, indent=2))
            elif args.format == "html":
                print(f"HTML report saved to: {report.get('html_file')}")
            else:  # text
                if "text_file" in report:
                    with open(report["text_file"], "r") as f:
                        print(f.read())
                else:
                    print(f"Report saved to: {report.get('report_file')}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error auditing Docker configuration: {str(e)}")
        return 1


def handle_report(args):
    """Handle the report command."""
    try:
        # Get the security reporter
        reporter = get_security_reporter()
        
        # Generate the report
        report = reporter.generate_comprehensive_report(
            image_name=args.image,
            check_type=args.check_type,
            severity=args.severity,
            output_format=args.format
        )
        
        # Output the report
        if args.output:
            # Save to file
            if args.format == "json":
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
            else:
                # Copy the appropriate file
                src_file = report.get("html_file" if args.format == "html" else "text_file")
                if src_file and os.path.exists(src_file):
                    import shutil
                    shutil.copy2(src_file, args.output)
                else:
                    logger.error(f"Report file not found: {src_file}")
                    return 1
        else:
            # Print to stdout
            if args.format == "json":
                print(json.dumps(report, indent=2))
            elif args.format == "html":
                print(f"HTML report saved to: {report.get('html_file')}")
            else:  # text
                if "text_file" in report:
                    with open(report["text_file"], "r") as f:
                        print(f.read())
                else:
                    print(f"Report saved to: {report.get('report_file')}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {str(e)}")
        return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="DockerForge Security CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Set up subparsers
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Command to run"
    )
    subparsers.required = True
    
    # Set up command parsers
    setup_vulnerability_scan_parser(subparsers)
    setup_audit_parser(subparsers)
    setup_report_parser(subparsers)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
