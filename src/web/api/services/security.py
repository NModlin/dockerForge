"""
Security services for the DockerForge Web UI.

This module provides services for security-related functionality.
"""
import os
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import asyncio
import docker
from sqlalchemy.orm import Session

from src.web.api.schemas.security import (
    ScanType, ScanStatus, SeverityLevel, 
    ImageScanRequest, ContainerScanRequest,
    ScanResult, ScanResultSummary, Vulnerability,
    RemediationPlan, RemediationStep, RemediationAction,
    SecurityDashboardStats
)
from src.security.vulnerability_scanner import get_vulnerability_scanner
from src.security.config_auditor import get_config_auditor
from src.security.security_reporter import get_security_reporter

# Set up logging
logger = logging.getLogger("api.services.security")

# Initialize Docker client
docker_client = docker.from_env()

# Get vulnerability scanner
vulnerability_scanner = get_vulnerability_scanner()

# Active scans dictionary to track running scans
active_scans = {}


async def scan_image(request: ImageScanRequest) -> str:
    """
    Start an asynchronous image vulnerability scan.
    
    Args:
        request: Image scan request
        
    Returns:
        Scan ID
    """
    scan_id = str(uuid.uuid4())
    
    # Create scan result entry
    scan_result = ScanResult(
        scan_id=scan_id,
        scan_type=ScanType.IMAGE,
        status=ScanStatus.PENDING,
        target=request.image_name,
        started_at=datetime.now(),
        vulnerability_counts={
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 0,
            SeverityLevel.MEDIUM: 0,
            SeverityLevel.LOW: 0,
            SeverityLevel.UNKNOWN: 0
        },
        total_vulnerabilities=0,
        vulnerabilities=[]
    )
    
    # Store scan result
    active_scans[scan_id] = scan_result
    
    # Start scan in background
    asyncio.create_task(_run_image_scan(scan_id, request))
    
    return scan_id


async def scan_container(request: ContainerScanRequest) -> str:
    """
    Start an asynchronous container vulnerability scan.
    
    Args:
        request: Container scan request
        
    Returns:
        Scan ID
    """
    scan_id = str(uuid.uuid4())
    
    # Create scan result entry
    scan_result = ScanResult(
        scan_id=scan_id,
        scan_type=ScanType.CONTAINER,
        status=ScanStatus.PENDING,
        target=request.container_id,
        started_at=datetime.now(),
        vulnerability_counts={
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 0,
            SeverityLevel.MEDIUM: 0,
            SeverityLevel.LOW: 0,
            SeverityLevel.UNKNOWN: 0
        },
        total_vulnerabilities=0,
        vulnerabilities=[]
    )
    
    # Store scan result
    active_scans[scan_id] = scan_result
    
    # Start scan in background
    asyncio.create_task(_run_container_scan(scan_id, request))
    
    return scan_id


