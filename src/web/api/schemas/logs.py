"""
Log schemas for the DockerForge Web UI.

This module provides the Pydantic models for log management.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class LogLevel(str, Enum):
    """Log level values."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class LogSource(str, Enum):
    """Log source types."""

    CONTAINER = "container"
    IMAGE = "image"
    VOLUME = "volume"
    NETWORK = "network"
    SYSTEM = "system"


class LogStream(str, Enum):
    """Log stream types for containers."""

    STDOUT = "stdout"
    STDERR = "stderr"
    BOTH = "both"


class LogRetentionPolicy(BaseModel):
    """Log retention policy schema."""

    max_age_days: Optional[int] = Field(None, description="Maximum age in days")
    max_size_mb: Optional[int] = Field(None, description="Maximum size in MB")
    max_entries: Optional[int] = Field(None, description="Maximum number of entries")


class LogEntryBase(BaseModel):
    """Base log entry schema."""

    source: LogSource = Field(..., description="Log source")
    source_id: Optional[str] = Field(None, description="Source ID (container ID, etc.)")
    source_name: Optional[str] = Field(
        None, description="Source name (container name, etc.)"
    )
    level: LogLevel = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(..., description="Log timestamp")
    stream: Optional[LogStream] = Field(None, description="Log stream (for containers)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LogEntryCreate(LogEntryBase):
    """Log entry creation schema."""

    pass


class LogEntry(LogEntryBase):
    """Log entry schema."""

    id: str = Field(..., description="Log entry ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class LogFilter(BaseModel):
    """Log filter schema."""

    source: Optional[List[LogSource]] = Field(None, description="Filter by source")
    source_id: Optional[List[str]] = Field(None, description="Filter by source ID")
    source_name: Optional[List[str]] = Field(None, description="Filter by source name")
    level: Optional[List[LogLevel]] = Field(None, description="Filter by log level")
    message_contains: Optional[str] = Field(
        None, description="Filter by message content"
    )
    message_regex: Optional[str] = Field(None, description="Filter by message regex")
    start_time: Optional[datetime] = Field(None, description="Filter by start time")
    end_time: Optional[datetime] = Field(None, description="Filter by end time")
    stream: Optional[LogStream] = Field(
        None, description="Filter by stream (for containers)"
    )
    limit: Optional[int] = Field(None, description="Limit number of results")
    offset: Optional[int] = Field(None, description="Offset for pagination")


class LogExportFormat(str, Enum):
    """Log export format types."""

    JSON = "json"
    CSV = "csv"
    TEXT = "text"


class LogExportRequest(BaseModel):
    """Log export request schema."""

    filter: LogFilter = Field(..., description="Log filter")
    format: LogExportFormat = Field(..., description="Export format")


class LogStatistics(BaseModel):
    """Log statistics schema."""

    total: int = Field(..., description="Total number of log entries")
    by_level: Dict[LogLevel, int] = Field(..., description="Logs by level")
    by_source: Dict[LogSource, int] = Field(..., description="Logs by source")
    by_stream: Optional[Dict[LogStream, int]] = Field(
        None, description="Logs by stream (for containers)"
    )
    error_rate: float = Field(..., description="Error rate (percentage)")
    warning_rate: float = Field(..., description="Warning rate (percentage)")


class LogAggregationSettings(BaseModel):
    """Log aggregation settings schema."""

    enabled: bool = Field(True, description="Whether log aggregation is enabled")
    collection_interval: int = Field(60, description="Collection interval in seconds")
    retention_policy: LogRetentionPolicy = Field(
        default_factory=lambda: LogRetentionPolicy(
            max_age_days=7, max_size_mb=1000, max_entries=1000000
        ),
        description="Retention policy",
    )
    sources: Dict[LogSource, bool] = Field(
        default_factory=lambda: {
            LogSource.CONTAINER: True,
            LogSource.IMAGE: True,
            LogSource.VOLUME: True,
            LogSource.NETWORK: True,
            LogSource.SYSTEM: True,
        },
        description="Enabled log sources",
    )
