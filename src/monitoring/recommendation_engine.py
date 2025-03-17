"""
Recommendation engine module for DockerForge.

This module provides functionality to generate recommendations for resolving
issues detected in container logs.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger
from src.core.ai_provider import get_ai_provider, AIProviderError
from src.monitoring.log_collector import LogEntry, get_log_collection_manager
from src.monitoring.pattern_recognition import (
    PatternMatch, PatternDefinition, get_pattern_recognition_engine
)
from src.monitoring.log_analyzer import AnalysisResult, get_log_analyzer
from src.monitoring.issue_detector import (
    Issue, IssueStatus, IssueSeverity, get_issue_detector
)

logger = get_logger("recommendation_engine")


@dataclass
class RecommendationStep:
    """Step in a recommendation."""
    
    description: str
    command: Optional[str] = None
    code: Optional[str] = None
    manual_action: Optional[str] = None
    verification: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert recommendation step to dictionary.
        
        Returns:
            Dict[str, Any]: Recommendation step as dictionary
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecommendationStep":
        """
        Create recommendation step from dictionary.
        
        Args:
            data: Dictionary with recommendation step data
            
        Returns:
            RecommendationStep: Recommendation step
        """
        return cls(**data)


@dataclass
class Recommendation:
    """Recommendation for resolving an issue."""
    
    id: str
    issue_id: str
    title: str
    description: str
    steps: List[RecommendationStep]
    created_at: datetime
    updated_at: datetime
    applied_at: Optional[datetime] = None
    source: str = "ai"  # ai, pattern, manual
    success_rate: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert recommendation to dictionary.
        
        Returns:
            Dict[str, Any]: Recommendation as dictionary
        """
        result = asdict(self)
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        if self.applied_at:
            result["applied_at"] = self.applied_at.isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recommendation":
        """
        Create recommendation from dictionary.
        
        Args:
            data: Dictionary with recommendation data
            
        Returns:
            Recommendation: Recommendation
        """
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("applied_at"):
            data["applied_at"] = datetime.fromisoformat(data["applied_at"])
        
        # Convert steps
        if "steps" in data:
            data["steps"] = [
                RecommendationStep.from_dict(step) if isinstance(step, dict) else step
                for step in data["steps"]
            ]
        
        return cls(**data)
    
    def mark_as_applied(self) -> None:
        """Mark recommendation as applied."""
        self.applied_at = datetime.now()
        self.updated_at = datetime.now()


