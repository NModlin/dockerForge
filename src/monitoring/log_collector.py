"""
Log collector module for DockerForge.

This module provides functionality to collect logs from Docker containers
in real-time, with efficient buffering and filtering capabilities.
"""

import os
import time
import threading
import logging
import queue
from typing import Dict, Any, List, Optional, Callable, Tuple, Set, Union
from datetime import datetime, timedelta
from collections import deque

from docker.models.containers import Container
from docker.errors import DockerException

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.docker.connection_manager import get_docker_client, DockerConnectionError

logger = get_logger("log_collector")


class LogEntry:
    """Represents a single log entry from a container."""
    
    def __init__(
        self,
        container_id: str,
        container_name: str,
        timestamp: datetime,
        message: str,
        stream: str = "stdout"
    ):
        """
        Initialize a log entry.
        
        Args:
            container_id: Container ID
            container_name: Container name
            timestamp: Log timestamp
            message: Log message
            stream: Log stream (stdout or stderr)
        """
        self.container_id = container_id
        self.container_name = container_name
        self.timestamp = timestamp
        self.message = message
        self.stream = stream
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert log entry to dictionary.
        
        Returns:
            Dict[str, Any]: Log entry as dictionary
        """
        return {
            "container_id": self.container_id,
            "container_name": self.container_name,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "stream": self.stream,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """
        Create log entry from dictionary.
        
        Args:
            data: Dictionary with log entry data
            
        Returns:
            LogEntry: Log entry
        """
        return cls(
            container_id=data["container_id"],
            container_name=data["container_name"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message=data["message"],
            stream=data["stream"],
        )
    
    def __str__(self) -> str:
        """String representation of log entry."""
        return f"[{self.timestamp.isoformat()}] {self.container_name}: {self.message}"


class CircularLogBuffer:
    """
    Circular buffer for storing log entries with a maximum size.
    
    This buffer automatically removes the oldest entries when the
    maximum size is reached.
    """
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize circular log buffer.
        
        Args:
            max_size: Maximum number of log entries to store
        """
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.lock = threading.RLock()
    
    def add(self, entry: LogEntry) -> None:
        """
        Add a log entry to the buffer.
        
        Args:
            entry: Log entry to add
        """
        with self.lock:
            self.buffer.append(entry)
    
    def get_all(self) -> List[LogEntry]:
        """
        Get all log entries in the buffer.
        
        Returns:
            List[LogEntry]: All log entries
        """
        with self.lock:
            return list(self.buffer)
    
    def get_last(self, count: int) -> List[LogEntry]:
        """
        Get the last N log entries.
        
        Args:
            count: Number of entries to get
            
        Returns:
            List[LogEntry]: Last N log entries
        """
        with self.lock:
            return list(self.buffer)[-count:] if count < len(self.buffer) else list(self.buffer)
    
    def get_since(self, timestamp: datetime) -> List[LogEntry]:
        """
        Get log entries since a specific timestamp.
        
        Args:
            timestamp: Timestamp to filter by
            
        Returns:
            List[LogEntry]: Log entries since timestamp
        """
        with self.lock:
            return [entry for entry in self.buffer if entry.timestamp >= timestamp]
    
    def clear(self) -> None:
        """Clear the buffer."""
        with self.lock:
            self.buffer.clear()
    
    def __len__(self) -> int:
        """Get the number of entries in the buffer."""
        with self.lock:
            return len(self.buffer)


class LogFilter:
    """Filter for log entries based on various criteria."""
    
    def __init__(
        self,
        container_ids: Optional[List[str]] = None,
        container_names: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        message_contains: Optional[List[str]] = None,
        message_regex: Optional[str] = None,
        streams: Optional[List[str]] = None,
    ):
        """
        Initialize log filter.
        
        Args:
            container_ids: List of container IDs to include
            container_names: List of container names to include
            since: Include logs since this timestamp
            until: Include logs until this timestamp
            message_contains: Include logs containing these strings
            message_regex: Include logs matching this regex
            streams: List of streams to include (stdout, stderr)
        """
        self.container_ids = set(container_ids) if container_ids else None
        self.container_names = set(container_names) if container_names else None
        self.since = since
        self.until = until
        self.message_contains = message_contains
        self.message_regex = message_regex
        self.streams = set(streams) if streams else None
        
        # Compile regex if provided
        self.regex = None
        if message_regex:
            import re
            try:
                self.regex = re.compile(message_regex)
            except re.error as e:
                logger.error(f"Invalid regex pattern: {str(e)}")
    
    def matches(self, entry: LogEntry) -> bool:
        """
        Check if a log entry matches the filter.
        
        Args:
            entry: Log entry to check
            
        Returns:
            bool: True if the entry matches the filter
        """
        # Check container ID
        if self.container_ids and entry.container_id not in self.container_ids:
            return False
        
        # Check container name
        if self.container_names and entry.container_name not in self.container_names:
            return False
        
        # Check timestamp
        if self.since and entry.timestamp < self.since:
            return False
        if self.until and entry.timestamp > self.until:
            return False
        
        # Check stream
        if self.streams and entry.stream not in self.streams:
            return False
        
        # Check message contains
        if self.message_contains:
            if not any(text in entry.message for text in self.message_contains):
                return False
        
        # Check message regex
        if self.regex:
            if not self.regex.search(entry.message):
                return False
        
        return True
    
    def filter_logs(self, logs: List[LogEntry]) -> List[LogEntry]:
        """
        Filter a list of log entries.
        
        Args:
            logs: List of log entries to filter
            
        Returns:
            List[LogEntry]: Filtered log entries
        """
        return [entry for entry in logs if self.matches(entry)]


