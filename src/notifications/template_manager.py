"""
Template manager module for DockerForge notifications.

This module provides functionality for managing notification templates.
"""

import json
import logging
import os
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import jinja2

from src.config.config_manager import get_config
from src.utils.logging_manager import get_logger

# Set up logging
logger = get_logger("template_manager")


class NotificationTemplate:
    """Notification template class."""

    def __init__(
        self,
        template_id: str,
        name: str,
        description: Optional[str] = None,
        html_template: Optional[str] = None,
        text_template: Optional[str] = None,
        slack_template: Optional[str] = None,
        discord_template: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a notification template.

        Args:
            template_id: The template ID
            name: The template name
            description: Optional template description
            html_template: Optional HTML template
            text_template: Optional text template
            slack_template: Optional Slack template
            discord_template: Optional Discord template
            metadata: Optional metadata
        """
        self.template_id = template_id
        self.name = name
        self.description = description
        self.html_template = html_template
        self.text_template = text_template
        self.slack_template = slack_template
        self.discord_template = discord_template
        self.metadata = metadata or {}
        self.created_at = None
        self.updated_at = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the template to a dictionary.

        Returns:
            A dictionary representation of the template
        """
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "html_template": self.html_template,
            "text_template": self.text_template,
            "slack_template": self.slack_template,
            "discord_template": self.discord_template,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotificationTemplate":
        """Create a template from a dictionary.

        Args:
            data: The dictionary to create the template from

        Returns:
            A new NotificationTemplate instance
        """
        template = cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data.get("description"),
            html_template=data.get("html_template"),
            text_template=data.get("text_template"),
            slack_template=data.get("slack_template"),
            discord_template=data.get("discord_template"),
            metadata=data.get("metadata", {}),
        )

        if data.get("created_at"):
            template.created_at = datetime.fromisoformat(data["created_at"])

        if data.get("updated_at"):
            template.updated_at = datetime.fromisoformat(data["updated_at"])

        return template

    def render(self, template_type: str, context: Dict[str, Any]) -> Optional[str]:
        """Render the template with the given context.

        Args:
            template_type: The template type (html, text, slack, discord)
            context: The context to render the template with

        Returns:
            The rendered template, or None if the template type is not available
        """
        template_content = None

        if template_type == "html" and self.html_template:
            template_content = self.html_template
        elif template_type == "text" and self.text_template:
            template_content = self.text_template
        elif template_type == "slack" and self.slack_template:
            template_content = self.slack_template
        elif template_type == "discord" and self.discord_template:
            template_content = self.discord_template
        else:
            return None

        try:
            # Create Jinja2 environment
            env = jinja2.Environment(
                loader=jinja2.BaseLoader(),
                autoescape=jinja2.select_autoescape(["html"]),
            )

            # Add custom filters
            env.filters["datetime"] = lambda dt, format="%Y-%m-%d %H:%M:%S": (
                dt.strftime(format) if dt else ""
            )

            # Compile template
            template = env.from_string(template_content)

            # Render template
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {self.template_id}: {str(e)}")
            return None


