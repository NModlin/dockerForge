"""
Security policy services for the DockerForge Web UI.

This module provides services for security policy management and enforcement.
"""
import os
import json
import logging
import uuid
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import docker
from sqlalchemy.orm import Session

from src.web.api.schemas.security import (
    SecurityPolicy, PolicyRule, PolicyRuleType, PolicyAction, 
    PolicyCreate, PolicyUpdate, PolicyViolation, PolicyEvaluationResult,
    ComplianceStatus, SeverityLevel, ScanResult
)

# Set up logging
logger = logging.getLogger("api.services.policy")

# Initialize Docker client
docker_client = docker.from_env()

# In-memory storage for policies (in a real app, this would be in a database)
policies: Dict[str, SecurityPolicy] = {}

# In-memory storage for policy violations (in a real app, this would be in a database)
violations: Dict[str, PolicyViolation] = {}


async def create_policy(policy_create: PolicyCreate) -> SecurityPolicy:
    """
    Create a new security policy.
    
    Args:
        policy_create: Policy creation data
        
    Returns:
        Created security policy
    """
    policy_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Generate IDs for rules if they don't have one
    rules = []
    for rule in policy_create.rules:
        if not hasattr(rule, 'id') or not rule.id:
            rule_dict = rule.dict()
            rule_dict['id'] = str(uuid.uuid4())
            rules.append(PolicyRule(**rule_dict))
        else:
            rules.append(rule)
    
    policy = SecurityPolicy(
        id=policy_id,
        name=policy_create.name,
        description=policy_create.description,
        enabled=policy_create.enabled,
        rules=rules,
        created_at=now,
        updated_at=now,
        applied_to=policy_create.applied_to
    )
    
    policies[policy_id] = policy
    return policy


async def get_policy(policy_id: str) -> Optional[SecurityPolicy]:
    """
    Get a security policy by ID.
    
    Args:
        policy_id: Policy ID
        
    Returns:
        Security policy or None if not found
    """
    return policies.get(policy_id)


async def get_policies() -> List[SecurityPolicy]:
    """
    Get all security policies.
    
    Returns:
        List of security policies
    """
    return list(policies.values())


async def update_policy(policy_id: str, policy_update: PolicyUpdate) -> Optional[SecurityPolicy]:
    """
    Update a security policy.
    
    Args:
        policy_id: Policy ID
        policy_update: Policy update data
        
    Returns:
        Updated security policy or None if not found
    """
    policy = await get_policy(policy_id)
    if not policy:
        return None
    
    # Update fields
    update_data = policy_update.dict(exclude_unset=True)
    
    # Handle rules separately
    if 'rules' in update_data:
        rules = []
        for rule in update_data['rules']:
            if not hasattr(rule, 'id') or not rule.id:
                rule['id'] = str(uuid.uuid4())
            rules.append(PolicyRule(**rule))
        update_data['rules'] = rules
    
    # Update the policy
    for key, value in update_data.items():
        setattr(policy, key, value)
    
    policy.updated_at = datetime.now()
    policies[policy_id] = policy
    
    return policy


async def delete_policy(policy_id: str) -> bool:
    """
    Delete a security policy.
    
    Args:
        policy_id: Policy ID
        
    Returns:
        True if the policy was deleted, False otherwise
    """
    if policy_id in policies:
        del policies[policy_id]
        return True
    return False