class RecommendationEngine:
    """Engine for generating recommendations for resolving issues."""
    
    def __init__(self, ai_provider_name: Optional[str] = None):
        """
        Initialize recommendation engine.
        
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
        self.log_analyzer = get_log_analyzer()
        self.issue_detector = get_issue_detector()
        
        # Recommendations
        self.recommendations: Dict[str, Recommendation] = {}
        
        # Recommendation database
        self.recommendations_dir = get_config(
            "monitoring.recommendations_dir",
            os.path.expanduser("~/.dockerforge/recommendations")
        )
        
        # Load recommendations from database
        self._load_recommendations()
        
        # Recommendation templates
        self.templates_dir = get_config(
            "monitoring.recommendation_templates_dir",
            os.path.expanduser("~/.dockerforge/recommendation_templates")
        )
        
        # Load recommendation templates
        self.templates = self._load_templates()
    
    def _load_recommendations(self) -> None:
        """Load recommendations from database."""
        if not os.path.exists(self.recommendations_dir):
            try:
                os.makedirs(self.recommendations_dir, exist_ok=True)
                logger.info(f"Created recommendations directory: {self.recommendations_dir}")
            except Exception as e:
                logger.error(f"Error creating recommendations directory: {str(e)}")
                return
        
        try:
            # Load recommendations from JSON files
            for filename in os.listdir(self.recommendations_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.recommendations_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            recommendation_data = json.load(f)
                            recommendation = Recommendation.from_dict(recommendation_data)
                            self.recommendations[recommendation.id] = recommendation
                            logger.debug(f"Loaded recommendation from {file_path}")
                    except Exception as e:
                        logger.error(f"Error loading recommendation from {file_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading recommendations from directory: {str(e)}")
    
    def _save_recommendation(self, recommendation: Recommendation) -> bool:
        """
        Save a recommendation to the database.
        
        Args:
            recommendation: Recommendation to save
            
        Returns:
            bool: True if the recommendation was saved
        """
        if not os.path.exists(self.recommendations_dir):
            try:
                os.makedirs(self.recommendations_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Error creating recommendations directory: {str(e)}")
                return False
        
        try:
            file_path = os.path.join(self.recommendations_dir, f"{recommendation.id}.json")
            with open(file_path, "w") as f:
                json.dump(recommendation.to_dict(), f, indent=2)
            
            logger.debug(f"Saved recommendation to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving recommendation: {str(e)}")
            return False
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load recommendation templates.
        
        Returns:
            Dict[str, Dict[str, Any]]: Recommendation templates
        """
        templates = {
            "default": {
                "name": "Default Recommendation",
                "description": "Default template for generating recommendations",
                "prompt": (
                    "Generate a recommendation for resolving the following issue in a Docker container:\n\n"
                    "Issue: {issue_title}\n"
                    "Description: {issue_description}\n"
                    "Container: {container_name}\n\n"
                    "Provide a step-by-step solution that addresses the root cause of the issue. "
                    "Include specific commands or code changes where applicable."
                ),
                "system_prompt": (
                    "You are an expert Docker troubleshooter. Your task is to generate clear, "
                    "actionable recommendations for resolving issues in Docker containers. "
                    "Focus on providing step-by-step instructions that address the root cause "
                    "of the issue, not just the symptoms."
                ),
                "output_format": {
                    "title": "Recommendation title",
                    "description": "Detailed description of the recommendation",
                    "steps": [
                        {
                            "description": "Step description",
                            "command": "Command to execute (if applicable)",
                            "code": "Code to add or modify (if applicable)",
                            "manual_action": "Manual action to take (if applicable)",
                            "verification": "How to verify this step was successful",
                        }
                    ]
                }
            },
            "permission_issue": {
                "name": "Permission Issue",
                "description": "Template for resolving permission issues",
                "prompt": (
                    "Generate a recommendation for resolving the following permission issue in a Docker container:\n\n"
                    "Issue: {issue_title}\n"
                    "Description: {issue_description}\n"
                    "Container: {container_name}\n\n"
                    "Provide a step-by-step solution that addresses the permission issue. "
                    "Include specific commands to fix permissions and verify the solution."
                ),
                "system_prompt": (
                    "You are an expert in Docker security and permissions. Your task is to generate "
                    "clear, actionable recommendations for resolving permission issues in Docker containers. "
                    "Focus on providing secure solutions that follow best practices."
                ),
                "output_format": {
                    "title": "Recommendation title",
                    "description": "Detailed description of the recommendation",
                    "steps": [
                        {
                            "description": "Step description",
                            "command": "Command to execute (if applicable)",
                            "manual_action": "Manual action to take (if applicable)",
                            "verification": "How to verify this step was successful",
                        }
                    ]
                }
            },
            "resource_issue": {
                "name": "Resource Issue",
                "description": "Template for resolving resource-related issues",
                "prompt": (
                    "Generate a recommendation for resolving the following resource issue in a Docker container:\n\n"
                    "Issue: {issue_title}\n"
                    "Description: {issue_description}\n"
                    "Container: {container_name}\n\n"
                    "Provide a step-by-step solution that addresses the resource issue (CPU, memory, disk, etc.). "
                    "Include specific commands to adjust resource limits and verify the solution."
                ),
                "system_prompt": (
                    "You are an expert in Docker resource management. Your task is to generate "
                    "clear, actionable recommendations for resolving resource issues in Docker containers. "
                    "Focus on providing solutions that optimize resource usage and prevent recurrence."
                ),
                "output_format": {
                    "title": "Recommendation title",
                    "description": "Detailed description of the recommendation",
                    "steps": [
                        {
                            "description": "Step description",
                            "command": "Command to execute (if applicable)",
                            "code": "Configuration changes (if applicable)",
                            "verification": "How to verify this step was successful",
                        }
                    ]
                }
            },
            "network_issue": {
                "name": "Network Issue",
                "description": "Template for resolving network-related issues",
                "prompt": (
                    "Generate a recommendation for resolving the following network issue in a Docker container:\n\n"
                    "Issue: {issue_title}\n"
                    "Description: {issue_description}\n"
                    "Container: {container_name}\n\n"
                    "Provide a step-by-step solution that addresses the network issue. "
                    "Include specific commands to diagnose and fix network problems."
                ),
                "system_prompt": (
                    "You are an expert in Docker networking. Your task is to generate "
                    "clear, actionable recommendations for resolving network issues in Docker containers. "
                    "Focus on providing solutions that ensure proper connectivity and follow best practices."
                ),
                "output_format": {
                    "title": "Recommendation title",
                    "description": "Detailed description of the recommendation",
                    "steps": [
                        {
                            "description": "Step description",
                            "command": "Command to execute (if applicable)",
                            "code": "Configuration changes (if applicable)",
                            "verification": "How to verify this step was successful",
                        }
                    ]
                }
            }
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
                            logger.error(f"Error loading template from {file_path}: {str(e)}")
            except Exception as e:
                logger.error(f"Error loading templates from directory: {str(e)}")
        
        return templates
    
    def save_template(self, template_id: str, template: Dict[str, Any]) -> bool:
        """
        Save a recommendation template.
        
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
        Get a recommendation template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Optional[Dict[str, Any]]: Template data or None
        """
        return self.templates.get(template_id)
    
    def get_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all recommendation templates.
        
        Returns:
            Dict[str, Dict[str, Any]]: All templates
        """
        return self.templates
    
    def generate_recommendation_for_issue(
        self,
        issue_id: str,
        template_id: str = "default",
        confirm_cost: bool = True,
    ) -> Optional[Recommendation]:
        """
        Generate a recommendation for an issue.
        
        Args:
            issue_id: Issue ID
            template_id: Template ID
            confirm_cost: Whether to confirm cost before generation
            
        Returns:
            Optional[Recommendation]: Generated recommendation or None
            
        Raises:
            ValueError: If issue not found or AI provider not available
        """
        # Get issue
        issue = self.issue_detector.get_issue(issue_id)
        if not issue:
            raise ValueError(f"Issue not found: {issue_id}")
        
        # Check if there's already a recommendation for this issue
        for recommendation in self.recommendations.values():
            if recommendation.issue_id == issue_id:
                return recommendation
        
        # Get AI provider
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
        logs = self.log_collection_manager.get_container_logs(
            container_id=issue.container_id,
            limit=100,  # Limit to recent logs
        )
        
        # Get pattern matches
        pattern_matches = []
        if issue.pattern_id:
            pattern = self.pattern_recognition_engine.get_pattern(issue.pattern_id)
            if pattern:
                pattern_matches.append({
                    "pattern": pattern.to_dict(),
                    "matches": issue.pattern_matches,
                })
        
        # Prepare context for AI generation
        context = {
            "issue": issue.to_dict(),
            "container_logs": "\n".join(str(log) for log in logs),
            "pattern_matches": pattern_matches,
        }
        
        # Prepare query
        system_prompt = template.get("system_prompt", "")
        prompt_template = template.get("prompt", "")
        output_format = template.get("output_format", {})
        
        # Format prompt
        prompt = prompt_template.format(
            issue_title=issue.title,
            issue_description=issue.description,
            container_name=issue.container_name,
        )
        
        query = (
            f"{prompt}\n\n"
            f"Please provide your recommendation in the following JSON format:\n"
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
                f"Estimated cost for recommendation generation: "
                f"${cost_info['estimated_cost_usd']:.4f} "
                f"({cost_info['input_tokens']} input tokens, "
                f"{cost_info['output_tokens']} output tokens)"
            )
            
            # Confirm cost
            if not self.ai_provider.confirm_cost(cost_info):
                raise ValueError(
                    f"Generation cost exceeds budget limits: "
                    f"${cost_info['estimated_cost_usd']:.4f}"
                )
        
        # Generate recommendation with AI
        generation = self.ai_provider.analyze(
            context=context,
            query=query,
            system_prompt=system_prompt,
        )
        
        # Parse generation result
        try:
            result_json = json.loads(generation["analysis"])
        except json.JSONDecodeError:
            # Try to extract JSON from text
            try:
                # Look for JSON block in markdown
                import re
                json_match = re.search(r"```json\n(.*?)\n```", generation["analysis"], re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group(1))
                else:
                    # Fallback to simple parsing
                    result_json = {
                        "title": f"Recommendation for {issue.title}",
                        "description": generation["analysis"],
                        "steps": [],
                    }
            except Exception:
                # Fallback to simple parsing
                result_json = {
                    "title": f"Recommendation for {issue.title}",
                    "description": generation["analysis"],
                    "steps": [],
                }
        
        # Create steps
        steps = []
        for step_data in result_json.get("steps", []):
            step = RecommendationStep(
                description=step_data.get("description", ""),
                command=step_data.get("command"),
                code=step_data.get("code"),
                manual_action=step_data.get("manual_action"),
                verification=step_data.get("verification"),
            )
            steps.append(step)
        
        # Create recommendation ID
        recommendation_id = f"{issue_id}_rec_{int(time.time())}"
        
        # Create recommendation
        recommendation = Recommendation(
            id=recommendation_id,
            issue_id=issue_id,
            title=result_json.get("title", f"Recommendation for {issue.title}"),
            description=result_json.get("description", ""),
            steps=steps,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="ai",
            tags=["ai-generated"],
        )
        
        # Add recommendation to database
        self.recommendations[recommendation.id] = recommendation
        self._save_recommendation(recommendation)
        
        # Record usage if available
        try:
            if hasattr(self.ai_provider, 'usage_tracker') and self.ai_provider.usage_tracker:
                # Extract token counts from response if available
                input_tokens = cost_info['input_tokens'] if 'input_tokens' in locals() else 0
                output_tokens = generation.get('output_tokens', 0)
                if 'raw_response' in generation and 'usage' in generation['raw_response']:
                    input_tokens = generation['raw_response']['usage'].get('prompt_tokens', input_tokens)
                    output_tokens = generation['raw_response']['usage'].get('completion_tokens', output_tokens)
                
                # Calculate cost
                cost = 0.0
                if 'estimated_cost_usd' in locals() and 'cost_info' in locals():
                    cost = cost_info['estimated_cost_usd']
                
                # Record usage
                self.ai_provider.usage_tracker.record_usage(
                    provider=generation['provider'],
                    model=generation['model'],
                    operation='generate_recommendation',
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost,
                )
        except Exception as e:
            logger.debug(f"Error recording usage: {str(e)}")
        
        logger.info(f"Generated recommendation: {recommendation.id} - {recommendation.title}")
        
        return recommendation
    
    def create_recommendation_from_pattern(self, issue_id: str) -> Optional[Recommendation]:
        """
        Create a recommendation from a pattern solution.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Optional[Recommendation]: Created recommendation or None
        """
        # Get issue
        issue = self.issue_detector.get_issue(issue_id)
        if not issue or not issue.pattern_id:
            return None
        
        # Get pattern
        pattern = self.pattern_recognition_engine.get_pattern(issue.pattern_id)
        if not pattern or not pattern.solution:
            return None
        
        # Create recommendation ID
        recommendation_id = f"{issue_id}_pattern_{int(time.time())}"
        
        # Create steps
        steps = [
            RecommendationStep(
                description=pattern.solution,
                manual_action="Apply the solution as described",
                verification="Check if the issue is resolved",
            )
        ]
        
        # Create recommendation
        recommendation = Recommendation(
            id=recommendation_id,
            issue_id=issue_id,
            title=f"Solution for {pattern.name}",
            description=f"Recommended solution for the detected pattern: {pattern.name}",
            steps=steps,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="pattern",
            tags=["pattern-based"],
        )
        
        # Add recommendation to database
        self.recommendations[recommendation.id] = recommendation
        self._save_recommendation(recommendation)
        
        logger.info(f"Created recommendation from pattern: {recommendation.id} - {recommendation.title}")
        
        return recommendation
    
    def create_recommendation_manual(
        self,
        issue_id: str,
        title: str,
        description: str,
        steps: List[Dict[str, Any]],
        tags: Optional[List[str]] = None,
    ) -> Recommendation:
        """
        Create a recommendation manually.
        
        Args:
            issue_id: Issue ID
            title: Recommendation title
            description: Recommendation description
            steps: Recommendation steps
            tags: Recommendation tags
            
        Returns:
            Recommendation: Created recommendation
            
        Raises:
            ValueError: If issue not found
        """
        # Get issue
        issue = self.issue_detector.get_issue(issue_id)
        if not issue:
            raise ValueError(f"Issue not found: {issue_id}")
        
        # Create recommendation ID
        recommendation_id = f"{issue_id}_manual_{int(time.time())}"
        
        # Create steps
        recommendation_steps = []
        for step_data in steps:
            step = RecommendationStep(
                description=step_data.get("description", ""),
                command=step_data.get("command"),
                code=step_data.get("code"),
                manual_action=step_data.get("manual_action"),
                verification=step_data.get("verification"),
            )
            recommendation_steps.append(step)
        
        # Create recommendation
        recommendation = Recommendation(
            id=recommendation_id,
            issue_id=issue_id,
            title=title,
            description=description,
            steps=recommendation_steps,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="manual",
            tags=tags or ["manual"],
        )
        
        # Add recommendation to database
        self.recommendations[recommendation.id] = recommendation
        self._save_recommendation(recommendation)
        
        logger.info(f"Created manual recommendation: {recommendation.id} - {recommendation.title}")
        
        return recommendation
    
    def get_recommendation(self, recommendation_id: str) -> Optional[Recommendation]:
        """
        Get a recommendation by ID.
        
        Args:
            recommendation_id: Recommendation ID
            
        Returns:
            Optional[Recommendation]: Recommendation or None
        """
        return self.recommendations.get(recommendation_id)
    
    def get_recommendations_for_issue(self, issue_id: str) -> List[Recommendation]:
        """
        Get recommendations for an issue.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            List[Recommendation]: Recommendations for the issue
        """
        return [r for r in self.recommendations.values() if r.issue_id == issue_id]
    
    def get_all_recommendations(self) -> List[Recommendation]:
        """
        Get all recommendations.
        
        Returns:
            List[Recommendation]: All recommendations
        """
        return list(self.recommendations.values())
    
    def apply_recommendation(self, recommendation_id: str) -> bool:
        """
        Mark a recommendation as applied.
        
        Args:
            recommendation_id: Recommendation ID
            
        Returns:
            bool: True if the recommendation was marked as applied
        """
        recommendation = self.get_recommendation(recommendation_id)
        if not recommendation:
            return False
        
        # Mark as applied
        recommendation.mark_as_applied()
        
        # Update issue status
        issue = self.issue_detector.get_issue(recommendation.issue_id)
        if issue and issue.status != IssueStatus.RESOLVED:
            self.issue_detector.update_issue(
                issue_id=issue.id,
                status=IssueStatus.RESOLVED,
                resolution=f"Applied recommendation: {recommendation.title}",
            )
        
        # Save recommendation
        self._save_recommendation(recommendation)
        
        logger.info(f"Marked recommendation as applied: {recommendation.id}")
        
        return True
    
    def delete_recommendation(self, recommendation_id: str) -> bool:
        """
        Delete a recommendation.
        
        Args:
            recommendation_id: Recommendation ID
            
        Returns:
            bool: True if the recommendation was deleted
        """
        if recommendation_id not in self.recommendations:
            return False
        
        # Remove from memory
        del self.recommendations[recommendation_id]
        
        # Remove from disk
        try:
            file_path = os.path.join(self.recommendations_dir, f"{recommendation_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            
            logger.info(f"Deleted recommendation: {recommendation_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting recommendation file: {str(e)}")
            return False
    
    def get_recommendation_for_issue(self, issue_id: str) -> Optional[Recommendation]:
        """
        Get or generate a recommendation for an issue.
        
        Args:
            issue_id: Issue ID
            
        Returns:
            Optional[Recommendation]: Recommendation or None
        """
        # Check if there's already a recommendation for this issue
        recommendations = self.get_recommendations_for_issue(issue_id)
        if recommendations:
            return recommendations[0]
        
        # Get issue
        issue = self.issue_detector.get_issue(issue_id)
        if not issue:
            return None
        
        # Try to create recommendation from pattern
        if issue.pattern_id:
            recommendation = self.create_recommendation_from_pattern(issue_id)
            if recommendation:
                return recommendation
        
        # Generate recommendation with AI
        try:
            return self.generate_recommendation_for_issue(issue_id)
        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            return None


# Singleton instance
_recommendation_engine = None


def get_recommendation_engine(ai_provider_name: Optional[str] = None) -> RecommendationEngine:
    """
    Get the recommendation engine (singleton).
    
    Args:
        ai_provider_name: AI provider name (default: from config)
        
    Returns:
        RecommendationEngine: Recommendation engine
    """
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine(ai_provider_name)
    
    return _recommendation_engine
