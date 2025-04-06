"""
Container schemas for the DockerForge Web UI.

This module provides the Pydantic schemas for container management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PortMapping(BaseModel):
    """
    Port mapping schema.
    """
    host_ip: Optional[str] = Field(None, description="Host IP")
    host_port: int = Field(..., description="Host port")
    container_port: int = Field(..., description="Container port")
    protocol: str = Field("tcp", description="Protocol (tcp or udp)")


class VolumeMapping(BaseModel):
    """
    Volume mapping schema.
    """
    host_path: str = Field(..., description="Host path")
    container_path: str = Field(..., description="Container path")
    mode: str = Field("rw", description="Mode (ro or rw)")


class ContainerBase(BaseModel):
    """
    Base container schema.
    """
    name: str = Field(..., description="Container name")
    image: str = Field(..., description="Image name")
    command: Optional[str] = Field(None, description="Command to run")
    entrypoint: Optional[str] = Field(None, description="Entrypoint")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    ports: Optional[List[PortMapping]] = Field(None, description="Port mappings")
    volumes: Optional[List[VolumeMapping]] = Field(None, description="Volume mappings")
    network: Optional[str] = Field(None, description="Network name")
    restart_policy: Optional[str] = Field(None, description="Restart policy")
    labels: Optional[Dict[str, str]] = Field(None, description="Container labels")
    hostname: Optional[str] = Field(None, description="Container hostname")
    dns: Optional[List[str]] = Field(None, description="DNS servers")
    dns_search: Optional[List[str]] = Field(None, description="DNS search domains")
    cpu_limit: Optional[float] = Field(None, description="CPU limit in cores")
    memory_limit: Optional[int] = Field(None, description="Memory limit in bytes")


class ContainerCreate(ContainerBase):
    """
    Container creation schema.
    """
    pass


class ContainerUpdate(BaseModel):
    """
    Container update schema.
    """
    name: Optional[str] = Field(None, description="Container name")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    restart_policy: Optional[str] = Field(None, description="Restart policy")
    labels: Optional[Dict[str, str]] = Field(None, description="Container labels")


class Container(ContainerBase):
    """
    Container schema for responses.
    """
    id: str = Field(..., description="Container ID")
    status: str = Field(..., description="Container status")
    created_at: datetime = Field(..., description="Creation time")
    started_at: Optional[datetime] = Field(None, description="Start time")
    finished_at: Optional[datetime] = Field(None, description="Finish time")
    health_status: Optional[str] = Field(None, description="Health status")
    ip_address: Optional[str] = Field(None, description="IP address")
    resource_usage: Optional[Dict[str, Any]] = Field(None, description="Resource usage")

    class Config:
        orm_mode = True
