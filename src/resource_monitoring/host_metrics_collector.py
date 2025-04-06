"""
DockerForge Host Metrics Collector

This module provides functionality for collecting host system resource metrics,
including CPU, memory, disk, and network usage.
"""

import json
import logging
import os
import platform
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

from src.config.config_manager import ConfigManager
from src.docker.connection_manager import ConnectionManager
from src.utils.file_utils import ensure_directory_exists

logger = logging.getLogger(__name__)


class HostMetricsCollector:
    """
    Collects resource metrics from the host system.

    This class handles:
    - CPU usage tracking
    - Memory utilization
    - Disk I/O statistics
    - Network traffic monitoring
    """

    def __init__(
        self, config_manager: ConfigManager, connection_manager: ConnectionManager
    ):
        """
        Initialize the host metrics collector.

        Args:
            config_manager: The configuration manager instance
            connection_manager: The Docker connection manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.connection_manager = connection_manager
        self.client = connection_manager.get_client()

        # Metrics configuration
        self.metrics_config = self.config.get("resource_monitoring", {}).get(
            "metrics", {}
        )
        self.collection_interval = self.metrics_config.get(
            "collection_interval", 10
        )  # seconds
        self.retention_period = self.metrics_config.get("retention_period", 7)  # days
        self.storage_path = self.metrics_config.get(
            "storage_path", "~/.dockerforge/metrics"
        )
        self.enabled_metrics = self.metrics_config.get(
            "enabled_metrics",
            {"cpu": True, "memory": True, "disk": True, "network": True},
        )

        # Expand storage path
        self.storage_path = os.path.expanduser(self.storage_path)
        ensure_directory_exists(self.storage_path)
        self.host_metrics_path = os.path.join(self.storage_path, "host")
        ensure_directory_exists(self.host_metrics_path)

        # Collection thread
        self.running = False
        self.collection_thread = None

        # Initialize metrics history
        self.metrics_history = {"cpu": [], "memory": [], "disk": [], "network": []}

        # Initialize previous network counters for rate calculation
        self.prev_net_io = psutil.net_io_counters()
        self.prev_net_time = time.time()

        # Initialize previous disk counters for rate calculation
        self.prev_disk_io = psutil.disk_io_counters()
        self.prev_disk_time = time.time()

        # Get system information
        self.system_info = self._get_system_info()

    def start_collection(self) -> None:
        """
        Start collecting metrics.
        """
        if self.running:
            logger.warning("Host metrics collection already running")
            return

        logger.info("Starting host metrics collection")
        self.running = True
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True
        self.collection_thread.start()

    def stop_collection(self) -> None:
        """
        Stop collecting metrics.
        """
        logger.info("Stopping host metrics collection")
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)

    def _collection_loop(self) -> None:
        """
        Main metrics collection loop.
        """
        while self.running:
            try:
                metrics = self.collect_metrics()
                self._store_metrics(metrics)
                self._cleanup_old_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error("Error in host metrics collection: %s", e)
                time.sleep(5)  # Wait a bit before retrying

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect metrics from the host system.

        Returns:
            A dictionary of host metrics
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {},
            "memory": {},
            "disk": {},
            "network": {},
        }

        # Collect CPU metrics
        if self.enabled_metrics.get("cpu", True):
            metrics["cpu"] = self._collect_cpu_metrics()

        # Collect memory metrics
        if self.enabled_metrics.get("memory", True):
            metrics["memory"] = self._collect_memory_metrics()

        # Collect disk metrics
        if self.enabled_metrics.get("disk", True):
            metrics["disk"] = self._collect_disk_metrics()

        # Collect network metrics
        if self.enabled_metrics.get("network", True):
            metrics["network"] = self._collect_network_metrics()

        return metrics

    def _collect_cpu_metrics(self) -> Dict[str, Any]:
        """
        Collect CPU metrics.

        Returns:
            A dictionary of CPU metrics
        """
        cpu_metrics = {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count(),
            "physical_count": psutil.cpu_count(logical=False),
            "per_cpu": psutil.cpu_percent(interval=0.1, percpu=True),
            "load_avg": psutil.getloadavg(),
        }

        # Add CPU frequency if available
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_metrics["frequency"] = {
                    "current": cpu_freq.current,
                    "min": cpu_freq.min,
                    "max": cpu_freq.max,
                }
        except Exception:
            pass

        # Add CPU times
        cpu_times = psutil.cpu_times_percent()
        cpu_metrics["times"] = {
            "user": cpu_times.user,
            "system": cpu_times.system,
            "idle": cpu_times.idle,
            "iowait": getattr(cpu_times, "iowait", 0),
            "irq": getattr(cpu_times, "irq", 0),
            "softirq": getattr(cpu_times, "softirq", 0),
            "steal": getattr(cpu_times, "steal", 0),
            "guest": getattr(cpu_times, "guest", 0),
        }

        return cpu_metrics

    def _collect_memory_metrics(self) -> Dict[str, Any]:
        """
        Collect memory metrics.

        Returns:
            A dictionary of memory metrics
        """
        virtual_memory = psutil.virtual_memory()
        swap_memory = psutil.swap_memory()

        memory_metrics = {
            "virtual": {
                "total": virtual_memory.total,
                "available": virtual_memory.available,
                "used": virtual_memory.used,
                "free": virtual_memory.free,
                "percent": virtual_memory.percent,
                "active": getattr(virtual_memory, "active", 0),
                "inactive": getattr(virtual_memory, "inactive", 0),
                "buffers": getattr(virtual_memory, "buffers", 0),
                "cached": getattr(virtual_memory, "cached", 0),
                "shared": getattr(virtual_memory, "shared", 0),
            },
            "swap": {
                "total": swap_memory.total,
                "used": swap_memory.used,
                "free": swap_memory.free,
                "percent": swap_memory.percent,
                "sin": swap_memory.sin,
                "sout": swap_memory.sout,
            },
        }

        return memory_metrics

    def _collect_disk_metrics(self) -> Dict[str, Any]:
        """
        Collect disk metrics.

        Returns:
            A dictionary of disk metrics
        """
        disk_metrics = {"usage": {}, "io": {}}

        # Collect disk usage for all mounted partitions
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_metrics["usage"][partition.mountpoint] = {
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                    "device": partition.device,
                    "fstype": partition.fstype,
                }
            except (PermissionError, OSError):
                # Skip partitions that can't be accessed
                pass

        # Collect disk I/O statistics
        try:
            current_disk_io = psutil.disk_io_counters()
            current_time = time.time()
            time_diff = current_time - self.prev_disk_time

            if time_diff > 0 and self.prev_disk_io:
                read_bytes_rate = (
                    current_disk_io.read_bytes - self.prev_disk_io.read_bytes
                ) / time_diff
                write_bytes_rate = (
                    current_disk_io.write_bytes - self.prev_disk_io.write_bytes
                ) / time_diff
                read_count_rate = (
                    current_disk_io.read_count - self.prev_disk_io.read_count
                ) / time_diff
                write_count_rate = (
                    current_disk_io.write_count - self.prev_disk_io.write_count
                ) / time_diff

                disk_metrics["io"] = {
                    "read_bytes": current_disk_io.read_bytes,
                    "write_bytes": current_disk_io.write_bytes,
                    "read_count": current_disk_io.read_count,
                    "write_count": current_disk_io.write_count,
                    "read_bytes_rate": read_bytes_rate,
                    "write_bytes_rate": write_bytes_rate,
                    "read_count_rate": read_count_rate,
                    "write_count_rate": write_count_rate,
                    "read_time": getattr(current_disk_io, "read_time", 0),
                    "write_time": getattr(current_disk_io, "write_time", 0),
                    "busy_time": getattr(current_disk_io, "busy_time", 0),
                }

            self.prev_disk_io = current_disk_io
            self.prev_disk_time = current_time
        except Exception as e:
            logger.warning("Error collecting disk I/O metrics: %s", e)

        return disk_metrics

    def _collect_network_metrics(self) -> Dict[str, Any]:
        """
        Collect network metrics.

        Returns:
            A dictionary of network metrics
        """
        network_metrics = {"io": {}, "connections": {}}

        # Collect network I/O statistics
        try:
            current_net_io = psutil.net_io_counters()
            current_time = time.time()
            time_diff = current_time - self.prev_net_time

            if time_diff > 0 and self.prev_net_io:
                bytes_sent_rate = (
                    current_net_io.bytes_sent - self.prev_net_io.bytes_sent
                ) / time_diff
                bytes_recv_rate = (
                    current_net_io.bytes_recv - self.prev_net_io.bytes_recv
                ) / time_diff
                packets_sent_rate = (
                    current_net_io.packets_sent - self.prev_net_io.packets_sent
                ) / time_diff
                packets_recv_rate = (
                    current_net_io.packets_recv - self.prev_net_io.packets_recv
                ) / time_diff

                network_metrics["io"] = {
                    "bytes_sent": current_net_io.bytes_sent,
                    "bytes_recv": current_net_io.bytes_recv,
                    "packets_sent": current_net_io.packets_sent,
                    "packets_recv": current_net_io.packets_recv,
                    "errin": current_net_io.errin,
                    "errout": current_net_io.errout,
                    "dropin": current_net_io.dropin,
                    "dropout": current_net_io.dropout,
                    "bytes_sent_rate": bytes_sent_rate,
                    "bytes_recv_rate": bytes_recv_rate,
                    "packets_sent_rate": packets_sent_rate,
                    "packets_recv_rate": packets_recv_rate,
                }

            self.prev_net_io = current_net_io
            self.prev_net_time = current_time
        except Exception as e:
            logger.warning("Error collecting network I/O metrics: %s", e)

        # Collect network interfaces
        try:
            network_metrics["interfaces"] = {}
            for interface, stats in psutil.net_if_stats().items():
                network_metrics["interfaces"][interface] = {
                    "isup": stats.isup,
                    "duplex": stats.duplex,
                    "speed": stats.speed,
                    "mtu": stats.mtu,
                }

                # Add address information
                addresses = psutil.net_if_addrs().get(interface, [])
                network_metrics["interfaces"][interface]["addresses"] = []
                for addr in addresses:
                    network_metrics["interfaces"][interface]["addresses"].append(
                        {
                            "family": addr.family,
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                            "ptp": addr.ptp,
                        }
                    )
        except Exception as e:
            logger.warning("Error collecting network interface metrics: %s", e)

        # Collect network connection statistics
        try:
            connections = psutil.net_connections(kind="inet")
            connection_stats = {
                "ESTABLISHED": 0,
                "SYN_SENT": 0,
                "SYN_RECV": 0,
                "FIN_WAIT1": 0,
                "FIN_WAIT2": 0,
                "TIME_WAIT": 0,
                "CLOSE": 0,
                "CLOSE_WAIT": 0,
                "LAST_ACK": 0,
                "LISTEN": 0,
                "CLOSING": 0,
                "NONE": 0,
            }

            for conn in connections:
                status = conn.status
                connection_stats[status] = connection_stats.get(status, 0) + 1

            network_metrics["connections"] = connection_stats
        except Exception as e:
            logger.warning("Error collecting network connection metrics: %s", e)

        return network_metrics

    def _store_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Store metrics to disk.

        Args:
            metrics: The metrics to store
        """
        timestamp = datetime.fromisoformat(metrics["timestamp"])
        date_str = timestamp.strftime("%Y-%m-%d")
        hour_str = timestamp.strftime("%H")

        # Create directory for date if it doesn't exist
        date_dir = os.path.join(self.host_metrics_path, date_str)
        ensure_directory_exists(date_dir)

        # Store metrics in hourly files
        file_path = os.path.join(date_dir, f"{hour_str}.jsonl")
        with open(file_path, "a") as f:
            f.write(json.dumps(metrics) + "\n")

        # Update in-memory metrics history
        for metric_type in ["cpu", "memory", "disk", "network"]:
            if metric_type in metrics:
                self.metrics_history[metric_type].append(
                    {"timestamp": metrics["timestamp"], "data": metrics[metric_type]}
                )

                # Limit the size of in-memory history
                max_history_size = 1000  # Keep last 1000 samples in memory
                if len(self.metrics_history[metric_type]) > max_history_size:
                    self.metrics_history[metric_type] = self.metrics_history[
                        metric_type
                    ][-max_history_size:]

    def _cleanup_old_metrics(self) -> None:
        """
        Clean up old metrics files.
        """
        try:
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=self.retention_period)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")

            # List all date directories
            for date_dir in os.listdir(self.host_metrics_path):
                if date_dir < cutoff_date_str:
                    # Remove old directory
                    date_path = os.path.join(self.host_metrics_path, date_dir)
                    if os.path.isdir(date_path):
                        for file in os.listdir(date_path):
                            os.remove(os.path.join(date_path, file))
                        os.rmdir(date_path)
                        logger.info("Removed old metrics directory: %s", date_path)
        except Exception as e:
            logger.error("Error cleaning up old metrics: %s", e)

    def get_metrics_history(
        self, metric_type: str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get metrics history for a specific metric type.

        Args:
            metric_type: The type of metric (cpu, memory, disk, network)
            start_time: The start time for the metrics
            end_time: The end time for the metrics

        Returns:
            A list of metrics
        """
        if metric_type not in self.metrics_history:
            return []

        # Filter metrics by time range
        filtered_metrics = []
        for metric in self.metrics_history[metric_type]:
            timestamp = datetime.fromisoformat(metric["timestamp"])
            if start_time <= timestamp <= end_time:
                filtered_metrics.append(metric)

        return filtered_metrics

    def get_latest_metrics(self) -> Dict[str, Any]:
        """
        Get the latest metrics.

        Returns:
            The latest metrics
        """
        return self.collect_metrics()

    def _get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.

        Returns:
            A dictionary of system information
        """
        system_info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "memory_total": psutil.virtual_memory().total,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        }

        # Add Docker information
        try:
            docker_info = self.client.info()
            system_info["docker"] = {
                "version": docker_info.get("ServerVersion", ""),
                "containers": docker_info.get("Containers", 0),
                "running": docker_info.get("ContainersRunning", 0),
                "paused": docker_info.get("ContainersPaused", 0),
                "stopped": docker_info.get("ContainersStopped", 0),
                "images": docker_info.get("Images", 0),
                "driver": docker_info.get("Driver", ""),
                "storage_driver": docker_info.get("Driver", ""),
                "logging_driver": docker_info.get("LoggingDriver", ""),
                "cgroup_driver": docker_info.get("CgroupDriver", ""),
                "kernel_version": docker_info.get("KernelVersion", ""),
                "operating_system": docker_info.get("OperatingSystem", ""),
                "os_type": docker_info.get("OSType", ""),
                "architecture": docker_info.get("Architecture", ""),
                "cpus": docker_info.get("NCPU", 0),
                "memory": docker_info.get("MemTotal", 0),
                "docker_root_dir": docker_info.get("DockerRootDir", ""),
                "index_server_address": docker_info.get("IndexServerAddress", ""),
                "registry_config": docker_info.get("RegistryConfig", {}),
            }
        except Exception as e:
            logger.warning("Error getting Docker information: %s", e)
            system_info["docker"] = {"error": str(e)}

        return system_info

    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.

        Returns:
            A dictionary of system information
        """
        return self.system_info
