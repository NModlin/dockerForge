"""
Compose schemas for the DockerForge Web UI.

This module provides the Pydantic models for Docker Compose management.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ComposeFileBase(BaseModel):
    """
    Base compose file schema.
    """
    name: str = Field(..., description="Compose file name")
    path: str = Field(..., description="Compose file path")
    description: Optional[str] = Field(None, description="Compose file description")


class ComposeFileCreate(ComposeFileBase):
    """
    Compose file creation schema.
    """
    content: str = Field(..., description="Compose file content")


class ComposeFileUpdate(BaseModel):
    """
    Compose file update schema.
    """
    name: Optional[str] = Field(None, description="Compose file name")
    path: Optional[str] = Field(None, description="Compose file path")
    content: Optional[str] = Field(None, description="Compose file content")
    description: Optional[str] = Field(None, description="Compose file description")


class ComposeService(BaseModel):
    """
    Compose service schema.
    """
    name: str = Field(..., description="Service name")
    image: str = Field(..., description="Service image")
    status: str = Field(..., description="Service status")
    ports: Optional[List[str]] = Field(None, description="Service ports")
    volumes: Optional[List[str]] = Field(None, description="Service volumes")
    networks: Optional[List[str]] = Field(None, description="Service networks")
    depends_on: Optional[List[str]] = Field(None, description="Service dependencies")
    environment: Optional[Dict[str, str]] = Field(None, description="Service environment variables")
    command: Optional[str] = Field(None, description="Service command")
    container_id: Optional[str] = Field(None, description="Container ID")
    container_name: Optional[str] = Field(None, description="Container name")


class ComposeFile(ComposeFileBase):
    """
    Compose file schema.
    """
    id: str = Field(..., description="Compose file ID")
    created_at: datetime = Field(..., description="Compose file creation time")
    updated_at: datetime = Field(..., description="Compose file last update time")
    content: Optional[str] = Field(None, description="Compose file content")
    services_count: int = Field(..., description="Number of services in the compose file")
    status: str = Field(..., description="Compose project status")
    services: Optional[List[ComposeService]] = Field(None, description="Compose services")
    
    class Config:
        orm_mode = True
