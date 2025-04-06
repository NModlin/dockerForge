"""
Image models for the DockerForge Web UI.

This module provides the SQLAlchemy models for image management.
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


class Image(BaseModel, TimestampMixin):
    """
    Image model for Docker image management.
    """

    __tablename__ = "images"

    name = Column(String(100), nullable=False, index=True)
    tag = Column(String(100), nullable=False, default="latest")
    docker_id = Column(String(64), unique=True, nullable=True, index=True)
    size = Column(Integer, nullable=True)  # Size in bytes
    digest = Column(String(100), nullable=True)
    created_at_docker = Column(
        DateTime, nullable=True
    )  # When the image was created in Docker
    author = Column(String(100), nullable=True)
    architecture = Column(String(20), nullable=True)
    os = Column(String(20), nullable=True)
    labels = Column(JSON, nullable=True)
    env = Column(JSON, nullable=True)
    cmd = Column(JSON, nullable=True)
    entrypoint = Column(JSON, nullable=True)
    exposed_ports = Column(JSON, nullable=True)
    volumes = Column(JSON, nullable=True)

    # Relationships
    containers = relationship("Container", back_populates="image")
    security_scans = relationship(
        "SecurityScan", back_populates="image", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Image(name='{self.name}', tag='{self.tag}', docker_id='{self.docker_id}')>"


class SecurityScan(BaseModel, TimestampMixin):
    """
    Security scan model for image vulnerability scanning.
    """

    __tablename__ = "security_scans"

    image_id = Column(ForeignKey("images.id"), nullable=False, index=True)
    scan_type = Column(
        String(50), nullable=False
    )  # e.g., 'vulnerability', 'compliance'
    status = Column(
        String(20), nullable=False, default="pending"
    )  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result_summary = Column(JSON, nullable=True)  # Summary of scan results
    vulnerabilities_count = Column(Integer, nullable=True)
    critical_count = Column(Integer, nullable=True)
    high_count = Column(Integer, nullable=True)
    medium_count = Column(Integer, nullable=True)
    low_count = Column(Integer, nullable=True)

    # Relationships
    image = relationship("Image", back_populates="security_scans")
    vulnerabilities = relationship(
        "Vulnerability", back_populates="scan", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SecurityScan(image_id={self.image_id}, scan_type='{self.scan_type}', status='{self.status}')>"


class Vulnerability(BaseModel, TimestampMixin):
    """
    Vulnerability model for storing security vulnerabilities.
    """

    __tablename__ = "vulnerabilities"

    scan_id = Column(ForeignKey("security_scans.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    package_name = Column(String(100), nullable=True)
    package_version = Column(String(50), nullable=True)
    fixed_version = Column(String(50), nullable=True)
    reference_urls = Column(JSON, nullable=True)
    cve_id = Column(String(20), nullable=True, index=True)

    # Relationships
    scan = relationship("SecurityScan", back_populates="vulnerabilities")

    def __repr__(self):
        return f"<Vulnerability(name='{self.name}', severity='{self.severity}', cve_id='{self.cve_id}')>"
