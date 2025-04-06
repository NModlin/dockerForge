"""
API key service for the DockerForge Web UI.

This module provides the API key services for the DockerForge Web UI.
"""

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from src.web.api.models.api_key import ApiKey
from src.web.api.models.api_key_usage import ApiKeyUsage, ApiKeyUsageSummary
from src.web.api.models.user import User
from src.web.api.schemas.api_key import ApiKeyCreate, ApiKeyUpdate
from src.web.api.schemas.api_key_usage import ApiKeyUsageCreate, ApiKeyUsageQuery


def get_api_keys(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[ApiKey]:
    """
    Get all API keys for a user.

    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of API keys
    """
    return (
        db.query(ApiKey)
        .filter(ApiKey.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_api_key(db: Session, key_id: int, user_id: int) -> Optional[ApiKey]:
    """
    Get an API key by ID.

    Args:
        db: Database session
        key_id: API key ID
        user_id: User ID

    Returns:
        API key if found, None otherwise
    """
    return (
        db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == user_id).first()
    )


def create_api_key(
    db: Session, key_data: ApiKeyCreate, user_id: int
) -> Tuple[ApiKey, str]:
    """
    Create a new API key.

    Args:
        db: Database session
        key_data: API key data
        user_id: User ID

    Returns:
        Tuple of (created API key, full API key)
    """
    # Generate a new API key
    full_key, key_prefix, key_hash = ApiKey.generate_key()

    # Calculate expiration date if provided
    expires_at = None
    if key_data.expiration and key_data.expiration != "never":
        if key_data.expiration.endswith("d"):
            days = int(key_data.expiration[:-1])
            expires_at = datetime.utcnow() + timedelta(days=days)
        elif key_data.expiration.endswith("y"):
            years = int(key_data.expiration[:-1])
            expires_at = datetime.utcnow() + timedelta(days=365 * years)

    # Create the API key
    api_key = ApiKey(
        name=key_data.name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        user_id=user_id,
        expires_at=expires_at,
        is_read_only=key_data.is_read_only,
        scopes=key_data.scopes,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return api_key, full_key


def update_api_key(
    db: Session, key_id: int, key_data: ApiKeyUpdate, user_id: int
) -> ApiKey:
    """
    Update an API key.

    Args:
        db: Database session
        key_id: API key ID
        key_data: API key data to update
        user_id: User ID

    Returns:
        Updated API key
    """
    api_key = get_api_key(db, key_id, user_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    # Update fields if provided
    if key_data.name is not None:
        api_key.name = key_data.name
    if key_data.is_active is not None:
        api_key.is_active = key_data.is_active
    if key_data.is_read_only is not None:
        api_key.is_read_only = key_data.is_read_only
    if key_data.scopes is not None:
        api_key.scopes = key_data.scopes

    db.commit()
    db.refresh(api_key)

    return api_key


def delete_api_key(db: Session, key_id: int, user_id: int) -> bool:
    """
    Delete an API key.

    Args:
        db: Database session
        key_id: API key ID
        user_id: User ID

    Returns:
        True if the key was deleted, False otherwise
    """
    api_key = get_api_key(db, key_id, user_id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    db.delete(api_key)
    db.commit()

    return True


def verify_api_key(db: Session, api_key: str) -> Optional[ApiKey]:
    """
    Verify an API key and return the associated API key object.

    Args:
        db: Database session
        api_key: API key to verify

    Returns:
        API key object if valid, None otherwise
    """
    # Extract the prefix for lookup
    if not api_key or len(api_key) < 8:
        return None

    key_prefix = api_key[:8]

    # Find API keys with matching prefix
    api_keys = (
        db.query(ApiKey)
        .filter(ApiKey.key_prefix == key_prefix, ApiKey.is_active == True)
        .all()
    )

    # Check each key
    for key in api_keys:
        if ApiKey.verify_key(api_key, key.key_hash):
            # Update last used timestamp
            key.last_used_at = datetime.utcnow()
            db.commit()

            # Check if the key has expired
            if key.expires_at and key.expires_at < datetime.utcnow():
                key.is_active = False
                db.commit()
                return None

            return key

    return None


def has_permission(api_key: ApiKey, required_scope: str) -> bool:
    """
    Check if an API key has a specific permission.

    Args:
        api_key: API key to check
        required_scope: Required permission scope

    Returns:
        True if the API key has the required permission, False otherwise
    """
    # Read-only keys can only perform read operations
    if api_key.is_read_only and required_scope.endswith(":write"):
        return False

    # If no scopes are defined, the key has full access
    if not api_key.scopes:
        return True

    # Check if the required scope is in the key's scopes
    return required_scope in api_key.scopes


def record_api_key_usage(
    db: Session,
    api_key_id: int,
    endpoint: str,
    method: str,
    status_code: int,
    response_time: float,
    request_size: Optional[int] = None,
    response_size: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> ApiKeyUsage:
    """
    Record API key usage.

    Args:
        db: Database session
        api_key_id: API key ID
        endpoint: API endpoint that was accessed
        method: HTTP method (GET, POST, etc.)
        status_code: HTTP status code
        response_time: Response time in milliseconds
        request_size: Size of the request in bytes
        response_size: Size of the response in bytes
        ip_address: IP address of the client
        user_agent: User agent of the client

    Returns:
        Created API key usage record
    """
    # Create usage record
    usage = ApiKeyUsage(
        api_key_id=api_key_id,
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        response_time=response_time,
        request_size=request_size,
        response_size=response_size,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(usage)

    # Update or create daily summary
    today = datetime.now().date()
    summary = (
        db.query(ApiKeyUsageSummary)
        .filter(
            ApiKeyUsageSummary.api_key_id == api_key_id,
            func.date(ApiKeyUsageSummary.date) == today,
        )
        .first()
    )

    if not summary:
        # Create new summary
        endpoints = {endpoint: 1}
        summary = ApiKeyUsageSummary(
            api_key_id=api_key_id,
            date=today,
            total_requests=1,
            successful_requests=1 if 200 <= status_code < 400 else 0,
            failed_requests=1 if status_code >= 400 else 0,
            avg_response_time=response_time,
            total_request_size=request_size or 0,
            total_response_size=response_size or 0,
            endpoints=endpoints,
        )
        db.add(summary)
    else:
        # Update existing summary
        summary.total_requests += 1
        if 200 <= status_code < 400:
            summary.successful_requests += 1
        else:
            summary.failed_requests += 1

        # Update average response time
        total_time = summary.avg_response_time * (summary.total_requests - 1)
        summary.avg_response_time = (
            total_time + response_time
        ) / summary.total_requests

        # Update request and response sizes
        if request_size:
            summary.total_request_size += request_size
        if response_size:
            summary.total_response_size += response_size

        # Update endpoints
        endpoints = summary.endpoints or {}
        endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
        summary.endpoints = endpoints

    db.commit()
    db.refresh(usage)

    return usage


def get_api_key_usage(
    db: Session, api_key_id: int, query: ApiKeyUsageQuery
) -> List[ApiKeyUsage]:
    """
    Get API key usage records.

    Args:
        db: Database session
        api_key_id: API key ID
        query: Query parameters

    Returns:
        List of API key usage records
    """
    # Start with base query
    db_query = db.query(ApiKeyUsage).filter(ApiKeyUsage.api_key_id == api_key_id)

    # Apply filters
    if query.start_date:
        db_query = db_query.filter(
            func.date(ApiKeyUsage.created_at) >= query.start_date
        )
    if query.end_date:
        db_query = db_query.filter(func.date(ApiKeyUsage.created_at) <= query.end_date)
    if query.endpoint:
        db_query = db_query.filter(ApiKeyUsage.endpoint == query.endpoint)
    if query.method:
        db_query = db_query.filter(ApiKeyUsage.method == query.method)
    if query.status_code:
        db_query = db_query.filter(ApiKeyUsage.status_code == query.status_code)

    # Apply pagination
    db_query = (
        db_query.order_by(desc(ApiKeyUsage.created_at))
        .offset(query.offset)
        .limit(query.limit)
    )

    return db_query.all()


def get_api_key_usage_stats(db: Session, api_key_id: int) -> Dict[str, Any]:
    """
    Get API key usage statistics.

    Args:
        db: Database session
        api_key_id: API key ID

    Returns:
        Dictionary of usage statistics
    """
    # Get total requests
    total_requests = (
        db.query(func.count(ApiKeyUsage.id))
        .filter(ApiKeyUsage.api_key_id == api_key_id)
        .scalar()
        or 0
    )

    # Get today's requests
    today = datetime.now().date()
    requests_today = (
        db.query(func.count(ApiKeyUsage.id))
        .filter(
            ApiKeyUsage.api_key_id == api_key_id,
            func.date(ApiKeyUsage.created_at) == today,
        )
        .scalar()
        or 0
    )

    # Get this week's requests
    week_start = today - timedelta(days=today.weekday())
    requests_this_week = (
        db.query(func.count(ApiKeyUsage.id))
        .filter(
            ApiKeyUsage.api_key_id == api_key_id,
            func.date(ApiKeyUsage.created_at) >= week_start,
        )
        .scalar()
        or 0
    )

    # Get this month's requests
    month_start = date(today.year, today.month, 1)
    requests_this_month = (
        db.query(func.count(ApiKeyUsage.id))
        .filter(
            ApiKeyUsage.api_key_id == api_key_id,
            func.date(ApiKeyUsage.created_at) >= month_start,
        )
        .scalar()
        or 0
    )

    # Get average response time
    avg_response_time = (
        db.query(func.avg(ApiKeyUsage.response_time))
        .filter(ApiKeyUsage.api_key_id == api_key_id)
        .scalar()
        or 0
    )

    # Get success rate
    successful_requests = (
        db.query(func.count(ApiKeyUsage.id))
        .filter(
            ApiKeyUsage.api_key_id == api_key_id,
            ApiKeyUsage.status_code >= 200,
            ApiKeyUsage.status_code < 400,
        )
        .scalar()
        or 0
    )

    success_rate = (
        (successful_requests / total_requests * 100) if total_requests > 0 else 0
    )

    # Get top endpoints
    top_endpoints_query = (
        db.query(ApiKeyUsage.endpoint, func.count(ApiKeyUsage.id).label("count"))
        .filter(ApiKeyUsage.api_key_id == api_key_id)
        .group_by(ApiKeyUsage.endpoint)
        .order_by(desc("count"))
        .limit(5)
    )

    top_endpoints = [
        {"endpoint": endpoint, "count": count}
        for endpoint, count in top_endpoints_query
    ]

    # Get usage over time (daily)
    usage_over_time_query = (
        db.query(
            func.date(ApiKeyUsage.created_at).label("date"),
            func.count(ApiKeyUsage.id).label("count"),
        )
        .filter(ApiKeyUsage.api_key_id == api_key_id)
        .group_by("date")
        .order_by("date")
        .limit(30)
    )

    usage_over_time = [
        {"date": date.isoformat(), "count": count}
        for date, count in usage_over_time_query
    ]

    return {
        "total_requests": total_requests,
        "requests_today": requests_today,
        "requests_this_week": requests_this_week,
        "requests_this_month": requests_this_month,
        "avg_response_time": round(avg_response_time, 2),
        "success_rate": round(success_rate, 2),
        "top_endpoints": top_endpoints,
        "usage_over_time": usage_over_time,
    }
