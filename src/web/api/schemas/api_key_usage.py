"""
API key usage schemas for the DockerForge Web UI.

This module provides the Pydantic schemas for API key usage.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApiKeyUsageBase(BaseModel):
    """
    Base schema for API key usage.
    """

    api_key_id: int = Field(..., description="API key ID")
    endpoint: str = Field(..., description="API endpoint that was accessed")
    method: str = Field(..., description="HTTP method (GET, POST, etc.)")
    status_code: int = Field(..., description="HTTP status code")
    response_time: float = Field(..., description="Response time in milliseconds")
    request_size: Optional[int] = Field(
        None, description="Size of the request in bytes"
    )
    response_size: Optional[int] = Field(
        None, description="Size of the response in bytes"
    )
    ip_address: Optional[str] = Field(None, description="IP address of the client")
    user_agent: Optional[str] = Field(None, description="User agent of the client")


class ApiKeyUsageCreate(ApiKeyUsageBase):
    """
    Schema for creating API key usage records.
    """

    pass


class ApiKeyUsageResponse(ApiKeyUsageBase):
    """
    Schema for API key usage responses.
    """

    id: int = Field(..., description="Usage record ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        orm_mode = True


class ApiKeyUsageSummaryBase(BaseModel):
    """
    Base schema for API key usage summary.
    """

    api_key_id: int = Field(..., description="API key ID")
    date: date = Field(..., description="Date of the summary")
    total_requests: int = Field(..., description="Total number of requests")
    successful_requests: int = Field(
        ..., description="Number of successful requests (2xx)"
    )
    failed_requests: int = Field(
        ..., description="Number of failed requests (4xx, 5xx)"
    )
    avg_response_time: float = Field(
        ..., description="Average response time in milliseconds"
    )
    total_request_size: int = Field(..., description="Total size of requests in bytes")
    total_response_size: int = Field(
        ..., description="Total size of responses in bytes"
    )
    endpoints: Optional[Dict[str, int]] = Field(
        None, description="Dictionary of endpoints and request counts"
    )


class ApiKeyUsageSummaryResponse(ApiKeyUsageSummaryBase):
    """
    Schema for API key usage summary responses.
    """

    id: int = Field(..., description="Summary record ID")

    class Config:
        orm_mode = True


class ApiKeyUsageStats(BaseModel):
    """
    Schema for API key usage statistics.
    """

    total_requests: int = Field(..., description="Total number of requests")
    requests_today: int = Field(..., description="Number of requests today")
    requests_this_week: int = Field(..., description="Number of requests this week")
    requests_this_month: int = Field(..., description="Number of requests this month")
    avg_response_time: float = Field(
        ..., description="Average response time in milliseconds"
    )
    success_rate: float = Field(..., description="Success rate (percentage)")
    top_endpoints: List[Dict[str, Any]] = Field(
        ..., description="Top endpoints by request count"
    )
    usage_over_time: List[Dict[str, Any]] = Field(
        ..., description="Usage over time (daily)"
    )


class ApiKeyUsageQuery(BaseModel):
    """
    Schema for querying API key usage.
    """

    start_date: Optional[date] = Field(None, description="Start date for filtering")
    end_date: Optional[date] = Field(None, description="End date for filtering")
    endpoint: Optional[str] = Field(None, description="Filter by endpoint")
    method: Optional[str] = Field(None, description="Filter by HTTP method")
    status_code: Optional[int] = Field(None, description="Filter by status code")
    limit: Optional[int] = Field(50, description="Limit the number of results")
    offset: Optional[int] = Field(0, description="Offset for pagination")
