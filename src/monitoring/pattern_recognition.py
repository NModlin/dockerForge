"""
Pattern recognition module for DockerForge.

This module provides functionality to recognize patterns in container logs,
including known error patterns and anomalies.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List, Optional, Pattern, Tuple, Set, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.monitoring.log_collector import LogEntry

logger = get_logger("pattern_recognition")


@dataclass
class PatternDefinition:
    """Definition of a log pattern."""
    
    id: str
    name: str
    description: str
    regex: str
    severity: str = "info"  # info, warning, error, critical
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)
    solution: Optional[str] = None
    compiled_regex: Optional[Pattern] = None
    
    def __post_init__(self):
        """Compile regex after initialization."""
        try:
            self.compiled_regex = re.compile(self.regex)
        except re.error as e:
            logger.error(f"Invalid regex pattern '{self.id}': {str(e)}")
            self.compiled_regex = None
    
    def matches(self, log_entry: LogEntry) -> bool:
        """
        Check if a log entry matches this pattern.
        
        Args:
            log_entry: Log entry to check
            
        Returns:
            bool: True if the log entry matches this pattern
        """
        if not self.compiled_regex:
            return False
        
        return bool(self.compiled_regex.search(log_entry.message))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pattern definition to dictionary.
        
        Returns:
            Dict[str, Any]: Pattern definition as dictionary
        """
        result = asdict(self)
        result.pop("compiled_regex", None)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatternDefinition":
        """
        Create pattern definition from dictionary.
        
        Args:
            data: Dictionary with pattern definition data
            
        Returns:
            PatternDefinition: Pattern definition
        """
        # Remove compiled_regex if present
        data = data.copy()
        data.pop("compiled_regex", None)
        
        return cls(**data)


