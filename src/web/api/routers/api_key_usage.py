"""
API key usage router for the DockerForge Web UI.

This module provides the API endpoints for API key usage tracking.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.web.api.database import get_db
from src.web.api.schemas.api_key_usage import (
    ApiKeyUsageQuery,
    ApiKeyUsageResponse,
    ApiKeyUsageStats,
)
from src.web.api.services import api_key as api_key_service
from src.web.api.services.auth import check_permission, get_current_active_user

router = APIRouter()


@router.get("/{key_id}/usage", response_model=List[ApiKeyUsageResponse])
async def get_api_key_usage(
    key_id: int,
    start_date: str = None,
    end_date: str = None,
    endpoint: str = None,
    method: str = None,
    status_code: int = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Get API key usage records.

    Args:
        key_id: API key ID
        start_date: Start date for filtering (YYYY-MM-DD)
        end_date: End date for filtering (YYYY-MM-DD)
        endpoint: Filter by endpoint
        method: Filter by HTTP method
        status_code: Filter by status code
        limit: Maximum number of records to return
        offset: Number of records to skip
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of API key usage records
    """
    # Check if the API key belongs to the user
    api_key = api_key_service.get_api_key(db, key_id, current_user.id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    # Create query object
    query = ApiKeyUsageQuery(
        start_date=start_date,
        end_date=end_date,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        limit=limit,
        offset=offset,
    )

    # Get usage records
    usage_records = api_key_service.get_api_key_usage(db, key_id, query)

    return usage_records


@router.get("/{key_id}/stats", response_model=Dict[str, Any])
async def get_api_key_usage_stats(
    key_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Get API key usage statistics.

    Args:
        key_id: API key ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        API key usage statistics
    """
    # Check if the API key belongs to the user
    api_key = api_key_service.get_api_key(db, key_id, current_user.id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    # Get usage statistics
    stats = api_key_service.get_api_key_usage_stats(db, key_id)

    return stats
