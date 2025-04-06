"""
Chat schemas for the DockerForge Web UI.

This module provides the Pydantic schemas for chat functionality,
including feedback, user preferences, and conversation memory.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ContextData(BaseModel):
    """
    Context data for chat messages.
    """

    current_page: Optional[str] = Field(None, description="Current page the user is on")
    current_container_id: Optional[str] = Field(
        None, description="Current container ID"
    )
    current_image_id: Optional[str] = Field(None, description="Current image ID")
    current_volume_id: Optional[str] = Field(None, description="Current volume ID")
    current_network_id: Optional[str] = Field(None, description="Current network ID")

    # Security related context
    vulnerability_id: Optional[str] = Field(None, description="Vulnerability ID")
    vulnerability_severity: Optional[str] = Field(
        None, description="Vulnerability severity level"
    )
    vulnerability_description: Optional[str] = Field(
        None, description="Vulnerability description"
    )
    affected_package: Optional[str] = Field(None, description="Affected package name")
    current_version: Optional[str] = Field(None, description="Current package version")
    fixed_version: Optional[str] = Field(None, description="Fixed package version")
    cve_id: Optional[str] = Field(None, description="CVE ID")
    recommendation_id: Optional[str] = Field(None, description="Recommendation ID")

    # Container troubleshooting context
    container_logs: Optional[str] = Field(
        None, description="Container logs for analysis"
    )
    issue_id: Optional[str] = Field(None, description="Issue ID from issue detector")
    issue_title: Optional[str] = Field(None, description="Issue title")
    issue_description: Optional[str] = Field(None, description="Issue description")
    issue_severity: Optional[str] = Field(None, description="Issue severity level")
    container_status: Optional[str] = Field(None, description="Container status")
    container_health: Optional[str] = Field(None, description="Container health status")
    container_stats: Optional[Dict[str, Any]] = Field(
        None, description="Container statistics"
    )
    exit_code: Optional[int] = Field(None, description="Container exit code if stopped")

    # Workflow related context
    workflow_id: Optional[str] = Field(
        None, description="Active workflow ID for multi-step processes"
    )
    workflow_type: Optional[str] = Field(
        None, description="Type of workflow (security, troubleshooting)"
    )

    additional_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional context data"
    )


class ChatMessageBase(BaseModel):
    """
    Base chat message schema.
    """

    type: str = Field(..., description="Message type (user, ai, system)")
    text: str = Field(..., description="Message text")
    context: Optional[ContextData] = Field(None, description="Message context")


class ChatMessageCreate(ChatMessageBase):
    """
    Schema for creating a new chat message.
    """

    session_id: Optional[int] = Field(
        None,
        description="Chat session ID (if not provided, a new session will be created)",
    )


class ChatMessage(ChatMessageBase):
    """
    Chat message schema for responses.
    """

    id: int = Field(..., description="Message ID")
    user_id: Optional[int] = Field(None, description="User ID")
    session_id: int = Field(..., description="Chat session ID")
    timestamp: datetime = Field(..., description="Message timestamp")

    model_config = {"from_attributes": True}


class ChatSessionBase(BaseModel):
    """
    Base chat session schema.
    """

    title: Optional[str] = Field(None, description="Session title")
    is_active: bool = Field(True, description="Is the session active")


class ChatSessionCreate(ChatSessionBase):
    """
    Schema for creating a new chat session.
    """

    pass


class ChatSessionUpdate(BaseModel):
    """
    Schema for updating a chat session.
    """

    title: Optional[str] = Field(None, description="Session title")
    is_active: Optional[bool] = Field(None, description="Is the session active")


class ChatSession(ChatSessionBase):
    """
    Chat session schema for responses.
    """

    id: int = Field(..., description="Session ID")
    user_id: Optional[int] = Field(None, description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    messages: List[ChatMessage] = Field([], description="Session messages")

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """
    AI response schema.
    """

    message: ChatMessage = Field(..., description="AI response message")
    session_id: int = Field(..., description="Chat session ID")
    suggestions: Optional[List[str]] = Field(
        None, description="Suggested user responses"
    )


class SessionsList(BaseModel):
    """
    List of chat sessions.
    """

    sessions: List[ChatSession] = Field(..., description="List of chat sessions")
    total: int = Field(..., description="Total number of sessions")


class MessagesList(BaseModel):
    """
    List of chat messages.
    """

    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    total: int = Field(..., description="Total number of messages")


# Feedback schemas
class ChatFeedbackBase(BaseModel):
    """
    Base schema for chat feedback.
    """

    rating: int = Field(..., description="Rating from 1-5", ge=1, le=5)
    feedback_text: Optional[str] = Field(None, description="Optional detailed feedback")


class ChatFeedbackCreate(ChatFeedbackBase):
    """
    Schema for creating chat feedback.
    """

    message_id: int = Field(..., description="ID of the message being rated")


class ChatFeedback(ChatFeedbackBase):
    """
    Schema for chat feedback responses.
    """

    id: int = Field(..., description="Feedback ID")
    message_id: int = Field(..., description="Message ID")
    user_id: Optional[int] = Field(None, description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


# User preference schemas
class UserPreferenceBase(BaseModel):
    """
    Base schema for user preferences.
    """

    response_style: Literal["technical", "simple", "balanced"] = Field(
        "balanced", description="Preferred response style"
    )
    auto_suggestions: bool = Field(True, description="Whether to show auto-suggestions")
    preferred_topics: Optional[List[str]] = Field(
        None, description="Topics the user frequently discusses"
    )
    avoided_topics: Optional[List[str]] = Field(
        None, description="Topics the user prefers to avoid"
    )


class UserPreferenceCreate(UserPreferenceBase):
    """
    Schema for creating user preferences.
    """

    pass


class UserPreferenceUpdate(BaseModel):
    """
    Schema for updating user preferences.
    """

    response_style: Optional[Literal["technical", "simple", "balanced"]] = Field(
        None, description="Preferred response style"
    )
    auto_suggestions: Optional[bool] = Field(
        None, description="Whether to show auto-suggestions"
    )
    preferred_topics: Optional[List[str]] = Field(
        None, description="Topics the user frequently discusses"
    )
    avoided_topics: Optional[List[str]] = Field(
        None, description="Topics the user prefers to avoid"
    )


class UserPreference(UserPreferenceBase):
    """
    Schema for user preference responses.
    """

    id: int = Field(..., description="Preference ID")
    user_id: int = Field(..., description="User ID")
    feedback_preferences: Optional[Dict[str, Any]] = Field(
        None, description="Feedback patterns stored for reference"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


# Command shortcut schemas
class ChatCommandShortcutBase(BaseModel):
    """
    Base schema for command shortcuts.
    """

    command: str = Field(
        ..., description="Shortcut command (e.g., /logs)", min_length=2, max_length=50
    )
    description: str = Field(
        ..., description="Description of what the command does", max_length=255
    )
    template: str = Field(..., description="Command template with placeholders")


class ChatCommandShortcutCreate(ChatCommandShortcutBase):
    """
    Schema for creating command shortcuts.
    """

    pass


class ChatCommandShortcutUpdate(BaseModel):
    """
    Schema for updating command shortcuts.
    """

    description: Optional[str] = Field(
        None, description="Description of what the command does", max_length=255
    )
    template: Optional[str] = Field(
        None, description="Command template with placeholders"
    )


class ChatCommandShortcut(ChatCommandShortcutBase):
    """
    Schema for command shortcut responses.
    """

    id: int = Field(..., description="Shortcut ID")
    user_id: int = Field(..., description="User ID")
    usage_count: int = Field(
        ..., description="Number of times this shortcut has been used"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


# Command shortcuts list schema
class CommandShortcutsList(BaseModel):
    """
    List of command shortcuts.
    """

    shortcuts: List[ChatCommandShortcut] = Field(
        ..., description="List of command shortcuts"
    )
    total: int = Field(..., description="Total number of shortcuts")


# Enhanced chat response schema to include feedback options
class EnhancedChatResponse(ChatResponse):
    """
    Enhanced AI response schema with feedback options.
    """

    feedback_id: Optional[int] = Field(
        None, description="ID of feedback if already provided"
    )
    command_shortcuts: Optional[List[ChatCommandShortcut]] = Field(
        None, description="Available command shortcuts"
    )
    user_preferences: Optional[UserPreference] = Field(
        None, description="User preferences"
    )