@dataclass
class PatternMatch:
    """Match of a log pattern."""
    
    pattern_id: str
    log_entry: LogEntry
    match_text: str
    groups: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pattern match to dictionary.
        
        Returns:
            Dict[str, Any]: Pattern match as dictionary
        """
        return {
            "pattern_id": self.pattern_id,
            "log_entry": self.log_entry.to_dict(),
            "match_text": self.match_text,
            "groups": self.groups,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatternMatch":
        """
        Create pattern match from dictionary.
        
        Args:
            data: Dictionary with pattern match data
            
        Returns:
            PatternMatch: Pattern match
        """
        data = data.copy()
        data["log_entry"] = LogEntry.from_dict(data["log_entry"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        return cls(**data)


class PatternDatabase:
    """Database of log patterns."""
    
    def __init__(self, patterns_dir: Optional[str] = None):
        """
        Initialize pattern database.
        
        Args:
            patterns_dir: Directory containing pattern definitions
        """
        self.patterns: Dict[str, PatternDefinition] = {}
        self.patterns_dir = patterns_dir or get_config(
            "monitoring.patterns_dir",
            os.path.expanduser("~/.dockerforge/patterns")
        )
        
        # Load built-in patterns
        self._load_builtin_patterns()
        
        # Load patterns from directory
        self._load_patterns_from_dir()
    
    def _load_builtin_patterns(self) -> None:
        """Load built-in patterns."""
        # Docker daemon errors
        self.add_pattern(PatternDefinition(
            id="docker_daemon_error",
            name="Docker Daemon Error",
            description="Error from the Docker daemon",
            regex=r"(?i)error from daemon: (.+)",
            severity="error",
            tags=["docker", "daemon", "error"],
            examples=[
                "Error from daemon: conflict: unable to delete image (must be forced) - image is being used by running container",
                "Error from daemon: Get https://registry-1.docker.io/v2/: net/http: request canceled while waiting for connection",
            ],
        ))
        
        # Container exit
        self.add_pattern(PatternDefinition(
            id="container_exit",
            name="Container Exit",
            description="Container exited with a non-zero exit code",
            regex=r"(?i)exited with code (?!0)(\d+)",
            severity="warning",
            tags=["container", "exit", "error"],
            examples=[
                "Container exited with code 1",
                "Process exited with code 137",
            ],
        ))
        
        # Out of memory
        self.add_pattern(PatternDefinition(
            id="out_of_memory",
            name="Out of Memory",
            description="Container or process ran out of memory",
            regex=r"(?i)(out of memory|memory exhausted|cannot allocate memory|killed process|oom-killer)",
            severity="critical",
            tags=["memory", "oom", "error"],
            examples=[
                "Out of memory: Killed process 123",
                "Container was killed as it was using too much memory",
                "java.lang.OutOfMemoryError: Java heap space",
            ],
            solution="Increase container memory limit or optimize application memory usage",
        ))
        
        # Permission denied
        self.add_pattern(PatternDefinition(
            id="permission_denied",
            name="Permission Denied",
            description="Permission denied error",
            regex=r"(?i)(permission denied|access denied|not permitted|unauthorized)",
            severity="error",
            tags=["permission", "access", "error"],
            examples=[
                "Permission denied: '/var/lib/docker'",
                "Access denied for user 'root'@'localhost'",
            ],
        ))
        
        # Connection refused
        self.add_pattern(PatternDefinition(
            id="connection_refused",
            name="Connection Refused",
            description="Connection refused error",
            regex=r"(?i)(connection refused|could not connect|failed to connect|connection reset|connection timed out)",
            severity="error",
            tags=["connection", "network", "error"],
            examples=[
                "Connection refused: localhost:5432",
                "Failed to connect to database",
            ],
        ))
        
        # File not found
        self.add_pattern(PatternDefinition(
            id="file_not_found",
            name="File Not Found",
            description="File or directory not found error",
            regex=r"(?i)(no such file|file not found|directory not found|not found|no such directory)",
            severity="error",
            tags=["file", "path", "error"],
            examples=[
                "No such file or directory: '/etc/config.json'",
                "Could not find file 'app.js'",
            ],
        ))
        
        # Disk space
        self.add_pattern(PatternDefinition(
            id="disk_space",
            name="Disk Space Issue",
            description="Disk space related error",
            regex=r"(?i)(no space left on device|disk full|not enough space|insufficient space)",
            severity="critical",
            tags=["disk", "storage", "error"],
            examples=[
                "No space left on device",
                "Disk full, cannot write to file",
            ],
            solution="Free up disk space or increase disk size",
        ))
        
        # Database connection
        self.add_pattern(PatternDefinition(
            id="database_connection",
            name="Database Connection Error",
            description="Error connecting to database",
            regex=r"(?i)(database connection|db connection|sql connection|mongodb connection).*?(error|failed|refused|timeout)",
            severity="error",
            tags=["database", "connection", "error"],
            examples=[
                "Database connection error: Connection refused",
                "Failed to connect to MySQL database",
            ],
        ))
        
        # API error
        self.add_pattern(PatternDefinition(
            id="api_error",
            name="API Error",
            description="Error from API call",
            regex=r"(?i)(api|http|https).*?(error|failed|status code [^2]\d{2})",
            severity="warning",
            tags=["api", "http", "error"],
            examples=[
                "API error: Status code 500",
                "HTTP request failed with status 404",
            ],
        ))
        
        # Configuration error
        self.add_pattern(PatternDefinition(
            id="config_error",
            name="Configuration Error",
            description="Error in configuration",
            regex=r"(?i)(config|configuration|settings|env|environment).*?(error|invalid|missing|not found)",
            severity="error",
            tags=["config", "settings", "error"],
            examples=[
                "Configuration error: Missing required setting 'API_KEY'",
                "Invalid configuration value for 'PORT'",
            ],
        ))
        
        # Crash or panic
        self.add_pattern(PatternDefinition(
            id="crash_panic",
            name="Crash or Panic",
            description="Application crash or panic",
            regex=r"(?i)(crash|crashed|panic|fatal error|segmentation fault|core dumped)",
            severity="critical",
            tags=["crash", "panic", "error"],
            examples=[
                "Application crashed with signal 11",
                "panic: runtime error: index out of range",
            ],
        ))
        
        # Deadlock
        self.add_pattern(PatternDefinition(
            id="deadlock",
            name="Deadlock",
            description="Deadlock detected",
            regex=r"(?i)(deadlock|dead lock|resource deadlock|deadlock detected)",
            severity="critical",
            tags=["deadlock", "concurrency", "error"],
            examples=[
                "Deadlock detected between threads",
                "Resource deadlock avoided",
            ],
        ))
        
        # Timeout
        self.add_pattern(PatternDefinition(
            id="timeout",
            name="Timeout",
            description="Operation timed out",
            regex=r"(?i)(timeout|timed out|time limit exceeded)",
            severity="warning",
            tags=["timeout", "performance", "error"],
            examples=[
                "Operation timed out after 30 seconds",
                "Request timed out waiting for response",
            ],
        ))
        
        # Rate limit
        self.add_pattern(PatternDefinition(
            id="rate_limit",
            name="Rate Limit",
            description="Rate limit exceeded",
            regex=r"(?i)(rate limit|rate limiting|too many requests|throttl)",
            severity="warning",
            tags=["rate-limit", "throttling", "error"],
            examples=[
                "Rate limit exceeded: 100 requests per minute",
                "Too many requests, please try again later",
            ],
        ))
        
        # Authentication failure
        self.add_pattern(PatternDefinition(
            id="auth_failure",
            name="Authentication Failure",
            description="Authentication failed",
            regex=r"(?i)(authentication failed|auth failed|login failed|invalid credentials|invalid password|invalid token)",
            severity="error",
            tags=["authentication", "security", "error"],
            examples=[
                "Authentication failed for user 'admin'",
                "Invalid credentials provided",
            ],
        ))
        
        # SSL/TLS error
        self.add_pattern(PatternDefinition(
            id="ssl_error",
            name="SSL/TLS Error",
            description="SSL/TLS related error",
            regex=r"(?i)(ssl|tls|certificate).*?(error|invalid|expired|verification|failed)",
            severity="error",
            tags=["ssl", "tls", "security", "error"],
            examples=[
                "SSL certificate verification failed",
                "TLS handshake error",
            ],
        ))
        
        # DNS resolution
        self.add_pattern(PatternDefinition(
            id="dns_error",
            name="DNS Resolution Error",
            description="DNS resolution failed",
            regex=r"(?i)(dns|domain name|resolve|resolution).*?(error|failed|not found|could not)",
            severity="error",
            tags=["dns", "network", "error"],
            examples=[
                "DNS resolution failed for host 'example.com'",
                "Could not resolve hostname",
            ],
        ))
        
        # Version mismatch
        self.add_pattern(PatternDefinition(
            id="version_mismatch",
            name="Version Mismatch",
            description="Version incompatibility",
            regex=r"(?i)(version|compatibility).*?(mismatch|incompatible|not compatible|requires|expected)",
            severity="warning",
            tags=["version", "compatibility", "error"],
            examples=[
                "Version mismatch: expected 2.0.0, got 1.5.0",
                "Incompatible library version",
            ],
        ))
        
        # Resource limit
        self.add_pattern(PatternDefinition(
            id="resource_limit",
            name="Resource Limit",
            description="Resource limit reached",
            regex=r"(?i)(resource limit|limit exceeded|quota exceeded|max.*?reached|too many)",
            severity="warning",
            tags=["resource", "limit", "error"],
            examples=[
                "Resource limit exceeded: max connections",
                "Too many open files",
            ],
        ))
        
        # Dependency missing
        self.add_pattern(PatternDefinition(
            id="dependency_missing",
            name="Dependency Missing",
            description="Required dependency is missing",
            regex=r"(?i)(dependency|module|package|library|import).*?(missing|not found|could not|failed to|error)",
            severity="error",
            tags=["dependency", "module", "error"],
            examples=[
                "Dependency 'requests' not found",
                "Failed to import module 'numpy'",
            ],
        ))
        
        # Syntax error
        self.add_pattern(PatternDefinition(
            id="syntax_error",
            name="Syntax Error",
            description="Syntax error in code or configuration",
            regex=r"(?i)(syntax error|parse error|invalid syntax|unexpected token|unexpected character)",
            severity="error",
            tags=["syntax", "parsing", "error"],
            examples=[
                "Syntax error at line 42",
                "Parse error: unexpected '}'",
            ],
        ))
        
        # Startup failure
        self.add_pattern(PatternDefinition(
            id="startup_failure",
            name="Startup Failure",
            description="Application failed to start",
            regex=r"(?i)(failed to start|startup failed|initialization failed|bootstrap failed|cannot start)",
            severity="critical",
            tags=["startup", "initialization", "error"],
            examples=[
                "Failed to start application",
                "Initialization failed: could not connect to database",
            ],
        ))
    
    def _load_patterns_from_dir(self) -> None:
        """Load patterns from directory."""
        if not os.path.exists(self.patterns_dir):
            try:
                os.makedirs(self.patterns_dir, exist_ok=True)
                logger.info(f"Created patterns directory: {self.patterns_dir}")
            except Exception as e:
                logger.error(f"Error creating patterns directory: {str(e)}")
                return
        
        try:
            # Load patterns from JSON files
            for filename in os.listdir(self.patterns_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.patterns_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            pattern_data = json.load(f)
                            
                            # Handle single pattern or list of patterns
                            if isinstance(pattern_data, list):
                                for data in pattern_data:
                                    pattern = PatternDefinition.from_dict(data)
                                    self.add_pattern(pattern)
                            else:
                                pattern = PatternDefinition.from_dict(pattern_data)
                                self.add_pattern(pattern)
                    except Exception as e:
                        logger.error(f"Error loading pattern from {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading patterns from directory: {str(e)}")
    
    def add_pattern(self, pattern: PatternDefinition) -> None:
        """
        Add a pattern to the database.
        
        Args:
            pattern: Pattern definition to add
        """
        if pattern.id in self.patterns:
            logger.warning(f"Pattern with ID '{pattern.id}' already exists, overwriting")
        
        self.patterns[pattern.id] = pattern
        logger.debug(f"Added pattern: {pattern.id}")
    
    def remove_pattern(self, pattern_id: str) -> bool:
        """
        Remove a pattern from the database.
        
        Args:
            pattern_id: ID of the pattern to remove
            
        Returns:
            bool: True if the pattern was removed
        """
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            logger.debug(f"Removed pattern: {pattern_id}")
            return True
        
        return False
    
    def get_pattern(self, pattern_id: str) -> Optional[PatternDefinition]:
        """
        Get a pattern by ID.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            Optional[PatternDefinition]: Pattern definition or None
        """
        return self.patterns.get(pattern_id)
    
    def get_all_patterns(self) -> List[PatternDefinition]:
        """
        Get all patterns.
        
        Returns:
            List[PatternDefinition]: All patterns
        """
        return list(self.patterns.values())
    
    def save_pattern(self, pattern: PatternDefinition) -> bool:
        """
        Save a pattern to a file.
        
        Args:
            pattern: Pattern definition to save
            
        Returns:
            bool: True if the pattern was saved
        """
        if not os.path.exists(self.patterns_dir):
            try:
                os.makedirs(self.patterns_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating patterns directory: {str(e)}")
                return False
        
        try:
            file_path = os.path.join(self.patterns_dir, f"{pattern.id}.json")
            with open(file_path, "w") as f:
                json.dump(pattern.to_dict(), f, indent=2)
            
            logger.debug(f"Saved pattern to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving pattern: {str(e)}")
            return False
    
    def match_log(self, log_entry: LogEntry) -> List[PatternMatch]:
        """
        Match a log entry against all patterns.
        
        Args:
            log_entry: Log entry to match
            
        Returns:
            List[PatternMatch]: Matching patterns
        """
        matches = []
        
        for pattern_id, pattern in self.patterns.items():
            if pattern.matches(log_entry):
                # Extract match text and groups
                match = pattern.compiled_regex.search(log_entry.message)
                if match:
                    match_text = match.group(0)
                    groups = {str(i): match.group(i) for i in range(1, len(match.groups()) + 1)}
                    
                    # Create pattern match
                    pattern_match = PatternMatch(
                        pattern_id=pattern_id,
                        log_entry=log_entry,
                        match_text=match_text,
                        groups=groups,
                    )
                    
                    matches.append(pattern_match)
        
        return matches


class PatternRecognitionEngine:
    """Engine for recognizing patterns in logs."""
    
    def __init__(self):
        """Initialize pattern recognition engine."""
        self.pattern_db = PatternDatabase()
        self.recent_matches: List[PatternMatch] = []
        self.max_recent_matches = get_config("monitoring.max_recent_matches", 1000)
    
    def process_log(self, log_entry: LogEntry) -> List[PatternMatch]:
        """
        Process a log entry and find matching patterns.
        
        Args:
            log_entry: Log entry to process
            
        Returns:
            List[PatternMatch]: Matching patterns
        """
        # Match log against patterns
        matches = self.pattern_db.match_log(log_entry)
        
        # Add to recent matches
        self.recent_matches.extend(matches)
        
        # Trim recent matches if needed
        if len(self.recent_matches) > self.max_recent_matches:
            self.recent_matches = self.recent_matches[-self.max_recent_matches:]
        
        return matches
    
    def process_logs(self, log_entries: List[LogEntry]) -> List[PatternMatch]:
        """
        Process multiple log entries and find matching patterns.
        
        Args:
            log_entries: Log entries to process
            
        Returns:
            List[PatternMatch]: Matching patterns
        """
        all_matches = []
        
        for log_entry in log_entries:
            matches = self.process_log(log_entry)
            all_matches.extend(matches)
        
        return all_matches
    
    def get_recent_matches(
        self,
        pattern_ids: Optional[List[str]] = None,
        severity: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[PatternMatch]:
        """
        Get recent pattern matches.
        
        Args:
            pattern_ids: Filter by pattern IDs
            severity: Filter by severity
            since: Filter by timestamp
            limit: Maximum number of matches to return
            
        Returns:
            List[PatternMatch]: Recent pattern matches
        """
        # Start with all recent matches
        matches = self.recent_matches.copy()
        
        # Filter by pattern IDs
        if pattern_ids:
            matches = [m for m in matches if m.pattern_id in pattern_ids]
        
        # Filter by severity
        if severity:
            # Get patterns with matching severity
            severity_patterns = {
                p.id for p in self.pattern_db.get_all_patterns()
                if p.severity == severity
            }
            matches = [m for m in matches if m.pattern_id in severity_patterns]
        
        # Filter by timestamp
        if since:
            matches = [m for m in matches if m.timestamp >= since]
        
        # Sort by timestamp (newest first)
        matches.sort(key=lambda m: m.timestamp, reverse=True)
        
        # Apply limit
        if limit and len(matches) > limit:
            matches = matches[:limit]
        
        return matches
    
    def get_pattern_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for pattern matches.
        
        Returns:
            Dict[str, Dict[str, Any]]: Pattern statistics
        """
        stats = {}
        
        for pattern in self.pattern_db.get_all_patterns():
            # Count matches for this pattern
            count = sum(1 for m in self.recent_matches if m.pattern_id == pattern.id)
            
            # Get most recent match
            recent = None
            for m in reversed(self.recent_matches):
                if m.pattern_id == pattern.id:
                    recent = m
                    break
            
            stats[pattern.id] = {
                "pattern": pattern.to_dict(),
                "count": count,
                "most_recent": recent.to_dict() if recent else None,
            }
        
        return stats
    
    def add_pattern(self, pattern: PatternDefinition) -> None:
        """
        Add a pattern to the database.
        
        Args:
            pattern: Pattern definition to add
        """
        self.pattern_db.add_pattern(pattern)
    
    def save_pattern(self, pattern: PatternDefinition) -> bool:
        """
        Save a pattern to a file.
        
        Args:
            pattern: Pattern definition to save
            
        Returns:
            bool: True if the pattern was saved
        """
        return self.pattern_db.save_pattern(pattern)
    
    def get_pattern(self, pattern_id: str) -> Optional[PatternDefinition]:
        """
        Get a pattern by ID.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            Optional[PatternDefinition]: Pattern definition or None
        """
        return self.pattern_db.get_pattern(pattern_id)
    
    def get_all_patterns(self) -> List[PatternDefinition]:
        """
        Get all patterns.
        
        Returns:
            List[PatternDefinition]: All patterns
        """
        return self.pattern_db.get_all_patterns()


# Singleton instance
_pattern_recognition_engine = None


def get_pattern_recognition_engine() -> PatternRecognitionEngine:
    """
    Get the pattern recognition engine (singleton).
    
    Returns:
        PatternRecognitionEngine: Pattern recognition engine
    """
    global _pattern_recognition_engine
    if _pattern_recognition_engine is None:
        _pattern_recognition_engine = PatternRecognitionEngine()
    
    return _pattern_recognition_engine