async def evaluate_policy(policy_id: str, resource_type: str, resource_id: str, scan_result: Optional[ScanResult] = None) -> PolicyEvaluationResult:
    """
    Evaluate a security policy against a resource.
    
    Args:
        policy_id: Policy ID
        resource_type: Resource type (e.g., "image", "container")
        resource_id: Resource ID
        scan_result: Optional scan result for vulnerability evaluation
        
    Returns:
        Policy evaluation result
    """
    policy = await get_policy(policy_id)
    if not policy:
        raise ValueError(f"Policy with ID {policy_id} not found")
    
    # Get resource details
    resource_name = ""
    if resource_type == "image":
        try:
            image = docker_client.images.get(resource_id)
            resource_name = image.tags[0] if image.tags else resource_id[:12]
        except Exception as e:
            logger.error(f"Error getting image {resource_id}: {str(e)}")
            resource_name = resource_id[:12]
    elif resource_type == "container":
        try:
            container = docker_client.containers.get(resource_id)
            resource_name = container.name
        except Exception as e:
            logger.error(f"Error getting container {resource_id}: {str(e)}")
            resource_name = resource_id[:12]
    
    # Initialize result
    result = PolicyEvaluationResult(
        policy_id=policy_id,
        policy_name=policy.name,
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        compliant=True,
        violations=[],
        evaluation_time=datetime.now()
    )
    
    # Skip evaluation if policy is disabled
    if not policy.enabled:
        return result
    
    # Check if the resource is in the applied_to list
    if policy.applied_to and not any(re.match(pattern, resource_name) for pattern in policy.applied_to):
        return result
    
    # Evaluate each rule
    for rule in policy.rules:
        # Skip disabled rules
        if not rule.enabled:
            continue
        
        violation = None
        
        # Evaluate rule based on type
        if rule.rule_type == PolicyRuleType.SEVERITY and scan_result:
            # Check for vulnerabilities with the specified severity
            severity = rule.pattern
            if severity in [s.value for s in SeverityLevel]:
                severity_level = SeverityLevel(severity)
                count = scan_result.vulnerability_counts.get(severity_level, 0)
                if count > 0:
                    violation = PolicyViolation(
                        id=str(uuid.uuid4()),
                        policy_id=policy_id,
                        rule_id=rule.id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        description=f"Found {count} vulnerabilities with severity {severity}",
                        severity=severity_level,
                        action_taken=rule.action,
                        created_at=datetime.now()
                    )
        
        elif rule.rule_type == PolicyRuleType.CVE and scan_result:
            # Check for specific CVEs
            cve_pattern = rule.pattern
            for vuln in scan_result.vulnerabilities:
                if vuln.cve_id and re.match(cve_pattern, vuln.cve_id):
                    violation = PolicyViolation(
                        id=str(uuid.uuid4()),
                        policy_id=policy_id,
                        rule_id=rule.id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        description=f"Found vulnerability {vuln.cve_id} ({vuln.severity})",
                        severity=vuln.severity,
                        action_taken=rule.action,
                        created_at=datetime.now()
                    )
                    break
        
        elif rule.rule_type == PolicyRuleType.PACKAGE and scan_result:
            # Check for specific packages
            package_pattern = rule.pattern
            for vuln in scan_result.vulnerabilities:
                if re.match(package_pattern, vuln.package_name):
                    violation = PolicyViolation(
                        id=str(uuid.uuid4()),
                        policy_id=policy_id,
                        rule_id=rule.id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        description=f"Found vulnerable package {vuln.package_name} ({vuln.severity})",
                        severity=vuln.severity,
                        action_taken=rule.action,
                        created_at=datetime.now()
                    )
                    break
        
        elif rule.rule_type == PolicyRuleType.IMAGE and resource_type == "image":
            # Check image name against pattern
            if re.match(rule.pattern, resource_name):
                violation = PolicyViolation(
                    id=str(uuid.uuid4()),
                    policy_id=policy_id,
                    rule_id=rule.id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=resource_name,
                    description=f"Image {resource_name} matches blocked pattern {rule.pattern}",
                    severity=SeverityLevel.HIGH,
                    action_taken=rule.action,
                    created_at=datetime.now()
                )
        
        elif rule.rule_type == PolicyRuleType.CONTAINER and resource_type == "container":
            # Check container name against pattern
            if re.match(rule.pattern, resource_name):
                violation = PolicyViolation(
                    id=str(uuid.uuid4()),
                    policy_id=policy_id,
                    rule_id=rule.id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=resource_name,
                    description=f"Container {resource_name} matches blocked pattern {rule.pattern}",
                    severity=SeverityLevel.HIGH,
                    action_taken=rule.action,
                    created_at=datetime.now()
                )
        
        elif rule.rule_type == PolicyRuleType.PRIVILEGED and resource_type == "container":
            # Check if container is privileged
            try:
                container = docker_client.containers.get(resource_id)
                inspect_data = container.attrs
                if inspect_data.get('HostConfig', {}).get('Privileged', False):
                    violation = PolicyViolation(
                        id=str(uuid.uuid4()),
                        policy_id=policy_id,
                        rule_id=rule.id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        description="Container is running in privileged mode",
                        severity=SeverityLevel.CRITICAL,
                        action_taken=rule.action,
                        created_at=datetime.now()
                    )
            except Exception as e:
                logger.error(f"Error checking privileged status for container {resource_id}: {str(e)}")
        
        # Add more rule types as needed...
        
        # If a violation was found, add it to the result
        if violation:
            result.violations.append(violation)
            violations[violation.id] = violation
            
            # Mark as non-compliant if action is BLOCK
            if rule.action == PolicyAction.BLOCK:
                result.compliant = False
    
    return result


async def evaluate_all_policies(resource_type: str, resource_id: str, scan_result: Optional[ScanResult] = None) -> List[PolicyEvaluationResult]:
    """
    Evaluate all security policies against a resource.
    
    Args:
        resource_type: Resource type (e.g., "image", "container")
        resource_id: Resource ID
        scan_result: Optional scan result for vulnerability evaluation
        
    Returns:
        List of policy evaluation results
    """
    results = []
    for policy_id in policies:
        result = await evaluate_policy(policy_id, resource_type, resource_id, scan_result)
        results.append(result)
    return results


