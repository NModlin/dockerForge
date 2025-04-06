"""
User preferences models for the DockerForge Web UI.

This module provides the database models for user preferences.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
import datetime

from .base import Base, BaseModel, TimestampMixin


class UserPreferences(BaseModel, TimestampMixin):
    """
    User preferences model.
    
    This model stores user preferences for the UI and application behavior.
    """
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = Column(String(20), default="light", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    date_format = Column(String(20), default="MM/DD/YYYY", nullable=False)
    time_format = Column(String(10), default="24h", nullable=False)
    notification_preferences = Column(JSON, nullable=True)
    display_preferences = Column(JSON, nullable=True)
    keyboard_preferences = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", backref="preferences")
    
    def __repr__(self):
        return f"<UserPreferences(id={self.id}, user_id={self.user_id})>"
