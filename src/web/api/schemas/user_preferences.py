"""
User preferences schemas for the DockerForge Web UI.

This module provides the Pydantic schemas for user preferences.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class NotificationPreferences(BaseModel):
    """
    Schema for notification preferences.
    """
    enabled: bool = Field(True, description="Whether notifications are enabled")
    desktop: bool = Field(True, description="Whether desktop notifications are enabled")
    email: bool = Field(False, description="Whether email notifications are enabled")
    emailAddress: Optional[str] = Field(None, description="Email address for notifications")
    events: List[str] = Field(default_factory=lambda: ["error", "security"], description="Events to notify")


class DisplayPreferences(BaseModel):
    """
    Schema for display preferences.
    """
    compactView: bool = Field(False, description="Whether to use compact view")
    showSystemContainers: bool = Field(False, description="Whether to show system containers")
    refreshInterval: int = Field(30, description="Auto-refresh interval in seconds")
    defaultPage: str = Field("dashboard", description="Default page to show")


class KeyboardPreferences(BaseModel):
    """
    Schema for keyboard preferences.
    """
    enableShortcuts: bool = Field(True, description="Whether keyboard shortcuts are enabled")
    customShortcuts: Dict[str, str] = Field(default_factory=dict, description="Custom keyboard shortcuts")


class UserPreferencesBase(BaseModel):
    """
    Base schema for user preferences.
    """
    theme: str = Field("light", description="UI theme")
    language: str = Field("en", description="Language")
    dateFormat: str = Field("MM/DD/YYYY", description="Date format")
    timeFormat: str = Field("24h", description="Time format")
    notifications: Optional[NotificationPreferences] = Field(None, description="Notification preferences")
    display: Optional[DisplayPreferences] = Field(None, description="Display preferences")
    keyboard: Optional[KeyboardPreferences] = Field(None, description="Keyboard preferences")


class UserPreferencesCreate(UserPreferencesBase):
    """
    Schema for creating user preferences.
    """
    pass


class UserPreferencesUpdate(BaseModel):
    """
    Schema for updating user preferences.
    """
    theme: Optional[str] = Field(None, description="UI theme")
    language: Optional[str] = Field(None, description="Language")
    dateFormat: Optional[str] = Field(None, description="Date format")
    timeFormat: Optional[str] = Field(None, description="Time format")
    notifications: Optional[NotificationPreferences] = Field(None, description="Notification preferences")
    display: Optional[DisplayPreferences] = Field(None, description="Display preferences")
    keyboard: Optional[KeyboardPreferences] = Field(None, description="Keyboard preferences")


class UserPreferences(UserPreferencesBase):
    """
    Schema for user preferences responses.
    """
    id: int = Field(..., description="Preference ID")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        orm_mode = True