async def _run_image_scan(scan_id: str, request: ImageScanRequest) -> None:
    """
    Run an image vulnerability scan.
    
    Args:
        scan_id: Scan ID
        request: Image scan request
    """
    scan_result = active_scans[scan_id]
    scan_result.status = ScanStatus.IN_PROGRESS
    
    try:
        # Convert severity filter to format expected by vulnerability scanner
        severity_filter = None
        if request.severity_filter:
            severity_filter = [s.value for s in request.severity_filter]
        
        # Run scan
        scan_output = vulnerability_scanner.scan_image(
            image_name=request.image_name,
            severity=severity_filter,
            output_format="json",
            ignore_unfixed=request.ignore_unfixed
        )
        
        # Process scan results
        if scan_output.get("success", False) == False:
            scan_result.status = ScanStatus.FAILED
            scan_result.error_message = scan_output.get("error", "Unknown error")
            return
        
        # Extract vulnerabilities
        vulnerabilities = []
        vulnerability_counts = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 0,
            SeverityLevel.MEDIUM: 0,
            SeverityLevel.LOW: 0,
            SeverityLevel.UNKNOWN: 0
        }
        
        # Process Trivy results
        results = scan_output.get("Results", [])
        for result in results:
            for vuln in result.get("Vulnerabilities", []):
                severity = vuln.get("Severity", "UNKNOWN").upper()
                if severity not in [e.value for e in SeverityLevel]:
                    severity = "UNKNOWN"
                
                vulnerability = Vulnerability(
                    vulnerability_id=vuln.get("VulnerabilityID", ""),
                    package_name=vuln.get("PkgName", ""),
                    installed_version=vuln.get("InstalledVersion", ""),
                    fixed_version=vuln.get("FixedVersion"),
                    severity=SeverityLevel(severity),
                    title=vuln.get("Title", ""),
                    description=vuln.get("Description", ""),
                    references=vuln.get("References", []),
                    cve_id=vuln.get("CVEID"),
                    cvss_score=vuln.get("CVSS", {}).get("Score"),
                    cvss_vector=vuln.get("CVSS", {}).get("Vector"),
                    published_date=vuln.get("PublishedDate"),
                    last_modified_date=vuln.get("LastModifiedDate"),
                    is_fixed=bool(vuln.get("FixedVersion"))
                )
                
                vulnerabilities.append(vulnerability)
                vulnerability_counts[SeverityLevel(severity)] += 1
        
        # Update scan result
        scan_result.vulnerabilities = vulnerabilities
        scan_result.vulnerability_counts = vulnerability_counts
        scan_result.total_vulnerabilities = sum(vulnerability_counts.values())
        scan_result.status = ScanStatus.COMPLETED
        scan_result.completed_at = datetime.now()
        scan_result.duration_seconds = (scan_result.completed_at - scan_result.started_at).seconds
        scan_result.raw_output = scan_output
        
    except Exception as e:
        logger.exception(f"Error scanning image {request.image_name}: {str(e)}")
        scan_result.status = ScanStatus.FAILED
        scan_result.error_message = str(e)


async def _run_container_scan(scan_id: str, request: ContainerScanRequest) -> None:
    """
    Run a container vulnerability scan.
    
    Args:
        scan_id: Scan ID
        request: Container scan request
    """
    scan_result = active_scans[scan_id]
    scan_result.status = ScanStatus.IN_PROGRESS
    
    try:
        # Get container
        container = docker_client.containers.get(request.container_id)
        
        # Get container image
        image_id = container.image.id
        image_name = container.image.tags[0] if container.image.tags else image_id
        
        # Convert severity filter to format expected by vulnerability scanner
        severity_filter = None
        if request.severity_filter:
            severity_filter = [s.value for s in request.severity_filter]
        
        # Run scan
        scan_output = vulnerability_scanner.scan_image(
            image_name=image_name,
            severity=severity_filter,
            output_format="json",
            ignore_unfixed=request.ignore_unfixed
        )
        
        # Process scan results
        if scan_output.get("success", False) == False:
            scan_result.status = ScanStatus.FAILED
            scan_result.error_message = scan_output.get("error", "Unknown error")
            return
        
        # Extract vulnerabilities
        vulnerabilities = []
        vulnerability_counts = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 0,
            SeverityLevel.MEDIUM: 0,
            SeverityLevel.LOW: 0,
            SeverityLevel.UNKNOWN: 0
        }
        
        # Process Trivy results
        results = scan_output.get("Results", [])
        for result in results:
            for vuln in result.get("Vulnerabilities", []):
                severity = vuln.get("Severity", "UNKNOWN").upper()
                if severity not in [e.value for e in SeverityLevel]:
                    severity = "UNKNOWN"
                
                vulnerability = Vulnerability(
                    vulnerability_id=vuln.get("VulnerabilityID", ""),
                    package_name=vuln.get("PkgName", ""),
                    installed_version=vuln.get("InstalledVersion", ""),
                    fixed_version=vuln.get("FixedVersion"),
                    severity=SeverityLevel(severity),
                    title=vuln.get("Title", ""),
                    description=vuln.get("Description", ""),
                    references=vuln.get("References", []),
                    cve_id=vuln.get("CVEID"),
                    cvss_score=vuln.get("CVSS", {}).get("Score"),
                    cvss_vector=vuln.get("CVSS", {}).get("Vector"),
                    published_date=vuln.get("PublishedDate"),
                    last_modified_date=vuln.get("LastModifiedDate"),
                    is_fixed=bool(vuln.get("FixedVersion"))
                )
                
                vulnerabilities.append(vulnerability)
                vulnerability_counts[SeverityLevel(severity)] += 1
        
        # Update scan result
        scan_result.vulnerabilities = vulnerabilities
        scan_result.vulnerability_counts = vulnerability_counts
        scan_result.total_vulnerabilities = sum(vulnerability_counts.values())
        scan_result.status = ScanStatus.COMPLETED
        scan_result.completed_at = datetime.now()
        scan_result.duration_seconds = (scan_result.completed_at - scan_result.started_at).seconds
        scan_result.raw_output = scan_output
        
    except Exception as e:
        logger.exception(f"Error scanning container {request.container_id}: {str(e)}")
        scan_result.status = ScanStatus.FAILED
        scan_result.error_message = str(e)


