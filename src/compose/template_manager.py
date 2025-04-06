"""DockerForge Compose Template Manager Module.

This module provides functionality for managing service templates for Docker Compose files.
It includes template storage, variable substitution, inheritance, validation, and categorization.

"""

import copy
import json
import os
import re
from typing import Any, Dict, List, Optional, Set

import yaml

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)

# Regular expression for template variable references
TEMPLATE_VAR_PATTERN = re.compile(r"\{\{([^}^{]+)\}\}")


class TemplateManager:
    """Manage service templates for Docker Compose files."""

    # Template categories
    DEFAULT_CATEGORIES = [
        "web",
        "database",
        "cache",
        "messaging",
        "monitoring",
        "development",
        "production",
        "testing",
        "infrastructure",
        "custom",
    ]

    # Template difficulty levels
    DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]

    def __init__(self, config: Dict = None):
        """Initialize TemplateManager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.template_dir = self._get_template_dir()
        self.templates = {}
        self.categories = self._get_categories()
        self._load_templates()

    def _get_template_dir(self) -> str:
        """Get the template directory path.

        Returns:
            Path to the template directory
        """
        template_dir = self.config.get(
            "template_dir", os.path.expanduser("~/.dockerforge/templates/compose")
        )
        os.makedirs(template_dir, exist_ok=True)

        # Create category subdirectories
        for category in self.DEFAULT_CATEGORIES:
            category_dir = os.path.join(template_dir, category)
            os.makedirs(category_dir, exist_ok=True)

        return template_dir

    def _get_categories(self) -> List[str]:
        """Get template categories.

        Returns:
            List of template categories
        """
        # Get categories from config or use defaults
        categories = self.config.get("categories", self.DEFAULT_CATEGORIES)
        return categories

    def _load_templates(self) -> None:
        """Load templates from disk."""
        try:
            # Load templates from template directory
            for root, _, files in os.walk(self.template_dir):
                for file in files:
                    if file.endswith((".yml", ".yaml", ".json")):
                        file_path = os.path.join(root, file)
                        try:
                            template = self._load_template_file(file_path)

                            # Get template name and category from path
                            rel_path = os.path.relpath(file_path, self.template_dir)
                            parts = rel_path.split(os.sep)

                            if len(parts) > 1:
                                # Template is in a category subdirectory
                                category = parts[0]
                                template_name = os.path.splitext(parts[-1])[0]
                            else:
                                # Template is in the root directory
                                category = "custom"
                                template_name = os.path.splitext(file)[0]

                            # Add metadata if not present
                            if "metadata" not in template:
                                template["metadata"] = {}

                            # Set category in metadata
                            if "category" not in template["metadata"]:
                                template["metadata"]["category"] = category

                            # Set name in metadata if not present
                            if "name" not in template["metadata"]:
                                template["metadata"]["name"] = template_name

                            # Add template to collection
                            self.templates[template_name] = template
                            logger.debug(
                                f"Loaded template: {template_name} (category: {category})"
                            )
                        except Exception as e:
                            logger.warning(f"Failed to load template {file_path}: {e}")

            logger.info(
                f"Loaded {len(self.templates)} templates from {self.template_dir}"
            )
        except Exception as e:
            logger.warning(f"Failed to load templates: {e}")

    def _load_template_file(self, file_path: str) -> Dict:
        """Load a template from a file.

        Args:
            file_path: Path to the template file

        Returns:
            Template dictionary
        """
        with open(file_path, "r") as f:
            if file_path.endswith(".json"):
                return json.load(f)
            else:
                return yaml.safe_load(f)

    def get_template(self, template_name: str) -> Optional[Dict]:
        """Get a template by name.

        Args:
            template_name: Name of the template

        Returns:
            Template dictionary or None if not found
        """
        return self.templates.get(template_name)

    def list_templates(self, category: Optional[str] = None) -> List[Dict]:
        """List available templates.

        Args:
            category: Optional category to filter by

        Returns:
            List of template dictionaries with metadata
        """
        result = []

        for name, template in self.templates.items():
            # Get template metadata
            metadata = template.get("metadata", {})
            template_category = metadata.get("category", "custom")

            # Filter by category if specified
            if category and template_category != category:
                continue

            # Create template info dictionary
            template_info = {
                "name": name,
                "category": template_category,
                "description": metadata.get("description", ""),
                "difficulty": metadata.get("difficulty", "beginner"),
                "created_at": metadata.get("created_at", ""),
                "updated_at": metadata.get("updated_at", ""),
                "tags": metadata.get("tags", []),
                "services": list(template.get("services", {}).keys()),
                "variables": list(self.extract_template_variables(template)),
            }

            result.append(template_info)

        return result

    def get_categories(self) -> List[str]:
        """Get all template categories.

        Returns:
            List of category names
        """
        return self.categories

    def get_templates_by_category(self) -> Dict[str, List[Dict]]:
        """Get templates organized by category.

        Returns:
            Dictionary mapping category names to lists of template info dictionaries
        """
        result = {category: [] for category in self.categories}

        # Add "all" category
        result["all"] = []

        for name, template in self.templates.items():
            # Get template metadata
            metadata = template.get("metadata", {})
            category = metadata.get("category", "custom")

            # Create template info dictionary
            template_info = {
                "name": name,
                "category": category,
                "description": metadata.get("description", ""),
                "difficulty": metadata.get("difficulty", "beginner"),
                "created_at": metadata.get("created_at", ""),
                "updated_at": metadata.get("updated_at", ""),
                "tags": metadata.get("tags", []),
                "services": list(template.get("services", {}).keys()),
                "variables": list(self.extract_template_variables(template)),
            }

            # Add to appropriate category
            if category in result:
                result[category].append(template_info)
            else:
                # If category doesn't exist, add to custom
                result["custom"].append(template_info)

            # Add to "all" category
            result["all"].append(template_info)

        return result

    def save_template(
        self, template_name: str, template_data: Dict, category: str = "custom"
    ) -> str:
        """Save a template to disk.

        Args:
            template_name: Name of the template
            template_data: Template data
            category: Template category (default: "custom")

        Returns:
            Path to the saved template file
        """
        try:
            # Ensure category exists
            if category not in self.categories:
                if category in self.DEFAULT_CATEGORIES:
                    # It's a default category, create the directory
                    category_dir = os.path.join(self.template_dir, category)
                    os.makedirs(category_dir, exist_ok=True)
                    self.categories.append(category)
                else:
                    # Not a recognized category, use custom
                    logger.warning(
                        f"Category {category} not recognized, using 'custom' instead"
                    )
                    category = "custom"

            # Create template file path in the category directory
            category_dir = os.path.join(self.template_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            file_path = os.path.join(category_dir, f"{template_name}.yml")

            # Ensure template has metadata
            if "metadata" not in template_data:
                template_data["metadata"] = {}

            # Update metadata
            template_data["metadata"]["name"] = template_name
            template_data["metadata"]["category"] = category

            # Add timestamp if not present
            if "created_at" not in template_data["metadata"]:
                from datetime import datetime

                template_data["metadata"]["created_at"] = datetime.now().isoformat()

            # Save template to file
            with open(file_path, "w") as f:
                yaml.dump(template_data, f, default_flow_style=False, sort_keys=False)

            # Add to in-memory templates
            self.templates[template_name] = template_data

            logger.info(f"Saved template {template_name} to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save template {template_name}: {e}")
            raise

    def delete_template(self, template_name: str) -> bool:
        """Delete a template.

        Args:
            template_name: Name of the template

        Returns:
            True if the template was deleted, False otherwise
        """
        try:
            # Check if template exists
            if template_name not in self.templates:
                logger.warning(f"Template {template_name} not found")
                return False

            # Get template category
            template = self.templates[template_name]
            category = template.get("metadata", {}).get("category", "custom")

            # Remove from in-memory templates
            del self.templates[template_name]

            # Remove template file from category directory
            category_dir = os.path.join(self.template_dir, category)
            file_path = os.path.join(category_dir, f"{template_name}.yml")

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted template {template_name} from {file_path}")
                return True

            # Check for other extensions
            for ext in [".yaml", ".json"]:
                file_path = os.path.join(category_dir, f"{template_name}{ext}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted template {template_name} from {file_path}")
                    return True

            # If not found in category directory, check root directory
            file_path = os.path.join(self.template_dir, f"{template_name}.yml")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted template {template_name} from {file_path}")
                return True

            logger.warning(f"Template {template_name} file not found")
            return False
        except Exception as e:
            logger.error(f"Failed to delete template {template_name}: {e}")
            return False

    def render_template(self, template_name: str, variables: Dict = None) -> Dict:
        """Render a template with variables.

        Args:
            template_name: Name of the template
            variables: Dictionary of variables to substitute

        Returns:
            Rendered template dictionary
        """
        # Get template
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")

        # Make a deep copy to avoid modifying the original
        rendered = copy.deepcopy(template)

        # Substitute variables
        if variables:
            rendered = self._substitute_variables(rendered, variables)

        # Resolve inheritance
        rendered = self._resolve_inheritance(rendered)

        return rendered

    def _substitute_variables(self, data: Any, variables: Dict) -> Any:
        """Substitute variables in data.

        Args:
            data: Data to substitute variables in
            variables: Dictionary of variables to substitute

        Returns:
            Data with variables substituted
        """
        if isinstance(data, str):
            # Substitute variables in string
            return self._substitute_variables_in_string(data, variables)
        elif isinstance(data, dict):
            # Substitute variables in dictionary
            return {
                k: self._substitute_variables(v, variables) for k, v in data.items()
            }
        elif isinstance(data, list):
            # Substitute variables in list
            return [self._substitute_variables(item, variables) for item in data]
        else:
            # Return other types unchanged
            return data

    def _substitute_variables_in_string(self, text: str, variables: Dict) -> str:
        """Substitute variables in a string.

        Args:
            text: String to substitute variables in
            variables: Dictionary of variables to substitute

        Returns:
            String with variables substituted
        """

        def _replace_var(match):
            var_name = match.group(1).strip()
            if var_name in variables:
                return str(variables[var_name])
            else:
                logger.warning(f"Variable {var_name} not found in template variables")
                return match.group(0)

        return TEMPLATE_VAR_PATTERN.sub(_replace_var, text)

    def _resolve_inheritance(self, template: Dict) -> Dict:
        """Resolve inheritance in a template.

        Args:
            template: Template dictionary

        Returns:
            Template with inheritance resolved
        """
        # Check for extends property
        if "extends" in template:
            extends = template.pop("extends")

            # Get parent template
            if isinstance(extends, str):
                # Simple string reference
                parent_name = extends
                parent = self.get_template(parent_name)
                if not parent:
                    logger.warning(f"Parent template {parent_name} not found")
                    return template

                # Merge parent and child
                merged = copy.deepcopy(parent)
                self._deep_merge(merged, template)
                return merged
            elif isinstance(extends, dict):
                # Dictionary with template name and optional service
                parent_name = extends.get("template")
                service = extends.get("service")

                if not parent_name:
                    logger.warning("Parent template name not specified in extends")
                    return template

                parent = self.get_template(parent_name)
                if not parent:
                    logger.warning(f"Parent template {parent_name} not found")
                    return template

                if service:
                    # Extend from a specific service in the parent
                    if "services" in parent and service in parent["services"]:
                        parent_service = parent["services"][service]
                        merged = copy.deepcopy(parent_service)
                        self._deep_merge(merged, template)
                        return merged
                    else:
                        logger.warning(
                            f"Service {service} not found in parent template {parent_name}"
                        )
                        return template
                else:
                    # Extend from the entire parent
                    merged = copy.deepcopy(parent)
                    self._deep_merge(merged, template)
                    return merged

        # No inheritance, return as is
        return template

    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """Deep merge source dictionary into target dictionary.

        Args:
            target: Target dictionary
            source: Source dictionary
        """
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge dictionaries
                self._deep_merge(target[key], value)
            else:
                # Replace or add value
                target[key] = copy.deepcopy(value)

    def create_service_from_template(
        self, template_name: str, service_name: str = None, variables: Dict = None
    ) -> Dict:
        """Create a service definition from a template.

        Args:
            template_name: Name of the template
            service_name: Optional name of the service (used for logging only)
            variables: Dictionary of variables to substitute

        Returns:
            Service definition dictionary
        """
        # Render template
        rendered = self.render_template(template_name, variables)

        # Extract service definition
        if "services" in rendered and len(rendered["services"]) > 0:
            # If the template has a services section, use the first service as a base
            service_template = list(rendered["services"].values())[0]
        else:
            # Otherwise, use the entire template as the service definition
            service_template = rendered

        # Create a deep copy to avoid modifying the original
        service = copy.deepcopy(service_template)

        # Log the service creation
        if service_name:
            logger.debug(
                f"Created service '{service_name}' from template '{template_name}'"
            )

        return service

    def add_service_to_compose(
        self, compose_data: Dict, service_name: str, service_def: Dict
    ) -> Dict:
        """Add a service to a Docker Compose file.

        Args:
            compose_data: Docker Compose data
            service_name: Name of the service
            service_def: Service definition

        Returns:
            Updated Docker Compose data
        """
        # Make a deep copy to avoid modifying the original
        result = copy.deepcopy(compose_data)

        # Ensure services section exists
        if "services" not in result:
            result["services"] = {}

        # Add service
        result["services"][service_name] = service_def

        return result

    def create_compose_from_template(
        self, template_name: str, variables: Dict = None
    ) -> Dict:
        """Create a Docker Compose file from a template.

        Args:
            template_name: Name of the template
            variables: Dictionary of variables to substitute

        Returns:
            Docker Compose data
        """
        # Render template
        rendered = self.render_template(template_name, variables)

        # Ensure it's a valid Docker Compose file
        if "version" not in rendered:
            rendered["version"] = "3"

        if "services" not in rendered:
            rendered["services"] = {}

        return rendered

    def validate_template(self, template_data: Dict) -> List[str]:
        """Validate a template.

        Args:
            template_data: Template data

        Returns:
            List of validation errors, empty if valid
        """
        errors = []

        # Check for required sections
        if "services" in template_data:
            # Check services
            services = template_data["services"]
            if not isinstance(services, dict):
                errors.append("'services' must be a dictionary")
            else:
                # Check each service
                for service_name, service in services.items():
                    if not isinstance(service, dict):
                        errors.append(f"Service '{service_name}' must be a dictionary")
                    else:
                        # Check for required service properties
                        if "image" not in service and "build" not in service:
                            errors.append(
                                f"Service '{service_name}' must have either 'image' or 'build' property"
                            )

        # Check for extends
        if "extends" in template_data:
            extends = template_data["extends"]
            if isinstance(extends, str):
                # Simple string reference
                parent_name = extends
                if parent_name not in self.templates:
                    errors.append(f"Parent template '{parent_name}' not found")
            elif isinstance(extends, dict):
                # Dictionary with template name and optional service
                if "template" not in extends:
                    errors.append("'extends' must have a 'template' property")
                else:
                    parent_name = extends["template"]
                    if parent_name not in self.templates:
                        errors.append(f"Parent template '{parent_name}' not found")

                    if "service" in extends:
                        service = extends["service"]
                        parent = self.templates.get(parent_name)
                        if parent and (
                            "services" not in parent
                            or service not in parent["services"]
                        ):
                            errors.append(
                                f"Service '{service}' not found in parent template '{parent_name}'"
                            )
            else:
                errors.append("'extends' must be a string or dictionary")

        return errors

    def extract_template_variables(self, template_data: Dict) -> Set[str]:
        """Extract variables from a template.

        Args:
            template_data: Template data

        Returns:
            Set of variable names
        """
        variables = set()

        # Convert template to string
        template_str = json.dumps(template_data)

        # Find all variable references
        for match in TEMPLATE_VAR_PATTERN.finditer(template_str):
            var_name = match.group(1).strip()
            variables.add(var_name)

        return variables

    def export_template(self, template_name: str, output_path: str = None) -> str:
        """Export a template to a file.

        Args:
            template_name: Name of the template to export
            output_path: Optional output path (default: current directory)

        Returns:
            Path to the exported template file
        """
        try:
            # Check if template exists
            template = self.get_template(template_name)
            if not template:
                raise ValueError(f"Template {template_name} not found")

            # Determine output path
            if not output_path:
                output_path = os.getcwd()

            # Create output file path
            file_path = os.path.join(output_path, f"{template_name}.yml")

            # Save template to file
            with open(file_path, "w") as f:
                yaml.dump(template, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Exported template {template_name} to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to export template {template_name}: {e}")
            raise

    def import_template(
        self, file_path: str, new_name: str = None, category: str = None
    ) -> str:
        """Import a template from a file.

        Args:
            file_path: Path to the template file
            new_name: Optional new name for the template
            category: Optional category for the template

        Returns:
            Name of the imported template
        """
        try:
            # Load template from file
            with open(file_path, "r") as f:
                if file_path.endswith(".json"):
                    template_data = json.load(f)
                else:
                    template_data = yaml.safe_load(f)

            # Determine template name
            if new_name:
                template_name = new_name
            else:
                # Use filename without extension
                template_name = os.path.splitext(os.path.basename(file_path))[0]

            # Determine category
            if not category:
                # Use category from metadata or default to custom
                category = template_data.get("metadata", {}).get("category", "custom")

            # Save template
            self.save_template(template_name, template_data, category)

            logger.info(f"Imported template {template_name} from {file_path}")
            return template_name
        except Exception as e:
            logger.error(f"Failed to import template {file_path}: {e}")
            raise

    def customize_template_with_ai(
        self, template_name: str, instructions: str, ai_provider=None
    ) -> Dict:
        """Customize a template using AI.

        Args:
            template_name: Name of the template to customize
            instructions: Instructions for customization
            ai_provider: Optional AI provider instance

        Returns:
            Customized template data
        """
        try:
            # Check if template exists
            template = self.get_template(template_name)
            if not template:
                raise ValueError(f"Template {template_name} not found")

            # Get AI provider if not provided
            if not ai_provider:
                from ..core.ai_provider import get_ai_provider

                ai_provider = get_ai_provider()

            # Convert template to YAML string for AI
            template_yaml = yaml.dump(
                template, default_flow_style=False, sort_keys=False
            )

            # Create prompt for AI
            prompt = f"""You are an expert in Docker and Docker Compose.
            Please customize the following Docker Compose template according to these instructions:

            INSTRUCTIONS:
            {instructions}

            TEMPLATE:
            ```yaml
{template_yaml}
```

            Please provide ONLY the modified YAML content without any explanations or markdown formatting.
            The output should be valid YAML that can be directly used as a Docker Compose file.
            """

            # Get customized template from AI
            response = ai_provider.generate_text(prompt)

            # Extract YAML content from response
            # This is a simple extraction - in production, you might need more robust parsing
            yaml_content = response.strip()
            if "```yaml" in yaml_content and "```" in yaml_content:
                # Extract content between yaml code blocks if present
                start = yaml_content.find("```yaml") + 7
                end = yaml_content.rfind("```")
                yaml_content = yaml_content[start:end].strip()
            elif "```" in yaml_content:
                # Extract content between generic code blocks if present
                start = yaml_content.find("```") + 3
                end = yaml_content.rfind("```")
                yaml_content = yaml_content[start:end].strip()

            # Parse the customized YAML
            try:
                customized_template = yaml.safe_load(yaml_content)
                if not customized_template:
                    raise ValueError("AI generated empty or invalid YAML")
            except Exception as yaml_error:
                logger.error(f"Failed to parse AI-generated YAML: {yaml_error}")
                raise ValueError(f"AI generated invalid YAML: {yaml_error}")

            # Preserve metadata
            if "metadata" in template:
                if "metadata" not in customized_template:
                    customized_template["metadata"] = {}

                # Copy metadata fields but allow AI to update some
                for key, value in template["metadata"].items():
                    if key not in customized_template["metadata"] and key not in [
                        "description",
                        "tags",
                    ]:
                        customized_template["metadata"][key] = value

                # Update metadata
                customized_template["metadata"]["customized"] = True
                from datetime import datetime

                customized_template["metadata"][
                    "updated_at"
                ] = datetime.now().isoformat()

                # Add customization instructions to metadata
                customized_template["metadata"][
                    "customization_instructions"
                ] = instructions

            return customized_template
        except Exception as e:
            logger.error(f"Failed to customize template {template_name} with AI: {e}")
            raise

    def create_template_from_service(
        self,
        compose_data: Dict,
        service_name: str,
        template_name: str,
        category: str = "custom",
        description: str = "",
        difficulty: str = "beginner",
        tags: List[str] = None,
    ) -> str:
        """Create a template from a service in a Docker Compose file.

        Args:
            compose_data: Docker Compose data
            service_name: Name of the service
            template_name: Name of the template to create
            category: Template category
            description: Template description
            difficulty: Template difficulty level
            tags: Template tags

        Returns:
            Path to the saved template file
        """
        # Check if service exists
        if (
            "services" not in compose_data
            or service_name not in compose_data["services"]
        ):
            raise ValueError(f"Service {service_name} not found in Docker Compose file")

        # Extract service definition
        service = compose_data["services"][service_name]

        # Create template
        template = {
            "services": {"service": service},
            "metadata": {
                "name": template_name,
                "category": category,
                "description": description,
                "difficulty": difficulty,
                "tags": tags or [],
                "source_service": service_name,
            },
        }

        # Save template
        return self.save_template(template_name, template, category)
