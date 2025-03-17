"""
Monitoring schemas for the DockerForge Web UI.

This module provides the Pydantic models for AI monitoring and troubleshooting.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


# AI Provider Status Schemas
class AICapabilities(BaseModel):
    """Schema for AI provider capabilities."""
    streaming: bool = False
    vision: bool = False
    batching: bool = False
    function_calling: bool = False
    token_counting: bool = False
    free_to_use: Optional[bool] = False
    local_execution: Optional[bool] = False


class AIProviderStatus(BaseModel):
    """Schema for AI provider status."""
    name: str
    enabled: bool
    available: bool
    type: str  # built-in or plugin
    model: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[AICapabilities] = None


class AIStatusResponse(BaseModel):
    """Schema for AI status response."""
    providers: Dict[str, AIProviderStatus]
    default_provider: str


# AI Usage Schemas
class AIModelUsage(BaseModel):
    """Schema for AI model usage."""
    input_tokens: int
    output_tokens: int
    cost_usd: float


class AIProviderUsage(BaseModel):
    """Schema for AI provider usage."""
    models: Dict[str, AIModelUsage]
    total_cost_usd: float


class AIUsageStats(BaseModel):
    """Schema for AI usage statistics."""
    date: str
    providers: Dict[str, AIProviderUsage]
    total_cost_usd: float


class AIBudgetStatus(BaseModel):
    """Schema for AI budget status."""
    year: int
    month: int
    providers: Dict[str, Dict[str, float]]
    total_usage_usd: float
    total_budget_usd: float
    total_remaining_usd: float
    total_percentage: float


class AIUsageReport(BaseModel):
    """Schema for AI usage report."""
    date: str
    daily_usage: AIUsageStats
    monthly_usage: Dict[str, Any]
    budget_status: AIBudgetStatus
    days_in_month: int
    days_passed: int
    days_remaining: int
    daily_average_usd: float
    projected_total_usd: float
    budget_remaining_usd: float
    budget_percentage: float
    projected_percentage: float


# Troubleshooting Schemas
class TroubleshootingRequest(BaseModel):
    """Base schema for troubleshooting requests."""
    confirm_cost: bool = True


class ContainerTroubleshootingRequest(TroubleshootingRequest):
    """Schema for container troubleshooting requests."""
    container_id: str


class LogsTroubleshootingRequest(TroubleshootingRequest):
    """Schema for logs troubleshooting requests."""
    logs: str


class DockerComposeRequest(TroubleshootingRequest):
    """Schema for Docker Compose troubleshooting requests."""
    content: str


class DockerfileRequest(TroubleshootingRequest):
    """Schema for Dockerfile troubleshooting requests."""
    content: str


class TroubleshootingResult(BaseModel):
    """Schema for troubleshooting results."""
    analysis: str
    provider: str
    model: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ContainerTroubleshootingResult(TroubleshootingResult):
    """Schema for container troubleshooting results."""
    container_id: str
    container_name: str
    container_status: str


class ConnectionTroubleshootingResult(BaseModel):
    """Schema for connection troubleshooting results."""
    connected: bool
    issues: List[str]
    fixes: List[str]
