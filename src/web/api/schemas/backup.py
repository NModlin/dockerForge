"""
Backup schemas for the DockerForge Web UI.

This module provides the Pydantic models for backup management.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


# Base schemas
class BackupItemBase(BaseModel):
    """Base schema for backup items."""
    item_type: str
    item_id: str
    item_name: str
    status: str = "pending"
    error_message: Optional[str] = None
    backup_metadata: Optional[Dict[str, Any]] = None


class BackupBase(BaseModel):
    """Base schema for backups."""
    name: str
    description: Optional[str] = None
    backup_type: str
    status: str = "pending"
    backup_metadata: Optional[Dict[str, Any]] = None


class RestoreItemBase(BaseModel):
    """Base schema for restore items."""
    backup_item_id: int
    status: str = "pending"
    error_message: Optional[str] = None
    new_item_id: Optional[str] = None


class RestoreJobBase(BaseModel):
    """Base schema for restore jobs."""
    backup_id: int
    name: str
    description: Optional[str] = None
    status: str = "pending"
    options: Optional[Dict[str, Any]] = None


# Create schemas (used for POST requests)
class BackupItemCreate(BackupItemBase):
    """Schema for creating backup items."""
    pass


class BackupCreate(BackupBase):
    """Schema for creating backups."""
    pass


class RestoreItemCreate(RestoreItemBase):
    """Schema for creating restore items."""
    pass


class RestoreJobCreate(RestoreJobBase):
    """Schema for creating restore jobs."""
    pass


# Update schemas (used for PUT requests)
class BackupItemUpdate(BaseModel):
    """Schema for updating backup items."""
    item_type: Optional[str] = None
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    backup_metadata: Optional[Dict[str, Any]] = None


class BackupUpdate(BaseModel):
    """Schema for updating backups."""
    name: Optional[str] = None
    description: Optional[str] = None
    backup_type: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    backup_metadata: Optional[Dict[str, Any]] = None


class RestoreItemUpdate(BaseModel):
    """Schema for updating restore items."""
    status: Optional[str] = None
    error_message: Optional[str] = None
    new_item_id: Optional[str] = None


class RestoreJobUpdate(BaseModel):
    """Schema for updating restore jobs."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    options: Optional[Dict[str, Any]] = None


# Response schemas (used for GET responses)
class BackupItem(BackupItemBase):
    """Schema for backup item responses."""
    id: int
    backup_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Backup(BackupBase):
    """Schema for backup responses."""
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class BackupDetail(Backup):
    """Schema for detailed backup responses."""
    backup_items: List[BackupItem] = []

    class Config:
        orm_mode = True


class RestoreItem(RestoreItemBase):
    """Schema for restore item responses."""
    id: int
    restore_job_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RestoreJob(RestoreJobBase):
    """Schema for restore job responses."""
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RestoreJobDetail(RestoreJob):
    """Schema for detailed restore job responses."""
    restore_items: List[RestoreItem] = []
    backup: Backup

    class Config:
        orm_mode = True
