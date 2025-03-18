"""
Models package for the DockerForge Web UI.

This module imports all models to make them available from the models package.
"""
from .base import Base, BaseModel, TimestampMixin
from .user import User, Role, Permission
from .container import Container, ContainerLog
from .image import Image, SecurityScan, Vulnerability
from .volume import Volume, VolumeMount
from .network import Network, NetworkConnection
from .compose import ComposeProject, ComposeFile, ComposeService, ComposeServiceContainer
from .backup import Backup, BackupItem, RestoreJob, RestoreItem
from .monitoring import (
    MetricSample, Alert, AlertRule, LogEntry, 
    Dashboard, DashboardWidget
)
from .chat import ChatMessage, ChatSession

# List of all models for easy access
__all__ = [
    'Base', 'BaseModel', 'TimestampMixin',
    'User', 'Role', 'Permission',
    'Container', 'ContainerLog',
    'Image', 'SecurityScan', 'Vulnerability',
    'Volume', 'VolumeMount',
    'Network', 'NetworkConnection',
    'ComposeProject', 'ComposeFile', 'ComposeService', 'ComposeServiceContainer',
    'Backup', 'BackupItem', 'RestoreJob', 'RestoreItem',
    'MetricSample', 'Alert', 'AlertRule', 'LogEntry', 'Dashboard', 'DashboardWidget',
    'ChatMessage', 'ChatSession',
]
