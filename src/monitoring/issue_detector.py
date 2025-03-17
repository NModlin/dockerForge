"""
Issue detector module for DockerForge.

This module provides functionality to detect and classify issues in container logs,
based on pattern matches and AI analysis.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum, auto

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.monitoring.log_collector import LogEntry, get_log_collection_manager
from src.monitoring.pattern_recognition import (
    PatternMatch, PatternDefinition, get_pattern_recognition_engine
)
from src.monitoring.log_analyzer import AnalysisResult, get_log_analyzer

logger = get_logger("issue_detector")


class IssueSeverity(Enum):
    """Severity levels for issues."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    @classmethod
    def from_string(cls, value: str) -> "IssueSeverity":
        """
        Create severity from string.
        
        Args:
            value: String value
            
        Returns:
            IssueSeverity: Severity level
        """
        try:
            return cls(value.lower())
        except ValueError:
            # Default to INFO for unknown values
            return cls.INFO


class IssueStatus(Enum):
    """Status of an issue."""
    
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class Issue:
    """Detected issue in a container."""
    
    id: str
    container_id: str
    container_name: str
    title: str
    description: str
    severity: IssueSeverity
    status: IssueStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    source: str = "pattern"  # pattern, analysis, manual
    pattern_id: Optional[str] = None
    pattern_matches: List[Dict[str, Any]] = field(default_factory=list)
    analysis_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    assignee: Optional[str] = None
    notes: List[Dict[str, Any]] = field(default_factory=list)
    related_issues: List[str] = field(default_factory=list)
    resolution: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert issue to dictionary.
        
        Returns:
            Dict[str, Any]: Issue as dictionary
        """
        result = asdict(self)
        result["severity"] = self.severity.value
        result["status"] = self.status.value
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        if self.resolved_at:
            result["resolved_at"] = self.resolved_at.isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Issue":
        """
        Create issue from dictionary.
        
        Args:
            data: Dictionary with issue data
            
        Returns:
            Issue: Issue
        """
        data = data.copy()
        data["severity"] = IssueSeverity.from_string(data["severity"])
        data["status"] = IssueStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("resolved_at"):
            data["resolved_at"] = datetime.fromisoformat(data["resolved_at"])
        
        return cls(**data)
    
    def update_status(self, status: IssueStatus) -> None:
        """
        Update issue status.
        
        Args:
            status: New status
        """
        self.status = status
        self.updated_at = datetime.now()
        
        if status == IssueStatus.RESOLVED:
            self.resolved_at = datetime.now()
    
    def add_note(self, text: str, author: Optional[str] = None) -> None:
        """
        Add a note to the issue.
        
        Args:
            text: Note text
            author: Note author
        """
        self.notes.append({
            "text": text,
            "author": author,
            "timestamp": datetime.now().isoformat(),
        })
        self.updated_at = datetime.now()
    
    def set_assignee(self, assignee: Optional[str]) -> None:
        """
        Set issue assignee.
        
        Args:
            assignee: Assignee name or None
        """
        self.assignee = assignee
        self.updated_at = datetime.now()
    
    def add_related_issue(self, issue_id: str) -> None:
        """
        Add a related issue.
        
        Args:
            issue_id: Related issue ID
        """
        if issue_id not in self.related_issues:
            self.related_issues.append(issue_id)
            self.updated_at = datetime.now()
    
    def set_resolution(self, resolution: str) -> None:
        """
        Set issue resolution.
        
        Args:
            resolution: Resolution description
        """
        self.resolution = resolution
        self.updated_at = datetime.now()
        
        if self.status != IssueStatus.RESOLVED:
            self.update_status(IssueStatus.RESOLVED)


class IssueDetector:
    """Detector for issues in container logs."""
    
    def __init__(self):
        """Initialize issue detector."""
        self.log_collection_manager = get_log_collection_manager()
        self.pattern_recognition_engine = get_pattern_recognition_engine()
        self.log_analyzer = get_log_analyzer()
        
        # Issues
        self.issues: Dict[str, Issue] = {}
        
        # Issue database
        self.issues_dir = get_config(
            "monitoring.issues_dir",
            os.path.expanduser("~/.dockerforge/issues")
        )
        
        # Load issues from database
        self._load_issues()
        
        # Register callback for new log entries
        self.log_collection_manager.add_callback(self._on_new_log_entry)
    
    def _load_issues(self) -> None:
        """Load issues from database."""
        if not os.path.exists(self.issues_dir):
            try:
                os.makedirs(self.issues_dir, exist_ok=True)
                logger.info(f"Created issues directory: {self.issues_dir}")
            except Exception as e:
                logger.error(f"Error creating issues directory: {str(e)}")
                return
        
        try:
            # Load issues from JSON files
            for filename in os.listdir(self.issues_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.issues_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            issue_data = json.load(f)
                            issue = Issue.from_dict(issue_data)
                            self.issues[issue.id] = issue
                            logger.debug(f"Loaded issue from {file_path}")
                    except Exception as e:
                        logger.error(f"Error loading issue from {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading issues from directory: {str(e)}")
    
    def _save_issue(self, issue: Issue) -> bool:
        """
        Save an issue to the database.
        
        Args:
            issue: Issue to save
            
        Returns:
            bool: True if the issue was saved
        """
        if not os.path.exists(self.issues_dir):
            try:
                os.makedirs(self.issues_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating issues directory: {str(e)}")
                return False
        
        try:
            file_path = os.path.join(self.issues_dir, f"{issue.id}.json")
            with open(file_path, "w") as f:
                json.dump(issue.to_dict(), f, indent=2)
            
            logger.debug(f"Saved issue to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving issue: {str(e)}")
            return False
    
    def _on_new_log_entry(self, log_entry: LogEntry) -> None:
        """
        Process a new log entry.
        
        Args:
            log_entry: Log entry
        """
        # Process log entry with pattern recognition engine
        matches = self.pattern_recognition_engine.process_log(log_entry)
        
        # Create issues for pattern matches
        for match in matches:
            self._create_issue_from_pattern_match(match)
    
    def _create_issue_from_pattern_match(self, match: PatternMatch) -> Optional[Issue]:
        """
        Create an issue from a pattern match.
        
        Args:
            match: Pattern match
            
        Returns:
            Optional[Issue]: Created issue or None
        """
        # Get pattern definition
        pattern = self.pattern_recognition_engine.get_pattern(match.pattern_id)
        if not pattern:
            return None
        
        # Check if there's an existing open issue for this pattern and container
        for issue in self.issues.values():
            if (issue.container_id == match.log_entry.container_id and
                issue.pattern_id == match.pattern_id and
                issue.status in (IssueStatus.OPEN, IssueStatus.ACKNOWLEDGED, IssueStatus.IN_PROGRESS)):
                # Add pattern match to existing issue
                issue.pattern_matches.append(match.to_dict())
                issue.updated_at = datetime.now()
                self._save_issue(issue)
                return issue
        
        # Create new issue
        issue_id = f"{match.log_entry.container_id[:8]}_{match.pattern_id}_{int(time.time())}"
        
        issue = Issue(
            id=issue_id,
            container_id=match.log_entry.container_id,
            container_name=match.log_entry.container_name,
            title=f"{pattern.name} in {match.log_entry.container_name}",
            description=pattern.description,
            severity=IssueSeverity.from_string(pattern.severity),
            status=IssueStatus.OPEN,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="pattern",
            pattern_id=match.pattern_id,
            pattern_matches=[match.to_dict()],
            tags=pattern.tags,
        )
        
        # Add issue to database
        self.issues[issue.id] = issue
        self._save_issue(issue)
        
        logger.info(f"Created new issue: {issue.id} - {issue.title}")
        
        return issue
    
    def create_issue_from_analysis(self, analysis_result: AnalysisResult, issue_data: Dict[str, Any]) -> Issue:
        """
        Create an issue from an analysis result.
        
        Args:
            analysis_result: Analysis result
            issue_data: Issue data from analysis
            
        Returns:
            Issue: Created issue
        """
        # Create issue ID
        issue_id = f"{analysis_result.container_id[:8]}_analysis_{int(time.time())}"
        
        # Determine severity
        severity_str = issue_data.get("severity", "info")
        severity = IssueSeverity.from_string(severity_str)
        
        # Create issue
        issue = Issue(
            id=issue_id,
            container_id=analysis_result.container_id,
            container_name=analysis_result.container_name,
            title=issue_data.get("title", "Issue detected by AI analysis"),
            description=issue_data.get("description", ""),
            severity=severity,
            status=IssueStatus.OPEN,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="analysis",
            analysis_id=str(analysis_result.timestamp.timestamp()),
            tags=["ai-analysis"],
        )
        
        # Add issue to database
        self.issues[issue.id] = issue
        self._save_issue(issue)
        
        logger.info(f"Created new issue from analysis: {issue.id} - {issue.title}")
        
        return issue
    
    def create_issue_manual(
        self,
        container_id: str,
        container_name: str,
        title: str,
        description: str,
        severity: Union[IssueSeverity, str],
        tags: Optional[List[str]] = None,
    ) -> Issue:
        """
        Create an issue manually.
        
        Args:
            container_id: Container ID
            container_name: Container name
            title: Issue title
            description: Issue description
            severity: Issue severity
            tags: Issue tags
            
        Returns:
            Issue: Created issue
        """
        # Create issue ID
        issue_id = f"{container_id[:8]}_manual_{int(time.time())}"
        
        # Convert severity string to enum if needed
        if isinstance(severity, str):
            severity = IssueSeverity.from_string(severity)
        
        # Create issue
        issue = Issue(
            id=issue_id,
            container_id=container_id,
            container_name=container_name,
            title=title,
            description=description,
            severity=severity,
            status=IssueStatus.OPEN,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="manual",
            tags=tags or ["manual"],
        )
        
        # Add issue to database
        self.issues[issue.id] = issue
        self._save_issue(issue)
        
        logger.info(f"Created new manual issue: {issue.id} - {issue.title}")
        
        return issue
    
    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """
        Get an issue by ID.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Optional[Issue]: Issue or None
        """
        return self.issues.get(issue_id)
    
    def get_issues(
        self,
        container_id: Optional[str] = None,
        status: Optional[Union[IssueStatus, str]] = None,
        severity: Optional[Union[IssueSeverity, str]] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Issue]:
        """
        Get issues with filtering.
        
        Args:
            container_id: Filter by container ID
            status: Filter by status
            severity: Filter by severity
            source: Filter by source
            tags: Filter by tags
            since: Filter by creation time
            limit: Maximum number of issues to return
            
        Returns:
            List[Issue]: Filtered issues
        """
        # Convert status string to enum if needed
        if isinstance(status, str):
            try:
                status = IssueStatus(status.lower())
            except ValueError:
                status = None
        
        # Convert severity string to enum if needed
        if isinstance(severity, str):
            severity = IssueSeverity.from_string(severity)
        
        # Start with all issues
        issues = list(self.issues.values())
        
        # Filter by container ID
        if container_id:
            issues = [i for i in issues if i.container_id == container_id]
        
        # Filter by status
        if status:
            issues = [i for i in issues if i.status == status]
        
        # Filter by severity
        if severity:
            issues = [i for i in issues if i.severity == severity]
        
        # Filter by source
        if source:
            issues = [i for i in issues if i.source == source]
        
        # Filter by tags
        if tags:
            issues = [i for i in issues if any(tag in i.tags for tag in tags)]
        
        # Filter by creation time
        if since:
            issues = [i for i in issues if i.created_at >= since]
        
        # Sort by creation time (newest first)
        issues.sort(key=lambda i: i.created_at, reverse=True)
        
        # Apply limit
        if limit and len(issues) > limit:
            issues = issues[:limit]
        
        return issues
    
    def update_issue(self, issue_id: str, **kwargs) -> Optional[Issue]:
        """
        Update an issue.
        
        Args:
            issue_id: Issue ID
            **kwargs: Fields to update
            
        Returns:
            Optional[Issue]: Updated issue or None
        """
        issue = self.get_issue(issue_id)
        if not issue:
            return None
        
        # Update fields
        for key, value in kwargs.items():
            if key == "status":
                if isinstance(value, str):
                    try:
                        value = IssueStatus(value.lower())
                    except ValueError:
                        continue
                issue.update_status(value)
            elif key == "severity":
                if isinstance(value, str):
                    value = IssueSeverity.from_string(value)
                setattr(issue, key, value)
            elif key == "assignee":
                issue.set_assignee(value)
            elif key == "resolution":
                issue.set_resolution(value)
            elif key == "notes":
                if isinstance(value, str):
                    issue.add_note(value)
                elif isinstance(value, dict):
                    issue.notes.append(value)
            elif key == "related_issues":
                if isinstance(value, str):
                    issue.add_related_issue(value)
                elif isinstance(value, list):
                    for related_id in value:
                        issue.add_related_issue(related_id)
            elif hasattr(issue, key):
                setattr(issue, key, value)
                issue.updated_at = datetime.now()
        
        # Save issue
        self._save_issue(issue)
        
        return issue
    
    def delete_issue(self, issue_id: str) -> bool:
        """
        Delete an issue.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            bool: True if the issue was deleted
        """
        if issue_id not in self.issues:
            return False
        
        # Remove from memory
        del self.issues[issue_id]
        
        # Remove from disk
        try:
            file_path = os.path.join(self.issues_dir, f"{issue_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            logger.info(f"Deleted issue: {issue_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting issue file: {str(e)}")
            return False
    
    def process_analysis_result(self, analysis_result: AnalysisResult) -> List[Issue]:
        """
        Process an analysis result and create issues.
        
        Args:
            analysis_result: Analysis result
            
        Returns:
            List[Issue]: Created issues
        """
        created_issues = []
        
        # Create issues for each issue in the analysis result
        for issue_data in analysis_result.issues:
            issue = self.create_issue_from_analysis(analysis_result, issue_data)
            created_issues.append(issue)
        
        return created_issues
    
    def get_container_issues(self, container_id: str) -> List[Issue]:
        """
        Get all issues for a container.
        
        Args:
            container_id: Container ID
            
        Returns:
            List[Issue]: Container issues
        """
        return self.get_issues(container_id=container_id)
    
    def get_open_issues(self) -> List[Issue]:
        """
        Get all open issues.
        
        Returns:
            List[Issue]: Open issues
        """
        return self.get_issues(status=IssueStatus.OPEN)
    
    def get_critical_issues(self) -> List[Issue]:
        """
        Get all critical issues.
        
        Returns:
            List[Issue]: Critical issues
        """
        return self.get_issues(severity=IssueSeverity.CRITICAL)
    
    def get_issue_stats(self) -> Dict[str, Any]:
        """
        Get issue statistics.
        
        Returns:
            Dict[str, Any]: Issue statistics
        """
        stats = {
            "total": len(self.issues),
            "by_status": {
                status.value: 0 for status in IssueStatus
            },
            "by_severity": {
                severity.value: 0 for severity in IssueSeverity
            },
            "by_source": {
                "pattern": 0,
                "analysis": 0,
                "manual": 0,
            },
            "by_container": {},
        }
        
        # Count issues by status, severity, source, and container
        for issue in self.issues.values():
            stats["by_status"][issue.status.value] += 1
            stats["by_severity"][issue.severity.value] += 1
            stats["by_source"][issue.source] += 1
            
            if issue.container_id not in stats["by_container"]:
                stats["by_container"][issue.container_id] = {
                    "name": issue.container_name,
                    "count": 0,
                }
            
            stats["by_container"][issue.container_id]["count"] += 1
        
        return stats


# Singleton instance
_issue_detector = None


def get_issue_detector() -> IssueDetector:
    """
    Get the issue detector (singleton).
    
    Returns:
        IssueDetector: Issue detector
    """
    global _issue_detector
    if _issue_detector is None:
        _issue_detector = IssueDetector()
    
    return _issue_detector
