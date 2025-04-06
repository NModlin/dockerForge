"""
API key usage models for the DockerForge Web UI.

This module provides the database models for tracking API key usage.
"""

import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base, BaseModel, TimestampMixin


class ApiKeyUsage(BaseModel, TimestampMixin):
    """
    API key usage model.

    This model tracks usage statistics for API keys.
    """

    __tablename__ = "api_key_usage"

    api_key_id = Column(
        Integer,
        ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    endpoint = Column(
        String(255), nullable=False, index=True
    )  # API endpoint that was accessed
    method = Column(String(10), nullable=False)  # HTTP method (GET, POST, etc.)
    status_code = Column(Integer, nullable=False)  # HTTP status code
    response_time = Column(Float, nullable=False)  # Response time in milliseconds
    request_size = Column(Integer, nullable=True)  # Size of the request in bytes
    response_size = Column(Integer, nullable=True)  # Size of the response in bytes
    ip_address = Column(String(50), nullable=True)  # IP address of the client
    user_agent = Column(String(255), nullable=True)  # User agent of the client

    # Relationships
    api_key = relationship("ApiKey", backref="usage_records")

    def __repr__(self):
        return f"<ApiKeyUsage(id={self.id}, api_key_id={self.api_key_id}, endpoint='{self.endpoint}')>"


class ApiKeyUsageSummary(BaseModel):
    """
    API key usage summary model.

    This model stores aggregated usage statistics for API keys.
    """

    __tablename__ = "api_key_usage_summary"

    api_key_id = Column(
        Integer,
        ForeignKey("api_keys.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date = Column(DateTime, nullable=False, index=True)  # Date of the summary (day)
    total_requests = Column(
        Integer, nullable=False, default=0
    )  # Total number of requests
    successful_requests = Column(
        Integer, nullable=False, default=0
    )  # Number of successful requests (2xx)
    failed_requests = Column(
        Integer, nullable=False, default=0
    )  # Number of failed requests (4xx, 5xx)
    avg_response_time = Column(
        Float, nullable=False, default=0
    )  # Average response time in milliseconds
    total_request_size = Column(
        Integer, nullable=False, default=0
    )  # Total size of requests in bytes
    total_response_size = Column(
        Integer, nullable=False, default=0
    )  # Total size of responses in bytes
    endpoints = Column(
        JSON, nullable=True
    )  # Dictionary of endpoints and request counts

    # Relationships
    api_key = relationship("ApiKey", backref="usage_summaries")

    def __repr__(self):
        return f"<ApiKeyUsageSummary(id={self.id}, api_key_id={self.api_key_id}, date='{self.date}', total_requests={self.total_requests})>"
