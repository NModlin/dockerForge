"""
Volume models for the DockerForge Web UI.

This module provides the SQLAlchemy models for volume management.
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin


class Volume(BaseModel, TimestampMixin):
    """
    Volume model for Docker volume management.
    """

    __tablename__ = "volumes"

    name = Column(String(100), nullable=False, index=True, unique=True)
    docker_id = Column(String(64), unique=True, nullable=True, index=True)
    driver = Column(String(50), nullable=False, default="local")
    mountpoint = Column(String(255), nullable=True)
    status = Column(
        String(20), nullable=False, default="available"
    )  # available, in-use, error
    size = Column(Integer, nullable=True)  # Size in bytes
    labels = Column(JSON, nullable=True)
    options = Column(JSON, nullable=True)
    scope = Column(String(20), nullable=False, default="local")  # local, global

    # Relationships
    volume_mounts = relationship(
        "VolumeMount", back_populates="volume", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Volume(name='{self.name}', driver='{self.driver}', status='{self.status}')>"


class VolumeMount(BaseModel, TimestampMixin):
    """
    Volume mount model for tracking volume usage by containers.
    """

    __tablename__ = "volume_mounts"

    volume_id = Column(ForeignKey("volumes.id"), nullable=False, index=True)
    container_id = Column(ForeignKey("containers.id"), nullable=False, index=True)
    destination = Column(String(255), nullable=False)  # Mount path in container
    read_only = Column(Boolean, nullable=False, default=False)

    # Relationships
    volume = relationship("Volume", back_populates="volume_mounts")
    container = relationship("Container")

    def __repr__(self):
        return f"<VolumeMount(volume_id={self.volume_id}, container_id={self.container_id}, destination='{self.destination}')>"
