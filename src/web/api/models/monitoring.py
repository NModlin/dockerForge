"""
Monitoring models for the DockerForge Web UI.

This module provides the SQLAlchemy models for monitoring management.
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin


class MetricSample(BaseModel, TimestampMixin):
    """
    Metric sample model for storing resource usage metrics.
    """

    __tablename__ = "metric_samples"

    container_id = Column(ForeignKey("containers.id"), nullable=True, index=True)
    metric_type = Column(
        String(50), nullable=False, index=True
    )  # cpu, memory, network, disk, etc.
    timestamp = Column(DateTime, nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # %, MB, GB/s, etc.
    labels = Column(JSON, nullable=True)  # Additional labels

    # Relationships
    container = relationship("Container")

    def __repr__(self):
        return f"<MetricSample(container_id={self.container_id}, metric_type='{self.metric_type}', value={self.value})>"


class Alert(BaseModel, TimestampMixin):
    """
    Alert model for storing monitoring alerts.
    """

    __tablename__ = "alerts"

    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    severity = Column(
        String(20), nullable=False, index=True
    )  # critical, high, medium, low
    status = Column(
        String(20), nullable=False, default="active", index=True
    )  # active, acknowledged, resolved
    source = Column(
        String(50), nullable=False
    )  # container, image, volume, network, system
    source_id = Column(
        String(100), nullable=True
    )  # ID of the source (container ID, etc.)
    metric_type = Column(String(50), nullable=True)  # cpu, memory, network, disk, etc.
    threshold = Column(Float, nullable=True)
    value = Column(Float, nullable=True)
    rule_id = Column(ForeignKey("alert_rules.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(ForeignKey("users.id"), nullable=True)

    # Relationships
    rule = relationship("AlertRule")
    acknowledged_user = relationship("User", foreign_keys=[acknowledged_by])

    def __repr__(self):
        return f"<Alert(name='{self.name}', severity='{self.severity}', status='{self.status}')>"


class AlertRule(BaseModel, TimestampMixin):
    """
    Alert rule model for defining monitoring alert rules.
    """

    __tablename__ = "alert_rules"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    source_type = Column(
        String(50), nullable=False
    )  # container, image, volume, network, system
    source_filter = Column(
        JSON, nullable=True
    )  # Filter for source (e.g., container name pattern)
    metric_type = Column(String(50), nullable=False)  # cpu, memory, network, disk, etc.
    condition = Column(String(20), nullable=False)  # >, <, >=, <=, ==, !=
    threshold = Column(Float, nullable=False)
    duration = Column(
        Integer, nullable=True
    )  # Duration in seconds for condition to be true
    cooldown = Column(Integer, nullable=True)  # Cooldown period in seconds
    actions = Column(JSON, nullable=True)  # Actions to take when alert is triggered

    def __repr__(self):
        return f"<AlertRule(name='{self.name}', metric_type='{self.metric_type}', condition='{self.condition}', threshold={self.threshold})>"


class LogEntry(BaseModel, TimestampMixin):
    """
    Log entry model for storing system and container logs.
    """

    __tablename__ = "log_entries"

    source = Column(
        String(50), nullable=False, index=True
    )  # container, image, volume, network, system
    source_id = Column(
        String(100), nullable=True, index=True
    )  # ID of the source (container ID, etc.)
    level = Column(
        String(20), nullable=False, index=True
    )  # info, warning, error, debug
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    log_metadata = Column(JSON, nullable=True)  # Additional metadata

    def __repr__(self):
        return f"<LogEntry(source='{self.source}', level='{self.level}', timestamp='{self.timestamp}')>"


class Dashboard(BaseModel, TimestampMixin):
    """
    Dashboard model for storing custom monitoring dashboards.
    """

    __tablename__ = "dashboards"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    layout = Column(JSON, nullable=False)  # Dashboard layout
    user_id = Column(ForeignKey("users.id"), nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)
    is_public = Column(Boolean, nullable=False, default=False)

    # Relationships
    user = relationship("User")
    widgets = relationship(
        "DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Dashboard(name='{self.name}', user_id={self.user_id})>"


class DashboardWidget(BaseModel, TimestampMixin):
    """
    Dashboard widget model for storing dashboard widgets.
    """

    __tablename__ = "dashboard_widgets"

    dashboard_id = Column(ForeignKey("dashboards.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    widget_type = Column(String(50), nullable=False)  # chart, gauge, table, etc.
    position = Column(JSON, nullable=False)  # Widget position (x, y, width, height)
    config = Column(JSON, nullable=False)  # Widget configuration

    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")

    def __repr__(self):
        return f"<DashboardWidget(dashboard_id={self.dashboard_id}, name='{self.name}', widget_type='{self.widget_type}')>"
