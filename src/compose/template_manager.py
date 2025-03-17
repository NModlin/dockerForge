"""
DockerForge Compose Template Manager Module.

This module provides functionality for managing service templates for Docker Compose files.
It includes template storage, variable substitution, inheritance, and validation.
"""

import os
import json
import yaml
import re
import copy
from typing import Dict, List, Any, Optional, Set, Union
from pathlib import Path

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)

# Regular expression for template variable references
TEMPLATE_VAR_PATTERN = re.compile(r'\{\{([^}^{]+)\}\}')


class TemplateManager:
    """Manage service templates for Docker Compose files."""

    def __init__(self, config: Dict = None):
        """Initialize TemplateManager.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.template_dir = self._get_template_dir()
        self.templates = {}
        self._load_templates()

    def _get_template_dir(self) -> str:
        """Get the template directory path.

        Returns:
            Path to the template directory
        """
        template_dir = self.config.get('template_dir', os.path.expanduser('~/.dockerforge/templates/compose'))
        os.makedirs(template_dir, exist_ok=True)
        return template_dir

    def _load_templates(self) -> None:
        """Load templates from disk."""
        try:
            # Load templates from template directory
            for root, _, files in os.walk(self.template_dir):
                for file in files:
                    if file.endswith(('.yml', '.yaml', '.json')):
                        file_path = os.path.join(root, file)
                        try:
                            template = self._load_template_file(file_path)
                            template_name = os.path.splitext(file)[0]
                            self.templates[template_name] = template
                            logger.debug(f"Loaded template: {template_name}")
                        except Exception as e:
                            logger.warning(f"Failed to load template {file_path}: {e}")
            
            logger.info(f"Loaded {len(self.templates)} templates from {self.template_dir}")
        except Exception as e:
            logger.warning(f"Failed to load templates: {e}")

    def _load_template_file(self, file_path: str) -> Dict:
        """Load a template from a file.

        Args:
            file_path: Path to the template file

        Returns:
            Template dictionary
        """
        with open(file_path, 'r') as f:
            if file_path.endswith('.json'):
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

    def list_templates(self) -> List[str]:
        """List available templates.

        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def save_template(self, template_name: str, template_data: Dict) -> str:
        """Save a template to disk.

        Args:
            template_name: Name of the template
            template_data: Template data

        Returns:
            Path to the saved template file
        """
        try:
            # Create template file path
            file_path = os.path.join(self.template_dir, f"{template_name}.yml")
            
            # Save template to file
            with open(file_path, 'w') as f:
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
            
            # Remove from in-memory templates
            del self.templates[template_name]
            
            # Remove template file
            file_path = os.path.join(self.template_dir, f"{template_name}.yml")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted template {template_name} from {file_path}")
                return True
            
            # Check for other extensions
            for ext in ['.yaml', '.json']:
                file_path = os.path.join(self.template_dir, f"{template_name}{ext}")
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
            return {k: self._substitute_variables(v, variables) for k, v in data.items()}
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
        if 'extends' in template:
            extends = template.pop('extends')
            
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
                parent_name = extends.get('template')
                service = extends.get('service')
                
                if not parent_name:
                    logger.warning("Parent template name not specified in extends")
                    return template
                
                parent = self.get_template(parent_name)
                if not parent:
                    logger.warning(f"Parent template {parent_name} not found")
                    return template
                
                if service:
                    # Extend from a specific service in the parent
                    if 'services' in parent and service in parent['services']:
                        parent_service = parent['services'][service]
                        merged = copy.deepcopy(parent_service)
                        self._deep_merge(merged, template)
                        return merged
                    else:
                        logger.warning(f"Service {service} not found in parent template {parent_name}")
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
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                self._deep_merge(target[key], value)
            else:
                # Replace or add value
                target[key] = copy.deepcopy(value)

    def create_service_from_template(self, template_name: str, service_name: str, variables: Dict = None) -> Dict:
        """Create a service definition from a template.

        Args:
            template_name: Name of the template
            service_name: Name of the service
            variables: Dictionary of variables to substitute

        Returns:
            Service definition dictionary
        """
        # Render template
        rendered = self.render_template(template_name, variables)
        
        # Extract service definition
        if 'services' in rendered and len(rendered['services']) > 0:
            # If the template has a services section, use the first service as a base
            service_template = list(rendered['services'].values())[0]
        else:
            # Otherwise, use the entire template as the service definition
            service_template = rendered
        
        # Create a deep copy to avoid modifying the original
        service = copy.deepcopy(service_template)
        
        return service

    def add_service_to_compose(self, compose_data: Dict, service_name: str, service_def: Dict) -> Dict:
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
        if 'services' not in result:
            result['services'] = {}
        
        # Add service
        result['services'][service_name] = service_def
        
        return result

    def create_compose_from_template(self, template_name: str, variables: Dict = None) -> Dict:
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
        if 'version' not in rendered:
            rendered['version'] = '3'
        
        if 'services' not in rendered:
            rendered['services'] = {}
        
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
        if 'services' in template_data:
            # Check services
            services = template_data['services']
            if not isinstance(services, dict):
                errors.append("'services' must be a dictionary")
            else:
                # Check each service
                for service_name, service in services.items():
                    if not isinstance(service, dict):
                        errors.append(f"Service '{service_name}' must be a dictionary")
                    else:
                        # Check for required service properties
                        if 'image' not in service and 'build' not in service:
                            errors.append(f"Service '{service_name}' must have either 'image' or 'build' property")
        
        # Check for extends
        if 'extends' in template_data:
            extends = template_data['extends']
            if isinstance(extends, str):
                # Simple string reference
                parent_name = extends
                if parent_name not in self.templates:
                    errors.append(f"Parent template '{parent_name}' not found")
            elif isinstance(extends, dict):
                # Dictionary with template name and optional service
                if 'template' not in extends:
                    errors.append("'extends' must have a 'template' property")
                else:
                    parent_name = extends['template']
                    if parent_name not in self.templates:
                        errors.append(f"Parent template '{parent_name}' not found")
                    
                    if 'service' in extends:
                        service = extends['service']
                        parent = self.templates.get(parent_name)
                        if parent and ('services' not in parent or service not in parent['services']):
                            errors.append(f"Service '{service}' not found in parent template '{parent_name}'")
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

    def create_template_from_service(self, compose_data: Dict, service_name: str, template_name: str) -> str:
        """Create a template from a service in a Docker Compose file.

        Args:
            compose_data: Docker Compose data
            service_name: Name of the service
            template_name: Name of the template to create

        Returns:
            Path to the saved template file
        """
        # Check if service exists
        if 'services' not in compose_data or service_name not in compose_data['services']:
            raise ValueError(f"Service {service_name} not found in Docker Compose file")
        
        # Extract service definition
        service = compose_data['services'][service_name]
        
        # Create template
        template = {
            'services': {
                'service': service
            }
        }
        
        # Save template
        return self.save_template(template_name, template)
