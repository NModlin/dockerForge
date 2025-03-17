"""
Preference manager module for DockerForge notifications.

This module provides functionality for managing user notification preferences.
"""

import os
import json
import logging
import threading
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.notifications.notification_manager import NotificationSeverity, NotificationType

# Set up logging
logger = get_logger("preference_manager")


class UserPreferences:
    """User notification preferences."""
    
    def __init__(
        self,
        user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        enabled_channels: Optional[List[str]] = None,
        severity_thresholds: Optional[Dict[str, bool]] = None,
        notification_types: Optional[Dict[str, bool]] = None,
        quiet_hours: Optional[Dict[str, Any]] = None,
        container_filters: Optional[List[str]] = None,
    ):
        """Initialize user preferences.
        
        Args:
            user_id: The user ID
            name: Optional user name
            email: Optional user email
            enabled_channels: Optional list of enabled channels
            severity_thresholds: Optional severity thresholds
            notification_types: Optional notification types
            quiet_hours: Optional quiet hours settings
            container_filters: Optional container filters
        """
        self.user_id = user_id
        self.name = name
        self.email = email
        self.enabled_channels = enabled_channels or []
        self.severity_thresholds = severity_thresholds or {
            "info": False,
            "warning": True,
            "error": True,
            "critical": True,
        }
        self.notification_types = notification_types or {
            "container_exit": True,
            "container_oom": True,
            "high_resource_usage": True,
            "security_issue": True,
            "update_available": True,
            "fix_proposal": True,
            "fix_applied": True,
            "custom": True,
        }
        self.quiet_hours = quiet_hours or {
            "enabled": False,
            "start": "22:00",
            "end": "08:00",
        }
        self.container_filters = container_filters or []
        self.created_at = None
        self.updated_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the preferences to a dictionary.
        
        Returns:
            A dictionary representation of the preferences
        """
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "enabled_channels": self.enabled_channels,
            "severity_thresholds": self.severity_thresholds,
            "notification_types": self.notification_types,
            "quiet_hours": self.quiet_hours,
            "container_filters": self.container_filters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """Create preferences from a dictionary.
        
        Args:
            data: The dictionary to create the preferences from
            
        Returns:
            A new UserPreferences instance
        """
        from datetime import datetime
        
        preferences = cls(
            user_id=data["user_id"],
            name=data.get("name"),
            email=data.get("email"),
            enabled_channels=data.get("enabled_channels", []),
            severity_thresholds=data.get("severity_thresholds", {}),
            notification_types=data.get("notification_types", {}),
            quiet_hours=data.get("quiet_hours", {}),
            container_filters=data.get("container_filters", []),
        )
        
        if data.get("created_at"):
            preferences.created_at = datetime.fromisoformat(data["created_at"])
        
        if data.get("updated_at"):
            preferences.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return preferences
    
    def should_notify(
        self,
        severity: NotificationSeverity,
        notification_type: NotificationType,
        container_id: Optional[str] = None,
    ) -> bool:
        """Check if a notification should be sent to this user.
        
        Args:
            severity: The notification severity
            notification_type: The notification type
            container_id: Optional container ID
            
        Returns:
            True if the notification should be sent, False otherwise
        """
        # Check severity threshold
        if not self.severity_thresholds.get(severity.value, True):
            return False
        
        # Check notification type
        if not self.notification_types.get(notification_type.value, True):
            return False
        
        # Check container filter
        if container_id and self.container_filters:
            if container_id not in self.container_filters:
                return False
        
        return True


class PreferenceManager:
    """Manager for user notification preferences."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Create a new PreferenceManager instance (singleton)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PreferenceManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the preference manager."""
        if self._initialized:
            return
        
        self._initialized = True
        self._preferences = {}
        
        # Load preferences
        self._load_preferences()
        
        logger.info("Preference manager initialized")
    
    def _load_preferences(self) -> None:
        """Load preferences from disk."""
        data_dir = os.path.expanduser(get_config("general.data_dir"))
        prefs_file = os.path.join(data_dir, "notification_preferences.json")
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, "r") as f:
                    data = json.load(f)
                    
                    # Load preferences
                    for user_id, user_data in data.items():
                        self._preferences[user_id] = UserPreferences.from_dict(user_data)
                    
                    logger.info(f"Loaded preferences for {len(self._preferences)} users")
            except Exception as e:
                logger.error(f"Error loading preferences: {str(e)}")
    
    def _save_preferences(self) -> None:
        """Save preferences to disk."""
        data_dir = os.path.expanduser(get_config("general.data_dir"))
        prefs_file = os.path.join(data_dir, "notification_preferences.json")
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        
        try:
            with open(prefs_file, "w") as f:
                data = {
                    user_id: prefs.to_dict() for user_id, prefs in self._preferences.items()
                }
                json.dump(data, f, indent=2)
                
                logger.debug(f"Saved preferences for {len(self._preferences)} users")
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")
    
    def get_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get preferences for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            The user preferences if found, None otherwise
        """
        return self._preferences.get(user_id)
    
    def set_preferences(self, preferences: UserPreferences) -> None:
        """Set preferences for a user.
        
        Args:
            preferences: The user preferences
        """
        from datetime import datetime
        
        # Set timestamps
        if not preferences.created_at:
            preferences.created_at = datetime.now()
        
        preferences.updated_at = datetime.now()
        
        # Save preferences
        self._preferences[preferences.user_id] = preferences
        self._save_preferences()
        
        logger.info(f"Updated preferences for user {preferences.user_id}")
    
    def delete_preferences(self, user_id: str) -> bool:
        """Delete preferences for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if the preferences were deleted, False otherwise
        """
        if user_id in self._preferences:
            del self._preferences[user_id]
            self._save_preferences()
            
            logger.info(f"Deleted preferences for user {user_id}")
            return True
        
        return False
    
    def get_all_users(self) -> List[str]:
        """Get all user IDs.
        
        Returns:
            List of user IDs
        """
        return list(self._preferences.keys())
    
    def get_users_for_notification(
        self,
        severity: NotificationSeverity,
        notification_type: NotificationType,
        container_id: Optional[str] = None,
    ) -> List[str]:
        """Get users who should receive a notification.
        
        Args:
            severity: The notification severity
            notification_type: The notification type
            container_id: Optional container ID
            
        Returns:
            List of user IDs who should receive the notification
        """
        users = []
        
        for user_id, prefs in self._preferences.items():
            if prefs.should_notify(severity, notification_type, container_id):
                users.append(user_id)
        
        return users
    
    def create_default_preferences(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> UserPreferences:
        """Create default preferences for a user.
        
        Args:
            user_id: The user ID
            name: Optional user name
            email: Optional user email
            
        Returns:
            The created user preferences
        """
        # Create default preferences
        preferences = UserPreferences(
            user_id=user_id,
            name=name,
            email=email,
        )
        
        # Save preferences
        self.set_preferences(preferences)
        
        return preferences


def get_preference_manager() -> PreferenceManager:
    """Get the preference manager instance.
    
    Returns:
        The preference manager instance
    """
    return PreferenceManager()