class ContainerLogCollector:
    """Collector for logs from a specific container."""
    
    def __init__(
        self,
        container: Container,
        buffer: CircularLogBuffer,
        callback: Optional[Callable[[LogEntry], None]] = None,
    ):
        """
        Initialize container log collector.
        
        Args:
            container: Docker container
            buffer: Circular log buffer
            callback: Optional callback function for new log entries
        """
        self.container = container
        self.container_id = container.id
        self.container_name = container.name
        self.buffer = buffer
        self.callback = callback
        self.running = False
        self.thread = None
        self.last_timestamp = datetime.now() - timedelta(hours=1)  # Start with logs from the last hour
    
    def start(self) -> None:
        """Start collecting logs."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collect_logs, daemon=True)
        self.thread.start()
    
    def stop(self) -> None:
        """Stop collecting logs."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
    
    def _collect_logs(self) -> None:
        """Collect logs from the container."""
        try:
            # Get initial logs
            logs = self.container.logs(
                timestamps=True,
                since=int(self.last_timestamp.timestamp()),
                stream=False,
            )
            
            # Parse initial logs
            self._parse_logs(logs)
            
            # Stream new logs
            for log in self.container.logs(
                timestamps=True,
                follow=True,
                stream=True,
                tail=0,  # Don't repeat logs we've already processed
            ):
                if not self.running:
                    break
                
                self._parse_log_line(log)
        except DockerException as e:
            logger.error(f"Error collecting logs from container {self.container_name}: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error collecting logs from container {self.container_name}: {str(e)}")
        finally:
            self.running = False
    
    def _parse_logs(self, logs: bytes) -> None:
        """
        Parse container logs.
        
        Args:
            logs: Container logs as bytes
        """
        if not logs:
            return
        
        # Split logs into lines
        log_lines = logs.split(b"\n")
        
        # Parse each line
        for line in log_lines:
            if line:
                self._parse_log_line(line)
    
    def _parse_log_line(self, line: bytes) -> None:
        """
        Parse a single log line.
        
        Args:
            line: Log line as bytes
        """
        try:
            # Decode line
            line_str = line.decode("utf-8", errors="replace").strip()
            
            # Parse timestamp and message
            if " " in line_str:
                timestamp_str, message = line_str.split(" ", 1)
                
                # Parse timestamp
                try:
                    # Docker timestamps are in format: 2021-09-01T12:34:56.789012345Z
                    timestamp = datetime.fromisoformat(timestamp_str.rstrip("Z").replace("T", " "))
                except ValueError:
                    # Fallback to current time if timestamp parsing fails
                    timestamp = datetime.now()
                    message = line_str  # Use the whole line as the message
            else:
                # No timestamp, use current time
                timestamp = datetime.now()
                message = line_str
            
            # Determine stream (stdout or stderr)
            # Docker prefixes stderr logs with a specific byte, but this is not
            # always reliable, so we default to stdout
            stream = "stdout"
            
            # Create log entry
            entry = LogEntry(
                container_id=self.container_id,
                container_name=self.container_name,
                timestamp=timestamp,
                message=message,
                stream=stream,
            )
            
            # Update last timestamp
            if timestamp > self.last_timestamp:
                self.last_timestamp = timestamp
            
            # Add to buffer
            self.buffer.add(entry)
            
            # Call callback if provided
            if self.callback:
                self.callback(entry)
        except Exception as e:
            logger.debug(f"Error parsing log line: {str(e)}")


