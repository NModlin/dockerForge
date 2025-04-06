"""
Volume schemas for the DockerForge Web UI.

This module provides the Pydantic models for volume management.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class VolumeBase(BaseModel):
    """
    Base volume schema.
    """
    name: str = Field(..., description="Volume name")
    driver: str = Field("local", description="Volume driver (local, nfs, etc.)")
    driver_opts: Optional[Dict[str, str]] = Field(None, description="Volume driver options")
    labels: Optional[Dict[str, str]] = Field(None, description="Volume labels")


class VolumeCreate(VolumeBase):
    """
    Volume creation schema.
    """
    pass


class VolumeUpdate(BaseModel):
    """
    Volume update schema.
    """
    labels: Optional[Dict[str, str]] = Field(None, description="Volume labels")


class VolumeMount(BaseModel):
    """
    Volume mount schema.
    """
    container_id: str = Field(..., description="Container ID")
    container_name: str = Field(..., description="Container name")
    source: str = Field(..., description="Source path")
    destination: str = Field(..., description="Destination path")
    mode: str = Field("rw", description="Mount mode (rw, ro)")
    rw: bool = Field(True, description="Read-write flag")
    propagation: Optional[str] = Field(None, description="Mount propagation")


class Volume(VolumeBase):
    """
    Volume schema.
    """
    id: str = Field(..., description="Volume ID")
    docker_id: Optional[str] = Field(None, description="Docker volume ID")
    created_at: datetime = Field(..., description="Volume creation time")
    updated_at: datetime = Field(..., description="Volume last update time")
    mountpoint: Optional[str] = Field(None, description="Volume mountpoint")
    scope: str = Field("local", description="Volume scope (local, global)")
    status: Optional[Dict[str, Any]] = Field(None, description="Volume status")
    type: str = Field("volume", description="Volume type (volume, bind, tmpfs)")
    mounts: Optional[List[VolumeMount]] = Field(None, description="Volume mounts")
    
    class Config:
        orm_mode = True
