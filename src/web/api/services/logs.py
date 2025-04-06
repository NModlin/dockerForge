"""
Log management service for the DockerForge Web UI.

This module provides functionality for managing logs, log aggregation, and log analysis.
"""
import logging
import uuid
import json
import re
import csv
import io
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text

from src.web.api.database import get_db
from src.web.api.models.monitoring import LogEntry
from src.web.api.schemas.logs import (
    LogEntryCreate, LogFilter, LogExportFormat, LogStatistics,
    LogLevel, LogSource, LogStream, LogAggregationSettings
)
from src.monitoring.log_collector import get_log_collection_manager
from src.monitoring.log_explorer import get_log_explorer
from src.config.config_manager import get_config

# Set up logging
logger = logging.getLogger("api.services.logs")


async def get_logs(
    db: Session,
    filter_params: LogFilter = None,
    skip: int = 0,
    limit: int = 100
) -> List[LogEntry]:
    """
    Get logs with optional filtering.
    
    Args:
        db: Database session
        filter_params: Log filter parameters
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of log entries
    """
    query = db.query(LogEntry)
    
    # Apply filters if provided
    if filter_params:
        if filter_params.source:
            query = query.filter(LogEntry.source.in_(filter_params.source))
        
        if filter_params.source_id:
            query = query.filter(LogEntry.source_id.in_(filter_params.source_id))
        
        if filter_params.source_name:
            # Use OR for multiple source names
            source_name_filters = []
            for name in filter_params.source_name:
                source_name_filters.append(LogEntry.source_name == name)
            
            if source_name_filters:
                query = query.filter(or_(*source_name_filters))
        
        if filter_params.level:
            query = query.filter(LogEntry.level.in_(filter_params.level))
        
        if filter_params.message_contains:
            query = query.filter(LogEntry.message.ilike(f"%{filter_params.message_contains}%"))
        
        if filter_params.message_regex:
            # Note: This is database-specific and may not work with all databases
            # For PostgreSQL, use the ~ operator
            query = query.filter(text(f"message ~ '{filter_params.message_regex}'"))
        
        if filter_params.start_time:
            query = query.filter(LogEntry.timestamp >= filter_params.start_time)
        
        if filter_params.end_time:
            query = query.filter(LogEntry.timestamp <= filter_params.end_time)
        
        if filter_params.stream:
            if filter_params.stream == LogStream.BOTH:
                query = query.filter(LogEntry.log_metadata["stream"].astext.in_([LogStream.STDOUT, LogStream.STDERR]))
            else:
                query = query.filter(LogEntry.log_metadata["stream"].astext == filter_params.stream)
    
    # Order by timestamp (newest first)
    query = query.order_by(LogEntry.timestamp.desc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


async def get_container_logs(
    container_id: str,
    tail: int = 100,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    stream: Optional[LogStream] = None,
    follow: bool = False
) -> List[Dict[str, Any]]:
    """
    Get logs for a specific container directly from Docker.
    
    Args:
        container_id: Container ID
        tail: Number of lines to return from the end of the logs
        since: Only return logs since this timestamp
        until: Only return logs before this timestamp
        stream: Stream to filter by (stdout, stderr, or both)
        follow: Whether to follow the logs (stream updates)
        
    Returns:
        List of log entries
    """
    # Get log collection manager
    log_manager = get_log_collection_manager()
    
    # Convert datetime to timestamp
    since_ts = None
    if since:
        since_ts = since.timestamp()
    
    until_ts = None
    if until:
        until_ts = until.timestamp()
    
    # Convert stream to list of streams
    streams = None
    if stream:
        if stream == LogStream.BOTH:
            streams = [LogStream.STDOUT, LogStream.STDERR]
        else:
            streams = [stream]
    
    # Get logs
    logs = log_manager.get_logs(
        container_ids=[container_id],
        since=since_ts,
        until=until_ts,
        streams=streams,
        limit=tail
    )
    
    # Convert to dictionary format
    result = []
    for log in logs:
        result.append({
            "timestamp": log.timestamp.isoformat(),
            "message": log.message,
            "stream": log.stream,
            "container_id": log.container_id,
            "container_name": log.container_name
        })
    
    return result


async def get_multi_container_logs(
    container_ids: List[str],
    tail: int = 100,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    stream: Optional[LogStream] = None,
    message_contains: Optional[str] = None,
    message_regex: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get logs for multiple containers.
    
    Args:
        container_ids: List of container IDs
        tail: Number of lines to return from the end of the logs
        since: Only return logs since this timestamp
        until: Only return logs before this timestamp
        stream: Stream to filter by (stdout, stderr, or both)
        message_contains: Only return logs containing this string
        message_regex: Only return logs matching this regex
        
    Returns:
        List of log entries
    """
    # Get log collection manager
    log_manager = get_log_collection_manager()
    
    # Convert datetime to timestamp
    since_ts = None
    if since:
        since_ts = since.timestamp()
    
    until_ts = None
    if until:
        until_ts = until.timestamp()
    
    # Convert stream to list of streams
    streams = None
    if stream:
        if stream == LogStream.BOTH:
            streams = [LogStream.STDOUT, LogStream.STDERR]
        else:
            streams = [stream]
    
    # Get logs
    logs = log_manager.get_logs(
        container_ids=container_ids,
        since=since_ts,
        until=until_ts,
        streams=streams,
        message_contains=message_contains,
        message_regex=message_regex,
        limit=tail
    )
    
    # Convert to dictionary format
    result = []
    for log in logs:
        result.append({
            "timestamp": log.timestamp.isoformat(),
            "message": log.message,
            "stream": log.stream,
            "container_id": log.container_id,
            "container_name": log.container_name
        })
    
    # Sort by timestamp (newest first)
    result.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Apply limit
    if len(result) > tail:
        result = result[:tail]
    
    return result


async def create_log_entry(db: Session, log_create: LogEntryCreate) -> LogEntry:
    """
    Create a new log entry.
    
    Args:
        db: Database session
        log_create: Log entry creation data
        
    Returns:
        Created log entry
    """
    # Generate ID
    log_id = str(uuid.uuid4())
    
    # Create metadata
    metadata = log_create.metadata or {}
    if log_create.stream:
        metadata["stream"] = log_create.stream
    
    # Create log entry
    log_entry = LogEntry(
        id=log_id,
        source=log_create.source,
        source_id=log_create.source_id,
        source_name=log_create.source_name,
        level=log_create.level,
        message=log_create.message,
        timestamp=log_create.timestamp,
        log_metadata=metadata,
        created_at=datetime.now()
    )
    
    # Add to database
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return log_entry


async def get_log_statistics(
    db: Session,
    filter_params: LogFilter = None,
    days: int = 7
) -> LogStatistics:
    """
    Get log statistics.
    
    Args:
        db: Database session
        filter_params: Log filter parameters
        days: Number of days to include in statistics
        
    Returns:
        Log statistics
    """
    # Calculate start date if not provided in filter
    start_date = None
    if filter_params and filter_params.start_time:
        start_date = filter_params.start_time
    else:
        start_date = datetime.now() - timedelta(days=days)
    
    # Build query
    query = db.query(LogEntry)
    
    # Apply filters
    if filter_params:
        if filter_params.source:
            query = query.filter(LogEntry.source.in_(filter_params.source))
        
        if filter_params.source_id:
            query = query.filter(LogEntry.source_id.in_(filter_params.source_id))
        
        if filter_params.source_name:
            # Use OR for multiple source names
            source_name_filters = []
            for name in filter_params.source_name:
                source_name_filters.append(LogEntry.source_name == name)
            
            if source_name_filters:
                query = query.filter(or_(*source_name_filters))
        
        if filter_params.level:
            query = query.filter(LogEntry.level.in_(filter_params.level))
        
        if filter_params.message_contains:
            query = query.filter(LogEntry.message.ilike(f"%{filter_params.message_contains}%"))
        
        if filter_params.message_regex:
            # Note: This is database-specific and may not work with all databases
            query = query.filter(text(f"message ~ '{filter_params.message_regex}'"))
        
        if filter_params.end_time:
            query = query.filter(LogEntry.timestamp <= filter_params.end_time)
        
        if filter_params.stream:
            if filter_params.stream == LogStream.BOTH:
                query = query.filter(LogEntry.log_metadata["stream"].astext.in_([LogStream.STDOUT, LogStream.STDERR]))
            else:
                query = query.filter(LogEntry.log_metadata["stream"].astext == filter_params.stream)
    
    # Apply start date filter
    query = query.filter(LogEntry.timestamp >= start_date)
    
    # Get total count
    total = query.count()
    
    # Get counts by level
    level_counts = db.query(
        LogEntry.level,
        func.count(LogEntry.id)
    ).filter(
        LogEntry.timestamp >= start_date
    ).group_by(
        LogEntry.level
    ).all()
    
    by_level = {level: 0 for level in LogLevel}
    for level, count in level_counts:
        by_level[level] = count
    
    # Get counts by source
    source_counts = db.query(
        LogEntry.source,
        func.count(LogEntry.id)
    ).filter(
        LogEntry.timestamp >= start_date
    ).group_by(
        LogEntry.source
    ).all()
    
    by_source = {source: 0 for source in LogSource}
    for source, count in source_counts:
        by_source[source] = count
    
    # Get counts by stream (for container logs)
    stream_counts = db.query(
        LogEntry.log_metadata["stream"].astext,
        func.count(LogEntry.id)
    ).filter(
        LogEntry.timestamp >= start_date,
        LogEntry.log_metadata["stream"].astext.in_([LogStream.STDOUT, LogStream.STDERR])
    ).group_by(
        LogEntry.log_metadata["stream"].astext
    ).all()
    
    by_stream = {stream: 0 for stream in [LogStream.STDOUT, LogStream.STDERR]}
    for stream, count in stream_counts:
        if stream:
            by_stream[stream] = count
    
    # Calculate error and warning rates
    error_count = by_level.get(LogLevel.ERROR, 0)
    warning_count = by_level.get(LogLevel.WARNING, 0)
    
    error_rate = 0
    warning_rate = 0
    
    if total > 0:
        error_rate = (error_count / total) * 100
        warning_rate = (warning_count / total) * 100
    
    # Create statistics
    return LogStatistics(
        total=total,
        by_level=by_level,
        by_source=by_source,
        by_stream=by_stream,
        error_rate=error_rate,
        warning_rate=warning_rate
    )


async def export_logs(
    db: Session,
    filter_params: LogFilter,
    format: LogExportFormat
) -> Tuple[str, bytes]:
    """
    Export logs in the specified format.
    
    Args:
        db: Database session
        filter_params: Log filter parameters
        format: Export format
        
    Returns:
        Tuple of (filename, file content)
    """
    # Get logs
    logs = await get_logs(db, filter_params, limit=10000)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs_export_{timestamp}"
    
    # Export based on format
    if format == LogExportFormat.JSON:
        # Convert to JSON
        log_dicts = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "source": log.source,
                "source_id": log.source_id,
                "source_name": log.source_name,
                "level": log.level,
                "message": log.message
            }
            
            # Add stream if available
            if log.log_metadata and "stream" in log.log_metadata:
                log_dict["stream"] = log.log_metadata["stream"]
            
            log_dicts.append(log_dict)
        
        content = json.dumps(log_dicts, indent=2).encode("utf-8")
        filename += ".json"
        return filename, content
    
    elif format == LogExportFormat.CSV:
        # Convert to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Timestamp", "Source", "Source ID", "Source Name", "Level", "Stream", "Message"])
        
        # Write rows
        for log in logs:
            stream = None
            if log.log_metadata and "stream" in log.log_metadata:
                stream = log.log_metadata["stream"]
            
            writer.writerow([
                log.timestamp.isoformat(),
                log.source,
                log.source_id,
                log.source_name,
                log.level,
                stream,
                log.message
            ])
        
        content = output.getvalue().encode("utf-8")
        filename += ".csv"
        return filename, content
    
    else:  # TEXT
        # Convert to plain text
        lines = []
        for log in logs:
            stream = ""
            if log.log_metadata and "stream" in log.log_metadata:
                stream = f" [{log.log_metadata['stream']}]"
            
            source = log.source
            if log.source_name:
                source += f" ({log.source_name})"
            
            lines.append(f"{log.timestamp.isoformat()} {source}{stream} [{log.level.upper()}] {log.message}")
        
        content = "\n".join(lines).encode("utf-8")
        filename += ".txt"
        return filename, content


async def get_log_aggregation_settings() -> LogAggregationSettings:
    """
    Get log aggregation settings.
    
    Returns:
        Log aggregation settings
    """
    # Get settings from config
    enabled = get_config("monitoring.log_aggregation.enabled", True)
    collection_interval = get_config("monitoring.log_aggregation.collection_interval", 60)
    
    # Get retention policy
    max_age_days = get_config("monitoring.log_aggregation.retention.max_age_days", 7)
    max_size_mb = get_config("monitoring.log_aggregation.retention.max_size_mb", 1000)
    max_entries = get_config("monitoring.log_aggregation.retention.max_entries", 1000000)
    
    # Get sources
    sources = {}
    for source in LogSource:
        sources[source] = get_config(f"monitoring.log_aggregation.sources.{source}", True)
    
    # Create settings
    return LogAggregationSettings(
        enabled=enabled,
        collection_interval=collection_interval,
        retention_policy={
            "max_age_days": max_age_days,
            "max_size_mb": max_size_mb,
            "max_entries": max_entries
        },
        sources=sources
    )


async def update_log_aggregation_settings(settings: LogAggregationSettings) -> bool:
    """
    Update log aggregation settings.
    
    Args:
        settings: Log aggregation settings
        
    Returns:
        True if successful
    """
    # Update settings in config
    config = get_config()
    
    # Update enabled
    config["monitoring"]["log_aggregation"]["enabled"] = settings.enabled
    
    # Update collection interval
    config["monitoring"]["log_aggregation"]["collection_interval"] = settings.collection_interval
    
    # Update retention policy
    config["monitoring"]["log_aggregation"]["retention"] = {
        "max_age_days": settings.retention_policy.max_age_days,
        "max_size_mb": settings.retention_policy.max_size_mb,
        "max_entries": settings.retention_policy.max_entries
    }
    
    # Update sources
    config["monitoring"]["log_aggregation"]["sources"] = settings.sources
    
    # Save config
    # TODO: Implement config saving
    
    # Restart log collection if needed
    log_manager = get_log_collection_manager()
    if settings.enabled:
        log_manager.start()
    else:
        log_manager.stop()
    
    return True


async def analyze_logs(
    container_id: str,
    hours: int = 24,
    include_patterns: bool = True
) -> Dict[str, Any]:
    """
    Analyze logs for a container.
    
    Args:
        container_id: Container ID
        hours: Number of hours to analyze
        include_patterns: Whether to include pattern matching
        
    Returns:
        Analysis results
    """
    # Get log explorer
    log_explorer = get_log_explorer()
    
    # Calculate start time
    start_time = datetime.now() - timedelta(hours=hours)
    
    # Get analysis
    analysis = log_explorer.analyze_container_logs(
        container_id,
        start_time=start_time,
        include_patterns=include_patterns
    )
    
    return analysis