async def get_compliance_status() -> ComplianceStatus:
    """
    Get the overall compliance status.
    
    Returns:
        Compliance status
    """
    # Get all resources
    images = []
    containers = []
    try:
        images = docker_client.images.list()
        containers = docker_client.containers.list(all=True)
    except Exception as e:
        logger.error(f"Error getting resources: {str(e)}")
    
    # Initialize counters
    total_policies = len(policies)
    compliant_policies = 0
    non_compliant_policies = 0
    total_resources = len(images) + len(containers)
    compliant_resources = 0
    non_compliant_resources = 0
    
    # Track which resources have been evaluated
    evaluated_resources = set()
    
    # Get all violations
    policy_violations = list(violations.values())
    
    # Count non-compliant resources
    for violation in policy_violations:
        resource_key = f"{violation.resource_type}:{violation.resource_id}"
        if resource_key not in evaluated_resources and violation.action_taken == PolicyAction.BLOCK and not violation.resolved:
            non_compliant_resources += 1
            evaluated_resources.add(resource_key)
    
    # Count compliant resources
    compliant_resources = total_resources - non_compliant_resources
    
    # Count compliant/non-compliant policies
    policy_violation_counts = {}
    for violation in policy_violations:
        if violation.action_taken == PolicyAction.BLOCK and not violation.resolved:
            policy_violation_counts[violation.policy_id] = policy_violation_counts.get(violation.policy_id, 0) + 1
    
    non_compliant_policies = len(policy_violation_counts)
    compliant_policies = total_policies - non_compliant_policies
    
    return ComplianceStatus(
        total_policies=total_policies,
        compliant_policies=compliant_policies,
        non_compliant_policies=non_compliant_policies,
        total_resources=total_resources,
        compliant_resources=compliant_resources,
        non_compliant_resources=non_compliant_resources,
        policy_violations=policy_violations,
        last_evaluation=datetime.now() if policy_violations else None
    )


async def get_violation(violation_id: str) -> Optional[PolicyViolation]:
    """
    Get a policy violation by ID.
    
    Args:
        violation_id: Violation ID
        
    Returns:
        Policy violation or None if not found
    """
    return violations.get(violation_id)


async def get_violations(
    policy_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    resolved: Optional[bool] = None
) -> List[PolicyViolation]:
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
    filtered_violations = list(violations.values())
    
    if policy_id:
        filtered_violations = [v for v in filtered_violations if v.policy_id == policy_id]
    
    if resource_type:
        filtered_violations = [v for v in filtered_violations if v.resource_type == resource_type]
    
    if resource_id:
        filtered_violations = [v for v in filtered_violations if v.resource_id == resource_id]
    
    if resolved is not None:
        filtered_violations = [v for v in filtered_violations if v.resolved == resolved]
    
    return filtered_violations


async def resolve_violation(violation_id: str, resolution_notes: Optional[str] = None) -> Optional[PolicyViolation]:
    """
    Mark a policy violation as resolved.
    
    Args:
        violation_id: Violation ID
        resolution_notes: Optional notes about the resolution
        
    Returns:
        Updated policy violation or None if not found
    """
    violation = await get_violation(violation_id)
    if not violation:
        return None
    
    violation.resolved = True
    violation.resolved_at = datetime.now()
    violation.resolution_notes = resolution_notes
    
    violations[violation_id] = violation
    return violation


# Initialize with some default policies
async def initialize_default_policies():
    """Initialize default security policies."""
    # Only initialize if no policies exist
    if policies:
        return
    
    # Create default policies
    await create_policy(PolicyCreate(
        name="Block Critical Vulnerabilities",
        description="Block images and containers with critical vulnerabilities",
        enabled=True,
        rules=[
            PolicyRule(
                id=str(uuid.uuid4()),
                name="Block Critical Vulnerabilities",
                description="Block images and containers with critical vulnerabilities",
                rule_type=PolicyRuleType.SEVERITY,
                pattern="CRITICAL",
                action=PolicyAction.BLOCK,
                enabled=True
            )
        ],
        applied_to=[]  # Apply to all resources
    ))
    
    await create_policy(PolicyCreate(
        name="Block Privileged Containers",
        description="Block containers running in privileged mode",
        enabled=True,
        rules=[
            PolicyRule(
                id=str(uuid.uuid4()),
                name="Block Privileged Containers",
                description="Block containers running in privileged mode",
                rule_type=PolicyRuleType.PRIVILEGED,
                pattern="true",
                action=PolicyAction.BLOCK,
                enabled=True
            )
        ],
        applied_to=[]  # Apply to all resources
    ))
    
    await create_policy(PolicyCreate(
        name="Warn on High Vulnerabilities",
        description="Warn about images and containers with high vulnerabilities",
        enabled=True,
        rules=[
            PolicyRule(
                id=str(uuid.uuid4()),
                name="Warn on High Vulnerabilities",
                description="Warn about images and containers with high vulnerabilities",
                rule_type=PolicyRuleType.SEVERITY,
                pattern="HIGH",
                action=PolicyAction.WARN,
                enabled=True
            )
        ],
        applied_to=[]  # Apply to all resources
    ))
