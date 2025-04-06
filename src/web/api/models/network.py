"""
Network models for the DockerForge Web UI.

This module provides the SQLAlchemy models for network management.
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


class Network(BaseModel, TimestampMixin):
    """
    Network model for Docker network management.
    """

    __tablename__ = "networks"

    name = Column(String(100), nullable=False, index=True, unique=True)
    docker_id = Column(String(64), unique=True, nullable=True, index=True)
    driver = Column(String(50), nullable=False, default="bridge")
    scope = Column(String(20), nullable=False, default="local")  # local, swarm, global
    internal = Column(Boolean, nullable=False, default=False)
    ipam = Column(JSON, nullable=True)  # IP address management config
    options = Column(JSON, nullable=True)
    labels = Column(JSON, nullable=True)

    # Relationships
    network_connections = relationship(
        "NetworkConnection", back_populates="network", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Network(name='{self.name}', driver='{self.driver}', scope='{self.scope}')>"


class NetworkConnection(BaseModel, TimestampMixin):
    """
    Network connection model for tracking network usage by containers.
    """

    __tablename__ = "network_connections"

    network_id = Column(ForeignKey("networks.id"), nullable=False, index=True)
    container_id = Column(ForeignKey("containers.id"), nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    ip_prefix_len = Column(Integer, nullable=True)
    gateway = Column(String(50), nullable=True)
    mac_address = Column(String(50), nullable=True)
    aliases = Column(JSON, nullable=True)

    # Relationships
    network = relationship("Network", back_populates="network_connections")
    container = relationship("Container")

    def __repr__(self):
        return f"<NetworkConnection(network_id={self.network_id}, container_id={self.container_id}, ip_address='{self.ip_address}')>"