async def get_scan_result(scan_id: str) -> Optional[ScanResult]:
    """
    Get scan result by ID.
    
    Args:
        scan_id: Scan ID
        
    Returns:
        Scan result or None if not found
    """
    return active_scans.get(scan_id)


async def get_scan_results() -> List[ScanResultSummary]:
    """
    Get all scan results.
    
    Returns:
        List of scan result summaries
    """
    return [
        ScanResultSummary(
            scan_id=scan_id,
            scan_type=scan.scan_type,
            status=scan.status,
            target=scan.target,
            started_at=scan.started_at,
            completed_at=scan.completed_at,
            duration_seconds=scan.duration_seconds,
            error_message=scan.error_message,
            vulnerability_counts=scan.vulnerability_counts,
            total_vulnerabilities=scan.total_vulnerabilities
        )
        for scan_id, scan in active_scans.items()
    ]


async def generate_remediation_plan(scan_id: str, vulnerability_id: str) -> Optional[RemediationPlan]:
    """
    Generate a remediation plan for a vulnerability.
    
    Args:
        scan_id: Scan ID
        vulnerability_id: Vulnerability ID
        
    Returns:
        Remediation plan or None if not found
    """
    scan_result = active_scans.get(scan_id)
    if not scan_result:
        return None
    
    # Find vulnerability
    vulnerability = None
    for vuln in scan_result.vulnerabilities:
        if vuln.vulnerability_id == vulnerability_id:
            vulnerability = vuln
            break
    
    if not vulnerability:
        return None
    
    # Generate remediation steps
    steps = []
    
    # If there's a fixed version, recommend updating
    if vulnerability.fixed_version:
        steps.append(
            RemediationStep(
                action=RemediationAction.UPDATE_PACKAGE,
                description=f"Update {vulnerability.package_name} to version {vulnerability.fixed_version}",
                command=f"apt-get update && apt-get install -y {vulnerability.package_name}={vulnerability.fixed_version}"
                if scan_result.target.startswith("debian") or scan_result.target.startswith("ubuntu")
                else None,
                difficulty="EASY",
                estimated_time="5 minutes"
            )
        )
    
    # If it's a base image vulnerability, recommend rebuilding with a newer base
    if vulnerability.package_name in ["base-files", "libc6", "openssl"]:
        steps.append(
            RemediationStep(
                action=RemediationAction.REPLACE_BASE_IMAGE,
                description="Use a newer base image that includes the security fix",
                command=None,
                difficulty="MEDIUM",
                estimated_time="30 minutes"
            )
        )
    
    # If no steps, add a generic rebuild step
    if not steps:
        steps.append(
            RemediationStep(
                action=RemediationAction.REBUILD_IMAGE,
                description="Rebuild the image with updated packages",
                command="docker build --no-cache -t your-image:latest .",
                difficulty="MEDIUM",
                estimated_time="15 minutes"
            )
        )
    
    return RemediationPlan(
        vulnerability_id=vulnerability_id,
        steps=steps,
        notes="These are automated recommendations. Please review before implementing."
    )


