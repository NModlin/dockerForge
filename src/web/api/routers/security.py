"""
Security router for the DockerForge Web UI.

This module provides the API endpoints for security-related functionality.
"""

import logging
from typing import List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)

from src.web.api.schemas.security import (
    ContainerScanRequest,
    ImageScanRequest,
    RemediationPlan,
    ScanResult,
    ScanResultSummary,
    ScanStatus,
    ScanType,
    SecurityDashboardStats,
    SeverityLevel,
    Vulnerability,
)
from src.web.api.services import security as security_service

# Set up logging
logger = logging.getLogger("api.routers.security")

# Create router
router = APIRouter()


@router.post("/scan/image", response_model=str, status_code=status.HTTP_202_ACCEPTED)
async def scan_image(request: ImageScanRequest):
    """
    Start an image vulnerability scan.

    Args:
        request: Image scan request

    Returns:
        Scan ID
    """
    try:
        scan_id = await security_service.scan_image(request)
        return scan_id
    except Exception as e:
        logger.exception(f"Error scanning image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scanning image: {str(e)}",
        )


@router.post(
    "/scan/container", response_model=str, status_code=status.HTTP_202_ACCEPTED
)
async def scan_container(request: ContainerScanRequest):
    """
    Start a container vulnerability scan.

    Args:
        request: Container scan request

    Returns:
        Scan ID
    """
    try:
        scan_id = await security_service.scan_container(request)
        return scan_id
    except Exception as e:
        logger.exception(f"Error scanning container: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scanning container: {str(e)}",
        )


@router.get("/scan/{scan_id}", response_model=ScanResult)
async def get_scan_result(scan_id: str = Path(..., description="Scan ID")):
    """
    Get scan result by ID.

    Args:
        scan_id: Scan ID

    Returns:
        Scan result
    """
    try:
        scan_result = await security_service.get_scan_result(scan_id)
        if not scan_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan with ID {scan_id} not found",
            )
        return scan_result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting scan result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting scan result: {str(e)}",
        )


@router.get("/scans", response_model=List[ScanResultSummary])
async def get_scan_results():
    """
    Get all scan results.

    Returns:
        List of scan result summaries
    """
    try:
        scan_results = await security_service.get_scan_results()
        return scan_results
    except Exception as e:
        logger.exception(f"Error getting scan results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting scan results: {str(e)}",
        )


@router.get("/remediation/{scan_id}/{vulnerability_id}", response_model=RemediationPlan)
async def get_remediation_plan(
    scan_id: str = Path(..., description="Scan ID"),
    vulnerability_id: str = Path(..., description="Vulnerability ID"),
):
    """
    Get remediation plan for a vulnerability.

    Args:
        scan_id: Scan ID
        vulnerability_id: Vulnerability ID

    Returns:
        Remediation plan
    """
    try:
        remediation_plan = await security_service.generate_remediation_plan(
            scan_id, vulnerability_id
        )
        if not remediation_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vulnerability with ID {vulnerability_id} not found in scan {scan_id}",
            )
        return remediation_plan
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating remediation plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating remediation plan: {str(e)}",
        )


@router.get("/dashboard", response_model=SecurityDashboardStats)
async def get_security_dashboard():
    """
    Get security dashboard statistics.

    Returns:
        Security dashboard statistics
    """
    try:
        dashboard_stats = await security_service.get_security_dashboard_stats()
        return dashboard_stats
    except Exception as e:
        logger.exception(f"Error getting security dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting security dashboard: {str(e)}",
        )
