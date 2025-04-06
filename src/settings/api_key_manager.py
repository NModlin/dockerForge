"""
DockerForge API Key Management Service

This module provides functionality for managing API keys, including generation,
validation, revocation, and usage tracking.
"""

import os
import uuid
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple
import secrets
import hashlib
import json
from sqlalchemy.orm import Session

from src.config.config_manager import ConfigManager
from src.web.api.models.api_key import ApiKey, ApiKeyUsage

logger = logging.getLogger(__name__)

class ApiKeyManager:
    """
    Manages API keys for DockerForge.
    
    This class handles:
    - API key generation
    - Key validation
    - Key revocation
    - Usage tracking
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the API key manager.
        
        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
    
    def generate_key(self, name: str, user_id: int, expiration: str = "never", 
                    is_read_only: bool = False, scopes: List[str] = None) -> Tuple[str, ApiKey]:
        """
        Generate a new API key.
        
        Args:
            name: A descriptive name for the key
            user_id: The ID of the user creating the key
            expiration: When the key should expire ("never", "30d", "90d", "1y")
            is_read_only: Whether the key should be read-only
            scopes: List of permission scopes for the key
            
        Returns:
            Tuple of (raw_key, api_key_model)
        """
        # Generate a random key
        raw_key = f"dk_{secrets.token_urlsafe(32)}"
        
        # Hash the key for storage
        key_hash = self._hash_key(raw_key)
        
        # Calculate expiration date
        expires_at = self._calculate_expiration(expiration)
        
        # Create API key model
        api_key = ApiKey(
            name=name,
            key_hash=key_hash,
            user_id=user_id,
            expires_at=expires_at,
            is_read_only=is_read_only,
            scopes=json.dumps(scopes) if scopes else json.dumps([]),
            created_at=datetime.datetime.utcnow()
        )
        
        return raw_key, api_key
    
    def validate_key(self, raw_key: str, db: Session) -> Optional[ApiKey]:
        """
        Validate an API key.
        
        Args:
            raw_key: The raw API key to validate
            db: Database session
            
        Returns:
            The API key model if valid, None otherwise
        """
        if not raw_key:
            return None
        
        # Hash the key
        key_hash = self._hash_key(raw_key)
        
        # Look up the key in the database
        api_key = db.query(ApiKey).filter(ApiKey.key_hash == key_hash, ApiKey.revoked_at.is_(None)).first()
        
        if not api_key:
            return None
        
        # Check if the key has expired
        if api_key.expires_at and api_key.expires_at < datetime.datetime.utcnow():
            return None
        
        # Update last used timestamp
        api_key.last_used = datetime.datetime.utcnow()
        db.commit()
        
        return api_key
    
    def revoke_key(self, key_id: int, db: Session) -> bool:
        """
        Revoke an API key.
        
        Args:
            key_id: The ID of the key to revoke
            db: Database session
            
        Returns:
            True if the key was revoked, False otherwise
        """
        api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
        
        if not api_key:
            return False
        
        api_key.revoked_at = datetime.datetime.utcnow()
        db.commit()
        
        return True
    
    def track_usage(self, api_key: ApiKey, endpoint: str, method: str, status_code: int, 
                   response_time: float, db: Session) -> None:
        """
        Track API key usage.
        
        Args:
            api_key: The API key model
            endpoint: The API endpoint that was accessed
            method: The HTTP method used
            status_code: The HTTP status code returned
            response_time: The response time in milliseconds
            db: Database session
        """
        usage = ApiKeyUsage(
            api_key_id=api_key.id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            created_at=datetime.datetime.utcnow()
        )
        
        db.add(usage)
        db.commit()
    
    def get_key_usage_stats(self, key_id: int, db: Session) -> Dict[str, Any]:
        """
        Get usage statistics for an API key.
        
        Args:
            key_id: The ID of the API key
            db: Database session
            
        Returns:
            Dictionary of usage statistics
        """
        # Get all usage records for the key
        usage_records = db.query(ApiKeyUsage).filter(ApiKeyUsage.api_key_id == key_id).all()
        
        if not usage_records:
            return {
                "total_requests": 0,
                "requests_today": 0,
                "success_rate": 0,
                "avg_response_time": 0,
                "usage_over_time": [],
                "top_endpoints": []
            }
        
        # Calculate statistics
        total_requests = len(usage_records)
        
        # Calculate requests today
        today = datetime.datetime.utcnow().date()
        requests_today = sum(1 for record in usage_records if record.created_at.date() == today)
        
        # Calculate success rate
        successful_requests = sum(1 for record in usage_records if 200 <= record.status_code < 300)
        success_rate = round((successful_requests / total_requests) * 100) if total_requests > 0 else 0
        
        # Calculate average response time
        avg_response_time = round(sum(record.response_time for record in usage_records) / total_requests, 2) if total_requests > 0 else 0
        
        # Calculate usage over time (last 30 days)
        usage_over_time = self._calculate_usage_over_time(usage_records)
        
        # Calculate top endpoints
        top_endpoints = self._calculate_top_endpoints(usage_records)
        
        return {
            "total_requests": total_requests,
            "requests_today": requests_today,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "usage_over_time": usage_over_time,
            "top_endpoints": top_endpoints
        }
    
    def _hash_key(self, raw_key: str) -> str:
        """
        Hash an API key for secure storage.
        
        Args:
            raw_key: The raw API key
            
        Returns:
            Hashed key
        """
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def _calculate_expiration(self, expiration: str) -> Optional[datetime.datetime]:
        """
        Calculate the expiration date for an API key.
        
        Args:
            expiration: Expiration string ("never", "30d", "90d", "1y")
            
        Returns:
            Expiration datetime or None if the key never expires
        """
        if expiration == "never":
            return None
        
        now = datetime.datetime.utcnow()
        
        if expiration == "30d":
            return now + datetime.timedelta(days=30)
        elif expiration == "90d":
            return now + datetime.timedelta(days=90)
        elif expiration == "1y":
            return now + datetime.timedelta(days=365)
        
        # Default to never expire
        return None
    
    def _calculate_usage_over_time(self, usage_records: List[ApiKeyUsage]) -> List[Dict[str, Any]]:
        """
        Calculate usage over time for the last 30 days.
        
        Args:
            usage_records: List of API key usage records
            
        Returns:
            List of daily usage counts
        """
        # Get date range for the last 30 days
        end_date = datetime.datetime.utcnow().date()
        start_date = end_date - datetime.timedelta(days=29)
        
        # Initialize result with zero counts for all days
        result = []
        current_date = start_date
        while current_date <= end_date:
            result.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "count": 0
            })
            current_date += datetime.timedelta(days=1)
        
        # Count requests for each day
        for record in usage_records:
            record_date = record.created_at.date()
            if start_date <= record_date <= end_date:
                day_index = (record_date - start_date).days
                result[day_index]["count"] += 1
        
        return result
    
    def _calculate_top_endpoints(self, usage_records: List[ApiKeyUsage]) -> List[Dict[str, Any]]:
        """
        Calculate the top 5 most frequently accessed endpoints.
        
        Args:
            usage_records: List of API key usage records
            
        Returns:
            List of top endpoints with counts
        """
        # Count requests by endpoint
        endpoint_counts = {}
        for record in usage_records:
            endpoint = record.endpoint
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
        
        # Sort by count and take top 5
        top_endpoints = sorted(
            [{"endpoint": endpoint, "count": count} for endpoint, count in endpoint_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:5]
        
        return top_endpoints
