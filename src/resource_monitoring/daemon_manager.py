"""
DockerForge Resource Monitoring Daemon Manager

This module provides functionality for managing the resource monitoring daemon,
including starting, stopping, and configuring the various components of the
resource monitoring system.
"""

import atexit
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from src.config.config_manager import ConfigManager
from src.docker.connection_manager_adapter import ConnectionManager
from src.notifications.notification_manager import NotificationManager
from src.resource_monitoring.anomaly_detector import AnomalyDetector
from src.resource_monitoring.metrics_collector import MetricsCollector
from src.resource_monitoring.optimization_engine import OptimizationEngine

logger = logging.getLogger(__name__)


class DaemonManager:
    """
    Manages the resource monitoring daemon.

    This class handles:
    - Starting and stopping the daemon
    - Configuring the monitoring components
    - Managing the lifecycle of the monitoring system
    - Handling signals and graceful shutdown
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        connection_manager: ConnectionManager,
        notification_manager: Optional[NotificationManager] = None,
    ):
        """
        Initialize the daemon manager.

        Args:
            config_manager: The configuration manager instance
            connection_manager: The Docker connection manager instance
            notification_manager: Optional notification manager for sending alerts
        """
        self.config_manager = config_manager
        self.config = config_manager.config if hasattr(config_manager, "config") else {}
        self.connection_manager = connection_manager
        self.notification_manager = notification_manager

        # Daemon configuration
        self.daemon_config = self.config.get("resource_monitoring", {}).get(
            "daemon", {}
        )
        self.pid_file = self.daemon_config.get("pid_file", "~/.dockerforge/daemon.pid")
        self.pid_file = os.path.expanduser(self.pid_file)
        self.log_file = self.daemon_config.get("log_file", "~/.dockerforge/daemon.log")
        self.log_file = os.path.expanduser(self.log_file)
        self.status_file = self.daemon_config.get(
            "status_file", "~/.dockerforge/daemon_status.json"
        )
        self.status_file = os.path.expanduser(self.status_file)

        # Components
        self.metrics_collector = None
        self.anomaly_detector = None
        self.optimization_engine = None

        # Status
        self.running = False
        self.status_thread = None
        self.status_interval = self.daemon_config.get("status_interval", 60)  # seconds

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(self.pid_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)

    def start(self, foreground: bool = False) -> None:
        """
        Start the resource monitoring daemon.

        Args:
            foreground: Whether to run in the foreground (True) or as a daemon (False)
        """
        if self.is_running():
            logger.info("Resource monitoring daemon is already running")
            return

        if not foreground:
            self._daemonize()

        # Write PID file
        with open(self.pid_file, "w") as f:
            f.write(str(os.getpid()))

        # Register cleanup handler
        atexit.register(self._cleanup)

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Initialize components
        self._initialize_components()

        # Start components
        self._start_components()

        # Start status thread
        self.running = True
        self.status_thread = threading.Thread(target=self._status_loop)
        self.status_thread.daemon = True
        self.status_thread.start()

        logger.info("Resource monitoring daemon started")

        if foreground:
            # Keep the main thread alive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """
        Stop the resource monitoring daemon.
        """
        logger.info("Stopping resource monitoring daemon")

        # Stop components
        self._stop_components()

        # Stop status thread
        self.running = False
        if self.status_thread:
            self.status_thread.join(timeout=5)

        # Remove PID file
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

        logger.info("Resource monitoring daemon stopped")

    def restart(self, foreground: bool = False) -> None:
        """
        Restart the resource monitoring daemon.

        Args:
            foreground: Whether to run in the foreground (True) or as a daemon (False)
        """
        self.stop()
        time.sleep(1)  # Give components time to shut down
        self.start(foreground)

    def is_running(self) -> bool:
        """
        Check if the daemon is running.

        Returns:
            True if the daemon is running, False otherwise
        """
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            # Process doesn't exist or PID file is invalid
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the daemon and its components.

        Returns:
            A dictionary containing status information
        """
        status = {
            "running": self.running,
            "pid": os.getpid() if self.running else None,
            "uptime": None,
            "components": {
                "metrics_collector": {
                    "running": self.metrics_collector is not None
                    and self.metrics_collector.running,
                    "containers_monitored": 0,
                    "metrics_collected": 0,
                },
                "anomaly_detector": {
                    "running": self.anomaly_detector is not None
                    and self.anomaly_detector.running,
                    "anomalies_detected": 0,
                },
                "optimization_engine": {
                    "running": self.optimization_engine is not None
                    and self.optimization_engine.running,
                    "recommendations_generated": 0,
                },
            },
            "last_updated": time.time(),
        }

        # Get component-specific status
        if self.metrics_collector:
            # Count containers being monitored
            containers_monitored = len(self.metrics_collector.get_metrics())
            status["components"]["metrics_collector"][
                "containers_monitored"
            ] = containers_monitored

            # Count total metrics collected
            metrics_collected = 0
            for container_metrics in self.metrics_collector.get_metrics().values():
                for metric_type, metrics in container_metrics.items():
                    metrics_collected += len(metrics)
            status["components"]["metrics_collector"][
                "metrics_collected"
            ] = metrics_collected

        if self.anomaly_detector:
            # Count anomalies detected
            anomalies_detected = 0
            for container_anomalies in self.anomaly_detector.anomaly_history.values():
                anomalies_detected += len(container_anomalies)
            status["components"]["anomaly_detector"][
                "anomalies_detected"
            ] = anomalies_detected

        if self.optimization_engine:
            # Count recommendations generated
            recommendations_generated = 0
            for container_recs in self.optimization_engine.recommendations.values():
                recommendations_generated += len(container_recs)
            status["components"]["optimization_engine"][
                "recommendations_generated"
            ] = recommendations_generated

        return status

    def _daemonize(self) -> None:
        """
        Daemonize the process.
        """
        # First fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError as e:
            logger.error("Fork #1 failed: %s", e)
            sys.exit(1)

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit second parent
                sys.exit(0)
        except OSError as e:
            logger.error("Fork #2 failed: %s", e)
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        # Open log file
        log_fd = open(self.log_file, "a+")

        # Duplicate file descriptors
        os.dup2(log_fd.fileno(), sys.stdin.fileno())
        os.dup2(log_fd.fileno(), sys.stdout.fileno())
        os.dup2(log_fd.fileno(), sys.stderr.fileno())

    def _initialize_components(self) -> None:
        """
        Initialize the monitoring components.
        """
        # Initialize metrics collector
        self.metrics_collector = MetricsCollector(
            self.config_manager, self.connection_manager
        )

        # Initialize anomaly detector
        self.anomaly_detector = AnomalyDetector(
            self.config_manager, self.metrics_collector, self.notification_manager
        )

        # Initialize optimization engine
        self.optimization_engine = OptimizationEngine(
            self.config_manager, self.metrics_collector
        )

    def _start_components(self) -> None:
        """
        Start the monitoring components.
        """
        # Start metrics collector
        if self.metrics_collector:
            self.metrics_collector.start_collection()

        # Start anomaly detector
        if self.anomaly_detector:
            self.anomaly_detector.start_detection()

        # Start optimization engine
        if self.optimization_engine:
            self.optimization_engine.start_analysis()

    def _stop_components(self) -> None:
        """
        Stop the monitoring components.
        """
        # Stop metrics collector
        if self.metrics_collector:
            self.metrics_collector.stop_collection()

        # Stop anomaly detector
        if self.anomaly_detector:
            self.anomaly_detector.stop_detection()

        # Stop optimization engine
        if self.optimization_engine:
            self.optimization_engine.stop_analysis()

    def _status_loop(self) -> None:
        """
        Main status update loop.
        """
        while self.running:
            try:
                # Get current status
                status = self.get_status()

                # Write status to file
                with open(self.status_file, "w") as f:
                    json.dump(status, f, indent=2)

                time.sleep(self.status_interval)
            except Exception as e:
                logger.error("Error updating status: %s", e)
                time.sleep(60)  # Wait a bit before retrying

    def _signal_handler(self, signum: int, frame) -> None:
        """
        Handle signals.

        Args:
            signum: The signal number
            frame: The current stack frame
        """
        if signum in (signal.SIGTERM, signal.SIGINT):
            logger.info("Received signal %s, shutting down", signum)
            self.stop()
            sys.exit(0)

    def _cleanup(self) -> None:
        """
        Clean up resources when the daemon exits.
        """
        self._stop_components()

        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)

    def get_metrics(
        self,
        container_id: Optional[str] = None,
        metric_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get metrics from the metrics collector.

        Args:
            container_id: Optional container ID to filter by
            metric_type: Optional metric type to filter by
            start_time: Optional start time for filtering (ISO format)
            end_time: Optional end time for filtering (ISO format)

        Returns:
            A dictionary of metrics
        """
        if not self.metrics_collector:
            return {}

        # Convert time strings to datetime objects
        start_datetime = None
        end_datetime = None

        if start_time:
            try:
                start_datetime = datetime.fromisoformat(start_time)
            except ValueError:
                logger.error("Invalid start time format: %s", start_time)

        if end_time:
            try:
                end_datetime = datetime.fromisoformat(end_time)
            except ValueError:
                logger.error("Invalid end time format: %s", end_time)

        return self.metrics_collector.get_metrics(
            container_id=container_id,
            metric_type=metric_type,
            start_time=start_datetime,
            end_time=end_datetime,
        )

    def get_anomalies(
        self,
        container_id: Optional[str] = None,
        metric_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        severity: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get anomalies from the anomaly detector.

        Args:
            container_id: Optional container ID to filter by
            metric_type: Optional metric type to filter by
            start_time: Optional start time for filtering (ISO format)
            end_time: Optional end time for filtering (ISO format)
            severity: Optional severity level to filter by

        Returns:
            A dictionary of anomalies
        """
        if not self.anomaly_detector:
            return {}

        # Convert time strings to datetime objects
        start_datetime = None
        end_datetime = None

        if start_time:
            try:
                start_datetime = datetime.fromisoformat(start_time)
            except ValueError:
                logger.error("Invalid start time format: %s", start_time)

        if end_time:
            try:
                end_datetime = datetime.fromisoformat(end_time)
            except ValueError:
                logger.error("Invalid end time format: %s", end_time)

        return self.anomaly_detector.get_anomalies(
            container_id=container_id,
            metric_type=metric_type,
            start_time=start_datetime,
            end_time=end_datetime,
            severity=severity,
        )

    def get_recommendations(
        self,
        container_id: Optional[str] = None,
        recommendation_type: Optional[str] = None,
        resource: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get recommendations from the optimization engine.

        Args:
            container_id: Optional container ID to filter by
            recommendation_type: Optional recommendation type to filter by
            resource: Optional resource type to filter by
            start_time: Optional start time for filtering (ISO format)
            end_time: Optional end time for filtering (ISO format)

        Returns:
            A dictionary of recommendations
        """
        if not self.optimization_engine:
            return {}

        # Convert time strings to datetime objects
        start_datetime = None
        end_datetime = None

        if start_time:
            try:
                start_datetime = datetime.fromisoformat(start_time)
            except ValueError:
                logger.error("Invalid start time format: %s", start_time)

        if end_time:
            try:
                end_datetime = datetime.fromisoformat(end_time)
            except ValueError:
                logger.error("Invalid end time format: %s", end_time)

        return self.optimization_engine.get_recommendations(
            container_id=container_id,
            recommendation_type=recommendation_type,
            resource=resource,
            start_time=start_datetime,
            end_time=end_datetime,
        )

    def generate_optimization_report(
        self, container_id: Optional[str] = None, format: str = "text"
    ) -> str:
        """
        Generate an optimization report.

        Args:
            container_id: Optional container ID to filter by
            format: The output format ('text', 'json', 'html')

        Returns:
            The optimization report as a string
        """
        if not self.optimization_engine:
            return "Optimization engine not available."

        return self.optimization_engine.generate_optimization_report(
            container_id=container_id, format=format
        )
