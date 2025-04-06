"""
Log router for the DockerForge Web UI.

This module provides API endpoints for log management.
"""

# Set up logging
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status
from sqlalchemy.orm import Session

from src.web.api.auth import check_permission, get_current_active_user
from src.web.api.database import get_db
from src.web.api.models.user import User
from src.web.api.schemas.logs import (
    LogAggregationSettings,
    LogEntry,
    LogEntryCreate,
    LogExportFormat,
    LogFilter,
    LogLevel,
    LogSource,
    LogStatistics,
    LogStream,
)
from src.web.api.services import logs as logs_service

logger = logging.getLogger("api.routers.logs")

# Create router
router = APIRouter()


@router.get("/", response_model=List[LogEntry])
async def get_logs(
    skip: int = 0,
    limit: int = 100,
    source: Optional[List[str]] = Query(None, description="Filter by source"),
    source_id: Optional[List[str]] = Query(None, description="Filter by source ID"),
    source_name: Optional[List[str]] = Query(None, description="Filter by source name"),
    level: Optional[List[str]] = Query(None, description="Filter by log level"),
    message_contains: Optional[str] = Query(
        None, description="Filter by message content"
    ),
    message_regex: Optional[str] = Query(None, description="Filter by message regex"),
    start_time: Optional[str] = Query(
        None, description="Filter by start time (ISO format)"
    ),
    end_time: Optional[str] = Query(
        None, description="Filter by end time (ISO format)"
    ),
    stream: Optional[str] = Query(
        None, description="Filter by stream (for containers)"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get logs with optional filtering.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Create filter
    filter_params = LogFilter(
        source=source,
        source_id=source_id,
        source_name=source_name,
        level=level,
        message_contains=message_contains,
        message_regex=message_regex,
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None,
        stream=stream,
        limit=limit,
        offset=skip,
    )

    return await logs_service.get_logs(db, filter_params, skip, limit)


@router.get("/containers/{container_id}", response_model=List[Dict[str, Any]])
async def get_container_logs(
    container_id: str = Path(..., description="Container ID"),
    tail: int = Query(
        100, description="Number of lines to return from the end of the logs"
    ),
    since: Optional[str] = Query(
        None, description="Only return logs since this timestamp (ISO format)"
    ),
    until: Optional[str] = Query(
        None, description="Only return logs before this timestamp (ISO format)"
    ),
    stream: Optional[str] = Query(
        None, description="Stream to filter by (stdout, stderr, or both)"
    ),
    follow: bool = Query(
        False, description="Whether to follow the logs (stream updates)"
    ),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get logs for a specific container directly from Docker.
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Convert ISO timestamps to datetime
    since_dt = None
    if since:
        since_dt = datetime.fromisoformat(since)

    until_dt = None
    if until:
        until_dt = datetime.fromisoformat(until)

    return await logs_service.get_container_logs(
        container_id,
        tail=tail,
        since=since_dt,
        until=until_dt,
        stream=stream,
        follow=follow,
    )


@router.get("/multi-container", response_model=List[Dict[str, Any]])
async def get_multi_container_logs(
    container_ids: List[str] = Query(..., description="List of container IDs"),
    tail: int = Query(
        100, description="Number of lines to return from the end of the logs"
    ),
    since: Optional[str] = Query(
        None, description="Only return logs since this timestamp (ISO format)"
    ),
    until: Optional[str] = Query(
        None, description="Only return logs before this timestamp (ISO format)"
    ),
    stream: Optional[str] = Query(
        None, description="Stream to filter by (stdout, stderr, or both)"
    ),
    message_contains: Optional[str] = Query(
        None, description="Only return logs containing this string"
    ),
    message_regex: Optional[str] = Query(
        None, description="Only return logs matching this regex"
    ),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get logs for multiple containers.
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Convert ISO timestamps to datetime
    since_dt = None
    if since:
        since_dt = datetime.fromisoformat(since)

    until_dt = None
    if until:
        until_dt = datetime.fromisoformat(until)

    return await logs_service.get_multi_container_logs(
        container_ids,
        tail=tail,
        since=since_dt,
        until=until_dt,
        stream=stream,
        message_contains=message_contains,
        message_regex=message_regex,
    )


@router.post("/", response_model=LogEntry, status_code=status.HTTP_201_CREATED)
async def create_log_entry(
    log_create: LogEntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new log entry.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        return await logs_service.create_log_entry(db, log_create)
    except Exception as e:
        logger.exception(f"Error creating log entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating log entry: {str(e)}",
        )


@router.get("/statistics", response_model=LogStatistics)
async def get_log_statistics(
    days: int = Query(7, description="Number of days to include in statistics"),
    source: Optional[List[str]] = Query(None, description="Filter by source"),
    source_id: Optional[List[str]] = Query(None, description="Filter by source ID"),
    source_name: Optional[List[str]] = Query(None, description="Filter by source name"),
    level: Optional[List[str]] = Query(None, description="Filter by log level"),
    message_contains: Optional[str] = Query(
        None, description="Filter by message content"
    ),
    message_regex: Optional[str] = Query(None, description="Filter by message regex"),
    stream: Optional[str] = Query(
        None, description="Filter by stream (for containers)"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get log statistics.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    # Create filter
    filter_params = LogFilter(
        source=source,
        source_id=source_id,
        source_name=source_name,
        level=level,
        message_contains=message_contains,
        message_regex=message_regex,
        stream=stream,
    )

    return await logs_service.get_log_statistics(db, filter_params, days)


@router.post("/export")
async def export_logs(
    filter_params: LogFilter,
    format: LogExportFormat = LogExportFormat.JSON,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Export logs in the specified format.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        filename, content = await logs_service.export_logs(db, filter_params, format)

        # Set content type based on format
        content_type = "application/json"
        if format == LogExportFormat.CSV:
            content_type = "text/csv"
        elif format == LogExportFormat.TEXT:
            content_type = "text/plain"

        # Return file as attachment
        return Response(
            content=content,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        logger.exception(f"Error exporting logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting logs: {str(e)}",
        )


@router.get("/settings", response_model=LogAggregationSettings)
async def get_log_aggregation_settings(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get log aggregation settings.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    return await logs_service.get_log_aggregation_settings()


@router.put("/settings", response_model=LogAggregationSettings)
async def update_log_aggregation_settings(
    settings: LogAggregationSettings,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update log aggregation settings.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    success = await logs_service.update_log_aggregation_settings(settings)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update log aggregation settings",
        )

    return settings


@router.get("/analyze/{container_id}", response_model=Dict[str, Any])
async def analyze_logs(
    container_id: str = Path(..., description="Container ID"),
    hours: int = Query(24, description="Number of hours to analyze"),
    include_patterns: bool = Query(
        True, description="Whether to include pattern matching"
    ),
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyze logs for a container.
    """
    # Check permission
    if not check_permission(current_user, "monitoring:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        return await logs_service.analyze_logs(container_id, hours, include_patterns)
    except Exception as e:
        logger.exception(f"Error analyzing logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing logs: {str(e)}",
        )
