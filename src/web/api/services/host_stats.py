"""
Host stats service for the DockerForge Web UI.

This module provides host system stats services for monitoring host resource usage.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import psutil
from sqlalchemy.orm import Session

from src.config.config_manager import get_config_manager
from src.docker.connection_manager import get_connection_manager
from src.resource_monitoring.host_metrics_collector import HostMetricsCollector
from src.web.api.models.monitoring import MetricSample

# Configure logging
logger = logging.getLogger(__name__)

# Host metrics collector instance
_host_metrics_collector = None


def get_host_metrics_collector() -> HostMetricsCollector:
    """
    Get the host metrics collector instance.

    Returns:
        Host metrics collector
    """
    global _host_metrics_collector

    if _host_metrics_collector is None:
        # Initialize host metrics collector
        config_manager = get_config_manager()
        connection_manager = get_connection_manager()
        _host_metrics_collector = HostMetricsCollector(
            config_manager, connection_manager
        )

        # Start collection
        _host_metrics_collector.start_collection()

    return _host_metrics_collector


async def get_host_metrics() -> Dict[str, Any]:
    """
    Get current host metrics.

    Returns:
        Host metrics
    """
    # Get host metrics collector
    collector = get_host_metrics_collector()

    # Get latest metrics
    metrics = collector.get_latest_metrics()

    return metrics


async def get_host_metrics_history(
    metric_type: str, start_time: datetime, end_time: datetime
) -> List[Dict[str, Any]]:
    """
    Get historical host metrics.

    Args:
        metric_type: Metric type (cpu, memory, disk, network)
        start_time: Start time
        end_time: End time

    Returns:
        List of metrics
    """
    # Get host metrics collector
    collector = get_host_metrics_collector()

    # Get metrics history
    metrics = collector.get_metrics_history(metric_type, start_time, end_time)

    return metrics


async def get_system_info() -> Dict[str, Any]:
    """
    Get system information.

    Returns:
        System information
    """
    # Get host metrics collector
    collector = get_host_metrics_collector()

    # Get system information
    system_info = collector.get_system_info()

    return system_info


async def get_resource_stats_summary() -> Dict[str, Any]:
    """
    Get resource stats summary.

    Returns:
        Resource stats summary
    """
    # Get host metrics collector
    collector = get_host_metrics_collector()

    # Get latest metrics
    metrics = collector.get_latest_metrics()

    # Get system information
    system_info = collector.get_system_info()

    # Calculate summary
    summary = {
        "cpu_usage": metrics["cpu"]["percent"],
        "cpu_cores": metrics["cpu"]["count"],
        "memory_usage_percent": metrics["memory"]["virtual"]["percent"],
        "memory_used": metrics["memory"]["virtual"]["used"],
        "memory_total": metrics["memory"]["virtual"]["total"],
        "disk_usage_percent": 0,
        "disk_used": 0,
        "disk_total": 0,
        "container_count": system_info["docker"]["containers"],
        "running_containers": system_info["docker"]["running"],
        "image_count": system_info["docker"]["images"],
        "volume_count": 0,  # Need to get from Docker API
        "network_count": 0,  # Need to get from Docker API
    }

    # Calculate disk usage (average across all partitions)
    if metrics["disk"]["usage"]:
        total_disk_percent = 0
        total_disk_used = 0
        total_disk_total = 0
        partition_count = 0

        for partition, usage in metrics["disk"]["usage"].items():
            total_disk_percent += usage["percent"]
            total_disk_used += usage["used"]
            total_disk_total += usage["total"]
            partition_count += 1

        if partition_count > 0:
            summary["disk_usage_percent"] = total_disk_percent / partition_count
            summary["disk_used"] = total_disk_used
            summary["disk_total"] = total_disk_total

    # Get volume and network counts from Docker
    try:
        docker_client = get_connection_manager().get_client()
        summary["volume_count"] = len(docker_client.volumes.list())
        summary["network_count"] = len(docker_client.networks.list())

        # Get container stats
        containers = []
        for container in docker_client.containers.list(
            all=False
        ):  # Only running containers
            try:
                # Get container stats
                stats = container.stats(stream=False)

                # Calculate CPU usage percentage
                cpu_delta = (
                    stats["cpu_stats"]["cpu_usage"]["total_usage"]
                    - stats["precpu_stats"]["cpu_usage"]["total_usage"]
                )
                system_delta = (
                    stats["cpu_stats"]["system_cpu_usage"]
                    - stats["precpu_stats"]["system_cpu_usage"]
                )
                cpu_percent = 0.0
                if system_delta > 0 and cpu_delta > 0:
                    cpu_percent = (
                        (cpu_delta / system_delta)
                        * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
                        * 100.0
                    )

                # Calculate memory usage percentage
                memory_usage = stats["memory_stats"].get("usage", 0)
                memory_limit = stats["memory_stats"].get("limit", 1)
                memory_percent = (
                    (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
                )

                # Add container stats
                containers.append(
                    {
                        "id": container.id,
                        "name": container.name,
                        "cpu_percent": round(cpu_percent, 2),
                        "memory_percent": round(memory_percent, 2),
                        "memory_usage": memory_usage,
                    }
                )
            except Exception as e:
                logger.error(
                    f"Error getting stats for container {container.id}: {str(e)}"
                )

        # Add containers to summary
        summary["containers"] = containers
    except Exception as e:
        logger.error(f"Error getting Docker volume and network counts: {str(e)}")

    return summary


async def store_host_metrics(metrics: Dict[str, Any], db: Session) -> bool:
    """
    Store host metrics in the database.

    Args:
        metrics: Host metrics
        db: Database session

    Returns:
        True if successful, False otherwise
    """
    try:
        # Parse timestamp
        timestamp = datetime.fromisoformat(metrics["timestamp"])

        # Create metric samples
        samples = []

        # CPU metrics
        samples.append(
            MetricSample(
                container_id=None,  # None for host metrics
                metric_type="cpu.percent",
                timestamp=timestamp,
                value=metrics["cpu"]["percent"],
                unit="%",
                labels={"type": "host"},
            )
        )

        # Memory metrics
        samples.append(
            MetricSample(
                container_id=None,
                metric_type="memory.percent",
                timestamp=timestamp,
                value=metrics["memory"]["virtual"]["percent"],
                unit="%",
                labels={"type": "host"},
            )
        )

        samples.append(
            MetricSample(
                container_id=None,
                metric_type="memory.used",
                timestamp=timestamp,
                value=metrics["memory"]["virtual"]["used"],
                unit="B",
                labels={"type": "host"},
            )
        )

        # Disk metrics
        if metrics["disk"]["usage"]:
            # Calculate average disk usage
            total_disk_percent = 0
            total_disk_used = 0
            partition_count = 0

            for partition, usage in metrics["disk"]["usage"].items():
                total_disk_percent += usage["percent"]
                total_disk_used += usage["used"]
                partition_count += 1

            if partition_count > 0:
                samples.append(
                    MetricSample(
                        container_id=None,
                        metric_type="disk.percent",
                        timestamp=timestamp,
                        value=total_disk_percent / partition_count,
                        unit="%",
                        labels={"type": "host"},
                    )
                )

                samples.append(
                    MetricSample(
                        container_id=None,
                        metric_type="disk.used",
                        timestamp=timestamp,
                        value=total_disk_used,
                        unit="B",
                        labels={"type": "host"},
                    )
                )

        # Network metrics
        if "io" in metrics["network"]:
            samples.append(
                MetricSample(
                    container_id=None,
                    metric_type="network.bytes_sent_rate",
                    timestamp=timestamp,
                    value=metrics["network"]["io"].get("bytes_sent_rate", 0),
                    unit="B/s",
                    labels={"type": "host"},
                )
            )

            samples.append(
                MetricSample(
                    container_id=None,
                    metric_type="network.bytes_recv_rate",
                    timestamp=timestamp,
                    value=metrics["network"]["io"].get("bytes_recv_rate", 0),
                    unit="B/s",
                    labels={"type": "host"},
                )
            )

        # Add to database
        db.add_all(samples)

        # Commit
        db.commit()

        return True
    except Exception as e:
        logger.error(f"Error storing host metrics: {str(e)}")
        db.rollback()
        return False
