"""
Prompt template module for DockerForge.

This module provides functionality to manage AI prompt templates.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger

logger = get_logger("prompt_template")


class PromptTemplate:
    """A template for AI prompts with version tracking and variables."""

    def __init__(self, name: str, template: str, version: str = "1.0.0",
                 description: str = "", variables: List[str] = None):
        """
        Initialize a prompt template.

        Args:
            name: Template name
            template: Template text
            version: Template version
            description: Template description
            variables: List of variable names used in the template
        """
        self.name = name
        self.template = template
        self.version = version
        self.description = description
        self.variables = variables or []
        self.performance_metrics = {
            "success_rate": 0.0,
            "avg_tokens": 0,
            "usage_count": 0,
        }

    def render(self, **kwargs) -> str:
        """
        Render the template with the provided variables.

        Args:
            **kwargs: Variables to substitute in the template

        Returns:
            str: Rendered template

        Raises:
            ValueError: If a required variable is missing
        """
        # Check for missing variables
        missing = [var for var in self.variables if var not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")

        # Render the template
        rendered = self.template
        for var, value in kwargs.items():
            placeholder = "{" + var + "}"
            rendered = rendered.replace(placeholder, str(value))

        return rendered

    def update_metrics(self, success: bool, tokens: int):
        """
        Update performance metrics for this template.

        Args:
            success: Whether the template was successful
            tokens: Number of tokens used
        """
        self.performance_metrics["usage_count"] += 1

        # Update success rate
        current_successes = self.performance_metrics["success_rate"] * (self.performance_metrics["usage_count"] - 1)
        if success:
            current_successes += 1
        self.performance_metrics["success_rate"] = current_successes / self.performance_metrics["usage_count"]

        # Update average tokens
        current_total = self.performance_metrics["avg_tokens"] * (self.performance_metrics["usage_count"] - 1)
        current_total += tokens
        self.performance_metrics["avg_tokens"] = current_total / self.performance_metrics["usage_count"]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to dictionary.

        Returns:
            Dict[str, Any]: Template as dictionary
        """
        return {
            "name": self.name,
            "template": self.template,
            "version": self.version,
            "description": self.description,
            "variables": self.variables,
            "performance_metrics": self.performance_metrics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """
        Create template from dictionary.

        Args:
            data: Template data

        Returns:
            PromptTemplate: Template instance
        """
        template = cls(
            name=data["name"],
            template=data["template"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            variables=data.get("variables", []),
        )

        if "performance_metrics" in data:
            template.performance_metrics = data["performance_metrics"]

        return template

    @classmethod
    def from_file(cls, template_name: str) -> 'PromptTemplate':
        """
        Load a template from a file.

        Args:
            template_name: Name of the template file (without extension)

        Returns:
            PromptTemplate: Template instance

        Raises:
            FileNotFoundError: If template file not found
            ValueError: If template file is invalid
        """
        # Get template manager
        from src.core.prompt_template import get_template_manager

        # Get template from manager
        template = get_template_manager().get_template(template_name)
        if template is None:
            # Try to load default templates
            default_templates_dir = os.path.join(os.path.dirname(__file__), "../templates")
            template_path = os.path.join(default_templates_dir, f"{template_name}.json")

            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template not found: {template_name}")

            try:
                with open(template_path, "r") as f:
                    template_data = json.load(f)

                template = cls.from_dict(template_data)
            except Exception as e:
                raise ValueError(f"Invalid template file: {str(e)}")

        return template


class PromptTemplateManager:
    """Manager for prompt templates with storage and retrieval."""

    def __init__(self):
        """Initialize the prompt template manager."""
        # Get templates directory from config
        templates_dir = get_config("ai.templates.directory", "~/.dockerforge/templates")
        self.templates_dir = os.path.expanduser(templates_dir)
        os.makedirs(self.templates_dir, exist_ok=True)

        # Load templates
        self.templates = {}
        self.load_templates()

    def load_templates(self):
        """Load templates from the templates directory."""
        if not os.path.exists(self.templates_dir):
            return

        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.templates_dir, filename), "r") as f:
                        template_data = json.load(f)

                    template = PromptTemplate.from_dict(template_data)
                    self.templates[template.name] = template
                    logger.debug(f"Loaded template: {template.name} (v{template.version})")
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {str(e)}")

    def save_template(self, template: PromptTemplate):
        """
        Save a template to the templates directory.

        Args:
            template: Template to save
        """
        filename = f"{template.name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.templates_dir, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(template.to_dict(), f, indent=2)

            logger.debug(f"Saved template: {template.name} (v{template.version})")
        except Exception as e:
            logger.error(f"Error saving template {filename}: {str(e)}")

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        Get a template by name.

        Args:
            name: Template name

        Returns:
            Optional[PromptTemplate]: Template or None if not found
        """
        return self.templates.get(name)

    def create_template(self, name: str, template: str, **kwargs) -> PromptTemplate:
        """
        Create a new template.

        Args:
            name: Template name
            template: Template text
            **kwargs: Additional template parameters

        Returns:
            PromptTemplate: Created template
        """
        template_obj = PromptTemplate(name=name, template=template, **kwargs)
        self.templates[name] = template_obj
        self.save_template(template_obj)
        return template_obj

    def update_template(self, name: str, template: str, **kwargs) -> Optional[PromptTemplate]:
        """
        Update an existing template.

        Args:
            name: Template name
            template: New template text
            **kwargs: Additional template parameters

        Returns:
            Optional[PromptTemplate]: Updated template or None if not found
        """
        if name not in self.templates:
            return None

        # Get existing template
        existing = self.templates[name]

        # Create new version
        version = kwargs.get("version", self._increment_version(existing.version))

        # Create updated template
        template_obj = PromptTemplate(
            name=name,
            template=template,
            version=version,
            description=kwargs.get("description", existing.description),
            variables=kwargs.get("variables", existing.variables),
        )

        # Copy performance metrics if not reset
        if not kwargs.get("reset_metrics", False):
            template_obj.performance_metrics = existing.performance_metrics

        # Save and return
        self.templates[name] = template_obj
        self.save_template(template_obj)
        return template_obj

    def delete_template(self, name: str) -> bool:
        """
        Delete a template.

        Args:
            name: Template name

        Returns:
            bool: True if deleted, False if not found
        """
        if name not in self.templates:
            return False

        # Remove from memory
        del self.templates[name]

        # Remove from disk
        filename = f"{name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.templates_dir, filename)

        try:
            if os.path.exists(filepath):
                os.remove(filepath)

            logger.debug(f"Deleted template: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting template {filename}: {str(e)}")
            return False

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all templates.

        Returns:
            List[Dict[str, Any]]: List of template information
        """
        return [
            {
                "name": template.name,
                "version": template.version,
                "description": template.description,
                "variables": template.variables,
                "usage_count": template.performance_metrics["usage_count"],
                "success_rate": template.performance_metrics["success_rate"],
            }
            for template in self.templates.values()
        ]

    def _increment_version(self, version: str) -> str:
        """
        Increment version number.

        Args:
            version: Current version

        Returns:
            str: Incremented version
        """
        try:
            # Parse version
            parts = version.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid version format")

            major, minor, patch = map(int, parts)

            # Increment patch version
            patch += 1

            # Return new version
            return f"{major}.{minor}.{patch}"
        except Exception:
            # If version parsing fails, just append .1
            return f"{version}.1"


# Singleton instance
_template_manager = None


def get_template_manager() -> PromptTemplateManager:
    """
    Get the prompt template manager (singleton).

    Returns:
        PromptTemplateManager: Prompt template manager
    """
    global _template_manager
    if _template_manager is None:
        _template_manager = PromptTemplateManager()

    return _template_manager


def get_template(name: str) -> Optional[PromptTemplate]:
    """
    Get a template by name.

    Args:
        name: Template name

    Returns:
        Optional[PromptTemplate]: Template or None if not found
    """
    return get_template_manager().get_template(name)


def render_template(name: str, **kwargs) -> str:
    """
    Render a template with variables.

    Args:
        name: Template name
        **kwargs: Variables to substitute

    Returns:
        str: Rendered template

    Raises:
        ValueError: If template not found or variables missing
    """
    template = get_template(name)
    if template is None:
        raise ValueError(f"Template not found: {name}")

    return template.render(**kwargs)
