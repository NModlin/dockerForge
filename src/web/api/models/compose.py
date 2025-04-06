"""
Compose models for the DockerForge Web UI.

This module provides the SQLAlchemy models for Docker Compose management.
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


class ComposeProject(BaseModel, TimestampMixin):
    """
    Compose project model for Docker Compose project management.
    """

    __tablename__ = "compose_projects"

    name = Column(String(100), nullable=False, index=True, unique=True)
    description = Column(String(255), nullable=True)
    status = Column(
        String(20), nullable=False, default="inactive"
    )  # inactive, active, error
    path = Column(String(255), nullable=True)  # Path to compose file directory
    version = Column(String(20), nullable=False, default="3.8")  # Compose file version

    # Relationships
    files = relationship(
        "ComposeFile", back_populates="project", cascade="all, delete-orphan"
    )
    services = relationship(
        "ComposeService", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ComposeProject(name='{self.name}', status='{self.status}')>"


class ComposeFile(BaseModel, TimestampMixin):
    """
    Compose file model for storing Docker Compose files.
    """

    __tablename__ = "compose_files"

    project_id = Column(ForeignKey("compose_projects.id"), nullable=False, index=True)
    name = Column(
        String(100), nullable=False
    )  # e.g., docker-compose.yml, docker-compose.override.yml
    content = Column(Text, nullable=False)
    is_main = Column(
        Boolean, nullable=False, default=False
    )  # Is this the main compose file?

    # Relationships
    project = relationship("ComposeProject", back_populates="files")

    def __repr__(self):
        return f"<ComposeFile(project_id={self.project_id}, name='{self.name}', is_main={self.is_main})>"


class ComposeService(BaseModel, TimestampMixin):
    """
    Compose service model for tracking services defined in Docker Compose files.
    """

    __tablename__ = "compose_services"

    project_id = Column(ForeignKey("compose_projects.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    image = Column(String(100), nullable=True)
    build = Column(JSON, nullable=True)  # Build configuration
    command = Column(String(255), nullable=True)
    entrypoint = Column(String(255), nullable=True)
    environment = Column(JSON, nullable=True)
    ports = Column(JSON, nullable=True)
    volumes = Column(JSON, nullable=True)
    networks = Column(JSON, nullable=True)
    depends_on = Column(JSON, nullable=True)
    restart = Column(String(50), nullable=True)
    deploy = Column(JSON, nullable=True)
    configs = Column(JSON, nullable=True)
    secrets = Column(JSON, nullable=True)

    # Relationships
    project = relationship("ComposeProject", back_populates="services")
    containers = relationship(
        "ComposeServiceContainer",
        back_populates="service",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<ComposeService(project_id={self.project_id}, name='{self.name}')>"


class ComposeServiceContainer(BaseModel, TimestampMixin):
    """
    Compose service container model for tracking containers created from compose services.
    """

    __tablename__ = "compose_service_containers"

    service_id = Column(ForeignKey("compose_services.id"), nullable=False, index=True)
    container_id = Column(ForeignKey("containers.id"), nullable=False, index=True)

    # Relationships
    service = relationship("ComposeService", back_populates="containers")
    container = relationship("Container")

    def __repr__(self):
        return f"<ComposeServiceContainer(service_id={self.service_id}, container_id={self.container_id})>"