class TemplateManager:
    """Manager for notification templates."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Create a new TemplateManager instance (singleton)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TemplateManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        """Initialize the template manager."""
        if self._initialized:
            return

        self._initialized = True
        self._templates = {}
        self._jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=jinja2.select_autoescape(["html"]),
        )

        # Add custom filters
        self._jinja_env.filters["datetime"] = lambda dt, format="%Y-%m-%d %H:%M:%S": (
            dt.strftime(format) if dt else ""
        )

        # Load templates
        self._load_templates()

        # Create default templates if none exist
        if not self._templates:
            self._create_default_templates()

        logger.info("Template manager initialized")

    def _load_templates(self) -> None:
        """Load templates from disk."""
        # Load from templates directory
        templates_dir = os.path.expanduser(
            get_config(
                "notifications.templates.directory",
                "~/.dockerforge/notification_templates",
            )
        )

        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir, exist_ok=True)
            logger.info(f"Created templates directory: {templates_dir}")
            return

        # Load templates from JSON files
        for filename in os.listdir(templates_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(templates_dir, filename), "r") as f:
                        data = json.load(f)
                        template = NotificationTemplate.from_dict(data)
                        self._templates[template.template_id] = template
                        logger.debug(f"Loaded template: {template.template_id}")
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {str(e)}")

        logger.info(f"Loaded {len(self._templates)} templates from {templates_dir}")

    def _save_template(self, template: NotificationTemplate) -> None:
        """Save a template to disk.

        Args:
            template: The template to save
        """
        templates_dir = os.path.expanduser(
            get_config(
                "notifications.templates.directory",
                "~/.dockerforge/notification_templates",
            )
        )

        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir, exist_ok=True)

        try:
            filename = os.path.join(templates_dir, f"{template.template_id}.json")

            with open(filename, "w") as f:
                json.dump(template.to_dict(), f, indent=2)

            logger.debug(f"Saved template: {template.template_id}")
        except Exception as e:
            logger.error(f"Error saving template {template.template_id}: {str(e)}")

    def _create_default_templates(self) -> None:
        """Create default notification templates."""
        # Default template
        default_template = NotificationTemplate(
            template_id="default",
            name="Default Template",
            description="Default notification template",
            html_template="<html><body><h1>{{ title }}</h1><p>{{ message }}</p></body></html>",
            text_template="{{ title }}\n\n{{ message }}",
            slack_template='{"blocks":[{"type":"header","text":{"type":"plain_text","text":"{{ title }}","emoji":true}}]}',
            discord_template='{"embeds":[{"title":"{{ title }}","description":"{{ message }}"}]}',
        )

        # Set timestamps
        default_template.created_at = datetime.now()
        default_template.updated_at = datetime.now()

        # Add to templates
        self._templates[default_template.template_id] = default_template

        # Save to disk
        self._save_template(default_template)

        logger.info("Created default notification template")

        # Container exit template
        container_exit_template = NotificationTemplate(
            template_id="container_exit",
            name="Container Exit Template",
            description="Template for container exit notifications",
            html_template="<html><body><h1>{{ title }}</h1><p>Container {{ container_name }} exited with code {{ exit_code }}</p></body></html>",
            text_template="{{ title }}\n\nContainer {{ container_name }} exited with code {{ exit_code }}",
            slack_template='{"blocks":[{"type":"header","text":{"type":"plain_text","text":"{{ title }}","emoji":true}}]}',
            discord_template='{"embeds":[{"title":"{{ title }}","description":"Container {{ container_name }} exited with code {{ exit_code }}"}]}',
        )

        # Set timestamps
        container_exit_template.created_at = datetime.now()
        container_exit_template.updated_at = datetime.now()

        # Add to templates
        self._templates[container_exit_template.template_id] = container_exit_template

        # Save to disk
        self._save_template(container_exit_template)

        logger.info("Created container exit notification template")

        # Fix proposal template
        fix_proposal_template = NotificationTemplate(
            template_id="fix_proposal",
            name="Fix Proposal Template",
            description="Template for fix proposal notifications",
            html_template="<html><body><h1>{{ title }}</h1><p>{{ message }}</p><p>Issue: {{ issue_id }}</p></body></html>",
            text_template="{{ title }}\n\n{{ message }}\n\nIssue: {{ issue_id }}",
            slack_template='{"blocks":[{"type":"header","text":{"type":"plain_text","text":"{{ title }}","emoji":true}}]}',
            discord_template='{"embeds":[{"title":"{{ title }}","description":"{{ message }}"}]}',
        )

        # Set timestamps
        fix_proposal_template.created_at = datetime.now()
        fix_proposal_template.updated_at = datetime.now()

        # Add to templates
        self._templates[fix_proposal_template.template_id] = fix_proposal_template

        # Save to disk
        self._save_template(fix_proposal_template)

        logger.info("Created fix proposal notification template")

    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Get a template by ID.

        Args:
            template_id: The template ID

        Returns:
            The template if found, None otherwise
        """
        return self._templates.get(template_id)

    def get_templates(self) -> Dict[str, NotificationTemplate]:
        """Get all templates.

        Returns:
            Dictionary of templates
        """
        return self._templates.copy()

    def add_template(self, template: NotificationTemplate) -> None:
        """Add a template.

        Args:
            template: The template to add
        """
        # Set timestamps
        if not template.created_at:
            template.created_at = datetime.now()

        template.updated_at = datetime.now()

        # Add to templates
        self._templates[template.template_id] = template

        # Save to disk
        self._save_template(template)

        logger.info(f"Added template: {template.template_id}")

    def update_template(self, template: NotificationTemplate) -> None:
        """Update a template.

        Args:
            template: The template to update
        """
        # Check if template exists
        if template.template_id not in self._templates:
            logger.warning(f"Template not found: {template.template_id}")
            return

        # Update timestamp
        template.updated_at = datetime.now()

        # Update template
        self._templates[template.template_id] = template

        # Save to disk
        self._save_template(template)

        logger.info(f"Updated template: {template.template_id}")

    def delete_template(self, template_id: str) -> bool:
        """Delete a template.

        Args:
            template_id: The template ID

        Returns:
            True if the template was deleted, False otherwise
        """
        # Check if template exists
        if template_id not in self._templates:
            logger.warning(f"Template not found: {template_id}")
            return False

        # Remove from templates
        del self._templates[template_id]

        # Remove from disk
        templates_dir = os.path.expanduser(
            get_config(
                "notifications.templates.directory",
                "~/.dockerforge/notification_templates",
            )
        )
        filename = os.path.join(templates_dir, f"{template_id}.json")

        if os.path.exists(filename):
            try:
                os.remove(filename)
                logger.info(f"Deleted template file: {filename}")
            except Exception as e:
                logger.error(f"Error deleting template file: {str(e)}")
                return False

        logger.info(f"Deleted template: {template_id}")
        return True

    def render_template(
        self, template_id: str, template_type: str, context: Dict[str, Any]
    ) -> Optional[str]:
        """Render a template with the given context.

        Args:
            template_id: The template ID
            template_type: The template type (html, text, slack, discord)
            context: The context to render the template with

        Returns:
            The rendered template, or None if the template was not found or could not be rendered
        """
        # Get template
        template = self.get_template(template_id)

        if not template:
            logger.warning(f"Template not found: {template_id}")
            return None

        # Render template
        return template.render(template_type, context)


def get_template_manager() -> TemplateManager:
    """Get the template manager instance.

    Returns:
        The template manager instance
    """
    return TemplateManager()
