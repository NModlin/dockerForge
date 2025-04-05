"""
DockerForge Metrics Collector

This module provides functionality for collecting resource metrics from Docker containers,
including CPU usage, memory utilization, disk I/O statistics, and network traffic.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import threading
import docker
from docker.models.containers import Container

from src.docker.connection_manager_adapter import ConnectionManager
from src.config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Collects resource metrics from Docker containers.

    This class handles:
    - CPU usage tracking
    - Memory utilization
    - Disk I/O statistics
    - Network traffic monitoring
    - Custom metric support
    """

    def __init__(self, config_manager: ConfigManager, connection_manager: ConnectionManager):
        """
        Initialize the metrics collector.

        Args:
            config_manager: The configuration manager instance
            connection_manager: The Docker connection manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.connection_manager = connection_manager
        self.client = connection_manager.get_client()

        # Metrics configuration
        self.metrics_config = self.config.get('resource_monitoring', {}).get('metrics', {})
        self.collection_interval = self.metrics_config.get('collection_interval', 10)  # seconds
        self.retention_period = self.metrics_config.get('retention_period', 7)  # days
        self.storage_path = self.metrics_config.get('storage_path', '~/.dockerforge/metrics')
        self.enabled_metrics = self.metrics_config.get('enabled_metrics', {
            'cpu': True,
            'memory': True,
            'disk': True,
            'network': True,
            'custom': True
        })

        # Metrics storage
        self.metrics_data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.metrics_lock = threading.Lock()

        # Collection thread
        self.collection_thread = None
        self.running = False

        # Custom metrics
        self.custom_metrics = self.metrics_config.get('custom_metrics', [])

    def start_collection(self) -> None:
        """
        Start collecting metrics in a background thread.
        """
        if self.collection_thread and self.collection_thread.is_alive():
            logger.info("Metrics collection is already running")
            return

        logger.info("Starting metrics collection")
        self.running = True
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True
        self.collection_thread.start()

    def stop_collection(self) -> None:
        """
        Stop collecting metrics.
        """
        logger.info("Stopping metrics collection")
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)

    def _collection_loop(self) -> None:
        """
        Main metrics collection loop.
        """
        while self.running:
            try:
                self.collect_metrics()
                self._cleanup_old_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error("Error in metrics collection: %s", e)
                time.sleep(5)  # Wait a bit before retrying

    def collect_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Collect metrics from all running containers.

        Returns:
            A dictionary of container metrics
        """
        containers = self.client.containers.list()
        metrics = {}

        for container in containers:
            try:
                container_metrics = self._collect_container_metrics(container)
                metrics[container.id] = container_metrics

                # Store metrics
                with self.metrics_lock:
                    if container.id not in self.metrics_data:
                        self.metrics_data[container.id] = {
                            'cpu': [],
                            'memory': [],
                            'disk': [],
                            'network': [],
                            'custom': []
                        }

                    # Store each metric type
                    for metric_type, metric_data in container_metrics.items():
                        if metric_type in self.metrics_data[container.id]:
                            self.metrics_data[container.id][metric_type].append({
                                'timestamp': datetime.now().isoformat(),
                                'data': metric_data
                            })
            except Exception as e:
                logger.error("Error collecting metrics for container %s: %s", container.id[:12], e)

        return metrics

    def _collect_container_metrics(self, container: Container) -> Dict[str, Any]:
        """
        Collect metrics for a specific container.

        Args:
            container: The Docker container

        Returns:
            A dictionary of metrics for the container
        """
        metrics = {}

        # Get container stats
        stats = container.stats(stream=False)

        # CPU metrics
        if self.enabled_metrics.get('cpu', True):
            metrics['cpu'] = self._extract_cpu_metrics(stats)

        # Memory metrics
        if self.enabled_metrics.get('memory', True):
            metrics['memory'] = self._extract_memory_metrics(stats)

        # Disk metrics
        if self.enabled_metrics.get('disk', True):
            metrics['disk'] = self._extract_disk_metrics(stats)

        # Network metrics
        if self.enabled_metrics.get('network', True):
            metrics['network'] = self._extract_network_metrics(stats)

        # Custom metrics
        if self.enabled_metrics.get('custom', True):
            metrics['custom'] = self._extract_custom_metrics(container, stats)

        # Add container metadata
        metrics['metadata'] = {
            'id': container.id,
            'name': container.name,
            'image': container.image.tags[0] if container.image.tags else container.image.id,
            'status': container.status,
            'created': container.attrs.get('Created'),
        }

        return metrics

    def _extract_cpu_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract CPU metrics from container stats.

        Args:
            stats: The container stats

        Returns:
            A dictionary of CPU metrics
        """
        cpu_stats = stats.get('cpu_stats', {})
        precpu_stats = stats.get('precpu_stats', {})

        # Calculate CPU usage percentage
        cpu_usage = cpu_stats.get('cpu_usage', {})
        precpu_usage = precpu_stats.get('cpu_usage', {})

        cpu_total_usage = cpu_usage.get('total_usage', 0)
        precpu_total_usage = precpu_usage.get('total_usage', 0)

        system_cpu_usage = cpu_stats.get('system_cpu_usage', 0)
        previous_system_cpu_usage = precpu_stats.get('system_cpu_usage', 0)

        # Calculate CPU usage percentage
        cpu_delta = cpu_total_usage - precpu_total_usage
        system_delta = system_cpu_usage - previous_system_cpu_usage

        cpu_percent = 0.0
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * 100.0

        # Get number of CPUs
        online_cpus = cpu_stats.get('online_cpus', 0)
        if online_cpus == 0:
            # Fall back to counting CPU usage entries
            online_cpus = len(cpu_usage.get('percpu_usage', []))

        # Adjust percentage for number of CPUs
        if online_cpus > 0:
            cpu_percent = cpu_percent * online_cpus

        return {
            'usage_percent': round(cpu_percent, 2),
            'total_usage': cpu_total_usage,
            'system_usage': system_cpu_usage,
            'online_cpus': online_cpus,
            'throttling_periods': cpu_stats.get('throttling_data', {}).get('periods', 0),
            'throttled_periods': cpu_stats.get('throttling_data', {}).get('throttled_periods', 0),
            'throttled_time': cpu_stats.get('throttling_data', {}).get('throttled_time', 0),
        }

    def _extract_memory_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract memory metrics from container stats.

        Args:
            stats: The container stats

        Returns:
            A dictionary of memory metrics
        """
        memory_stats = stats.get('memory_stats', {})

        # Calculate memory usage
        memory_usage = memory_stats.get('usage', 0)
        memory_limit = memory_stats.get('limit', 0)

        # Calculate memory percentage
        memory_percent = 0.0
        if memory_limit > 0:
            memory_percent = (memory_usage / memory_limit) * 100.0

        # Calculate cache usage
        cache = memory_stats.get('stats', {}).get('cache', 0)

        # Calculate actual memory usage (excluding cache)
        memory_usage_actual = memory_usage - cache if memory_usage > cache else memory_usage

        # Calculate actual memory percentage
        memory_percent_actual = 0.0
        if memory_limit > 0:
            memory_percent_actual = (memory_usage_actual / memory_limit) * 100.0

        return {
            'usage': memory_usage,
            'usage_actual': memory_usage_actual,
            'limit': memory_limit,
            'usage_percent': round(memory_percent, 2),
            'usage_percent_actual': round(memory_percent_actual, 2),
            'cache': cache,
            'rss': memory_stats.get('stats', {}).get('rss', 0),
            'swap': memory_stats.get('stats', {}).get('swap', 0),
            'active_anon': memory_stats.get('stats', {}).get('active_anon', 0),
            'inactive_anon': memory_stats.get('stats', {}).get('inactive_anon', 0),
            'active_file': memory_stats.get('stats', {}).get('active_file', 0),
            'inactive_file': memory_stats.get('stats', {}).get('inactive_file', 0),
        }

    def _extract_disk_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract disk I/O metrics from container stats.

        Args:
            stats: The container stats

        Returns:
            A dictionary of disk I/O metrics
        """
        blkio_stats = stats.get('blkio_stats', {})

        # Extract I/O service bytes
        io_service_bytes = {}
        for entry in blkio_stats.get('io_service_bytes_recursive', []):
            op = entry.get('op', '').lower()
            value = entry.get('value', 0)
            if op:
                io_service_bytes[op] = io_service_bytes.get(op, 0) + value

        # Extract I/O serviced
        io_serviced = {}
        for entry in blkio_stats.get('io_serviced_recursive', []):
            op = entry.get('op', '').lower()
            value = entry.get('value', 0)
            if op:
                io_serviced[op] = io_serviced.get(op, 0) + value

        return {
            'io_service_bytes': io_service_bytes,
            'io_serviced': io_serviced,
            'read_bytes': io_service_bytes.get('read', 0),
            'write_bytes': io_service_bytes.get('write', 0),
            'read_ops': io_serviced.get('read', 0),
            'write_ops': io_serviced.get('write', 0),
        }

    def _extract_network_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract network metrics from container stats.

        Args:
            stats: The container stats

        Returns:
            A dictionary of network metrics
        """
        networks = stats.get('networks', {})

        # Aggregate network metrics across all interfaces
        rx_bytes = 0
        tx_bytes = 0
        rx_packets = 0
        tx_packets = 0
        rx_errors = 0
        tx_errors = 0
        rx_dropped = 0
        tx_dropped = 0

        # Per-interface metrics
        interfaces = {}

        for interface, data in networks.items():
            rx_bytes += data.get('rx_bytes', 0)
            tx_bytes += data.get('tx_bytes', 0)
            rx_packets += data.get('rx_packets', 0)
            tx_packets += data.get('tx_packets', 0)
            rx_errors += data.get('rx_errors', 0)
            tx_errors += data.get('tx_errors', 0)
            rx_dropped += data.get('rx_dropped', 0)
            tx_dropped += data.get('tx_dropped', 0)

            # Store per-interface metrics
            interfaces[interface] = {
                'rx_bytes': data.get('rx_bytes', 0),
                'tx_bytes': data.get('tx_bytes', 0),
                'rx_packets': data.get('rx_packets', 0),
                'tx_packets': data.get('tx_packets', 0),
                'rx_errors': data.get('rx_errors', 0),
                'tx_errors': data.get('tx_errors', 0),
                'rx_dropped': data.get('rx_dropped', 0),
                'tx_dropped': data.get('tx_dropped', 0),
            }

        return {
            'interfaces': interfaces,
            'rx_bytes': rx_bytes,
            'tx_bytes': tx_bytes,
            'rx_packets': rx_packets,
            'tx_packets': tx_packets,
            'rx_errors': rx_errors,
            'tx_errors': tx_errors,
            'rx_dropped': rx_dropped,
            'tx_dropped': tx_dropped,
        }

    def _extract_custom_metrics(self, container: Container, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract custom metrics from container.

        Args:
            container: The Docker container
            stats: The container stats

        Returns:
            A dictionary of custom metrics
        """
        custom_metrics = {}

        # Process each custom metric
        for metric in self.custom_metrics:
            try:
                metric_name = metric.get('name')
                metric_type = metric.get('type')

                if not metric_name or not metric_type:
                    continue

                if metric_type == 'command':
                    # Execute command in container
                    command = metric.get('command')
                    if command:
                        result = container.exec_run(command)
                        if result.exit_code == 0:
                            custom_metrics[metric_name] = result.output.decode('utf-8').strip()
                elif metric_type == 'label':
                    # Get container label
                    label = metric.get('label')
                    if label:
                        custom_metrics[metric_name] = container.labels.get(label, '')
                elif metric_type == 'env':
                    # Get container environment variable
                    env_var = metric.get('env_var')
                    if env_var:
                        for env in container.attrs.get('Config', {}).get('Env', []):
                            if env.startswith(f"{env_var}="):
                                custom_metrics[metric_name] = env.split('=', 1)[1]
                                break
            except Exception as e:
                logger.error("Error collecting custom metric %s: %s", metric.get('name'), e)

        return custom_metrics

    def get_metrics(self, container_id: Optional[str] = None, metric_type: Optional[str] = None,
                   start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get collected metrics.

        Args:
            container_id: Optional container ID to filter by
            metric_type: Optional metric type to filter by
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering

        Returns:
            A dictionary of metrics
        """
        with self.metrics_lock:
            if container_id:
                # Get metrics for a specific container
                if container_id not in self.metrics_data:
                    return {}

                if metric_type:
                    # Get specific metric type
                    if metric_type not in self.metrics_data[container_id]:
                        return {}

                    # Filter by time range if specified
                    if start_time or end_time:
                        filtered_metrics = self._filter_metrics_by_time(
                            self.metrics_data[container_id][metric_type],
                            start_time,
                            end_time
                        )
                        return {container_id: {metric_type: filtered_metrics}}
                    else:
                        return {container_id: {metric_type: self.metrics_data[container_id][metric_type]}}
                else:
                    # Get all metric types for the container
                    if start_time or end_time:
                        filtered_data = {}
                        for m_type, m_data in self.metrics_data[container_id].items():
                            filtered_data[m_type] = self._filter_metrics_by_time(m_data, start_time, end_time)
                        return {container_id: filtered_data}
                    else:
                        return {container_id: self.metrics_data[container_id]}
            else:
                # Get metrics for all containers
                if metric_type:
                    # Get specific metric type for all containers
                    result = {}
                    for c_id, c_data in self.metrics_data.items():
                        if metric_type in c_data:
                            if start_time or end_time:
                                result[c_id] = {
                                    metric_type: self._filter_metrics_by_time(c_data[metric_type], start_time, end_time)
                                }
                            else:
                                result[c_id] = {metric_type: c_data[metric_type]}
                    return result
                else:
                    # Get all metrics for all containers
                    if start_time or end_time:
                        result = {}
                        for c_id, c_data in self.metrics_data.items():
                            filtered_data = {}
                            for m_type, m_data in c_data.items():
                                filtered_data[m_type] = self._filter_metrics_by_time(m_data, start_time, end_time)
                            result[c_id] = filtered_data
                        return result
                    else:
                        return self.metrics_data

    def _filter_metrics_by_time(self, metrics: List[Dict[str, Any]],
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Filter metrics by time range.

        Args:
            metrics: The metrics to filter
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            Filtered metrics
        """
        if not start_time and not end_time:
            return metrics

        filtered = []
        for metric in metrics:
            timestamp = datetime.fromisoformat(metric['timestamp'])

            if start_time and timestamp < start_time:
                continue

            if end_time and timestamp > end_time:
                continue

            filtered.append(metric)

        return filtered

    def _cleanup_old_metrics(self) -> None:
        """
        Clean up metrics older than the retention period.
        """
        if not self.retention_period:
            return

        cutoff_time = datetime.now() - timedelta(days=self.retention_period)

        with self.metrics_lock:
            for container_id in list(self.metrics_data.keys()):
                for metric_type in list(self.metrics_data[container_id].keys()):
                    self.metrics_data[container_id][metric_type] = [
                        m for m in self.metrics_data[container_id][metric_type]
                        if datetime.fromisoformat(m['timestamp']) >= cutoff_time
                    ]

    def export_metrics(self, container_id: Optional[str] = None,
                      metric_type: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      format: str = 'json') -> str:
        """
        Export metrics in the specified format.

        Args:
            container_id: Optional container ID to filter by
            metric_type: Optional metric type to filter by
            start_time: Optional start time for filtering
            end_time: Optional end time for filtering
            format: The export format ('json', 'csv', etc.)

        Returns:
            The exported metrics as a string
        """
        metrics = self.get_metrics(container_id, metric_type, start_time, end_time)

        if format.lower() == 'json':
            return json.dumps(metrics, indent=2)
        elif format.lower() == 'csv':
            # This is a simplified CSV export that would need to be expanded
            # for a real implementation
            csv_lines = ['timestamp,container_id,metric_type,metric_name,value']

            for c_id, c_data in metrics.items():
                for m_type, m_data in c_data.items():
                    for entry in m_data:
                        timestamp = entry['timestamp']
                        data = entry['data']

                        if isinstance(data, dict):
                            for k, v in data.items():
                                if isinstance(v, (int, float, str, bool)):
                                    csv_lines.append(f"{timestamp},{c_id},{m_type},{k},{v}")

            return '\n'.join(csv_lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_container_metrics_summary(self, container_id: str) -> Dict[str, Any]:
        """
        Get a summary of metrics for a specific container.

        Args:
            container_id: The container ID

        Returns:
            A summary of metrics for the container
        """
        metrics = self.get_metrics(container_id)
        if not metrics or container_id not in metrics:
            return {}

        container_metrics = metrics[container_id]

        # Calculate CPU average
        cpu_avg = self._calculate_metric_average(container_metrics.get('cpu', []), 'usage_percent')

        # Calculate memory average
        memory_avg = self._calculate_metric_average(container_metrics.get('memory', []), 'usage_percent')

        # Calculate disk I/O rates
        disk_read_rate = self._calculate_metric_rate(container_metrics.get('disk', []), 'read_bytes')
        disk_write_rate = self._calculate_metric_rate(container_metrics.get('disk', []), 'write_bytes')

        # Calculate network rates
        network_rx_rate = self._calculate_metric_rate(container_metrics.get('network', []), 'rx_bytes')
        network_tx_rate = self._calculate_metric_rate(container_metrics.get('network', []), 'tx_bytes')

        return {
            'container_id': container_id,
            'cpu': {
                'average_usage_percent': cpu_avg,
                'current': self._get_latest_metric_value(container_metrics.get('cpu', []), 'usage_percent'),
                'min': self._get_min_metric_value(container_metrics.get('cpu', []), 'usage_percent'),
                'max': self._get_max_metric_value(container_metrics.get('cpu', []), 'usage_percent'),
            },
            'memory': {
                'average_usage_percent': memory_avg,
                'current': self._get_latest_metric_value(container_metrics.get('memory', []), 'usage_percent'),
                'min': self._get_min_metric_value(container_metrics.get('memory', []), 'usage_percent'),
                'max': self._get_max_metric_value(container_metrics.get('memory', []), 'usage_percent'),
            },
            'disk': {
                'read_rate_bytes_per_sec': disk_read_rate,
                'write_rate_bytes_per_sec': disk_write_rate,
                'total_read_bytes': self._get_latest_metric_value(container_metrics.get('disk', []), 'read_bytes'),
                'total_write_bytes': self._get_latest_metric_value(container_metrics.get('disk', []), 'write_bytes'),
            },
            'network': {
                'rx_rate_bytes_per_sec': network_rx_rate,
                'tx_rate_bytes_per_sec': network_tx_rate,
                'total_rx_bytes': self._get_latest_metric_value(container_metrics.get('network', []), 'rx_bytes'),
                'total_tx_bytes': self._get_latest_metric_value(container_metrics.get('network', []), 'tx_bytes'),
            },
        }

    def _calculate_metric_average(self, metrics: List[Dict[str, Any]], key: str) -> Optional[float]:
        """
        Calculate the average value of a metric.

        Args:
            metrics: The metrics data
            key: The metric key

        Returns:
            The average value, or None if no data
        """
        if not metrics:
            return None

        values = []
        for metric in metrics:
            if 'data' in metric and key in metric['data']:
                value = metric['data'][key]
                if isinstance(value, (int, float)):
                    values.append(value)

        if not values:
            return None

        return sum(values) / len(values)

    def _calculate_metric_rate(self, metrics: List[Dict[str, Any]], key: str) -> Optional[float]:
        """
        Calculate the rate of change of a metric.

        Args:
            metrics: The metrics data
            key: The metric key

        Returns:
            The rate in units per second, or None if insufficient data
        """
        if not metrics or len(metrics) < 2:
            return None

        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m['timestamp'])

        # Get first and last metrics
        first = sorted_metrics[0]
        last = sorted_metrics[-1]

        # Check if the key exists in both metrics
        if ('data' not in first or key not in first['data'] or
            'data' not in last or key not in last['data']):
            return None

        # Get values
        first_value = first['data'][key]
        last_value = last['data'][key]

        # Check if values are numeric
        if not isinstance(first_value, (int, float)) or not isinstance(last_value, (int, float)):
            return None

        # Calculate time difference
        first_time = datetime.fromisoformat(first['timestamp'])
        last_time = datetime.fromisoformat(last['timestamp'])
        time_diff_seconds = (last_time - first_time).total_seconds()

        if time_diff_seconds <= 0:
            return None

        # Calculate rate
        value_diff = last_value - first_value
        rate = value_diff / time_diff_seconds

        return rate

    def _get_latest_metric_value(self, metrics: List[Dict[str, Any]], key: str) -> Optional[Any]:
        """
        Get the latest value of a metric.

        Args:
            metrics: The metrics data
            key: The metric key

        Returns:
            The latest value, or None if no data
        """
        if not metrics:
            return None

        # Sort metrics by timestamp (descending)
        sorted_metrics = sorted(metrics, key=lambda m: m['timestamp'], reverse=True)

        # Get the latest metric
        latest = sorted_metrics[0]

        # Check if the key exists
        if 'data' in latest and key in latest['data']:
            return latest['data'][key]

        return None

    def _get_min_metric_value(self, metrics: List[Dict[str, Any]], key: str) -> Optional[Any]:
        """
        Get the minimum value of a metric.

        Args:
            metrics: The metrics data
            key: The metric key

        Returns:
            The minimum value, or None if no data
        """
        values = []
        for metric in metrics:
            if 'data' in metric and key in metric['data']:
                value = metric['data'][key]
                if isinstance(value, (int, float)):
                    values.append(value)

        if not values:
            return None

        return min(values)

    def _get_max_metric_value(self, metrics: List[Dict[str, Any]], key: str) -> Optional[Any]:
        """
        Get the maximum value of a metric.

        Args:
            metrics: The metrics data
            key: The metric key

        Returns:
            The maximum value, or None if no data
        """
        values = []
        for metric in metrics:
            if 'data' in metric and key in metric['data']:
                value = metric['data'][key]
                if isinstance(value, (int, float)):
                    values.append(value)

        if not values:
            return None

        return max(values)

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system-wide metrics.

        Returns:
            A dictionary of system metrics
        """
        system_metrics = {
            'containers': {
                'total': 0,
                'running': 0,
                'paused': 0,
                'stopped': 0,
            },
            'cpu': {
                'total_usage_percent': 0,
            },
            'memory': {
                'total_usage_bytes': 0,
                'total_limit_bytes': 0,
                'usage_percent': 0,
            },
            'disk': {
                'read_rate_bytes_per_sec': 0,
                'write_rate_bytes_per_sec': 0,
            },
            'network': {
                'rx_rate_bytes_per_sec': 0,
                'tx_rate_bytes_per_sec': 0,
            },
        }

        try:
            # Get container counts
            containers = self.client.containers.list(all=True)
            system_metrics['containers']['total'] = len(containers)
            system_metrics['containers']['running'] = len([c for c in containers if c.status == 'running'])
            system_metrics['containers']['paused'] = len([c for c in containers if c.status == 'paused'])
            system_metrics['containers']['stopped'] = len([c for c in containers if c.status == 'exited'])

            # Aggregate container metrics
            running_containers = [c for c in containers if c.status == 'running']
            total_cpu_percent = 0
            total_memory_usage = 0
            total_memory_limit = 0
            total_disk_read_rate = 0
            total_disk_write_rate = 0
            total_network_rx_rate = 0
            total_network_tx_rate = 0

            for container in running_containers:
                try:
                    # Get container metrics summary
                    summary = self.get_container_metrics_summary(container.id)

                    # Aggregate CPU
                    if summary.get('cpu', {}).get('average_usage_percent') is not None:
                        total_cpu_percent += summary['cpu']['average_usage_percent']

                    # Aggregate memory
                    if 'memory' in summary:
                        memory_data = summary['memory']
                        if memory_data.get('current') is not None:
                            total_memory_usage += memory_data.get('current', 0)

                    # Aggregate disk I/O rates
                    if 'disk' in summary:
                        disk_data = summary['disk']
                        if disk_data.get('read_rate_bytes_per_sec') is not None:
                            total_disk_read_rate += disk_data.get('read_rate_bytes_per_sec', 0)
                        if disk_data.get('write_rate_bytes_per_sec') is not None:
                            total_disk_write_rate += disk_data.get('write_rate_bytes_per_sec', 0)

                    # Aggregate network rates
                    if 'network' in summary:
                        network_data = summary['network']
                        if network_data.get('rx_rate_bytes_per_sec') is not None:
                            total_network_rx_rate += network_data.get('rx_rate_bytes_per_sec', 0)
                        if network_data.get('tx_rate_bytes_per_sec') is not None:
                            total_network_tx_rate += network_data.get('tx_rate_bytes_per_sec', 0)
                except Exception as e:
                    logger.error("Error aggregating metrics for container %s: %s", container.id[:12], e)

            # Update system metrics
            system_metrics['cpu']['total_usage_percent'] = total_cpu_percent
            system_metrics['memory']['total_usage_bytes'] = total_memory_usage
            system_metrics['memory']['total_limit_bytes'] = total_memory_limit
            if total_memory_limit > 0:
                system_metrics['memory']['usage_percent'] = (total_memory_usage / total_memory_limit) * 100
            system_metrics['disk']['read_rate_bytes_per_sec'] = total_disk_read_rate
            system_metrics['disk']['write_rate_bytes_per_sec'] = total_disk_write_rate
            system_metrics['network']['rx_rate_bytes_per_sec'] = total_network_rx_rate
            system_metrics['network']['tx_rate_bytes_per_sec'] = total_network_tx_rate

        except Exception as e:
            logger.error("Error collecting system metrics: %s", e)

        return system_metrics

    def get_metrics_history(self, container_id: str, metric_type: str,
                           duration: timedelta = timedelta(hours=1)) -> List[Dict[str, Any]]:
        """
        Get historical metrics for a specific container and metric type.

        Args:
            container_id: The container ID
            metric_type: The metric type (cpu, memory, disk, network)
            duration: The time duration to look back

        Returns:
            A list of metrics data points
        """
        end_time = datetime.now()
        start_time = end_time - duration

        metrics = self.get_metrics(container_id, metric_type, start_time, end_time)
        if not metrics or container_id not in metrics or metric_type not in metrics[container_id]:
            return []

        return metrics[container_id][metric_type]
