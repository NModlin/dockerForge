"""
Chat models for the DockerForge Web UI.

This module provides the database models for chat messages, sessions, feedback,
user preferences, and conversation memory.
"""

import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base
from .user import User


class ChatMessage(Base):
    """
    Chat message model.

    This model represents a chat message sent by a user or the AI assistant.
    """

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    session_id = Column(
        Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(String(20), nullable=False)  # 'user', 'ai', 'system'
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    context = Column(
        JSON, nullable=True
    )  # Store context information (page, container ID, etc.)

    # Relationships
    user = relationship("User", back_populates="chat_messages")
    session = relationship("ChatSession", back_populates="messages")


class ChatSession(Base):
    """
    Chat session model.

    This model represents a chat session between a user and the AI assistant.
    """

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=True)  # Auto-generated title or user-defined
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )


# Update User model relationships
User.chat_messages = relationship(
    "ChatMessage", back_populates="user", cascade="all, delete-orphan"
)
User.chat_sessions = relationship(
    "ChatSession", back_populates="user", cascade="all, delete-orphan"
)


class ChatFeedback(Base):
    """
    Chat feedback model.

    This model represents user feedback on AI responses for improvement.
    """

    __tablename__ = "chat_feedback"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(
        Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5 star rating
    feedback_text = Column(Text, nullable=True)  # Optional detailed feedback
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    message = relationship("ChatMessage", backref="feedback")
    user = relationship("User", backref="message_feedback")


class UserPreference(Base):
    """
    User chat preferences model.

    This model stores user preferences for the chat experience.
    """

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    response_style = Column(
        String(20), default="balanced", nullable=False
    )  # 'technical', 'simple', 'balanced'
    auto_suggestions = Column(Boolean, default=True, nullable=False)
    preferred_topics = Column(
        JSON, nullable=True
    )  # List of topics the user frequently discusses
    avoided_topics = Column(JSON, nullable=True)  # Topics the user prefers to avoid
    feedback_preferences = Column(
        JSON, nullable=True
    )  # Feedback patterns stored for reference
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="chat_preferences")


class ChatCommandShortcut(Base):
    """
    Custom command shortcuts for frequent actions.

    This model stores user-defined shortcut commands for common chat operations.
    """

    __tablename__ = "chat_command_shortcuts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    command = Column(String(50), nullable=False)  # Short command (e.g., '/logs')
    description = Column(
        String(255), nullable=False
    )  # Description of what the command does
    template = Column(Text, nullable=False)  # Command template with placeholders
    usage_count = Column(Integer, default=0, nullable=False)  # Track usage frequency
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    # Relationships
    user = relationship("User", backref="command_shortcuts")

    # Ensure command uniqueness per user
    __table_args__ = (
        # Unique constraint for command per user
        # This prevents duplicate commands for the same user
        {"sqlite_autoincrement": True},
    )


class ConversationMemory(Base):
    """
    Conversation memory for maintaining context across chat sessions.

    This model stores embeddings and key information from past conversations
    to provide better context-aware responses.
    """

    __tablename__ = "conversation_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_id = Column(
        Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True
    )
    message_id = Column(
        Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=True
    )
    embedding = Column(JSON, nullable=True)  # Vector embedding of the message content
    key_information = Column(
        JSON, nullable=True
    )  # Extracted key information from the message
    importance_score = Column(
        Float, default=1.0, nullable=False
    )  # Higher score for more important information
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="conversation_memories")
    session = relationship("ChatSession", backref="memories")
    message = relationship("ChatMessage", backref="memory_entry")


# Add relationship to ChatMessage for feedback
ChatMessage.feedback_entries = relationship(
    "ChatFeedback", back_populates="message", cascade="all, delete-orphan"
)
