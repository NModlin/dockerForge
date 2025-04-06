"""
API key schemas for the DockerForge Web UI.

This module provides the Pydantic schemas for API keys.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class ApiKeyBase(BaseModel):
    """
    Base schema for API keys.
    """
    name: str = Field(..., description="Name of the API key")
    is_read_only: bool = Field(False, description="Whether the API key is read-only")
    scopes: Optional[List[str]] = Field(None, description="Permission scopes for the API key")


class ApiKeyCreate(ApiKeyBase):
    """
    Schema for creating a new API key.
    """
    expiration: Optional[str] = Field(None, description="Expiration period (e.g., '30d', '90d', '1y', or 'never')")
    
    @validator('expiration')
    def validate_expiration(cls, v):
        if v is not None and v != 'never' and not (v.endswith('d') or v.endswith('y')):
            raise ValueError("Expiration must be 'never' or end with 'd' (days) or 'y' (years)")
        return v


class ApiKeyResponse(ApiKeyBase):
    """
    Schema for API key responses.
    """
    id: int = Field(..., description="API key ID")
    key_prefix: str = Field(..., description="Prefix of the API key for display")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    last_used_at: Optional[datetime] = Field(None, description="Last used timestamp")
    is_active: bool = Field(True, description="Whether the API key is active")
    
    class Config:
        orm_mode = True


class ApiKeyCreatedResponse(ApiKeyResponse):
    """
    Schema for newly created API key responses.
    """
    key: str = Field(..., description="The full API key (only returned once at creation)")


class ApiKeyUpdate(BaseModel):
    """
    Schema for updating an API key.
    """
    name: Optional[str] = Field(None, description="Name of the API key")
    is_active: Optional[bool] = Field(None, description="Whether the API key is active")
    is_read_only: Optional[bool] = Field(None, description="Whether the API key is read-only")
    scopes: Optional[List[str]] = Field(None, description="Permission scopes for the API key")
    
    class Config:
        orm_mode = True