async def get_security_dashboard_stats() -> SecurityDashboardStats:
    """
    Get security dashboard statistics.
    
    Returns:
        Security dashboard statistics
    """
    # Calculate security score based on vulnerabilities
    total_vulns = sum(
        sum(scan.vulnerability_counts.values())
        for scan in active_scans.values()
        if scan.status == ScanStatus.COMPLETED
    )
    
    critical_vulns = sum(
        scan.vulnerability_counts.get(SeverityLevel.CRITICAL, 0)
        for scan in active_scans.values()
        if scan.status == ScanStatus.COMPLETED
    )
    
    high_vulns = sum(
        scan.vulnerability_counts.get(SeverityLevel.HIGH, 0)
        for scan in active_scans.values()
        if scan.status == ScanStatus.COMPLETED
    )
    
    # Calculate security score (higher is better)
    # Formula: 100 - (critical_vulns * 10) - (high_vulns * 5)
    security_score = 100 - (critical_vulns * 10) - (high_vulns * 5)
    security_score = max(0, min(100, security_score))  # Clamp between 0 and 100
    
    # Aggregate vulnerability counts
    vulnerability_counts = {
        SeverityLevel.CRITICAL: critical_vulns,
        SeverityLevel.HIGH: high_vulns,
        SeverityLevel.MEDIUM: sum(
            scan.vulnerability_counts.get(SeverityLevel.MEDIUM, 0)
            for scan in active_scans.values()
            if scan.status == ScanStatus.COMPLETED
        ),
        SeverityLevel.LOW: sum(
            scan.vulnerability_counts.get(SeverityLevel.LOW, 0)
            for scan in active_scans.values()
            if scan.status == ScanStatus.COMPLETED
        ),
        SeverityLevel.UNKNOWN: sum(
            scan.vulnerability_counts.get(SeverityLevel.UNKNOWN, 0)
            for scan in active_scans.values()
            if scan.status == ScanStatus.COMPLETED
        )
    }
    
    # Get recent scans
    recent_scans = [
        ScanResultSummary(
            scan_id=scan_id,
            scan_type=scan.scan_type,
            status=scan.status,
            target=scan.target,
            started_at=scan.started_at,
            completed_at=scan.completed_at,
            duration_seconds=scan.duration_seconds,
            error_message=scan.error_message,
            vulnerability_counts=scan.vulnerability_counts,
            total_vulnerabilities=scan.total_vulnerabilities
        )
        for scan_id, scan in sorted(
            active_scans.items(),
            key=lambda x: x[1].started_at,
            reverse=True
        )[:5]  # Get 5 most recent scans
    ]
    
    # Mock compliance stats for now
    compliance_stats = {
        "passed": 42,
        "failed": 8
    }
    
    # Mock recommendations for now
    recommendations = [
        {
            "id": "rec1",
            "title": "Update base images to latest versions",
            "description": "Several images are using outdated base images with known vulnerabilities.",
            "severity": "HIGH",
            "effort": "MEDIUM"
        },
        {
            "id": "rec2",
            "title": "Enable image signing",
            "description": "Enable Docker Content Trust to ensure image integrity.",
            "severity": "MEDIUM",
            "effort": "LOW"
        },
        {
            "id": "rec3",
            "title": "Implement least privilege principle",
            "description": "Run containers with minimal required privileges.",
            "severity": "HIGH",
            "effort": "MEDIUM"
        }
    ]
    
    return SecurityDashboardStats(
        security_score=security_score,
        vulnerability_counts=vulnerability_counts,
        compliance_stats=compliance_stats,
        recent_scans=recent_scans,
        recommendations=recommendations
    )
