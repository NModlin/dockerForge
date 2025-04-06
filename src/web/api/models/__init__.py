"""
Models package for the DockerForge Web UI.

This module imports all models to make them available from the models package.
"""

from .api_key import ApiKey
from .backup import Backup, BackupItem, RestoreItem, RestoreJob
from .base import Base, BaseModel, TimestampMixin
from .chat import (
    ChatCommandShortcut,
    ChatFeedback,
    ChatMessage,
    ChatSession,
    ConversationMemory,
    UserPreference,
)
from .compose import (
    ComposeFile,
    ComposeProject,
    ComposeService,
    ComposeServiceContainer,
)
from .container import Container, ContainerLog
from .image import Image, SecurityScan, Vulnerability
from .monitoring import (
    Alert,
    AlertRule,
    Dashboard,
    DashboardWidget,
    LogEntry,
    MetricSample,
)
from .network import Network, NetworkConnection
from .user import Permission, Role, User
from .user_preferences import UserPreferences
from .volume import Volume, VolumeMount

# List of all models for easy access
__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "User",
    "Role",
    "Permission",
    "Container",
    "ContainerLog",
    "Image",
    "SecurityScan",
    "Vulnerability",
    "Volume",
    "VolumeMount",
    "Network",
    "NetworkConnection",
    "ComposeProject",
    "ComposeFile",
    "ComposeService",
    "ComposeServiceContainer",
    "Backup",
    "BackupItem",
    "RestoreJob",
    "RestoreItem",
    "MetricSample",
    "Alert",
    "AlertRule",
    "LogEntry",
    "Dashboard",
    "DashboardWidget",
    "ChatMessage",
    "ChatSession",
    "ChatFeedback",
    "UserPreference",
    "ChatCommandShortcut",
    "ConversationMemory",
    "ApiKey",
    "UserPreferences",
]
