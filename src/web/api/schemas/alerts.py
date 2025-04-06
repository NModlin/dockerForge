"""
Alert schemas for the DockerForge Web UI.

This module provides the Pydantic models for alert management.
"""
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertStatus(str, Enum):
    """Alert status values."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertSource(str, Enum):
    """Alert source types."""
    CONTAINER = "container"
    IMAGE = "image"
    VOLUME = "volume"
    NETWORK = "network"
    SYSTEM = "system"


class MetricType(str, Enum):
    """Metric types for alerts."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    UPTIME = "uptime"
    HEALTH = "health"
    CUSTOM = "custom"


class AlertCondition(str, Enum):
    """Alert condition operators."""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="


class NotificationType(str, Enum):
    """Notification channel types."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    CUSTOM = "custom"


class NotificationChannelBase(BaseModel):
    """Base notification channel schema."""
    name: str = Field(..., description="Channel name")
    type: NotificationType = Field(..., description="Channel type")
    enabled: bool = Field(True, description="Whether the channel is enabled")
    config: Dict[str, Any] = Field(..., description="Channel configuration")


class NotificationChannelCreate(NotificationChannelBase):
    """Notification channel creation schema."""
    pass


class NotificationChannel(NotificationChannelBase):
    """Notification channel schema."""
    id: str = Field(..., description="Channel ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        orm_mode = True


class AlertRuleBase(BaseModel):
    """Base alert rule schema."""
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    enabled: bool = Field(True, description="Whether the rule is enabled")
    severity: AlertSeverity = Field(..., description="Alert severity")
    source_type: AlertSource = Field(..., description="Alert source type")
    source_filter: Optional[Dict[str, Any]] = Field(None, description="Filter for source (e.g., container name pattern)")
    metric_type: MetricType = Field(..., description="Metric type")
    condition: AlertCondition = Field(..., description="Condition operator")
    threshold: float = Field(..., description="Threshold value")
    duration: Optional[int] = Field(None, description="Duration in seconds for condition to be true")
    cooldown: Optional[int] = Field(None, description="Cooldown period in seconds")
    notification_channels: List[str] = Field([], description="List of notification channel IDs")


class AlertRuleCreate(AlertRuleBase):
    """Alert rule creation schema."""
    pass


class AlertRuleUpdate(BaseModel):
    """Alert rule update schema."""
    name: Optional[str] = Field(None, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    enabled: Optional[bool] = Field(None, description="Whether the rule is enabled")
    severity: Optional[AlertSeverity] = Field(None, description="Alert severity")
    source_type: Optional[AlertSource] = Field(None, description="Alert source type")
    source_filter: Optional[Dict[str, Any]] = Field(None, description="Filter for source (e.g., container name pattern)")
    metric_type: Optional[MetricType] = Field(None, description="Metric type")
    condition: Optional[AlertCondition] = Field(None, description="Condition operator")
    threshold: Optional[float] = Field(None, description="Threshold value")
    duration: Optional[int] = Field(None, description="Duration in seconds for condition to be true")
    cooldown: Optional[int] = Field(None, description="Cooldown period in seconds")
    notification_channels: Optional[List[str]] = Field(None, description="List of notification channel IDs")


class AlertRule(AlertRuleBase):
    """Alert rule schema."""
    id: str = Field(..., description="Rule ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        orm_mode = True


class AlertBase(BaseModel):
    """Base alert schema."""
    name: str = Field(..., description="Alert name")
    description: Optional[str] = Field(None, description="Alert description")
    severity: AlertSeverity = Field(..., description="Alert severity")
    source: AlertSource = Field(..., description="Alert source")
    source_id: Optional[str] = Field(None, description="Source ID (container ID, etc.)")
    source_name: Optional[str] = Field(None, description="Source name (container name, etc.)")
    metric_type: Optional[MetricType] = Field(None, description="Metric type")
    threshold: Optional[float] = Field(None, description="Threshold value")
    value: Optional[float] = Field(None, description="Actual value")


class AlertCreate(AlertBase):
    """Alert creation schema."""
    rule_id: Optional[str] = Field(None, description="Alert rule ID")


class Alert(AlertBase):
    """Alert schema."""
    id: str = Field(..., description="Alert ID")
    status: AlertStatus = Field(..., description="Alert status")
    rule_id: Optional[str] = Field(None, description="Alert rule ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgement timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    acknowledged_by: Optional[str] = Field(None, description="User ID who acknowledged the alert")

    class Config:
        orm_mode = True


class AlertUpdate(BaseModel):
    """Alert update schema."""
    status: Optional[AlertStatus] = Field(None, description="Alert status")
    acknowledged_by: Optional[str] = Field(None, description="User ID who acknowledged the alert")
    resolution_notes: Optional[str] = Field(None, description="Notes about the resolution")


class AlertHistoryFilter(BaseModel):
    """Alert history filter schema."""
    severity: Optional[List[AlertSeverity]] = Field(None, description="Filter by severity")
    status: Optional[List[AlertStatus]] = Field(None, description="Filter by status")
    source: Optional[List[AlertSource]] = Field(None, description="Filter by source")
    source_id: Optional[str] = Field(None, description="Filter by source ID")
    metric_type: Optional[List[MetricType]] = Field(None, description="Filter by metric type")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    rule_id: Optional[str] = Field(None, description="Filter by rule ID")


class AlertStatistics(BaseModel):
    """Alert statistics schema."""
    total: int = Field(..., description="Total number of alerts")
    by_severity: Dict[AlertSeverity, int] = Field(..., description="Alerts by severity")
    by_status: Dict[AlertStatus, int] = Field(..., description="Alerts by status")
    by_source: Dict[AlertSource, int] = Field(..., description="Alerts by source")
    by_metric_type: Dict[MetricType, int] = Field(..., description="Alerts by metric type")
    active_by_severity: Dict[AlertSeverity, int] = Field(..., description="Active alerts by severity")