class LogCollectionManager:
    """Manager for collecting logs from multiple containers."""
    
    def __init__(self):
        """Initialize log collection manager."""
        self.collectors = {}  # type: Dict[str, ContainerLogCollector]
        self.buffer = CircularLogBuffer(
            max_size=get_config("monitoring.log_buffer_size", 100000)
        )
        self.callbacks = []  # type: List[Callable[[LogEntry], None]]
        self.running = False
        self.thread = None
        self.lock = threading.RLock()
        
        # Docker client
        self.docker_client = None
        
        # Container filter
        self.container_filter = get_config("monitoring.container_filter", {})
    
    def start(self) -> None:
        """Start log collection."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_containers, daemon=True)
        self.thread.start()
        
        logger.info("Log collection started")
    
    def stop(self) -> None:
        """Stop log collection."""
        self.running = False
        
        # Stop all collectors
        with self.lock:
            for collector in self.collectors.values():
                collector.stop()
            self.collectors.clear()
        
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        logger.info("Log collection stopped")
    
    def add_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """
        Add a callback function for new log entries.
        
        Args:
            callback: Callback function
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[LogEntry], None]) -> None:
        """
        Remove a callback function.
        
        Args:
            callback: Callback function
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _callback(self, entry: LogEntry) -> None:
        """
        Call all registered callbacks for a new log entry.
        
        Args:
            entry: Log entry
        """
        for callback in self.callbacks:
            try:
                callback(entry)
            except Exception as e:
                logger.debug(f"Error in log callback: {str(e)}")
    
    def _monitor_containers(self) -> None:
        """Monitor containers and collect logs."""
        while self.running:
            try:
                # Get Docker client
                if not self.docker_client:
                    self.docker_client = get_docker_client()
                
                # Get running containers
                containers = self.docker_client.containers.list(
                    filters=self.container_filter
                )
                
                # Update collectors
                self._update_collectors(containers)
                
                # Sleep before next update
                time.sleep(10)
            except DockerConnectionError as e:
                logger.error(f"Docker connection error: {str(e)}")
                self.docker_client = None
                time.sleep(30)  # Longer sleep on connection error
            except Exception as e:
                logger.exception(f"Error monitoring containers: {str(e)}")
                time.sleep(30)  # Longer sleep on error
    
    def _update_collectors(self, containers: List[Container]) -> None:
        """
        Update collectors based on running containers.
        
        Args:
            containers: List of running containers
        """
        with self.lock:
            # Get current container IDs
            current_ids = set(self.collectors.keys())
            
            # Get new container IDs
            new_ids = set(container.id for container in containers)
            
            # Stop collectors for containers that are no longer running
            for container_id in current_ids - new_ids:
                collector = self.collectors.pop(container_id, None)
                if collector:
                    collector.stop()
                    logger.debug(f"Stopped log collection for container {collector.container_name}")
            
            # Start collectors for new containers
            for container in containers:
                if container.id not in self.collectors:
                    collector = ContainerLogCollector(
                        container=container,
                        buffer=self.buffer,
                        callback=self._callback,
                    )
                    collector.start()
                    self.collectors[container.id] = collector
                    logger.debug(f"Started log collection for container {container.name}")
    
    def get_logs(
        self,
        container_ids: Optional[List[str]] = None,
        container_names: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        message_contains: Optional[List[str]] = None,
        message_regex: Optional[str] = None,
        streams: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """
        Get filtered logs.
        
        Args:
            container_ids: List of container IDs to include
            container_names: List of container names to include
            since: Include logs since this timestamp
            until: Include logs until this timestamp
            message_contains: Include logs containing these strings
            message_regex: Include logs matching this regex
            streams: List of streams to include (stdout, stderr)
            limit: Maximum number of logs to return
            
        Returns:
            List[LogEntry]: Filtered logs
        """
        # Create filter
        log_filter = LogFilter(
            container_ids=container_ids,
            container_names=container_names,
            since=since,
            until=until,
            message_contains=message_contains,
            message_regex=message_regex,
            streams=streams,
        )
        
        # Get all logs
        all_logs = self.buffer.get_all()
        
        # Apply filter
        filtered_logs = log_filter.filter_logs(all_logs)
        
        # Sort by timestamp
        filtered_logs.sort(key=lambda entry: entry.timestamp)
        
        # Apply limit
        if limit and len(filtered_logs) > limit:
            filtered_logs = filtered_logs[-limit:]
        
        return filtered_logs
    
    def get_container_logs(
        self,
        container_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        message_contains: Optional[List[str]] = None,
        message_regex: Optional[str] = None,
        streams: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """
        Get logs for a specific container.
        
        Args:
            container_id: Container ID
            since: Include logs since this timestamp
            until: Include logs until this timestamp
            message_contains: Include logs containing these strings
            message_regex: Include logs matching this regex
            streams: List of streams to include (stdout, stderr)
            limit: Maximum number of logs to return
            
        Returns:
            List[LogEntry]: Container logs
        """
        return self.get_logs(
            container_ids=[container_id],
            since=since,
            until=until,
            message_contains=message_contains,
            message_regex=message_regex,
            streams=streams,
            limit=limit,
        )
    
    def get_container_names(self) -> List[str]:
        """
        Get names of containers being monitored.
        
        Returns:
            List[str]: Container names
        """
        with self.lock:
            return [collector.container_name for collector in self.collectors.values()]
    
    def get_container_ids(self) -> List[str]:
        """
        Get IDs of containers being monitored.
        
        Returns:
            List[str]: Container IDs
        """
        with self.lock:
            return list(self.collectors.keys())
    
    def clear_logs(self) -> None:
        """Clear all logs."""
        self.buffer.clear()


# Singleton instance
_log_collection_manager = None


def get_log_collection_manager() -> LogCollectionManager:
    """
    Get the log collection manager (singleton).
    
    Returns:
        LogCollectionManager: Log collection manager
    """
    global _log_collection_manager
    if _log_collection_manager is None:
        _log_collection_manager = LogCollectionManager()
    
    return _log_collection_manager
