"""
Monitoring schemas for the DockerForge Web UI.

This module provides the Pydantic models for AI monitoring, resource monitoring, and troubleshooting.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

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


# Resource Monitoring Schemas


# CPU Metrics
class CPUMetrics(BaseModel):
    """Schema for CPU metrics."""

    percent: float
    count: int
    physical_count: Optional[int] = None
    per_cpu: List[float]
    load_avg: List[float]
    frequency: Optional[Dict[str, float]] = None
    times: Dict[str, float]


# Memory Metrics
class MemoryDetails(BaseModel):
    """Schema for memory details."""

    total: int
    available: Optional[int] = None
    used: int
    free: int
    percent: float
    active: Optional[int] = None
    inactive: Optional[int] = None
    buffers: Optional[int] = None
    cached: Optional[int] = None
    shared: Optional[int] = None


class MemoryMetrics(BaseModel):
    """Schema for memory metrics."""

    virtual: MemoryDetails
    swap: MemoryDetails


# Disk Metrics
class DiskUsage(BaseModel):
    """Schema for disk usage."""

    total: int
    used: int
    free: int
    percent: float
    device: str
    fstype: str


class DiskIO(BaseModel):
    """Schema for disk I/O."""

    read_bytes: int
    write_bytes: int
    read_count: int
    write_count: int
    read_bytes_rate: float
    write_bytes_rate: float
    read_count_rate: float
    write_count_rate: float
    read_time: Optional[int] = None
    write_time: Optional[int] = None
    busy_time: Optional[int] = None


class DiskMetrics(BaseModel):
    """Schema for disk metrics."""

    usage: Dict[str, DiskUsage]
    io: DiskIO


# Network Metrics
class NetworkAddress(BaseModel):
    """Schema for network address."""

    family: int
    address: str
    netmask: Optional[str] = None
    broadcast: Optional[str] = None
    ptp: Optional[str] = None


class NetworkInterface(BaseModel):
    """Schema for network interface."""

    isup: bool
    duplex: int
    speed: int
    mtu: int
    addresses: List[NetworkAddress]


class NetworkIO(BaseModel):
    """Schema for network I/O."""

    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int
    dropout: int
    bytes_sent_rate: float
    bytes_recv_rate: float
    packets_sent_rate: float
    packets_recv_rate: float


class NetworkMetrics(BaseModel):
    """Schema for network metrics."""

    io: NetworkIO
    interfaces: Dict[str, NetworkInterface]
    connections: Dict[str, int]


# Host Metrics
class HostMetrics(BaseModel):
    """Schema for host metrics."""

    timestamp: str
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics


# System Information
class DockerInfo(BaseModel):
    """Schema for Docker information."""

    version: str
    containers: int
    running: int
    paused: int
    stopped: int
    images: int
    driver: str
    storage_driver: str
    logging_driver: str
    cgroup_driver: str
    kernel_version: str
    operating_system: str
    os_type: str
    architecture: str
    cpus: int
    memory: int
    docker_root_dir: str
    index_server_address: str
    registry_config: Dict[str, Any]


class SystemInfo(BaseModel):
    """Schema for system information."""

    platform: str
    system: str
    release: str
    version: str
    architecture: str
    processor: str
    hostname: str
    python_version: str
    cpu_count: int
    physical_cpu_count: int
    memory_total: int
    boot_time: str
    docker: DockerInfo


# Resource Stats Summary
class ResourceStatsSummary(BaseModel):
    """Schema for resource stats summary."""

    cpu_usage: float
    cpu_cores: int
    memory_usage_percent: float
    memory_used: int
    memory_total: int
    disk_usage_percent: float
    disk_used: int
    disk_total: int
    container_count: int
    running_containers: int
    image_count: int
    volume_count: int
    network_count: int
    containers: Optional[List[Dict[str, Any]]] = None


# Alert Schemas
class AlertSeverity(str):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertMetric(BaseModel):
    """Schema for alert metric."""

    name: str
    value: float
    unit: str


class AlertResource(BaseModel):
    """Schema for alert resource."""

    type: str
    id: str
    name: str


class Alert(BaseModel):
    """Schema for alert."""

    id: str
    title: str
    description: str
    severity: str
    timestamp: str
    acknowledged: bool = False
    resolved: bool = False
    resource: Optional[AlertResource] = None
    metrics: Optional[List[AlertMetric]] = None
