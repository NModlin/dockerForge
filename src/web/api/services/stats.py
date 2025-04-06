"""
Stats service for the DockerForge Web UI.

This module provides container stats services for monitoring container resource usage.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import WebSocket
from sqlalchemy.orm import Session

import docker
from docker.errors import DockerException
from src.web.api.models.monitoring import MetricSample
from src.web.api.services import docker as docker_service

# Configure logging
logger = logging.getLogger(__name__)

# Docker client
docker_client = docker.from_env()


# Stats session class
class StatsSession:
    def __init__(self, container_id: str, interval: int = 5):
        self.container_id = container_id
        self.interval = interval  # Seconds between stats updates
        self.last_update = datetime.now()
        self.stats_history: List[Dict[str, Any]] = []
        self.max_history_length = 60  # Store up to 60 data points
        self.active = True


# Store active stats sessions
class StatsManager:
    def __init__(self):
        # Dictionary mapping session IDs to stats sessions
        self.active_sessions: Dict[str, "StatsSession"] = {}
        # Dictionary mapping container IDs to lists of WebSocket connections
        self.container_subscribers: Dict[str, List[WebSocket]] = {}
        # Flag to control the background stats collection task
        self.running = False
        # Background task
        self.background_task = None

    async def start_background_collection(self):
        """
        Start the background stats collection task.
        """
        if self.running:
            return

        self.running = True
        self.background_task = asyncio.create_task(self._collect_stats_background())
        logger.info("Started background stats collection task")

    async def stop_background_collection(self):
        """
        Stop the background stats collection task.
        """
        if not self.running:
            return

        self.running = False
        if self.background_task:
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                pass
            self.background_task = None
        logger.info("Stopped background stats collection task")

    async def _collect_stats_background(self):
        """
        Background task to collect stats for all running containers.
        """
        try:
            while self.running:
                # Get all running containers
                containers = docker_client.containers.list(
                    filters={"status": "running"}
                )

                # Collect stats for each container
                for container in containers:
                    try:
                        # Get container stats
                        stats = container.stats(stream=False)
                        parsed_stats = docker_service.parse_stats(stats)

                        # Add timestamp
                        parsed_stats["timestamp"] = datetime.now().isoformat()

                        # Broadcast to subscribers
                        await self._broadcast_stats(container.id, parsed_stats)

                    except Exception as e:
                        logger.error(
                            f"Error collecting stats for container {container.id}: {str(e)}"
                        )

                # Wait before next collection
                await asyncio.sleep(2)  # Collect stats every 2 seconds

        except asyncio.CancelledError:
            logger.info("Background stats collection task cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in background stats collection task: {str(e)}")
            self.running = False

    async def _broadcast_stats(self, container_id: str, stats: Dict[str, Any]):
        """
        Broadcast stats to all subscribers for a container.

        Args:
            container_id: Container ID
            stats: Container stats
        """
        if container_id not in self.container_subscribers:
            return

        # Prepare message
        message = {
            "type": "stats",
            "container_id": container_id,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }

        # Send to all subscribers
        subscribers = self.container_subscribers[container_id]
        closed_connections = []

        for websocket in subscribers:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending stats to subscriber: {str(e)}")
                closed_connections.append(websocket)

        # Remove closed connections
        for websocket in closed_connections:
            subscribers.remove(websocket)

        # Remove container from subscribers if no connections left
        if not subscribers:
            del self.container_subscribers[container_id]

    async def subscribe(self, container_id: str, websocket: WebSocket):
        """
        Subscribe to stats for a container.

        Args:
            container_id: Container ID
            websocket: WebSocket connection
        """
        if container_id not in self.container_subscribers:
            self.container_subscribers[container_id] = []

        self.container_subscribers[container_id].append(websocket)
        logger.info(f"Subscribed to stats for container {container_id}")

    async def unsubscribe(self, container_id: str, websocket: WebSocket):
        """
        Unsubscribe from stats for a container.

        Args:
            container_id: Container ID
            websocket: WebSocket connection
        """
        if container_id in self.container_subscribers:
            if websocket in self.container_subscribers[container_id]:
                self.container_subscribers[container_id].remove(websocket)

            if not self.container_subscribers[container_id]:
                del self.container_subscribers[container_id]

        logger.info(f"Unsubscribed from stats for container {container_id}")

    def get_subscriber_count(self, container_id: str) -> int:
        """
        Get the number of subscribers for a container.

        Args:
            container_id: Container ID

        Returns:
            Number of subscribers
        """
        if container_id not in self.container_subscribers:
            return 0

        return len(self.container_subscribers[container_id])

    def get_total_subscriber_count(self) -> int:
        """
        Get the total number of subscribers.

        Returns:
            Total number of subscribers
        """
        count = 0
        for subscribers in self.container_subscribers.values():
            count += len(subscribers)

        return count


async def get_container_stats(container_id: str) -> Optional[Dict[str, Any]]:
    """
    Get current stats for a container.

    Args:
        container_id: Container ID

    Returns:
        Container stats or None if not found
    """
    try:
        # Get container
        container = docker_client.containers.get(container_id)

        # Check if container is running
        if container.status != "running":
            return None

        # Get container stats
        stats = container.stats(stream=False)
        parsed_stats = docker_service.parse_stats(stats)

        # Add timestamp
        parsed_stats["timestamp"] = datetime.now().isoformat()

        return parsed_stats
    except DockerException as e:
        logger.error(f"Docker error getting container stats: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error getting container stats: {str(e)}")
        return None


async def get_container_stats_history(
    container_id: str,
    metric_type: str,
    start_time: datetime,
    end_time: datetime,
    db: Session,
) -> List[Dict[str, Any]]:
    """
    Get historical stats for a container.

    Args:
        container_id: Container ID
        metric_type: Metric type (cpu, memory, network, disk)
        start_time: Start time
        end_time: End time
        db: Database session

    Returns:
        List of stats
    """
    try:
        # Query database for historical stats
        query = db.query(MetricSample).filter(
            MetricSample.container_id == container_id,
            MetricSample.timestamp >= start_time,
            MetricSample.timestamp <= end_time,
        )

        if metric_type:
            query = query.filter(MetricSample.metric_type == metric_type)

        # Order by timestamp
        query = query.order_by(MetricSample.timestamp)

        # Get results
        samples = query.all()

        # Convert to dict
        return [
            {
                "metric_type": sample.metric_type,
                "timestamp": sample.timestamp.isoformat(),
                "value": sample.value,
                "unit": sample.unit,
                "labels": sample.labels,
            }
            for sample in samples
        ]
    except Exception as e:
        logger.error(f"Error getting container stats history: {str(e)}")
        return []


async def store_container_stats(
    container_id: str, stats: Dict[str, Any], db: Session
) -> bool:
    """
    Store container stats in the database.

    Args:
        container_id: Container ID
        stats: Container stats
        db: Database session

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create metric samples
        timestamp = datetime.now()

        # CPU usage
        cpu_sample = MetricSample(
            container_id=container_id,
            metric_type="cpu",
            timestamp=timestamp,
            value=stats["cpu_percent"],
            unit="%",
            labels={"type": "usage"},
        )

        # Memory usage
        memory_sample = MetricSample(
            container_id=container_id,
            metric_type="memory",
            timestamp=timestamp,
            value=stats["memory_usage"],
            unit="bytes",
            labels={"type": "usage"},
        )

        # Memory percent
        memory_percent_sample = MetricSample(
            container_id=container_id,
            metric_type="memory",
            timestamp=timestamp,
            value=stats["memory_percent"],
            unit="%",
            labels={"type": "percent"},
        )

        # Network RX
        network_rx_sample = MetricSample(
            container_id=container_id,
            metric_type="network",
            timestamp=timestamp,
            value=stats["network_rx_bytes"],
            unit="bytes",
            labels={"type": "rx"},
        )

        # Network TX
        network_tx_sample = MetricSample(
            container_id=container_id,
            metric_type="network",
            timestamp=timestamp,
            value=stats["network_tx_bytes"],
            unit="bytes",
            labels={"type": "tx"},
        )

        # Block read
        block_read_sample = MetricSample(
            container_id=container_id,
            metric_type="disk",
            timestamp=timestamp,
            value=stats["block_read_bytes"],
            unit="bytes",
            labels={"type": "read"},
        )

        # Block write
        block_write_sample = MetricSample(
            container_id=container_id,
            metric_type="disk",
            timestamp=timestamp,
            value=stats["block_write_bytes"],
            unit="bytes",
            labels={"type": "write"},
        )

        # Add to database
        db.add_all(
            [
                cpu_sample,
                memory_sample,
                memory_percent_sample,
                network_rx_sample,
                network_tx_sample,
                block_read_sample,
                block_write_sample,
            ]
        )

        # Commit
        db.commit()

        return True
    except Exception as e:
        logger.error(f"Error storing container stats: {str(e)}")
        db.rollback()
        return False


# Create stats manager instance
stats_manager = StatsManager()


def get_stats_manager() -> StatsManager:
    """
    Get the stats manager instance.

    Returns:
        Stats manager
    """
    return stats_manager
