"""
Image schemas for the DockerForge Web UI.

This module provides the Pydantic schemas for image management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ImageBase(BaseModel):
    """
    Base image schema.
    """
    name: str
    tag: Optional[str] = "latest"


class ImageCreate(ImageBase):
    """
    Image creation schema.
    """
    pull: bool = True


class ImageUpdate(BaseModel):
    """
    Image update schema.
    """
    tag: Optional[str] = None


class ImagePort(BaseModel):
    """
    Image port schema.
    """
    container_port: int
    protocol: str = "tcp"


class ImageVolume(BaseModel):
    """
    Image volume schema.
    """
    container_path: str
    mode: Optional[str] = None


class ImageEnv(BaseModel):
    """
    Image environment variable schema.
    """
    key: str
    value: str


class Image(ImageBase):
    """
    Image schema for responses.
    """
    id: str
    docker_id: Optional[str] = None
    short_id: Optional[str] = None
    size: Optional[int] = None
    digest: Optional[str] = None
    created_at: Optional[datetime] = None
    author: Optional[str] = None
    architecture: Optional[str] = None
    os: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    env: Optional[List[ImageEnv]] = None
    cmd: Optional[List[str]] = None
    entrypoint: Optional[List[str]] = None
    exposed_ports: Optional[List[ImagePort]] = None
    volumes: Optional[List[ImageVolume]] = None

    class Config:
        orm_mode = True


class ImageScan(BaseModel):
    """
    Image scan schema.
    """
    id: int
    image_id: int
    scan_type: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    vulnerabilities_count: Optional[int] = None
    critical_count: Optional[int] = None
    high_count: Optional[int] = None
    medium_count: Optional[int] = None
    low_count: Optional[int] = None

    class Config:
        orm_mode = True


class ImageVulnerability(BaseModel):
    """
    Image vulnerability schema.
    """
    id: int
    scan_id: int
    name: str
    description: Optional[str] = None
    severity: str
    package_name: Optional[str] = None
    package_version: Optional[str] = None
    fixed_version: Optional[str] = None
    reference_urls: Optional[List[str]] = None
    cve_id: Optional[str] = None

    class Config:
        orm_mode = True


class ImageScanCreate(BaseModel):
    """
    Image scan creation schema.
    """
    scan_type: str = "vulnerability"


class ImageScanResult(BaseModel):
    """
    Image scan result schema.
    """
    scan: ImageScan
    vulnerabilities: List[ImageVulnerability]


class DockerfileValidation(BaseModel):
    """
    Dockerfile validation result schema.
    """
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    analysis: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class DockerfileBuild(BaseModel):
    """
    Dockerfile build request schema.
    """
    dockerfile: str
    name: str
    tag: str = "latest"
    options: Dict[str, Any] = Field(default_factory=dict)
