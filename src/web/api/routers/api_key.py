"""
API key router for the DockerForge Web UI.

This module provides the API endpoints for API key management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.web.api.database import get_db
from src.web.api.schemas.api_key import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse, ApiKeyUpdate
from src.web.api.services import api_key as api_key_service
from src.web.api.services.auth import get_current_active_user, check_permission

router = APIRouter()


@router.get("", response_model=List[ApiKeyResponse])
async def get_api_keys(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get all API keys for the current user.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of API keys
    """
    return api_key_service.get_api_keys(db, current_user.id, skip, limit)


@router.post("", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create a new API key.
    
    Args:
        key_data: API key data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created API key with the full key (only returned once)
    """
    # Check if the user has permission to create API keys
    if not check_permission(current_user, "api:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    api_key, full_key = api_key_service.create_api_key(db, key_data, current_user.id)
    
    # Create response with the full key
    response = ApiKeyCreatedResponse.from_orm(api_key)
    response.key = full_key
    
    return response


@router.get("/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get an API key by ID.
    
    Args:
        key_id: API key ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        API key
    """
    api_key = api_key_service.get_api_key(db, key_id, current_user.id)
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return api_key


@router.put("/{key_id}", response_model=ApiKeyResponse)
async def update_api_key(
    key_id: int,
    key_data: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update an API key.
    
    Args:
        key_id: API key ID
        key_data: API key data to update
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated API key
    """
    # Check if the user has permission to update API keys
    if not check_permission(current_user, "api:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return api_key_service.update_api_key(db, key_id, key_data, current_user.id)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Delete an API key.
    
    Args:
        key_id: API key ID
        db: Database session
        current_user: Current authenticated user
    """
    # Check if the user has permission to delete API keys
    if not check_permission(current_user, "api:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    api_key_service.delete_api_key(db, key_id, current_user.id)
