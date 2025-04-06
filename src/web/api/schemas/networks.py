"""
Network schemas for the DockerForge Web UI.

This module provides the Pydantic models for network management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NetworkBase(BaseModel):
    """
    Base network schema.
    """

    name: str = Field(..., description="Network name")
    driver: str = Field(
        "bridge",
        description="Network driver (bridge, host, overlay, macvlan, ipvlan, etc.)",
    )
    scope: str = Field("local", description="Network scope (local, swarm, global)")
    internal: bool = Field(False, description="Whether the network is internal")
    labels: Optional[Dict[str, str]] = Field(None, description="Network labels")
    options: Optional[Dict[str, str]] = Field(
        None, description="Network driver options"
    )


class NetworkCreate(NetworkBase):
    """
    Network creation schema.
    """

    subnet: Optional[str] = Field(
        None, description="Network subnet (e.g., 172.18.0.0/16)"
    )
    gateway: Optional[str] = Field(
        None, description="Network gateway (e.g., 172.18.0.1)"
    )


class NetworkUpdate(BaseModel):
    """
    Network update schema.
    """

    labels: Optional[Dict[str, str]] = Field(None, description="Network labels")
    options: Optional[Dict[str, str]] = Field(
        None, description="Network driver options"
    )


class IPAMConfig(BaseModel):
    """
    IPAM (IP Address Management) configuration schema.
    """

    subnet: Optional[str] = Field(None, description="Subnet in CIDR format")
    gateway: Optional[str] = Field(None, description="Gateway address")
    ip_range: Optional[str] = Field(None, description="IP range in CIDR format")
    aux_addresses: Optional[Dict[str, str]] = Field(
        None, description="Auxiliary addresses"
    )


class IPAM(BaseModel):
    """
    IPAM (IP Address Management) schema.
    """

    driver: str = Field("default", description="IPAM driver")
    config: List[IPAMConfig] = Field(
        default_factory=list, description="IPAM configuration"
    )
    options: Optional[Dict[str, str]] = Field(None, description="IPAM driver options")


class NetworkContainer(BaseModel):
    """
    Container connected to a network schema.
    """

    id: str = Field(..., description="Container ID")
    name: str = Field(..., description="Container name")
    ip_address: Optional[str] = Field(None, description="Container IP address")
    mac_address: Optional[str] = Field(None, description="Container MAC address")
    aliases: Optional[List[str]] = Field(None, description="Container network aliases")


class Network(NetworkBase):
    """
    Network schema.
    """

    id: str = Field(..., description="Network ID")
    docker_id: Optional[str] = Field(None, description="Docker network ID")
    created_at: datetime = Field(..., description="Network creation time")
    updated_at: datetime = Field(..., description="Network last update time")
    ipam: Optional[IPAM] = Field(None, description="IPAM configuration")
    containers: Optional[List[NetworkContainer]] = Field(
        None, description="Connected containers"
    )

    class Config:
        orm_mode = True
