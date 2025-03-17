"""
Base database models for the DockerForge Web UI.

This module provides the base SQLAlchemy models for the DockerForge Web UI.
"""
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps to models.
    """
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base):
    """
    Base model with common attributes.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
