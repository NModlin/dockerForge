"""
DockerForge Resource Monitoring CLI

This module provides a command-line interface for the resource monitoring system,
allowing users to start/stop the monitoring daemon, view metrics, anomalies,
and optimization recommendations.
"""

import argparse
import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import textwrap

from src.config.config_manager import ConfigManager
from src.docker.connection_manager_adapter import ConnectionManager
from src.resource_monitoring.daemon_manager import DaemonManager
from src.notifications.notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class ResourceMonitoringCLI:
    """
    Command-line interface for the resource monitoring system.
    """

    def __init__(self):
        """
        Initialize the CLI.
        """
        self.config_manager = ConfigManager()
        self.connection_manager = ConnectionManager(self.config_manager)
        self.notification_manager = NotificationManager(self.config_manager)
        self.daemon_manager = DaemonManager(
            self.config_manager,
            self.connection_manager,
            self.notification_manager
        )

    def parse_args(self, args: List[str]) -> argparse.Namespace:
        """
        Parse command-line arguments.

        Args:
            args: Command-line arguments

        Returns:
            Parsed arguments
        """
        parser = argparse.ArgumentParser(
            description="DockerForge Resource Monitoring CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent("""
                Examples:
                  # Start the monitoring daemon
                  python -m src.cli_resource_monitoring start

                  # Start the monitoring daemon in the foreground
                  python -m src.cli_resource_monitoring start --foreground

                  # Stop the monitoring daemon
                  python -m src.cli_resource_monitoring stop

                  # Show the daemon status
                  python -m src.cli_resource_monitoring status

                  # Show metrics for all containers
                  python -m src.cli_resource_monitoring metrics

                  # Show CPU metrics for a specific container
                  python -m src.cli_resource_monitoring metrics --container-id abc123 --metric-type cpu

                  # Show anomalies
                  python -m src.cli_resource_monitoring anomalies

                  # Show optimization recommendations
                  python -m src.cli_resource_monitoring recommendations

                  # Generate an optimization report
                  python -m src.cli_resource_monitoring report

                  # Generate an HTML optimization report for a specific container
                  python -m src.cli_resource_monitoring report --container-id abc123 --format html --output report.html
            """)
        )

        subparsers = parser.add_subparsers(dest='command', help='Command to execute')

        # Start command
        start_parser = subparsers.add_parser('start', help='Start the monitoring daemon')
        start_parser.add_argument('--foreground', action='store_true', help='Run in the foreground')

        # Stop command
        stop_parser = subparsers.add_parser('stop', help='Stop the monitoring daemon')

        # Restart command
        restart_parser = subparsers.add_parser('restart', help='Restart the monitoring daemon')
        restart_parser.add_argument('--foreground', action='store_true', help='Run in the foreground')

        # Status command
        status_parser = subparsers.add_parser('status', help='Show the daemon status')
        status_parser.add_argument('--json', action='store_true', help='Output in JSON format')

        # Metrics command
        metrics_parser = subparsers.add_parser('metrics', help='Show container metrics')
        metrics_parser.add_argument('--container-id', help='Container ID to filter by')
        metrics_parser.add_argument('--metric-type', choices=['cpu', 'memory', 'disk', 'network'], help='Metric type to filter by')
        metrics_parser.add_argument('--start-time', help='Start time (ISO format)')
        metrics_parser.add_argument('--end-time', help='End time (ISO format)')
        metrics_parser.add_argument('--json', action='store_true', help='Output in JSON format')

        # Anomalies command
        anomalies_parser = subparsers.add_parser('anomalies', help='Show detected anomalies')
        anomalies_parser.add_argument('--container-id', help='Container ID to filter by')
        anomalies_parser.add_argument('--metric-type', choices=['cpu', 'memory', 'disk', 'network'], help='Metric type to filter by')
        anomalies_parser.add_argument('--start-time', help='Start time (ISO format)')
        anomalies_parser.add_argument('--end-time', help='End time (ISO format)')
        anomalies_parser.add_argument('--severity', type=int, choices=[1, 2, 3], help='Severity level to filter by')
        anomalies_parser.add_argument('--json', action='store_true', help='Output in JSON format')

        # Recommendations command
        recommendations_parser = subparsers.add_parser('recommendations', help='Show optimization recommendations')
        recommendations_parser.add_argument('--container-id', help='Container ID to filter by')
        recommendations_parser.add_argument('--type', choices=['sizing', 'performance', 'cost'], help='Recommendation type to filter by')
        recommendations_parser.add_argument('--resource', choices=['cpu', 'memory', 'disk', 'network', 'general'], help='Resource type to filter by')
        recommendations_parser.add_argument('--start-time', help='Start time (ISO format)')
        recommendations_parser.add_argument('--end-time', help='End time (ISO format)')
        recommendations_parser.add_argument('--json', action='store_true', help='Output in JSON format')

        # Report command
        report_parser = subparsers.add_parser('report', help='Generate an optimization report')
        report_parser.add_argument('--container-id', help='Container ID to filter by')
        report_parser.add_argument('--format', choices=['text', 'json', 'html'], default='text', help='Output format')
        report_parser.add_argument('--output', help='Output file path')

        return parser.parse_args(args)

    def run(self, args: List[str]) -> int:
        """
        Run the CLI with the given arguments.

        Args:
            args: Command-line arguments

        Returns:
            Exit code
        """
        parsed_args = self.parse_args(args)

        if not parsed_args.command:
            print("Error: No command specified")
            return 1

        try:
            # Execute the appropriate command
            if parsed_args.command == 'start':
                return self.start_daemon(parsed_args.foreground)
            elif parsed_args.command == 'stop':
                return self.stop_daemon()
            elif parsed_args.command == 'restart':
                return self.restart_daemon(parsed_args.foreground)
            elif parsed_args.command == 'status':
                return self.show_status(parsed_args.json)
            elif parsed_args.command == 'metrics':
                return self.show_metrics(
                    parsed_args.container_id,
                    parsed_args.metric_type,
                    parsed_args.start_time,
                    parsed_args.end_time,
                    parsed_args.json
                )
            elif parsed_args.command == 'anomalies':
                return self.show_anomalies(
                    parsed_args.container_id,
                    parsed_args.metric_type,
                    parsed_args.start_time,
                    parsed_args.end_time,
                    parsed_args.severity,
                    parsed_args.json
                )
            elif parsed_args.command == 'recommendations':
                return self.show_recommendations(
                    parsed_args.container_id,
                    getattr(parsed_args, 'type', None),  # 'type' is a Python keyword
                    parsed_args.resource,
                    parsed_args.start_time,
                    parsed_args.end_time,
                    parsed_args.json
                )
            elif parsed_args.command == 'report':
                return self.generate_report(
                    parsed_args.container_id,
                    parsed_args.format,
                    parsed_args.output
                )
            else:
                print(f"Error: Unknown command '{parsed_args.command}'")
                return 1
        except Exception as e:
            print(f"Error: {e}")
            logger.exception("Error executing command")
            return 1

    def start_daemon(self, foreground: bool = False) -> int:
        """
        Start the monitoring daemon.

        Args:
            foreground: Whether to run in the foreground

        Returns:
            Exit code
        """
        if self.daemon_manager.is_running():
            print("Daemon is already running")
            return 0

        print(f"Starting monitoring daemon{' in foreground' if foreground else ''}...")
        self.daemon_manager.start(foreground)

        if not foreground:
            # Wait a bit for the daemon to start
            time.sleep(1)

            if self.daemon_manager.is_running():
                print("Daemon started successfully")
                return 0
            else:
                print("Failed to start daemon")
                return 1

        return 0

    def stop_daemon(self) -> int:
        """
        Stop the monitoring daemon.

        Returns:
            Exit code
        """
        if not self.daemon_manager.is_running():
            print("Daemon is not running")
            return 0

        print("Stopping monitoring daemon...")
        self.daemon_manager.stop()

        # Wait a bit for the daemon to stop
        time.sleep(1)

        if not self.daemon_manager.is_running():
            print("Daemon stopped successfully")
            return 0
        else:
            print("Failed to stop daemon")
            return 1

    def restart_daemon(self, foreground: bool = False) -> int:
        """
        Restart the monitoring daemon.

        Args:
            foreground: Whether to run in the foreground

        Returns:
            Exit code
        """
        print(f"Restarting monitoring daemon{' in foreground' if foreground else ''}...")
        self.daemon_manager.restart(foreground)

        if not foreground:
            # Wait a bit for the daemon to restart
            time.sleep(1)

            if self.daemon_manager.is_running():
                print("Daemon restarted successfully")
                return 0
            else:
                print("Failed to restart daemon")
                return 1

        return 0

    def show_status(self, json_output: bool = False) -> int:
        """
        Show the daemon status.

        Args:
            json_output: Whether to output in JSON format

        Returns:
            Exit code
        """
        if not self.daemon_manager.is_running():
            if json_output:
                print(json.dumps({'running': False}, indent=2))
            else:
                print("Daemon is not running")
            return 0

        status = self.daemon_manager.get_status()

        if json_output:
            print(json.dumps(status, indent=2))
        else:
            print("Daemon Status:")
            print(f"  Running: {status['running']}")
            print(f"  PID: {status['pid']}")
            print(f"  Last Updated: {datetime.fromtimestamp(status['last_updated']).strftime('%Y-%m-%d %H:%M:%S')}")
            print("\nComponents:")

            for component, component_status in status['components'].items():
                print(f"  {component.replace('_', ' ').title()}:")
                for key, value in component_status.items():
                    print(f"    {key.replace('_', ' ').title()}: {value}")

        return 0

    def show_metrics(self, container_id: Optional[str] = None,
                    metric_type: Optional[str] = None,
                    start_time: Optional[str] = None,
                    end_time: Optional[str] = None,
                    json_output: bool = False) -> int:
        """
        Show container metrics.

        Args:
            container_id: Container ID to filter by
            metric_type: Metric type to filter by
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            json_output: Whether to output in JSON format

        Returns:
            Exit code
        """
        if not self.daemon_manager.is_running():
            print("Error: Daemon is not running")
            return 1

        metrics = self.daemon_manager.get_metrics(
            container_id=container_id,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time
        )

        if not metrics:
            print("No metrics found")
            return 0

        if json_output:
            print(json.dumps(metrics, indent=2))
        else:
            print("Container Metrics:")

            for container_id, container_metrics in metrics.items():
                print(f"\nContainer: {container_id}")

                for metric_type, metric_data in container_metrics.items():
                    print(f"  {metric_type.capitalize()} Metrics:")

                    for i, entry in enumerate(metric_data[:5]):  # Show only the first 5 entries
                        print(f"    Entry {i+1}:")
                        print(f"      Timestamp: {entry['timestamp']}")
                        print(f"      Data: {json.dumps(entry['data'], indent=8)[:100]}...")

                    if len(metric_data) > 5:
                        print(f"    ... and {len(metric_data) - 5} more entries")

        return 0

    def show_anomalies(self, container_id: Optional[str] = None,
                      metric_type: Optional[str] = None,
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      severity: Optional[int] = None,
                      json_output: bool = False) -> int:
        """
        Show detected anomalies.

        Args:
            container_id: Container ID to filter by
            metric_type: Metric type to filter by
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            severity: Severity level to filter by
            json_output: Whether to output in JSON format

        Returns:
            Exit code
        """
        if not self.daemon_manager.is_running():
            print("Error: Daemon is not running")
            return 1

        anomalies = self.daemon_manager.get_anomalies(
            container_id=container_id,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
            severity=severity
        )

        if not anomalies:
            print("No anomalies found")
            return 0

        if json_output:
            print(json.dumps(anomalies, indent=2))
        else:
            print("Detected Anomalies:")

            for container_id, container_anomalies in anomalies.items():
                print(f"\nContainer: {container_id}")
                print(f"  Total Anomalies: {len(container_anomalies)}")

                # Group anomalies by type
                anomalies_by_type = {}
                for anomaly in container_anomalies:
                    anomaly_type = anomaly.get('type', 'unknown')
                    if anomaly_type not in anomalies_by_type:
                        anomalies_by_type[anomaly_type] = []
                    anomalies_by_type[anomaly_type].append(anomaly)

                for anomaly_type, type_anomalies in anomalies_by_type.items():
                    print(f"  {anomaly_type.capitalize()} Anomalies: {len(type_anomalies)}")

                    for i, anomaly in enumerate(type_anomalies[:3]):  # Show only the first 3 anomalies of each type
                        print(f"    {i+1}. {anomaly.get('description', 'No description')}")
                        print(f"       Timestamp: {anomaly.get('timestamp', 'Unknown')}")
                        print(f"       Severity: {anomaly.get('severity', 'Unknown')}")
                        print(f"       Metric Type: {anomaly.get('metric_type', 'Unknown')}")

                    if len(type_anomalies) > 3:
                        print(f"    ... and {len(type_anomalies) - 3} more {anomaly_type} anomalies")

        return 0

    def show_recommendations(self, container_id: Optional[str] = None,
                            recommendation_type: Optional[str] = None,
                            resource: Optional[str] = None,
                            start_time: Optional[str] = None,
                            end_time: Optional[str] = None,
                            json_output: bool = False) -> int:
        """
        Show optimization recommendations.

        Args:
            container_id: Container ID to filter by
            recommendation_type: Recommendation type to filter by
            resource: Resource type to filter by
            start_time: Start time (ISO format)
            end_time: End time (ISO format)
            json_output: Whether to output in JSON format

        Returns:
            Exit code
        """
        if not self.daemon_manager.is_running():
            print("Error: Daemon is not running")
            return 1

        recommendations = self.daemon_manager.get_recommendations(
            container_id=container_id,
            recommendation_type=recommendation_type,
            resource=resource,
            start_time=start_time,
            end_time=end_time
        )

        if not recommendations:
            print("No recommendations found")
            return 0

        if json_output:
            print(json.dumps(recommendations, indent=2))
        else:
            print("Optimization Recommendations:")

            for container_id, container_recs in recommendations.items():
                print(f"\nContainer: {container_id}")
                print(f"  Total Recommendations: {len(container_recs)}")

                # Group recommendations by type
                recs_by_type = {}
                for rec in container_recs:
                    rec_type = rec.get('type', 'unknown')
                    if rec_type not in recs_by_type:
                        recs_by_type[rec_type] = []
                    recs_by_type[rec_type].append(rec)

                for rec_type, type_recs in recs_by_type.items():
                    print(f"  {rec_type.capitalize()} Recommendations: {len(type_recs)}")

                    for i, rec in enumerate(type_recs[:3]):  # Show only the first 3 recommendations of each type
                        print(f"    {i+1}. {rec.get('description', 'No description')}")
                        print(f"       Impact: {rec.get('impact', 'Unknown')}")
                        print(f"       Resource: {rec.get('resource', 'Unknown')}")

                        if 'command' in rec:
                            print(f"       Command: {rec['command']}")

                        if 'suggestions' in rec:
                            print("       Suggestions:")
                            for suggestion in rec['suggestions'][:2]:  # Show only the first 2 suggestions
                                print(f"         - {suggestion}")
                            if len(rec['suggestions']) > 2:
                                print(f"         ... and {len(rec['suggestions']) - 2} more suggestions")

                    if len(type_recs) > 3:
                        print(f"    ... and {len(type_recs) - 3} more {rec_type} recommendations")

        return 0

    def generate_report(self, container_id: Optional[str] = None,
                       format: str = 'text',
                       output_file: Optional[str] = None) -> int:
        """
        Generate an optimization report.

        Args:
            container_id: Container ID to filter by
            format: Output format
            output_file: Output file path

        Returns:
            Exit code
        """
        if not self.daemon_manager.is_running():
            print("Error: Daemon is not running")
            return 1

        report = self.daemon_manager.generate_optimization_report(
            container_id=container_id,
            format=format
        )

        if not report or report == "No optimization recommendations available.":
            print("No optimization recommendations available")
            return 0

        if output_file:
            # Write report to file
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report written to {output_file}")
        else:
            # Print report to stdout
            print(report)

        return 0

def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code
    """
    cli = ResourceMonitoringCLI()
    return cli.run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())
