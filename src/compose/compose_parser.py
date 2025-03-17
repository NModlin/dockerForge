"""
DockerForge Compose Parser Module.

This module provides functionality for parsing and validating Docker Compose files.
It includes syntax validation, schema validation, environment variable expansion,
and version detection.
"""

import os
import re
import yaml
import json
import jsonschema
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path

from ..utils.logging_manager import get_logger

logger = get_logger(__name__)

# Regular expression for environment variable references
ENV_VAR_PATTERN = re.compile(r'\$\{([^}^{]+)\}')


class ComposeParser:
    """Parser for Docker Compose files with enhanced capabilities."""

    def __init__(self, config: Dict = None):
        """Initialize ComposeParser.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.schemas = self._load_schemas()

    def _load_schemas(self) -> Dict[str, Dict]:
        """Load JSON schemas for Docker Compose validation.

        Returns:
            Dict mapping version strings to schema dictionaries
        """
        schemas = {}
        schema_dir = self.config.get('schema_dir', os.path.join(
            os.path.dirname(__file__), 'schemas'))
        
        # Create schema directory if it doesn't exist
        os.makedirs(schema_dir, exist_ok=True)
        
        # Load built-in schemas
        try:
            # In a real implementation, we would include schema files in the package
            # and load them from there. For now, we'll use a placeholder.
            schemas = {
                '3': {},  # Placeholder for schema v3
                '3.1': {},  # Placeholder for schema v3.1
                '3.8': {},  # Placeholder for schema v3.8
            }
            logger.debug(f"Loaded {len(schemas)} Docker Compose schemas")
        except Exception as e:
            logger.warning(f"Failed to load Docker Compose schemas: {e}")
        
        return schemas

    def parse_file(self, file_path: str, expand_env: bool = True) -> Dict:
        """Parse a Docker Compose file.

        Args:
            file_path: Path to the Docker Compose file
            expand_env: Whether to expand environment variables

        Returns:
            Dict containing the parsed Docker Compose file
        """
        try:
            logger.debug(f"Parsing Docker Compose file: {file_path}")
            
            # Read the file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Expand environment variables if requested
            if expand_env:
                content = self._expand_env_vars(content)
            
            # Parse YAML
            compose_data = yaml.safe_load(content)
            
            # Detect version
            version = compose_data.get('version')
            logger.debug(f"Detected Docker Compose version: {version}")
            
            return compose_data
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse Docker Compose file {file_path}: {e}")
            raise ValueError(f"Invalid YAML in Docker Compose file: {e}")
        except Exception as e:
            logger.error(f"Error parsing Docker Compose file {file_path}: {e}")
            raise

    def _expand_env_vars(self, content: str) -> str:
        """Expand environment variables in a string.

        Args:
            content: String containing environment variable references

        Returns:
            String with environment variables expanded
        """
        def _replace_env_var(match):
            env_var = match.group(1)
            # Check for default value syntax ${VAR:-default}
            if ':-' in env_var:
                var_name, default = env_var.split(':-', 1)
                return os.environ.get(var_name, default)
            # Check for required variable syntax ${VAR:?error}
            elif ':?' in env_var:
                var_name, error = env_var.split(':?', 1)
                if var_name in os.environ:
                    return os.environ[var_name]
                else:
                    raise ValueError(f"Required environment variable {var_name} is not set: {error}")
            # Simple variable reference ${VAR}
            else:
                return os.environ.get(env_var, '')
        
        return ENV_VAR_PATTERN.sub(_replace_env_var, content)

    def validate(self, compose_data: Dict, version: str = None) -> List[str]:
        """Validate a Docker Compose file against its schema.

        Args:
            compose_data: Dict containing the parsed Docker Compose file
            version: Docker Compose version to validate against (optional)

        Returns:
            List of validation errors, empty if valid
        """
        # Determine version if not provided
        if not version:
            version = compose_data.get('version')
        
        # Find the appropriate schema
        schema = self._get_schema_for_version(version)
        if not schema:
            logger.warning(f"No schema available for Docker Compose version {version}")
            return []
        
        # Validate against schema
        validator = jsonschema.Draft7Validator(schema)
        errors = list(validator.iter_errors(compose_data))
        
        # Convert errors to strings
        error_strings = []
        for error in errors:
            path = '.'.join(str(p) for p in error.path) if error.path else 'root'
            error_strings.append(f"{path}: {error.message}")
        
        return error_strings

    def _get_schema_for_version(self, version: str) -> Optional[Dict]:
        """Get the schema for a specific Docker Compose version.

        Args:
            version: Docker Compose version

        Returns:
            Schema dict or None if not found
        """
        if not version:
            return None
        
        # Try exact match
        if version in self.schemas:
            return self.schemas[version]
        
        # Try major version match
        major_version = version.split('.')[0]
        if major_version in self.schemas:
            return self.schemas[major_version]
        
        return None

    def resolve_includes(self, compose_data: Dict, base_dir: str) -> Dict:
        """Resolve includes and extends in a Docker Compose file.

        Args:
            compose_data: Dict containing the parsed Docker Compose file
            base_dir: Base directory for resolving relative paths

        Returns:
            Dict with includes and extends resolved
        """
        # This is a placeholder for a more complex implementation
        # In a real implementation, we would handle Docker Compose includes and extends
        # For now, we'll just return the original data
        return compose_data

    def get_services(self, compose_data: Dict) -> Dict[str, Dict]:
        """Get services defined in a Docker Compose file.

        Args:
            compose_data: Dict containing the parsed Docker Compose file

        Returns:
            Dict mapping service names to service definitions
        """
        return compose_data.get('services', {})

    def get_networks(self, compose_data: Dict) -> Dict[str, Dict]:
        """Get networks defined in a Docker Compose file.

        Args:
            compose_data: Dict containing the parsed Docker Compose file

        Returns:
            Dict mapping network names to network definitions
        """
        return compose_data.get('networks', {})

    def get_volumes(self, compose_data: Dict) -> Dict[str, Dict]:
        """Get volumes defined in a Docker Compose file.

        Args:
            compose_data: Dict containing the parsed Docker Compose file

        Returns:
            Dict mapping volume names to volume definitions
        """
        return compose_data.get('volumes', {})

    def get_secrets(self, compose_data: Dict) -> Dict[str, Dict]:
        """Get secrets defined in a Docker Compose file.

        Args:
            compose_data: Dict containing the parsed Docker Compose file

        Returns:
            Dict mapping secret names to secret definitions
        """
        return compose_data.get('secrets', {})

    def get_configs(self, compose_data: Dict) -> Dict[str, Dict]:
        """Get configs defined in a Docker Compose file.

        Args:
            compose_data: Dict containing the parsed Docker Compose file

        Returns:
            Dict mapping config names to config definitions
        """
        return compose_data.get('configs', {})

    def get_dependencies(self, compose_data: Dict) -> Dict[str, List[str]]:
        """Get service dependencies defined in a Docker Compose file.

        Args:
            compose_data: Dict containing the parsed Docker Compose file

        Returns:
            Dict mapping service names to lists of dependency service names
        """
        services = self.get_services(compose_data)
        dependencies = {}
        
        for service_name, service_def in services.items():
            deps = []
            
            # Check 'depends_on'
            if 'depends_on' in service_def:
                depends_on = service_def['depends_on']
                if isinstance(depends_on, list):
                    deps.extend(depends_on)
                elif isinstance(depends_on, dict):
                    deps.extend(depends_on.keys())
            
            # Check 'links'
            if 'links' in service_def:
                links = service_def['links']
                for link in links:
                    # Handle 'service:alias' format
                    if ':' in link:
                        service = link.split(':', 1)[0]
                        deps.append(service)
                    else:
                        deps.append(link)
            
            dependencies[service_name] = deps
        
        return dependencies

    def serialize(self, compose_data: Dict, file_path: str) -> None:
        """Serialize a Docker Compose file.

        Args:
            compose_data: Dict containing the Docker Compose data
            file_path: Path to write the file to
        """
        try:
            with open(file_path, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
            logger.debug(f"Wrote Docker Compose file to {file_path}")
        except Exception as e:
            logger.error(f"Failed to write Docker Compose file to {file_path}: {e}")
            raise
