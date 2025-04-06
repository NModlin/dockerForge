"""
API key models for the DockerForge Web UI.

This module provides the database models for API keys.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Table
from sqlalchemy.orm import relationship
import datetime
import uuid

from .base import Base, BaseModel, TimestampMixin


class ApiKey(BaseModel, TimestampMixin):
    """
    API key model.
    
    This model stores API keys for programmatic access to the API.
    """
    __tablename__ = "api_keys"

    name = Column(String(100), nullable=False)
    key_prefix = Column(String(10), nullable=False)  # First few characters of the key for display
    key_hash = Column(String(100), nullable=False)  # Hashed API key for verification
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=True)  # NULL means no expiration
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_read_only = Column(Boolean, default=False, nullable=False)
    scopes = Column(JSON, nullable=True)  # List of permission scopes
    
    # Relationships
    user = relationship("User", backref="api_keys")
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    @classmethod
    def generate_key(cls):
        """
        Generate a new API key.
        
        Returns:
            Tuple of (full_key, prefix, hashed_key)
        """
        import hashlib
        import secrets
        
        # Generate a random key with a prefix
        prefix = "df_"
        random_part = secrets.token_hex(16)
        full_key = f"{prefix}{random_part}"
        
        # Get the prefix for display (first 8 chars)
        key_prefix = full_key[:8]
        
        # Hash the key for storage
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        
        return full_key, key_prefix, key_hash
    
    @classmethod
    def verify_key(cls, key, key_hash):
        """
        Verify an API key against its hash.
        
        Args:
            key: The API key to verify
            key_hash: The stored hash to compare against
            
        Returns:
            True if the key is valid, False otherwise
        """
        import hashlib
        
        # Hash the provided key
        computed_hash = hashlib.sha256(key.encode()).hexdigest()
        
        # Compare with the stored hash
        return computed_hash == key_hash
