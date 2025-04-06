"""
Security policy router for the DockerForge Web UI.

This module provides the API endpoints for security policy management.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.web.api.schemas.security import (
    ComplianceStatus,
    PolicyCreate,
    PolicyEvaluationResult,
    PolicyUpdate,
    PolicyViolation,
    SecurityPolicy,
)
from src.web.api.services import policy as policy_service

# Set up logging
logger = logging.getLogger("api.routers.policy")

# Create router
router = APIRouter()


@router.post(
    "/policies", response_model=SecurityPolicy, status_code=status.HTTP_201_CREATED
)
async def create_policy(policy_create: PolicyCreate):
    """
    Create a new security policy.

    Args:
        policy_create: Policy creation data

    Returns:
        Created security policy
    """
    try:
        policy = await policy_service.create_policy(policy_create)
        return policy
    except Exception as e:
        logger.exception(f"Error creating policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating policy: {str(e)}",
        )


@router.get("/policies", response_model=List[SecurityPolicy])
async def get_policies():
    """
    Get all security policies.

    Returns:
        List of security policies
    """
    try:
        policies = await policy_service.get_policies()
        return policies
    except Exception as e:
        logger.exception(f"Error getting policies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting policies: {str(e)}",
        )


@router.get("/policies/{policy_id}", response_model=SecurityPolicy)
async def get_policy(policy_id: str = Path(..., description="Policy ID")):
    """
    Get a security policy by ID.

    Args:
        policy_id: Policy ID

    Returns:
        Security policy
    """
    try:
        policy = await policy_service.get_policy(policy_id)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with ID {policy_id} not found",
            )
        return policy
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting policy: {str(e)}",
        )


@router.put("/policies/{policy_id}", response_model=SecurityPolicy)
async def update_policy(
    policy_update: PolicyUpdate, policy_id: str = Path(..., description="Policy ID")
):
    """
    Update a security policy.

    Args:
        policy_id: Policy ID
        policy_update: Policy update data

    Returns:
        Updated security policy
    """
    try:
        policy = await policy_service.update_policy(policy_id, policy_update)
        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with ID {policy_id} not found",
            )
        return policy
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating policy: {str(e)}",
        )


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(policy_id: str = Path(..., description="Policy ID")):
    """
    Delete a security policy.

    Args:
        policy_id: Policy ID
    """
    try:
        deleted = await policy_service.delete_policy(policy_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Policy with ID {policy_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting policy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting policy: {str(e)}",
        )


@router.post(
    "/evaluate/{resource_type}/{resource_id}",
    response_model=List[PolicyEvaluationResult],
)
async def evaluate_policies(
    resource_type: str = Path(
        ..., description="Resource type (e.g., 'image', 'container')"
    ),
    resource_id: str = Path(..., description="Resource ID"),
    scan_id: Optional[str] = Query(
        None, description="Optional scan ID for vulnerability evaluation"
    ),
):
    """
    Evaluate all security policies against a resource.

    Args:
        resource_type: Resource type (e.g., "image", "container")
        resource_id: Resource ID
        scan_id: Optional scan ID for vulnerability evaluation

    Returns:
        List of policy evaluation results
    """
    try:
        # Get scan result if scan_id is provided
        scan_result = None
        if scan_id:
            from src.web.api.services import security as security_service

            scan_result = await security_service.get_scan_result(scan_id)
            if not scan_result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Scan with ID {scan_id} not found",
                )

        results = await policy_service.evaluate_all_policies(
            resource_type, resource_id, scan_result
        )
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error evaluating policies: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating policies: {str(e)}",
        )


@router.get("/compliance", response_model=ComplianceStatus)
async def get_compliance_status():
    """
    Get the overall compliance status.

    Returns:
        Compliance status
    """
    try:
        status = await policy_service.get_compliance_status()
        return status
    except Exception as e:
        logger.exception(f"Error getting compliance status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting compliance status: {str(e)}",
        )


@router.get("/violations", response_model=List[PolicyViolation])
async def get_violations(
    policy_id: Optional[str] = Query(None, description="Filter by policy ID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
):
    """
    Get policy violations with optional filtering.

    Args:
        policy_id: Optional policy ID to filter by
        resource_type: Optional resource type to filter by
        resource_id: Optional resource ID to filter by
        resolved: Optional resolved status to filter by

    Returns:
        List of policy violations
    """
    try:
        violations = await policy_service.get_violations(
            policy_id=policy_id,
            resource_type=resource_type,
            resource_id=resource_id,
            resolved=resolved,
        )
        return violations
    except Exception as e:
        logger.exception(f"Error getting violations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting violations: {str(e)}",
        )


@router.get("/violations/{violation_id}", response_model=PolicyViolation)
async def get_violation(violation_id: str = Path(..., description="Violation ID")):
    """
    Get a policy violation by ID.

    Args:
        violation_id: Violation ID

    Returns:
        Policy violation
    """
    try:
        violation = await policy_service.get_violation(violation_id)
        if not violation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Violation with ID {violation_id} not found",
            )
        return violation
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting violation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting violation: {str(e)}",
        )


@router.post("/violations/{violation_id}/resolve", response_model=PolicyViolation)
async def resolve_violation(
    violation_id: str = Path(..., description="Violation ID"),
    resolution_notes: Optional[str] = Query(
        None, description="Optional notes about the resolution"
    ),
):
    """
    Mark a policy violation as resolved.

    Args:
        violation_id: Violation ID
        resolution_notes: Optional notes about the resolution

    Returns:
        Updated policy violation
    """
    try:
        violation = await policy_service.resolve_violation(
            violation_id, resolution_notes
        )
        if not violation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Violation with ID {violation_id} not found",
            )
        return violation
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error resolving violation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving violation: {str(e)}",
        )
