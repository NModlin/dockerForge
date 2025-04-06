"""
Log analyzer module for DockerForge.

This module provides functionality to analyze container logs using AI,
identify issues, and generate recommendations.
"""

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from src.config.config_manager import get_config
from src.core.ai_provider import AIProviderError, get_ai_provider
from src.monitoring.log_collector import LogEntry, get_log_collection_manager
from src.monitoring.pattern_recognition import (
    PatternMatch,
    get_pattern_recognition_engine,
)
from src.utils.logging_manager import get_logger

logger = get_logger("log_analyzer")


@dataclass
class AnalysisResult:
    """Result of log analysis."""

    container_id: str
    container_name: str
    timestamp: datetime
    summary: str
    issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    pattern_matches: List[Dict[str, Any]]
    ai_provider: str
    ai_model: str
    analysis_duration: float  # in seconds
    log_count: int

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert analysis result to dictionary.

        Returns:
            Dict[str, Any]: Analysis result as dictionary
        """
        result = asdict(self)
        result["timestamp"] = result["timestamp"].isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """
        Create analysis result from dictionary.

        Args:
            data: Dictionary with analysis result data

        Returns:
            AnalysisResult: Analysis result
        """
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        return cls(**data)


class LogAnalyzer:
    """Analyzer for container logs using AI."""

    def __init__(self, ai_provider_name: Optional[str] = None):
        """
        Initialize log analyzer.

        Args:
            ai_provider_name: AI provider name (default: from config)
        """
        try:
            self.ai_provider = get_ai_provider(ai_provider_name)
        except AIProviderError as e:
            logger.warning(f"AI provider error: {str(e)}")
            self.ai_provider = None

        self.log_collection_manager = get_log_collection_manager()
        self.pattern_recognition_engine = get_pattern_recognition_engine()

        # Analysis history
        self.analysis_history: List[AnalysisResult] = []
        self.max_history_size = get_config("monitoring.max_analysis_history", 100)

        # Analysis templates
        self.templates_dir = get_config(
            "monitoring.templates_dir", os.path.expanduser("~/.dockerforge/templates")
        )

        # Load analysis templates
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load analysis templates.

        Returns:
            Dict[str, Dict[str, Any]]: Analysis templates
        """
        templates = {
            "default": {
                "name": "Default Log Analysis",
                "description": "Default template for analyzing container logs",
                "prompt": (
                    "Analyze the following Docker container logs and identify any issues, "
                    "errors, or potential problems. Focus on critical errors, warnings, "
                    "and patterns that might indicate problems with the container or application. "
                    "Provide a summary of the issues found and specific recommendations for "
                    "resolving each issue."
                ),
                "system_prompt": (
                    "You are an expert Docker container log analyzer. Your task is to analyze "
                    "container logs, identify issues, and provide actionable recommendations. "
                    "Focus on identifying patterns, errors, and anomalies that might indicate "
                    "problems with the container or application."
                ),
                "output_format": {
                    "summary": "A brief summary of the analysis",
                    "issues": [
                        {
                            "title": "Issue title",
                            "description": "Detailed description of the issue",
                            "severity": "critical|error|warning|info",
                            "evidence": "Log lines or patterns that indicate this issue",
                        }
                    ],
                    "recommendations": [
                        {
                            "title": "Recommendation title",
                            "description": "Detailed description of the recommendation",
                            "steps": ["Step 1", "Step 2", "..."],
                        }
                    ],
                },
            },
            "error_analysis": {
                "name": "Error Analysis",
                "description": "Template for analyzing error logs",
                "prompt": (
                    "Analyze the following Docker container error logs and identify the root causes "
                    "of the errors. Focus on critical errors and exceptions. Provide detailed "
                    "explanations of each error and specific recommendations for resolving them."
                ),
                "system_prompt": (
                    "You are an expert in debugging and error analysis for Docker containers. "
                    "Your task is to analyze error logs, identify root causes, and provide "
                    "actionable recommendations for resolving the errors."
                ),
                "output_format": {
                    "summary": "A brief summary of the errors found",
                    "issues": [
                        {
                            "title": "Error title",
                            "description": "Detailed description of the error",
                            "severity": "critical|error|warning|info",
                            "error_type": "Type of error (e.g., NullPointerException)",
                            "stack_trace": "Relevant stack trace if available",
                        }
                    ],
                    "recommendations": [
                        {
                            "title": "Recommendation title",
                            "description": "Detailed description of the recommendation",
                            "steps": ["Step 1", "Step 2", "..."],
                            "code_example": "Example code fix if applicable",
                        }
                    ],
                },
            },
            "performance_analysis": {
                "name": "Performance Analysis",
                "description": "Template for analyzing performance-related logs",
                "prompt": (
                    "Analyze the following Docker container logs and identify any performance issues "
                    "or bottlenecks. Focus on slow operations, timeouts, high resource usage, and "
                    "other performance-related indicators. Provide specific recommendations for "
                    "improving performance."
                ),
                "system_prompt": (
                    "You are an expert in performance optimization for Docker containers. "
                    "Your task is to analyze logs, identify performance bottlenecks, and provide "
                    "actionable recommendations for improving performance."
                ),
                "output_format": {
                    "summary": "A brief summary of the performance issues found",
                    "issues": [
                        {
                            "title": "Performance issue title",
                            "description": "Detailed description of the performance issue",
                            "severity": "critical|error|warning|info",
                            "metrics": {
                                "operation": "Operation name",
                                "average_time": "Average time in ms",
                                "max_time": "Maximum time in ms",
                            },
                        }
                    ],
                    "recommendations": [
                        {
                            "title": "Recommendation title",
                            "description": "Detailed description of the recommendation",
                            "expected_improvement": "Expected performance improvement",
                            "steps": ["Step 1", "Step 2", "..."],
                        }
                    ],
                },
            },
            "security_analysis": {
                "name": "Security Analysis",
                "description": "Template for analyzing security-related logs",
                "prompt": (
                    "Analyze the following Docker container logs and identify any security issues, "
                    "vulnerabilities, or suspicious activities. Focus on authentication failures, "
                    "access control issues, injection attempts, and other security-related indicators. "
                    "Provide specific recommendations for addressing security concerns."
                ),
                "system_prompt": (
                    "You are an expert in container security. Your task is to analyze logs, "
                    "identify security issues and vulnerabilities, and provide actionable "
                    "recommendations for improving security."
                ),
                "output_format": {
                    "summary": "A brief summary of the security issues found",
                    "issues": [
                        {
                            "title": "Security issue title",
                            "description": "Detailed description of the security issue",
                            "severity": "critical|error|warning|info",
                            "cve": "CVE identifier if applicable",
                            "attack_vector": "How the vulnerability could be exploited",
                        }
                    ],
                    "recommendations": [
                        {
                            "title": "Recommendation title",
                            "description": "Detailed description of the recommendation",
                            "priority": "high|medium|low",
                            "steps": ["Step 1", "Step 2", "..."],
                        }
                    ],
                },
            },
        }

        # Check if templates directory exists
        if not os.path.exists(self.templates_dir):
            try:
                os.makedirs(self.templates_dir, exist_ok=True)
                logger.info(f"Created templates directory: {self.templates_dir}")

                # Save default templates
                for template_id, template in templates.items():
                    file_path = os.path.join(self.templates_dir, f"{template_id}.json")
                    with open(file_path, "w") as f:
                        json.dump(template, f, indent=2)
                    logger.debug(f"Saved template to {file_path}")
            except Exception as e:
                logger.error(f"Error creating templates directory: {str(e)}")
        else:
            # Load templates from directory
            try:
                for filename in os.listdir(self.templates_dir):
                    if filename.endswith(".json"):
                        file_path = os.path.join(self.templates_dir, filename)
                        try:
                            with open(file_path, "r") as f:
                                template_data = json.load(f)
                                template_id = os.path.splitext(filename)[0]
                                templates[template_id] = template_data
                                logger.debug(f"Loaded template from {file_path}")
                        except Exception as e:
                            logger.error(
                                f"Error loading template from {file_path}: {str(e)}"
                            )
            except Exception as e:
                logger.error(f"Error loading templates from directory: {str(e)}")

        return templates

    def save_template(self, template_id: str, template: Dict[str, Any]) -> bool:
        """
        Save an analysis template.

        Args:
            template_id: Template ID
            template: Template data

        Returns:
            bool: True if the template was saved
        """
        if not os.path.exists(self.templates_dir):
            try:
                os.makedirs(self.templates_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating templates directory: {str(e)}")
                return False

        try:
            file_path = os.path.join(self.templates_dir, f"{template_id}.json")
            with open(file_path, "w") as f:
                json.dump(template, f, indent=2)

            # Update templates dictionary
            self.templates[template_id] = template

            logger.debug(f"Saved template to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving template: {str(e)}")
            return False

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an analysis template.

        Args:
            template_id: Template ID

        Returns:
            Optional[Dict[str, Any]]: Template data or None
        """
        return self.templates.get(template_id)

    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all analysis templates.

        Returns:
            Dict[str, Dict[str, Any]]: All templates
        """
        return self.templates

    def analyze_container_logs(
        self,
        container_id: str,
        template_id: str = "default",
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
        confirm_cost: bool = True,
    ) -> AnalysisResult:
        """
        Analyze logs for a specific container.

        Args:
            container_id: Container ID
            template_id: Analysis template ID
            since: Include logs since this timestamp
            until: Include logs until this timestamp
            limit: Maximum number of logs to analyze
            confirm_cost: Whether to confirm cost before analysis

        Returns:
            AnalysisResult: Analysis result

        Raises:
            ValueError: If container not found or AI provider not available
        """
        if not self.ai_provider:
            try:
                self.ai_provider = get_ai_provider()
            except AIProviderError as e:
                raise ValueError(f"AI provider not available: {str(e)}")

        # Get template
        template = self.get_template(template_id)
        if not template:
            logger.warning(f"Template '{template_id}' not found, using default")
            template = self.get_template("default")
            if not template:
                raise ValueError("Default template not found")

        # Get container logs
        start_time = time.time()
        logs = self.log_collection_manager.get_container_logs(
            container_id=container_id,
            since=since,
            until=until,
            limit=limit,
        )

        if not logs:
            raise ValueError(f"No logs found for container {container_id}")

        # Get container name
        container_name = logs[0].container_name

        # Get pattern matches
        pattern_matches = []
        for log_entry in logs:
            matches = self.pattern_recognition_engine.process_log(log_entry)
            pattern_matches.extend(matches)

        # Prepare logs for analysis
        log_text = "\n".join(str(log) for log in logs)

        # Prepare pattern matches for analysis
        pattern_matches_text = ""
        if pattern_matches:
            pattern_matches_text = "Pattern Matches:\n"
            for match in pattern_matches:
                pattern = self.pattern_recognition_engine.get_pattern(match.pattern_id)
                if pattern:
                    pattern_matches_text += (
                        f"- Pattern: {pattern.name} (Severity: {pattern.severity})\n"
                        f"  Match: {match.match_text}\n"
                        f"  Log: {match.log_entry}\n\n"
                    )

        # Prepare context for AI analysis
        context = {
            "container_id": container_id,
            "container_name": container_name,
            "log_count": len(logs),
            "time_range": {
                "start": logs[0].timestamp.isoformat() if logs else None,
                "end": logs[-1].timestamp.isoformat() if logs else None,
            },
            "logs": log_text,
            "pattern_matches": pattern_matches_text,
        }

        # Prepare query
        system_prompt = template.get("system_prompt", "")
        prompt = template.get("prompt", "")
        output_format = template.get("output_format", {})

        query = (
            f"{prompt}\n\n"
            f"Please provide your analysis in the following JSON format:\n"
            f"{json.dumps(output_format, indent=2)}\n\n"
        )

        # Estimate cost
        if confirm_cost:
            # Convert context to string for cost estimation
            context_str = json.dumps(context, indent=2)

            # Estimate cost
            cost_info = self.ai_provider.estimate_cost(
                context_str + "\n\n" + system_prompt + "\n\n" + query
            )

            # Log cost information
            logger.info(
                f"Estimated cost for log analysis: "
                f"${cost_info['estimated_cost_usd']:.4f} "
                f"({cost_info['input_tokens']} input tokens, "
                f"{cost_info['output_tokens']} output tokens)"
            )

            # Confirm cost
            if not self.ai_provider.confirm_cost(cost_info):
                raise ValueError(
                    f"Analysis cost exceeds budget limits: "
                    f"${cost_info['estimated_cost_usd']:.4f}"
                )

        # Analyze with AI
        # Check if the provider supports system_prompt parameter
        provider_capabilities = getattr(
            self.ai_provider, "report_capabilities", lambda: {}
        )()

        if provider_capabilities.get("function_calling", False):
            # Provider likely supports system_prompt as a parameter
            try:
                analysis = self.ai_provider.analyze(
                    context=context,
                    query=query,
                    system_prompt=system_prompt,
                )
            except TypeError:
                # Fallback if system_prompt is not supported
                combined_query = f"{system_prompt}\n\n{query}"
                analysis = self.ai_provider.analyze(
                    context=context,
                    query=combined_query,
                )
        else:
            # For providers that don't support system_prompt, combine with query
            combined_query = f"{system_prompt}\n\n{query}"
            analysis = self.ai_provider.analyze(
                context=context,
                query=combined_query,
            )

        # Parse analysis result
        try:
            result_json = json.loads(analysis["analysis"])
        except json.JSONDecodeError:
            # Try to extract JSON from text
            try:
                # Look for JSON block in markdown
                import re

                json_match = re.search(
                    r"```json\n(.*?)\n```", analysis["analysis"], re.DOTALL
                )
                if json_match:
                    result_json = json.loads(json_match.group(1))
                else:
                    # Fallback to simple parsing
                    result_json = {
                        "summary": analysis["analysis"],
                        "issues": [],
                        "recommendations": [],
                    }
            except Exception:
                # Fallback to simple parsing
                result_json = {
                    "summary": analysis["analysis"],
                    "issues": [],
                    "recommendations": [],
                }

        # Create analysis result
        analysis_result = AnalysisResult(
            container_id=container_id,
            container_name=container_name,
            timestamp=datetime.now(),
            summary=result_json.get("summary", ""),
            issues=result_json.get("issues", []),
            recommendations=result_json.get("recommendations", []),
            pattern_matches=[match.to_dict() for match in pattern_matches],
            ai_provider=analysis["provider"],
            ai_model=analysis["model"],
            analysis_duration=time.time() - start_time,
            log_count=len(logs),
        )

        # Add to history
        self.analysis_history.append(analysis_result)

        # Trim history if needed
        if len(self.analysis_history) > self.max_history_size:
            self.analysis_history = self.analysis_history[-self.max_history_size :]

        # Record usage if available
        try:
            if (
                hasattr(self.ai_provider, "usage_tracker")
                and self.ai_provider.usage_tracker
            ):
                # Extract token counts from response if available
                input_tokens = (
                    cost_info["input_tokens"] if "input_tokens" in locals() else 0
                )
                output_tokens = analysis.get("output_tokens", 0)
                if "raw_response" in analysis and "usage" in analysis["raw_response"]:
                    input_tokens = analysis["raw_response"]["usage"].get(
                        "prompt_tokens", input_tokens
                    )
                    output_tokens = analysis["raw_response"]["usage"].get(
                        "completion_tokens", output_tokens
                    )

                # Calculate cost
                cost = 0.0
                if "estimated_cost_usd" in locals() and "cost_info" in locals():
                    cost = cost_info["estimated_cost_usd"]

                # Record usage
                self.ai_provider.usage_tracker.record_usage(
                    provider=analysis["provider"],
                    model=analysis["model"],
                    operation="analyze_container_logs",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost,
                )
        except Exception as e:
            logger.debug(f"Error recording usage: {str(e)}")

        return analysis_result

    def get_analysis_history(
        self,
        container_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[AnalysisResult]:
        """
        Get analysis history.

        Args:
            container_id: Filter by container ID
            since: Filter by timestamp
            limit: Maximum number of results to return

        Returns:
            List[AnalysisResult]: Analysis history
        """
        # Start with all history
        history = self.analysis_history.copy()

        # Filter by container ID
        if container_id:
            history = [h for h in history if h.container_id == container_id]

        # Filter by timestamp
        if since:
            history = [h for h in history if h.timestamp >= since]

        # Sort by timestamp (newest first)
        history.sort(key=lambda h: h.timestamp, reverse=True)

        # Apply limit
        if limit and len(history) > limit:
            history = history[:limit]

        return history

    def get_latest_analysis(self, container_id: str) -> Optional[AnalysisResult]:
        """
        Get the latest analysis for a container.

        Args:
            container_id: Container ID

        Returns:
            Optional[AnalysisResult]: Latest analysis or None
        """
        history = self.get_analysis_history(container_id=container_id, limit=1)
        return history[0] if history else None

    def clear_analysis_history(self) -> None:
        """Clear analysis history."""
        self.analysis_history.clear()


# Singleton instance
_log_analyzer = None


def get_log_analyzer(ai_provider_name: Optional[str] = None) -> LogAnalyzer:
    """
    Get the log analyzer (singleton).

    Args:
        ai_provider_name: AI provider name (default: from config)

    Returns:
        LogAnalyzer: Log analyzer
    """
    global _log_analyzer
    if _log_analyzer is None:
        _log_analyzer = LogAnalyzer(ai_provider_name)

    return _log_analyzer
