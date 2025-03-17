"""
Fix proposal module for DockerForge.

This module provides functionality for proposing fixes for Docker-related issues.
"""

import os
import json
import logging
import threading
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.notifications.notification_manager import get_notification_manager, Notification, NotificationSeverity, NotificationType

# Set up logging
logger = get_logger("fix_proposal")


class FixRiskLevel(Enum):
    """Fix risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FixStatus(Enum):
    """Fix status values."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class FixStep:
    """A step in a fix proposal."""
    
    def __init__(
        self,
        title: str,
        description: str,
        command: Optional[str] = None,
        code: Optional[str] = None,
        file_path: Optional[str] = None,
        manual_action: Optional[str] = None,
        verification: Optional[str] = None,
    ):
        """Initialize a fix step.
        
        Args:
            title: The step title
            description: The step description
            command: Optional command to execute
            code: Optional code to apply
            file_path: Optional file path to modify
            manual_action: Optional manual action to take
            verification: Optional verification step
        """
        self.title = title
        self.description = description
        self.command = command
        self.code = code
        self.file_path = file_path
        self.manual_action = manual_action
        self.verification = verification
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the fix step to a dictionary.
        
        Returns:
            A dictionary representation of the fix step
        """
        return {
            "title": self.title,
            "description": self.description,
            "command": self.command,
            "code": self.code,
            "file_path": self.file_path,
            "manual_action": self.manual_action,
            "verification": self.verification,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FixStep':
        """Create a fix step from a dictionary.
        
        Args:
            data: The dictionary to create the fix step from
            
        Returns:
            A new FixStep instance
        """
        return cls(
            title=data["title"],
            description=data["description"],
            command=data.get("command"),
            code=data.get("code"),
            file_path=data.get("file_path"),
            manual_action=data.get("manual_action"),
            verification=data.get("verification"),
        )


class FixProposal:
    """A fix proposal for a Docker-related issue."""
    
    def __init__(
        self,
        issue_id: str,
        title: str,
        description: str,
        steps: List[FixStep],
        risk_level: FixRiskLevel = FixRiskLevel.MEDIUM,
        container_id: Optional[str] = None,
        container_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a fix proposal.
        
        Args:
            issue_id: The issue ID
            title: The fix title
            description: The fix description
            steps: The fix steps
            risk_level: The fix risk level
            container_id: Optional container ID
            container_name: Optional container name
            metadata: Optional metadata
        """
        self.id = f"fix_{uuid.uuid4().hex[:12]}"
        self.issue_id = issue_id
        self.title = title
        self.description = description
        self.steps = steps
        self.risk_level = risk_level
        self.container_id = container_id
        self.container_name = container_name
        self.metadata = metadata or {}
        self.status = FixStatus.PROPOSED
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.approved_at = None
        self.approved_by = None
        self.rejected_at = None
        self.rejected_by = None
        self.applied_at = None
        self.result = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the fix proposal to a dictionary.
        
        Returns:
            A dictionary representation of the fix proposal
        """
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "title": self.title,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "risk_level": self.risk_level.value,
            "container_id": self.container_id,
            "container_name": self.container_name,
            "metadata": self.metadata,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None,
            "rejected_by": self.rejected_by,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "result": self.result,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FixProposal':
        """Create a fix proposal from a dictionary.
        
        Args:
            data: The dictionary to create the fix proposal from
            
        Returns:
            A new FixProposal instance
        """
        fix = cls(
            issue_id=data["issue_id"],
            title=data["title"],
            description=data["description"],
            steps=[FixStep.from_dict(step) for step in data["steps"]],
            risk_level=FixRiskLevel(data["risk_level"]),
            container_id=data.get("container_id"),
            container_name=data.get("container_name"),
            metadata=data.get("metadata", {}),
        )
        
        fix.id = data["id"]
        fix.status = FixStatus(data["status"])
        fix.created_at = datetime.fromisoformat(data["created_at"])
        fix.updated_at = datetime.fromisoformat(data["updated_at"])
        
        if data.get("approved_at"):
            fix.approved_at = datetime.fromisoformat(data["approved_at"])
        
        fix.approved_by = data.get("approved_by")
        
        if data.get("rejected_at"):
            fix.rejected_at = datetime.fromisoformat(data["rejected_at"])
        
        fix.rejected_by = data.get("rejected_by")
        
        if data.get("applied_at"):
            fix.applied_at = datetime.fromisoformat(data["applied_at"])
        
        fix.result = data.get("result")
        
        return fix
    
    def approve(self, user: Optional[str] = None) -> None:
        """Approve the fix proposal.
        
        Args:
            user: Optional user who approved the fix
        """
        self.status = FixStatus.APPROVED
        self.approved_at = datetime.now()
        self.approved_by = user
        self.updated_at = datetime.now()
    
    def reject(self, user: Optional[str] = None) -> None:
        """Reject the fix proposal.
        
        Args:
            user: Optional user who rejected the fix
        """
        self.status = FixStatus.REJECTED
        self.rejected_at = datetime.now()
        self.rejected_by = user
        self.updated_at = datetime.now()
    
    def mark_as_applied(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark the fix as applied.
        
        Args:
            result: Optional result of applying the fix
        """
        self.status = FixStatus.APPLIED
        self.applied_at = datetime.now()
        self.result = result
        self.updated_at = datetime.now()
    
    def mark_as_failed(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark the fix as failed.
        
        Args:
            result: Optional result of the failed fix
        """
        self.status = FixStatus.FAILED
        self.result = result
        self.updated_at = datetime.now()
    
    def mark_as_rolled_back(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark the fix as rolled back.
        
        Args:
            result: Optional result of rolling back the fix
        """
        self.status = FixStatus.ROLLED_BACK
        self.result = result
        self.updated_at = datetime.now()
    
    def send_notification(self) -> bool:
        """Send a notification for this fix proposal.
        
        Returns:
            True if the notification was sent, False otherwise
        """
        notification_manager = get_notification_manager()
        
        # Create notification
        notification = Notification(
            title=f"Fix Proposal: {self.title}",
            message=self.description,
            severity=NotificationSeverity.WARNING,
            notification_type=NotificationType.FIX_PROPOSAL,
            container_id=self.container_id,
            container_name=self.container_name,
            issue_id=self.issue_id,
            fix_id=self.id,
            metadata={
                "template_id": "fix_proposal",
                "risk_level": self.risk_level.value,
                "fix_steps": [step.to_dict() for step in self.steps],
                "issue_title": self.metadata.get("issue_title", "Unknown Issue"),
                "issue_description": self.metadata.get("issue_description", ""),
            },
            actions=[
                {
                    "label": "Approve Fix",
                    "url": f"/api/fixes/{self.id}/approve",
                },
                {
                    "label": "Reject Fix",
                    "url": f"/api/fixes/{self.id}/reject",
                },
                {
                    "label": "View Details",
                    "url": f"/fixes/{self.id}",
                },
            ],
        )
        
        # Send notification
        return notification_manager.send_notification(notification)


class FixProposalManager:
    """Manager for fix proposals."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Create a new FixProposalManager instance (singleton)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FixProposalManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the fix proposal manager."""
        if self._initialized:
            return
        
        self._initialized = True
        self._fixes = {}
        
        # Load fixes
        self._load_fixes()
        
        logger.info("Fix proposal manager initialized")
    
    def _get_fixes_dir(self) -> str:
        """Get the fixes directory.
        
        Returns:
            The fixes directory path
        """
        data_dir = os.path.expanduser(get_config("general.data_dir"))
        fixes_dir = os.path.join(data_dir, "fixes")
        
        if not os.path.exists(fixes_dir):
            os.makedirs(fixes_dir, exist_ok=True)
        
        return fixes_dir
    
    def _load_fixes(self) -> None:
        """Load fixes from disk."""
        fixes_dir = self._get_fixes_dir()
        
        # Load fixes from JSON files
        for filename in os.listdir(fixes_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(fixes_dir, filename), "r") as f:
                        data = json.load(f)
                        fix = FixProposal.from_dict(data)
                        self._fixes[fix.id] = fix
                except Exception as e:
                    logger.error(f"Error loading fix {filename}: {str(e)}")
        
        logger.info(f"Loaded {len(self._fixes)} fixes")
    
    def _save_fix(self, fix: FixProposal) -> None:
        """Save a fix to disk.
        
        Args:
            fix: The fix to save
        """
        fixes_dir = self._get_fixes_dir()
        
        try:
            filename = os.path.join(fixes_dir, f"{fix.id}.json")
            
            with open(filename, "w") as f:
                json.dump(fix.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving fix {fix.id}: {str(e)}")
    
    def create_fix(
        self,
        issue_id: str,
        title: str,
        description: str,
        steps: List[FixStep],
        risk_level: Union[FixRiskLevel, str] = FixRiskLevel.MEDIUM,
        container_id: Optional[str] = None,
        container_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        send_notification: bool = True,
    ) -> FixProposal:
        """Create a new fix proposal.
        
        Args:
            issue_id: The issue ID
            title: The fix title
            description: The fix description
            steps: The fix steps
            risk_level: The fix risk level
            container_id: Optional container ID
            container_name: Optional container name
            metadata: Optional metadata
            send_notification: Whether to send a notification
            
        Returns:
            The created fix proposal
        """
        # Convert string risk level to enum if needed
        if isinstance(risk_level, str):
            risk_level = FixRiskLevel(risk_level)
        
        # Create fix
        fix = FixProposal(
            issue_id=issue_id,
            title=title,
            description=description,
            steps=steps,
            risk_level=risk_level,
            container_id=container_id,
            container_name=container_name,
            metadata=metadata,
        )
        
        # Add to fixes
        self._fixes[fix.id] = fix
        
        # Save to disk
        self._save_fix(fix)
        
        logger.info(f"Created fix proposal: {fix.id} - {fix.title}")
        
        # Send notification if requested
        if send_notification:
            if fix.send_notification():
                logger.info(f"Sent notification for fix proposal: {fix.id}")
            else:
                logger.warning(f"Failed to send notification for fix proposal: {fix.id}")
        
        return fix
    
    def get_fix(self, fix_id: str) -> Optional[FixProposal]:
        """Get a fix by ID.
        
        Args:
            fix_id: The fix ID
            
        Returns:
            The fix if found, None otherwise
        """
        return self._fixes.get(fix_id)
    
    def get_fixes_for_issue(self, issue_id: str) -> List[FixProposal]:
        """Get fixes for an issue.
        
        Args:
            issue_id: The issue ID
            
        Returns:
            List of fixes for the issue
        """
        return [fix for fix in self._fixes.values() if fix.issue_id == issue_id]
    
    def get_fixes_for_container(self, container_id: str) -> List[FixProposal]:
        """Get fixes for a container.
        
        Args:
            container_id: The container ID
            
        Returns:
            List of fixes for the container
        """
        return [fix for fix in self._fixes.values() if fix.container_id == container_id]
    
    def get_all_fixes(self, status: Optional[FixStatus] = None) -> List[FixProposal]:
        """Get all fixes.
        
        Args:
            status: Optional status to filter by
            
        Returns:
            List of all fixes
        """
        if status:
            return [fix for fix in self._fixes.values() if fix.status == status]
        else:
            return list(self._fixes.values())
    
    def approve_fix(self, fix_id: str, user: Optional[str] = None) -> bool:
        """Approve a fix.
        
        Args:
            fix_id: The fix ID
            user: Optional user who approved the fix
            
        Returns:
            True if the fix was approved, False otherwise
        """
        fix = self.get_fix(fix_id)
        
        if not fix:
            logger.warning(f"Fix not found: {fix_id}")
            return False
        
        if fix.status != FixStatus.PROPOSED:
            logger.warning(f"Fix {fix_id} is not in PROPOSED state: {fix.status.value}")
            return False
        
        # Approve fix
        fix.approve(user)
        
        # Save to disk
        self._save_fix(fix)
        
        logger.info(f"Approved fix: {fix_id}")
        
        # Send notification
        notification_manager = get_notification_manager()
        notification = Notification(
            title=f"Fix Approved: {fix.title}",
            message=f"The fix proposal has been approved{' by ' + user if user else ''}.",
            severity=NotificationSeverity.INFO,
            notification_type=NotificationType.FIX_PROPOSAL,
            container_id=fix.container_id,
            container_name=fix.container_name,
            issue_id=fix.issue_id,
            fix_id=fix.id,
            actions=[
                {
                    "label": "View Details",
                    "url": f"/fixes/{fix.id}",
                },
            ],
        )
        
        notification_manager.send_notification(notification)
        
        return True
    
    def reject_fix(self, fix_id: str, user: Optional[str] = None, reason: Optional[str] = None) -> bool:
        """Reject a fix.
        
        Args:
            fix_id: The fix ID
            user: Optional user who rejected the fix
            reason: Optional reason for rejection
            
        Returns:
            True if the fix was rejected, False otherwise
        """
        fix = self.get_fix(fix_id)
        
        if not fix:
            logger.warning(f"Fix not found: {fix_id}")
            return False
        
        if fix.status != FixStatus.PROPOSED:
            logger.warning(f"Fix {fix_id} is not in PROPOSED state: {fix.status.value}")
            return False
        
        # Reject fix
        fix.reject(user)
        
        # Add reason to metadata if provided
        if reason:
            fix.metadata["rejection_reason"] = reason
        
        # Save to disk
        self._save_fix(fix)
        
        logger.info(f"Rejected fix: {fix_id}")
        
        # Send notification
        notification_manager = get_notification_manager()
        notification = Notification(
            title=f"Fix Rejected: {fix.title}",
            message=f"The fix proposal has been rejected{' by ' + user if user else ''}.{' Reason: ' + reason if reason else ''}",
            severity=NotificationSeverity.WARNING,
            notification_type=NotificationType.FIX_PROPOSAL,
            container_id=fix.container_id,
            container_name=fix.container_name,
            issue_id=fix.issue_id,
            fix_id=fix.id,
            actions=[
                {
                    "label": "View Details",
                    "url": f"/fixes/{fix.id}",
                },
            ],
        )
        
        notification_manager.send_notification(notification)
        
        return True
    
    def update_fix_status(self, fix_id: str, status: FixStatus, result: Optional[Dict[str, Any]] = None) -> bool:
        """Update a fix status.
        
        Args:
            fix_id: The fix ID
            status: The new status
            result: Optional result data
            
        Returns:
            True if the fix status was updated, False otherwise
        """
        fix = self.get_fix(fix_id)
        
        if not fix:
            logger.warning(f"Fix not found: {fix_id}")
            return False
        
        # Update status
        if status == FixStatus.APPLIED:
            fix.mark_as_applied(result)
        elif status == FixStatus.FAILED:
            fix.mark_as_failed(result)
        elif status == FixStatus.ROLLED_BACK:
            fix.mark_as_rolled_back(result)
        else:
            fix.status = status
            fix.updated_at = datetime.now()
            if result:
                fix.result = result
        
        # Save to disk
        self._save_fix(fix)
        
        logger.info(f"Updated fix status: {fix_id} -> {status.value}")
        
        # Send notification
        notification_manager = get_notification_manager()
        
        if status == FixStatus.APPLIED:
            notification = Notification(
                title=f"Fix Applied: {fix.title}",
                message="The fix has been successfully applied.",
                severity=NotificationSeverity.INFO,
                notification_type=NotificationType.FIX_APPLIED,
                container_id=fix.container_id,
                container_name=fix.container_name,
                issue_id=fix.issue_id,
                fix_id=fix.id,
                actions=[
                    {
                        "label": "View Details",
                        "url": f"/fixes/{fix.id}",
                    },
                ],
            )
        elif status == FixStatus.FAILED:
            notification = Notification(
                title=f"Fix Failed: {fix.title}",
                message="The fix application failed.",
                severity=NotificationSeverity.ERROR,
                notification_type=NotificationType.FIX_APPLIED,
                container_id=fix.container_id,
                container_name=fix.container_name,
                issue_id=fix.issue_id,
                fix_id=fix.id,
                actions=[
                    {
                        "label": "View Details",
                        "url": f"/fixes/{fix.id}",
                    },
                ],
            )
        elif status == FixStatus.ROLLED_BACK:
            notification = Notification(
                title=f"Fix Rolled Back: {fix.title}",
                message="The fix has been rolled back.",
                severity=NotificationSeverity.WARNING,
                notification_type=NotificationType.FIX_APPLIED,
                container_id=fix.container_id,
                container_name=fix.container_name,
                issue_id=fix.issue_id,
                fix_id=fix.id,
                actions=[
                    {
                        "label": "View Details",
                        "url": f"/fixes/{fix.id}",
                    },
                ],
            )
        else:
            # No notification for other status changes
            return True
        
        notification_manager.send_notification(notification)
        
        return True
    
    def delete_fix(self, fix_id: str) -> bool:
        """Delete a fix.
        
        Args:
            fix_id: The fix ID
            
        Returns:
            True if the fix was deleted, False otherwise
        """
        if fix_id not in self._fixes:
            logger.warning(f"Fix not found: {fix_id}")
            return False
        
        # Remove from fixes
        del self._fixes[fix_id]
        
        # Remove from disk
        fixes_dir = self._get_fixes_dir()
        filename = os.path.join(fixes_dir, f"{fix_id}.json")
        
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e:
                logger.error(f"Error deleting fix file: {str(e)}")
                return False
        
        logger.info(f"Deleted fix: {fix_id}")
        
        return True


def get_fix_proposal_manager() -> FixProposalManager:
    """Get the fix proposal manager instance.
    
    Returns:
        The fix proposal manager instance
    """
    return FixProposalManager()
