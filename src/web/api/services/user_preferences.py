"""
User preferences service for the DockerForge Web UI.

This module provides the user preferences services for the DockerForge Web UI.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.web.api.models.user_preferences import UserPreferences
from src.web.api.schemas.user_preferences import (
    UserPreferencesCreate,
    UserPreferencesUpdate,
)


def get_user_preferences(db: Session, user_id: int) -> UserPreferences:
    """
    Get user preferences.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User preferences
    """
    preferences = (
        db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    )

    # Create default preferences if none exist
    if not preferences:
        preferences = UserPreferences(
            user_id=user_id,
            theme="light",
            language="en",
            date_format="MM/DD/YYYY",
            time_format="24h",
            notification_preferences={
                "enabled": True,
                "desktop": True,
                "email": False,
                "emailAddress": None,
                "events": ["error", "security"],
            },
            display_preferences={
                "compactView": False,
                "showSystemContainers": False,
                "refreshInterval": 30,
                "defaultPage": "dashboard",
            },
            keyboard_preferences={"enableShortcuts": True, "customShortcuts": {}},
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


def create_user_preferences(
    db: Session, preferences_data: UserPreferencesCreate, user_id: int
) -> UserPreferences:
    """
    Create user preferences.

    Args:
        db: Database session
        preferences_data: User preferences data
        user_id: User ID

    Returns:
        Created user preferences
    """
    # Check if preferences already exist
    existing = (
        db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User preferences already exist",
        )

    # Create preferences
    preferences = UserPreferences(
        user_id=user_id,
        theme=preferences_data.theme,
        language=preferences_data.language,
        date_format=preferences_data.dateFormat,
        time_format=preferences_data.timeFormat,
        notification_preferences=(
            preferences_data.notifications.dict()
            if preferences_data.notifications
            else None
        ),
        display_preferences=(
            preferences_data.display.dict() if preferences_data.display else None
        ),
        keyboard_preferences=(
            preferences_data.keyboard.dict() if preferences_data.keyboard else None
        ),
    )

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return preferences


def update_user_preferences(
    db: Session, preferences_data: UserPreferencesUpdate, user_id: int
) -> UserPreferences:
    """
    Update user preferences.

    Args:
        db: Database session
        preferences_data: User preferences data to update
        user_id: User ID

    Returns:
        Updated user preferences
    """
    # Get existing preferences or create default
    preferences = get_user_preferences(db, user_id)

    # Update fields if provided
    if preferences_data.theme is not None:
        preferences.theme = preferences_data.theme
    if preferences_data.language is not None:
        preferences.language = preferences_data.language
    if preferences_data.dateFormat is not None:
        preferences.date_format = preferences_data.dateFormat
    if preferences_data.timeFormat is not None:
        preferences.time_format = preferences_data.timeFormat

    # Update notification preferences
    if preferences_data.notifications:
        if not preferences.notification_preferences:
            preferences.notification_preferences = {}

        # Update with new values
        preferences.notification_preferences.update(
            preferences_data.notifications.dict(exclude_unset=True)
        )

    # Update display preferences
    if preferences_data.display:
        if not preferences.display_preferences:
            preferences.display_preferences = {}

        # Update with new values
        preferences.display_preferences.update(
            preferences_data.display.dict(exclude_unset=True)
        )

    # Update keyboard preferences
    if preferences_data.keyboard:
        if not preferences.keyboard_preferences:
            preferences.keyboard_preferences = {}

        # Update with new values
        preferences.keyboard_preferences.update(
            preferences_data.keyboard.dict(exclude_unset=True)
        )

    db.commit()
    db.refresh(preferences)

    return preferences


def reset_user_preferences(db: Session, user_id: int) -> UserPreferences:
    """
    Reset user preferences to defaults.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Reset user preferences
    """
    # Get existing preferences
    preferences = (
        db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
    )

    # If preferences exist, delete them
    if preferences:
        db.delete(preferences)
        db.commit()

    # Create new default preferences
    return get_user_preferences(db, user_id)
