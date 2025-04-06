"""
DockerForge Anomaly Detector

This module provides functionality for detecting anomalies in Docker container resource metrics,
including statistical outlier detection, trend analysis, seasonality awareness, correlation detection,
and alert generation.
"""

import json
import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from src.config.config_manager import ConfigManager
from src.notifications.notification_manager import NotificationManager
from src.resource_monitoring.metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detects anomalies in Docker container resource metrics.

    This class handles:
    - Statistical outlier detection
    - Trend analysis
    - Seasonality awareness
    - Correlation detection
    - Alert generation
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        metrics_collector: MetricsCollector,
        notification_manager: Optional[NotificationManager] = None,
    ):
        """
        Initialize the anomaly detector.

        Args:
            config_manager: The configuration manager instance
            metrics_collector: The metrics collector instance
            notification_manager: Optional notification manager for sending alerts
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.metrics_collector = metrics_collector
        self.notification_manager = notification_manager

        # Anomaly detection configuration
        self.anomaly_config = self.config.get("resource_monitoring", {}).get(
            "anomaly_detection", {}
        )
        self.detection_interval = self.anomaly_config.get(
            "detection_interval", 300
        )  # seconds
        self.lookback_period = self.anomaly_config.get("lookback_period", 24)  # hours
        self.threshold_multiplier = self.anomaly_config.get(
            "threshold_multiplier", 3.0
        )  # standard deviations
        self.min_data_points = self.anomaly_config.get(
            "min_data_points", 10
        )  # minimum data points for detection
        self.enabled_metrics = self.anomaly_config.get(
            "enabled_metrics",
            {"cpu": True, "memory": True, "disk": True, "network": True},
        )
        self.alert_cooldown = self.anomaly_config.get("alert_cooldown", 3600)  # seconds

        # Detection thread
        self.detection_thread = None
        self.running = False

        # Anomaly history
        self.anomaly_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.last_alert_time: Dict[str, Dict[str, datetime]] = defaultdict(dict)

        # Baseline statistics
        self.baselines: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def start_detection(self) -> None:
        """
        Start anomaly detection in a background thread.
        """
        if self.detection_thread and self.detection_thread.is_alive():
            logger.info("Anomaly detection is already running")
            return

        logger.info("Starting anomaly detection")
        self.running = True
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def stop_detection(self) -> None:
        """
        Stop anomaly detection.
        """
        logger.info("Stopping anomaly detection")
        self.running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=5)

    def _detection_loop(self) -> None:
        """
        Main anomaly detection loop.
        """
        while self.running:
            try:
                self.detect_anomalies()
                time.sleep(self.detection_interval)
            except Exception as e:
                logger.error("Error in anomaly detection: %s", e)
                time.sleep(60)  # Wait a bit before retrying

    def detect_anomalies(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect anomalies in container metrics.

        Returns:
            A dictionary of detected anomalies by container ID
        """
        # Get all container metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=self.lookback_period)

        detected_anomalies: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Process each metric type
        for metric_type, enabled in self.enabled_metrics.items():
            if not enabled:
                continue

            # Get metrics for this type
            metrics = self.metrics_collector.get_metrics(
                container_id=None,
                metric_type=metric_type,
                start_time=start_time,
                end_time=end_time,
            )

            if not metrics:
                continue

            # Process each container
            for container_id, container_metrics in metrics.items():
                if (
                    metric_type not in container_metrics
                    or not container_metrics[metric_type]
                ):
                    continue

                # Detect anomalies for this container and metric type
                anomalies = self._detect_container_anomalies(
                    container_id, metric_type, container_metrics[metric_type]
                )

                if anomalies:
                    detected_anomalies[container_id].extend(anomalies)

                    # Store anomalies in history
                    self.anomaly_history[container_id].extend(anomalies)

                    # Send alerts if notification manager is available
                    if self.notification_manager:
                        self._send_anomaly_alerts(container_id, anomalies)

        return detected_anomalies

    def _detect_container_anomalies(
        self, container_id: str, metric_type: str, metrics_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies for a specific container and metric type.

        Args:
            container_id: The container ID
            metric_type: The metric type
            metrics_data: The metrics data

        Returns:
            A list of detected anomalies
        """
        if len(metrics_data) < self.min_data_points:
            return []

        # Update baseline statistics
        self._update_baseline(container_id, metric_type, metrics_data)

        # Get baseline
        baseline = self.baselines.get(container_id, {}).get(metric_type)
        if not baseline:
            return []

        # Extract the main metric values based on metric type
        values = []
        timestamps = []

        for entry in metrics_data:
            timestamps.append(datetime.fromisoformat(entry["timestamp"]))

            # Extract the main value based on metric type
            if metric_type == "cpu":
                value = entry["data"].get("usage_percent", 0)
            elif metric_type == "memory":
                value = entry["data"].get("usage_percent", 0)
            elif metric_type == "disk":
                value = entry["data"].get("read_bytes", 0) + entry["data"].get(
                    "write_bytes", 0
                )
            elif metric_type == "network":
                value = entry["data"].get("rx_bytes", 0) + entry["data"].get(
                    "tx_bytes", 0
                )
            else:
                # Try to find a numeric value
                for k, v in entry["data"].items():
                    if isinstance(v, (int, float)):
                        value = v
                        break
                else:
                    value = 0

            values.append(value)

        # Detect anomalies using different methods
        anomalies = []

        # Statistical outlier detection
        outlier_anomalies = self._detect_statistical_outliers(
            container_id, metric_type, timestamps, values, baseline
        )
        anomalies.extend(outlier_anomalies)

        # Trend analysis
        trend_anomalies = self._detect_trend_anomalies(
            container_id, metric_type, timestamps, values, baseline
        )
        anomalies.extend(trend_anomalies)

        # Seasonality analysis (if enough data)
        if len(values) >= 24:  # At least 24 data points for hourly seasonality
            seasonality_anomalies = self._detect_seasonality_anomalies(
                container_id, metric_type, timestamps, values, baseline
            )
            anomalies.extend(seasonality_anomalies)

        return anomalies

    def _update_baseline(
        self, container_id: str, metric_type: str, metrics_data: List[Dict[str, Any]]
    ) -> None:
        """
        Update baseline statistics for a container and metric type.

        Args:
            container_id: The container ID
            metric_type: The metric type
            metrics_data: The metrics data
        """
        # Extract values based on metric type
        values = []

        for entry in metrics_data:
            # Extract the main value based on metric type
            if metric_type == "cpu":
                value = entry["data"].get("usage_percent", 0)
            elif metric_type == "memory":
                value = entry["data"].get("usage_percent", 0)
            elif metric_type == "disk":
                value = entry["data"].get("read_bytes", 0) + entry["data"].get(
                    "write_bytes", 0
                )
            elif metric_type == "network":
                value = entry["data"].get("rx_bytes", 0) + entry["data"].get(
                    "tx_bytes", 0
                )
            else:
                # Try to find a numeric value
                for k, v in entry["data"].items():
                    if isinstance(v, (int, float)):
                        value = v
                        break
                else:
                    value = 0

            values.append(value)

        # Calculate statistics
        if not values:
            return

        mean = np.mean(values)
        std_dev = np.std(values)
        median = np.median(values)
        min_val = np.min(values)
        max_val = np.max(values)

        # Calculate percentiles
        p25 = np.percentile(values, 25)
        p75 = np.percentile(values, 75)
        p90 = np.percentile(values, 90)
        p95 = np.percentile(values, 95)
        p99 = np.percentile(values, 99)

        # Calculate IQR (Interquartile Range)
        iqr = p75 - p25

        # Store baseline
        if container_id not in self.baselines:
            self.baselines[container_id] = {}

        self.baselines[container_id][metric_type] = {
            "mean": mean,
            "std_dev": std_dev,
            "median": median,
            "min": min_val,
            "max": max_val,
            "p25": p25,
            "p75": p75,
            "p90": p90,
            "p95": p95,
            "p99": p99,
            "iqr": iqr,
            "upper_bound": mean + self.threshold_multiplier * std_dev,
            "lower_bound": mean - self.threshold_multiplier * std_dev,
            "updated_at": datetime.now(),
        }

    def _detect_statistical_outliers(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: List[float],
        baseline: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Detect statistical outliers in metrics data.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            baseline: The baseline statistics

        Returns:
            A list of detected anomalies
        """
        anomalies = []

        # Get thresholds
        upper_bound = baseline["upper_bound"]
        lower_bound = baseline["lower_bound"]

        # Check for outliers
        for i, (timestamp, value) in enumerate(zip(timestamps, values)):
            if value > upper_bound or value < lower_bound:
                # Check if this is a new anomaly (not too close to previous ones)
                if self._is_new_anomaly(container_id, metric_type, timestamp):
                    anomalies.append(
                        {
                            "container_id": container_id,
                            "metric_type": metric_type,
                            "timestamp": timestamp.isoformat(),
                            "value": value,
                            "baseline": baseline["mean"],
                            "threshold": (
                                upper_bound if value > upper_bound else lower_bound
                            ),
                            "deviation": (
                                (value - baseline["mean"]) / baseline["std_dev"]
                                if baseline["std_dev"] > 0
                                else 0
                            ),
                            "type": "outlier",
                            "severity": self._calculate_severity(
                                value, baseline["mean"], baseline["std_dev"]
                            ),
                            "description": f"Abnormal {metric_type} usage detected: {value:.2f} (baseline: {baseline['mean']:.2f})",
                        }
                    )

        return anomalies

    def _detect_trend_anomalies(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: List[float],
        baseline: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Detect trend anomalies in metrics data.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            baseline: The baseline statistics

        Returns:
            A list of detected anomalies
        """
        anomalies = []

        # Need at least a few data points for trend analysis
        if len(values) < 5:
            return []

        # Calculate moving average
        window_size = min(5, len(values))
        moving_avg = np.convolve(
            values, np.ones(window_size) / window_size, mode="valid"
        )

        # Calculate trend (slope)
        if len(moving_avg) >= 2:
            trend = (moving_avg[-1] - moving_avg[0]) / (len(moving_avg) - 1)

            # Normalize trend by baseline mean
            normalized_trend = trend / baseline["mean"] if baseline["mean"] > 0 else 0

            # Check for significant trend
            if abs(normalized_trend) > 0.1:  # 10% change per data point
                # Check if this is a new anomaly
                if self._is_new_anomaly(container_id, metric_type, timestamps[-1]):
                    anomalies.append(
                        {
                            "container_id": container_id,
                            "metric_type": metric_type,
                            "timestamp": timestamps[-1].isoformat(),
                            "value": values[-1],
                            "baseline": baseline["mean"],
                            "trend": trend,
                            "normalized_trend": normalized_trend,
                            "type": "trend",
                            "direction": "increasing" if trend > 0 else "decreasing",
                            "severity": min(
                                3, int(abs(normalized_trend) * 10)
                            ),  # Scale 1-3
                            "description": f"Abnormal {metric_type} {'increase' if trend > 0 else 'decrease'} detected: {normalized_trend:.2%} change per data point",
                        }
                    )

        return anomalies

    def _detect_seasonality_anomalies(
        self,
        container_id: str,
        metric_type: str,
        timestamps: List[datetime],
        values: List[float],
        baseline: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Detect seasonality anomalies in metrics data.

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamps: The timestamps
            values: The metric values
            baseline: The baseline statistics

        Returns:
            A list of detected anomalies
        """
        # This is a simplified implementation of seasonality detection
        # A more robust implementation would use techniques like STL decomposition
        # or Fourier analysis to detect and model seasonality

        anomalies = []

        # Need at least 24 data points for hourly seasonality
        if len(values) < 24:
            return []

        # Group values by hour of day
        hourly_values = defaultdict(list)

        for timestamp, value in zip(timestamps, values):
            hour = timestamp.hour
            hourly_values[hour].append(value)

        # Calculate hourly statistics
        hourly_stats = {}

        for hour, hour_values in hourly_values.items():
            if len(hour_values) >= 3:  # Need at least a few data points
                hourly_stats[hour] = {
                    "mean": np.mean(hour_values),
                    "std_dev": np.std(hour_values),
                }

        # Check if the latest value deviates from the expected hourly pattern
        if hourly_stats and timestamps:
            latest_timestamp = timestamps[-1]
            latest_hour = latest_timestamp.hour
            latest_value = values[-1]

            if latest_hour in hourly_stats:
                hour_mean = hourly_stats[latest_hour]["mean"]
                hour_std_dev = hourly_stats[latest_hour]["std_dev"]

                # Calculate deviation
                if hour_std_dev > 0:
                    deviation = (latest_value - hour_mean) / hour_std_dev

                    # Check for significant deviation
                    if abs(deviation) > self.threshold_multiplier:
                        # Check if this is a new anomaly
                        if self._is_new_anomaly(
                            container_id, metric_type, latest_timestamp
                        ):
                            anomalies.append(
                                {
                                    "container_id": container_id,
                                    "metric_type": metric_type,
                                    "timestamp": latest_timestamp.isoformat(),
                                    "value": latest_value,
                                    "expected_value": hour_mean,
                                    "deviation": deviation,
                                    "type": "seasonality",
                                    "hour": latest_hour,
                                    "severity": self._calculate_severity(
                                        latest_value, hour_mean, hour_std_dev
                                    ),
                                    "description": f"Abnormal {metric_type} usage for hour {latest_hour}: {latest_value:.2f} (expected: {hour_mean:.2f})",
                                }
                            )

        return anomalies

    def _is_new_anomaly(
        self, container_id: str, metric_type: str, timestamp: datetime
    ) -> bool:
        """
        Check if an anomaly is new (not too close to previous ones).

        Args:
            container_id: The container ID
            metric_type: The metric type
            timestamp: The timestamp

        Returns:
            True if this is a new anomaly, False otherwise
        """
        # Check if we've already alerted for this container and metric type recently
        if (
            container_id in self.last_alert_time
            and metric_type in self.last_alert_time[container_id]
        ):
            last_time = self.last_alert_time[container_id][metric_type]
            if (timestamp - last_time).total_seconds() < self.alert_cooldown:
                return False

        # Update last alert time
        if container_id not in self.last_alert_time:
            self.last_alert_time[container_id] = {}

        self.last_alert_time[container_id][metric_type] = timestamp

        return True

    def _calculate_severity(self, value: float, mean: float, std_dev: float) -> int:
        """
        Calculate the severity of an anomaly (1-3).

        Args:
            value: The anomaly value
            mean: The mean value
            std_dev: The standard deviation

        Returns:
            The severity level (1-3)
        """
        if std_dev <= 0:
            return 1

        deviation = abs(value - mean) / std_dev

        if deviation > 5:
            return 3  # High severity
        elif deviation > 3:
            return 2  # Medium severity
        else:
            return 1  # Low severity

    def _send_anomaly_alerts(
        self, container_id: str, anomalies: List[Dict[str, Any]]
    ) -> None:
        """
        Send alerts for detected anomalies.

        Args:
            container_id: The container ID
            anomalies: The detected anomalies
        """
        if not self.notification_manager or not anomalies:
            return

        # Group anomalies by severity
        anomalies_by_severity = defaultdict(list)

        for anomaly in anomalies:
            severity = anomaly.get("severity", 1)
            anomalies_by_severity[severity].append(anomaly)

        # Send alerts for each severity level
        for severity, severity_anomalies in anomalies_by_severity.items():
            # Prepare alert message
            subject = f"DockerForge: {len(severity_anomalies)} anomalies detected in container {container_id[:12]}"

            message = f"DockerForge has detected {len(severity_anomalies)} anomalies in container {container_id}:\n\n"

            for anomaly in severity_anomalies:
                message += f"- {anomaly['description']}\n"
                message += f"  Timestamp: {anomaly['timestamp']}\n"
                message += f"  Type: {anomaly['type']}\n"
                message += f"  Severity: {anomaly['severity']}\n\n"

            # Send notification
            self.notification_manager.send_notification(
                subject=subject,
                message=message,
                severity=severity,
                category="anomaly",
                metadata={
                    "container_id": container_id,
                    "anomalies": severity_anomalies,
                },
            )

    def get_anomalies(
        self,
        container_id: Optional[str] = None,
        metric_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[int] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get detected anomalies.

        Args:
            container_id: Optional container ID to filter by
            metric_type: Optional metric type to filter by
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering
            severity: Optional severity level to filter by

        Returns:
            A dictionary of anomalies by container ID
        """
        result = {}

        # Filter by container ID
        if container_id:
            if container_id in self.anomaly_history:
                result[container_id] = self._filter_anomalies(
                    self.anomaly_history[container_id],
                    metric_type,
                    start_time,
                    end_time,
                    severity,
                )
        else:
            # Include all containers
            for c_id, anomalies in self.anomaly_history.items():
                filtered = self._filter_anomalies(
                    anomalies, metric_type, start_time, end_time, severity
                )

                if filtered:
                    result[c_id] = filtered

        return result

    def _filter_anomalies(
        self,
        anomalies: List[Dict[str, Any]],
        metric_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        severity: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter anomalies by various criteria.

        Args:
            anomalies: The anomalies to filter
            metric_type: Optional metric type to filter by
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering
            severity: Optional severity level to filter by

        Returns:
            Filtered anomalies
        """
        filtered = []

        for anomaly in anomalies:
            # Filter by metric type
            if metric_type and anomaly.get("metric_type") != metric_type:
                continue

            # Filter by time range
            if start_time or end_time:
                timestamp = datetime.fromisoformat(anomaly["timestamp"])

                if start_time and timestamp < start_time:
                    continue

                if end_time and timestamp > end_time:
                    continue

            # Filter by severity
            if severity is not None and anomaly.get("severity") != severity:
                continue

            filtered.append(anomaly)

        return filtered

    def get_baselines(
        self, container_id: Optional[str] = None, metric_type: Optional[str] = None
    ) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Get baseline statistics.

        Args:
            container_id: Optional container ID to filter by
            metric_type: Optional metric type to filter by

        Returns:
            A dictionary of baseline statistics
        """
        if container_id:
            if container_id in self.baselines:
                if metric_type:
                    if metric_type in self.baselines[container_id]:
                        return {
                            container_id: {
                                metric_type: self.baselines[container_id][metric_type]
                            }
                        }
                    else:
                        return {}
                else:
                    return {container_id: self.baselines[container_id]}
            else:
                return {}
        else:
            if metric_type:
                result = {}
                for c_id, metrics in self.baselines.items():
                    if metric_type in metrics:
                        if c_id not in result:
                            result[c_id] = {}
                        result[c_id][metric_type] = metrics[metric_type]
                return result
            else:
                return self.baselines
