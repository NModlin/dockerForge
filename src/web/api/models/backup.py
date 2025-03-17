"""
Backup models for the DockerForge Web UI.

This module provides the SQLAlchemy models for backup management.
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Integer, Text
from sqlalchemy.orm import relationship

from .base import BaseModel, TimestampMixin


class Backup(BaseModel, TimestampMixin):
    """
    Backup model for Docker backup management.
    """
    __tablename__ = 'backups'
    
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    backup_type = Column(String(20), nullable=False)  # container, image, volume, compose, system
    status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    file_path = Column(String(255), nullable=True)  # Path to backup file
    file_size = Column(Integer, nullable=True)  # Size in bytes
    backup_metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Relationships
    backup_items = relationship("BackupItem", back_populates="backup", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Backup(name='{self.name}', backup_type='{self.backup_type}', status='{self.status}')>"


class BackupItem(BaseModel, TimestampMixin):
    """
    Backup item model for tracking items included in a backup.
    """
    __tablename__ = 'backup_items'
    
    backup_id = Column(ForeignKey('backups.id'), nullable=False, index=True)
    item_type = Column(String(20), nullable=False)  # container, image, volume, network, compose
    item_id = Column(String(100), nullable=False)  # ID of the item (container ID, image ID, etc.)
    item_name = Column(String(100), nullable=False)  # Name of the item
    status = Column(String(20), nullable=False, default='pending')  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    backup_metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Relationships
    backup = relationship("Backup", back_populates="backup_items")
    
    def __repr__(self):
        return f"<BackupItem(backup_id={self.backup_id}, item_type='{self.item_type}', item_name='{self.item_name}')>"


class RestoreJob(BaseModel, TimestampMixin):
    """
    Restore job model for tracking restore operations.
    """
    __tablename__ = 'restore_jobs'
    
    backup_id = Column(ForeignKey('backups.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    options = Column(JSON, nullable=True)  # Restore options
    
    # Relationships
    backup = relationship("Backup")
    restore_items = relationship("RestoreItem", back_populates="restore_job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RestoreJob(backup_id={self.backup_id}, name='{self.name}', status='{self.status}')>"


class RestoreItem(BaseModel, TimestampMixin):
    """
    Restore item model for tracking items included in a restore operation.
    """
    __tablename__ = 'restore_items'
    
    restore_job_id = Column(ForeignKey('restore_jobs.id'), nullable=False, index=True)
    backup_item_id = Column(ForeignKey('backup_items.id'), nullable=False)
    status = Column(String(20), nullable=False, default='pending')  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    new_item_id = Column(String(100), nullable=True)  # ID of the newly created item
    
    # Relationships
    restore_job = relationship("RestoreJob", back_populates="restore_items")
    backup_item = relationship("BackupItem")
    
    def __repr__(self):
        return f"<RestoreItem(restore_job_id={self.restore_job_id}, backup_item_id={self.backup_item_id}, status='{self.status}')>"
