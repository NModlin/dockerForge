"""
Container models for the DockerForge Web UI.

This module provides the SQLAlchemy models for container management.
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Text, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin


class Container(BaseModel, TimestampMixin):
    """
    Container model for Docker container management.
    """
    __tablename__ = 'containers'

    name = Column(String(100), nullable=False, index=True)
    docker_id = Column(String(64), unique=True, nullable=True, index=True)
    image_id = Column(Integer, ForeignKey('images.id'), nullable=False)
    status = Column(String(20), nullable=False, default='created')
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    health_status = Column(String(20), nullable=True)
    ip_address = Column(String(50), nullable=True)
    command = Column(String(255), nullable=True)
    entrypoint = Column(String(255), nullable=True)
    environment = Column(JSON, nullable=True)
    ports = Column(JSON, nullable=True)
    volumes = Column(JSON, nullable=True)
    network = Column(String(50), nullable=True)
    restart_policy = Column(String(50), nullable=True)
    labels = Column(JSON, nullable=True)
    resource_usage = Column(JSON, nullable=True)
    hostname = Column(String(100), nullable=True)
    dns = Column(JSON, nullable=True)
    dns_search = Column(JSON, nullable=True)
    cpu_limit = Column(Integer, nullable=True)
    memory_limit = Column(Integer, nullable=True)

    # Relationships
    image = relationship("Image", back_populates="containers")
    logs = relationship("ContainerLog", back_populates="container", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Container(name='{self.name}', docker_id='{self.docker_id}', status='{self.status}')>"


class ContainerLog(BaseModel, TimestampMixin):
    """
    Container log model for storing container logs.
    """
    __tablename__ = 'container_logs'

    container_id = Column(ForeignKey('containers.id'), nullable=False, index=True)
    log_type = Column(String(20), nullable=False, default='stdout')  # stdout, stderr
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # Relationships
    container = relationship("Container", back_populates="logs")

    def __repr__(self):
        return f"<ContainerLog(container_id={self.container_id}, log_type='{self.log_type}', timestamp='{self.timestamp}')>"
