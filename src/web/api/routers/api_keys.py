"""
API key router for the DockerForge Web UI.

This module provides API endpoints for managing API keys.
"""

import datetime
import json

# Set up logging
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from src.config.config_manager import ConfigManager
from src.settings.api_key_manager import ApiKeyManager
from src.web.api.auth import check_permission, get_current_active_user
from src.web.api.database import get_db
from src.web.api.models.api_key import ApiKey
from src.web.api.models.api_key_usage import ApiKeyUsage, ApiKeyUsageSummary
from src.web.api.models.user import User
from src.web.api.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyDetail,
    ApiKeyList,
    ApiKeyResponse,
    ApiKeyUsageRecord,
    ApiKeyUsageResponse,
    ApiKeyUsageStats,
)

logger = logging.getLogger("api.routers.api_keys")

# Create router
router = APIRouter()

# Initialize config manager
config_manager = ConfigManager()

# Initialize API key manager
api_key_manager = ApiKeyManager(config_manager)


@router.get("/", response_model=ApiKeyList)
async def get_api_keys(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get all API keys for the current user.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Get API keys for the current user
        api_keys = (
            db.query(ApiKey)
            .filter(ApiKey.user_id == current_user.id, ApiKey.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

        # Convert to response format
        result = []
        for key in api_keys:
            result.append(
                {
                    "id": key.id,
                    "name": key.name,
                    "key_preview": key.key_prefix,
                    "created_at": key.created_at,
                    "expires_at": key.expires_at,
                    "last_used": key.last_used_at,
                    "is_read_only": key.is_read_only,
                    "scopes": key.scopes,
                }
            )

        return {"items": result, "total": len(result)}
    except Exception as e:
        logger.exception(f"Error getting API keys: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting API keys: {str(e)}",
        )


@router.post("/", response_model=ApiKeyResponse)
async def create_api_key(
    api_key: ApiKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new API key.
    """
    # Check permission
    if not check_permission(current_user, "settings:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Generate a new API key
        full_key, key_prefix, key_hash = ApiKey.generate_key()

        # Calculate expiration date
        expires_at = None
        if api_key.expiration == "30d":
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        elif api_key.expiration == "90d":
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        elif api_key.expiration == "1y":
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=365)

        # Create new API key
        new_key = ApiKey(
            name=api_key.name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            user_id=current_user.id,
            expires_at=expires_at,
            is_active=True,
            is_read_only=api_key.is_read_only,
            scopes=api_key.scopes if not api_key.is_read_only else [],
        )

        db.add(new_key)
        db.commit()
        db.refresh(new_key)

        # Return the full key (this is the only time it will be shown)
        return {
            "id": new_key.id,
            "name": new_key.name,
            "key": full_key,
            "expires_at": new_key.expires_at,
            "is_read_only": new_key.is_read_only,
            "scopes": new_key.scopes,
        }
    except Exception as e:
        logger.exception(f"Error creating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating API key: {str(e)}",
        )


@router.get("/{key_id}", response_model=ApiKeyDetail)
async def get_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get details for a specific API key.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Get API key
        api_key = (
            db.query(ApiKey)
            .filter(
                ApiKey.id == key_id,
                ApiKey.user_id == current_user.id,
                ApiKey.is_active == True,
            )
            .first()
        )

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        # Return key details
        return {
            "id": api_key.id,
            "name": api_key.name,
            "key_preview": api_key.key_prefix,
            "created_at": api_key.created_at,
            "expires_at": api_key.expires_at,
            "last_used": api_key.last_used_at,
            "is_read_only": api_key.is_read_only,
            "scopes": api_key.scopes,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting API key: {str(e)}",
        )


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Revoke an API key.
    """
    # Check permission
    if not check_permission(current_user, "settings:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Get API key
        api_key = (
            db.query(ApiKey)
            .filter(
                ApiKey.id == key_id,
                ApiKey.user_id == current_user.id,
                ApiKey.is_active == True,
            )
            .first()
        )

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        # Revoke the key
        api_key.is_active = False
        db.commit()

        return {"message": "API key revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error revoking API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error revoking API key: {str(e)}",
        )


@router.get("/{key_id}/usage", response_model=ApiKeyUsageResponse)
async def get_api_key_usage(
    key_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get usage records for a specific API key.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Check if the API key exists and belongs to the user
        api_key = (
            db.query(ApiKey)
            .filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id)
            .first()
        )

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        # Get usage records
        usage_records = (
            db.query(ApiKeyUsage)
            .filter(ApiKeyUsage.api_key_id == key_id)
            .order_by(ApiKeyUsage.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        # Count total records
        total_records = (
            db.query(ApiKeyUsage).filter(ApiKeyUsage.api_key_id == key_id).count()
        )

        # Convert to response format
        result = []
        for record in usage_records:
            result.append(
                {
                    "id": record.id,
                    "endpoint": record.endpoint,
                    "method": record.method,
                    "status_code": record.status_code,
                    "response_time": record.response_time,
                    "created_at": record.created_at,
                }
            )

        return {"items": result, "total": total_records}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting API key usage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting API key usage: {str(e)}",
        )


@router.get("/{key_id}/stats", response_model=ApiKeyUsageStats)
async def get_api_key_stats(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get usage statistics for a specific API key.
    """
    # Check permission
    if not check_permission(current_user, "settings:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    try:
        # Check if the API key exists and belongs to the user
        api_key = (
            db.query(ApiKey)
            .filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id)
            .first()
        )

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
            )

        # Get usage statistics
        stats = api_key_manager.get_key_usage_stats(key_id, db)

        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting API key statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting API key statistics: {str(e)}",
        )


# Middleware for tracking API key usage
@router.middleware("http")
async def track_api_key_usage(request: Request, call_next):
    """
    Middleware to track API key usage.
    """
    # Skip tracking for API key endpoints
    if request.url.path.startswith("/api/settings/api-keys"):
        return await call_next(request)

    # Check if request has an API key
    api_key = None
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        api_key_value = auth_header.replace("Bearer ", "")

        # Get database session
        db = next(get_db())

        # Find API key in database
        api_keys = db.query(ApiKey).filter(ApiKey.is_active == True).all()

        for key in api_keys:
            if ApiKey.verify_key(api_key_value, key.key_hash):
                api_key = key
                break

    # If no API key found, just continue
    if not api_key:
        return await call_next(request)

    # Track API key usage
    start_time = time.time()

    # Call next middleware/route handler
    response = await call_next(request)

    # Calculate response time
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Record usage
    try:
        # Get database session
        db = next(get_db())

        # Update last used timestamp
        api_key.last_used_at = datetime.datetime.utcnow()
        db.commit()

        # Create usage record
        usage = ApiKeyUsage(
            api_key_id=api_key.id,
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            response_time=response_time,
            request_size=int(request.headers.get("content-length", 0)),
            response_size=int(response.headers.get("content-length", 0)),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        db.add(usage)
        db.commit()
    except Exception as e:
        logger.error(f"Error tracking API key usage: {str(e)}")

    return response
