"""
Security schemas for the DockerForge Web UI.

This module provides the Pydantic schemas for security-related functionality.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Severity level for vulnerabilities."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class ScanStatus(str, Enum):
    """Status of a vulnerability scan."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ScanType(str, Enum):
    """Type of vulnerability scan."""

    IMAGE = "IMAGE"
    CONTAINER = "CONTAINER"
    FILESYSTEM = "FILESYSTEM"


class VulnerabilityBase(BaseModel):
    """Base schema for vulnerability information."""

    vulnerability_id: str
    package_name: str
    installed_version: str
    fixed_version: Optional[str] = None
    severity: SeverityLevel
    title: str
    description: Optional[str] = None
    references: Optional[List[str]] = None


class Vulnerability(VulnerabilityBase):
    """Schema for vulnerability with additional details."""

    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    published_date: Optional[datetime] = None
    last_modified_date: Optional[datetime] = None
    remediation: Optional[str] = None
    is_fixed: bool = False


class ScanRequestBase(BaseModel):
    """Base schema for scan requests."""

    scan_type: ScanType = ScanType.IMAGE
    severity_filter: Optional[List[SeverityLevel]] = None
    ignore_unfixed: bool = False


class ImageScanRequest(ScanRequestBase):
    """Schema for image scan requests."""

    image_name: str = Field(..., description="Name of the Docker image to scan")
    image_id: Optional[str] = Field(None, description="ID of the Docker image to scan")


class ContainerScanRequest(ScanRequestBase):
    """Schema for container scan requests."""

    container_id: str = Field(..., description="ID of the Docker container to scan")
    container_name: Optional[str] = Field(
        None, description="Name of the Docker container to scan"
    )


class ScanResultBase(BaseModel):
    """Base schema for scan results."""

    scan_id: str
    scan_type: ScanType
    status: ScanStatus
    target: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None


class ScanResultSummary(ScanResultBase):
    """Schema for scan result summary."""

    vulnerability_counts: Dict[SeverityLevel, int]
    total_vulnerabilities: int


class ScanResult(ScanResultSummary):
    """Schema for detailed scan results."""

    vulnerabilities: List[Vulnerability]
    scanner_version: Optional[str] = None
    scanner_name: str = "Trivy"
    raw_output: Optional[Dict[str, Any]] = None


class RemediationAction(str, Enum):
    """Type of remediation action."""

    UPDATE_PACKAGE = "UPDATE_PACKAGE"
    REBUILD_IMAGE = "REBUILD_IMAGE"
    REPLACE_BASE_IMAGE = "REPLACE_BASE_IMAGE"
    IGNORE_VULNERABILITY = "IGNORE_VULNERABILITY"


class RemediationStep(BaseModel):
    """Schema for remediation steps."""

    action: RemediationAction
    description: str
    command: Optional[str] = None
    difficulty: str = "MEDIUM"  # EASY, MEDIUM, HARD
    estimated_time: Optional[str] = None  # e.g., "5 minutes", "1 hour"


class RemediationPlan(BaseModel):
    """Schema for remediation plan."""

    vulnerability_id: str
    steps: List[RemediationStep]
    notes: Optional[str] = None


class PolicyRuleType(str, Enum):
    """Type of policy rule."""

    SEVERITY = "SEVERITY"
    CVE = "CVE"
    PACKAGE = "PACKAGE"
    IMAGE = "IMAGE"
    CONTAINER = "CONTAINER"
    PRIVILEGED = "PRIVILEGED"
    CAPABILITY = "CAPABILITY"
    VOLUME = "VOLUME"
    PORT = "PORT"
    NETWORK = "NETWORK"


class PolicyAction(str, Enum):
    """Action to take when a policy rule is triggered."""

    BLOCK = "BLOCK"
    WARN = "WARN"
    ALLOW = "ALLOW"
    AUDIT = "AUDIT"


class PolicyRule(BaseModel):
    """Schema for a security policy rule."""

    id: str
    name: str
    description: Optional[str] = None
    rule_type: PolicyRuleType
    pattern: str  # Pattern to match (e.g., "CRITICAL", "CVE-2021-*", "nginx:*")
    action: PolicyAction
    enabled: bool = True


class PolicyCreate(BaseModel):
    """Schema for creating a security policy."""

    name: str
    description: Optional[str] = None
    enabled: bool = True
    rules: List[PolicyRule] = []
    applied_to: List[str] = []  # List of image/container patterns


class PolicyUpdate(BaseModel):
    """Schema for updating a security policy."""

    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    rules: Optional[List[PolicyRule]] = None
    applied_to: Optional[List[str]] = None


class SecurityPolicy(BaseModel):
    """Schema for security policy."""

    id: str
    name: str
    description: Optional[str] = None
    enabled: bool = True
    rules: List[PolicyRule] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    applied_to: List[str] = []  # List of image/container patterns


class PolicyViolation(BaseModel):
    """Schema for a policy violation."""

    id: str
    policy_id: str
    rule_id: str
    resource_type: str  # "image" or "container"
    resource_id: str
    resource_name: str
    description: str
    severity: SeverityLevel
    action_taken: PolicyAction
    created_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class PolicyEvaluationResult(BaseModel):
    """Schema for policy evaluation result."""

    policy_id: str
    policy_name: str
    resource_type: str
    resource_id: str
    resource_name: str
    compliant: bool
    violations: List[PolicyViolation] = []
    evaluation_time: datetime


class ComplianceStatus(BaseModel):
    """Schema for compliance status."""

    total_policies: int
    compliant_policies: int
    non_compliant_policies: int
    total_resources: int
    compliant_resources: int
    non_compliant_resources: int
    policy_violations: List[PolicyViolation] = []
    last_evaluation: Optional[datetime] = None


class SecurityDashboardStats(BaseModel):
    """Schema for security dashboard statistics."""

    security_score: int = Field(..., ge=0, le=100)
    vulnerability_counts: Dict[SeverityLevel, int]
    compliance_stats: Dict[str, int]
    recent_scans: List[ScanResultSummary]
    recommendations: List[Dict[str, Any]]
    compliance_status: Optional[ComplianceStatus] = None
