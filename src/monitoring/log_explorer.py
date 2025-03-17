"""
Log explorer module for DockerForge.

This module provides functionality to explore and search container logs,
with advanced filtering and visualization capabilities.
"""

import os
import json
import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple, Set, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.monitoring.log_collector import (
    LogEntry, LogFilter, get_log_collection_manager
)
from src.monitoring.pattern_recognition import (
    PatternMatch, get_pattern_recognition_engine
)

logger = get_logger("log_explorer")


@dataclass
class LogSearchResult:
    """Result of a log search."""
    
    query: str
    logs: List[LogEntry]
    total_matches: int
    execution_time: float  # in seconds
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search result to dictionary.
        
        Returns:
            Dict[str, Any]: Search result as dictionary
        """
        return {
            "query": self.query,
            "logs": [log.to_dict() for log in self.logs],
            "total_matches": self.total_matches,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogSearchResult":
        """
        Create search result from dictionary.
        
        Args:
            data: Dictionary with search result data
            
        Returns:
            LogSearchResult: Search result
        """
        data = data.copy()
        data["logs"] = [LogEntry.from_dict(log) for log in data["logs"]]
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        return cls(**data)


@dataclass
class LogStatistics:
    """Statistics for container logs."""
    
    container_id: str
    container_name: str
    log_count: int
    time_range: Tuple[datetime, datetime]
    message_length_avg: float
    message_length_max: int
    message_length_min: int
    messages_per_minute: Dict[str, int]  # minute -> count
    common_terms: List[Tuple[str, int]]  # (term, count)
    error_count: int
    warning_count: int
    pattern_matches: Dict[str, int]  # pattern_id -> count
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert statistics to dictionary.
        
        Returns:
            Dict[str, Any]: Statistics as dictionary
        """
        return {
            "container_id": self.container_id,
            "container_name": self.container_name,
            "log_count": self.log_count,
            "time_range": [t.isoformat() for t in self.time_range],
            "message_length_avg": self.message_length_avg,
            "message_length_max": self.message_length_max,
            "message_length_min": self.message_length_min,
            "messages_per_minute": self.messages_per_minute,
            "common_terms": self.common_terms,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "pattern_matches": self.pattern_matches,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogStatistics":
        """
        Create statistics from dictionary.
        
        Args:
            data: Dictionary with statistics data
            
        Returns:
            LogStatistics: Statistics
        """
        data = data.copy()
        data["time_range"] = tuple(datetime.fromisoformat(t) for t in data["time_range"])
        
        return cls(**data)


class LogExplorer:
    """Explorer for container logs."""
    
    def __init__(self):
        """Initialize log explorer."""
        self.log_collection_manager = get_log_collection_manager()
        self.pattern_recognition_engine = get_pattern_recognition_engine()
        
        # Search history
        self.search_history: List[LogSearchResult] = []
        self.max_history_size = get_config("monitoring.max_search_history", 100)
    
    def search_logs(
        self,
        query: str,
        container_ids: Optional[List[str]] = None,
        container_names: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
        case_sensitive: bool = False,
        regex: bool = False,
    ) -> LogSearchResult:
        """
        Search logs with a query.
        
        Args:
            query: Search query
            container_ids: Filter by container IDs
            container_names: Filter by container names
            since: Filter by timestamp
            until: Filter by timestamp
            limit: Maximum number of logs to return
            case_sensitive: Whether the search is case-sensitive
            regex: Whether the query is a regular expression
            
        Returns:
            LogSearchResult: Search result
        """
        start_time = time.time()
        
        # Prepare regex pattern
        if regex:
            try:
                if case_sensitive:
                    pattern = re.compile(query)
                else:
                    pattern = re.compile(query, re.IGNORECASE)
            except re.error as e:
                logger.error(f"Invalid regex pattern: {str(e)}")
                return LogSearchResult(
                    query=query,
                    logs=[],
                    total_matches=0,
                    execution_time=time.time() - start_time,
                )
        else:
            # Escape special regex characters
            escaped_query = re.escape(query)
            if case_sensitive:
                pattern = re.compile(escaped_query)
            else:
                pattern = re.compile(escaped_query, re.IGNORECASE)
        
        # Get logs
        logs = self.log_collection_manager.get_logs(
            container_ids=container_ids,
            container_names=container_names,
            since=since,
            until=until,
            message_regex=pattern.pattern,
        )
        
        # Apply limit
        if limit and len(logs) > limit:
            logs = logs[-limit:]
        
        # Create search result
        result = LogSearchResult(
            query=query,
            logs=logs,
            total_matches=len(logs),
            execution_time=time.time() - start_time,
        )
        
        # Add to history
        self.search_history.append(result)
        
        # Trim history if needed
        if len(self.search_history) > self.max_history_size:
            self.search_history = self.search_history[-self.max_history_size:]
        
        return result
    
    def filter_logs(
        self,
        container_ids: Optional[List[str]] = None,
        container_names: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        message_contains: Optional[List[str]] = None,
        message_regex: Optional[str] = None,
        streams: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """
        Filter logs with various criteria.
        
        Args:
            container_ids: Filter by container IDs
            container_names: Filter by container names
            since: Filter by timestamp
            until: Filter by timestamp
            message_contains: Filter by message content
            message_regex: Filter by message regex
            streams: Filter by streams
            limit: Maximum number of logs to return
            
        Returns:
            List[LogEntry]: Filtered logs
        """
        return self.log_collection_manager.get_logs(
            container_ids=container_ids,
            container_names=container_names,
            since=since,
            until=until,
            message_contains=message_contains,
            message_regex=message_regex,
            streams=streams,
            limit=limit,
        )
    
    def get_container_logs(
        self,
        container_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """
        Get logs for a specific container.
        
        Args:
            container_id: Container ID
            since: Filter by timestamp
            until: Filter by timestamp
            limit: Maximum number of logs to return
            
        Returns:
            List[LogEntry]: Container logs
        """
        return self.log_collection_manager.get_container_logs(
            container_id=container_id,
            since=since,
            until=until,
            limit=limit,
        )
    
    def get_log_statistics(
        self,
        container_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> LogStatistics:
        """
        Get statistics for container logs.
        
        Args:
            container_id: Container ID
            since: Filter by timestamp
            until: Filter by timestamp
            
        Returns:
            LogStatistics: Log statistics
            
        Raises:
            ValueError: If container not found or no logs available
        """
        # Get container logs
        logs = self.log_collection_manager.get_container_logs(
            container_id=container_id,
            since=since,
            until=until,
        )
        
        if not logs:
            raise ValueError(f"No logs found for container {container_id}")
        
        # Get container name
        container_name = logs[0].container_name
        
        # Calculate time range
        start_time = min(log.timestamp for log in logs)
        end_time = max(log.timestamp for log in logs)
        
        # Calculate message length statistics
        message_lengths = [len(log.message) for log in logs]
        message_length_avg = sum(message_lengths) / len(message_lengths)
        message_length_max = max(message_lengths)
        message_length_min = min(message_lengths)
        
        # Calculate messages per minute
        messages_per_minute = defaultdict(int)
        for log in logs:
            minute_key = log.timestamp.strftime("%Y-%m-%d %H:%M")
            messages_per_minute[minute_key] += 1
        
        # Calculate common terms
        term_counter = Counter()
        for log in logs:
            # Split message into words
            words = re.findall(r'\b\w+\b', log.message.lower())
            # Filter out common stop words
            stop_words = {
                'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
                'at', 'from', 'by', 'for', 'with', 'about', 'to', 'in', 'on', 'of',
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can', 'could',
                'may', 'might', 'must', 'this', 'that', 'these', 'those', 'it', 'its',
                'i', 'you', 'he', 'she', 'we', 'they', 'their', 'our', 'your', 'my',
            }
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            term_counter.update(filtered_words)
        
        # Get most common terms
        common_terms = term_counter.most_common(20)
        
        # Count errors and warnings
        error_count = sum(1 for log in logs if re.search(r'(?i)(error|exception|fail|failed|failure)', log.message))
        warning_count = sum(1 for log in logs if re.search(r'(?i)(warning|warn|caution)', log.message))
        
        # Count pattern matches
        pattern_matches = defaultdict(int)
        for log in logs:
            matches = self.pattern_recognition_engine.process_log(log)
            for match in matches:
                pattern_matches[match.pattern_id] += 1
        
        # Create statistics
        statistics = LogStatistics(
            container_id=container_id,
            container_name=container_name,
            log_count=len(logs),
            time_range=(start_time, end_time),
            message_length_avg=message_length_avg,
            message_length_max=message_length_max,
            message_length_min=message_length_min,
            messages_per_minute=dict(messages_per_minute),
            common_terms=common_terms,
            error_count=error_count,
            warning_count=warning_count,
            pattern_matches=dict(pattern_matches),
        )
        
        return statistics
    
    def get_log_timeline(
        self,
        container_id: str,
        interval: str = "minute",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """
        Get log timeline for a container.
        
        Args:
            container_id: Container ID
            interval: Time interval (minute, hour, day)
            since: Filter by timestamp
            until: Filter by timestamp
            
        Returns:
            Dict[str, int]: Timeline data (time -> count)
            
        Raises:
            ValueError: If container not found or no logs available
        """
        # Get container logs
        logs = self.log_collection_manager.get_container_logs(
            container_id=container_id,
            since=since,
            until=until,
        )
        
        if not logs:
            raise ValueError(f"No logs found for container {container_id}")
        
        # Determine time format based on interval
        if interval == "minute":
            time_format = "%Y-%m-%d %H:%M"
        elif interval == "hour":
            time_format = "%Y-%m-%d %H:00"
        elif interval == "day":
            time_format = "%Y-%m-%d"
        else:
            raise ValueError(f"Invalid interval: {interval}")
        
        # Count logs per interval
        timeline = defaultdict(int)
        for log in logs:
            time_key = log.timestamp.strftime(time_format)
            timeline[time_key] += 1
        
        return dict(timeline)
    
    def get_log_patterns(
        self,
        container_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, List[PatternMatch]]:
        """
        Get pattern matches for container logs.
        
        Args:
            container_id: Container ID
            since: Filter by timestamp
            until: Filter by timestamp
            limit: Maximum number of logs to process
            
        Returns:
            Dict[str, List[PatternMatch]]: Pattern matches by pattern ID
            
        Raises:
            ValueError: If container not found or no logs available
        """
        # Get container logs
        logs = self.log_collection_manager.get_container_logs(
            container_id=container_id,
            since=since,
            until=until,
            limit=limit,
        )
        
        if not logs:
            raise ValueError(f"No logs found for container {container_id}")
        
        # Process logs for pattern matches
        pattern_matches: Dict[str, List[PatternMatch]] = defaultdict(list)
        for log in logs:
            matches = self.pattern_recognition_engine.process_log(log)
            for match in matches:
                pattern_matches[match.pattern_id].append(match)
        
        return dict(pattern_matches)
    
    def extract_log_context(
        self,
        log_entry: LogEntry,
        context_lines: int = 5,
    ) -> List[LogEntry]:
        """
        Extract context around a log entry.
        
        Args:
            log_entry: Log entry
            context_lines: Number of context lines before and after
            
        Returns:
            List[LogEntry]: Log entries with context
        """
        # Get all logs for the container
        all_logs = self.log_collection_manager.get_container_logs(
            container_id=log_entry.container_id,
        )
        
        # Find the index of the log entry
        try:
            index = next(i for i, log in enumerate(all_logs) if (
                log.container_id == log_entry.container_id and
                log.timestamp == log_entry.timestamp and
                log.message == log_entry.message
            ))
        except StopIteration:
            # Log entry not found
            return [log_entry]
        
        # Extract context
        start_index = max(0, index - context_lines)
        end_index = min(len(all_logs), index + context_lines + 1)
        
        return all_logs[start_index:end_index]
    
    def get_search_history(
        self,
        limit: Optional[int] = None,
    ) -> List[LogSearchResult]:
        """
        Get search history.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List[LogSearchResult]: Search history
        """
        # Apply limit
        if limit and len(self.search_history) > limit:
            return self.search_history[-limit:]
        
        return self.search_history
    
    def clear_search_history(self) -> None:
        """Clear search history."""
        self.search_history.clear()
    
    def export_logs(
        self,
        logs: List[LogEntry],
        format: str = "text",
        file_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Export logs to a file or string.
        
        Args:
            logs: Logs to export
            format: Export format (text, json, csv)
            file_path: Output file path or None for string output
            
        Returns:
            Optional[str]: Exported logs as string if file_path is None
            
        Raises:
            ValueError: If format is invalid
        """
        if format == "text":
            # Format as plain text
            output = "\n".join(str(log) for log in logs)
        elif format == "json":
            # Format as JSON
            output = json.dumps([log.to_dict() for log in logs], indent=2)
        elif format == "csv":
            # Format as CSV
            import csv
            import io
            
            output_buffer = io.StringIO()
            writer = csv.writer(output_buffer)
            
            # Write header
            writer.writerow(["Container ID", "Container Name", "Timestamp", "Stream", "Message"])
            
            # Write logs
            for log in logs:
                writer.writerow([
                    log.container_id,
                    log.container_name,
                    log.timestamp.isoformat(),
                    log.stream,
                    log.message,
                ])
            
            output = output_buffer.getvalue()
        else:
            raise ValueError(f"Invalid export format: {format}")
        
        # Write to file if specified
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(output)
                return None
            except Exception as e:
                logger.error(f"Error writing to file: {str(e)}")
                raise
        
        return output
    
    def highlight_logs(
        self,
        logs: List[LogEntry],
        highlight_terms: Optional[List[str]] = None,
        highlight_regex: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Highlight terms in logs.
        
        Args:
            logs: Logs to highlight
            highlight_terms: Terms to highlight
            highlight_regex: Regex pattern to highlight
            
        Returns:
            List[Dict[str, Any]]: Logs with highlighted terms
        """
        result = []
        
        # Prepare regex pattern
        patterns = []
        if highlight_terms:
            for term in highlight_terms:
                patterns.append(re.compile(re.escape(term), re.IGNORECASE))
        
        if highlight_regex:
            try:
                patterns.append(re.compile(highlight_regex, re.IGNORECASE))
            except re.error as e:
                logger.error(f"Invalid regex pattern: {str(e)}")
        
        # Process logs
        for log in logs:
            log_dict = log.to_dict()
            
            # Find matches
            matches = []
            for pattern in patterns:
                for match in pattern.finditer(log.message):
                    matches.append({
                        "start": match.start(),
                        "end": match.end(),
                        "text": match.group(0),
                    })
            
            # Sort matches by start position
            matches.sort(key=lambda m: m["start"])
            
            # Add matches to log
            log_dict["highlights"] = matches
            
            result.append(log_dict)
        
        return result
    
    def group_logs_by(
        self,
        logs: List[LogEntry],
        group_by: str,
    ) -> Dict[str, List[LogEntry]]:
        """
        Group logs by a field.
        
        Args:
            logs: Logs to group
            group_by: Field to group by (container_id, container_name, stream, hour, day)
            
        Returns:
            Dict[str, List[LogEntry]]: Grouped logs
            
        Raises:
            ValueError: If group_by is invalid
        """
        result = defaultdict(list)
        
        for log in logs:
            if group_by == "container_id":
                key = log.container_id
            elif group_by == "container_name":
                key = log.container_name
            elif group_by == "stream":
                key = log.stream
            elif group_by == "hour":
                key = log.timestamp.strftime("%Y-%m-%d %H:00")
            elif group_by == "day":
                key = log.timestamp.strftime("%Y-%m-%d")
            else:
                raise ValueError(f"Invalid group_by: {group_by}")
            
            result[key].append(log)
        
        return dict(result)
    
    def analyze_log_trends(
        self,
        container_id: str,
        interval: str = "hour",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Analyze log trends for a container.
        
        Args:
            container_id: Container ID
            interval: Time interval (minute, hour, day)
            since: Filter by timestamp
            until: Filter by timestamp
            
        Returns:
            Dict[str, Any]: Trend analysis
            
        Raises:
            ValueError: If container not found or no logs available
        """
        # Get container logs
        logs = self.log_collection_manager.get_container_logs(
            container_id=container_id,
            since=since,
            until=until,
        )
        
        if not logs:
            raise ValueError(f"No logs found for container {container_id}")
        
        # Get timeline
        timeline = self.get_log_timeline(
            container_id=container_id,
            interval=interval,
            since=since,
            until=until,
        )
        
        # Calculate error and warning trends
        error_timeline = defaultdict(int)
        warning_timeline = defaultdict(int)
        
        # Determine time format based on interval
        if interval == "minute":
            time_format = "%Y-%m-%d %H:%M"
        elif interval == "hour":
            time_format = "%Y-%m-%d %H:00"
        elif interval == "day":
            time_format = "%Y-%m-%d"
        else:
            raise ValueError(f"Invalid interval: {interval}")
        
        for log in logs:
            time_key = log.timestamp.strftime(time_format)
            
            if re.search(r'(?i)(error|exception|fail|failed|failure)', log.message):
                error_timeline[time_key] += 1
            
            if re.search(r'(?i)(warning|warn|caution)', log.message):
                warning_timeline[time_key] += 1
        
        # Calculate pattern match trends
        pattern_timelines = defaultdict(lambda: defaultdict(int))
        for log in logs:
            time_key = log.timestamp.strftime(time_format)
            
            matches = self.pattern_recognition_engine.process_log(log)
            for match in matches:
                pattern_timelines[match.pattern_id][time_key] += 1
        
        # Calculate trend statistics
        total_logs = len(logs)
        total_errors = sum(error_timeline.values())
        total_warnings = sum(warning_timeline.values())
        
        error_rate = total_errors / total_logs if total_logs > 0 else 0
        warning_rate = total_warnings / total_logs if total_logs > 0 else 0
        
        # Detect spikes
        spikes = []
        if len(timeline) > 1:
            avg_logs = total_logs / len(timeline)
            for time_key, count in timeline.items():
                if count > avg_logs * 2:  # Spike threshold: 2x average
                    spikes.append({
                        "time": time_key,
                        "count": count,
                        "ratio": count / avg_logs,
                    })
        
        # Create trend analysis
        analysis = {
            "container_id": container_id,
            "container_name": logs[0].container_name,
            "total_logs": total_logs,
            "timeline": timeline,
            "error_timeline": dict(error_timeline),
            "warning_timeline": dict(warning_timeline),
            "pattern_timelines": {pid: dict(ptl) for pid, ptl in pattern_timelines.items()},
            "error_rate": error_rate,
            "warning_rate": warning_rate,
            "spikes": spikes,
        }
        
        return analysis


# Singleton instance
_log_explorer = None


def get_log_explorer() -> LogExplorer:
    """
    Get the log explorer (singleton).
    
    Returns:
        LogExplorer: Log explorer
    """
    global _log_explorer
    if _log_explorer is None:
        _log_explorer = LogExplorer()
    
    return _log_explorer
