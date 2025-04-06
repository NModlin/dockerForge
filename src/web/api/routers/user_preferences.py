"""
User preferences router for the DockerForge Web UI.

This module provides the API endpoints for user preferences.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.web.api.database import get_db
from src.web.api.schemas.user_preferences import UserPreferences, UserPreferencesCreate, UserPreferencesUpdate
from src.web.api.services import user_preferences as preferences_service
from src.web.api.services.auth import get_current_active_user

router = APIRouter()


@router.get("", response_model=UserPreferences)
async def get_user_preferences(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get user preferences.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        User preferences
    """
    return preferences_service.get_user_preferences(db, current_user.id)


@router.post("", response_model=UserPreferences, status_code=status.HTTP_201_CREATED)
async def create_user_preferences(
    preferences_data: UserPreferencesCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create user preferences.
    
    Args:
        preferences_data: User preferences data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created user preferences
    """
    return preferences_service.create_user_preferences(db, preferences_data, current_user.id)


@router.put("", response_model=UserPreferences)
async def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update user preferences.
    
    Args:
        preferences_data: User preferences data to update
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated user preferences
    """
    return preferences_service.update_user_preferences(db, preferences_data, current_user.id)


@router.post("/reset", response_model=UserPreferences)
async def reset_user_preferences(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Reset user preferences to defaults.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Reset user preferences
    """
    return preferences_service.reset_user_preferences(db, current_user.id)
