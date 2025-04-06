"""
Additional methods for the SecurityReporter class.
"""


def _convert_to_html(self, report, report_type):
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

        # Define HTML template based on report type
        if report_type == "comprehensive":
            template_str = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Comprehensive Docker Security Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    h2 { color: #666; margin-top: 20px; }
                    h3 { color: #888; margin-top: 15px; }
                    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .critical { background-color: #ffdddd; }
                    .high { background-color: #ffffcc; }
                    .medium { background-color: #e6f3ff; }
                    .low { background-color: #f2f2f2; }
                    .pass { background-color: #dff0d8; }
                    .warn { background-color: #fcf8e3; }
                    .fail { background-color: #f2dede; }
                    .summary { margin-top: 20px; padding: 10px; background-color: #f9f9f9; border: 1px solid #ddd; }
                    .score { font-size: 24px; font-weight: bold; }
                    .good { color: green; }
                    .medium { color: orange; }
                    .bad { color: red; }
                    .section { margin-top: 30px; padding: 15px; border: 1px solid #ddd; }
                </style>
            </head>
            <body>
                <h1>Comprehensive Docker Security Report</h1>
                <p>Generated on: {{ report.timestamp }}</p>
                
                <div class="summary">
                    <h2>Executive Summary</h2>
                    <p>Overall Security Score: <span class="score {% if report.summary.overall_score >= 80 %}good{% elif report.summary.overall_score >= 60 %}medium{% else %}bad{% endif %}">{{ report.summary.overall_score }}%</span></p>
                    <p>Vulnerability Score: <span class="score {% if report.summary.vulnerability_score >= 80 %}good{% elif report.summary.vulnerability_score >= 60 %}medium{% else %}bad{% endif %}">{{ report.summary.vulnerability_score }}%</span></p>
                    <p>Audit Score: <span class="score {% if report.summary.audit_score >= 80 %}good{% elif report.summary.audit_score >= 60 %}medium{% else %}bad{% endif %}">{{ report.summary.audit_score }}%</span></p>
                    
                    {% if report.summary.critical_issues %}
                    <h3>Critical Issues</h3>
                    <table>
                        <tr>
                            <th>Type</th>
                            <th>ID</th>
                            <th>Severity</th>
                            <th>Title</th>
                            <th>Description</th>
                        </tr>
                        {% for issue in report.summary.critical_issues %}
                        <tr>
                            <td>{{ issue.type }}</td>
                            <td>{{ issue.id }}</td>
                            <td>{{ issue.severity }}</td>
                            <td>{{ issue.title }}</td>
                            <td>{{ issue.description }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}
                    
                    {% if report.summary.high_priority_remediation %}
                    <h3>High Priority Remediation</h3>
                    <table>
                        <tr>
                            <th>Type</th>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Description</th>
                        </tr>
                        {% for step in report.summary.high_priority_remediation %}
                        <tr>
                            <td>{{ step.type }}</td>
                            <td>{{ step.id }}</td>
                            <td>{{ step.title }}</td>
                            <td>{{ step.description }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}
                </div>
                
                <div class="section">
                    <h2>Vulnerability Report</h2>
                    <p>See detailed vulnerability report: <a href="{{ report.vulnerability_report.report_file }}">{{ report.vulnerability_report.report_file }}</a></p>
                </div>
                
                <div class="section">
                    <h2>Audit Report</h2>
                    <p>See detailed audit report: <a href="{{ report.audit_report.report_file }}">{{ report.audit_report.report_file }}</a></p>
                </div>
            </body>
            </html>
            """
        else:
            # Use existing templates for vulnerability and audit reports
            return "HTML template not defined for this report type"

        # Create template and render
        template = Template(template_str)
        return template.render(report=report)

    except Exception as e:
        self.logger.error(f"Error converting report to HTML: {str(e)}")
        return f"Error generating HTML report: {str(e)}"


def _convert_to_text(self, report, report_type):
    """
    Convert a report to text format.

    Args:
        report: Report data.
        report_type: Type of report (vulnerability, audit, comprehensive).

    Returns:
        Text string.
    """
    try:
        if report_type == "vulnerability":
            # Generate vulnerability report text
            text = []
            text.append("=== Docker Vulnerability Report ===")
            text.append(f"Generated on: {report['timestamp']}")
            text.append(f"Target: {report['target']}")
            text.append("")

            if report.get("summary"):
                text.append("--- Summary ---")
                if report["target"] == "all_images":
                    text.append(
                        f"Total Images: {report['summary'].get('total_images', 0)}"
                    )
                text.append(
                    f"Total Vulnerabilities: {report['summary'].get('total_vulnerabilities', 0)}"
                )
                text.append("Severity Counts:")
                for severity, count in (
                    report["summary"].get("severity_counts", {}).items()
                ):
                    text.append(f"  {severity}: {count}")
                text.append(
                    f"Fixable Vulnerabilities: {report['summary'].get('fixable_vulnerabilities', 0)}"
                )
                text.append("")

                if report["summary"].get("top_vulnerabilities"):
                    text.append("Top Vulnerabilities:")
                    for vuln in report["summary"]["top_vulnerabilities"]:
                        text.append(f"  ID: {vuln.get('id', 'unknown')}")
                        text.append(f"  Severity: {vuln.get('severity', 'unknown')}")
                        text.append(f"  Package: {vuln.get('package', 'unknown')}")
                        text.append(
                            f"  Installed Version: {vuln.get('installed_version', 'unknown')}"
                        )
                        text.append(f"  Fixed Version: {vuln.get('fixed_version', '')}")
                        text.append(f"  CVSS Score: {vuln.get('cvss_score', 0)}")
                        text.append(f"  Title: {vuln.get('title', '')}")
                        text.append("")

            text.append("--- Detailed Results ---")
            for image_id, result in report.get("results", {}).items():
                text.append(f"Image: {result.get('image', image_id)}")
                if result.get("success", False):
                    if "Results" in result:
                        for res in result["Results"]:
                            text.append(f"Target: {res.get('Target', 'unknown')}")
                            if "Vulnerabilities" in res and res["Vulnerabilities"]:
                                text.append(
                                    f"Vulnerabilities: {len(res['Vulnerabilities'])}"
                                )
                                for vuln in res["Vulnerabilities"][
                                    :10
                                ]:  # Show only first 10
                                    text.append(
                                        f"  {vuln.get('VulnerabilityID', 'unknown')}: {vuln.get('Title', '')}"
                                    )
                                    text.append(
                                        f"    Package: {vuln.get('PkgName', 'unknown')} {vuln.get('InstalledVersion', '')}"
                                    )
                                    text.append(
                                        f"    Severity: {vuln.get('Severity', 'unknown')}"
                                    )
                                    if vuln.get("FixedVersion"):
                                        text.append(
                                            f"    Fixed Version: {vuln.get('FixedVersion', '')}"
                                        )
                                    text.append("")
                                if len(res.get("Vulnerabilities", [])) > 10:
                                    text.append(
                                        f"  ... and {len(res['Vulnerabilities']) - 10} more vulnerabilities"
                                    )
                            else:
                                text.append("  No vulnerabilities found.")
                            text.append("")
                    else:
                        text.append("  No results available.")
                else:
                    text.append(f"  Error: {result.get('error', 'Unknown error')}")
                text.append("")

            return "\n".join(text)

        elif report_type == "audit":
            # Generate audit report text
            text = []
            text.append("=== Docker Configuration Audit Report ===")
            text.append(f"Generated on: {report['timestamp']}")
            text.append(f"Check Type: {report['check_type']}")
            text.append("")

            if report.get("summary"):
                text.append("--- Summary ---")
                text.append(f"Total Checks: {report['summary'].get('total_checks', 0)}")
                text.append(f"Passed: {report['summary'].get('passed', 0)}")
                text.append(f"Failed: {report['summary'].get('failed', 0)}")
                text.append(f"Warnings: {report['summary'].get('warnings', 0)}")
                text.append(f"Score: {report['summary'].get('score', 0)}%")
                text.append("")

                if report["summary"].get("categories"):
                    text.append("Categories:")
                    for category, stats in report["summary"]["categories"].items():
                        text.append(f"  {category}:")
                        text.append(f"    Total: {stats.get('total', 0)}")
                        text.append(f"    Passed: {stats.get('passed', 0)}")
                        text.append(f"    Failed: {stats.get('failed', 0)}")
                        text.append(f"    Warnings: {stats.get('warnings', 0)}")
                        text.append(f"    Score: {stats.get('score', 0)}%")
                        text.append("")

                if report["summary"].get("critical_issues"):
                    text.append("Critical Issues:")
                    for issue in report["summary"]["critical_issues"]:
                        text.append(f"  ID: {issue.get('id', 'unknown')}")
                        text.append(f"  Description: {issue.get('description', '')}")
                        text.append(f"  Remediation: {issue.get('remediation', '')}")
                        text.append("")

            if report.get("remediation_steps"):
                text.append("--- Remediation Steps ---")
                for step in report["remediation_steps"]:
                    text.append(f"ID: {step.get('id', 'unknown')}")
                    text.append(f"Description: {step.get('description', '')}")
                    text.append(f"Remediation: {step.get('remediation', '')}")
                    text.append(f"Level: {step.get('level', 'unknown')}")
                    text.append("")

            text.append("--- Detailed Results ---")
            if "tests" in report.get("results", {}):
                for test in report["results"]["tests"]:
                    text.append(f"Test: {test.get('desc', 'unknown')}")
                    for result in test.get("results", []):
                        text.append(f"  ID: {result.get('id', 'unknown')}")
                        text.append(f"  Description: {result.get('desc', '')}")
                        text.append(f"  Result: {result.get('result', 'unknown')}")
                        if result.get("remediation"):
                            text.append(
                                f"  Remediation: {result.get('remediation', '')}"
                            )
                        text.append("")
            elif "checks" in report.get("results", {}):
                for check in report["results"]["checks"]:
                    text.append(f"Check: {check.get('id', 'unknown')}")
                    text.append(f"  Description: {check.get('description', '')}")
                    text.append(f"  Status: {check.get('status', 'unknown')}")
                    text.append(f"  Output: {check.get('output', '')}")
                    if check.get("remediation"):
                        text.append(f"  Remediation: {check.get('remediation', '')}")
                    text.append("")
            else:
                text.append("No detailed results available.")

            return "\n".join(text)

        elif report_type == "comprehensive":
            # Generate comprehensive report text
            text = []
            text.append("=== Comprehensive Docker Security Report ===")
            text.append(f"Generated on: {report['timestamp']}")
            text.append("")

            text.append("--- Executive Summary ---")
            text.append(
                f"Overall Security Score: {report['summary'].get('overall_score', 0)}%"
            )
            text.append(
                f"Vulnerability Score: {report['summary'].get('vulnerability_score', 0)}%"
            )
            text.append(f"Audit Score: {report['summary'].get('audit_score', 0)}%")
            text.append("")

            if report["summary"].get("critical_issues"):
                text.append("Critical Issues:")
                for issue in report["summary"]["critical_issues"]:
                    text.append(f"  Type: {issue.get('type', 'unknown')}")
                    text.append(f"  ID: {issue.get('id', 'unknown')}")
                    text.append(f"  Severity: {issue.get('severity', 'unknown')}")
                    text.append(f"  Title: {issue.get('title', '')}")
                    text.append(f"  Description: {issue.get('description', '')}")
                    text.append("")

            if report["summary"].get("high_priority_remediation"):
                text.append("High Priority Remediation:")
                for step in report["summary"]["high_priority_remediation"]:
                    text.append(f"  Type: {step.get('type', 'unknown')}")
                    text.append(f"  ID: {step.get('id', 'unknown')}")
                    text.append(f"  Title: {step.get('title', '')}")
                    text.append(f"  Description: {step.get('description', '')}")
                    text.append("")

            text.append("--- Vulnerability Report ---")
            text.append(
                f"See detailed vulnerability report: {report.get('vulnerability_report', {}).get('report_file', 'N/A')}"
            )
            text.append("")

            text.append("--- Audit Report ---")
            text.append(
                f"See detailed audit report: {report.get('audit_report', {}).get('report_file', 'N/A')}"
            )

            return "\n".join(text)

        else:
            return f"Text conversion not implemented for report type: {report_type}"

    except Exception as e:
        self.logger.error(f"Error converting report to text: {str(e)}")
        return f"Error generating text report: {str(e)}"
